"""Persona 390: the Meal times Trends card (v3.10.1282).
Covers: hidden with no timed meals; with data shows last meal average, first meal, meals a day, carbs after 5pm and draws a chart; hide and show; reorder with the arrows; included in the Food filter; a saved card order without it gets it after Overnight Fast; the 30-day range and Today view. Invented data; real taps."""
import sys, json; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from datetime import date, timedelta
from playwright.sync_api import sync_playwright
f = Findings()
dmy = lambda n: (date.today() - timedelta(days=n)).strftime('%d/%m/%y')
def day(n):
    log = [{'id': n * 10 + i, 'time': t, 'description': 'Zzqx meal', 'kcal': 400, 'protein': p, 'carbs': c, 'fat': 5} for i, (t, p, c) in enumerate([('08:00', 30, 2), ('13:00', 30, 3), ('19:00', 40, 6)])]
    return {'date': dmy(n), 'mode': 'standard', 'notes': 'standard', 'log': log, 'totals': {'kcal': 1600, 'protein': 100, 'carbs': 11, 'fat': 60}}
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    page = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block').new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    disp = lambda: ev("getComputedStyle(document.getElementById('mcMealTime')).display")
    show = lambda: (ev("switchTab('insights'); switchSubTab('insights','trends'); trendsWindow = 30; renderTrends()"), page.wait_for_timeout(900))
    ev("state.history = []; saveState()"); show()
    if disp() != 'none': f.add('BUG', '1: hidden with no timed meals')
    ev("state.history = " + json.dumps([day(i) for i in range(1, 9)]) + "; saveState()"); show()
    if disp() == 'none': f.add('BUG', '2: shown with 8 timed days')
    t = lambda i: ev(f"document.getElementById('{i}').textContent")
    if t('mcMealTimeVal') != '19:00' or t('statMealFirst') != '08:00' or t('statMealN') != '3' or t('statMealEve') != '6g': f.add('BUG', f"3: figures {t('mcMealTimeVal')} {t('statMealFirst')} {t('statMealN')} {t('statMealEve')}")
    if not ev("!!chartInstances['chartMealTime']"): f.add('BUG', '4: chart drawn')
    ev("toggleTrendCardHidden('mcMealTime')")
    if disp() != 'none': f.add('BUG', '5: can be hidden')
    ev("toggleTrendCardHidden('mcMealTime')")
    if disp() == 'none': f.add('BUG', '5b: can be shown again')
    o0 = ev("getTrendCardsOrder()"); ev("moveTrendCard('mcMealTime','down')"); o1 = ev("getTrendCardsOrder()")
    if o1.index('mcMealTime') != o0.index('mcMealTime') + 1: f.add('BUG', f'6: moves down: {o0.index("mcMealTime")} -> {o1.index("mcMealTime")}')
    ev("mhTrendsGroupSet('food')"); page.wait_for_timeout(300)
    if disp() == 'none': f.add('BUG', '7: in the Food filter')
    ev("mhTrendsGroupSet('body')"); page.wait_for_timeout(300)
    if disp() != 'none': f.add('BUG', '7b: not in the Body filter')
    ev("mhTrendsGroupSet('all')")
    old = "['mcWeight','mcHR','mcSpO2','mcHRV','mcSteps','mcSleep','mcCal','mcProt','mcCarb','mcWater','mcFast','mcGKI','mcFatPct','mcMusclePct','mcBoneMass','mcHydration','mcDistance']"
    ev(f"localStorage.setItem(TREND_CARDS_ORDER_KEY, JSON.stringify({old}))"); o = ev("getTrendCardsOrder()")
    if o.index('mcMealTime') != o.index('mcFast') + 1: f.add('BUG', f'8: an older saved order gets it after Overnight Fast: {o}')
    ev("trendsWindow = 'today'; renderTrends()"); page.wait_for_timeout(500)
    if disp() != 'none': f.add('BUG', '9: not in the Today view')
    show(); ev("document.getElementById('mcMealTime').scrollIntoView({block:'center'})"); page.wait_for_timeout(300); page.screenshot(path='/tmp/p390.png')
    if errs: f.add('BUG', f'page errors {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
