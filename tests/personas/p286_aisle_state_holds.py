"""Persona 286: aisles you opened stay open and ones you closed stay closed through adding items, switching panes/tabs and a reload (v3.10.1182). Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("mhStockTrack('Zzqx Rice',{base:'g'}); mhStockTrack('Zzqx Beans',{base:'g'})")
    ev("const s=mhShopLoad(); ['Zzqx Milk','Zzqx Bread','Zzqx Apples'].forEach(n=>mhShopSetAdd(s,n,'own','',null)); mhShopSave(s)")
    ev("switchTabById('shop')"); page.wait_for_timeout(500)
    open_list = lambda: ev("[...document.querySelectorAll('#mhShopPane [data-item]')].map(e=>e.dataset.item)")
    ev("(()=>{const h=document.querySelector('#mhShopPane [data-aisle], #mhShopPane [onclick*=mhShopFold]');if(h)h.click()})()"); page.wait_for_timeout(300)
    before = open_list()
    if not before: f.add('INFO', 'no aisle header could be opened to test')
    # add an item to another aisle, switch pane, switch tab, come back, reload
    ev("_shopUi.addOpen=true; mhShopAddKind('food')"); page.wait_for_timeout(200)
    page.fill('#mhShopOwn', 'Zzqx Cheese'); ev("mhShopAddOwn()"); page.wait_for_timeout(500)
    ev("mhShopPaneSet('stock')"); page.wait_for_timeout(300); ev("mhShopPaneSet('list')"); page.wait_for_timeout(300)
    ev("switchTabById('log')"); page.wait_for_timeout(300); ev("switchTabById('shop')"); page.wait_for_timeout(400)
    mid = open_list()
    for n in before:
        if n not in mid: f.add('BUG', f'{n} was visible and then closed itself after add / pane / tab switch')
    page.reload(); page.wait_for_timeout(1500); ev("document.getElementById('onboardingOverlay')?.remove()"); ev("switchTabById('shop')"); page.wait_for_timeout(500)
    after = open_list()
    for n in mid:
        if n not in after: f.add('BUG', f'{n} was visible and then closed itself after a reload')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
