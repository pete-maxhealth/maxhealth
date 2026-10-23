"""Persona 299: the default shop can be chosen; new foods go to it; deleting the default hands it to another shop (v3.10.1198). Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()"); ev("localStorage.setItem('mh_shop_pane','both')")
    ev("mhShopAddShopNamed('Zzqx Lidl'); mhShopSetShop('Asda')"); ev("switchTabById('shop')"); page.wait_for_timeout(500)
    if ev("mhShopLoad().def") != 'Asda': f.add('BUG', 'Asda starts as the default')
    if not page.locator('#mhShopDef select').count(): f.add('BUG', 'a Default shop dropdown shows with two shops')
    page.select_option('#mhShopDef select', 'Zzqx Lidl'); page.wait_for_timeout(400)
    if ev("mhShopLoad().def") != 'Zzqx Lidl': f.add('BUG', 'choosing Lidl makes it the default')
    ev("const s=mhShopLoad(); mhShopSetAdd(s,'Zzqx Plain','own'); mhShopSave(s)")
    ev("mhShopSetShop('Asda'); mhShopSetShop('Zzqx Lidl')")
    # delete the default through hide -> delete for good
    ev("mhShopOff('Zzqx Lidl')"); page.wait_for_timeout(300); ev("mhShopDelShop('Zzqx Lidl')"); page.wait_for_timeout(400)
    if ev("mhShopLoad().shops.includes('Zzqx Lidl')"): f.add('BUG', 'the default shop can be deleted')
    if ev("mhShopLoad().def") != 'Asda': f.add('BUG', 'deleting the default hands it to another shop')
    if ev("mhShopLoad().shops.length") != 1 or page.locator('#mhShopDef').count(): f.add('BUG', 'one shop left: no dropdown')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
