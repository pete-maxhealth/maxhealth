"""Persona 467 (v3.10.1382): nine hints that wrapped to three lines now fit two, with the rest behind the standard "?" (or just shorter).
Pete: anything longer than a couple of lines goes behind a "?". Checks at 390px: each visible line is at most two lines; each ? shows and hides its text; the
medication-with-fat safety line stays visible; Spanish translates the visible line and the hidden text. Demo persona, invented data only."""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
# (tab, help id or None, visible start, hidden text start or None, Spanish visible start)
ITEMS = [
 ('manage', 'kgdisplayhelp', 'Display only. Your data is always stored in kg', 'With st + lb', 'Solo visualización'),
 ('manage', 'fastmedhelp', 'Medication taken with fat or food?', 'For example MCT oil', '¿Medicación con grasa'),
 ('manage', None, 'MaxedHealth checks for updates on its own.', None, 'MaxedHealth busca actualizaciones'),
 ('manage', 'demoexithelp', 'Explore with 30 days of sample data.', 'Exit anytime', 'Explora con 30 días'),
 ('import', 'missedperiodhelp', 'Finished days below with no steps', 'The period starts at the last 14 days', 'Días terminados'),
 ('import', 'coveragehelp', 'How much of your history has each kind of data', 'Meals, steps, sleep', 'Cuánto de tu historial'),
 ('move', None, 'Needs smart-scale readings with fat and muscle.', None, 'Necesita lecturas'),
]
LINES = """t=>{const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT); let n; while(n=w.nextNode()){ if(!n.textContent.includes(t)) continue; const e=n.parentElement; const cs=getComputedStyle(e); if(cs.display==='none') continue; const lh=parseFloat(cs.lineHeight)||parseFloat(cs.fontSize)*1.3; return Math.round(e.getBoundingClientRect().height/lh);} return -1}"""  # the whole block, so a "?" wrapped onto its own line counts
TOG = "id=>{const h=document.getElementById('help-'+id); if(!h) return null; const q=h.previousElementSibling; const vis=()=>getComputedStyle(h).display!=='none'&&h.getBoundingClientRect().height>0; const a=vis(); q.click(); const b=vis(); const txt=h.innerText; q.click(); return [a,b,vis(),txt]}"
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 900}, service_workers='block'); page = ctx.new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.dismiss()); ev = page.evaluate
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500); ev("startDemoMode('doris')"); page.wait_for_timeout(2000)
    for tab, hid, vis, hid_txt, es in ITEMS:
        ev(f"switchTabById('{tab}')"); page.wait_for_timeout(500); ev("document.querySelectorAll('details').forEach(d=>d.open=true)")
        n = ev(LINES, vis)
        if n == -1: f.add('BUG', f'{vis!r}: visible line not found on {tab}')
        elif n > 2: f.add('BUG', f'{vis!r}: still {n} lines at 390px')
        if hid:
            r = ev(TOG, hid)
            if r is None: f.add('BUG', f'{hid}: no ? on {tab}')
            else:
                a, b2, c, txt = r
                if a or not b2 or c: f.add('BUG', f'{hid}: ? did not toggle properly {r[:3]}')
                if hid_txt not in txt: f.add('BUG', f'{hid}: hidden text lost {hid_txt!r}: {txt[:80]!r}')
    # the safety line stays visible
    ev("switchTabById('manage')"); page.wait_for_timeout(400)
    if 'Never delay a dose.' not in ev("document.body.innerText"): f.add('BUG', 'the never-delay-a-dose safety line is no longer visible')
    # Move association note and the lifestyle note (rendered by code): the ? exist and the visible half is short
    for tab, js, hid in (('move', None, 'moveassochelp'), ('manage', None, 'lifestylenotehelp')):
        ev(f"switchTabById('{tab}')"); page.wait_for_timeout(500)
        if ev(f"!!document.getElementById('help-{hid}')") is False: f.add('INFO', f'{hid} not on screen in this persona (rendered only with data)')
        else:
            r = ev(TOG, hid)
            if r is None or r[0] or not r[1] or r[2]: f.add('BUG', f'{hid}: ? did not toggle properly {r}')
    # Spanish: visible lines translate; the hidden texts do too
    ev("localStorage.setItem('mh_lang','es')"); page.reload(); page.wait_for_timeout(1800); ev("startDemoMode('doris')"); page.wait_for_timeout(2200)
    for tab, hid, vis, hid_txt, es in ITEMS:
        ev(f"switchTabById('{tab}')"); page.wait_for_timeout(700); ev("document.querySelectorAll('details').forEach(d=>d.open=true)")
        if es not in ev("document.body.innerText"): f.add('BUG', f'Spanish: {es!r} not shown for {vis!r}')
        if hid:
            r = ev(TOG, hid)
            if r and re.search(r'[A-Za-z]{4,}', hid_txt or '') and hid_txt in r[3]: f.add('BUG', f'Spanish: hidden text for {hid} still English: {r[3][:60]!r}')
    if errs: f.add('JS-exception', errs[0])
print('findings', len(f))
for x in f: print(x)
sys.exit(1 if f else 0)
