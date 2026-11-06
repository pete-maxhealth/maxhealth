"""Persona 413: "Phone only" notes on a PC browser (v3.10.1309). Pete 5 Nov: anything that does not apply on a PC (launcher, Health Connect, Termux) is marked "phone only" with a "?" explaining why.
Covers: on a desktop Chrome user agent the three notes (Pipeline & Health Connect Log, Advanced / Manual Pipeline, Health Connect sync in About) are visible with a working "?", on an
Android phone user agent they are hidden, a touch (coarse pointer) desktop-sized window counts as a phone, the notes do not change the card's own open/close, no page errors.
Invented data, demo persona."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
PC = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
AND = 'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Mobile Safari/537.36'
IDS = ['phoneonly-pipelinelog', 'phoneonly-advanced', 'phoneonly-hcsync']
def run(b, ua, w, touch, pc_expected):
    ctx = b.new_context(viewport={'width': w, 'height': 900}, user_agent=ua, has_touch=touch, is_mobile=touch, service_workers='block'); page = ctx.new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.dismiss()); ev = page.evaluate
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay').style.display='none'")
    cls = ev("document.documentElement.classList.contains('mh-pc')")
    if cls != pc_expected: f.add('BUG', f'1: {ua[:25]} touch={touch}: mh-pc class is {cls}, wanted {pc_expected}')
    for i in IDS:
        n = ev(f"(()=>{{const q=document.getElementById('help-{i}'); const n=q&&q.closest('.mh-phone-note'); return n?getComputedStyle(n).display:'missing'}})()")
        if n == 'missing': f.add('BUG', f'2: note {i} missing'); continue
        if pc_expected and n == 'none': f.add('BUG', f'3: {i} hidden on a PC')
        if not pc_expected and n != 'none': f.add('BUG', f'4: {i} shown on a phone')
    if pc_expected:
        # open the Advanced card and the log card so the notes can be seen, then tap the ?
        ev("switchTabById('import')"); page.wait_for_timeout(700); ev("toggleSection('imp-advanced','imp-advanced-wrap','imp-advanced-icon')"); page.wait_for_timeout(300)
        shown = ev("getComputedStyle(document.getElementById('imp-advanced-wrap')).display")
        ev("document.querySelector('#imp-advanced-wrap .mh-phone-note [onclick*=phoneonly-advanced]').click()"); page.wait_for_timeout(200)
        if ev("getComputedStyle(document.getElementById('help-phoneonly-advanced')).display")=='none': f.add('BUG', '5: the ? on the Advanced note does not open')
        ev("toggleSection('imp-advanced','imp-advanced-wrap','imp-advanced-icon')"); page.wait_for_timeout(200)
        if ev("getComputedStyle(document.getElementById('imp-advanced-wrap')).display")==shown: f.add('BUG', '6: tapping the note changed the card open/close state')
    # the Home Screen tip is for phones only
    ev("localStorage.removeItem('mh_homescreen_tip_shown'); document.getElementById('toast') && document.getElementById('toast').classList.remove('show'); maybeShowHomeScreenTip()"); page.wait_for_timeout(2200)
    tip = ev("(document.getElementById('toast')||{}).innerText||''")
    if pc_expected and 'Home Screen' in tip: f.add('BUG', '7: the Home Screen tip shows on a PC')
    if not pc_expected and 'Home Screen' not in tip: f.add('BUG', f'8: the Home Screen tip is missing on a phone (toast: {tip[:60]})')
    if errs: f.add('BUG', f'page errors {errs[:3]}')
    ctx.close()
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch()
    run(b, PC, 1280, False, True)
    run(b, AND, 390, True, False)
    run(b, PC, 1280, True, False)   # a touch screen at desktop size is treated as a phone/tablet
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
