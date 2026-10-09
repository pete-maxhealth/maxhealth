"""Persona 66: a day with only wearable data (placeholder entry at 23:59, 0 kcal) must not show a bogus 'Meals - by calorie
contribution' card; a day with a real meal still shows it, and the placeholder is not listed among the meals."""
import sys, re; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
def stub(n=20261009): return {'id': n, 'time': '23:59', 'description': '4,093 steps, 3.6h sleep, HRV 25.6, SpO2 94.7%', 'kcal': 0, 'protein': 0, 'fat': 0, 'carbs': 0}
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("localStorage.setItem('mh_onboarded','1')")
    def show(log, kcal):
        page.evaluate("""([log,kcal]) => { state.todayLog = []; state.history = []; saveState();
          renderDailyView([{date: todayStr(), mode:'standard', log, totals:{kcal,protein:0,fat:0,carbs:0}, steps:4093, sleep_duration:414}]); }""", [log, kcal])
        return page.evaluate("(()=>{const w=document.getElementById('dv-meals-wrap'); return w ? w.innerText : null})()")
    page.evaluate("switchTab('insights'); switchSubTab('insights','trends')"); page.wait_for_timeout(500)
    if show([stub()], 0) is not None: f.add('BUG', 'wearable-only day still shows a Meals card')
    t = show([stub(), {'id': 1760000000000, 'time': '12:30', 'description': 'omelette', 'kcal': 450, 'protein': 30, 'fat': 35, 'carbs': 2}], 450)
    if not t or 'omelette' not in t: f.add('BUG', 'real meal missing from the Meals card')
    elif '4,093' in t: f.add('BUG', 'placeholder listed among the meals')
    if errs: f.add('BUG', f'page errors: {errs[:2]}')
print('findings', len(f)); sys.exit(1 if f else 0)
