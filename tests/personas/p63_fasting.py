"""Persona 63: Fasting, embodied across the app. Fasts are measured from logged meal times (no new entry): overnight fast,
eating window, threshold for what breaks a fast, late-night meals, approximate-time entries ignored, multi-day fasts only when the
days between are tagged Fasting. Checks the Today card (with hide and order migration), Settings, the Trends card (with order
migration), Compare Metrics, the Reports section, the AI context and the condition notes, for a user with no condition and for
diabetes / ketogenic users, and that someone with no data sees nothing broken."""
import sys, os, re, json; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from datetime import date, timedelta
from playwright.sync_api import sync_playwright
f = Findings()
dmy = lambda n: (date.today() - timedelta(days=n)).strftime('%d/%m/%y')
def day(n, meals, notes='standard', **extra):
    log = [{'id': 1000 + i, 'time': t, 'description': 'meal', 'kcal': k, 'protein': 20, 'fat': 20, 'carbs': 8, **({'timeApprox': True} if ap else {})} for i, (t, k, ap) in enumerate(meals)]
    return {'date': dmy(n), 'mode': 'standard', 'notes': notes, 'log': log, 'totals': {'kcal': sum(m[1] for m in meals), 'protein': 20 * len(meals), 'fat': 20 * len(meals), 'carbs': 8 * len(meals)}, **extra}
