"""Persona 247: weight logged against a stock item counted in ml asks once for grams-per-ml, then converts (v3.10.1142).
Pete logged 500 g of Asda double cream (library, per 100 g) against stock counted in ml: "could not read the amount". Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    K = "mhShopKey('Zzqx Cream (Asda)')"
    def setup(base='ml', lvl=1200):
        ev("localStorage.removeItem(MH_STOCK_KEY)"); ev("mhStockTrack('Zzqx Cream (Asda)',{base:%r}); mhStockSetLevel(%s,%d)" % (base, K, lvl))
    def level(): return ev("mhStockLoad().items[%s].level" % K)
    def log(amt): ev("mhStockOnLog({id:Date.now()+Math.floor(Math.random()*1e6),items:[{name:'Zzqx Cream (Asda)',amount:%r}]}, todayStr())" % amt); page.wait_for_timeout(700)
    setup(); log('500g')
    if not page.locator('#appPromptInput').count(): f.add('BUG', '1: weight against an ml item asks for grams per ml')
    else:
        page.fill('#appPromptInput', '1'); page.click('#appModalConfirm'); page.wait_for_timeout(400)
        if level() != 700: f.add('BUG', f'2: 500 g at 1 g/ml takes 500 ml off: {level()}')
        log('100g')
        if page.locator('#appPromptInput').count(): f.add('BUG', '3: remembered, not asked again')
        if level() != 600: f.add('BUG', f'4: next log converts by itself: {level()}')
    # a different density is honoured, and nonsense is refused
    setup(); log('500g'); page.fill('#appPromptInput', '0.5'); page.click('#appModalConfirm'); page.wait_for_timeout(400)
    if level() != 200: f.add('BUG', f'5: 500 g at 0.5 g/ml is 1000 ml: {level()}')
    setup(); log('500g'); page.fill('#appPromptInput', 'abc'); page.click('#appModalConfirm'); page.wait_for_timeout(400)
    if level() != 1200: f.add('BUG', f'6: a non-number leaves stock alone: {level()}')
    setup(); log('500g'); page.fill('#appPromptInput', '50'); page.click('#appModalConfirm'); page.wait_for_timeout(400)
    if level() != 1200: f.add('BUG', f'6b: an impossible density (50 g per ml) leaves stock alone: {level()}')
    # cancel leaves it alone
    setup(); log('500g'); page.click('#appModalCancel'); page.wait_for_timeout(300)
    if level() != 1200: f.add('BUG', '7: cancel leaves stock alone')
    # ml against a gram item the other way round
    setup('g', 1000); log('250ml'); page.fill('#appPromptInput', '2'); page.click('#appModalConfirm'); page.wait_for_timeout(400)
    if level() != 500: f.add('BUG', f'8: 250 ml at 2 g/ml takes 500 g off: {level()}')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
