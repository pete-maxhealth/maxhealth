"""Persona 52: sleep-conflict card flags a stage-less (time-in-bed) source and lets you type your own figure; one-tap bug report builds a prefilled GitHub issue."""
import sys, re, json; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    ctx.route(re.compile(r'https://(cdn\.jsdelivr\.net|cdnjs\.cloudflare\.com|fonts\.(googleapis|gstatic)\.com)/.*'), lambda r: r.abort())
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:160]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200)
    conflict = {"date": "2026-10-08", "sessions": [
        {"source": "ringconn", "start": "2026-10-07T23:16:00", "end": "2026-10-08T08:01:00", "duration_minutes": 525},
        {"source": "zepp", "start": "2026-10-07T23:17:00", "end": "2026-10-08T07:52:00", "duration_minutes": 300}]}
    page.evaluate("c => showSleepConflictComparison(c)", conflict)
    txt = page.evaluate("document.getElementById('sleepConflictModal').textContent")
    if 'no sleep stages' not in txt or 'ringconn' not in txt.split('no sleep stages')[0][-80:]: f.add('BUG', 'span-only source not flagged')
    if txt.count('no sleep stages') != 1: f.add('BUG', f'flag should appear once (zepp has stages): {txt.count("no sleep stages")}')
    if not page.evaluate("!!document.getElementById('sleepConflictOwn')"): f.add('BUG', 'own-figure box missing')
    # server accepts manual, rejects silly values
    import urllib.request
    def post(body):
        req = urllib.request.Request('http://localhost:5757/resolve-sleep-conflict', json.dumps(body).encode(), {'Content-Type': 'application/json'})
        try:
            r = urllib.request.urlopen(req); return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read() or b'{}')
    import os
    json.dump([conflict], open(os.path.join(root, 'data', 'sleep_conflicts_pending.json'), 'w'))
    code, _ = post({'date': '2026-10-08', 'resolution': {'type': 'manual', 'minutes': 5}})
    if code != 400: f.add('BUG', f'silly manual sleep accepted: {code}')
    code, r = post({'date': '2026-10-08', 'resolution': {'type': 'manual', 'minutes': 415}})
    if code != 200 or r.get('status') != 'ok': f.add('BUG', f'own figure not accepted: {code} {r}')
    me = json.load(open(os.path.join(root, 'data', 'inbox', 'manual_entry.json'))) if os.path.exists(os.path.join(root, 'data', 'inbox', 'manual_entry.json')) else []
    if not any(e.get('date') == '2026-10-08' and e.get('sleep_duration') == 415 for e in me): f.add('BUG', f'manual sleep not saved: {me}')
    # bug report
    t = page.evaluate("mhBuildBugReportText()")
    if 'App version: v3.10.' not in t or 'Device/browser' not in t: f.add('BUG', f'bug report text thin: {t[:120]}')
    page.evaluate("window.__opened=null; window.open=(u)=>{window.__opened=u}")
    page.evaluate("mhReportBug()"); page.wait_for_timeout(500)
    u = page.evaluate("window.__opened") or ''
    if not u.startswith('https://github.com/pete-maxhealth/maxhealth/issues/new') or 'screenshot' not in u.lower() or len(u) > 7000: f.add('BUG', f'bug url wrong: {u[:100]} len={len(u)}')
    if errs: f.add('BUG', f'page errors: {errs[:3]}')
    b.close()
print("findings", len(f)); sys.exit(1 if f else 0)
