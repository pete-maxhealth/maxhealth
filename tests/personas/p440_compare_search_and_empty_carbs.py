"""Persona 440 (v3.10.1338): searching finds Compare Metrics and lands on its button; the carb drill-down with no days shows a dash, not NaN%."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); page = b.new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); ev = page.evaluate; errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200)
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay').style.display='none'")
    hits = ev("SITE_SEARCH_SETTINGS.filter(s=>(s.label+' '+s.keywords).toLowerCase().includes('compare metrics')||s.key==='trends-compare-metrics').map(s=>s.key)")
    if 'trends-compare-metrics' not in hits: f.add('BUG', f'1: search list has Compare Metrics: {hits}')
    for q in ['food', 'overlay']:
        r = ev(f"SITE_SEARCH_SETTINGS.filter(s=>(s.label+' '+(s.keywords||'')).toLowerCase().includes('{q}')).map(s=>s.key)")
        if 'trends-compare-metrics' not in r: f.add('BUG', f'2: searching "{q}" finds it: {r}')
    ev("switchTab('log', document.getElementById('maintab-log'))")
    ev("siteSearchOpenSettings('trends-compare-metrics','trends','insights','trends-compare-metrics')"); page.wait_for_timeout(900)
    if ev("document.getElementById('maintab-insights').classList.contains('active')") is not True: f.add('BUG', '3a: lands on Insights')
    vis = ev("(()=>{const e=document.getElementById('trends-compare-metrics'); if(!e) return 'missing'; const r=e.getBoundingClientRect(); return r.top>=0 && r.top<innerHeight && r.height>0})()")
    if vis is not True: f.add('BUG', f'3b: the Compare Metrics button is on screen after the jump: {vis}')
    # carb drill with no days
    ev("startDemoMode && false")
    ev("openMetricDrill('carbs')"); page.wait_for_timeout(700)
    t = ev("document.getElementById('metricDrillOverlay').innerText")
    if 'NaN' in t or 'null%' in t: f.add('BUG', f'4: carb drill-down with no days shows NaN/null: {t[:200]!r}')
    if errs: f.add('BUG', f'page errors {errs}')
print('findings', len(f)); [print(v) for v in f]; sys.exit(1 if f else 0)
