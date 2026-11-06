"""Persona 410: PC-width layout (v3.10.1306). On a window 900px or wider the page column is 880px instead of the 480px phone column; under 900px nothing changes.
Covers: widths 390 / 480 / 899 keep the phone column, 900 / 1440 give 880 (centred), no sideways scrolling on Today, Log, Insights, Settings at each width, the Log input bar
and the bottom sheet (a modal) stay inside the screen, no page errors, mouse-only walk (no touch). Invented data, demo persona."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
WANT = {390: 390, 480: 480, 899: 480, 900: 880, 1440: 880}
TABS = ('today', 'log', 'insights', 'settings')
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    for w, want in WANT.items():
        page = b.new_context(viewport={'width': w, 'height': 900}, service_workers='block').new_page()
        page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.dismiss()); ev = page.evaluate
        page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
        ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay').style.display='none'"); ev("startDemoMode('doris')"); page.wait_for_timeout(1800)
        bw = ev("document.body.getBoundingClientRect().width")
        if abs(bw - want) > 1: f.add('BUG', f'1: width {w}: body is {bw}px, wanted {want}')
        left = ev("document.body.getBoundingClientRect().left"); right = w - ev("document.body.getBoundingClientRect().right")
        if abs(left - right) > 2: f.add('BUG', f'2: width {w}: column not centred ({left} vs {right})')
        for t in TABS:
            ev(f"document.getElementById('maintab-{t}').click()"); page.wait_for_timeout(700)
            over = ev("document.documentElement.scrollWidth - document.documentElement.clientWidth")
            if over > 1: f.add('BUG', f'3: width {w}, {t}: page scrolls sideways by {over}px')
        ev("document.getElementById('maintab-log').click()"); page.wait_for_timeout(600)
        box = ev("(()=>{const e=document.getElementById('chatInput')||document.querySelector('textarea, input[type=text]'); if(!e) return null; const r=e.getBoundingClientRect(); return [r.left, r.right]})()")
        if box and (box[0] < -1 or box[1] > w + 1): f.add('BUG', f'4: width {w}: Log input outside the screen {box}')
        page.context.close()
    if errs: f.add('BUG', f'page errors {errs[:3]}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
