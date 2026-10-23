"""Persona 295: Shopping complete can clear the ticked items without touching the cupboards or opening the stock review; Empty the basket still opens the review (v3.10.1194). Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    def setup():
        ev("mhStockTrack('Zzqx Rice',{base:'g'}); mhStockSetLevel(mhShopKey('Zzqx Rice'),500); const s=mhShopLoad(); if(!s.items.some(i=>i.name==='Zzqx Rice'))mhShopSetAdd(s,'Zzqx Rice','own','',null); if(!s.items.some(i=>i.name==='Zzqx Bin bags'))mhShopSetAdd(s,'Zzqx Bin bags','own','',null,{nonFood:true}); s.items.forEach(i=>{if(/Zzqx/.test(i.name))i.checked=true}); mhShopSave(s)")
    setup(); ev("switchTabById('shop')"); page.wait_for_timeout(400)
    ev("mhShopComplete()"); page.wait_for_timeout(300)
    if not page.locator('#appModalClear').count(): f.add('BUG', 'the box offers a way to clear and leave the cupboards alone')
    else:
        page.click('#appModalClear'); page.wait_for_timeout(500)
        if ev("mhShopLoad().items.some(i=>/Zzqx/.test(i.name)&&i.checked)"): f.add('BUG', 'the ticked items are cleared')
        if ev("_shopUi.view") == 'stockbought': f.add('BUG', 'no stock review opens')
        if ev("mhStockLoad().items[mhShopKey('Zzqx Rice')].level") != 500: f.add('BUG', 'the count is untouched')
        if ev("!!mhStockLoad().items[mhShopKey('Zzqx Bin bags')]"): f.add('BUG', 'nothing is put on the shelf')
    # Empty the basket still opens the review
    setup(); ev("mhShopRender(); mhShopComplete()"); page.wait_for_timeout(300); page.click('#appModalConfirm'); page.wait_for_timeout(500)
    if ev("_shopUi.view") != 'stockbought': f.add('BUG', 'Empty the basket still opens the add-to-cupboards review')
    if ev("mhStockLoad().items[mhShopKey('Zzqx Rice')].level") != 500: f.add('BUG', 'and still changes no count until you confirm')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
