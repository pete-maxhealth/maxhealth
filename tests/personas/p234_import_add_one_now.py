"""Persona 234: "Add this one now" on an import row (v3.10.1127). One food goes into the cupboards straight away and its row locks as done; the bottom button then adds only
what is left, so nothing is counted twice; a reload in the middle keeps the done rows done; the import is logged once. Invented data only."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("saveLibrary([{id:'l1',name:'Cheddar',kcal:410,protein:25,carbs:0.1,fat:34,portion:'100g'},{id:'l2',name:'Plain Rice',kcal:350,protein:7,carbs:78,fat:1,portion:'100g'},{id:'l3',name:'Oat Milk',kcal:45,protein:1,carbs:6,fat:1.5,portion:'100ml'}])")
    ev("mhShopOpen()"); ev("mhOrdOpen('receipt')"); page.wait_for_timeout(200)
    page.fill('#mhOrdText', "Cheddar 400g\n2.00\nPlain Rice 1kg\n1.00\nOat Milk 1l\n1.20\n"); page.click('#mhOrdRead'); page.wait_for_timeout(400)
    ev("mhShopRender()")
    rows = ev("_shopUi.ord.rows.map(r=>[r.track,r.amount,r.on])")
    lvl = lambda n: ev("n=>{const i=mhStockLoad().items[mhShopKey(n)]; return i ? i.level : null}", n)
    if len(rows) != 3: f.add('BUG', f'0: three lines read: {rows}')
    ev("mhOrdSet(0,'amount','400 g'); mhOrdSet(1,'amount','1000 g'); mhOrdSet(2,'amount','1000 ml'); mhShopRender()"); page.wait_for_timeout(200)
    if not ev("!!document.querySelector('[data-ord=\"0\"] button')") : f.add('BUG', '1: rows have buttons')
    page.click('[data-ord="0"] button:has-text("Add this one now")'); page.wait_for_timeout(400)
    if lvl(rows[0][0]) != 400: f.add('BUG', f'2: the first food is in the cupboards at once: {lvl(rows[0][0])}')
    if lvl(rows[1][0]) is not None: f.add('BUG', f'3: the others are untouched: {lvl(rows[1][0])}')
    if not ev("!!document.querySelector('[data-ord=\"0\"][data-done]')"): f.add('BUG', '4: the added row shows as done')
    page.reload(); page.wait_for_timeout(1500); ev = page.evaluate; ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("mhShopOpen()"); ev("mhOrdOpen('receipt')"); page.wait_for_timeout(300)
    if ev("_shopUi.ord.rows[0].done") is not True: f.add('BUG', '5: done survives a reload')
    ev("mhOrdApply()"); page.wait_for_timeout(400)
    if lvl(rows[0][0]) != 400: f.add('BUG', f'6: the first food is not counted twice: {lvl(rows[0][0])}')
    if lvl(rows[1][0]) != 1000 or lvl(rows[2][0]) != 1000: f.add('BUG', f'7: the rest arrive: {lvl(rows[1][0])} {lvl(rows[2][0])}')
    n = ev("mhStockLoad().imports.length")
    if n != 1: f.add('BUG', f'8: the import is logged once: {n}')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
