"""Persona 140: Your routine looks and folds exactly like Patterns (same section title style, ▾ hide hint), sits straight before Patterns, sleep wording does not repeat itself."""
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
    ev("switchTab('insights', document.getElementById('maintab-insights'))"); page.wait_for_timeout(900)
    ev("(()=>{const el=document.getElementById('mcRoutine'); el.dataset.has='1'; el.hidden=false; document.getElementById('mcRoutineBody').innerHTML='<div>x</div>';})()")
    if ev("document.getElementById('title-trends-routine').className") != ev("document.getElementById('title-trends-patterns').className"): f.add('BUG', 'routine title style differs from Patterns')
    a = ev("document.getElementById('trends-routine-wrap').style.display !== 'none'")
    ev("document.getElementById('title-trends-routine').click()"); page.wait_for_timeout(200)
    b = ev("document.getElementById('trends-routine-wrap').style.display !== 'none'")
    if a == b: f.add('BUG', 'routine card does not fold')
    if '▸ show' not in ev("document.getElementById('trends-routine-icon').textContent"): f.add('BUG', 'no show hint when folded')
    if not ev("getGenericOrder('trends').indexOf('trends-routine') + 1 === getGenericOrder('trends').indexOf('trends-patterns')"): f.add('BUG', 'routine not straight before Patterns')
    src = ev("mhRoutineLines.toString()")
    if "Last 3 nights: '" in src: f.add('BUG', 'sleep wording prefix still doubles up')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
