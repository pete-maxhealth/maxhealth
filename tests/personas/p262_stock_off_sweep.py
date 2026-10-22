"""Persona 262: stock switched OFF, every way in and out (v3.10.1158). With counting off nothing may change a count or put anything on the list by number
(typed log, library log, database log, recipe log, cooked batch, used-or-binned, deleting, editing, ate-out, receipt, shopping complete), while the shopping list,
regulars and saved lists keep working. Switching back on picks up exactly where the counts were left. Invented data."""
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
    snap = lambda: ev("JSON.stringify([mhStockLoad().items, mhStockLoad().ledger.length])")
    listnames = lambda: ev("mhShopLoad().items.map(i=>i.key).sort().join('|')")
    def log(name, amt):
        ev("([n,a])=>logFoods([{name:n,amount:a,kcal:100,protein:1,fat:1,carbs:1}],'t')", [name, amt]); page.wait_for_timeout(150)
    ev("""(()=>{const l=loadLibrary(); l.push({name:'Zz Off',portion:'50 g',kcal:100,protein:1,fat:1,carbs:1}); localStorage.setItem(LIBRARY_KEY, JSON.stringify(l));})()""")
    ev("([n])=>{mhStockTrack(n,{base:'g',pack:500}); mhStockSetLevel(mhShopKey(n),1000); mhStockSetReorder(mhShopKey(n),900);}", ['Zz Off'])
    ev("localStorage.setItem('mh_recipes', JSON.stringify([{id:'ro',name:'Off dish',servings:2,ingredients:[{name:'Zz Off',amount:200,kcal:100,protein:1,fat:1,carbs:1}]}]))")
    log('Zz Off', '100g'); eid = ev("state.todayLog[state.todayLog.length-1].id")
    ev("mhStockSweep()")
    base_list = listnames()
    if ev("mhStockLoad().items[mhShopKey('Zz Off')].level") != 900: f.add('BUG', 'setup: on, logging 100 g takes it to 900')
    ev("mhStockSetOn(false)"); page.wait_for_timeout(200)
    if ev("mhStockOn()"): f.add('BUG', 'setup: now off')
    s0 = snap(); l0 = listnames()
    def same(label):
        if snap() != s0: f.add('BUG', f'off, {label}: counts or ledger changed')
        if listnames() != l0: f.add('BUG', f'off, {label}: the list was added to by number')
    log('Zz Off', '300g'); same('typed log')
    i = ev("loadLibrary().findIndex(x=>x.name==='Zz Off')")
    ev("i=>quickLogFromLibrary(i)", i); page.wait_for_timeout(300); page.fill('#libPortionInput', '50'); ev("i=>logLibraryWithPortion(i)", i); page.wait_for_timeout(400); same('library log')
    ev("_selectedFoodItem={name:'Zz Off',brand:'',kcal:100,prot:1,carb:1,fat:1}; document.getElementById('foodAmountGrams').value=30; logFoodFromDatabase()"); page.wait_for_timeout(400); ev("typeof closeSaveLibraryModal==='function' && closeSaveLibraryModal()"); same('database log')
    ev("()=>logRecipe('ro',1)"); page.wait_for_timeout(300); same('recipe log')
    ev("()=>mhStockCooked('ro',2)"); same('cooked batch')
    ev("k=>mhStockWaste(k,50)", K('Zz Off')); same('used or binned')
    last = ev("state.todayLog[state.todayLog.length-1].id")
    ev("id=>{const e=state.todayLog.find(x=>x.id===id); e.items[0].amount='60g'; mhStockResync(e,todayStr());}", last); same('editing an entry')
    ev("id=>mhStockAteOutToggle(id)", last); same('ate out')
    ev("id=>_doDeleteLogEntry(id)", last); same('deleting an entry')
    ev("id=>_doDeleteLogEntry(id)", eid); same('deleting the first entry (logged while on)')
    # receipt
    ev("typeof closeSaveLibraryModal==='function' && closeSaveLibraryModal()"); ev("document.getElementById('libraryImpactBanner')?.remove()")
    ev("switchTabById('shop')"); ev("mhShopView('list')")
    ev("mhOrdDraftClear(); mhOrdOpen('receipt')"); page.fill('#mhOrdText', "ASDA\nZZ OFF 500G 1.20\n17 Oct 2026\n"); page.click('#mhOrdRead'); page.wait_for_timeout(400)
    ev("_shopUi.ord.rows.forEach(r=>{ if(r.name.toLowerCase().includes('zz off')) { r.track='Zz Off'; r.mode='add'; } })")
    if page.locator('#mhOrdGo').count(): page.click('#mhOrdGo'); page.wait_for_timeout(500)
    if ev("mhStockLoad().items[mhShopKey('Zz Off')].level") != 900: f.add('BUG', 'off, receipt: stock is not touched (stays 900)')
    # sweep never adds by number
    s0 = snap(); l0 = listnames()   # a receipt ticks what was bought off the list, which is right; from here the sweep must change nothing
    ev("mhStockSweep()"); same('sweep')
    # the list itself still works: add, tick, complete, regulars
    ev("(()=>{const s=mhShopLoad(); mhShopSetAdd && 0;})()")
    ev("n=>{const s=mhShopLoad(); s.items.push({id:'x1',key:mhShopKey(n),name:n,checked:false}); mhShopSave(s);}", 'Zz Plain')
    ev("(()=>{const s=mhShopLoad(); s.usuals=(s.usuals||[]).concat([{key:mhShopKey('Zz Regular'),name:'Zz Regular'}]); mhShopSave(s);})()")
    if 'zz plain' not in listnames().lower(): f.add('BUG', 'off: the list still takes items')
    ev("(()=>{const s=mhShopLoad(); s.items.forEach(i=>i.checked=true); mhShopSave(s);})()"); ev("mhShopComplete()")
    if page.locator('#appModalConfirm').count(): page.click('#appModalConfirm'); page.wait_for_timeout(400)
    if 'zz plain' in listnames().lower(): f.add('BUG', 'off: shopping complete empties the basket')
    if ev("(mhShopLoad().usuals||[]).some(u=>u.key===mhShopKey('Zz Regular'))") is not True: f.add('BUG', 'off: regulars survive shopping complete')
    if ev("mhStockLoad().items[mhShopKey('Zz Off')].level") != 900: f.add('BUG', 'off: completing a shop does not touch counts')
    # back on: picks up where it was
    ev("mhStockSetOn(true)")
    if ev("mhStockLoad().items[mhShopKey('Zz Off')].level") != 900: f.add('BUG', 'on again: the count is exactly where it was left')
    log('Zz Off', '100g')
    if ev("mhStockLoad().items[mhShopKey('Zz Off')].level") != 800: f.add('BUG', 'on again: counting resumes')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
