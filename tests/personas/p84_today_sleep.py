"""Persona 84: Trends 'Today' shows today's own sleep (the night you woke from), not yesterday's row; yesterday's only fills in when today has none."""
import sys, re; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    page = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block').new_page()
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("localStorage.setItem('mh_onboarded','1')"); page.reload(); page.wait_for_timeout(1500)
    ev = page.evaluate
    ev("""() => { const fmt = n => { const d = new Date(Date.now() - n * 86400000); return String(d.getDate()).padStart(2,'0') + '/' + String(d.getMonth()+1).padStart(2,'0') + '/' + String(d.getFullYear()).slice(2); };
      state.history = [ { date: fmt(0), sleep_duration: 505, sleep_deep: 79, sleep_light: 273, sleep_rem: 153, steps: 4277, totals: {kcal:0,protein:0,carbs:0}, log: [] },
                        { date: fmt(1), sleep_duration: 195, sleep_deep: 50, sleep_light: 95, sleep_rem: 35, steps: 3374, totals: {kcal:0,protein:0,carbs:0}, log: [] } ]; window.__fmt = fmt; }""")
    ev("trendsWindow = 'today'; _trendsDayOffset = 0")
    d = ev("getTrendsData()[0]")
    if d.get('sleep_duration') != 505: f.add('BUG', f"today should show its own sleep 505, got {d.get('sleep_duration')}")
    ev("state.history[0].sleep_duration = null; state.history[0].sleep_deep = null")
    d = ev("getTrendsData()[0]")
    if d.get('sleep_duration') != 195: f.add('BUG', f"with no sleep on today's row, yesterday's should fill in, got {d.get('sleep_duration')}")
    if errs: f.add('BUG', f'page errors: {errs[:2]}')
print('findings', len(f)); sys.exit(1 if f else 0)
