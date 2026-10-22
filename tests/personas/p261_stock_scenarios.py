"""Persona 261: stock scenarios, end to end (v3.10.1157). Pete asked for: a recipe with everything available; a recipe with substitutes; watching stock go down for an item
already recorded; stock going up on an existing item; and every way stock goes in and out. Each step is checked against arithmetic done here, not against what the app says.
Found and fixed on the way: cooking left millilitre foods alone even with a density given, and ignored substitutes. Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    K = lambda n: ev("n=>mhShopKey(n)", n)
    lv = lambda n: ev("n=>{const i=mhStockLoad().items[mhShopKey(n)]; return i ? i.level : 'missing'}", n)
    track = lambda n, base, level, **kw: ev("([n,b,l,o])=>{mhStockTrack(n,Object.assign({base:b},o)); mhStockSetLevel(mhShopKey(n),l); if(o.reorder!=null) mhStockSetReorder(mhShopKey(n),o.reorder); if(o.gPerMl){const s=mhStockLoad(); s.items[mhShopKey(n)].gPerMl=o.gPerMl; mhStockSave(s);}}", [n, base, level, kw])
    onlist = lambda n: ev("n=>mhShopLoad().items.some(i=>i.key===mhShopKey(n))", n)
    def log(name, amt):
        ev("([n,a])=>logFoods([{name:n,amount:a,kcal:100,protein:1,fat:1,carbs:1}],'t')", [name, amt]); page.wait_for_timeout(150)
    def reset(): ev("localStorage.removeItem(MH_STOCK_KEY); state.todayLog=[]; (()=>{const s=mhShopLoad(); s.items=[]; mhShopSave(s);})()")
    def recipe(rid, name, servings, ings): ev("([r])=>localStorage.setItem('mh_recipes', JSON.stringify([r]))", [{'id': rid, 'name': name, 'servings': servings, 'ingredients': ings}])
    ing = lambda n, a, u=None, **m: dict({'name': n, 'amount': a, 'kcal': 100, 'protein': 5, 'fat': 5, 'carbs': 5}, **({'unit': u} if u else {}), **m)

    # ───── S1: a recipe with everything available ─────
    reset(); recipe('r1', 'Creamy bake', 2, [ing('Zz Mince', 400), ing('Zz Cream', 200), ing('Zz Onion', 100), ing('Zz Egg', 100)])
    track('Zz Mince', 'g', 1000, reorder=650); track('Zz Cream', 'ml', 500, gPerMl=1); track('Zz Onion', 'g', 300); track('Zz Egg', 'each', 6)
    note = ev("mhStockRecipeNote(loadRecipes()[0])")
    if 'short of' in note: f.add('BUG', f'S1.1: everything is in, the card must not say short: {note}')
    ev("()=>mhStockCooked('r1',2)")
    got = {n: lv(n) for n in ['Zz Mince', 'Zz Cream', 'Zz Onion', 'Zz Egg']}
    if got != {'Zz Mince': 600, 'Zz Cream': 300, 'Zz Onion': 200, 'Zz Egg': 6}: f.add('BUG', f'S1.2: a batch takes grams, and millilitres via the density you gave; eggs (grams cannot become a count) are left alone: {got}')
    if not onlist('Zz Mince'): f.add('BUG', 'S1.3: mince fell under its reorder level (600 <= 650) so it is on the list')
    if ev("mhShopLoad().items.filter(i=>i.key===mhShopKey('Zz Mince')).length") != 1: f.add('BUG', 'S1.4: once, not twice')
    ev("()=>logRecipe('r1',1)"); page.wait_for_timeout(200)
    if lv('Zz Mince') != 600 or lv('Zz Cream') != 300: f.add('BUG', 'S1.5: eating from the cooked batch takes nothing more')
    ev("()=>mhStockCooked('r1',1)")
    if lv('Zz Mince') != 400 or lv('Zz Cream') != 200: f.add('BUG', f'S1.6: half a batch takes half: {lv("Zz Mince")} {lv("Zz Cream")}')
    # without a density the millilitre food is not guessed
    track('Zz Cream', 'ml', 500); ev("(()=>{const o=mhStockLoad(); delete o.items[mhShopKey('Zz Cream')].gPerMl; mhStockSave(o);})()"); ev("()=>mhStockCooked('r1',2)")
    if lv('Zz Cream') != 500: f.add('BUG', 'S1.7: no density given, so millilitres are never guessed')

    # ───── S2: a recipe with substitutes ─────
    reset()
    ev("""(()=>{const l=loadLibrary(); l.push({name:'Zz Whole Milk',portion:'100 ml',kcal:50,protein:3,fat:3,carbs:5},{name:'Zz Oat Milk',portion:'100 ml',kcal:45,protein:1,fat:1.5,carbs:5}); localStorage.setItem(LIBRARY_KEY, JSON.stringify(l));})()""")
    recipe('r2', 'Milk pudding', 2, [ing('Zz Mince', 200), dict(ing('Zz Whole Milk', 300, 'ml'), kcal=150, protein=9, fat=9, carbs=15)])
    track('Zz Mince', 'g', 1000); track('Zz Whole Milk', 'ml', 0); track('Zz Oat Milk', 'ml', 1000)
    sw = ev("mhStockCookSwaps(loadRecipes()[0], 2)")
    if len(sw) != 1 or sw[0]['from'] != 'Zz Whole Milk' or sw[0]['to'] != 'Zz Oat Milk' or sw[0]['take'] != 300: f.add('BUG', f'S2.1: out of whole milk, oat milk is the swap, 300 ml: {sw}')
    # asked through the real prompts: yes
    ev("()=>mhStockCookedAsk('r2')"); page.wait_for_timeout(200); page.fill('#appPromptInput', '2'); page.click('#appModalConfirm'); page.wait_for_timeout(300)
    if not page.locator('#appModalConfirm').count(): f.add('BUG', 'S2.2: it asks before using a swap')
    else: page.click('#appModalConfirm'); page.wait_for_timeout(300)
    if (lv('Zz Oat Milk'), lv('Zz Whole Milk'), lv('Zz Mince')) != (700, 0, 800): f.add('BUG', f'S2.3: yes: oat milk 1000-300, whole milk stays 0, mince 1000-200: {(lv("Zz Oat Milk"), lv("Zz Whole Milk"), lv("Zz Mince"))}')
    # no: left alone
    ev("()=>{const o=mhStockLoad(); delete o.cooked; mhStockSave(o);}"); track('Zz Mince', 'g', 1000); track('Zz Oat Milk', 'ml', 1000)
    ev("()=>mhStockCookedAsk('r2')"); page.wait_for_timeout(200); page.fill('#appPromptInput', '2'); page.click('#appModalConfirm'); page.wait_for_timeout(300); page.click('#appModalCancel'); page.wait_for_timeout(300)
    if lv('Zz Oat Milk') != 1000 or lv('Zz Mince') != 800: f.add('BUG', f'S2.4: no: the swap is left alone, the rest still comes off: {(lv("Zz Oat Milk"), lv("Zz Mince"))}')
    # nothing to swap when the original is in
    track('Zz Whole Milk', 'ml', 1000)
    if ev("mhStockCookSwaps(loadRecipes()[0], 2)"): f.add('BUG', 'S2.5: whole milk is in, so no swap is offered')
    # a swap that is itself out is not offered
    track('Zz Whole Milk', 'ml', 0); track('Zz Oat Milk', 'ml', 100)
    if ev("mhStockCookSwaps(loadRecipes()[0], 2)"): f.add('BUG', 'S2.6: the swap has too little, so it is not offered')

    # ───── S3: watching an item already recorded go down ─────
    reset(); track('Zz Whey', 'g', 750, reorder=100, pack=750, serving=25)
    steps = [('25g', 725), ('2 servings', 675), ('0.05 kg', 625), ('500g', 125)]
    for a, want in steps:
        log('Zz Whey', a)
        if lv('Zz Whey') != want: f.add('BUG', f'S3: after logging {a}: {lv("Zz Whey")}, wanted {want}')
    if onlist('Zz Whey'): f.add('BUG', 'S3.1: 125 g is still above the reorder level of 100: not on the list yet')
    log('Zz Whey', '25g')
    if lv('Zz Whey') != 100 or not onlist('Zz Whey'): f.add('BUG', f'S3.2: reaching the reorder level (100) puts it on the list: {lv("Zz Whey")} {onlist("Zz Whey")}')
    log('Zz Whey', '25g'); log('Zz Whey', '25g')
    if ev("mhShopLoad().items.filter(i=>i.key===mhShopKey('Zz Whey')).length") != 1: f.add('BUG', 'S3.3: still on the list once')
    log('Zz Whey', '500g')
    if lv('Zz Whey') != 0: f.add('BUG', f'S3.4: it never goes below zero: {lv("Zz Whey")}')
    led = ev("mhStockLoad().ledger.filter(l=>l.k===mhShopKey('Zz Whey')).reduce((a,l)=>a+l.d,0)")
    if led != -750: f.add('BUG', f'S3.5: the ledger adds up to what actually came off (750 g): {led}')

    # ───── S4: stock going up on an existing item ─────
    reset(); track('Zz Rice', 'g', 200, reorder=300, pack=1000)
    ev("mhStockSweep()")
    if not onlist('Zz Rice'): f.add('BUG', 'S4.0: 200 <= 300 so it starts on the list')
    # bought: a full pack
    ev("(()=>{const s=mhShopLoad(); s.items.forEach(i=>i.checked=true); mhShopSave(s);})()"); ev("mhShopComplete()"); page.click('#appModalConfirm'); page.wait_for_timeout(400)
    ev("_shopUi.bgt={}"); ev("mhStockBoughtDone()"); page.wait_for_timeout(300)
    if lv('Zz Rice') != 1200: f.add('BUG', f'S4.1: buying a pack adds to what is there, 200 + 1000: {lv("Zz Rice")}')
    if onlist('Zz Rice'): f.add('BUG', 'S4.2: above the reorder level, off the list')
    # a typed amount on the cupboard row sets it
    ev("switchTabById('shop')"); ev("(()=>{const st=mhSlState(); st.q='Zz Rice'; st.f='all'; mhShopView('stocklist');})()"); page.wait_for_timeout(300)
    page.fill('[data-sl] [data-f="amt"]', '900 g'); page.press('[data-sl] [data-f="amt"]', 'Tab'); page.wait_for_timeout(300)
    if lv('Zz Rice') != 900: f.add('BUG', f'S4.3: typing what you have on the cupboard row sets it: {lv("Zz Rice")}')
    # the edit form autosaves
    ev("mhStockEditView(mhShopKey('Zz Rice'),'Zz Rice')"); ev("mhStkSet('level','850'); mhStkCommit('level')")
    if lv('Zz Rice') != 850: f.add('BUG', f'S4.4: the edit form saves as you change it: {lv("Zz Rice")}')
    ev("mhStkUndo && mhStkUndo()"); 
    # a receipt adds on top
    ev("_shopUi.stk=null"); ev("mhShopView('list')")
    before = lv('Zz Rice')
    ev("mhOrdDraftClear(); mhOrdOpen('receipt')"); page.fill('#mhOrdText', "ASDA\nZZ RICE 500G 1.20\n17 Oct 2026\n"); page.click('#mhOrdRead'); page.wait_for_timeout(400)
    ev("_shopUi.ord.rows.forEach(r=>{ if(r.name.toLowerCase().includes('rice')) { r.track='Zz Rice'; r.mode='add'; } })")
    page.click('#mhOrdGo'); page.wait_for_timeout(500)
    if lv('Zz Rice') != before + 500: f.add('BUG', f'S4.5: a receipt line adds its pack on top, {before} + 500: {lv("Zz Rice")}')
    # restocked item leaves the list
    track('Zz Rice', 'g', 200, reorder=300); ev("mhStockSweep()")
    if not onlist('Zz Rice'): f.add('BUG', 'S4.6: low again, back on the list')

    # ───── S5: every way in and out, one item, checked against a running total ─────
    reset(); track('Zz Matrix', 'g', 1000, pack=500); total = 1000
    ev("mhStockSetLevel(mhShopKey('Zz Matrix'),1000)")
    ev("""(()=>{const l=loadLibrary(); l.push({name:'Zz Matrix',portion:'50 g',kcal:100,protein:1,fat:1,carbs:1}); localStorage.setItem(LIBRARY_KEY, JSON.stringify(l));})()""")
    def check(label, want):
        if lv('Zz Matrix') != want: f.add('BUG', f'S5 {label}: running total {want}, app says {lv("Zz Matrix")}')
    check('typed count', total)
    log('Zz Matrix', '100g'); total -= 100; check('typed log', total)
    i = ev("loadLibrary().findIndex(x=>x.name==='Zz Matrix')")
    ev("i=>quickLogFromLibrary(i)", i); page.wait_for_timeout(300); page.fill('#libPortionInput', '50'); ev("i=>logLibraryWithPortion(i)", i); page.wait_for_timeout(400); total -= 50; check('library log', total)
    qid = ev("state.todayLog[state.todayLog.length-1].id")
    ev("_selectedFoodItem={name:'Zz Matrix',brand:'',kcal:100,prot:1,carb:1,fat:1}; document.getElementById('foodAmountGrams').value=30; logFoodFromDatabase()"); page.wait_for_timeout(400); total -= 30; check('database / barcode log', total)
    recipe('r5', 'Matrix dish', 2, [ing('Zz Matrix', 200)])
    ev("()=>logRecipe('r5',1)"); page.wait_for_timeout(300); total -= 100; check('recipe log (1 of 2 servings, none cooked)', total)
    ev("()=>mhStockCooked('r5',2)"); total -= 200; check('cooked batch', total)
    ev("k=>mhStockWaste(k,20)", K('Zz Matrix')); total -= 20; check('used or binned', total)
    ev("(k)=>{mhStockAdjust(k,500,'bought','shop')}", K('Zz Matrix')); total += 500; check('bought (+500)', total)
    ev("id=>_doDeleteLogEntry(id)", qid); total += 50; check('deleting the library entry gives its 50 back', total)
    tid = ev("state.todayLog.find(e=>e.description==='t').id")
    ev("id=>{const e=state.todayLog.find(x=>x.id===id); e.items[0].amount='60g'; mhStockResync(e,todayStr());}", tid); total += 40; check('editing 100 g down to 60 g gives 40 back', total)
    ev("id=>mhStockAteOutToggle(id)", tid); total += 60; check('marking it ate out gives it all back', total)
    log('Zz Matrix', '10g'); ev("id=>mhStockAteOutToggle(id)", ev("state.todayLog[state.todayLog.length-1].id")); check('ate out leaves stock alone', total)
    # a stock-take covers what was logged before it: deleting an older entry gives nothing back
    log('Zz Matrix', '100g'); old = ev("state.todayLog[state.todayLog.length-1].id"); ev("mhStockSetLevel(mhShopKey('Zz Matrix'),400)"); ev("id=>_doDeleteLogEntry(id)", old)
    if lv('Zz Matrix') != 400: f.add('BUG', f'S5 stock-take: a count made after the entry already covers it, deleting it changes nothing: {lv("Zz Matrix")}')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
