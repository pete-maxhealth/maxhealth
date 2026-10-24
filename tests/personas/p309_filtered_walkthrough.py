"""Persona 309: select all of Filtered, Put back on shelf -> each food that still needs details opens one at a time ("Food n of N"), Next is refused until that food is complete, Finish puts them all back, the result names them and says which are low and on the list; Stop here keeps the rest in Filtered. Invented foods."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
names = ['Zzqx Chicken', 'Zzqx Salmon', 'Zzqx Broccoli', 'Zzqx Spinach', 'Zzqx Cheddar', 'Zzqx Eggs', 'Zzqx Olive', 'Zzqx Almonds']
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay').style.display='none'"); ev("localStorage.setItem('mh_shop_pane','both')")
    lib = str([{'id': 'i%d' % i, 'name': n, 'kcal': 100, 'protein': 5, 'carbs': 5, 'fat': 5, 'portion': '100g'} for i, n in enumerate(names)]).replace("'", '"')
    ev("window._mhLibQuiet=true; saveLibrary(%s)" % lib); ev("window.appConfirm=(m,ok)=>{ok&&ok()}; mhLibToFiltered()")
    ev("switchTabById('shop')"); page.wait_for_timeout(400); ev("_shopUi.heldOpen=true; mhShopRender()")
    if ev("mhShopHeldFoods().length") != 8: f.add('BUG', 'eight foods in Filtered')
    ev("mhShopHeldAll()"); ev("mhShopHeldRelease()"); page.wait_for_timeout(300)
    if 'Food 1 of 8' not in page.inner_text('#mhCqHead'): f.add('BUG', 'first screen says Food 1 of 8')
    if ev("mhShopHeldFoods().length") != 8: f.add('BUG', 'nothing leaves Filtered before it is complete')
    page.click('#mhCqNext'); page.wait_for_timeout(200)
    if 'Still needs' not in (page.inner_text('#mhStkErr') if page.query_selector('#mhStkErr') else ''): f.add('BUG', 'Next is refused with a reason while details are missing')
    if 'Food 1 of 8' not in page.inner_text('#mhCqHead'): f.add('BUG', 'stays on food 1 when refused')
    for i in range(8):
        txt = page.inner_text('#mhCqHead')
        if 'Food %d of 8' % (i + 1) not in txt: f.add('BUG', f'screen {i+1}: {txt}')
        nm = ev("_shopUi.stk.name")
        if nm not in page.inner_text('body'): f.add('BUG', f'screen {i+1} names the food {nm}')
        ev("(()=>{const f=_shopUi.stk; f.shop='Asda'; f.reorder='%d'; f.reorderU=f.base; mhStkCommit('reorder')})()" % (200 if i < 5 else 0 if False else 50)); page.wait_for_timeout(100)
        # stock 0 and reorder set => low; the last three have stock 500 so are not low
        if i >= 5: ev("(()=>{const f=_shopUi.stk; f.level='500'; f.levelU=f.base; mhStkCommit('level')})()")
        page.click('#mhCqNext'); page.wait_for_timeout(200)
    msg = page.inner_text('body')
    if ev("mhShopHeldFoods().length") != 0: f.add('BUG', 'all eight are out of Filtered after Finish')
    if 'Put 8 back' not in msg or not all(n in msg for n in names): f.add('BUG', f'result names all eight: {msg[:300]}')
    if '5 on your list now' not in msg: f.add('BUG', f'result says which are low: {msg[:300]}')
    onlist = ev("mhShopLoad().items.filter(i=>/Zzqx/.test(i.name)).length")
    if onlist != 5: f.add('BUG', f'five low foods on the list, got {onlist}')
    # Stop here keeps the rest
    ev("mhStockLoad(); const o=mhStockLoad(); Object.values(o.items).forEach(it=>{ if(/Zzqx (Chicken|Salmon|Broccoli)/.test(it.name)){ it.held=true; it.onboard=true; delete it.reorder; } }); mhStockSave(o); mhShopRender()")
    ev("_shopUi.heldOpen=true; mhShopHeldAll(); mhShopHeldRelease()"); page.wait_for_timeout(200)
    ev("(()=>{const f=_shopUi.stk; f.shop='Asda'; f.reorder='50'; f.reorderU=f.base; mhStkCommit('reorder')})()"); page.click('#mhCqNext'); page.wait_for_timeout(200)
    ev("mhCqStop()"); page.wait_for_timeout(200)
    if ev("mhShopHeldFoods().length") != 2: f.add('BUG', 'Stop here puts back the finished one and keeps two in Filtered')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
