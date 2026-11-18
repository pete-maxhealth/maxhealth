"""Persona 500 (v3.10.1421): on a receipt import the quantity reads "on the receipt" (not "bought", which read as a claim that an unticked item was bought),
a ticked line says nothing extra, an unticked line says it is not added, and says what is already in the cupboards. Invented data."""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept()); page.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("mhStockTrack('Zzqx Cherry Tomatoes',{base:'g',shop:'Asda'}); mhStockSetLevel(mhShopKey('Zzqx Cherry Tomatoes'),415)")
    ev("mhShopOpen()"); ev("mhOrdOpen('receipt')"); page.wait_for_timeout(250)
    ev("t=>mhOrdLoad(t,'a receipt')", 'Zzqx Cherry Tomatoes 300g x2\nZzqx Fine Cut Salad 230g\n'); page.wait_for_timeout(300)
    txt = lambda: ev("document.getElementById('mhShopPane').innerText")
    body = txt()
    import re as _re
    if _re.search(r'· [\d.]+ bought', body): f.add('BUG', 'the word "bought" still sits beside a line quantity')
    if 'on the receipt' not in body: f.add('BUG', 'quantity does not say "on the receipt"')
    if 'ticked to add' not in body: f.add('BUG', 'summary does not say ticked to add')
    ev("mhOrdTick(0, false)"); page.wait_for_timeout(300)
    n = ev("document.querySelectorAll('[data-notadded]').length"); t = ev("document.querySelector('[data-notadded]')?.innerText||''")
    if n != 1: f.add('BUG', f'one unticked line, one "not added" note: {n}')
    if 'not added' not in t: f.add('BUG', f'unticked line says it is not added: {t!r}')
    if ev("mhOrdTick(0, true); mhShopRender(); document.querySelectorAll('[data-notadded]').length"): f.add('BUG', 'a ticked line carries no "not added" note')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
