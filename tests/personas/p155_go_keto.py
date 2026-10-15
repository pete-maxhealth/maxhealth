"""Persona 155 (v3.10.1050): 'Go Keto!' opt-in for non-keto profiles. Needs the tick, turns on keto mode and a 50g ceiling without
changing the profile, Stop restores the old ceilings, a keto profile is not offered it, and a demo never leaks it into a real account."""
import sys; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    ev = page.evaluate
    ev("state.onboarded=true; localStorage.setItem('mh_condition','general'); localStorage.setItem('mh_ceil_standard','150'); saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev("startDemoMode('alex')"); page.wait_for_timeout(2500)
    ev("switchMainTab && switchMainTab('settings')") if False else None
    ev("siteSearchOpenSettings('condition','manage','settings','')"); page.wait_for_timeout(800)
    ev("mhGoKetoRender()")
    if 'Go Keto' not in ev("document.getElementById('mhGoKetoRow').innerText"): f.add('BUG', 'Go Keto not offered to Alex')
    if ev("isKetogenicCondition()"): f.add('BUG', 'Alex already keto')
    cond0 = ev("localStorage.getItem('mh_condition')")
    ev("mhGoKetoOpen()"); page.wait_for_timeout(300)
    if not ev("document.getElementById('mhGoKetoGo').disabled"): f.add('BUG', 'Go button enabled before the tick')
    ev("mhGoKetoApply()")
    if ev("localStorage.getItem('mh_keto_opt')"): f.add('BUG', 'applied without the tick')
    page.click('#mhGoKetoTick'); page.wait_for_timeout(200)
    if ev("document.getElementById('mhGoKetoGo').disabled"): f.add('BUG', 'Go button still disabled after the tick')
    page.click('#mhGoKetoGo'); page.wait_for_timeout(600)
    if not ev("isKetogenicCondition()"): f.add('BUG', 'keto mode not on after Go Keto')
    if ev("localStorage.getItem('mh_ceil_standard')") != '50': f.add('BUG', 'ceiling not 50')
    if ev("localStorage.getItem('mh_condition')") != cond0: f.add('BUG', 'profile changed')
    if 'Stop keto' not in ev("document.getElementById('mhGoKetoRow').innerText"): f.add('BUG', 'no Stop button while on')
    page.wait_for_timeout(2300)
    ev("mhGoKetoStop()")
    if ev("isKetogenicCondition()"): f.add('BUG', 'still keto after Stop')
    ev("mhGoKetoApply = mhGoKetoApply")
    # leave the demo with keto on and check the real account is untouched
    ev("localStorage.setItem('mh_keto_opt','1')"); ev("exitDemoMode()"); page.wait_for_timeout(1500)
    if ev("localStorage.getItem('mh_keto_opt')"): f.add('BUG', 'keto flag leaked out of the demo into the real account')
    if ev("localStorage.getItem('mh_ceil_standard')") != '150': f.add('BUG', 'real ceiling not restored after demo')
    ev("startDemoMode('raj')"); page.wait_for_timeout(2500)
    ev("siteSearchOpenSettings('condition','manage','settings','')"); page.wait_for_timeout(500); ev("mhGoKetoRender()")
    if ev("document.getElementById('mhGoKetoRow').innerText.trim()"): f.add('BUG', 'keto profile (Raj) offered Go Keto')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
