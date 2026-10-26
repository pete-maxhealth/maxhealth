"""Persona 330 (v3.10.1223): the Trends weight chart must show the weight. Found while recording the charts video: for anyone under about 80 kg the axis started at 80, so the line was off the chart (blank chart). Checks the axis covers every reading in kg, lb and st, in line, bar and dots; and the style toggle really changes the chart type."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("startDemoMode('alex')"); page.wait_for_timeout(2500)
    ev("switchTabById('trends'); setTrendsFilter(30, document.getElementById('trendsBtn30'))"); page.wait_for_timeout(2000)
    for unit in ['kg', 'lbs', 'st']:
        try: ev(f"localStorage.setItem('mh_weight_unit','{unit}'); renderTrends()")
        except Exception as e: f.add('BUG', f'{unit}: {str(e)[:80]}'); continue
        page.wait_for_timeout(1200)
        d = ev("(()=>{ const c = chartInstances.chartWeight; if (!c) return null; const ys = c.data.datasets[0].data.filter(v => v != null && v !== '').map(Number); return {min: c.scales.y.min, max: c.scales.y.max, lo: Math.min(...ys), hi: Math.max(...ys), n: ys.length}; })()")
        if not d or not d['n']: f.add('BUG', f'{unit}: weight chart has readings to show'); continue
        if d['min'] > d['lo'] or d['max'] < d['hi']: f.add('BUG', f'{unit}: axis {d["min"]}-{d["max"]} covers the readings {d["lo"]}-{d["hi"]}')
    ev("localStorage.setItem('mh_weight_unit','kg'); renderTrends()"); page.wait_for_timeout(800)
    for st, typ in [('bar', 'bar'), ('point', 'line'), ('line', 'line')]:
        ev("(s)=>{ document.querySelector('.mh-chart-style-btn[data-metric-key=\"weight\"][data-style=\"'+s+'\"]').click(); }", st); page.wait_for_timeout(900)
        t = ev("chartInstances.chartWeight.config.data.datasets[0].type")
        if t != typ: f.add('BUG', f'style {st} draws the data as {typ}, got {t}')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
