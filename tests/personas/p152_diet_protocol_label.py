"""Persona 152: Settings row is called 'Diet protocol' (not 'Condition / Protocol') and every language pack translates the new label."""
import sys, json, glob, os; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
for p in sorted(glob.glob(os.path.join(root_dir, 'lang', '*.json'))):
    d = json.load(open(p, encoding='utf-8'))
    if 'Condition / Protocol' in d: f.add('BUG', f'{os.path.basename(p)} still has the old label key')
    if not d.get('Diet protocol'): f.add('BUG', f'{os.path.basename(p)} has no translation for Diet protocol')
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    lab = page.evaluate("document.getElementById('settingsCondition').parentElement.querySelector('.settings-label').textContent.trim()")
    if lab != 'Diet protocol': f.add('BUG', f'label is {lab!r}')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
