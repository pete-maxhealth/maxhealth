"""Persona 284: a new non-nutritional item added from the list also lands in the cupboards; a shop can be removed from the list pane, the cupboards pane and Add foods (v3.10.1181). Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("mhStockTrack('Zzqx Seed rice',{base:'g'})")   # cupboards are on once anything is counted
    ev("switchTabById('shop')"); page.wait_for_timeout(400)
    msg = lambda: ev("document.getElementById('mhShopPane').innerText")
    # 1. new non-nutritional from the list: also in the cupboards
    ev("_shopUi.addOpen = true; mhShopAddKind('nonfood')"); page.wait_for_timeout(300)
    page.fill('#mhShopOwn', 'Zzqx Washing up liquid'); ev("mhShopAddOwn()"); page.wait_for_timeout(500)
    it = ev("mhStockLoad().items[mhShopKey('Zzqx Washing up liquid')]")
    if not it or not it.get('nonFood'): f.add('BUG', f'a new non-nutritional item from the list is also in the cupboards: {it}')
    if 'and to your cupboards' not in msg(): f.add('BUG', 'and the message says so')
    # 2. again: no duplicates
    ev("mhShopAddKind('nonfood')"); page.wait_for_timeout(300)
    page.fill('#mhShopOwn', 'Zzqx Washing up liquid'); ev("mhShopAddOwn()"); page.wait_for_timeout(500)
    if ev("Object.keys(mhStockLoad().items).filter(k=>/washing up liquid/.test(k)).length") != 1: f.add('BUG', 'no second cupboard entry')
    # 3. already a cupboard food: list add says so and leaves it alone
    ev("mhStockTrack('Zzqx Bin bags',{base:'each'}); const o=mhStockLoad(); o.items[mhShopKey('Zzqx Bin bags')].nonFood=true; mhStockSave(o)")
    ev("mhShopAddKind('nonfood')"); page.wait_for_timeout(300)
    page.fill('#mhShopOwn', 'Zzqx Bin bags'); ev("mhShopAddOwn()"); page.wait_for_timeout(500)
    if 'already in your cupboards' not in msg(): f.add('BUG', 'it says it is already in the cupboards')
    # 4. a food is NOT copied to the cupboards by the list
    ev("mhShopAddKind('food')"); page.wait_for_timeout(300)
    page.fill('#mhShopOwn', 'Zzqx Spinach'); ev("mhShopAddOwn()"); page.wait_for_timeout(500)
    if ev("!!mhStockLoad().items[mhShopKey('Zzqx Spinach')]"): f.add('BUG', 'plain food from the list does not go into the cupboards')
    # 5. shops: remove from every place
    ev("mhShopAddShopNamed('Zzqx Butchers')"); page.wait_for_timeout(300)
    ev("mhStockTrack('Zzqx Sausages',{base:'g',shop:'Zzqx Butchers'}); const s=mhShopLoad(); mhShopSetAdd(s,'Zzqx Mince','own','',null); s.items[s.items.length-1].shop='Zzqx Butchers'; mhShopSave(s)")
    ev("mhShopRender()"); page.wait_for_timeout(300)
    if page.locator('#mhShopChips span[data-shop="Zzqx Butchers"]').count(): f.add('BUG', 'a shop with items on the list has no list-screen ✕ (it is hide-only, and only for empty shops)')
    page.click('#mhShopSwitch [data-pane="stock"]'); page.wait_for_timeout(400)
    if not page.locator('#mhCbShops [data-delshop="Zzqx Butchers"]').count(): f.add('BUG', 'an X on the cupboards pane shop row')
    page.click('#mhCbShops [data-delshop="Zzqx Butchers"]'); page.wait_for_timeout(300); page.click('#appModalConfirm'); page.wait_for_timeout(500)
    if 'Zzqx Butchers' in ev("mhShopLoad().shops"): f.add('BUG', 'the shop is removed')
    if ev("mhShopLoad().items.some(i=>i.name==='Zzqx Mince')"): f.add('BUG', 'its list items come off the list')
    sau = ev("mhStockLoad().items[mhShopKey('Zzqx Sausages')]")
    if not sau or sau.get('shop'): f.add('BUG', f'its cupboard foods stay, with no shop: {sau}')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
