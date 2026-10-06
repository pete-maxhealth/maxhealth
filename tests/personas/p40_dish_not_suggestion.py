"""Persona 40: a typed dish ('Ceaser salad with beef bacon') is logged, not hijacked into library suggestions; real structured requests still work."""
import sys, re, json; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    def route(r):
        u = r.request.url
        if u.startswith('http://localhost'): return r.continue_()
        if 'openfoodfacts' in u:
            return r.fulfill(status=200, content_type='application/json', headers={'access-control-allow-origin': '*'}, body=json.dumps({'status': 0}))
        r.abort()
    ctx.route(re.compile(r'^https?://'), route)
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:160])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200)
    page.evaluate("onboardNext(2)"); page.fill('#onboardName', 'Ola'); page.evaluate("onboardNext(3)")
    page.evaluate("obSetSex('male')"); page.fill('#onboardAge', '58'); page.fill('#onboardHeight', '176')
    page.fill('#onboardWeight', '82'); page.fill('#onboardTarget', '78')
    page.evaluate("onboardNext(4)"); page.evaluate("obSetActivity('light')"); page.evaluate("obSetGoal('lose')")
    page.evaluate("onboardNext(5)"); page.evaluate("obSetCondition('general')")
    page.evaluate("onboardNext(6)"); page.evaluate("onboardFinish()"); page.wait_for_timeout(1500)
    page.evaluate("switchTabById('log')"); page.wait_for_timeout(300)
    res = page.evaluate("""(() => {
      const calls = []; window.suggestMealFromLibrary = (k, c) => calls.push(k);
      const T = {kcal:0,protein:0,carbs:0,fat:0}, G = {kcal:2000,protein:100,carbs:20};
      const out = {};
      for (const ph of ['ceaser salad with beef bacon','chicken breast and rice','steak with salad','meat and 2 veg','protein and pasta','chicken and 2 veg','meat and veg']) {
        calls.length = 0; const handled = handleNextMealQuery(ph, T, G); out[ph] = [handled, calls.length];
      }
      return out;
    })()""")
    for ph in ['ceaser salad with beef bacon','chicken breast and rice','steak with salad']:
        if res[ph][1]: f.add('BUG', f'"{ph}" was treated as a suggestion request')
    for ph in ['meat and 2 veg','protein and pasta','meat and veg']:
        if not res[ph][1]: f.add('BUG', f'structured request "{ph}" no longer reaches suggestions')
    if errs: f.add('JS-exception', str(errs[:3]))
    print(res)
    b.close()
print('findings', len(f)); sys.exit(1 if f else 0)
