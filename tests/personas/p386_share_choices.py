"""Persona 386: the person decides what a carer/clinician link shows (v3.10.1277).
Pete (4 Nov): clinician sharing is governed by the user in Settings; presets are only starting points; diabetes team wants foods by time of day, oncology wants intake around treatment and supplements.
Covers: role chips set a starting set, each item can then be changed, totals are always on, new items (time of day, meals and food names, treatment sessions) are OFF by default, choices survive a reload, the link payload holds only what is ticked, the carer page shows the extras and escapes names, and the summary line says what is and is not shown. Invented data; real taps."""
import sys, re, json, base64, urllib.parse; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from datetime import date, timedelta
from playwright.sync_api import sync_playwright
f = Findings()
dmy = lambda n: (date.today() - timedelta(days=n)).strftime('%d/%m/%Y')
def day(n):
    log = [{'id': n * 10 + i, 'time': t, 'description': nm, 'kcal': 400, 'protein': p, 'carbs': c, 'fat': fa} for i, (t, nm, p, c, fa) in enumerate([('08:00', 'Zzqx Eggs', 20, 2, 15), ('13:00', '<b>Zzqx Chicken</b>', 40, 3, 10), ('19:00', 'Zzqx Steak', 50, 4, 30)])]
    return {'date': dmy(n), 'mode': 'standard', 'notes': 'standard', 'weight': 80, 'log': log, 'totals': {'kcal': 1600, 'protein': 110, 'carbs': 9, 'fat': 55}}
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    page = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block').new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("state.history = " + json.dumps([day(i) for i in range(1, 13)]) + "; saveState()")
    ev("mhTreatmentSeed = 0"); ev("localStorage.setItem('mh_treatment_defs', JSON.stringify([{id:'t1',name:'Zzqx Session'}])); localStorage.setItem('mh_treatment_log', JSON.stringify([{id:'a',treatmentId:'t1',date:'" + dmy(2) + "',time:'10:00',note:'PRIVATE NOTE'}]))")
    ev("localStorage.setItem('mh_name','<i>Pat</i>')")
    def go(): ev("switchTab('settings'); try{switchSubTab('settings','manage')}catch(e){}; mhShareRender(); document.getElementById('shareItems').scrollIntoView()"); page.wait_for_timeout(300)
    def tap(sel):
        ev("document.querySelectorAll('.toast').forEach(t=>t.style.display='none')")
        page.locator(sel).first.scroll_into_view_if_needed(); bb = page.locator(sel).first.bounding_box(); page.mouse.move(bb['x'] + bb['width'] / 2, bb['y'] + bb['height'] / 2); page.mouse.down(); page.mouse.up(); page.wait_for_timeout(300)
    go()
    on = lambda k: ev(f"document.querySelector('#shareItems [data-k={k}]').checked")
    # 1 defaults: today's behaviour kept, new things off
    if not (on('totals') and on('weight') and on('exercise') and on('sleep')): f.add('BUG', '1: totals, weight, exercise, sleep on by default')
    if on('timing') or on('meals') or on('treat'): f.add('BUG', '1b: time of day, meals and treatment are OFF by default')
    if not ev("document.querySelector('#shareItems [data-k=totals]').disabled"): f.add('BUG', '1c: totals cannot be switched off')
    # 2 payload by default
    def link():
        ev("generateCarerLink()"); page.wait_for_timeout(300)
        u = ev("document.querySelector('#carerLinkOutput textarea').value"); return json.loads(urllib.parse.unquote(base64.b64decode(u.split('#', 1)[1]).decode('latin1').encode('latin1').decode('utf8') if False else base64.b64decode(u.split('#', 1)[1]).decode('utf8'))), u
    pl, url = link()
    if 'timing' in pl or 'treat' in pl or any('m' in d for d in pl['history']): f.add('BUG', '2: default link carries no time of day, meals or treatment')
    if 'Zzqx' in json.dumps(pl): f.add('BUG', '2b: no food names in the default link')
    # 3 Diabetes team chip: a starting set
    tap('#shareRoles [data-role=diab]')
    if not (on('timing') and on('meals') and not on('treat') and not on('exercise')): f.add('BUG', '3: Diabetes team starts with time of day and meals, not treatment or exercise')
    # 4 changeable after
    tap('#shareItems [data-k=treat]')
    if not on('treat') or ev("document.querySelector('#shareRoles .active')"): f.add('BUG', '4: a switch can be changed after choosing a role (and the role chip then clears)')
    # 5 payload follows
    pl, url = link()
    if 'timing' not in pl or not pl['timing']['bands']: f.add('BUG', '5: timing in the link')
    if not any('m' in d for d in pl['history']) or sum(1 for d in pl['history'] if 'm' in d) != 10: f.add('BUG', '5b: meals only for the last 10 days: ' + str(sum(1 for d in pl['history'] if 'm' in d)))
    if 'treat' not in pl or not pl['treat'] or 'PRIVATE NOTE' in json.dumps(pl): f.add('BUG', '5c: treatment sessions listed, note not shared')
    if 'exercise' in pl['shared'] or any('ex' in d for d in pl['history']): f.add('BUG', '5d: exercise left out when off')
    if 'Eggs' not in json.dumps(pl): f.add('BUG', '5e: food names present when meals are on')
    txt = ev("document.getElementById('carerLinkShows').innerText")
    if 'Shows:' not in txt or 'Not shown:' not in txt or 'exercise' not in txt.split('Not shown:')[1]: f.add('BUG', '5f: the link says what it shows and what it does not: ' + txt)
    # 6 reload keeps it
    page.reload(); page.wait_for_timeout(1500); ev("document.getElementById('onboardingOverlay')?.remove()"); go()
    if not (on('timing') and on('meals') and on('treat') and not on('exercise')): f.add('BUG', '6: choices survive a reload')
    # 7 the carer page
    p2 = page.context.new_page(); p2.on('pageerror', lambda e: errs.append('carer: ' + str(e)[:200]))
    p2.goto(url.replace('https://', 'http://') if url.startswith('http://localhost') else 'http://localhost:5757/carer.html#' + url.split('#', 1)[1]); p2.wait_for_timeout(1200)
    t2 = p2.evaluate("document.body.innerText").lower()
    for need in ['Grams by time of day', 'Treatment sessions', 'Zzqx Session', 'Meals, last 10 days', 'Zzqx Eggs']:
        if need.lower() not in t2: f.add('BUG', f'7: carer page shows {need!r}')
    if p2.evaluate("!!document.querySelector('#app b, #app i')"): f.add('BUG', '7b: names (including the person\'s own name in the link) are escaped, not rendered as markup')
    if '<b>zzqx chicken</b>' not in t2: f.add('BUG', '7c: a name with markup shows as plain text')
    p2.evaluate("[...document.querySelectorAll('.section-title')].find(e=>/time of day/i.test(e.innerText)).scrollIntoView()"); p2.screenshot(path='/tmp/p386_carer.png')
    # 7d preview inside the app, before sending (v3.10.1281)
    page.bring_to_front(); ev("mhShareRole('diab')"); pl, url = link(); tap('#carerPreviewBtn'); page.wait_for_timeout(1500)
    if not ev("!!document.getElementById('carerPreviewModal')"): f.add('BUG', '7d: the preview opens')
    fr = [x for x in page.frames if 'carer.html' in x.url]
    if not fr or 'grams by time of day' not in fr[0].evaluate("document.body.innerText").lower(): f.add('BUG', '7e: the preview shows the page the link makes')
    page.screenshot(path='/tmp/p386_preview.png')
    ev("document.getElementById('carerPreviewModal').remove()")
    # 7f report profiles: timing series can be picked, but are never pre-ticked
    ev("openReportProfileWizard()"); page.wait_for_timeout(300)
    d = ev("window._reportWizardDraft.metrics"); ev("closeReportProfileWizard()")
    if any(k in d for k in ['meal_n', 'meal_first', 'meal_last', 'am_protein', 'eve_carbs']) or 'calories' not in d: f.add('BUG', '7f: a new report profile starts without the timing series: ' + str(d)[:80])
    if not ev("getAllOverlayableMetrics().some(m => m.key === 'meal_last')"): f.add('BUG', '7g: the timing series can be chosen for a report profile')
    # 7h supplements: off by default, on for Oncology team, list only (name, dose, when), shown on the carer page, gone when off
    ev("localStorage.setItem('mh_supplement_defs', JSON.stringify([{id:'s1',name:'Zzqx Vitamin',dose:'500mg',periods:['morning'],active:true},{id:'s2',name:'Zzqx Retired',dose:'1g',periods:['evening'],active:false}]))")
    ev("mhShareToggle('supps',false)"); pl, url = link()
    if 'supps' in pl or 'supps' in pl.get('shared', []): f.add('BUG', '7h: supplements off means not in the link')
    ev("mhShareRole('onc')")
    if not ev("mhSharePrefs().items.supps"): f.add('BUG', '7i: Oncology team starts with supplements')
    pl, url = link()
    if pl.get('supps') != [['Zzqx Vitamin', '500mg', 'morning']]: f.add('BUG', '7j: only active supplements, name dose when: ' + str(pl.get('supps')))
    p2.goto('http://localhost:5757/carer.html#' + url.split('#', 1)[1]); p2.reload(); p2.wait_for_timeout(1000); t4 = p2.evaluate("document.body.innerText")
    if 'Zzqx Vitamin' not in t4 or '500mg' not in t4 or 'Zzqx Retired' in t4: f.add('BUG', '7k: carer page lists the active supplement only')
    # 8 default link on the carer page shows none of the extras
    page.bring_to_front(); ev("mhShareToggle('timing',false); mhShareToggle('meals',false); mhShareToggle('treat',false); mhShareToggle('supps',false)"); pl, url = link()
    p2.goto('http://localhost:5757/carer.html#' + url.split('#', 1)[1]); p2.reload(); p2.wait_for_timeout(1000); t3 = p2.evaluate("document.body.innerText").lower().lower()
    if any(x in t3 for x in ['grams by time of day', 'treatment sessions', 'meals, last 10 days', 'zzqx']): f.add('BUG', '8: nothing extra on the page when all are off: ' + str([x for x in ['grams by time of day', 'treatment sessions', 'meals, last 10 days', 'zzqx'] if x in t3]) + str(pl.get('shared')))
    go(); page.screenshot(path='/tmp/p386_settings.png')
    if errs: f.add('BUG', f'page errors {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
