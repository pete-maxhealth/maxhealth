"""Persona 298: ✕ on a running-low item moves it to Filtered (kept on the shelf, still counted, not re-added); Filtered is collapsed by default, groups by aisle, selects all/individual and puts back on the shelf (v3.10.1197). Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()"); ev("localStorage.setItem('mh_shop_pane','both')")
    ev("window.mhShopIsShut=()=>false")
    for n in ['Zzqx Mince', 'Zzqx Jam']:
        ev(f"mhStockTrack('{n}',{{base:'g',shop:'Asda'}}); mhStockSetLevel(mhShopKey('{n}'),0); mhStockSetReorder(mhShopKey('{n}'),400)")
    ev("mhStockSweep()"); ev("switchTabById('shop')"); page.wait_for_timeout(500); ev("mhShopRender()")
    k = ev("mhShopKey('Zzqx Mince')")
    if not ev("mhShopLoad().items.some(i=>i.key==='%s')" % k): f.add('BUG', 'the low food is on the list to begin with')
    if page.locator('#mhShopHeld').count(): f.add('BUG', 'no Filtered section until something is filtered')
    page.click('[data-item="Zzqx Mince"] [data-rm]'); page.wait_for_timeout(500)
    if ev("mhShopLoad().items.some(i=>i.key==='%s')" % k): f.add('BUG', 'the ✕ takes it off the list')
    if not ev("!!mhStockLoad().items['%s']" % k): f.add('BUG', 'it stays on the shelf')
    if ev("mhStockLoad().items['%s'].level" % k) != 0: f.add('BUG', 'its count is untouched')
    ev("mhStockSweep(); mhShopRender()")
    if ev("mhShopLoad().items.some(i=>i.key==='%s')" % k): f.add('BUG', 'the sweep does not bring it back while filtered')
    if '(1)' not in ev("document.getElementById('mhShopHeld')?.innerText||''"): f.add('BUG', 'Filtered (1) shows')
    if page.locator('#mhShopHeld [data-held]').count(): f.add('BUG', 'Filtered is collapsed by default')
    page.click('#mhShopHeld span'); page.wait_for_timeout(300)
    if not page.locator('#mhShopHeld [data-held="Zzqx Mince"]').count(): f.add('BUG', 'opened, the food is listed')
    if not page.locator('#mhShopHeld [data-heldsec]').count(): f.add('BUG', 'grouped by aisle')
    # second food: filter it too, then select all and put both back
    page.click('[data-item="Zzqx Jam"] [data-rm]'); page.wait_for_timeout(400)
    if not page.locator('#mhShopHeld [data-held]').count(): page.click('#mhShopHeld span'); page.wait_for_timeout(300)
    page.click('[data-heldall]'); page.wait_for_timeout(300)
    if ev("Object.keys(_shopUi.heldSel||{}).length") != 2: f.add('BUG', 'Select all ticks both')
    page.click('[data-heldall]'); page.wait_for_timeout(300)
    if ev("Object.keys(_shopUi.heldSel||{}).length") != 0: f.add('BUG', 'Deselect all clears')
    page.click('#mhShopHeld [data-held="Zzqx Jam"]'); page.wait_for_timeout(300); page.click('[data-heldrelease]'); page.wait_for_timeout(500)
    if ev("!!mhStockLoad().items['%s'].held" % ev("mhShopKey('Zzqx Jam')")): f.add('BUG', 'put back clears the filter')
    if not ev("mhShopLoad().items.some(i=>i.key==='%s')" % ev("mhShopKey('Zzqx Jam')")): f.add('BUG', 'a put-back food that is still low is back on the list')
    if not ev("!!mhStockLoad().items['%s'].held" % k): f.add('BUG', 'the one not ticked stays filtered')
    # an ordinary typed item is just removed, not filtered
    ev("const s=mhShopLoad(); mhShopSetAdd(s,'Zzqx Typed','own'); mhShopSave(s); mhShopRender()"); page.wait_for_timeout(300)
    page.click('[data-item="Zzqx Typed"] [data-rm]'); page.wait_for_timeout(400)
    if ev("mhShopHeldFoods().length") != 1: f.add('BUG', 'a typed item is not filtered')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
