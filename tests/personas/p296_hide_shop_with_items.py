"""Persona 296: a shop with items can be hidden (asks first); its items come off, its low foods are not added while hidden and return when it is brought back; the list tag says running low only for entries that came from running low (v3.10.1195). Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()"); ev("localStorage.setItem('mh_shop_pane','both')")
    ev("mhShopAddShopNamed('Zzqx Heylo'); mhShopSetShop('Asda')")
    ev("mhStockTrack('Zzqx Granola',{base:'g',shop:'Zzqx Heylo'}); const k=mhShopKey('Zzqx Granola'); mhStockSetReorder(k,100); mhStockSetLevel(k,0); mhStockSweep()")
    ev("mhStockTrack('Zzqx Jam',{base:'g'}); mhStockSetLevel(mhShopKey('Zzqx Jam'),200); mhStockSetReorder(mhShopKey('Zzqx Jam'),100); const s=mhShopLoad(); mhShopSetAdd(s,'Zzqx Jam','stock','added by hand',null); mhShopSave(s)")
    ev("switchTabById('shop')"); page.wait_for_timeout(500)
    ev("mhShopSetShop('Asda')"); page.wait_for_timeout(300); ev("window.mhShopIsShut=()=>false; mhShopRender()"); page.wait_for_timeout(300)
    txt = ev("(()=>{const e=[...document.querySelectorAll('#mhShopPane [data-item]')].find(e=>e.dataset.item==='Zzqx Jam');return e?e.innerText:''})()")
    if 'running low' in txt: f.add('BUG', f'an entry added by hand does not say running low: {txt!r}')
    if not page.locator('#mhShopChips span[data-shop="Zzqx Heylo"]').count(): f.add('BUG', 'a shop with items has a hide ✕')
    else:
        page.click('#mhShopChips span[data-shop="Zzqx Heylo"]'); page.wait_for_timeout(300)
        if not page.locator('#appModalConfirm').count(): f.add('BUG', 'hiding a shop that has items asks first')
        else: page.click('#appModalConfirm'); page.wait_for_timeout(500)
    if ev("mhShopLoad().items.some(i=>i.shop==='Zzqx Heylo')"): f.add('BUG', 'its items come off the list')
    if 'Zzqx Heylo' not in ev("mhShopOffLoad()"): f.add('BUG', 'the shop is hidden')
    if not ev("!!mhStockLoad().items[mhShopKey('Zzqx Granola')]"): f.add('BUG', 'the cupboards are untouched')
    ev("mhStockSweep()")
    if ev("mhShopLoad().items.some(i=>i.key===mhShopKey('Zzqx Granola'))"): f.add('BUG', 'while hidden, its low foods are not added again')
    ev("mhShopOn('Zzqx Heylo'); mhStockSweep()"); page.wait_for_timeout(300)
    if not ev("mhShopLoad().items.some(i=>i.key===mhShopKey('Zzqx Granola') && i.shop==='Zzqx Heylo')"): f.add('BUG', 'bringing the shop back returns its low foods')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
