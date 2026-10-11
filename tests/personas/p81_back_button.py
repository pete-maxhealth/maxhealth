"""Persona 81: a top-left Back button remembers the previous screen and appears once scrolled down; it goes back one screen."""
import sys, re; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    page = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block').new_page()
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("localStorage.setItem('mh_onboarded','1')"); page.reload(); page.wait_for_timeout(1500)
    ev = page.evaluate
    ev("switchTab('today')"); ev("switchTab('settings'); switchSubTab('settings','manage')"); page.wait_for_timeout(400)
    if not ev("window._navPrev") or ev("window._navPrev.tab") != 'today': f.add('BUG', f'previous screen not remembered: {ev("window._navPrev")}')
    shown = lambda: ev("getComputedStyle(document.getElementById('globalBackBtn')).display")
    if shown() != 'none': f.add('BUG', 'back button should be hidden at the top of the screen')
    ev("(() => { const el = document.getElementById('manageScroll'); el.style.paddingBottom='1500px'; el.scrollTop = 400; trackScrollNav(el); })()"); page.wait_for_timeout(300)
    if shown() == 'none': f.add('BUG', 'back button should appear once scrolled down')
    ev("document.getElementById('globalBackBtn').click()"); page.wait_for_timeout(400)
    if ev("_navSnap().tab") != 'today': f.add('BUG', 'back did not return to the previous screen')
    # chat gets up/down arrows too (placed up the right side, clear of the docked send button)
    ev("switchTab('log'); switchSubTab('log','log')"); page.wait_for_timeout(400)
    ev("(() => { const el = document.getElementById('chatScroll'); const pad = document.createElement('div'); pad.style.cssText='height:3000px;flex:none'; el.appendChild(pad); el.scrollTop = 500; trackScrollNav(el); })()"); page.wait_for_timeout(300)
    if ev("getComputedStyle(document.getElementById('globalScrollTopBtn')).display") == 'none': f.add('BUG', 'chat should get an up arrow when scrolled down')
    if ev("getComputedStyle(document.getElementById('globalScrollTopBtn')).bottom") not in ('auto',) and ev("document.getElementById('globalScrollTopBtn').style.top") != '150px': f.add('BUG', 'chat arrows should sit clear of the send button')
    if errs: f.add('BUG', f'page errors: {errs[:2]}')
print('findings', len(f)); sys.exit(1 if f else 0)
