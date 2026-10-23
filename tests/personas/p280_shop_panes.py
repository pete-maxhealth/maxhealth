"""Persona 280: the Shopping tab has two panes, Shopping list and My cupboards, shown one at a time and remembered (v3.10.1177). Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("mhStockTrack('Zzqx Flatbread',{base:'g',shop:'Asda'}); mhStockSetLevel(mhShopKey('Zzqx Flatbread'),200)")
    ev("switchTabById('shop')"); page.wait_for_timeout(500)
    has = lambda sel: ev("!!document.querySelector('%s')" % sel)
    if not has('#mhShopSwitch'): f.add('BUG', 'a Shopping list / My cupboards switch is at the top')
    if not has('#shoplistCard') or has('#stockctlCard'): f.add('BUG', 'it opens on the Shopping list only')
    page.click('#mhShopSwitch [data-pane="stock"]'); page.wait_for_timeout(300)
    if has('#shoplistCard') or has('#shopaddCard') or not has('#stockctlCard'): f.add('BUG', 'My cupboards shows only the cupboards')
    page.reload(); page.wait_for_timeout(1500); ev("document.getElementById('onboardingOverlay')?.remove()"); ev("switchTabById('shop')"); page.wait_for_timeout(500)
    if not has('#stockctlCard') or has('#shoplistCard'): f.add('BUG', 'the pane you were on is remembered after a reload')
    page.click('#mhShopSwitch [data-pane="list"]'); page.wait_for_timeout(300)
    if not has('#shoplistCard') or has('#stockctlCard'): f.add('BUG', 'and back to the list')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
