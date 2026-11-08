"""Persona 429: an amount written as a count with the weight in brackets ("5 slices (175g)", "2 (90g)") is no longer read as 5 g / 2 g, so a normal plate of bacon and sausage is not called "impossible" (Pete 8 Nov, phone screenshot). A genuinely impossible one still is."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    g = lambda a: ev("_amountGrams(%r)" % a)
    for a, want in [('175', 175), ('175g', 175), ('1.5kg', 1500), ('250 ml', 250), ('5 slices (175g)', 175), ('2 (90g)', 90), ('2 eggs', 0), ('', 0), ('1 tbsp', 0)]:
        if g(a) != want: f.add('BUG', f'_amountGrams({a!r}) = {g(a)}, want {want}')
    run = lambda amt, p, fat, c: ev("(() => { const r = sanitiseFatValues([{name:'bacon', amount:%r, kcal:500, protein:%s, fat:%s, carbs:%s}]); return [!!r[0]._impossibleMacroMassWarning, !!r[0]._implausibleAmountWarning]; })()" % (amt, p, fat, c))
    if run('5 slices (175g)', 36, 38.4, 0) != [False, False]: f.add('BUG', 'bacon 5 slices (175g) with 74g of macros is fine: ' + str(run('5 slices (175g)', 36, 38.4, 0)))
    if run('2 (90g)', 14, 22.9, 0) != [False, False]: f.add('BUG', 'sausage 2 (90g) is fine')
    if run('5g', 36, 38.4, 0)[0] is not True: f.add('BUG', 'a real 5 g food with 74 g of macros is still impossible')
    if run('100g', 60, 50, 10)[0] is not True: f.add('BUG', '120 g of macros in 100 g is still impossible')
    if run('2 eggs', 14, 10, 1)[0] is not False: f.add('BUG', 'no weight written: no weight-based alarm')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
