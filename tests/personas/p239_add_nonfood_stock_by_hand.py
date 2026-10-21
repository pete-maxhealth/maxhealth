"""Persona 239: a non-nutritional item can be added to the cupboards by hand (v3.10.1133). Pete found non-food stock only came from receipts. Add a food > type "Washing Powder" >
"Add as non-nutritional": it is tracked, counted in each, flagged non-food, never in the food library; the Non-nutritional chip then appears in My cupboards. Invented data only."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()"); ev("mhShopOpen()")
    nlib = ev("loadLibrary().length")
    import re
    chip = lambda: re.search(r'Non-nutritional \(\d+\)', ev("document.getElementById('mhShopPane').innerText"))
    if chip(): f.add('BUG', '0: no chip before any non-food stock')
    ev("mhShopView('stockadd')"); page.wait_for_timeout(200); page.fill('#mhStockQ', 'Washing Powder'); page.wait_for_timeout(300)
    if not ev("!!document.getElementById('mhStockTypedNonFood')"): f.add('BUG', '1: a non-nutritional option is offered for a typed name')
    else:
        page.click('#mhStockTypedNonFood'); page.wait_for_timeout(400)
        it = ev("mhStockLoad().items[mhShopKey('Washing Powder')]")
        if not it or not it.get('nonFood') or it.get('base') != 'each': f.add('BUG', f'2: tracked as non-food counted in each: {it}')
        if ev("loadLibrary().length") != nlib: f.add('BUG', '3: nothing is added to the food library')
        ev("mhShopView('list')"); page.wait_for_timeout(300)
        if not chip(): f.add('BUG', '4: the Non-nutritional chip appears in My cupboards')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
