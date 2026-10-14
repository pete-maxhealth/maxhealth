"""Persona 153 (v3.10.1048): a food with 'boiled' in its name is not treated as an oil (the fat plausibility check matched 'oil' inside 'boiled'
and told people a boiled egg's fat 'looks far too low'). Real oils and butter still get the check."""
import sys; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    ev = page.evaluate
    ev("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev("startDemoMode('alex')"); page.wait_for_timeout(2500)
    ev("switchTab('log', document.getElementById('maintab-log'))"); page.wait_for_timeout(600)
    ev("(t)=>{const i=document.getElementById('chatInput'); i.value=t; i.dispatchEvent(new Event('input',{bubbles:true})); sendChat()}", '2 eggs and butter'); page.wait_for_timeout(4500)
    txt = ev("document.getElementById('chatScroll').innerText")
    if 'Egg, boiled' not in txt: f.add('BUG', 'typed 2 eggs did not reach the preview: ' + txt[:700].replace(chr(10), ' / '))
    if 'looks far too low' in txt: f.add('BUG', "boiled egg flagged by the pure-fat check")
    src = open(__file__.rsplit('/tests/',1)[0] + '/maxhealth.html').read()
    if '/oil|butter|cream' in src: f.add('BUG', 'unbounded oil regex is back')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
