"""Persona 141: the "▾ hide" fold hint is never capitalised, whichever header style a section uses (Wellness Balance, Import labels, section titles)."""
import sys; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev = page.evaluate
    for hid in ('trends-wellness-icon', 'trends-patterns-icon', 'imp-restore-icon', 'imp-combined-icon'):
        tt = ev(f"(()=>{{const e=document.getElementById('{hid}'); return e ? getComputedStyle(e).textTransform : 'missing'}})()")
        if tt not in ('none',): f.add('BUG', f'{hid} text-transform is {tt}')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
