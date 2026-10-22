"""Persona 253: a name typed into the cupboard search that matches nothing can be added as a new food right there (v3.10.1149). Pete wanted "Heylo flatbread"
in his Heylo shop and the search screen was a dead end. A shop named in the text becomes that food's shop. Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("localStorage.removeItem(MH_STOCK_KEY); mhStockTrack('Zzqx Seed',{base:'g'}); (()=>{const s=mhShopLoad(); if(!s.shops.includes('Zzqhey')) s.shops.push('Zzqhey'); mhShopSave(s);})()")
    ev("switchTabById('shop')"); page.wait_for_timeout(300)
    ev("(()=>{const st=mhSlState(); st.q='Zzqhey flatbread'; st.f='all'; mhShopView('stocklist');})()"); page.wait_for_timeout(300)
    if not page.locator('#mhSlNew button').count(): f.add('BUG', '1: a name that matches nothing offers to add it as a new food')
    else:
        page.click('#mhSlNew button'); page.wait_for_timeout(300)
        d = ev("({v:_shopUi.view, n:_shopUi.stk&&_shopUi.stk.name, s:_shopUi.stk&&_shopUi.stk.shop, nw:_shopUi.stk&&_shopUi.stk.isNew})")
        if d['v'] != 'stockedit' or d['n'] != 'Zzqhey flatbread'.capitalize() or not d['nw']: f.add('BUG', f'2: opens the new-food form with the name filled in: {d}')
        if d['s'] != 'Zzqhey': f.add('BUG', f'3: a shop named in the text becomes its shop: {d}')
        ev("mhStkBase('g')"); ev("mhStockFormSave()"); page.wait_for_timeout(300)
        it = ev("mhStockLoad().items[mhShopKey('Zzqhey flatbread')]")
        if not it or it.get('shop') != 'Zzqhey' or it.get('base') != 'g': f.add('BUG', f'4: saved into the cupboards under that shop: {it}')
    ev("(()=>{const st=mhSlState(); st.q='Zzqx Seed'; mhShopView('stocklist');})()"); page.wait_for_timeout(300)
    if page.locator('#mhSlNew button').count(): f.add('BUG', '5: a name that already exists is not offered as new')
    ev("(()=>{const st=mhSlState(); st.q=''; mhShopView('stocklist');})()"); page.wait_for_timeout(300)
    if page.locator('#mhSlNew button').count(): f.add('BUG', '6: an empty search offers nothing')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
