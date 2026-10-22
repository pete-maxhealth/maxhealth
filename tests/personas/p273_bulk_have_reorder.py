"""Persona 273: the Add foods bar can set Have now and Reorder at for all ticked foods (v3.10.1168). Blank leaves each food as it was. Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("""(()=>{const s=mhShopLoad(); if(!s.shops.includes('Heylo')) s.shops.push('Heylo'); mhShopSave(s); ['Zzqx Flatbread','Zzqx Crackers'].forEach(n=>mhStockTrack(n,{base:'g',shop:'Heylo'}));mhStockSetLevel(mhShopKey('Zzqx Crackers'),50);})()""")
    ev("switchTabById('shop')"); ev("mhSlOpen()"); page.wait_for_timeout(500)
    page.click('[data-slshop="Heylo"]'); page.click('button:has-text("Tick all shown")'); page.wait_for_timeout(300)
    page.fill('#mhSlBulkHave', '240'); page.fill('#mhSlBulkRe', '80')
    page.click('#mhSlBulk button:has-text("Add to my cupboards")'); page.wait_for_timeout(400)
    got = ev("['Zzqx Flatbread','Zzqx Crackers'].map(n=>{const i=mhStockLoad().items[mhShopKey(n)];return [i.level,i.reorder]})")
    if got != [[240, 80], [240, 80]]: f.add('BUG', f'every ticked food gets Have now and Reorder at: {got}')
    # blank keeps
    ev("mhSlOpen()"); page.wait_for_timeout(300); page.click('[data-slshop="Heylo"]'); page.click('button:has-text("Tick all shown")'); page.wait_for_timeout(300)
    page.click('#mhSlBulk button:has-text("Add to my cupboards")'); page.wait_for_timeout(400)
    got = ev("['Zzqx Flatbread','Zzqx Crackers'].map(n=>{const i=mhStockLoad().items[mhShopKey(n)];return [i.level,i.reorder]})")
    if got != [[240, 80], [240, 80]]: f.add('BUG', f'blank boxes leave them as they were: {got}')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
