"""Persona 392: condition-aware starting adviser, and intake around treatment sessions (v3.10.1284).
Pete (4 Nov): diabetes wants foods by time of day; oncology wants intake around treatment sessions and supplements. Covers: with no choice made the adviser starts from the condition (diabetes -> Diabetes team, GBM -> Oncology nutrition, otherwise Coach), a remembered choice wins; the Around treatment sessions block (day before, session day, day after) with correct averages and counts, hidden with no sessions, and carried into the advice prompt. Invented data."""
import sys, json; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from datetime import date, timedelta
from playwright.sync_api import sync_playwright
f = Findings()
dmy = lambda n: (date.today() - timedelta(days=n)).strftime('%d/%m/%y')
def day(n, kcal):
    log = [{'id': n * 10 + i, 'time': t, 'description': 'Zzqx meal', 'kcal': kcal / 2, 'protein': 30, 'carbs': 5, 'fat': 5} for i, t in enumerate(['08:00', '19:00'])]
    return {'date': dmy(n), 'mode': 'standard', 'notes': 'standard', 'log': log, 'totals': {'kcal': kcal, 'protein': 60, 'carbs': 10, 'fat': 10}}
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    page = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block').new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500); ev = page.evaluate
    ev("localStorage.setItem('mh_age','52'); state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("window._calls=[]; window.callHealthAI = async (p,o)=>{ window._calls.push(p); return {ok:true,text:'TEST ADVICE'}; }")
    for cond, want in [('t2_diabetes', 'diabetes'), ('gbm', 'oncology'), ('general', 'coach')]:
        ev(f"localStorage.removeItem('mh_coach_role'); localStorage.setItem('mh_condition','{cond}')")
        if ev("mhCoachRole()") != want: f.add('BUG', f'1: {cond} starts as {want}: ' + ev("mhCoachRole()"))
    ev("localStorage.setItem('mh_condition','gbm'); mhCoachSetRole('pt')")
    if ev("mhCoachRole()") != 'pt': f.add('BUG', '2: a remembered choice wins over the condition')
    ev("localStorage.removeItem('mh_coach_role')")
    # days 1..12; sessions on days 5 and 9. before = 6,10 ; day = 5,9 ; after = 4,8
    kc = {i: 1500 for i in range(1, 13)}; kc.update({6: 2000, 10: 1800, 5: 1000, 9: 1200, 4: 1400, 8: 1600})
    ev("state.history = " + json.dumps([day(i, kc[i]) for i in range(1, 13)]) + "; saveState()")
    ev("localStorage.setItem('mh_treatment_defs', JSON.stringify([{id:'t1',name:'Zzqx Session'}])); localStorage.setItem('mh_treatment_log', JSON.stringify([{id:'a',treatmentId:'t1',date:'" + dmy(5) + "',time:'10:00'},{id:'b',treatmentId:'t1',date:'" + dmy(9) + "',time:'10:00'}]))")
    ev("switchTab('insights'); switchSubTab('insights','reports'); _rptRange=0; renderReports()"); page.wait_for_timeout(600)
    t = ev("document.getElementById('wheneat-around')?.innerText||''")
    if 'Day before' not in t or '1900 kcal' not in t or '1100 kcal' not in t or '1500 kcal' not in t or '(2)' not in t: f.add('BUG', '3: around-treatment averages (before 1900, day 1100, after 1500, 2 sessions): ' + t)
    if not ev("document.querySelector('#wheneatRoles .active')?.dataset.role") == 'oncology': f.add('BUG', '4: the Oncology adviser starts selected for GBM: ' + str(ev("document.querySelector('#wheneatRoles .active')?.dataset.role")))
    ev("document.getElementById('wheneatCoachBtn').click()"); page.wait_for_timeout(800)
    if not any('Average intake around 2 logged treatment sessions' in str(c) for c in ev("window._calls")): f.add('BUG', '5: carried into the advice prompt')
    ev("localStorage.setItem('mh_treatment_log','[]'); renderReports()"); page.wait_for_timeout(500)
    if ev("!!document.getElementById('wheneat-around')"): f.add('BUG', '6: hidden with no sessions')
    ev("localStorage.setItem('mh_treatment_log', JSON.stringify([{id:'a',treatmentId:'t1',date:'" + dmy(5) + "',time:'10:00'},{id:'b',treatmentId:'t1',date:'" + dmy(9) + "',time:'10:00'}])); renderReports()"); page.wait_for_timeout(500)
    ev("document.getElementById('wheneat-around').scrollIntoView({block:'center'})"); page.wait_for_timeout(300); page.screenshot(path='/tmp/p392.png')
    if errs: f.add('BUG', f'page errors {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
