"""Persona 251: pick several foods and set shop / where kept in one go (v3.10.1147), and none of the new shopping/stock features switch stock back on or show up when it is off (v3.10.1147).
Pete: search "Heylo", select all or some, add to the shop, set fridge/freezer/cupboard; and "will this affect anything with it switched off?". Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("""saveLibrary([{id:'h1',name:'Zzqx Heylo Soup',kcal:40,protein:2,carbs:5,fat:1,portion:'100g',useCount:2},
      {id:'h2',name:'Zzqx Heylo Yoghurt',kcal:60,protein:4,carbs:6,fat:2,portion:'100ml',useCount:2},
      {id:'h3',name:'Zzqx Heylo Mystery',kcal:90,protein:4,carbs:9,fat:3,portion:'1 pot',useCount:2},
      {id:'o1',name:'Zzqx Other Rice',kcal:130,protein:3,carbs:28,fat:0.3,portion:'100g',useCount:2}])""")
    ev("(()=>{const s=mhShopLoad(); if(!s.shops.includes('Heylo')) s.shops.push('Heylo'); mhShopSave(s);})()")
    ev("mhStockTrack('Zzqx Seed',{base:'g'})")   # stock starts off until something is tracked
    ev("mhShopOpen()"); page.wait_for_timeout(300)
    # 1) the Add box has a way in, carrying what was typed
    ev("_shopUi.addOpen=true; mhShopAddKind('food')"); page.wait_for_timeout(200)
    page.fill('#mhShopOwn', 'Zzqx Heylo')
    if not page.locator('button:has-text("Search my foods and pick several")').count(): f.add('BUG', '1: the Add box offers to search my foods and pick several')
    else:
        page.click('button:has-text("Search my foods and pick several")'); page.wait_for_timeout(300)
        if ev("mhSlState().q") != 'Zzqx Heylo': f.add('BUG', '2: what you typed becomes the filter')
        names = ev("[...document.querySelectorAll('#mhSlRows [data-sl]')].map(e=>e.dataset.n).sort()")
        if names != ['Zzqx Heylo Mystery', 'Zzqx Heylo Soup', 'Zzqx Heylo Yoghurt']: f.add('BUG', f'3: only the matching foods are listed: {names}')
        # 2) tick all shown, apply Bought at Heylo + Kept in fridge
        page.click('#mhSlBulk button:has-text("Tick all shown")'); page.wait_for_timeout(200)
        if '3 ticked' not in ev("document.getElementById('mhSlTicked').innerText"): f.add('BUG', '4: Tick all shown ticks every shown row')
        k0 = ev("mhShopKey('Zzqx Heylo Yoghurt')"); page.uncheck('[data-pick="%s"]' % k0); page.wait_for_timeout(150)
        if '2 ticked' not in ev("document.getElementById('mhSlTicked').innerText") or ev("!!mhSlState().sel[%r]" % k0): f.add('BUG', '4b: unticking one row removes it from the ticked set')
        page.check('[data-pick="%s"]' % k0); page.wait_for_timeout(150)
        page.click('[data-slshop="Heylo"]'); page.select_option('#mhSlBulkStore', 'fridge'); page.click('#mhSlBulk button:has-text("Add to my cupboards")'); page.wait_for_timeout(300)
        st = ev("Object.fromEntries(Object.values(mhStockLoad().items).map(i=>[i.name,[i.shop,i.store||'',i.base]]))")
        if st.get('Zzqx Heylo Soup') != ['Heylo', 'fridge', 'g'] or st.get('Zzqx Heylo Yoghurt') != ['Heylo', 'fridge', 'ml']: f.add('BUG', f'5: ticked foods get the shop and where they are kept: {st}')
        if 'Zzqx Heylo Mystery' in st: f.add('BUG', '6: a food with no known unit is skipped, never guessed')
        if 'skipped' not in ev("document.getElementById('mhShopMsg')?.innerText||''"): f.add('BUG', '7: and the skipped count is said')
        if 'Zzqx Other Rice' in st: f.add('BUG', '8: unticked / non-matching foods are untouched')
        # 3) individually: tick one, put on the list under the chosen shop
        page.click('[data-pick="%s"]' % ev("mhShopKey('Zzqx Heylo Yoghurt')")); page.click('[data-slshop="Heylo"]'); page.click('#mhSlBulk button:has-text("Put on the list")'); page.wait_for_timeout(300)
        on = ev("mhShopLoad().items.map(i=>[i.name,i.shop])")
        if on != [['Zzqx Heylo Yoghurt', 'Heylo']]: f.add('BUG', f'9: one ticked food goes on the list under Heylo: {on}')
        # 4) the per-row Kept in
        page.select_option('[data-sl="%s"] [data-f="store"]' % ev("mhShopKey('Zzqx Heylo Soup')"), 'freezer'); page.wait_for_timeout(300)
        if ev("mhStockLoad().items[mhShopKey('Zzqx Heylo Soup')].store") != 'freezer': f.add('BUG', '10: a row has its own Kept in')
    # 5) switched off: nothing new shows, nothing is created, and it stays off
    ev("localStorage.removeItem(MH_STOCK_KEY); mhStockTrack('Zzqx Tea',{base:'g'}); mhStockSetLevel(mhShopKey('Zzqx Tea'),250); (()=>{const o=mhStockLoad(); o.enabled=false; mhStockSave(o);})()")
    ev("(()=>{const s=mhShopLoad(); s.items=[{id:'q1',key:'zzqx tissues',name:'Zzqx Tissues',cat:'nonfood',checked:true,shop:s.shop,nonFood:true,src:'own',from:''},{id:'q2',key:'zzqx tea',name:'Zzqx Tea',cat:'other',checked:false,shop:s.shop,src:'own',from:''}]; mhShopSave(s);})()")
    ev("_shopUi.view='list'; _shopUi.addOpen=true; mhShopAddKind('food')"); page.wait_for_timeout(300)
    if page.locator('button:has-text("Search my foods and pick several")').count(): f.add('BUG', '11: with stock off the Add box has no stock search button')
    ev("mhShopComplete()"); page.wait_for_timeout(200); page.click('#appModalConfirm'); page.wait_for_timeout(400)
    if ev("mhStockLoad().enabled") is not False: f.add('BUG', '12: Shopping complete does not switch stock back on')
    if ev("Object.keys(mhStockLoad().items).join()") != 'zzqx tea': f.add('BUG', '13: and creates nothing on the shelf')
    ev("_shopUi.view='list'; mhShopRender()"); ev("(()=>{const s=mhShopLoad(); s.items=[{id:'q3',key:mhShopKey('Zzqx Tea'),name:'Zzqx Tea',cat:'other',checked:false,shop:s.shop,src:'own',from:''}]; mhShopSave(s);})()"); ev("mhShopRender()"); page.wait_for_timeout(300)
    if page.locator('#mhShopPane [data-stocknote]').count(): f.add('BUG', '14: with stock off the list rows show no stock amounts')
    ev("(()=>{const o=mhStockLoad(); o.enabled=true; mhStockSave(o);})()"); ev("mhShopRender()"); page.wait_for_timeout(300)
    if not page.locator('#mhShopPane [data-stocknote]').count(): f.add('BUG', '15: with stock on they do')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
