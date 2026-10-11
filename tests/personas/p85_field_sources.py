"""Persona 85: each day-card row names the device its figure came from (from the server's field_sources.json); /field-sources route answers."""
import sys, re, os, json; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    os.makedirs(os.path.join(root, 'data'), exist_ok=True)
    errs = []
    from datetime import date
    t = date.today(); iso = t.isoformat(); dd = t.strftime('%d/%m/%y')
    json.dump({iso: {'steps': 'amazfit', 'distance_m': 'amazfit', 'sleep_duration': 'health_connect', 'weight': 'withings'}}, open(os.path.join(root, 'data', 'field_sources.json'), 'w'))
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 844}, service_workers='block').new_page()
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("localStorage.setItem('mh_onboarded','1')"); page.reload(); page.wait_for_timeout(2000)
    ev = page.evaluate
    r = ev("fetch('/field-sources').then(r => r.json())")
    if r.get(iso, {}).get('steps') != 'amazfit': f.add('BUG', f'/field-sources did not return the file: {r}')
    ev("mhLoadFieldSources()"); page.wait_for_timeout(500)
    ev("(d) => { state.history = [{ date: d, steps: 4277, distance_m: 3000, sleep_duration: 505, weight: 92, totals: {kcal:0,protein:0,carbs:0}, log: [] }]; trendsWindow = 'today'; _trendsDayOffset = 0; }", dd)
    ev("switchTab('insights'); switchSubTab('insights','trends'); renderTrends()"); page.wait_for_timeout(600)
    txt = ev("document.getElementById('trendsDailyView').innerText")
    for want in ('Zepp', 'Health Connect', 'Withings'):
        if want not in txt: f.add('BUG', f'day view lacks "{want}"')
    if errs: f.add('BUG', f'page errors: {errs[:2]}')
print('findings', len(f)); sys.exit(1 if f else 0)
