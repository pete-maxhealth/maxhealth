"""Persona 110: demo personas for the newer cohorts (Frank hypertension, Linda asthma, Ben MS, Arthur Parkinson's, Helen menopause, Nadia IBS):
each loads, has its symptoms, treatments and day tags, the picker lists them, before/after can anchor on a tag, exit restores real data, no page errors."""
import sys; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("localStorage.setItem('mh_onboarded','1')"); page.reload(); page.wait_for_timeout(1500)
    ev = page.evaluate
    ev("saveSymptomDefs([{id:'real1',name:'Real symptom',active:true}])")
    for pid in ['frank', 'linda', 'ben', 'arthur', 'helen', 'nadia']:
        ev("(id)=>startDemoMode(id)", pid); page.wait_for_timeout(1500)
        names = ev("loadSymptomDefs().map(s=>s.name)")
        if len(names) < 3 or 'Real symptom' in names: f.add('BUG', f'{pid} symptoms {names}')
        if not ev("state.history.length"): f.add('BUG', f'{pid} no history')
        if not ev("mhAnchorDefs().some(d=>d.isTag)"): f.add('BUG', f'{pid} no day tags')
        if pid in ('frank', 'linda', 'ben', 'arthur', 'helen') and not ev("loadTreatmentDefs().length"): f.add('BUG', f'{pid} no treatments')
        if pid == 'ben':
            a = ev("mhAnchorDefs().filter(d=>d.isTag).map(d=>d.id)")
            st = ev("(id)=>computeTreatmentSessionStats(id,'weight',1,'0')", 'tagcat:exercise')
            if st['insufficientData']: f.add('BUG', f'ben exercise anchor insufficient {a}')
        if not ev("document.getElementById('demoBanner').style.display!=='none'"): f.add('BUG', f'{pid} banner')
        ev("exitDemoMode()"); page.wait_for_timeout(800)
        if 'Real symptom' not in ev("loadSymptomDefs().map(s=>s.name)"): f.add('BUG', f'{pid} exit did not restore symptoms')
    ev("showDemoPersonaPicker()")
    t = ev("document.getElementById('demoPersonaOverlay').innerText")
    for n in ['Frank', 'Linda', 'Ben', 'Arthur', 'Helen', 'Nadia']:
        if n not in t: f.add('BUG', f'picker missing {n}')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
