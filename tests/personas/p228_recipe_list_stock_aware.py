"""Persona 228: adding a recipe to the shopping list leaves off what is already in the cupboards (v3.10.1125). Covers: with the cupboards on, a counted food with
some left is not put on the list and the message says how many were left off; a food that is low, out, past its use-by, or not counted is put on; the recipe's
ingredient checklist labels held foods "in your cupboards"; with the cupboards switched off every ingredient goes on as before; a meal-plan refresh follows the
same rule; the old "you always have it" staples still work. Invented data only."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ing = lambda n, g: {'name': n, 'amount': g, 'kcal': 100, 'protein': 5, 'carbs': 5, 'fat': 5}
    ev("r=>saveRecipes(r)", [{'id': 'r1', 'name': 'Test Traybake', 'servings': 2, 'steps': ['Cook.'], 'ingredients': [ing(n, 100) for n in ('Chicken Thigh', 'Peppers', 'Olive Oil', 'Lemon Juice', 'Courgette', 'Rice')]}])
    names = lambda: sorted(ev("mhShopLoad().items.map(i=>i.name)"))
    def reset(): ev("()=>{const s=mhShopLoad(); s.items=[]; mhShopSave(s);}")
    ev("""()=>{ for (const [n,l] of [['Olive Oil',400],['Chicken Thigh',500],['Lemon Juice',5],['Courgette',0]]) { mhStockTrack(n,{base:'g',pack:500,serving:null}); mhStockSetLevel(mhShopKey(n),l); }
      const o=mhStockLoad(); o.items[mhShopKey('Lemon Juice')].reorder=50; o.items[mhShopKey('Chicken Thigh')].reorder=100; mhStockSave(o); }""")
    ev("mhShopOpen()"); ev("mhShopRecipeAdd('test traybake')"); page.wait_for_timeout(200)
    got = names()
    if got != ['Courgette', 'Lemon Juice', 'Peppers', 'Rice']: f.add('BUG', f'held foods are left off; low, out and uncounted go on: {got}')
    msg = ev("document.getElementById('mhShopMsg')?.innerText") or ''
    if '2 already in your cupboards' not in msg: f.add('BUG', f'the message says how many were left off: {msg!r}')
    reset()
    ev("()=>{const o=mhStockLoad(); o.items[mhShopKey('Chicken Thigh')].useBy=mhAddDaysISO(-1); mhStockSave(o);}"); ev("mhShopRecipeAdd('test traybake')")
    if 'Chicken Thigh' not in names(): f.add('BUG', 'a food past its use-by goes on the list')
    reset(); ev("()=>{const o=mhStockLoad(); delete o.items[mhShopKey('Chicken Thigh')].useBy; mhStockSave(o);}")
    ev("mhShopView('recipe','test traybake')"); page.wait_for_timeout(250)
    row = lambda n: ev("(n)=>document.querySelector('[data-ing=\"'+n+'\"]')?.innerText||''", n)
    if 'in your cupboards' not in row('Olive Oil'): f.add('BUG', f'the checklist labels a held food: {row("Olive Oil")!r}')
    if 'in your cupboards' in row('Rice'): f.add('BUG', 'an uncounted food is not labelled')
    reset(); ev("()=>{const o=mhStockLoad(); o.enabled=false; mhStockSave(o);}"); ev("mhShopRecipeAdd('test traybake')")
    if len(names()) != 6: f.add('BUG', f'with the cupboards switched off every ingredient goes on: {names()}')
    reset(); ev("()=>{const o=mhStockLoad(); o.enabled=true; mhStockSave(o);}")
    ev("()=>{ localStorage.setItem('mh_planned_v1', JSON.stringify([{id:'p1',date:todayStr(),h:18,m:0,foods:[{name:'Test Traybake',amount:'1'}],text:'x'}])); }"); ev("mhShopRefresh(true)")
    if 'Olive Oil' in names() or 'Rice' not in names(): f.add('BUG', f'a meal-plan refresh follows the same rule: {names()}')
    reset(); ev("()=>{const s=mhShopLoad(); s.pantry.push(mhShopKey('Rice')); mhShopSave(s);}"); ev("mhShopRefresh(true)")
    if 'Rice' in names(): f.add('BUG', 'an always-have staple is still left off a plan refresh')
    if errs: f.add('BUG', f'page errors: {errs[:3]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
