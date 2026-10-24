"""Persona 244: non-nutritional items bought through the list land on the shelf at Shopping complete (v3.10.1139).
Pete imported cola, Irn-Bru, Vimto, sugar as a list marked non-nutritional; after Shopping complete they were nowhere. Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("mhStockTrack('Zzqx Seed',{base:'g'})")   # stock on: with it switched off nothing is shelved (v3.10.1147)
    ev("mhShopOpen()"); ev("mhOrdOpen('list')"); page.wait_for_timeout(200)
    page.fill('#mhOrdText', "Zzqx Cola\nZzqx Squash\nZzqx Double Cream\n"); page.click('#mhOrdRead'); page.wait_for_timeout(400)
    ev("mhOrdKindSet(0,'nonfood'); mhOrdKindSet(1,'nonfood')"); ev("mhOrdShop('Asda')"); page.click('#mhOrdGo'); page.wait_for_timeout(500)
    ev("(()=>{const s=mhShopLoad(); s.items.forEach(i=>i.checked=true); mhShopSave(s);})()"); ev("mhShopComplete()"); page.click("#appModalConfirm"); page.wait_for_timeout(400)
    st = ev("Object.values(mhStockLoad().items).map(i=>[i.name,!!i.nonFood,i.level])")
    if sorted(n for n, nf, l in st if nf) != ['Zzqx Cola (Asda)', 'Zzqx Squash (Asda)']: f.add('BUG', f'1: the two non-nutritional items are on the shelf as non-food: {st}')
    if any('Cream' in n for n, nf, l in st): f.add('BUG', f'2: the food is not put on the shelf: {st}')
    if any(l not in (None, 0) and nf for n, nf, l in st): f.add('BUG', f'3: no count is invented: {st}')
    if ev("mhShopLoad().items.length") != 0: f.add('BUG', '4: the list is emptied')
    ev("localStorage.setItem('mh_shop_pane','both'); _shopUi.view='list'; mhShopRender(); mhCbTab('nonfood')"); page.wait_for_timeout(300)
    if page.locator('#stockctlCard [data-stock]').count() != 2: f.add('BUG', '5: they now show on My cupboards > Non-nutritional')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
