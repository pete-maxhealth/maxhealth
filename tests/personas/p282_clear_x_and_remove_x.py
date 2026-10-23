"""Persona 282: an X clears each typing box, an X removes a cupboard food, and + Shop is in the cupboards pane (v3.10.1179). Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("['Zzqx Flatbread','Zzqx Crackers'].forEach(n=>{mhStockTrack(n,{base:'g',shop:'Asda'}); mhStockSetLevel(mhShopKey(n),200)})")
    ev("switchTabById('shop')"); page.wait_for_timeout(500)
    # list pane: type in Add to the list, X appears, clears
    ev("_shopUi.addOpen = true; mhShopRender()"); page.wait_for_timeout(300)
    vis = lambda sel: ev("(s)=>{const e=document.querySelector(s); return !!e && getComputedStyle(e).display!=='none'}", sel)
    if vis('[data-clear-for="mhShopOwn"]'): f.add('BUG', 'no X while the box is empty')
    page.fill('#mhShopOwn', 'Zzqx test'); page.wait_for_timeout(200)
    if not vis('[data-clear-for="mhShopOwn"]'): f.add('BUG', 'an X shows once there is text')
    page.click('[data-clear-for="mhShopOwn"]'); page.wait_for_timeout(200)
    if ev("document.getElementById('mhShopOwn').value") != '': f.add('BUG', 'the X clears the box')
    # cupboards pane: search box X, row X, + Shop
    page.click('#mhShopSwitch [data-pane="stock"]'); page.wait_for_timeout(400)
    if not page.locator('#mhCbShops [data-cbshop-add]').count(): f.add('BUG', '+ Shop in the cupboards pane')
    k = ev("mhShopKey('Zzqx Crackers')")
    page.click('[data-stock="Zzqx Crackers"] [title="Remove from my cupboards"]'); page.wait_for_timeout(300); page.click('#appModalConfirm'); page.wait_for_timeout(500)
    if ev("!!mhStockLoad().items[%r]" % k): f.add('BUG', 'the row X removes the food after asking')
    if not ev("!!mhStockLoad().items[mhShopKey('Zzqx Flatbread')]"): f.add('BUG', 'only that food is removed')
    # the Add a food screen's search box also gets an X
    ev("mhShopView('stockadd')"); page.wait_for_timeout(400)
    if not page.locator('[data-clear-for="mhStockQ"]').count(): f.add('BUG', 'the Add a food search box has an X')
    page.fill('#mhStockQ', 'zzqx'); page.wait_for_timeout(300)
    page.click('[data-clear-for="mhStockQ"]'); page.wait_for_timeout(400)
    if ev("document.getElementById('mhStockQ').value") != '': f.add('BUG', 'its X clears the search')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