M = lambda t, k=500, ap=False: (t, k, ap)
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("localStorage.setItem('mh_condition','general')")
    # ---- 0. a brand-new user with nothing logged: nothing breaks ----
    page.evaluate("state.history = []; state.todayLog = []; saveState(); updateDashboard()"); page.wait_for_timeout(400)
    if 'starts timing' not in page.evaluate("document.getElementById('fastNowSub').textContent"): f.add('BUG', 'empty state wording missing on the Today card')
    page.evaluate("switchTab('insights'); switchSubTab('insights','trends'); renderTrends()"); page.wait_for_timeout(500)
    if page.evaluate("getComputedStyle(document.getElementById('mcFast')).display") != 'none': f.add('BUG', 'Trends fast card shown with no data')
    # ---- 1. the measuring rules ----
    hist = [
        day(10, [M('08:00'), M('13:00'), M('19:30')]),                   # last meal 19:30
        day(9,  [M('07:00', 5), M('11:00'), M('18:00')]),                # coffee under threshold ignored: first real 11:00 -> fast 15.5h; window 7h
        day(8,  [M('12:00'), M('20:00'), M('01:00')]),                   # 01:00 snack = late end of this day -> last 25:00
        day(7,  [M('09:00')]),                                           # fast = 09:00 - 01:00 = 8h ; single meal window 0
        day(6,  [M('08:30'), M('18:30')]),                               # fast 23.5h
        day(5,  [M('08:00'), M('21:00', 500, True)]),                    # 21:00 is approximate: ignored -> window 0
        day(4,  [M('08:00'), M('19:00')]),                               # fast from 08:00(d5) = 24h
        day(3,  [M('09:00'), M('19:00')]),                               # fast 14h
        day(2, [], 'Fasting'), day(1, [], 'Fasting'),                    # two tagged days, no meals
        day(0, [M('08:00', 450)]),                                       # extended fast from day 3 19:00 to day 0 08:00 = 61h
    ]
    page.evaluate("h => { state.history = h.slice(0, -1); state.todayLog = h[h.length-1].log; state.notes = 'standard'; saveState(); }", hist)
    m = page.evaluate("Object.fromEntries([...mhFastingMap()].map(([k,v]) => [k, {f: v.fastH, w: v.windowH, e: v.extended}]))")
    near = lambda a, b: a is not None and abs(a - b) < 0.02
    chk = lambda n, key, fh, wh=None, ext=False: (near((m.get(dmy(n)) or {}).get(key), fh) if fh is not None else (m.get(dmy(n)) or {}).get(key) is None)
    if m.get(dmy(10), {}).get('f') is not None: f.add('BUG', 'first ever day should have no fast')
    if not near(m[dmy(9)]['f'], (24 - 19.5) + 11): f.add('BUG', f'coffee under the threshold broke the fast: {m[dmy(9)]}')
    if not near(m[dmy(9)]['w'], 7): f.add('BUG', f'eating window wrong: {m[dmy(9)]}')
    if not near(m[dmy(7)]['f'], 8): f.add('BUG', f'late-night 01:00 meal not treated as the end of that day: {m[dmy(7)]}')
    if not near(m[dmy(7)]['w'], 0): f.add('BUG', 'single-meal day should have a 0 window')
    if not near(m[dmy(6)]['f'], 23.5): f.add('BUG', f'fast across a day wrong: {m[dmy(6)]}')
    if not near(m[dmy(5)]['w'], 0): f.add('BUG', 'approximate-time entry was counted')
    if not near(m[dmy(4)]['f'], 24): f.add('BUG', f'fast after an ignored approximate entry wrong: {m[dmy(4)]}')
    if not near(m[dmy(3)]['f'], 14): f.add('BUG', f'fast wrong: {m[dmy(3)]}')
    if not (m[dmy(0)]['e'] and near(m[dmy(0)]['f'], 61)): f.add('BUG', f'tagged multi-day fast not recognised: {m[dmy(0)]}')
    # without the tags the same gap is NOT a fast
    page.evaluate("state.history.forEach(d => { if (d.notes === 'Fasting') d.notes = 'standard'; }); saveState()")
    m2 = page.evaluate("Object.fromEntries([...mhFastingMap()].map(([k,v]) => [k, v.fastH]))")
    if m2.get(dmy(0)) is not None: f.add('BUG', 'an unlogged gap was counted as a fast without the Fasting tag')
    page.evaluate("state.history.forEach(d => { if (!d.log.length) d.notes = 'Fasting'; }); saveState()")
    # ---- 2. threshold setting changes the answer ----
    page.evaluate("localStorage.setItem('mh_fasting_kcal_threshold','0')")
    z = page.evaluate("mhFastingMap().get(arguments[0])", dmy(9)) if False else page.evaluate("d => mhFastingMap().get(d).fastH", dmy(9))
    if not near(z, (24 - 19.5) + 7): f.add('BUG', f'threshold 0 should let the 5 kcal coffee count: {z}')
    page.evaluate("localStorage.removeItem('mh_fasting_kcal_threshold')")
    # ---- 3. Today card, live ----
    page.evaluate("""() => { const d = new Date(Date.now() - 5*60000); const t = String(d.getHours()).padStart(2,'0')+':'+String(d.getMinutes()).padStart(2,'0');
        state.todayLog = [{id: 5001, time: t, description: 'x', kcal: 400, protein: 20, fat: 20, carbs: 5}]; saveState(); updateDashboard(); }""")
    page.evaluate("switchTab('today')"); page.wait_for_timeout(500)
    now_txt = page.evaluate("document.getElementById('fastNowVal').textContent")
    if page.evaluate("new Date().getHours()*60+new Date().getMinutes()") >= 6 and not re.match(r'^\d+m$', now_txt): f.add('BUG', f'live timer should read minutes after a meal 5 min ago, got {now_txt!r}')
    if 'goal 12h' not in page.evaluate("document.getElementById('fastNowSub').textContent"): f.add('BUG', 'goal missing on the Today card')
    if 'Last fast' not in page.evaluate("document.getElementById('fastLastLine').textContent"): f.add('BUG', 'last completed fast not shown')
    # hide / show and order
    page.evaluate("toggleDashboardSectionHidden('fasting')")
    if page.evaluate("getComputedStyle(document.getElementById('dashSection-fasting')).display") != 'none': f.add('BUG', 'Fasting card cannot be hidden')
    page.evaluate("toggleDashboardSectionHidden('fasting')")
    page.evaluate("localStorage.setItem('mh_dashboard_order', JSON.stringify(['weight','daymode','ketosis','macros','macroratio','goalcheck','steps','symptoms','treatment','activity','water','log','guides']))")
    o = page.evaluate("getDashboardOrder()")
    if 'fasting' not in o or o.index('fasting') != o.index('water') - 1 or 'weather' not in o: f.add('BUG', f'saved Today order not migrated: {o}')
    page.evaluate("moveDashboardSection('fasting','up')")
    if page.evaluate("getDashboardOrder().indexOf('fasting')") >= o.index('fasting'): f.add('BUG', 'Fasting card cannot be moved up')
    # ---- 4. settings ----
    page.evaluate("switchTab('settings'); switchSubTab('settings','manage')"); page.wait_for_timeout(600)
    page.evaluate("mhLoadFastingSettings()")
    if page.evaluate("document.getElementById('settingFastGoal').value") != '12': f.add('BUG', 'goal field should default to 12')
    page.fill('#settingFastGoal', '14'); page.evaluate("mhSaveFastingSettings()")
    if page.evaluate("mhFastGoalH()") != 14: f.add('BUG', 'goal not saved')
    if 'goal 14h' not in page.evaluate("document.getElementById('fastNowSub').textContent"): f.add('BUG', 'Today card did not pick up the new goal')
    if 'mh_fasting_goal_h' not in page.evaluate("Object.keys(localStorage).filter(k => k.startsWith('mh_')).join(',')"): f.add('BUG', 'goal not in an mh_ key (so not in backups)')
    # ---- 5. Trends card + order migration + hide ----
    page.evaluate("localStorage.setItem('mh_trend_cards_order', JSON.stringify(['mcWeight','mcHR','mcSpO2','mcHRV','mcSteps','mcSleep','mcCal','mcProt','mcCarb','mcWater','mcGKI','mcFatPct','mcMusclePct','mcBoneMass','mcHydration','mcDistance']))")
    ko = page.evaluate("typeof TREND_CARDS_ORDER_KEY !== 'undefined' ? TREND_CARDS_ORDER_KEY : null")
    if ko: page.evaluate("k => localStorage.setItem(k, JSON.stringify(['mcWeight','mcHR','mcSpO2','mcHRV','mcSteps','mcSleep','mcCal','mcProt','mcCarb','mcWater','mcGKI','mcFatPct','mcMusclePct','mcBoneMass','mcHydration','mcDistance']))", ko)
    to = page.evaluate("getTrendCardsOrder()")
    if 'mcFast' not in to or to.index('mcFast') != to.index('mcWater') + 1: f.add('BUG', f'saved Trends order not migrated: {to}')
    page.evaluate("switchTab('insights'); switchSubTab('insights','trends'); trendsWindow = 30; renderTrends()"); page.wait_for_timeout(900)
    if page.evaluate("getComputedStyle(document.getElementById('mcFast')).display") == 'none': f.add('BUG', 'Trends fast card not shown with data')
    if page.evaluate("document.getElementById('mcFastVal').textContent") in ('', '—'): f.add('BUG', 'Trends fast card has no average')
    if not page.evaluate("!!chartInstances['chartFast']"): f.add('BUG', 'Trends fast chart not drawn')
    page.evaluate("toggleTrendCardHidden('mcFast')")
    if page.evaluate("getComputedStyle(document.getElementById('mcFast')).display") != 'none': f.add('BUG', 'Trends fast card cannot be hidden')
    page.evaluate("toggleTrendCardHidden('mcFast')")
    # ---- 6. Compare Metrics ----
    dd = page.evaluate("getDrillData('fast_h', 0).map(d => d.val)")
    if len(dd) < 5: f.add('BUG', f'Compare Metrics has too few fast values: {dd}')
    if not page.evaluate("MM_METRIC_GROUPS.some(g => g.match({key:'fast_h'}) && g.match({key:'eat_window'}))"): f.add('BUG', 'fast metrics not in a Compare group')
    if len(page.evaluate("getDrillData('eat_window', 0)")) < 3: f.add('BUG', 'eating window metric empty')
    # ---- 7. Reports (needs 7 fasts) ----
    more = [day(n, [M('08:00'), M('18:00')], sleep_duration=420 + (n % 3) * 30) for n in range(20, 10, -1)]
    page.evaluate("m => { state.history = m.concat(state.history); saveState(); }", more)
    page.evaluate("localStorage.setItem('mh_fasting_goal_h','16')")
    page.evaluate("switchTab('insights'); switchSubTab('insights','reports')"); page.wait_for_timeout(600)
    page.evaluate("renderFastingReport()")
    if page.evaluate("getComputedStyle(document.getElementById('fasting-report-section')).display") == 'none': f.add('BUG', 'Fasting report hidden with enough data')
    txt = page.evaluate("document.getElementById('fasting-report-content').textContent")
    if 'average overnight fast' not in txt or 'association' not in txt.lower(): f.add('BUG', f'Fasting report content wrong: {txt[:120]}')
    page.evaluate("toggleSection('rpt-fasting','rpt-fasting-wrap','rpt-fasting-icon')")
    if page.evaluate("getComputedStyle(document.getElementById('rpt-fasting-wrap')).display") != 'none': f.add('BUG', 'Fasting report cannot be collapsed')
    if 'rpt-fasting' not in page.evaluate("JSON.stringify(GENERIC_DEFAULT_ORDER.reports)"): f.add('BUG', 'report not in the reorder list')
    # ---- 8. AI context ----
    ctxf = page.evaluate("(() => { const c = buildPatientContext(state.history); return c.fasting ? {n: c.fasting.nFasts, g: c.fasting.goal} : null; })()")
    if not ctxf or ctxf['n'] < 3: f.add('BUG', f'AI context has no fasting: {ctxf}')
    src = open(os.path.join(REPO, 'maxhealth.html'), encoding='utf-8').read()
    if "do not tell them to fast more or less" not in src: f.add('BUG', 'AI fasting rule missing')
    # ---- 8b. help tip: longer is not better, keto, medication with fat or protein ----
    for k in ('Longer is not better', 'ketogenic diet', 'medicine with fat or protein', 'Never skip or delay a dose'):
        if k not in src: f.add('BUG', f'fasting help tip missing: {k}')
    page.evaluate("switchTab('today')"); page.wait_for_timeout(300)
    page.evaluate("initHelpSlots()")
    if not page.evaluate("!!document.getElementById('help-fastinghelp')"): f.add('BUG', 'Today fasting help tip not created')
    # ---- 9. conditions ----
    for cond, want in (('general', ''), ('t1_diabetes', 'insulin'), ('t2_diabetes', 'insulin'), ('epilepsy', 'anti-seizure'), ('migraine', 'migraine'), ('gbm', 'ketones'), ('strict_keto', 'ketones')):
        page.evaluate("c => { localStorage.setItem('mh_condition', c); mhRenderFastingCard(); }", cond)
        shown = page.evaluate("getComputedStyle(document.getElementById('fastCaution')).display !== 'none' ? document.getElementById('fastCaution').textContent : ''")
        if want and want not in shown: f.add('BUG', f'{cond}: condition note missing ({shown[:60]!r})')
        if not want and shown: f.add('BUG', f'{cond}: unexpected note {shown[:60]!r}')
    if errs: f.add('JS-exception', str(errs[:3]))
    b.close()
print('findings', len(f)); sys.exit(1 if f else 0)
