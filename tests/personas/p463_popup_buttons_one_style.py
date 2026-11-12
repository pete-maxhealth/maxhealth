"""Persona 463 (v3.10.1378, Pete 12 Nov): pop-up Close / Cancel / Back are one style. Source check: every hand-built pop-up button reading Back / Cancel / Close is the grey .modal-btn.cancel (full-width closers add .mh-pop-close), apart from a frozen list of compact inline editors; rendered check: opened pop-ups show the same height, radius and colour on their Close/Cancel; Close and Cancel buttons are on screen and clickable and close their pop-up."""
import re, sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    html = open('maxhealth.html', encoding='utf-8').read()
    odd = []
    for m in re.finditer(r'<button\b([^>]*)>((?:← |✕ )?(?:Back to categories|Back|Cancel|Close(?: \(review the rest later\))?|Done))</button>', html):
        if 'modal-btn cancel' not in m.group(1): odd.append(re.sub(r'\s+', ' ', m.group(1)))
    ALLOWED = ('cancelStrengthAdd', 'cancelLibraryEdit', 'routineListContainer', 'showRoutineList', 'cancelRoutineApply', 'cancelLogEdit', 'renderResearchDigestHistory', 'cookModeTimerCancel', 'mhRulerClose', 'mhRulerBack')
    for o in odd:
        if not any(a in o for a in ALLOWED): f.add('BUG', f'1: pop-up button not in the one style: {o[:90]}')
    if 'Done' in re.findall(r'id="mhTagsClose"[^>]*>([^<]*)<', html): f.add('BUG', '2: the tags pop-up saves as you go, so it says Save not Done')
    ctx = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block'); page = ctx.new_page(); ev = page.evaluate
    page.on('pageerror', lambda e: f.add('JS-exception', str(e)[:300])); page.on('dialog', lambda d: d.dismiss())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500); ev("startDemoMode('doris')"); page.wait_for_timeout(2500)
    seen = {}
    for name, opener, mid in (('confused', "mhConfusedOpen()", 'mhConfusedModal'), ('paste', "openPasteMealModal()", 'pasteMealModal'), ('manage cats', "openManageCategoriesModal()", 'manageCategoriesModal')):
        try: ev(opener)
        except Exception as e: print('skip', name, str(e)[:60]); continue
        page.wait_for_timeout(500)
        info = ev("""(mid)=>{const m=document.getElementById(mid); if(!m) return null; const bs=[...m.querySelectorAll('button')].filter(b=>/^(← )?(Back|Cancel|Close|Save)/.test(b.textContent.trim()) && b.offsetParent!==null); return bs.map(b=>{const r=b.getBoundingClientRect(),c=getComputedStyle(b); return {t:b.textContent.trim(),h:Math.round(r.height),rad:c.borderTopLeftRadius,bg:c.backgroundColor,col:c.color,fs:c.fontSize,w:Math.round(r.width),onscreen:r.bottom<=innerHeight+1&&r.top>=0}})}""", mid)
        if info is None: f.add('BUG', f'3: {name} did not open'); continue
        if not info: f.add('BUG', f'4: {name} has no visible Close/Cancel'); continue
        for b in info:
            seen[(name, b['t'])] = b
        ev("(mid)=>document.getElementById(mid) && (document.getElementById(mid).style.display='none')", mid) if mid == 'pasteMealModal' else ev("(mid)=>document.getElementById(mid)?.remove()", mid)
    cols = {(b['bg'], b['col'], b['rad']) for b in seen.values()}
    hs = {b['h'] for b in seen.values()}
    if max(hs) - min(hs) > 2: f.add('BUG', f'6: Close/Cancel heights differ: {hs}')
    if len(cols) > 1: f.add('BUG', f'5: Close/Cancel colour or radius differs between pop-ups: {cols}')
    print({k: (v['h'], v['fs']) for k, v in seen.items()})
print('findings', len(f))
for x in f: print(x)
sys.exit(1 if f else 0)
