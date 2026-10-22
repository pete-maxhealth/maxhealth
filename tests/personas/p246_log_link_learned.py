"""Persona 246: a logged food that matches no cupboard item by name but has one clear candidate is offered once, and the answer is remembered (v3.10.1141).
Pete: "the whole purpose of this is that it will match". Invented data."""
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
    def log(name, amt): ev("mhStockOnLog({id:Date.now()+Math.floor(Math.random()*1e6),items:[{name:%r,amount:%r}]}, todayStr())" % (name, amt)); page.wait_for_timeout(700)
    yes = 'button:has-text("Yes, that one")'
    setup('ASDA Fresh Double Cream'); log('Double Cream', '1000 ml')
    if not page.locator(yes).count(): f.add('BUG', '1: a clear candidate is offered')
    else:
        page.click(yes); page.wait_for_timeout(400)
        if level('ASDA Fresh Double Cream') != 1000: f.add('BUG', f'2: yes takes it off: {level("ASDA Fresh Double Cream")}')
        log('Double Cream', '300 ml')
        if page.locator(yes).count(): f.add('BUG', '3: the answer is remembered, no second question')
        if level('ASDA Fresh Double Cream') != 700: f.add('BUG', f'4: the next log matches by itself: {level("ASDA Fresh Double Cream")}')
    # no: nothing taken, never asked again
    setup('ASDA Fresh Double Cream'); ev("(()=>{const o=mhStockLoad(); delete o.alias; mhStockSave(o);})()"); log('Double Cream', '1000 ml')
    if page.locator(yes).count(): page.click('.app-modal-btn.cancel'); page.wait_for_timeout(300)
    if level('ASDA Fresh Double Cream') != 2000: f.add('BUG', '5: no leaves stock alone')
    log('Double Cream', '1000 ml')
    if page.locator(yes).count(): f.add('BUG', '6: a no is not asked again')
    # two candidates: never guess, no question
    setup('ASDA Fresh Double Cream', 'Double Cream Whipping'); log('Double Cream', '1000 ml')
    if page.locator(yes).count() or level('ASDA Fresh Double Cream') != 2000: f.add('BUG', '7: two candidates are not guessed between')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
