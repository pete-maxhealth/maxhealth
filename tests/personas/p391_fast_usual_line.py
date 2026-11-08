"""Persona 391: "Your usual" line on the Today Fasting card (v3.10.1283).
Covers: hidden with fewer than 3 timed days; first meal, last meal and biggest-meal share from the NEWEST 30 logged days only (older days ignored); a plain fact with no advice; sits on the card when shown. Invented data."""
import sys, json; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from datetime import date, timedelta
from playwright.sync_api import sync_playwright
f = Findings()
dmy = lambda n: (date.today() - timedelta(days=n)).strftime('%d/%m/%y')
def day(n, meals):
    log = [{'id': n * 10 + i, 'time': t, 'description': 'Zzqx meal', 'kcal': 400, 'protein': p, 'carbs': 3, 'fat': 5} for i, (t, p) in enumerate(meals)]
    return {'date': dmy(n), 'mode': 'standard', 'notes': 'standard', 'log': log, 'totals': {'kcal': 1600, 'protein': 100, 'carbs': 11, 'fat': 60}}
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    page = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block').new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    txt = lambda: ev("(()=>{mhRenderFastingCard(); const e=document.getElementById('fastUsualLine'); return e.style.display==='none' ? '' : e.textContent})()")
    ev("state.history = " + json.dumps([day(i, [('08:00', 25), ('19:00', 75)]) for i in (1, 2)]) + "; saveState()")
    t1 = txt()
    if 'first meal' in t1 or 'not enough logged meal times' not in t1: f.add('BUG', '1: with 2 timed days no figures, just the not-enough line (v3.10.1329: it keeps the range control reachable): ' + t1)
    H = [day(i, [('08:00', 25), ('19:00', 75)]) for i in range(1, 31)] + [day(i, [('04:00', 50), ('23:30', 50)]) for i in range(31, 41)]
    ev("state.history = " + json.dumps(H) + "; saveState()")
    t = txt()
    if 'first meal 08:00' not in t or 'last meal 19:00' not in t or '75%' not in t or '29 logged days' not in t or 'the last 30 days' not in t: f.add('BUG', '2: the last 30 days only (older days ignored), with the right figures: ' + t)
    if any(w in t.lower() for w in ['should', 'try ', 'aim', 'better']): f.add('BUG', '3: a fact, not advice: ' + t)
    ev("switchTab('today')"); page.wait_for_timeout(500); ev("document.getElementById('fastUsualLine').scrollIntoView({block:'center'})"); page.wait_for_timeout(300); page.screenshot(path='/tmp/p391.png')
    if errs: f.add('BUG', f'page errors {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
