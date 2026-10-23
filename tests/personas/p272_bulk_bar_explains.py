"""Persona 272: the Add foods bar says what it will do (v3.10.1167). Pete could not tell what the bar's buttons meant or which shop a tick-all would use. The bar now names the count and
the shop, has a Bought at picker, and explains both buttons. Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("""(()=>{const s=mhShopLoad(); if(!s.shops.includes('Heylo')) s.shops.push('Heylo'); mhShopSave(s); ['Zzqx Flatbread','Zzqx Crackers'].forEach(n=>mhStockTrack(n,{base:'g',shop:'Heylo'}));})()""")
    ev("switchTabById('shop')"); ev("mhSlOpen()"); page.wait_for_timeout(500)
    page.click('[data-slshop="Heylo"]'); page.wait_for_timeout(300)
    page.click('button:has-text("Tick all shown")'); page.wait_for_timeout(300)
    t = page.inner_text('#mhSlBarMsg')
    n = ev("Object.keys(mhSlState().sel).length")
    if str(n) not in t or 'Heylo' not in t: f.add('BUG', f'the bar names the count and the shop: {t!r}')
    if 'stock' not in t or 'shopping list' not in t: f.add('BUG', 'the bar explains both buttons')
    ev("document.getElementById('mhSlBulkMore').open=true"); page.wait_for_timeout(200)
    if page.input_value('#mhSlBulkShop') != 'Heylo': f.add('BUG', 'the Bought at picker shows Heylo')
    other = ev("mhShopLoad().shops.find(x=>x!=='Heylo')")
    page.select_option('#mhSlBulkShop', other); page.wait_for_timeout(400)
    if ev("mhSlShop()") != other or n != ev("Object.keys(mhSlState().sel).length"): f.add('BUG', 'changing the shop in the bar keeps the ticks')
    if other not in page.inner_text('#mhSlBarMsg'): f.add('BUG', 'the bar text follows the shop')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
