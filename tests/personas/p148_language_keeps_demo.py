"""Persona 148: changing language inside demo mode keeps you in the same demo persona, and your real data is restored on exit."""
import sys; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    ev = page.evaluate
    ev("state.onboarded=true; saveState(); localStorage.setItem('mh_name','Pete'); localStorage.setItem('mh_tdee','3400')")
    page.reload(); page.wait_for_timeout(1500)
    ev("startDemoMode('doris')"); page.wait_for_timeout(1000)
    ev("mhLangSet('es')"); page.wait_for_timeout(3500)
    if not ev("_demoMode"): f.add('BUG', 'demo mode ended after a language change')
    if ev("document.getElementById('demoBanner').style.display") != 'block': f.add('BUG', 'demo banner not showing after language change')
    if ev("localStorage.getItem('mh_name')") != 'Doris': f.add('BUG', 'persona not active after language change')
    if ev("localStorage.getItem('mh_tdee')") == '3400': f.add('BUG', 'real TDEE visible after language change in demo')
    ev("exitDemoMode()"); page.wait_for_timeout(500)
    if ev("localStorage.getItem('mh_name')") != 'Pete' or ev("localStorage.getItem('mh_tdee')") != '3400': f.add('BUG', 'real values not restored after exit')
    page.reload(); page.wait_for_timeout(2500)
    if ev("_demoMode"): f.add('BUG', 'demo resumed after exit and reload')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
