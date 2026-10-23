"""Persona 294: a food on the list as 'running low' comes off when its count is corrected above the reorder level, even for entries already stuck there; ticked ones stay; it returns when low again (v3.10.1193). Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    on = lambda n: ev("(n)=>mhShopLoad().items.filter(i=>i.key===mhShopKey(n)).map(i=>i.from)", n)
    ev("['Zzqx Rice','Zzqx Oats','Zzqx Tea'].forEach(n=>{mhStockTrack(n,{base:'g'}); const k=mhShopKey(n); mhStockSetReorder(k,50); mhStockSetLevel(k,0);}); mhStockSweep()")
    if on('Zzqx Rice') != ['running low']: f.add('BUG', 'setup: a food at 0 goes on the list')
    ev("mhStockSetLevel(mhShopKey('Zzqx Rice'),200); mhStockSweep()")
    if on('Zzqx Rice'): f.add('BUG', f'corrected above reorder, it comes off the list: {on("Zzqx Rice")}')
    # ticked into the basket: left alone
    ev("const s=mhShopLoad(); s.items.find(i=>i.key===mhShopKey('Zzqx Oats')).checked=true; mhShopSave(s); mhStockSetLevel(mhShopKey('Zzqx Oats'),200); mhStockSweep()")
    if not on('Zzqx Oats'): f.add('BUG', 'a ticked item in the basket stays')
    # data already stuck on the list is cleared when the screen draws
    ev("mhStockSetLevel(mhShopKey('Zzqx Tea'),200)")
    ev("const s=mhShopLoad(); if(!s.items.some(i=>i.key===mhShopKey('Zzqx Tea'))){mhShopSetAdd(s,'Zzqx Tea','stock','running low',null);} mhShopSave(s)")
    ev("switchTabById('shop')"); page.wait_for_timeout(500)
    if on('Zzqx Tea'): f.add('BUG', 'an entry already stuck on the list is cleared when the shopping screen draws')
    # low again -> back
    ev("mhStockSetLevel(mhShopKey('Zzqx Rice'),10); mhStockSweep()")
    if on('Zzqx Rice') != ['running low']: f.add('BUG', 'a food that drops low again comes back')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
