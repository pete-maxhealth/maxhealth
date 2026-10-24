"""Persona 304: one tap puts every Library food with no stock entry into My cupboards as filtered with 0 stock (nothing on the shopping list); foods with no g/ml portion are left out; Undo removes exactly those (v3.10.1206). Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()"); ev("localStorage.setItem('mh_shop_pane','both')")
    ev("window.appConfirm=(m,fn)=>{fn&&fn()}")
    ev("saveLibrary([{id:'a',name:'Zzqx Chicken',kcal:200,protein:30,carbs:0,fat:8,portion:'100g'},{id:'b',name:'Zzqx Milk',kcal:50,protein:3,carbs:5,fat:2,portion:'100ml'},{id:'c',name:'Zzqx Bread',kcal:80,protein:3,carbs:14,fat:1,portion:'1 slice'},{id:'d',name:'Zzqx Rice',kcal:130,protein:3,carbs:28,fat:0,portion:'100g'}])")
    ev("mhStockTrack('Zzqx Rice',{base:'g',shop:'Asda'}); mhStockSetLevel(mhShopKey('Zzqx Rice'),500)")
    before = ev("Object.keys(mhStockLoad().items).length"); lb = ev("mhShopLoad().items.length")
    plan = ev("(()=>{const p=mhLibToFilteredPlan(); return [p.ok.map(x=>x.name).sort(), p.noUnit.sort()]})()")
    if plan != [['Zzqx Chicken', 'Zzqx Milk'], ['Zzqx Bread']]: f.add('BUG', f'plan: what is added and what is left out: {plan}')
    ev("mhLibToFiltered()"); page.wait_for_timeout(400)
    for n in ['Zzqx Chicken', 'Zzqx Milk']:
        k = ev("mhShopKey(%r)" % n); it = ev("mhStockLoad().items[%r]" % k)
        if not it or not it.get('held') or it.get('level') != 0: f.add('BUG', f'{n}: added filtered with 0 stock: {it}')
        if it and it.get('reorder') is not None: f.add('BUG', f'{n}: reorder level left empty: {it}')
        if it and it.get('shop'): f.add('BUG', f'{n}: no shop chosen for you: {it}')
    if ev("!!mhStockLoad().items[mhShopKey('Zzqx Bread')]"): f.add('BUG', 'a food with no g/ml portion is left out, never guessed')
    if ev("mhStockLoad().items[mhShopKey('Zzqx Rice')].level") != 500 or ev("!!mhStockLoad().items[mhShopKey('Zzqx Rice')].held"): f.add('BUG', 'a food already in stock is untouched')
    ev("mhStockSweep()")
    if ev("mhShopLoad().items.length") != lb: f.add('BUG', 'nothing reaches the shopping list')
    if ev("mhShopHeldFoods().length") != 2: f.add('BUG', 'both show in Filtered')
    ev("mhLibToFilteredUndo()"); page.wait_for_timeout(300)
    if ev("Object.keys(mhStockLoad().items).length") != before: f.add('BUG', 'Undo takes back exactly what was added')
    if ev("mhStockLoad().items[mhShopKey('Zzqx Rice')].level") != 500: f.add('BUG', 'Undo leaves the food you already had')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
