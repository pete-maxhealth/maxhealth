"""Persona 297: a shop's ✕ hides it the same way on the list, My cupboards and Add foods; it disappears from all three together; Hidden shops brings it back (v3.10.1196). Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()"); ev("localStorage.setItem('mh_shop_pane','both')")
    ev("mhShopAddShopNamed('Zzqx Nicks'); mhShopSetShop('Asda'); mhStockTrack('Zzqx Bar',{base:'g',shop:'Zzqx Nicks'}); mhStockSetLevel(mhShopKey('Zzqx Bar'),100)")
    ev("switchTabById('shop')"); page.wait_for_timeout(500)
    where = {'list': '#mhShopChips', 'cupboards': '#mhCbShops'}
    for name, sel in where.items():
        if not page.locator(sel + ' [data-hideshop="Zzqx Nicks"]').count(): f.add('BUG', f'{name}: the shop has a hide ✕')
        if page.locator(sel + ' [data-delshop]').count(): f.add('BUG', f'{name}: no ✕ deletes a shop outright')
    ev("_shopUi.view='stocklist'; mhSlState().f='all'; mhShopRender()"); page.wait_for_timeout(400)
    if not page.locator('#mhSlShops [data-hideshop="Zzqx Nicks"]').count(): f.add('BUG', 'Add foods: the shop has a hide ✕')
    page.click('#mhSlShops [data-hideshop="Zzqx Nicks"]'); page.wait_for_timeout(500)
    if page.locator('#mhSlShops [data-slshop="Zzqx Nicks"]').count(): f.add('BUG', 'Add foods: hidden, it is gone from the chips')
    if 'Hidden shops (1)' not in ev("document.getElementById('mhSlShops').innerText"): f.add('BUG', 'Add foods: a Hidden shops line')
    ev("_shopUi.view='list'; mhShopRender()"); page.wait_for_timeout(400)
    if page.locator('#mhShopChips button[data-shop="Zzqx Nicks"]').count() or page.locator('#mhCbShops [data-cbshop="Zzqx Nicks"]').count(): f.add('BUG', 'hidden in one place, it is hidden in all')
    ev("mhShopOn('Zzqx Nicks')"); page.wait_for_timeout(400)
    if not page.locator('#mhShopChips button[data-shop="Zzqx Nicks"]').count() or not page.locator('#mhCbShops [data-cbshop="Zzqx Nicks"]').count(): f.add('BUG', 'brought back, it is back in all')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
