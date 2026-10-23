"""Persona 276: the Add foods bar has a Both button, keeps ticks after an action, and the Use by date can be cleared (v3.10.1171). Invented data."""
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
    page.click('[data-slshop="Heylo"]'); page.click('button:has-text("Tick all shown")'); page.wait_for_timeout(300)
    if not page.is_visible('#mhSlBulk button:has-text("Both")'): f.add('BUG', 'a Both button is in the bar')
    if page.is_visible('#mhSlBulkStore'): f.add('BUG', 'shop and kept-in are tucked away until asked for')
    page.click('#mhSlBulk button:has-text("Both")'); page.wait_for_timeout(500)
    onlist = ev("mhShopLoad().items.filter(i=>/Zzqx/.test(i.name)).length")
    if onlist != 2: f.add('BUG', f'Both puts the foods on the list: {onlist}')
    if ev("mhSlState().f") != 'gaps': f.add('BUG', 'after adding to cupboards it jumps to Needs details to fill in amounts')
    # Use by can be cleared
    ev("mhStockSetUseBy(mhShopKey('Zzqx Flatbread'), '2026-10-23')")
    ev("mhStockEditView(mhShopKey('Zzqx Flatbread'), 'Zzqx Flatbread')"); page.wait_for_timeout(400)
    page.click('button:has-text("Clear the date")'); page.wait_for_timeout(400)
    if ev("mhStockLoad().items[mhShopKey('Zzqx Flatbread')].useBy"): f.add('BUG', 'Clear the date removes the use-by')
    if page.is_visible('button:has-text("Clear the date")'): f.add('BUG', 'no Clear button once the date is empty')
    page.fill('#mhStkUseBy', '2026-10-23'); page.wait_for_timeout(100); page.dispatch_event('#mhStkUseBy', 'change'); page.wait_for_timeout(400)
    if ev("mhStockLoad().items[mhShopKey('Zzqx Flatbread')].useBy") != '2026-10-23': f.add('BUG', 're-picking the same date after clearing saves it')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
