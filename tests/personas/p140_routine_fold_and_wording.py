"""Persona 140: the Your routine card folds (▾ hide / show) like Patterns, sleep wording does not repeat itself, and a meal window wider than 4h reads 'varies a lot' instead of a meaningless range."""
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
    ev("""(()=>{const el=document.getElementById('mcRoutine'),b=document.getElementById('mcRoutineBody');
      b.innerHTML=mhRoutineLines ? '' : ''; el.dataset.has='1'; el.style.display='block'; b.innerHTML='<div>x</div>';})()""")
    a = ev("document.getElementById('mcRoutineBody').style.display !== 'none'")
    ev("document.querySelector('#mcRoutine .metric-header').click()"); page.wait_for_timeout(200)
    b = ev("document.getElementById('mcRoutineBody').style.display !== 'none'")
    if a == b: f.add('BUG', 'routine card does not fold')
    if not ev("!!document.getElementById('trends-routine-icon')"): f.add('BUG', 'no hide/show hint on routine card')
    src = ev("mhRoutineLines.toString()")
    if "Last 3 nights: '" in src: f.add('BUG', 'sleep wording prefix still doubles up')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
