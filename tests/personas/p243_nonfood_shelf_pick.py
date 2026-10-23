"""Persona 243: Non-nutritional on the Add card lists what is on the shelf, My cupboards always has the Non-nutritional tab, and a typed search offers Add as non-nutritional (v3.10.1138).
Pete: "I have to type the name when I don't know what's on the shelf" and "My cupboard doesn't give me the option to add a non-nutritional item". Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("localStorage.setItem('mh_shop_pane','both')")   # these tests look at the list and the cupboards together (v3.10.1177)
    ev("mhShopOpen()"); page.wait_for_timeout(300)
    ev("mhStockTrack('Zzqx Cheese',{base:'g'})"); ev("mhStockSetLevel(mhShopKey('Zzqx Cheese'),200)")
    ev("_shopUi.addOpen=true; mhShopAddKind('nonfood')"); page.wait_for_timeout(300)
    if 'Nothing non-nutritional on your shelf' not in ev("document.getElementById('mhNfShelf')?.innerText||''"): f.add('BUG', '1: empty shelf says so')
    # tab is there even with nothing in it, and a typed search offers non-nutritional
    ev("mhCbTab('all'); mhShopRender()"); page.wait_for_timeout(200)
    if not page.locator('#mhCbTabs [data-cb="nonfood"]').count(): f.add('BUG', '2: the Non-nutritional tab shows even when empty')
    ev("mhCbTab('nonfood')"); page.wait_for_timeout(200)
    if 'No non-nutritional items yet' not in ev("document.getElementById('stockctlCard').innerText"): f.add('BUG', '3: the empty tab explains what to do')
    ev("mhCbQ('Zzqx Soap')"); page.wait_for_timeout(300)
    if not page.locator('[data-add-nonfood]').count(): f.add('BUG', '4: typing a new name offers Add as non-nutritional')
    else:
        ev("mhStockAddNonFood('Zzqx Soap')"); page.wait_for_timeout(300)
    ev("mhStockAddNonFood('Zzqx Bin Bags')"); page.wait_for_timeout(200)
    ev("_shopUi.view='list'; _shopUi.addOpen=true; mhShopAddKind('nonfood')"); page.wait_for_timeout(300)
    names = ev("[...document.querySelectorAll('[data-nfshelf]')].map(e=>e.dataset.nfshelf)")
    if sorted(names) != ['Zzqx Bin Bags', 'Zzqx Soap']: f.add('BUG', f'5: the shelf list shows the non-nutritional items and not the food: {names}')
    else:
        page.click('[data-nfshelf="Zzqx Soap"] button'); page.wait_for_timeout(300)
        it = ev("mhShopLoad().items.find(i=>i.name==='Zzqx Soap')")
        if not it or not it.get('nonFood'): f.add('BUG', f'6: tapping it puts it on the list as non-food: {it}')
        ev("mhShopAddKind('nonfood')"); page.wait_for_timeout(200)
        if 'ON LIST' not in ev("document.querySelector('[data-nfshelf=\"Zzqx Soap\"]')?.innerText||''"): f.add('BUG', '7: it then shows ON LIST')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
