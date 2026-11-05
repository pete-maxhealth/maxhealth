"""Persona 398: the "Oncology team" Share-with role only shows on a GBM profile, once treatment
sessions are logged, or when it is already the chosen role (v3.10.1292). A standard profile sees four roles.
Also: the adviser chips and the share roles agree, the chosen role survives a reload, and nothing else changes."""
import sys, json; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    page = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block').new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("localStorage.setItem('mh_condition','general')")
    def go(): ev("switchTab('settings'); try{switchSubTab('settings','manage')}catch(e){}; mhShareRender()"); page.wait_for_timeout(300)
    roles = lambda: ev("[...document.querySelectorAll('#shareRoles [data-role]')].map(e=>e.dataset.role)")
    adv = lambda: ev("mhCoachRolesShown().map(r=>r[0])")
    # 1 standard profile
    go(); r = roles()
    if r != ['carer', 'clin', 'diab', 'pt']: f.add('BUG', f'1: standard profile sees four share roles, no oncology: {r}')
    if 'oncology' in adv(): f.add('BUG', '1b: standard profile adviser list has no oncology')
    if 'Oncology' in ev("document.getElementById('shareRoles').innerText"): f.add('BUG', '1c: no oncology wording in the share roles')
    # 2 GBM profile
    ev("localStorage.setItem('mh_condition','gbm')"); go(); r = roles()
    if r != ['carer', 'clin', 'diab', 'onc', 'pt']: f.add('BUG', f'2: GBM profile sees all five share roles in order: {r}')
    if 'oncology' not in adv(): f.add('BUG', '2b: GBM adviser list has oncology')
    # 3 treatment sessions logged on a standard profile
    ev("localStorage.setItem('mh_condition','general'); localStorage.setItem('mh_treatment_log', JSON.stringify([{id:'a',treatmentId:'t1',date:'01/11/2026',time:'10:00',note:''}]))"); go()
    if 'onc' not in roles(): f.add('BUG', '3: logged treatment sessions bring the oncology role back')
    ev("localStorage.removeItem('mh_treatment_log')"); go()
    if 'onc' in roles(): f.add('BUG', '3b: gone again with no sessions')
    # 4 already chosen: stays visible and active, survives reload, and clears normally
    ev("mhShareRole('onc')"); page.wait_for_timeout(200)
    if 'onc' not in roles() or not ev("!!document.querySelector('#shareRoles [data-role=onc].active')"): f.add('BUG', '4: a chosen oncology role stays shown and active')
    if not ev("mhSharePrefs().items.supps"): f.add('BUG', '4b: the role still sets its items')
    page.reload(); page.wait_for_timeout(1500); ev("document.getElementById('onboardingOverlay')?.remove()"); go()
    if 'onc' not in roles(): f.add('BUG', '4c: chosen role still shown after reload')
    ev("mhShareRole('carer')"); page.wait_for_timeout(200)
    if 'onc' in roles(): f.add('BUG', '5: choosing another role on a standard profile hides oncology again')
    if ev("[...document.querySelectorAll('#shareRoles [data-role]')].some(e=>e.offsetWidth===0)"): f.add('BUG', '6: every role chip is visible')
    page.screenshot(path='/tmp/p398_roles.png')
    if errs: f.add('BUG', 'JS errors: ' + errs[0])
print('findings', len(f)); sys.exit(1 if f else 0)
