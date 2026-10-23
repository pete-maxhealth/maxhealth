"""Persona 273: the Add foods bar sets Have now and Reorder at for ONE ticked food (v3.10.1171; amounts make no sense across several foods). Blank leaves it as it was. Invented data."""
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
    page.click('[data-slshop="Heylo"]'); page.wait_for_timeout(300)
    page.click('button:has-text("Tick all shown")'); page.wait_for_timeout(300)
    ev("document.getElementById('mhSlBulkMore').open=true")
    if page.is_visible('#mhSlBulkHave'): f.add('BUG', 'amount boxes are hidden while several foods are ticked')
    ev("mhSlPickAll(false)"); page.wait_for_timeout(200)
    ev("mhSlState().sel[mhShopKey('Zzqx Flatbread')]=1; mhSlBulkRefresh()"); page.wait_for_timeout(200)
    ev("document.getElementById('mhSlBulkMore').open=true")
    if not page.is_visible('#mhSlBulkHave'): f.add('BUG', 'amount boxes show for exactly one ticked food')
    page.fill('#mhSlBulkHave', '240'); page.fill('#mhSlBulkRe', '80')
    page.click('#mhSlBulk button:has-text("Add to my cupboards")'); page.wait_for_timeout(400)
    got = ev("['Zzqx Flatbread','Zzqx Crackers'].map(n=>{const i=mhStockLoad().items[mhShopKey(n)];return [i.level,i.reorder]})")
    if got[0] != [240, 80] or got[1][0] != 50: f.add('BUG', f'the one ticked food gets the amounts, the other is untouched: {got}')
    ev("mhSlF('all')"); ev("mhSlState().sel[mhShopKey('Zzqx Flatbread')]=1; mhSlBulkRefresh()"); page.wait_for_timeout(300)
    # blank keeps
    page.click('#mhSlBulk button:has-text("Add to my cupboards")'); page.wait_for_timeout(400)
    got = ev("['Zzqx Flatbread'].map(n=>{const i=mhStockLoad().items[mhShopKey(n)];return [i.level,i.reorder]})")
    if got != [[240, 80]]: f.add('BUG', f'blank boxes leave it as it was: {got}')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
