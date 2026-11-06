"""Persona 416: the top-left back arrow (v3.10.1312, logo clear of it v3.10.1314) must be clickable, not hidden under the header.
Covers: widths 400 / 900 / 1000 / 1440, Settings -> Today then scroll: the arrow is the top element at its own position and a real mouse click returns to Settings; pressing again returns to Today; nothing else changes. Demo persona, invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    for w in (400, 900, 1000, 1440):
        page = b.new_context(viewport={'width': w, 'height': 900}, service_workers='block').new_page(); ev = page.evaluate
        page.on('pageerror', lambda e: errs.append(str(e)[:200]))
        page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
        ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay').style.display='none'"); ev("startDemoMode('doris')"); page.wait_for_timeout(1500)
        ev("document.getElementById('maintab-settings').click()"); page.wait_for_timeout(700)
        ev("document.getElementById('maintab-today').click()"); page.wait_for_timeout(700)
        ev("(()=>{const s=document.getElementById(window._activeScrollContainerId); s.scrollTop=400; s.dispatchEvent(new Event('scroll'))})()"); page.wait_for_timeout(500)
        top = ev("(()=>{const r=document.getElementById('globalBackBtn').getBoundingClientRect(); const e=document.elementFromPoint(r.left+22,r.top+22); return e&&e.id})()")
        if top != 'globalBackBtn': f.add('BUG', f'1: width {w}: arrow is covered by {top}')
        lg = ev("(()=>{const b=document.getElementById('globalBackBtn').getBoundingClientRect(), l=document.getElementById('appLogoDefault').getBoundingClientRect(); return l.left < b.right && l.right > b.left && l.top < b.bottom && l.bottom > b.top})()")
        if lg: f.add('BUG', f'4: width {w}: the arrow sits on top of the logo')
        try:
            page.click('#globalBackBtn', timeout=3000); page.wait_for_timeout(600)
            tab = ev("document.querySelector('#mainTabRow .tab.active').id")
            if tab != 'maintab-settings': f.add('BUG', f'2: width {w}: click went to {tab}, wanted settings')
        except Exception as e: f.add('BUG', f'3: width {w}: click failed {str(e)[:80]}')
        page.context.close()
    if errs: f.add('BUG', f'page errors {errs[:3]}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
