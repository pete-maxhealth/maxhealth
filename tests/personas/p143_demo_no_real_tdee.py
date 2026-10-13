"""Persona 143: demo mode never shows the real account's TDEE/carb ceiling, and exit restores them."""
import sys; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    ev = page.evaluate
    ev("state.onboarded=true; saveState(); localStorage.setItem('mh_tdee','3400'); localStorage.setItem('mh_tdee_confirmed_date','2026-10-01'); localStorage.setItem('mh_ceil_standard','30'); localStorage.setItem('mh_target_fat','281')")
    page.reload(); page.wait_for_timeout(1500)
    ev("startDemoMode('zara')"); page.wait_for_timeout(800)
    t = int(ev("localStorage.getItem('mh_tdee')"))
    if t == 3400 or not (1700 <= t <= 2600): f.add('BUG', f'zara demo TDEE unrealistic/leaked: {t}')
    if ev("localStorage.getItem('mh_ceil_standard')") != '110': f.add('BUG', 'demo carb ceiling is not the persona target')
    fat = int(ev("localStorage.getItem('mh_target_fat')"))
    if not (80 <= fat <= 120): f.add('BUG', f'demo fat target leaked/unrealistic: {fat}')
    ev("renderSuggestedTargets()")
    txt = ev("document.getElementById('suggestedTargetsContent').textContent")
    if '3400' in txt: f.add('BUG', 'real TDEE visible in Suggested Targets during demo')
    ev("exitDemoMode()"); page.wait_for_timeout(500)
    if ev("localStorage.getItem('mh_tdee')") != '3400': f.add('BUG', 'exit did not restore real TDEE')
    if ev("localStorage.getItem('mh_tdee_confirmed_date')") != '2026-10-01': f.add('BUG', 'exit did not restore confirmed date')
    if ev("localStorage.getItem('mh_ceil_standard')") != '30': f.add('BUG', 'exit did not restore carb ceiling')
    if ev("localStorage.getItem('mh_target_fat')") != '281': f.add('BUG', 'exit did not restore fat target')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
