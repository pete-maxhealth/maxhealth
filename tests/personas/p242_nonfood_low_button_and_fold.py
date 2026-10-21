"""Persona 242: non-nutritional stock has a hand-operated running-low button, and its group on the list starts folded (v3.10.1137).
Pete: no way of policing a reorder level for toilet roll, so he marks it low himself; it goes on the list, then basket, Shopping complete, and it is still on the shelf. Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("mhShopOpen()"); page.wait_for_timeout(300)
    ev("mhStockAddNonFood('Zzqx Toilet Roll', 'Asda')") if ev("typeof mhStockAddNonFood") == 'function' else None
    if not ev("!!mhStockLoad().items[mhShopKey('Zzqx Toilet Roll')]"):
        ev("mhStockTrack('Zzqx Toilet Roll',{base:'each'}); (()=>{const o=mhStockLoad(); o.items[mhShopKey('Zzqx Toilet Roll')].nonFood=true; o.items[mhShopKey('Zzqx Toilet Roll')].level=4; mhStockSave(o);})()")
    ev("_shopUi.view='list'; mhShopRender()"); page.wait_for_timeout(300)
    if not page.locator('[data-stock="Zzqx Toilet Roll"] [data-lowbtn]').count(): f.add('BUG', '1: a non-nutritional cupboard row has a running-low button')
    else:
        page.click('[data-stock="Zzqx Toilet Roll"] [data-lowbtn]'); page.wait_for_timeout(300)
        it = ev("mhShopLoad().items.find(i=>i.name==='Zzqx Toilet Roll')")
        if not it or not it.get('nonFood'): f.add('BUG', f'2: tapping it puts the item on the shopping list as non-food: {it}')
        if not page.locator('[data-stock="Zzqx Toilet Roll"] [data-lowlist]').count(): f.add('BUG', '3: the row then shows ON LIST')
        # folded by default on the list
        ev("_shopUi.fold={}; _shopUi.view='list'; mhShopRender()"); page.wait_for_timeout(200)
        if page.locator('#mhShopPane [data-item="Zzqx Toilet Roll"]').count(): f.add('BUG', '4: the Non-nutritional group on the list starts folded')
        ev("mhShopFold('m' + (MH_SHOP_WALK.length + 1))"); page.wait_for_timeout(200)
        if not page.locator('#mhShopPane [data-item="Zzqx Toilet Roll"]').count(): f.add('BUG', '5: one tap opens it')
        # basket, complete: still on the shelf
        ev("(()=>{const s=mhShopLoad(); s.items.forEach(i=>i.checked=true); mhShopSave(s);})()"); ev("mhShopComplete()"); page.wait_for_timeout(300)
        if ev("mhShopLoad().items.length") != 0: f.add('BUG', '6: Shopping complete clears it from the list')
        if not ev("!!mhStockLoad().items[mhShopKey('Zzqx Toilet Roll')]"): f.add('BUG', '7: it is still on the shelf afterwards')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
