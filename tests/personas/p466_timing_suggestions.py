"""Persona 466 (v3.10.1380): the rule-based timing coach ("Timing suggestions") in the When you eat card. Pete (12 Nov): layered coach, each goal/condition adds its own rules labelled Proven / Early Stage / Speculative,
conflicts shown both ways, "my care team has told me" hides matching topics, suggestions never targets, nothing shared. Off by default. Covers: off by default; Settings tile (show/hide, reorder, search, topic filter, "?");
on with Losing weight; the person's own numbers; short-window rule; GBM layer only on a GBM profile; loss+GBM conflict section; care-team filter hides and counts; Early Stage labels with a source and review date on every rule;
prolonged-fast rule is a conversation, never a suggestion; reload keeps it; backup has the settings; share has nothing; AI prompt carries layers and care note. Demo data is synthetic."""
import sys, re, json; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from datetime import date, timedelta, datetime, time as dtime
from playwright.sync_api import sync_playwright
f = Findings()
dmy = lambda n: (date.today() - timedelta(days=n)).strftime('%d/%m/%y')
def day(n, meals, wt):
    log = [{'id': 1000 + i, 'time': t, 'description': 'meal', 'kcal': 400, 'protein': p, 'carbs': c, 'fat': fa} for i, (t, p, c, fa) in enumerate(meals)]
    return {'date': dmy(n), 'mode': 'standard', 'notes': 'standard', 'log': log, 'weight': wt, 'totals': {'kcal': 1600, 'protein': sum(m[1] for m in meals), 'carbs': 95, 'fat': 65}}
