"""Persona 291: list entries that came from the cupboards sit under the shop the food is bought at, and a shop with them is not empty (v3.10.1190). Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("mhShopAddShopNamed('Zzqx Heylo'); mhShopSetShop('Asda')")
    # a food with no shop runs low -> list under Asda; then it is given a shop
    ev("mhStockTrack('Zzqx Bread',{base:'g'}); mhStockSetLevel(mhShopKey('Zzqx Bread'),0); mhStockSetReorder(mhShopKey('Zzqx Bread'),100); mhStockSweep()")
    if ev("mhShopLoad().items.find(i=>i.key===mhShopKey('Zzqx Bread'))?.shop") != 'Asda': f.add('BUG', 'setup: it starts on the Asda list')
    ev("mhStockTrack('Zzqx Bread',{base:'g',shop:'Zzqx Heylo'})")
    if ev("mhShopLoad().items.find(i=>i.key===mhShopKey('Zzqx Bread'))?.shop") != 'Zzqx Heylo': f.add('BUG', 'giving a food a shop moves its list entry, even from no shop')
    # data already in the wrong place is put right when the screen draws
    ev("const s=mhShopLoad(); s.items.find(i=>i.key===mhShopKey('Zzqx Bread')).shop='Asda'; mhShopSave(s)")
    ev("switchTabById('shop')"); page.wait_for_timeout(500)
    if ev("mhShopLoad().items.find(i=>i.key===mhShopKey('Zzqx Bread'))?.shop") != 'Zzqx Heylo': f.add('BUG', 'an entry filed under the wrong shop is moved to the food\'s shop')
    if 'Zzqx Heylo (1)' not in ev("document.getElementById('mhShopChips').innerText"): f.add('BUG', 'the shop chip shows its count')
    # something ticked in the basket is left where it is
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
