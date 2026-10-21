"""Persona 240: a line switched to Non-nutritional by hand is not left behind on a receipt import (v3.10.1134). Pete marked about 20 lines non-nutritional and they never reached
the cupboards: a line with no amount (or a weight/volume) stayed unticked and Tick all skipped it. Now it counts in items like an auto-spotted one, is ticked, and a
"Tick non-nutritional only" button exists. List imports keep free-text amounts. Invented data only."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("mhShopOpen()"); ev("mhOrdOpen('receipt')"); page.wait_for_timeout(200)
    page.fill('#mhOrdText', "ASDA\nSCOURING PADS 3.00\nMYSTERY SOAP 500G 1.00\nCHEDDAR 400G 2.50\n"); page.click('#mhOrdRead'); page.wait_for_timeout(400)
    ev("_shopUi.ord.rows.forEach((r,i)=>{ if(r.name.indexOf('CHEDDAR')<0) mhOrdKindSet(i,'nonfood'); })"); page.wait_for_timeout(200)
    rows = ev("_shopUi.ord.rows.map(r=>[r.name,r.kind,r.amount,r.on])")
    for r in rows:
        if r[1] == 'nonfood' and (r[2] != '1' or r[3] is not True): f.add('BUG', f'1: a hand-marked non-food line counts in items and is ticked: {r}')
    if not ev("!!document.querySelector('button')") : pass
    if 'Tick non-nutritional only' not in ev("document.getElementById('mhShopPane').innerText"): f.add('BUG', '2: a Tick non-nutritional only button is offered')
    ev("mhOrdAll(false)"); ev("mhOrdOnlyKind('nonfood')")
    on = ev("_shopUi.ord.rows.map(r=>[r.kind,r.on])")
    if on != [['nonfood', True], ['nonfood', True], ['food', False]]: f.add('BUG', f'3: only the non-food lines are ticked: {on}')
    ev("mhOrdApply()"); page.wait_for_timeout(400)
    st = ev("Object.values(mhStockLoad().items).map(i=>[i.name,!!i.nonFood])")
    if sorted(n for n, nf in st if nf) != ['Mystery Soap (Asda)', 'Scouring Pads (Asda)'] or any(n.startswith('Cheddar') for n, nf in st): f.add('BUG', f'4: both reach the cupboards as non-food and the cheddar is untouched: {st}')
    # a list import keeps a free-text amount
    ev("mhOrdOpen('list')"); page.wait_for_timeout(200); page.fill('#mhOrdText', "Zzqx Gadget\n"); page.click('#mhOrdRead'); page.wait_for_timeout(300)
    ev("mhOrdSet(0,'amount','2 bottles'); mhOrdKindSet(0,'nonfood')")
    if ev("_shopUi.ord.rows[0].amount") != '2 bottles': f.add('BUG', '5: a list import keeps free-text amounts')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
