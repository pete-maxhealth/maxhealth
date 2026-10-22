"""Persona 252: the Logged card says how much is left in the cupboard (v3.10.1148). Pete asked where the 'what's left' figure from stock was after logging Asda double cream.
Only items that really came off stock get a line; nothing is shown with stock off, for a food not in the cupboards, or one left alone. Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    def setup():
        ev("localStorage.removeItem(MH_STOCK_KEY); mhStockTrack('Zzqx Cream (Asda)',{base:'g'}); mhStockSetLevel(mhShopKey('Zzqx Cream (Asda)'),2000); mhStockSetReorder(mhShopKey('Zzqx Cream (Asda)'),300)")
    def log(name, amt):
        ev("([n,a])=>logFoods([{name:n,amount:a,kcal:100,protein:1,fat:10,carbs:1}],'t')", [name, amt]); page.wait_for_timeout(250)
    def lines(): return page.locator('.mh-stock-left').all_inner_texts()
    setup(); log('Zzqx Cream', '500g')
    t = ' '.join(lines())
    if 'Stock left' not in t or '1500' not in t.replace(',', '').replace(' ', ''): f.add('BUG', f'1: card shows what is left after logging (brand-matched): {t!r}')
    n = len(lines()); log('Zzqx Cream', '1300g')
    t = lines()[-1] if len(lines()) > n else ''
    if 'running low' not in t: f.add('BUG', f'2: at or under the reorder level it says running low: {t!r}')
    n = len(lines()); log('Zzqx Mystery Food', '100g')
    if len(lines()) != n: f.add('BUG', '3: a food not in the cupboards gets no stock line')
    ev("(()=>{const o=mhStockLoad(); o.enabled=false; mhStockSave(o);})()"); n = len(lines()); log('Zzqx Cream', '10g')
    if len(lines()) != n: f.add('BUG', '4: with stock off there is no stock line')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
