"""Persona 455: the Fasting and Fibre cards show only the headline until "?" is tapped (Pete, 12 Nov 2026: "Text everywhere!").
Closed: no sentence-length text is visible in either card (the your-usual line, the range picker, the condition note, the fibre notes all sit behind the ?).
One tap on ? shows them, a second hides them, and a reload keeps the state. Demo persona, invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
VIS = "k=>[...document.querySelectorAll('#dashSection-'+k+' *')].filter(e=>e.offsetParent&&!e.children.length&&e.textContent.trim().length>25&&!e.closest('.mh-ctl')).map(e=>e.textContent.trim().slice(0,50))"
HAS = "k=>{const d=document.getElementById(k+'Detail'); return d&&getComputedStyle(d).display!=='none'}"
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page()
    page.on('pageerror', lambda e: f.add('JS-exception', str(e)[:300])); page.on('dialog', lambda d: d.dismiss())
    ev = page.evaluate
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500); ev("startDemoMode('doris')"); page.wait_for_timeout(2500)
    ev("localStorage.setItem('mh_condition','gbm'); mhRenderFastingCard(); mhFibreRender(); switchTab('today'); switchSubTab('today','dashboard')"); page.wait_for_timeout(600)
    for k in ('fasting', 'fibre'):
        v = ev(VIS, k)
        if v: f.add('BUG', f'1: {k} card shows text while closed: {v}')
        ev(f"mhCardInfo('{k}')"); page.wait_for_timeout(200)
        if not ev(HAS, k): f.add('BUG', f'2: {k}: ? did not open the details')
    shown = ev("document.getElementById('dashSection-fasting').innerText")
    for need in ('Your usual', 'Proven: fasting raises', 'Longer is not better', 'Last 30 days'):
        if need not in shown: f.add('BUG', f'3: fasting details lack "{need}"')
    if 'Nothing logged yet' not in ev("document.getElementById('dashSection-fibre').innerText") and '14-day' not in ev("document.getElementById('dashSection-fibre').innerText"): f.add('BUG', '3b: fibre details empty')
    page.reload(); page.wait_for_timeout(2500); ev("switchTab('today'); switchSubTab('today','dashboard')"); page.wait_for_timeout(500)
    if not ev(HAS, 'fasting'): f.add('BUG', '4: open state lost on reload')
    for k in ('fasting', 'fibre'):
        ev(f"mhCardInfo('{k}')"); page.wait_for_timeout(150)
        if ev(HAS, k) or ev(VIS, k): f.add('BUG', f'5: {k}: second tap did not hide everything: {ev(VIS, k)}')
print('findings', len(f))
for x in f: print(x)
sys.exit(1 if f else 0)
