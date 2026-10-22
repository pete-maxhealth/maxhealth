"""Persona 266: moving a food from one shop to another (v3.10.1158). Toilet roll and milk are now Lidl instead of Aldi: the cupboard row's "Bought at" changes, the
count, reorder, ledger and history stay put, a copy already on the list moves to the new shop (not left under the old one, not duplicated), and from then on running low
puts it on the new shop's list. Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("""(()=>{const s=mhShopLoad(); ['Aldi','Lidl'].forEach(n=>{ if(!s.shops.includes(n)) s.shops.push(n); }); mhShopSave(s);})()""")
    ev("([n])=>{mhStockTrack(n,{base:'ml',pack:1000,shop:'Aldi'}); mhStockSetLevel(mhShopKey(n),900); mhStockSetReorder(mhShopKey(n),500);}", ['Zz Milk'])
    ev("([n])=>logFoods([{name:n,amount:'100ml',kcal:1,protein:1,fat:1,carbs:1}],'t')", ['Zz Milk']); page.wait_for_timeout(150)
    ev("typeof closeSaveLibraryModal==='function' && closeSaveLibraryModal()")
    shop = lambda: ev("mhStockLoad().items[mhShopKey('Zz Milk')].shop")
    rows = lambda: ev("mhShopLoad().items.filter(i=>i.key===mhShopKey('Zz Milk')).map(i=>i.shop)")
    ev("([n])=>logFoods([{name:n,amount:'300ml',kcal:1,protein:1,fat:1,carbs:1}],'t')", ['Zz Milk']); page.wait_for_timeout(150)
    ev("typeof closeSaveLibraryModal==='function' && closeSaveLibraryModal()")
    if rows() != ['Aldi']: f.add('BUG', f'setup: low milk is on the Aldi list: {rows()}')
    snap = ev("JSON.stringify(mhStockLoad().ledger.map(l=>[l.k,l.d]))"); lvl = ev("mhStockLoad().items[mhShopKey('Zz Milk')].level")
    # move it with the real control on the cupboard row
    ev("switchTabById('shop')"); ev("(()=>{const st=mhSlState(); st.q='Zz Milk'; st.f='all'; st.shop=''; mhShopView('stocklist');})()"); page.wait_for_timeout(300)
    page.select_option('[data-sl] [data-f="shop"]', 'Lidl'); page.wait_for_timeout(300)
    if shop() != 'Lidl': f.add('BUG', f'the cupboard row moves it to Lidl: {shop()}')
    if ev("mhStockLoad().items[mhShopKey('Zz Milk')].level") != lvl or ev("JSON.stringify(mhStockLoad().ledger.map(l=>[l.k,l.d]))") != snap: f.add('BUG', 'moving shop keeps the count and history exactly')
    if ev("mhStockLoad().items[mhShopKey('Zz Milk')].reorder") != 500 or ev("mhStockLoad().items[mhShopKey('Zz Milk')].pack") != 1000: f.add('BUG', 'moving shop keeps reorder and pack')
    if rows() != ['Lidl']: f.add('BUG', f'the copy already on the list moves with it, once: {rows()}')
    # restocked, then low again: appears under Lidl only
    ev("(()=>{mhStockSetLevel(mhShopKey('Zz Milk'),1000); mhStockSweep(); const s=mhShopLoad(); s.items=s.items.filter(i=>i.key!==mhShopKey('Zz Milk')); mhShopSave(s);})()")
    ev("([n])=>logFoods([{name:n,amount:'600ml',kcal:1,protein:1,fat:1,carbs:1}],'t')", ['Zz Milk']); page.wait_for_timeout(150)
    ev("typeof closeSaveLibraryModal==='function' && closeSaveLibraryModal()")
    if rows() != ['Lidl']: f.add('BUG', f'running low after the move lists it under Lidl only: {rows()}')
    # the edit form too
    ev("mhStockEditView(mhShopKey('Zz Milk'),'Zz Milk')"); ev("mhStkShopPick('Aldi')"); page.wait_for_timeout(200)
    if shop() != 'Aldi' or rows() != ['Aldi']: f.add('BUG', f'the edit form moves it back and the list follows: {shop()} {rows()}')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
