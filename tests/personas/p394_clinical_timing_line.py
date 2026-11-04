"""Persona 394: the printed Clinical report carries the meal-timing line (v3.10.1287).
Covers: line on screen (#protoTimingLine) and in the copied text with 3+ timed days, figures right, no food names, absent with fewer than 3 timed days, no page errors. Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from datetime import date, timedelta
from playwright.sync_api import sync_playwright
f = Findings()
dmy = lambda n: (date.today() - timedelta(days=n)).strftime('%d/%m/%y')
def day(n):
    return {'date': dmy(n), 'mode': 'standard', 'notes': 'standard', 'totals': {'kcal': 1600, 'protein': 100, 'carbs': 20, 'fat': 60}, 'log': [
        {'id': n * 10 + 1, 'time': '08:00', 'description': 'Zzqx a', 'kcal': 400, 'protein': 30, 'carbs': 2, 'fat': 5},
        {'id': n * 10 + 2, 'time': '13:00', 'description': 'Zzqx b', 'kcal': 400, 'protein': 30, 'carbs': 3, 'fat': 5},
        {'id': n * 10 + 3, 'time': '19:00', 'description': 'Zzqx c', 'kcal': 400, 'protein': 40, 'carbs': 6, 'fat': 5}]}
import json
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    page = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block').new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    mk = lambda n: "state.history=" + json.dumps([day(i) for i in range(1, n + 1)]) + "; saveState()"
    ev("(()=>{let e=document.getElementById('oncologyPeriod'); if(!e){e=document.createElement('select');e.id='oncologyPeriod';document.body.appendChild(e)} e.innerHTML='<option value=30>30</option>'; e.value='30'})()")
    ev(mk(5)); ev("generateOncologyView()"); page.wait_for_timeout(500)
    line = ev("document.getElementById('protoTimingLine')?.innerText||''")
    if '5 days with times' not in line or 'first meal about 08:00' not in line or 'last about 19:00' not in line: f.add('BUG', '1: on-screen line: ' + line)
    if 'Zzqx' in line: f.add('BUG', '2: no food names')
    if 'Meal timing (5 days' not in ev("window._oncologyText"): f.add('BUG', '3: in the copied text')
    ev(mk(2)); ev("generateOncologyView()"); page.wait_for_timeout(400)
    if ev("!!document.getElementById('protoTimingLine')") or 'Meal timing' in ev("window._oncologyText"): f.add('BUG', '4: nothing with fewer than 3 days')
    ev(mk(5)); ev("generateOncologyView()"); page.wait_for_timeout(400)
    ev("document.getElementById('protoTimingLine').scrollIntoView({block:'center'})"); page.screenshot(path='/tmp/p394.png')
    if errs: f.add('BUG', f'page errors {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
