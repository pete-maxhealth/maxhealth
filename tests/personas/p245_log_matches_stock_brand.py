"""Persona 245: logging "Double Cream" takes stock off "Double Cream (Asda)" (v3.10.1140). Pete logged 1000 ml of Asda double cream and the cupboard stayed at 2000 ml:
the logged name did not equal the stock name, so nothing was taken and nothing was said. Brand-only differences now match when exactly one item fits. Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    def setup(*names):
        ev("localStorage.removeItem(MH_STOCK_KEY)")
        for n in names: ev("(n=>{mhStockTrack(n,{base:'ml'}); mhStockSetLevel(mhShopKey(n),2000);})(%r)" % n)
    def level(n): return ev("mhStockLoad().items[mhShopKey(%r)].level" % n)
    def log(name, amt): ev("mhStockOnLog({id:Date.now()+Math.floor(Math.random()*1e6),items:[{name:%r,amount:%r}]}, todayStr())" % (name, amt))
    setup('Double Cream (Asda)')
    for nm in ['Double Cream', 'Asda Double Cream', 'Double Cream (Asda)']:
        setup('Double Cream (Asda)'); log(nm, '1000 ml')
        if level('Double Cream (Asda)') != 1000: f.add('BUG', f'1: logging {nm!r} takes 1000 ml off Double Cream (Asda): {level("Double Cream (Asda)")}')
    # two possible products: never guess
    setup('Double Cream (Asda)', 'Double Cream (Tesco)'); log('Double Cream', '1000 ml')
    if level('Double Cream (Asda)') != 2000 or level('Double Cream (Tesco)') != 2000: f.add('BUG', '2: two matching items is ambiguous: nothing is taken')
    # a different food is not matched
    setup('Double Cream (Asda)'); log('Single Cream', '1000 ml')
    if level('Double Cream (Asda)') != 2000: f.add('BUG', '3: a different food does not match')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
