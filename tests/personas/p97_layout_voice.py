"""Persona 97: layout by voice/typing - hide/show a Today card, open/close all, reset - and ordinary questions are never hijacked."""
import sys, re; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("localStorage.setItem('mh_onboarded','1')"); page.reload(); page.wait_for_timeout(1800)
    page.evaluate("document.querySelectorAll('[id*=nboard]').forEach(e=>{ if(e.style) e.style.display='none'; })")
    ev = page.evaluate
    r = ev("[handleLayoutQuery('hide the fasting card'), getDashboardHidden().includes('fasting'), handleLayoutQuery('show the fasting card'), getDashboardHidden().includes('fasting')]")
    if r != [True, True, True, False]: f.add('BUG', f'hide/show by voice {r}')
    r = ev("[handleLayoutQuery('close all cards'), handleLayoutQuery('open all cards')]")
    if r != [True, True]: f.add('BUG', f'open/close all {r}')
    for q in ['show today summary', 'what is my weight', 'show the weather forecast', 'hide the dog card', 'how many eggs have I had this week']:
        if ev(f"handleLayoutQuery({q!r})"): f.add('BUG', f'ordinary text hijacked: {q}')
    if not ev("(processMessage.toString().indexOf('handleLayoutQuery') > 0)"): f.add('BUG', 'not wired into processMessage')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
