"""Persona 67: the placeholder entry on a wearable-only day (23:59, 0 kcal, numeric date id) must not leak into things that read
meals: Top foods, the 'usual first meal' nudge, the AI's list of what was eaten yesterday, and fasting. Real meals (including a
real 23:59 meal with calories) still count."""
import sys, re, os; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from datetime import date, timedelta
from playwright.sync_api import sync_playwright
f = Findings()
dmy = lambda n: (date.today() - timedelta(days=n)).strftime('%d/%m/%y')
HTML = open(os.path.join(REPO, 'maxhealth.html'), encoding='utf-8').read()
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("localStorage.setItem('mh_onboarded','1')")
    r = page.evaluate("""(d) => {
      const stub = (n) => ({id: 20261000 + n, time:'23:59', description:'4,093 steps, 3.6h sleep, HRV 25.6', kcal:0, protein:0, fat:0, carbs:0});
      state.history = [1,2,3].map(n => ({date: d[n], mode:'standard', notes:'', log:[stub(n)], totals:{kcal:0,protein:0,fat:0,carbs:0}, steps:4000}));
      state.history.push({date: d[4], mode:'standard', notes:'', log:[{id:1760000000000,time:'23:59',description:'late supper',kcal:300,protein:20,fat:20,carbs:2,
          items:[{name:'late supper',amount:'1',kcal:300,protein:20,fat:20,carbs:2}]}], totals:{kcal:300,protein:20,fat:20,carbs:2}});
      const top = getTopFoodsData(0);
      const names = JSON.stringify(top).toLowerCase();
      return { isStub: [mhIsDeviceStub(stub(1)), mhIsDeviceStub(state.history[3].log[0]), mhIsDeviceStub(null)], hasSteps: names.includes('steps'), hasSupper: names.includes('late supper') };
    }""", [None] + [dmy(n) for n in range(1, 5)])
    if r['isStub'] != [True, False, False]: f.add('BUG', f'mhIsDeviceStub wrong: {r["isStub"]}')
    if r['hasSteps']: f.add('BUG', 'Top foods lists the wearable placeholder')
    if not r['hasSupper']: f.add('BUG', 'a real 23:59 meal went missing from Top foods')
    if errs: f.add('BUG', f'page errors: {errs[:2]}')
for name in ('checkFirstLogNudge', 'suggestMealFromLibrary'):
    m = re.search(r'function ' + name + r'\b.*?\n}\n', HTML, re.S)
    if not m or 'mhIsDeviceStub' not in m.group(0): f.add('BUG', f'{name} does not exclude the wearable placeholder')
print('findings', len(f)); sys.exit(1 if f else 0)
