"""Persona 383: the "When you eat" Reports card (v3.10.1270).
Pete (4 Nov): "we already have the ability to see what times of the day protein, fat, and carbs are consumed ... a real tool for any analysis."
Covers: hidden until 7 days have timed meals; protein, carbs and fat per part of the day (averages and shares); meals with an approximate time are left out; eating occasions a day (a new one after an hour apart), protein a meal and the biggest meal's share; follows the Reports date range; hide/show survives a reload; default order sits after Fasting; found in search; the AI context carries it. Invented data; real taps."""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from datetime import date, timedelta, datetime, time as dtime
from playwright.sync_api import sync_playwright
f = Findings()
dmy = lambda n: (date.today() - timedelta(days=n)).strftime('%d/%m/%y')
def day(n, extra=()):
    meals = [('08:00', 30, 20, 10), ('13:00', 40, 30, 20), ('19:00', 50, 40, 30), ('22:30', 10, 5, 5)] + list(extra)
    log = [{'id': 1000 + i, 'time': t, 'description': 'meal', 'kcal': 400, 'protein': p, 'carbs': c, 'fat': fa, **({'timeApprox': True} if len(m) > 4 else {})} for i, m in enumerate(meals) for (t, p, c, fa) in [m[:4]]]
    return {'date': dmy(n), 'mode': 'standard', 'notes': 'standard', 'log': log, 'totals': {'kcal': 1600, 'protein': 130, 'carbs': 95, 'fat': 65}}
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block', timezone_id='UTC')
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    ctx.clock.install(time=datetime.combine(date.today(), dtime(12, 0)))
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500); ev = page.evaluate
    ev("localStorage.setItem('mh_condition','general'); state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    show = lambda: (ev("switchTab('insights'); switchSubTab('insights','reports'); _rptRange=0; renderReports()"), page.wait_for_timeout(500))
    disp = lambda: ev("getComputedStyle(document.getElementById('wheneat-report-section')).display")
    txt = lambda: ev("(document.getElementById('wheneat-report-content')?.innerText||'')")
    # 1. too few days: hidden
    ev("state.history = " + str([day(i) for i in range(1, 6)]).replace('True', 'true') + "; saveState()"); show()
    if disp() == 'none' or not ev("!!document.getElementById('wheneat-few')") or 'All time' not in txt(): f.add('BUG', '1: fewer than 7 timed days: card says so, with its period (v3.10.1274)')
    ev("_rptRange=7; renderReports()"); page.wait_for_timeout(300)
    if 'Last 7 days' not in txt(): f.add('BUG', '1b: the card names the 7 Days period: ' + txt()[:60])
    ev("state.history = []; saveState()"); show()
    if disp() != 'none': f.add('BUG', '1c: no timed meals at all: hidden')
    ev("state.history = " + str([day(i) for i in range(1, 6)]).replace('True', 'true') + "; saveState()"); show()
    # 2. ten days, with an approximate-time meal that must be ignored
    import json
    hist = [day(i, [('15:00', 99, 99, 99, 'approx')]) for i in range(1, 11)]
    ev("state.history = " + json.dumps(hist) + "; saveState()"); show()
    if disp() == 'none': f.add('BUG', '2: shown with 10 days')
    if 'All time' not in txt() or ev("!!document.getElementById('wheneat-few')"): f.add('BUG', '2b: the full card names its period: ' + txt()[:60])
    t = txt(); tl = t.lower()
    if 'from 10 days' not in tl: f.add('BUG', f'3: says it covers 10 days: {t[:120]!r}')
    for want in ['early morning', 'late morning', 'afternoon', 'evening', 'late night', '30 g', '40 g', '50 g', '23%', '31%', '38%', '8%']:
        if want not in tl: f.add('BUG', f'4: the card shows {want!r}')
    if '99 g' in tl or '229' in tl: f.add('BUG', '5: a meal with an approximate time is left out')
    if '4' not in re.findall(r'eating occasions\s*([\d.]+)', tl.replace('\n', ' ')) and not re.search(r'eating occasions\s*4\b', tl.replace('\n', ' ')): f.add('BUG', f'6: four eating occasions a day: {tl[-200:]!r}')
    if '33 g' not in tl or '38% of the day' not in tl: f.add('BUG', '7: protein a meal (33 g) and the biggest meal share (38%)')
    # 8. follows the range
    ev("_rptRange=7; renderReports()"); page.wait_for_timeout(300)
    t7 = txt().lower()
    if disp() != 'none' and 'from 10 days' in t7: f.add('BUG', '8: the card follows the Reports date range')
    ev("_rptRange=0; renderReports()")
    # 9. hide / show survives a reload
    ev("document.getElementById('title-rpt-wheneat').scrollIntoView()")
    bb = page.locator('#title-rpt-wheneat').bounding_box(); page.mouse.click(bb['x'] + 20, bb['y'] + bb['height'] / 2); page.wait_for_timeout(300)
    if ev("getComputedStyle(document.getElementById('rpt-wheneat-wrap')).display") != 'none': f.add('BUG', '9: tapping the title hides the card body')
    page.reload(); page.wait_for_timeout(1500); show()
    if ev("getComputedStyle(document.getElementById('rpt-wheneat-wrap')).display") != 'none': f.add('BUG', '10: hidden stays hidden after a reload')
    ev("document.getElementById('title-rpt-wheneat').scrollIntoView()")
    bb = page.locator('#title-rpt-wheneat').bounding_box(); page.mouse.click(bb['x'] + 20, bb['y'] + bb['height'] / 2); page.wait_for_timeout(300)
    if ev("getComputedStyle(document.getElementById('rpt-wheneat-wrap')).display") == 'none': f.add('BUG', '11: shows again')
    # 12. order, search, AI context
    o = ev("GENERIC_DEFAULT_ORDER.reports")
    if 'rpt-wheneat' not in o or o.index('rpt-wheneat') != o.index('rpt-fasting') + 1: f.add('BUG', f'12: default order sits after Fasting: {o}')
    if not ev("SITE_SEARCH_SETTINGS.some(x=>x.key==='rpt-wheneat' && /when you eat/i.test(x.label))"): f.add('BUG', '13: found in search')
    ctxo = ev("JSON.stringify(buildPatientContext(state.history)||{}).includes('WHEN THEY EAT') || (()=>{try{return !!buildPatientContext(state.history).whenEat}catch(e){return false}})()")
    if not ctxo: f.add('BUG', '14: the AI context carries it')
    ev("document.getElementById('wheneat-report-section').scrollIntoView()"); page.screenshot(path='/tmp/p383.png')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
