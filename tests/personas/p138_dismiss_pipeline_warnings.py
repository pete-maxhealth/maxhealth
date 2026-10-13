"""Persona 138: pipeline warnings in System health can be dismissed. They disappear after dismissing, come back if the same problem is logged again afterwards, nothing else is touched; the client shows the link, 'Resolve sleep conflict' says so when nothing is open."""
import sys, os, json, urllib.request; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright
U = 'http://localhost:5757'; f = Findings()
def get(p): return json.loads(urllib.request.urlopen(U + p, timeout=15).read())
def post(p, b=None): return json.loads(urllib.request.urlopen(urllib.request.Request(U + p, json.dumps(b or {}).encode(), {'Content-Type': 'application/json'}), timeout=10).read())
def line(ts, msg): return f"{ts.strftime('%Y-%m-%d %H:%M:%S')} | health_connect | x | WARN | {msg}\n"
with fresh_server() as root, sync_playwright() as pw:
    write_hc_export(root, [dict(date=d, steps=6000, sleep_duration=420, hr_avg=65, weight=80.0) for d in days(10)]); run_pipeline(root)
    log = os.path.join(root, 'logs', 'pipeline.log'); os.makedirs(os.path.dirname(log), exist_ok=True)
    with open(log, 'a') as fh:
        for i in range(3): fh.write(line(datetime.now() - timedelta(hours=2 + i), 'Overlapping sleep sessions for 2026-10-13, needs resolution'))
    pw_items = lambda: [i['text'] for i in get('/selfcheck')['items'] if 'Pipeline' in i['text']]
    if not pw_items(): f.add('BUG', f'seeded pipeline warning not reported: {get("/selfcheck")["items"]}')
    other = [i['text'] for i in get('/selfcheck')['items'] if 'Pipeline' not in i['text']]
    if post('/clear-pipeline-warnings').get('status') != 'ok': f.add('BUG', 'clear endpoint did not say ok')
    if pw_items(): f.add('BUG', f'warnings still shown after dismissing: {pw_items()}')
    if [i['text'] for i in get('/selfcheck')['items'] if 'Pipeline' not in i['text']] != other: f.add('BUG', 'dismissing changed other items')
    import time; time.sleep(1.2)
    with open(log, 'a') as fh: fh.write(line(datetime.now(), 'Overlapping sleep sessions for 2026-10-14, needs resolution'))
    if not pw_items(): f.add('BUG', 'a new warning after dismissing was hidden')
    # client
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto(U + '/'); page.wait_for_timeout(1500); page.evaluate("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev = page.evaluate
    ev("switchTab('settings', document.getElementById('maintab-settings'))"); page.wait_for_timeout(600); ev("updateSelfCheckDisplay()"); page.wait_for_timeout(800)
    t = ev("document.getElementById('selfCheckDisplay').textContent")
    for need in ('Dismiss pipeline warnings', 'Resolve sleep conflict'):
        if need not in t: f.add('BUG', f'System health lacks {need!r}')
    ev("mhResolveSleepFromHealth()"); page.wait_for_timeout(900)
    toast = ev("document.body.innerText")
    if 'No open sleep conflict' not in toast: f.add('BUG', 'resolve link gave no feedback when nothing is open')
    ev("mhClearPipelineWarnings()"); page.wait_for_timeout(500)
    ev("(()=>{ const b=[...document.querySelectorAll('button')].filter(b=>b.textContent.trim()==='Dismiss' && b.offsetParent); if(b[0]) b[0].click(); })()"); page.wait_for_timeout(1500)
    if pw_items(): f.add('BUG', 'client dismiss did not clear the warnings')
    if 'Dismiss pipeline warnings' in ev("document.getElementById('selfCheckDisplay').textContent"): f.add('BUG', 'dismiss link still shown with nothing to dismiss')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
