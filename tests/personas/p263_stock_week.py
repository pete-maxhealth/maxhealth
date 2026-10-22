"""Persona 263: a whole week in the kitchen (v3.10.1158). Seven days of logging, cooking, running low, shopping and restocking, with the expected count of every
item worked out here from first principles and compared after every step, so any drift (a double count, a missed reversal, a stale list entry) shows on the day it
happens. Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    lv = lambda n: ev("n=>{const i=mhStockLoad().items[mhShopKey(n)]; return i ? i.level : 'missing'}", n)
    onlist = lambda n: ev("n=>mhShopLoad().items.filter(i=>i.key===mhShopKey(n)).length", n)
    def log(name, amt):
        ev("([n,a])=>logFoods([{name:n,amount:a,kcal:100,protein:1,fat:1,carbs:1}],'t')", [name, amt]); page.wait_for_timeout(120)
    # name: (base, start, reorder, pack)
    items = {'Zz Rice': ('g', 1000, 300, 1000), 'Zz Milk': ('ml', 2000, 500, 1000), 'Zz Chicken': ('g', 800, 300, 500), 'Zz Eggs': ('each', 12, 4, 6)}
    exp = {n: v[1] for n, v in items.items()}
    for n, (b, lvl, ro, pk) in items.items():
        ev("([n,b,l,r,p])=>{mhStockTrack(n,{base:b,pack:p}); mhStockSetLevel(mhShopKey(n),l); mhStockSetReorder(mhShopKey(n),r);}", [n, b, lvl, ro, pk])
    ev("localStorage.setItem('mh_recipes', JSON.stringify([{id:'w1',name:'Chicken rice',servings:4,ingredients:[{name:'Zz Chicken',amount:400,kcal:100,protein:1,fat:1,carbs:1},{name:'Zz Rice',amount:240,kcal:100,protein:1,fat:1,carbs:1}]}]))")
    def check(day, step):
        for n in items:
            if lv(n) != exp[n]: f.add('BUG', f'day {day} {step}: {n} is {lv(n)}, working says {exp[n]}')
        for n, (b, lvl, ro, pk) in items.items():
            want = 1 if exp[n] <= ro else 0
            if onlist(n) != want and not (want == 0 and day_bought.get(n)): f.add('BUG', f'day {day} {step}: {n} at {exp[n]} (reorder {ro}) should be on the list {want} time(s), is {onlist(n)}')
    day_bought = {}
    # Day 1: ordinary logging
    log('Zz Rice', '150g'); exp['Zz Rice'] -= 150; log('Zz Milk', '250ml'); exp['Zz Milk'] -= 250; log('Zz Eggs', '2'); exp['Zz Eggs'] -= 2; check(1, 'logging')
    # Day 2: cook a batch of 4 servings (chicken 400, rice 240), then eat 2 servings from it (no further stock)
    ev("()=>mhStockCooked('w1',4)"); exp['Zz Chicken'] -= 400; exp['Zz Rice'] -= 240; check(2, 'cooked')
    ev("()=>logRecipe('w1',2)"); page.wait_for_timeout(300); check(2, 'ate 2 servings of the batch (nothing more comes off)')
    # Day 3: more logging; milk and eggs
    log('Zz Milk', '400ml'); exp['Zz Milk'] -= 400; log('Zz Eggs', '3'); exp['Zz Eggs'] -= 3; log('Zz Rice', '100g'); exp['Zz Rice'] -= 100; check(3, 'logging')
    # Day 3 evening: delete a mistaken entry, edit another
    mid = ev("state.todayLog[state.todayLog.length-1].id")
    ev("id=>_doDeleteLogEntry(id)", mid); exp['Zz Rice'] += 100; check(3, 'deleted the 100 g rice entry')
    # Day 4: eggs and milk run low (eggs 12-2-3=7; two more days)
    log('Zz Eggs', '2'); exp['Zz Eggs'] -= 2; log('Zz Milk', '700ml'); exp['Zz Milk'] -= 700; check(4, 'logging')
    log('Zz Eggs', '2'); exp['Zz Eggs'] -= 2; check(4, 'eggs at the reorder level')
    # Day 5: shopping: tick everything on the list, complete the shop, record buying a pack each
    ev("(()=>{const s=mhShopLoad(); s.items.forEach(i=>i.checked=true); mhShopSave(s);})()")
    listed = ev("mhShopLoad().items.map(i=>i.name).sort()")
    ev("mhShopComplete()"); page.click('#appModalConfirm'); page.wait_for_timeout(400)
    ev("_shopUi.bgt={}"); ev("mhStockBoughtDone()"); page.wait_for_timeout(300)
    for n in listed:
        if n in items: exp[n] += items[n][3]; day_bought[n] = 1
    if not listed: f.add('BUG', 'day 5: something should have been on the list to buy')
    day_bought = {}; check(5, 'bought a pack of each low item')
    # Day 6: a second run of logging; chicken cooked again
    ev("()=>mhStockCooked('w1',2)"); exp['Zz Chicken'] -= 200; exp['Zz Rice'] -= 120; check(6, 'half batch cooked')
    log('Zz Milk', '300ml'); exp['Zz Milk'] -= 300; check(6, 'milk')
    # Day 7: a stock-take of rice by hand, then more logging; waste a bit of chicken
    ev("n=>mhStockSetLevel(mhShopKey(n),420)", 'Zz Rice'); exp['Zz Rice'] = 420; check(7, 'counted rice by hand')
    log('Zz Rice', '150g'); exp['Zz Rice'] -= 150; check(7, 'rice after the count')
    ev("k=>mhStockWaste(k,50)", ev("mhShopKey('Zz Chicken')")); exp['Zz Chicken'] -= 50; check(7, 'binned 50 g chicken')
    # the ledger agrees with the count change since the last stock-take for rice
    led = ev("mhStockLoad().ledger.filter(l=>l.k===mhShopKey('Zz Rice')).reduce((a,l)=>a+l.d,0)")
    if led != -150: f.add('BUG', f'day 7: rice ledger since the count should be -150, is {led}')
    # nothing is on the list twice
    names = ev("mhShopLoad().items.map(i=>i.key)")
    if len(names) != len(set(names)): f.add('BUG', f'a food is on the list twice: {names}')
    # foods tracked or imported with NO amount yet count as available (the gentle way to bring in a receipt); only the strict setting treats them as missing
    ev("localStorage.setItem('mh_recipes', JSON.stringify([{id:'w2',name:'Uncounted dish',servings:2,ingredients:[{name:'Zz Fresh',amount:100,kcal:1,protein:1,fat:1,carbs:1},{name:'Zz Rice',amount:50,kcal:1,protein:1,fat:1,carbs:1}]}]))")
    ev("mhStockTrack('Zz Fresh',{base:'g'})")
    mk = lambda m: ev("m=>mhRecipeMakeable(loadRecipes()[0], mhStockLoad(), m).ok", m)
    if not mk('hide'): f.add('BUG', 'a tracked food with no amount yet counts as available in the normal mode')
    if mk('strict'): f.add('BUG', 'strict mode does not count a food with no amount')
    ev("mhStockSetLevel(mhShopKey('Zz Fresh'),0)")
    if mk('hide'): f.add('BUG', 'a food counted at zero is out, in every mode')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
