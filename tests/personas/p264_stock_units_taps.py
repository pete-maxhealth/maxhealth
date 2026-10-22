"""Persona 264: unit traps and double taps (v3.10.1158). Units: what is logged is either converted exactly or left alone, never guessed (kg, l, g, ml and counts
convert; spoons, cups, ounces and slices on a gram or ml food, and weights on a counted food, change nothing; grams<->ml only with a density you gave).
Taps: the same thing pressed twice (the same entry logged twice, deleted twice, ate-out flipped twice, bought-done twice, shopping complete twice) never counts twice. Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    lv = lambda: ev("mhStockLoad().items[mhShopKey('Zz U')].level")
    def setup(base, level=1000, **kw):
        ev("([b,l,o])=>{localStorage.removeItem(MH_STOCK_KEY); mhStockTrack('Zz U',Object.assign({base:b,serving:50},o)); mhStockSetLevel(mhShopKey('Zz U'),l); if(o.gPerMl){const s=mhStockLoad(); s.items[mhShopKey('Zz U')].gPerMl=o.gPerMl; mhStockSave(s);} }", [base, level, kw])
    def log(amt): ev("([a])=>logFoods([{name:'Zz U',amount:a,kcal:1,protein:1,fat:1,carbs:1}],'t')", [amt]); page.wait_for_timeout(100)
    # (base, amount, amount taken off, or 0 = left alone)
    table = [('g', '250g', 250), ('g', '1 kg', 1000), ('g', '0.5 kg', 500), ('g', '2 servings', 100),
             ('ml', '250ml', 250), ('ml', '0.5 l', 500), ('ml', '1 litre', 1000), ('ml', '3 servings', 150),
             ('each', '3', 3), ('each', '2 eggs', 2), ('each', '2 each', 2), ('each', '0.5', 0.5),
             ('g', '2 tbsp', 0), ('g', '1 tsp', 0), ('g', '3 slices', 0), ('g', '200ml', 0), ('g', '1 cup', 0),
             ('ml', '1 tbsp', 0), ('ml', '1 cup', 0), ('ml', '200g', 0), ('each', '100g', 0), ('each', '250ml', 0), ('each', '1 kg', 0)]
    for base, amt, take in table:
        setup(base); log(amt)
        if abs(lv() - (1000 - take)) > 1e-6: f.add('BUG', f'unit trap: {amt} of a {base} food took {1000 - lv()}, should be {take}')
    # a density you gave converts exactly, both ways; none given means untouched
    setup('ml', 1000, gPerMl=1.25); log('250g'); 
    if abs(lv() - 800) > 1e-6: f.add('BUG', f'250 g at 1.25 g/ml is 200 ml: {1000 - lv()}')
    setup('g', 1000, gPerMl=0.5); log('100ml')
    if abs(lv() - 950) > 1e-6: f.add('BUG', f'100 ml at 0.5 g/ml is 50 g: {1000 - lv()}')
    # never below zero
    setup('g', 100); log('500g')
    if lv() != 0: f.add('BUG', 'never below zero')

    # ───── taps ─────
    setup('g', 1000)
    entry = {'id': 'tap1', 'description': 'Zz U', 'items': [{'name': 'Zz U', 'amount': '100g'}], 'kcal': 1, 'protein': 0, 'carbs': 0, 'fat': 0}
    ev("e=>{state.todayLog.push(e); mhStockOnLog(e, todayStr());}", entry)
    if lv() != 900: f.add('BUG', f'tap setup: {lv()}')
    # the same entry logged again by id through the real path does nothing
    ev("e=>{if(!state.todayLog.some(x=>x.id===e.id)){state.todayLog.push(e); mhStockOnLog(e,todayStr());}}", entry)
    # delete twice
    ev("id=>_doDeleteLogEntry(id)", 'tap1'); ev("id=>_doDeleteLogEntry(id)", 'tap1')
    if lv() != 1000: f.add('BUG', f'deleting twice gives back once: {lv()}')
    # ate-out flipped twice returns to the same count
    log('100g'); eid = ev("state.todayLog[state.todayLog.length-1].id"); a = lv()
    ev("id=>mhStockAteOutToggle(id)", eid); ev("id=>mhStockAteOutToggle(id)", eid)
    if lv() != a: f.add('BUG', f'ate-out on then off is a wash: {a} then {lv()}')
    # re-syncing an unchanged entry twice changes nothing
    ev("id=>{const e=state.todayLog.find(x=>x.id===id); mhStockResync(e,todayStr()); mhStockResync(e,todayStr());}", eid)
    if lv() != a: f.add('BUG', f'resync twice with no change: {a} then {lv()}')
    # bought-done twice, shopping complete twice
    setup('g', 200, pack=1000, reorder=300); ev("mhStockSetReorder(mhShopKey('Zz U'),300)"); ev("mhStockSweep()")
    ev("(()=>{const s=mhShopLoad(); s.items.forEach(i=>i.checked=true); mhShopSave(s);})()"); ev("typeof closeSaveLibraryModal==='function' && closeSaveLibraryModal()"); ev("document.getElementById('libraryImpactBanner')?.remove()"); ev("switchTabById('shop')"); ev("document.querySelectorAll('.app-modal-overlay').forEach(x=>x.remove())")
    ev("mhShopComplete()"); page.wait_for_timeout(200); ev("mhShopComplete()"); page.wait_for_timeout(300)   # two taps
    if page.locator('#appModalConfirm').count() != 1: f.add('BUG', f'two taps on Shopping complete must leave ONE question, found {page.locator("#appModalConfirm").count()}')
    ev("document.querySelectorAll('.app-modal-overlay').forEach((x,i)=>{ if(i>0) x.remove(); })")
    if page.locator('#appModalConfirm').count(): page.click('#appModalConfirm'); page.wait_for_timeout(400)
    else: f.add('BUG', 'no completion prompt')
    ev("_shopUi.bgt={}"); ev("mhStockBoughtDone()"); page.wait_for_timeout(300); ev("mhStockBoughtDone()"); page.wait_for_timeout(300)
    if lv() != 200 + 1000: f.add('BUG', f'buying recorded twice: should be 1200, is {lv()}')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
