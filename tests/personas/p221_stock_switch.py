"""Persona 221: cupboards & stock can be switched off (v3.10.1123). Off puts the app back the old way: logging never touches stock, the list
is never added to, meal ideas are not filtered, no reservations, no ate-out button, the card offers to turn it back on; counts are kept;
it survives a reload; tracking something (a deliberate act) turns it on. On again works as before. Invented data only."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("saveLibrary([{id:'l1',name:'Double Cream',kcal:450,protein:2,carbs:2.5,fat:48,portion:'100ml',useCount:9},{id:'l2',name:'Butter',kcal:700,protein:1,carbs:0.5,fat:80,portion:'10g',useCount:5}])")
    ev("""()=>{ mhStockTrack('Double Cream',{base:'ml',pack:300,shop:'Asda'}); mhStockSetLevel(mhShopKey('Double Cream'),500); mhStockSetReorder(mhShopKey('Double Cream'),100);
      mhStockTrack('Butter',{base:'g',pack:250,shop:'Asda'}); mhStockSetLevel(mhShopKey('Butter'),0); }""")
    ev("mhShopOpen()")
    lvl = lambda: ev("mhStockLoad().items[mhShopKey('Double Cream')].level")
    food = lambda n, a: {'name': n, 'amount': a, 'kcal': 100, 'protein': 1, 'fat': 5, 'carbs': 1}
    if not ev("mhStockOn()"): f.add('BUG', '1: on by default when something is tracked')
    if 'Check the cupboards' not in ev("mhStockCardHtml(mhShopLoad())") or 'Turn off' not in ev("mhStockCardHtml(mhShopLoad())"): f.add('BUG', '1: the card has its buttons and a Turn off')
    ev("([x,t])=>logFoods(x,t)", [[food('Double Cream', '100 ml')], 'cream']); page.wait_for_timeout(300)
    if lvl() != 400: f.add('BUG', f'1: on: logging takes stock off: {lvl()}')
    # off through the UI
    page.click('[onclick="mhStockOffAsk()"]'); page.wait_for_timeout(300)
    if not ev("!!document.getElementById('appModalConfirm')"): f.add('BUG', '2: turning off asks first')
    else: page.click('#appModalConfirm'); page.wait_for_timeout(400)
    if ev("mhStockOn()"): f.add('BUG', '2: confirmed: it is off')
    card = ev("mhStockCardHtml(mhShopLoad())")
    if 'Turn cupboards' not in card or 'Check the cupboards' in card or 'Start stock from an order' in card or 'stockctlCard' not in card or 'stockctlBody' not in card: f.add('BUG', '2: the off card offers only to turn it on, keeps its id and controls')
    if 'mh-ctl' not in card: f.add('BUG', '2: the off card keeps show/hide and reorder controls')
    if ev("Object.keys(mhStockLoad().items).length") != 2 or lvl() != 400: f.add('BUG', '2: counts are kept while off')
    # behaviour off
    ev("([x,t])=>logFoods(x,t)", [[food('Double Cream', '350 ml')], 'cream']); page.wait_for_timeout(300)
    if lvl() != 400: f.add('BUG', f'3: off: logging must not touch stock: {lvl()}')
    ev("()=>{const o=mhStockLoad(); o.items[mhShopKey('Double Cream')].level=50; mhStockSave(o)}")
    if ev("mhStockSweep()") != 0 or any(i['name'] == 'Double Cream' for i in ev("mhShopLoad().items")): f.add('BUG', '3: off: nothing is added to the list')
    ev("()=>{const o=mhStockLoad(); o.items[mhShopKey('Double Cream')].level=400; mhStockSave(o)}")
    if ev("mhSuggestMode()") != 'off': f.add('BUG', f'3: off: meal ideas are not filtered: {ev("mhSuggestMode()")}')
    fl = ev("()=>{const r=mhSuggestFilter(loadLibrary(),[]); return {n:r.lib.length, a:r.active}}")
    if fl['n'] != 2 or fl['a']: f.add('BUG', f'3: off: the whole library is offered: {fl}')
    if ev("JSON.stringify(mhPlanReserved())") != '{}': f.add('BUG', '3: off: no reservations')
    if ev("mhStockPreferLine()") != '': f.add('BUG', '3: off: no stock steer in prompts')
    if page.locator('[data-ateout]').count(): f.add('BUG', '3: off: no ate-out button')
    page.reload(); page.wait_for_timeout(1200)
    if ev("mhStockOn()"): f.add('BUG', '4: off survives a reload')
    ev("document.getElementById('onboardingOverlay')?.remove(); mhShopOpen()")
    page.click('[onclick="mhStockSetOn(true)"]'); page.wait_for_timeout(400)
    if not ev("mhStockOn()") or 'Check the cupboards' not in ev("mhStockCardHtml(mhShopLoad())"): f.add('BUG', '4: turned back on from the card, counts and buttons are back')
    ev("([x,t])=>logFoods(x,t)", [[food('Double Cream', '100 ml')], 'cream']); page.wait_for_timeout(300)
    if lvl() != 300: f.add('BUG', f'4: on again: logging takes stock off: {lvl()}')
    if ev("mhSuggestMode()") != 'hide': f.add('BUG', '4: on again: filtering is back')
    # tracking something turns it on
    ev("mhStockSetOn(false)"); ev("mhStockTrack('Honey',{base:'g',pack:340})")
    if not ev("mhStockOn()"): f.add('BUG', '5: tracking a food is a deliberate act and turns it on')
    if errs: f.add('JS-exception', errs[0])
print('\n'.join(f'{a}: {b}' for a, b in f) or 'PASS')
sys.exit(1 if f else 0)
