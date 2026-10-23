"""Persona 283: a food added in My cupboards (as non-nutritional) is shown afterwards: aisle open, scrolled to, other aisles untouched (v3.10.1180). Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("['Chicken Breast','Cheddar','Pasta','Beef Mince','Butter','Frozen Peas','Olive Oil','Basmati Rice','Whole Milk','Eggs'].forEach(n=>{mhStockTrack(n,{base:'g',shop:'Asda'}); mhStockSetLevel(mhShopKey(n),200)})")
    ev("localStorage.setItem('mh_shop_pane','stock'); switchTabById('shop')"); page.wait_for_timeout(500)
    rowsN = "document.querySelectorAll('#stockctlCard [data-stock]').length"
    if ev(rowsN) != 0: f.add('BUG', f'aisles start closed: {ev(rowsN)}')
    # open one aisle by hand: it must stay open
    ev("document.querySelector('#stockctlCard [data-cb-aisle]').click()"); page.wait_for_timeout(300)
    opened = ev(rowsN)
    # add washing up liquid as non-nutritional through Add a food, then Back
    ev("mhShopView('stockadd')"); page.wait_for_timeout(300)
    ev("mhStockAddNonFood('Zzqx Washing up liquid')"); page.wait_for_timeout(400)
    page.click('button:has-text("Back")'); page.wait_for_timeout(800)
    names = ev("[...document.querySelectorAll('#stockctlCard [data-stock]')].map(e=>e.dataset.stock)")
    if 'Zzqx Washing up liquid' not in names: f.add('BUG', f'the added food is on screen after Back: {names}')
    if ev(rowsN) < opened + 1: f.add('BUG', 'the aisle you had open stays open')
    if ev("mhShopPane()") != 'stock': f.add('BUG', 'it shows on the cupboards pane')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
