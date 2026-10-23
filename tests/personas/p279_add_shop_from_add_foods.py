"""Persona 279: the Add foods screen has a + Shop button that adds a shop and selects it (v3.10.1176). Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("switchTabById('shop')"); ev("mhSlOpen()"); page.wait_for_timeout(400)
    if not page.locator('#mhSlShops [data-slshop-add]').count(): f.add('BUG', 'a + Shop button is on the Add foods screen')
    page.click('#mhSlShops [data-slshop-add]'); page.wait_for_timeout(400)
    page.fill('#appPromptInput', 'Zzqx Butchers')
    page.click('#appModalConfirm'); page.wait_for_timeout(500)
    if 'Zzqx Butchers' not in ev("mhShopLoad().shops"): f.add('BUG', 'the shop is added')
    if ev("mhSlShop()") != 'Zzqx Butchers': f.add('BUG', 'and chosen for what you add next')
    if not page.locator('#mhSlShops [data-slshop="Zzqx Butchers"]').count(): f.add('BUG', 'and shown as a chip')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
