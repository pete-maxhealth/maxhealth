"""Persona 106: occasion tags. 'Treatment: <own treatment>' chips come from the user's own list (any condition), toggle on/off, a free-text 'Treatment: Massage' works,
and the same tag is not shown twice (Active tags + pinned strip) when the picker is open."""
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
    ev("renderOccasionTags()")
    if ev("document.querySelectorAll('.mh-treat-chip').length") != 0 and not ev("loadTreatmentDefs().length"): f.add('BUG', 'chips with no treatments')
    ev("localStorage.setItem('mh_treatment_defs', JSON.stringify([{id:'t1',name:'Massage',active:true},{id:'t2',name:'Old',active:false}]))")
    names = ev("loadTreatmentDefs().map(t=>t.name)")
    if 'Massage' not in names: f.add('BUG', f'could not seed treatments {names}')
    else:
        ev("renderOccasionTags()")
        chips = ev("[...document.querySelectorAll('.mh-treat-chip')].map(c=>c.textContent.trim())")
        if not any('Massage' in c for c in chips) or any('Old' in c for c in chips): f.add('BUG', f'chips {chips}')
        ev("document.querySelector('.mh-treat-chip').click()"); page.wait_for_timeout(300)
        if 'Treatment: Massage' not in ev("_getOccasionTags()"): f.add('BUG', 'chip did not add tag')
        if not ev("document.querySelector('.mh-treat-chip').classList.contains('active')"): f.add('BUG', 'chip not active')
        ev("document.querySelector('.mh-treat-chip').click()"); page.wait_for_timeout(300)
        if ev("_getOccasionTags().length"): f.add('BUG', 'chip did not toggle off')
    ev("document.getElementById('customOccasionInput').value='Treatment: Acupuncture'; setCustomOccasion()"); page.wait_for_timeout(300)
    if 'Treatment: Acupuncture' not in ev("_getOccasionTags()"): f.add('BUG', 'free text tag')
    # no duplicate when picker open
    ev("switchTab('today', document.getElementById('maintab-today'))")
    ev("document.getElementById('occasionDisplay').scrollIntoView()")
    cnt = ev("[...document.querySelectorAll('span')].filter(s=>s.offsetParent && /Treatment: Acupuncture/.test(s.textContent) && !s.querySelector('span')).length")
    if cnt > 1: f.add('BUG', f'tag shown {cnt} times')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
