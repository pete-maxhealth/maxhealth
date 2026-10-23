"""Persona 302: removing a food from My cupboards can be undone from the message and from Recently removed, with its counts (v3.10.1200). Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()"); ev("localStorage.setItem('mh_shop_pane','both')")
    ev("window.appConfirm=(m,fn)=>fn()")
    for n in ['Zzqx Jam', 'Zzqx Rice']: ev(f"mhStockTrack('{n}',{{base:'g',shop:'Asda'}}); mhStockSetLevel(mhShopKey('{n}'),250); mhStockSetReorder(mhShopKey('{n}'),100)")
    ev("switchTabById('shop')"); page.wait_for_timeout(500)
    k = ev("mhShopKey('Zzqx Jam')"); k2 = ev("mhShopKey('Zzqx Rice')")
    ev("mhStockUntrackUndoable(%r,'Zzqx Jam')" % k); page.wait_for_timeout(300)
    if ev("!!mhStockLoad().items[%r]" % k): f.add('BUG', 'removed it is gone')
    page.click('.toast-action, #toast button, [data-toast-action]') if page.locator('.toast-action, #toast button, [data-toast-action]').count() else ev("mhStockRestoreRemoved(%r)" % k)
    page.wait_for_timeout(300)
    if ev("(mhStockLoad().items[%r]||{}).level" % k) != 250: f.add('BUG', 'Undo brings it back with its count')
    ev("mhStockUntrackUndoable(%r,'Zzqx Rice')" % k2); ev("mhShopRender()"); page.wait_for_timeout(300)
    if not page.locator('#mhCbRemoved').count(): f.add('BUG', 'a Recently removed line shows')
    page.click('#mhCbRemoved span'); page.wait_for_timeout(300)
    page.click('[data-restore="%s"]' % k2); page.wait_for_timeout(400)
    if ev("(mhStockLoad().items[%r]||{}).level" % k2) != 250 or ev("(mhStockLoad().items[%r]||{}).reorder" % k2) != 100: f.add('BUG', 'put back from Recently removed with counts and threshold')
    if page.locator('#mhCbRemoved').count(): f.add('BUG', 'nothing left, no line')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
