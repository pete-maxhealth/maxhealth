"""Persona 62: a connection that is ON but silent (airplane mode with a VPN still up). Once the app page has been saved by the service
worker, a server that never answers must not hold the page up: the saved copy appears in about NET_WAIT_MS, not the browser's long timeout.
Also the landing page (index.html) is covered by the same fallback."""
import sys, os, re, time; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844})
    state = {'hang': False}
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    def silence(on):                                   # a stopped server accepts connections but never answers
        import signal
        for pid in os.listdir('/proc'):
            if pid.isdigit():
                try:
                    if os.readlink(f'/proc/{pid}/cwd') == root + '/app' and 'server.py' in open(f'/proc/{pid}/cmdline').read(): os.kill(int(pid), signal.SIGSTOP if on else signal.SIGCONT)
                except OSError: pass
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:160]))
    ver = lambda: page.evaluate("typeof APP_VERSION !== 'undefined' ? APP_VERSION : null")
    page.goto('http://localhost:5757/'); page.wait_for_timeout(2500)
    page.reload(); page.wait_for_timeout(2500)           # saved by the worker now
    v = ver()
    page.goto('http://localhost:5757/index.html'); page.wait_for_timeout(1500)   # landing page visited once, saved too
    silence(True)
    t = time.time()
    try: page.goto('http://localhost:5757/', timeout=15000, wait_until='commit')
    except Exception as e: f.add('BUG', f'app page did not open with a silent connection: {str(e)[:100]}')
    page.wait_for_timeout(500)
    dt = time.time() - t
    if dt > 8: f.add('BUG', f'silent connection held the app page up for {dt:.1f}s')
    page.wait_for_timeout(1500)
    if ver() != v: f.add('BUG', f'saved copy not shown: {ver()!r} vs {v!r}')
    t = time.time()
    try: page.goto('http://localhost:5757/index.html', timeout=15000, wait_until='commit')
    except Exception as e: f.add('BUG', f'landing page did not open with a silent connection: {str(e)[:100]}')
    if time.time() - t > 8: f.add('BUG', 'silent connection held the landing page up')
    silence(False)
    if errs: f.add('JS-exception', str(errs[:3]))
    b.close()
print('findings', len(f)); sys.exit(1 if f else 0)
