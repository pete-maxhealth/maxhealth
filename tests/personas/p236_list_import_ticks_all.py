"""Persona 236: a "list to shop for" import starts with every line ticked and Tick all ticks them, because a shopping list needs no amount (v3.10.1129).
Pete's phone showed 0 for items added to Asda. Covers: start ticked, button count, Tick all after Untick all, applying puts every line on the Asda list and the Asda chip counts them. Invented data only."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("mhShopOpen()"); ev("mhOrdOpen('list')"); page.wait_for_timeout(200)
    page.fill('#mhOrdText', "Double cream\nBaked beans\nToilet roll\n"); page.click('#mhOrdRead'); page.wait_for_timeout(400)
    ev("mhOrdShop('Asda')"); page.wait_for_timeout(200)
    on = ev("_shopUi.ord.rows.map(r=>r.on)")
    if on != [True, True, True]: f.add('BUG', f'1: every listed line starts ticked: {on}')
    if '3 items' not in ev("document.getElementById('mhOrdGo').textContent"): f.add('BUG', '2: the button counts all three')
    ev("mhOrdAll(false)"); ev("mhOrdAll(true)")
    if ev("_shopUi.ord.rows.map(r=>r.on)") != [True, True, True]: f.add('BUG', '3: Tick all ticks lines that have no amount on a list')
    page.click('#mhOrdGo'); page.wait_for_timeout(500)
    n = ev("mhShopLoad().items.filter(i=>i.shop==='Asda').length")
    if n != 3: f.add('BUG', f'4: all three are on the Asda list: {n}')
    chip = ev("[...document.querySelectorAll('#mhShopChips button')].map(b=>b.textContent.trim())")
    if not any(c.startswith('Asda') and '(3)' in c for c in chip): f.add('BUG', f'5: the Asda chip shows 3: {chip}')
    # a receipt import is unchanged: no amount means not ticked
    ev("mhOrdOpen('receipt')"); page.wait_for_timeout(200); page.fill('#mhOrdText', "Mystery thing\n1.00\n"); page.click('#mhOrdRead'); page.wait_for_timeout(300)
    if ev("_shopUi.ord.rows[0].on") is True and not ev("_shopUi.ord.rows[0].amount"): f.add('BUG', '6: a stock import still needs an amount before a line is ticked')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
