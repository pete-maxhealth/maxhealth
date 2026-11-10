"""Persona 444 (v3.10.1346): pressing Add on a receipt import that stays on the review (a row skipped, some left waiting) now shows its message where you are (toast + scrolled into view), and pressing it again never counts a done row twice. Invented data only."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 700}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("mhShopOpen()"); ev("mhOrdOpen('receipt')"); page.wait_for_timeout(200)
    page.fill('#mhOrdText', "Cheddar 400g\n2.00\nPlain Rice 1kg\n1.00\nOat Milk 1l\n1.20\n"); page.click('#mhOrdRead'); page.wait_for_timeout(400)
    ev("mhShopRender()")
    rows = ev("_shopUi.ord.rows.map(r=>r.track)")
    lvl = lambda n: ev("n=>{const e=Object.entries(mhStockLoad().items).find(([k])=>k.startsWith(n.toLowerCase())); return e ? e[1].level : null}", n)
    ev("mhOrdSet(0,'amount','400 g'); mhOrdSet(1,'amount','1000 g'); mhOrdSet(2,'amount',''); mhShopRender()"); page.wait_for_timeout(200)
    page.evaluate("document.querySelector('#mhOrdGo').scrollIntoView()"); page.click('#mhOrdGo'); page.wait_for_timeout(900)
    if not ev("!!document.getElementById('mhShopMsg')"): f.add('BUG', '1: no message after a partial add')
    if not ev("(()=>{const e=document.getElementById('mhShopMsg'); if(!e) return false; const r=e.getBoundingClientRect(); return r.bottom>0 && r.top<innerHeight})()"): f.add('BUG', '2: the message is not in view')
    if lvl(rows[0]) != 400 or lvl(rows[1]) != 1000: f.add('BUG', f'3: the two good rows are added: {lvl(rows[0])} {lvl(rows[1])}')
    page.evaluate("document.querySelector('#mhOrdGo').scrollIntoView()"); page.click('#mhOrdGo'); page.wait_for_timeout(700)
    if lvl(rows[0]) != 400 or lvl(rows[1]) != 1000: f.add('BUG', f'4: a second press counted twice: {lvl(rows[0])} {lvl(rows[1])}')
    if not ev("!!document.getElementById('mhShopMsg')"): f.add('BUG', '5: no message on the second press')
    if errs: f.add('BUG', f'errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
