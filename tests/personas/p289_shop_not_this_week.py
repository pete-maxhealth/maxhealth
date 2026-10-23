"""Persona 289: on the list screen a shop with nothing on the list can be hidden for the week without deleting anything, and brought back or deleted from Hidden shops (v3.10.1187). Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("mhStockTrack('Zzqx Sausages',{base:'g',shop:'Zzqx Butchers'})")
    ev("mhShopAddShopNamed('Zzqx Butchers'); mhShopAddShopNamed('Zzqx Bakery')"); page.wait_for_timeout(300)
    ev("const s=mhShopLoad(); mhShopSetAdd(s,'Zzqx Loaf','own','',null); s.items[s.items.length-1].shop='Zzqx Bakery'; mhShopSave(s)"); ev("mhShopRender()"); page.wait_for_timeout(300)
    ev("switchTabById('shop')"); page.wait_for_timeout(500)
    x = lambda n: page.locator('#mhShopChips span[data-shop="%s"]' % n).count()
    if x('Zzqx Bakery'): f.add('BUG', 'a shop with something on the list has no ✕')
    if not x('Zzqx Butchers'): f.add('BUG', 'a shop with nothing on the list has a ✕')
    page.click('#mhShopChips span[data-shop="Zzqx Butchers"]'); page.wait_for_timeout(300)
    if 'Zzqx Butchers' not in ev("mhShopLoad().shops"): f.add('BUG', 'hiding does not delete the shop')
    if ev("mhStockLoad().items[mhShopKey('Zzqx Sausages')].shop") != 'Zzqx Butchers': f.add('BUG', 'cupboard foods keep their shop')
    if page.locator('#mhShopChips button[data-shop="Zzqx Butchers"]').count(): f.add('BUG', 'the shop is hidden from the list screen')
    if 'Hidden shops (1)' not in ev("document.getElementById('mhShopPane').innerText"): f.add('BUG', 'a Hidden shops line says how many')
    ev("mhShopOffToggle()"); page.wait_for_timeout(300)
    page.click('button[data-shop="Zzqx Butchers"]'); page.wait_for_timeout(300)
    if not page.locator('#mhShopChips button[data-shop="Zzqx Butchers"]').count(): f.add('BUG', 'tapping a hidden shop brings it back')
    # hide, then delete for good from Hidden shops
    page.click('#mhShopChips span[data-shop="Zzqx Butchers"]'); page.wait_for_timeout(300); ev("_shopUi.offOpen=true; mhShopRender()"); page.wait_for_timeout(300)
    page.click('span[title="Delete this shop"]'); page.wait_for_timeout(300)
    if page.locator('#appModalConfirm').count(): page.click('#appModalConfirm'); page.wait_for_timeout(400)
    if 'Zzqx Butchers' in ev("mhShopLoad().shops"): f.add('BUG', 'the ✕ in Hidden shops deletes it for good')
    # the last visible shop cannot be hidden
    if ev("(()=>{const s=mhShopLoad();return s.shops.length})()") >= 2:
        ev("mhShopOff('Zzqx Bakery')")
    if not page.locator('#mhShopChips button').count(): f.add('BUG', 'at least one shop stays visible')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
