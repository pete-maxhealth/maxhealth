"""Persona 387: meal-timing series in Compare Metrics (v3.10.1278).
Pete (4 Nov): "These extra nuggets could feed into the multiple metrics graph?" Covers: five new series (eating occasions, first meal, last meal, protein before noon, carbs after 5pm) from logged meal times, correct values for a known day, approximate-time and medication entries left out, listed in the Nutrition group of the picker, selectable and drawn in the overlay with a neighbour series, a day with no timed meals gives no point. Invented data; real taps."""
import sys, json; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from datetime import date, timedelta
from playwright.sync_api import sync_playwright
f = Findings()
dmy = lambda n: (date.today() - timedelta(days=n)).strftime('%d/%m/%y')
def day(n, meals):
    log = [{'id': n * 10 + i, 'time': t, 'description': 'Zzqx meal', 'kcal': 400, 'protein': p, 'carbs': c, 'fat': (5 if (p or c) else 0), **({'timeApprox': True} if a else {})} for i, (t, p, c, a) in enumerate(meals)]
    return {'date': dmy(n), 'mode': 'standard', 'notes': 'standard', 'weight': 80, 'log': log, 'totals': {'kcal': 1600, 'protein': 100, 'carbs': 20, 'fat': 60}}
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    page = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block').new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    H = [day(1, [('08:00', 30, 2, 0), ('08:20', 10, 1, 0), ('13:00', 40, 3, 0), ('18:00', 20, 6, 0), ('21:30', 5, 4, 0), ('15:00', 99, 99, 1)]), day(2, [('09:30', 25, 2, 0), ('19:00', 45, 5, 0)]), day(3, [('10:00', 0, 0, 0)])]
    ev("state.history = " + json.dumps(H) + "; saveState()")
    v = lambda k: ev(f"getDrillData({k!r}, 0).map(d => d.date + ':' + d.val)")
    d1, d2 = dmy(1), dmy(2)
    exp = {'meal_n': [f'{d1}:4', f'{d2}:2'], 'meal_first': [f'{d1}:8', f'{d2}:9.5'], 'meal_last': [f'{d1}:21.5', f'{d2}:19'], 'am_protein': [f'{d1}:40', f'{d2}:25'], 'eve_carbs': [f'{d1}:10', f'{d2}:5']}
    for k, e in exp.items():
        got = sorted(v(k)); 
        if got != sorted(e): f.add('BUG', f'1: {k} expected {e} got {got}')
    if len(v('meal_n')) != 2: f.add('BUG', '2: a day with no usable timed meals (zero macros) gives no point: ' + str(v('meal_n')))
    if not ev("['meal_n','meal_first','meal_last','am_protein','eve_carbs'].every(k => MM_METRIC_GROUPS.find(g => g.label==='Nutrition').match({key:k}) && !!DRILL_CONFIG[k])"): f.add('BUG', '3: all five in the Nutrition group of Compare Metrics')
    ev("_mmSelectedMetrics=['calories']; openMultiMetricOverlay()"); page.wait_for_timeout(600)
    ev("_mmExpandedGroups.add('Nutrition'); renderMMMetricPicker()"); page.wait_for_timeout(300)
    if 'Eating occasions' not in ev("document.getElementById('mmMetricPicker').innerText") or 'Carbs after 5pm' not in ev("document.getElementById('mmMetricPicker').innerText"): f.add('BUG', '4: picker lists the new series')
    ev("toggleMMMetric('meal_last')"); page.wait_for_timeout(500); ev("toggleMMMetric('eve_carbs')"); page.wait_for_timeout(800)
    if not ev("_mmSelectedMetrics.includes('meal_last') && _mmSelectedMetrics.includes('eve_carbs')"): f.add('BUG', '5: series can be selected')
    if not ev("!!document.querySelector('#multiMetricOverlay canvas')"): f.add('BUG', '6: chart drawn')
    page.screenshot(path='/tmp/p387.png')
    if errs: f.add('BUG', f'page errors {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
