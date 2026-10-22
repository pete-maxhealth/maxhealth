"""Persona 249: Shopping complete works even when the browser swallows its pop-ups, and a bought non-nutritional item is not left low (v3.10.1144).
Pete: pressing Shopping complete "isn't doing anything". The native confirm() can be suppressed (it silently answers no); the app's own confirm box cannot. Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.dismiss())   # every native pop-up is refused
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("mhShopOpen()"); page.wait_for_timeout(300)
    K = "mhShopKey('Zzqx Coffee')"
    ev("mhStockAddNonFood('Zzqx Coffee')"); ev("(()=>{const k=%s; mhStockSetLevel(k,1); const o=mhStockLoad(); o.items[k].reorder=1; o.items[k].shop='Asda'; mhStockSave(o); mhStockSweep();})()" % K)
    if ev("mhShopLoad().items.length") != 0: f.add('BUG', '1: a non-nutritional item is never listed by a number, only by the 🛒 button')
    ev("mhStockLowNow(%s)" % K); ev("(()=>{const s=mhShopLoad(); s.items.forEach(i=>i.checked=true); mhShopSave(s);})()"); ev("_shopUi.view='list'; mhShopRender()")
    ev("mhShopComplete()"); page.wait_for_timeout(300)
    if not page.locator('#appModalConfirm').count(): f.add('BUG', '2: Shopping complete shows the app confirm box even though native pop-ups are blocked')
    else:
        if ev("mhShopLoad().items.length") != 1: f.add('BUG', '3: nothing happens until you confirm')
        page.click('#appModalConfirm'); page.wait_for_timeout(400)
        if ev("mhShopLoad().items.length") != 0: f.add('BUG', '4: confirming empties the basket')
        if ev("_shopUi.view") == 'stockbought': f.add('BUG', '5: a non-nutritional item is not sent to the how-much-did-you-buy step')
        if not ev("!!mhStockLoad().items[%s]" % K): f.add('BUG', '6: it stays on the shelf')
    # cancel keeps everything
    ev("mhStockLowNow(%s)" % K); ev("(()=>{const s=mhShopLoad(); s.items.forEach(i=>i.checked=true); mhShopSave(s);})()"); ev("mhShopComplete()"); page.wait_for_timeout(300)
    if page.locator('.app-modal-btn.cancel').count(): page.click('.app-modal-btn.cancel'); page.wait_for_timeout(200)
    if ev("mhShopLoad().items.length") != 1: f.add('BUG', '7: Not yet keeps the basket')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
