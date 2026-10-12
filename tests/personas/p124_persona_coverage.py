"""Persona 124: every starter pack has a demo persona whose story matches it, and each new persona starts cleanly with its own symptoms and no page errors."""
import sys, json, os; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
NEW = ['gareth','mick','chloe','eileen','dawn','josh','zara','marion','colin','ellie','dev']
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev = page.evaluate
    ids = ev("DEMO_PERSONAS.map(p=>p.id)")
    if len(ids) != len(set(ids)): f.add('BUG', 'duplicate persona ids')
    if len(ids) < 28: f.add('BUG', f'only {len(ids)} demo personas for 27 starter packs')
    for i in NEW:
        if i not in ids: f.add('BUG', f'missing persona {i}')
    icons = ev("DEMO_PERSONA_ICONS")
    for i in ids:
        if i not in icons: f.add('BUG', f'no icon for {i}')
    for i in NEW:
        if i not in ids: continue
        ev(f"startDemoMode('{i}')"); page.wait_for_timeout(1800)
        defs = ev("JSON.parse(localStorage.getItem('mh_symptom_defs')||'[]').map(s=>s.name)")
        want = ev(f"DEMO_PERSONAS.find(p=>p.id==='{i}').symptomDefs")
        if not all(w in defs for w in want): f.add('BUG', f'{i}: symptoms not loaded {defs[:6]}')
        if len(page.inner_text('body')) < 500: f.add('BUG', f'{i}: empty screen')
        ev("exitDemoMode()"); page.wait_for_timeout(1500)
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
