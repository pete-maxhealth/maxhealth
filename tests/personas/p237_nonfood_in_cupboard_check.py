"""Persona 237: non-food stock (toilet roll, bin bags) in Check the cupboards (v3.10.1130). Pete asked where they are. They are labelled Non-nutritional (toilet roll
used to read "Oils & fats"), and a Non-nutritional filter chip shows only them; no chip when there are none. Invented data only."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("mhShopOpen()"); ev("mhShopView('stocklist')"); page.wait_for_timeout(200)
    if 'Non-nutritional' in ev("document.getElementById('mhShopPane').innerText"): f.add('BUG', '1: no Non-nutritional chip when there is no non-food stock')
    ev("mhOrdOpen('receipt')"); page.wait_for_timeout(200)
    page.fill('#mhOrdText', "ASDA\nCHEDDAR 400G 2.50\nTOILET ROLL 9 PACK 4.00\nBIN BAGS 20 PACK 2.00\n"); page.click('#mhOrdRead'); page.wait_for_timeout(400)
    ev("mhOrdAll(true)"); ev("mhOrdApply()"); page.wait_for_timeout(400)
    ev("mhShopView('stocklist')"); page.wait_for_timeout(300)
    t = ev("document.getElementById('mhShopPane').innerText")
    if 'Oils & fats' in t: f.add('BUG', '2: toilet roll is not labelled Oils & fats')
    if t.count('Non-nutritional') < 3: f.add('BUG', f'3: both non-food rows say Non-nutritional and a chip exists: {t.count("Non-nutritional")}')
    ev("mhSlF('nonfood')"); page.wait_for_timeout(200)
    rows = ev("[...document.querySelectorAll('#mhSlRows > *')].map(e=>e.innerText.split('\\n')[0])")
    if len(rows) != 2 or any('Cheddar' in r for r in rows): f.add('BUG', f'4: the chip shows only the non-food rows: {rows}')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
