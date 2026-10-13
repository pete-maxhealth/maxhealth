"""Persona 142: Settings > Condition / Protocol explains that it only sets the carb target and report framing, and its link opens Change my focus (the 27 starter packs)."""
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
    row = ev("(()=>{const s=document.getElementById('settingsCondition'); return s ? s.parentElement.textContent : ''})()")
    if '27 starter packs' not in row or 'carb target' not in row: f.add('BUG', 'protocol dropdown has no explanation of how it differs from the packs')
    if ev("document.getElementById('settingsCondition').options.length") != 9: f.add('BUG', 'protocol list is no longer the nine dietary protocols')
    ev("window.__fo=0; window.mhFocusOpen=function(){window.__fo=1}")
    ev("document.querySelector('#settingsCondition').parentElement.querySelector('a').click()")
    if ev("window.__fo") != 1: f.add('BUG', 'link did not call Change my focus')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
