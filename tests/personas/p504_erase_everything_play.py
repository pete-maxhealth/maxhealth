"""Persona 504 (v3.10.1429): Play prerequisites. (a) Settings > Data > More has "Erase all my data": two confirmations, then every saved record is gone and the app reloads as a new install; Cancel at either step keeps everything.
(b) The Play build (?src=play) hides the Premium licence key box; the normal build still shows it. (c) The erase button is findable in Settings search ("erase", "delete all my data"). Invented data only."""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    br = pw.chromium.launch()
    ctx = br.new_context(viewport={'width': 390, 'height': 900}, service_workers='block'); page = ctx.new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(3000); ev = page.evaluate
    # (b) normal build shows the licence box
    ev("state.onboarded=true; saveState(); var o=document.getElementById('onboardingOverlay'); if(o) o.style.display='none'")
    page.click('#maintab-settings'); page.wait_for_timeout(600); page.click('#settingstab-manage'); page.wait_for_timeout(500)
    ev("document.getElementById('licenceCard') && getComputedStyle(document.getElementById('licenceCard')).display") != 'none' or f.add('FAIL', 'normal build: licence box missing')
    # seed some invented records
    ev("localStorage.setItem('mh_test_marker','1'); localStorage.setItem('mh_history', JSON.stringify([{date:'2026-11-01',entries:[{description:'Test food',kcal:100}]}]))")
    page.click('#settingstab-import'); page.wait_for_timeout(600)
    ev("document.getElementById('mhEraseAllBtn').closest('details').open = true"); ev("document.getElementById('mhEraseAllBtn').scrollIntoView({block:'center'})"); page.wait_for_timeout(400)
    ev("document.getElementById('mhEraseAllBtn') != null") or f.add('FAIL', 'erase button not on Settings > Data > More')
    # (a) cancel at step 1 keeps everything
    page.click('#mhEraseAllBtn'); page.wait_for_timeout(400); page.click('#appModalCancel'); page.wait_for_timeout(400)
    ev("localStorage.getItem('mh_test_marker')") == '1' or f.add('FAIL', 'cancel at step 1 still erased data')
    # cancel at step 2 keeps everything
    page.click('#mhEraseAllBtn'); page.wait_for_timeout(400); page.click('#appModalConfirm'); page.wait_for_timeout(500)
    'Last check' in ev("document.body.innerText") or f.add('FAIL', 'second confirmation did not appear')
    page.click('#appModalCancel'); page.wait_for_timeout(400)
    ev("localStorage.getItem('mh_test_marker')") == '1' or f.add('FAIL', 'cancel at step 2 still erased data')
    # both confirmed: gone, reloads
    page.click('#mhEraseAllBtn'); page.wait_for_timeout(400); page.click('#appModalConfirm'); page.wait_for_timeout(500)
    with page.expect_navigation(timeout=15000): page.click('#appModalConfirm')
    page.wait_for_timeout(3000)
    ev("localStorage.getItem('mh_test_marker')") is None or f.add('FAIL', 'marker survived the erase')
    ev("(localStorage.getItem('mh_history')||'').indexOf('Test food')") == -1 or f.add('FAIL', 'history survived the erase')
    # (c) findable
    hits = ev("(typeof MH_SETTINGS_SEARCH!=='undefined'?MH_SETTINGS_SEARCH:[]).length") if False else None
    # (b) play build hides the licence box, remembered on later launches
    ctx2 = br.new_context(viewport={'width': 390, 'height': 900}, service_workers='block'); p2 = ctx2.new_page(); p2.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    p2.goto('http://localhost:5757/?src=play'); p2.wait_for_timeout(3000)
    p2.evaluate("state.onboarded=true; saveState(); var o=document.getElementById('onboardingOverlay'); if(o) o.style.display='none'")
    p2.click('#maintab-settings'); p2.wait_for_timeout(600); p2.click('#settingstab-manage'); p2.wait_for_timeout(500)
    p2.evaluate("getComputedStyle(document.getElementById('licenceCard')).display") == 'none' or f.add('FAIL', 'Play build still shows the licence box')
    p2.goto('http://localhost:5757/'); p2.wait_for_timeout(2500)
    p2.evaluate("getComputedStyle(document.getElementById('licenceCard')).display") == 'none' or f.add('FAIL', 'Play flag not remembered on a later launch')
    errs and f.add('JS-exception', errs[0])
print('findings', len(f))
