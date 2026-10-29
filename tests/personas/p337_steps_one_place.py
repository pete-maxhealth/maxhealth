"""Persona 337 (v3.10.1239): Steps is one box (typed total + 'includes your logged walk' note); exercise is entered in Exercise today only;
the old steps calculator is gone (What if covers it, incl. a Steps chip that Log it adds to the day total)."""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
bad = []
def check(n, ok, info=''):
    print(('PASS ' if ok else 'FAIL ') + n + (f'  {info}' if info and not ok else ''))
    if not ok: bad.append(n)
with fresh_server() as root, sync_playwright() as pw:
    br = pw.chromium.launch(); ctx = br.new_context(viewport={'width': 430, 'height': 900}, service_workers='block'); page = ctx.new_page()
    errs = []; page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.dismiss())
    page.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); page.evaluate("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev = page.evaluate
    ev("startDemoMode('alex')"); page.wait_for_timeout(2200)
    ev("switchTabById('move')"); page.wait_for_timeout(500)
    check('old calculator removed', ev("!document.getElementById('stepsCalc') && typeof mhStepsCalcN==='undefined'"))
    page.fill('#dailyStepsInput', '5000'); page.keyboard.press('Tab'); page.wait_for_timeout(300)
    check('typed total saved', ev("parseInt(localStorage.getItem('mh_steps_today'))")==5000)
    check('Steps box says what it is', 'steps so far today' in ev("document.getElementById('dailyStepsCard').innerText"))
    # What if with the Steps chip
    page.click('#whatIf >> text=Steps'); page.wait_for_timeout(200)
    page.fill('#wiInput', '3000'); page.wait_for_timeout(300)
    out = ev("document.getElementById('wiOut').innerText")
    check('steps what-if shows an outcome', 'kcal' in out or 'no extra' in out.lower(), out)
    check('what-if leaves the typed total alone', ev("parseInt(localStorage.getItem('mh_steps_today'))")==5000)
    base = ev("mhStepsTodayTotal()")
    ev("mhWiLog()"); page.wait_for_timeout(400)
    check('Log it adds the steps to the day total', ev("parseInt(localStorage.getItem('mh_steps_today'))")==base+3000, f"base {base}")
    check('no JS errors', not errs, str(errs))
print('FAILED: ' + ', '.join(bad) if bad else 'ALL PASS'); sys.exit(1 if bad else 0)
