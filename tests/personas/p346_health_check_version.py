"""Persona 346 (v3.10.1233): App Health Check no longer cries MISMATCH because of the placeholder version text in the file's markup.
It compares the version actually on screen, the file's constant and the running value; a real drift still shows."""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 430, 'height': 1000}, service_workers='block')
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    p = ctx.new_page(); p.on('pageerror', lambda e: errs.append(str(e)[:200])); ev = p.evaluate
    p.goto('http://localhost:5757/'); p.wait_for_timeout(1200); ev("state.onboarded=true; saveState()"); p.reload(); p.wait_for_timeout(1500)
    ev("switchTabById('settings')"); p.wait_for_timeout(600)
    ev("runAppHealthCheck()"); p.wait_for_timeout(3000)
    t = ev("document.getElementById('appHealthCheckOutput').textContent")
    if 'MISMATCH' in t: f.add('BUG', 'healthy app reported a version mismatch: ' + t[:300])
    if 'All in sync' not in t: f.add('BUG', 'expected "All in sync" in the version check: ' + t[:200])
    shown = ev("document.getElementById('settingsVersionDisplay').textContent")
    if ev("APP_VERSION") not in shown: f.add('BUG', f'screen version {shown!r} differs from APP_VERSION')
    # a real drift is still caught: pretend the screen shows another version
    ev("document.getElementById('settingsVersionDisplay').textContent='MaxedHealth v3.10.1'; runAppHealthCheck()"); p.wait_for_timeout(3000)
    t2 = ev("document.getElementById('appHealthCheckOutput').textContent")
    if 'MISMATCH' not in t2: f.add('BUG', 'real drift between screen and file must still be flagged')
    if errs: f.add('JS-exception', errs[0])
    b.close()
bad = any(s in ('BUG', 'JS-exception') for s, _ in f); print('BUGS' if bad else 'OK', len(f)); sys.exit(1 if bad else 0)