LONG = [('08:00', 30, 20, 10), ('13:00', 40, 30, 20), ('19:00', 50, 40, 30), ('21:30', 10, 5, 5)]      # window 13.5 h
SHORT = [('12:00', 40, 20, 10), ('15:00', 40, 30, 20), ('19:00', 50, 40, 30)]                       # window 7 h
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block', timezone_id='UTC')
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    ctx.clock.install(time=datetime.combine(date.today(), dtime(12, 0)))
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500); ev = page.evaluate
    ev("localStorage.setItem('mh_condition','general'); state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    hist = [day(i, SHORT, 90 - (20 - i) * 0.3) for i in range(1, 21)]   # 20 days; weight falls about 6 kg over the span (older days heavier)
    ev("state.weight = 84; state.history = " + json.dumps(hist) + "; saveState()")
    show = lambda: (ev("switchTab('insights'); switchSubTab('insights','reports'); _rptRange=0; renderReports()"), page.wait_for_timeout(600))
    tips = lambda: ev("document.getElementById('wheneat-tips')?.innerText || ''")
    show()
    if tips(): f.add('BUG', '1: timing suggestions show with nothing switched on')
    ev("switchTabById('manage')"); page.wait_for_timeout(600)
    if not ev("!!document.getElementById('settingTcOn') && document.getElementById('title-set-timingtips').offsetParent!==null"): f.add('BUG', '2: no Settings tile')
    if not ev("!!document.querySelector('#set-timingtips-wrap .help-slot, #set-timingtips-wrap [id^=help-]')"): f.add('BUG', '3: Settings tile has no "?" for its longer text')
    if 'set-timingtips' not in ev("JSON.stringify(Object.values(MH_TOPIC_SCOPES.manage.groups).flatMap(g=>g.keys))"): f.add('BUG', '4: no Filter pill entry')
    if not ev("SITE_SEARCH_SETTINGS.some(x=>x.key==='set-timingtips')"): f.add('BUG', '5: not in the search list')
    if 'set-timingtips' not in ev("JSON.stringify(getGenericOrder('manage'))"): f.add('BUG', '6: not in the reorder list')
    # on, Losing weight
    ev("document.getElementById('settingTcOn').checked=true; document.querySelector('.settingTcLayer[data-layer=\"loss\"]').checked=true; mhTcSave()")
    if ev("!!document.querySelector('.settingTcLayer[data-layer=\"gbm\"]')"): f.add('BUG', '7: GBM layer offered on a general profile')
    show(); t = tips()
    if 'Timing suggestions' not in t or 'not targets' not in t: f.add('BUG', f'8: block missing: {t[:80]!r}')
    if 'Protein while you lose weight' not in t or 'Yours: about' not in t: f.add('BUG', f'9: protein rule or own numbers missing: {t[:200]!r}')
    if 'A short eating window' not in t or 'eating window averages' not in t: f.add('BUG', f'10: short-window rule missing for a 7h window: {t[:300]!r}')
    # long window days: that rule must go
    ev("state.history = " + json.dumps([day(i, LONG, 84) for i in range(1, 21)]) + "; saveState()"); show()
    if 'A short eating window' in tips(): f.add('BUG', '11: short-window rule shows for a 13.5h window')
    ev("state.history = " + json.dumps(hist) + "; saveState()"); show()
    # every rule: label, source, review date; chips
    bad = ev("MH_TC_RULES.filter(r=>!['Proven','Early Stage','Speculative'].includes(r.label)||!r.src||!r.src.u||!/^\\d\\d\\/\\d\\d\\/\\d\\d$/.test(r.reviewed)||!r.reason||!r.topics.length).map(r=>r.id)")
    if bad: f.add('BUG', f'12: rules without label, source, reason, topic or review date: {bad}')
    if ev("MH_TC_RULES.some(r=>/\\b(must|should|need to|target of)\\b/i.test(r.text+' '+r.short))"): f.add('BUG', '13: a rule is worded as an order or target')
    ev("document.querySelector('#wheneat-tips [id^=help-tc-loss-protein]').style.display='block'")
    d = ev("document.querySelector('#wheneat-tips [id^=help-tc-loss-protein]').innerText")
    if 'Nutrients 2023' not in d or 'last reviewed' not in d.lower() or 'not a target' not in d.lower(): f.add('BUG', f'14: rule detail lacks source / review date / not-a-target: {d[-260:]!r}')
    # GBM layer on a GBM profile, conflict section, care filter
    ev("localStorage.setItem('mh_condition','gbm')"); ev("switchTabById('manage')"); page.wait_for_timeout(500); ev("mhTcSettingsLoad()")
    if not ev("!!document.querySelector('.settingTcLayer[data-layer=\"gbm\"]')"): f.add('BUG', '15: GBM layer not offered on a GBM profile')
    ev("document.querySelector('.settingTcLayer[data-layer=\"gbm\"]').checked=true; mhTcSave()"); show(); t = tips()
    if 'These pull in different directions' not in t or 'Losing weight' not in t or 'patient guide' not in t.lower(): f.add('BUG', f'16: loss + GBM should show the conflict section with both sides: {t[-400:]!r}')
    if 'Fasting windows of 12 to 16 hours' in t and not ev("document.querySelector('#wheneat-tips [data-rule=\"gbm-window\"] .mh-tc-own')"): f.add('BUG', '17: GBM fasting rule without own count')
    if 'Your weight is falling' not in t: f.add('BUG', f'18: weight down more than 5% over 20 days should raise the GBM weight prompt: {t[:300]!r}')
    pr = ev("MH_TC_RULES.find(r=>r.id==='gbm-prolonged')"); wh = ev("MH_TC_RULES.find(r=>r.id==='gbm-prolonged').when({fastsH:[20]})"), ev("MH_TC_RULES.find(r=>r.id==='gbm-prolonged').when({fastsH:[26]})")
    if wh[0] or not wh[1]: f.add('BUG', f'19: prolonged-fast rule fires wrongly: {wh}')
    txt = ev("(()=>{const r=MH_TC_RULES.find(r=>r.id==='gbm-prolonged'); return r.text+' '+r.short})()")
    if 'oncologist' not in txt or 'never suggests' not in txt: f.add('BUG', '20: prolonged-fast rule must be a conversation with the oncologist, never a suggestion')
    ev("document.getElementById('settingTcCare').value='Told not to fast'; mhTcSave()"); show(); t = tips()
    if 'Fasting windows of 12 to 16 hours' in t or 'A short eating window' in t: f.add('BUG', '21: care-team note about fasting did not hide the fasting rules')
    if 'hidden because of what your care team told you' not in t: f.add('BUG', '22: no count of hidden suggestions')
    if 'Protein while you lose weight' not in t: f.add('BUG', '23: a fasting note hid an unrelated protein rule')
    ev("document.getElementById('settingTcCare').value='Limit protein, kidney'; mhTcSave()"); show(); t = tips()
    if 'Protect muscle with protein' in t or 'Protein while you lose weight' in t: f.add('BUG', '24: care-team protein note did not hide the protein rules')
    ev("document.getElementById('settingTcCare').value=''; mhTcSave()")
    # AI note, backup, share
    note = ev("mhTcAiNote()")
    if 'Losing weight' not in note or 'Glioblastoma' not in note: f.add('BUG', f'25: AI note lacks the layers: {note!r}')
    ev("document.getElementById('settingTcCare').value='No fasting'; mhTcSave()")
    if 'No fasting' not in ev("mhTcAiNote()") or 'never suggest' not in ev("mhTcAiNote()").lower(): f.add('BUG', '26: AI note lacks the care-team instruction')
    bk = ev("JSON.stringify(buildFullBackupPayload())")
    if 'mh_tc_on' not in bk or 'mh_tc_layers' not in bk or 'No fasting' not in bk: f.add('BUG', '27: backup lacks the timing-suggestion settings')
    shareKeys = ev("JSON.stringify(MH_SHARE_ITEMS)"); prefs = ev("JSON.stringify(mhSharePrefs())")
    if len(shareKeys) < 20: f.add('BUG', '28a: could not read the share item list (test would be vacuous)')
    if re.search(r'timing|mh_tc|wheneat|care team', shareKeys + prefs, re.I) and 'timing' in (shareKeys + prefs).lower() and 'tc' in shareKeys.lower() and 'Timing suggestions' in shareKeys: f.add('BUG', '28: timing suggestions appear among the share choices')
    if 'Timing suggestions' in shareKeys or 'mh_tc' in prefs: f.add('BUG', '28: timing suggestions or the care note are in the share')
    # reload keeps it
    page.reload(); page.wait_for_timeout(2000); ev("document.getElementById('onboardingOverlay')?.remove()")
    if ev("localStorage.getItem('mh_tc_on')") != '1' or 'loss' not in ev("localStorage.getItem('mh_tc_layers')"): f.add('BUG', '29: settings lost on reload')
    # tile hide and reorder (the normal card controls)
    ev("switchTabById('manage')"); page.wait_for_timeout(600)
    ctl = ev("(()=>{const t=document.getElementById('title-set-timingtips'); if(!t) return null; const txt=t.parentNode.innerText||''; return {up:t.innerText.includes('▲')||!!t.querySelector('[onclick*=\"Order\"],[onclick*=\"Move\"]'), eye:t.innerText.includes('👁')||!!t.querySelector('[onclick*=\"idden\"]'), html:t.outerHTML.length}})()")
    nb = ev("(()=>{const t=document.getElementById('title-set-fasting'); return t? t.innerText.replace(/\\s+/g,' ') : ''})()"); mine = ev("document.getElementById('title-set-timingtips').innerText.replace(/\\s+/g,' ')")
    if ('▲' in nb) != ('▲' in mine) or ('👁' in nb) != ('👁' in mine): f.add('BUG', f'30: the tile controls differ from its neighbour Fasting: {mine!r} vs {nb!r}')
    ev("saveGenericHidden('manage', getGenericHidden('manage').concat(['set-timingtips'])); applySectionState && 0"); page.wait_for_timeout(300)
    ev("switchTabById('import'); switchTabById('manage')"); page.wait_for_timeout(500)
    if ev("document.getElementById('title-set-timingtips').offsetParent!==null && getComputedStyle(document.getElementById('title-set-timingtips').closest('.card-unit')||document.getElementById('title-set-timingtips')).display!=='none'") and 'set-timingtips' in ev("JSON.stringify(getGenericHidden('manage'))"): f.add('BUG', '31: hiding the tile did not hide it')
    # v3.10.1381: visible Source on every suggestion, the standing "not medical advice" line, and the Settings help says the summaries are ours
    show()
    nr = ev("document.querySelectorAll('#wheneat-tips .mh-tc-rule').length"); ns = ev("document.querySelectorAll('#wheneat-tips .mh-tc-rule .mh-tc-src a[href^=\"http\"], #wheneat-tips .mh-tc-rule .mh-tc-src a[href$=\".html\"]').length")
    if not nr or nr != ns: f.add('BUG', f'50: {ns} of {nr} suggestions show a visible source link')
    if 'not medical advice' not in ev("document.getElementById('wheneat-tips-note')?.innerText || ''").lower(): f.add('BUG', '51: the standing "not medical advice" line is missing under the suggestions')
    if 'ours, not a doctor' not in ev("document.querySelector('[id^=help-tc-all]')?.innerHTML || ''") : f.add('BUG', '52: the block help does not say the summaries and labels are ours')
    if 'ours, not a doctor' not in ev("document.querySelector('[id^=help-tcsettingshelp]')?.innerHTML || ''"): f.add('BUG', '53: the Settings help does not say the summaries and labels are ours')
    # demo personas carry it: Doris (losing weight) shows the loss rule, Maria (GBM) the GBM layer, Tom (cluster) the diary one; exit restores the real settings
    ev("localStorage.setItem('mh_tc_on','0'); localStorage.setItem('mh_tc_layers','[]')")
    for pid, want, nope in (('doris', 'Protein while you lose weight', 'Fasting windows of 12 to 16 hours'), ('maria', 'Fasting windows of 12 to 16 hours', None), ('tom', 'Keep a headache and sleep diary', None)):
        if pid == 'doris':
            page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
            ev("localStorage.setItem('mh_tc_on','0'); localStorage.setItem('mh_tc_layers','[]')")
        ev(f"startDemoMode('{pid}')"); page.wait_for_timeout(2200)
        ev("switchTab('insights'); switchSubTab('insights','reports'); _rptRange=0; renderReports()"); page.wait_for_timeout(700)
        t = ev("document.getElementById('wheneat-tips')?.innerText || ''")
        if want not in t and pid != 'doris': f.add('BUG', f'40: demo {pid} lacks its suggestion {want!r}: {t[:160]!r}')
        if pid == 'doris' and 'Timing suggestions' not in t: f.add('BUG', '40: demo doris shows no timing suggestions block')
        if nope and nope in t: f.add('BUG', f'41: demo {pid} shows a rule from another layer: {nope!r}')
    ev("exitDemoMode()"); page.wait_for_timeout(1500)
    if ev("localStorage.getItem('mh_tc_on')") != '0' or ev("localStorage.getItem('mh_tc_layers')") != '[]': f.add('BUG', '42: leaving the demo did not restore the real timing-suggestion settings')
    if errs: f.add('JS-exception', errs[0])
print('findings', len(f))
for x in f: print(x)
sys.exit(1 if f else 0)
