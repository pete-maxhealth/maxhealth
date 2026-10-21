"""Persona 241: the shopping list basket has an Untick all (v3.10.1135). Pete could not find one. Invented data."""
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
    ev("mhOrdOpen('list')"); page.wait_for_timeout(200); page.fill('#mhOrdText', "Zzqx Cans\nZzqx Coffee\nZzqx Soap\n"); page.click('#mhOrdRead'); page.wait_for_timeout(300)
    ev("mhOrdShop('Asda')"); page.wait_for_timeout(200); page.click('#mhOrdGo'); page.wait_for_timeout(500)
    ev("(()=>{const s=mhShopLoad(); s.items.forEach(i=>i.checked=true); mhShopSave(s);})()"); ev("_shopUi.basketOpen=true; mhShopRender()"); page.wait_for_timeout(200)
    n = ev("mhShopLoad().items.filter(i=>i.checked).length")
    if n < 1: f.add('BUG', f'setup: items in the basket: {n}')
    if not page.locator('button:has-text("Put everything back")').count(): f.add('BUG', '1: basket offers a Put everything back on the list button')
    else:
        page.click('button:has-text("Put everything back")'); page.wait_for_timeout(200)
        left = ev("mhShopLoad().items.filter(i=>i.checked).length")
        if left != 0: f.add('BUG', f'2: all put back on the list, {left} still ticked')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
