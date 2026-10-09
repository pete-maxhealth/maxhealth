"""Persona 69: the TDEE recheck nudge offers a suggested figure with a review-and-confirm step. Nothing changes until the person
confirms; Cancel keeps the old figure; the suggestion moves at most 300 kcal; a trend close to expected gets no button."""
import sys, re; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from datetime import date, timedelta
from playwright.sync_api import sync_playwright
f = Findings()
dmy = lambda n: (date.today() - timedelta(days=n)).strftime('%d/%m/%y')
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("localStorage.setItem('mh_onboarded','1')")
    def setup(weights):
        page.evaluate("""([d, w]) => { localStorage.setItem('mh_tdee','3000'); localStorage.setItem('mh_tdee_confirmed_date', d[20]);
          localStorage.setItem('mh_goal','lose'); localStorage.removeItem('mh_tdee_check_dismissed');
          state.history = w.map((kg,i) => ({date: d[19-i*3], mode:'standard', notes:'', log:[], totals:{kcal:0,protein:0,fat:0,carbs:0}, weight: kg}));
          saveState(); document.getElementById('chatScroll').innerHTML=''; checkTdeeStillAccurate(); }""", [[dmy(n) for n in range(0, 31)], weights])
    # flat weight on a Lose target: expected about -1.3 kg, so TDEE looks too high -> suggest lower, capped at -300
    setup([90.0, 90.0, 90.1, 89.9, 90.0, 90.0, 90.0])
    txt = page.evaluate("document.getElementById('chatScroll').innerText")
    if 'Review a suggested TDEE: 2700kcal' not in txt: f.add('BUG', f'expected a 2700 suggestion (3000 minus the 300 cap), got: {txt[-200:]!r}')
    page.evaluate("document.querySelector('#chatScroll button.confirm-new').click()"); page.wait_for_timeout(300)
    if page.evaluate("localStorage.getItem('mh_tdee')") != '3000': f.add('BUG', 'TDEE changed before the person confirmed')
    page.evaluate("document.getElementById('appModalCancel')?.click()"); page.wait_for_timeout(200)
    if page.evaluate("localStorage.getItem('mh_tdee')") != '3000': f.add('BUG', 'Cancel changed the TDEE')
    page.evaluate("document.querySelector('#chatScroll button.confirm-new').click()"); page.wait_for_timeout(300)
    page.evaluate("document.getElementById('appModalConfirm').click()"); page.wait_for_timeout(300)
    if page.evaluate("localStorage.getItem('mh_tdee')") != '2700': f.add('BUG', 'confirming did not set the suggested TDEE')
    if page.evaluate("localStorage.getItem('mh_tdee_confirmed_date')") != dmy(0): f.add('BUG', 'confirmed date not re-stamped')
    if errs: f.add('BUG', f'page errors: {errs[:2]}')
print('findings', len(f)); sys.exit(1 if f else 0)
