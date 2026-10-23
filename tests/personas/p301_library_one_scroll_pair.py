"""Persona 301: Library shows one pair of scroll arrows, not two (v3.10.1199). Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("switchTabById('library')"); page.wait_for_timeout(600)
    ev("(()=>{const e=document.getElementById('libraryScroll'); const p=document.createElement('div'); p.style.height='6000px'; e.appendChild(p); e.scrollTo(0,1500); e.dispatchEvent(new Event('scroll')); })()"); page.wait_for_timeout(600)
    vis = ev("[...document.querySelectorAll('button')].filter(b=>/^[↑↓]$/.test(b.textContent.trim()) && getComputedStyle(b).display!=='none' && b.offsetParent!==null && b.getBoundingClientRect().width>0).map(b=>b.id)")
    if sorted(vis) != ['globalScrollBottomBtn', 'globalScrollTopBtn']: f.add('BUG', f'one pair of arrows on Library, saw {vis}')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
