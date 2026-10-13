"""Persona 145: Barry (neutral PEMF user) has Bill's treatment story but none of the PEMFiT branding."""
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
    if not ev("DEMO_PERSONAS.some(p=>p.id==='barry')"): f.add('BUG', 'Barry persona missing')
    ev("startDemoMode('barry')"); page.wait_for_timeout(1500)
    if ev("localStorage.getItem('mh_org_logo')"): f.add('BUG', 'org logo set for neutral persona')
    if 'pemfit' in (ev("localStorage.getItem('mh_org_name')") or '').lower(): f.add('BUG', 'PEMFiT org name set')
    if ev("(document.body.innerText.match(/PEMFiT/gi)||[]).length") > 0: f.add('BUG', 'PEMFiT text present in the page during Barry demo')
    if ev("loadTreatmentDefs().filter(t=>t.name==='PEMF Session').length") != 1: f.add('BUG', 'PEMF Session treatment missing')
    if ev("loadSymptomDefs().length") != 3: f.add('BUG', 'symptom defs wrong')
    ev("exitDemoMode()")
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
