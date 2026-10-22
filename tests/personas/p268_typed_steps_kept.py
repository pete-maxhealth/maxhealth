"""Persona 268: a typed daily step total is kept (v3.10.1161). Typing 10k stays in the box and survives a refresh; a synced figure LOWER than it (a watch that has
only counted 3k so far) does not wipe it; a synced figure equal or higher retires it, as the box promises. Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("switchSubTab('today','move',document.getElementById('todaytab-move'))"); page.wait_for_timeout(300)
    page.fill('#dailyStepsInput', '10k'); page.press('#dailyStepsInput', 'Tab'); page.wait_for_timeout(400)
    box = lambda: ev("document.getElementById('dailyStepsInput').value"); st = lambda: ev("localStorage.getItem('mh_steps_today')")
    if (box(), st()) != ('10000', '10000'): f.add('BUG', f'10k is kept: {box()} {st()}')
    ev("mhStepsRetireTyped(3000)"); ev("updateDashboard(true)")
    if (box(), st()) != ('10000', '10000'): f.add('BUG', f'a synced 3,000 must not wipe a typed 10,000: {box()} {st()}')
    ev("mhStepsRetireTyped(10000)")
    if st(): f.add('BUG', 'a synced figure equal to what you typed retires it')
    ev("localStorage.setItem('mh_steps_today','4000'); mhStepsRetireTyped(9000)")
    if st(): f.add('BUG', 'a higher synced figure retires it')
    ev("localStorage.removeItem('mh_steps_today')")
    if ev("mhStepsRetireTyped(500)") is not True: f.add('BUG', 'nothing typed: nothing to keep')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
