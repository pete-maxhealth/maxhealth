"""Persona 43: with NO connection at all the app page still opens (service worker serves the last good copy), is always fresh when the server answers, and keeps its own worker across loads."""
import sys, os, re; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844})  # service workers ALLOWED
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:160]))
    ver = lambda: page.evaluate("typeof APP_VERSION !== 'undefined' ? APP_VERSION : null")
    page.goto('http://localhost:5757/'); page.wait_for_timeout(2500)
    page.evaluate("localStorage.setItem('p43_marker','kept')")
    ready = page.evaluate("navigator.serviceWorker.ready.then(r => r.active && r.active.scriptURL.endsWith('/sw.js'))")
    if not ready: f.add('BUG', 'service worker not active')
    # the page's own load must not remove the worker
    page.reload(); page.wait_for_timeout(2500)
    regs = page.evaluate("navigator.serviceWorker.getRegistrations().then(r => r.length)")
    if regs != 1: f.add('BUG', f'expected exactly 1 registration after reload, got {regs}')
    v_online = ver()
    # freshness: change the served page, online reload must show the NEW one
    html = os.path.join(root, 'app', 'maxhealth.html'); s = open(html).read()
    open(html, 'w').write(re.sub(r"const APP_VERSION = '[^']*'", "const APP_VERSION = 'v9.9.999'", s, count=1))
    page.reload(); page.wait_for_timeout(2000)
    if ver() != 'v9.9.999': f.add('BUG', f'online reload not fresh: {ver()}')
    # NO connection at all: server unreachable from the browser's point of view
    ctx.set_offline(True)
    page.goto('http://localhost:5757/'); page.wait_for_timeout(2500)
    if ver() != 'v9.9.999': f.add('BUG', f'offline open did not show the last good page: {ver()!r}')
    if page.evaluate("localStorage.getItem('p43_marker')") != 'kept': f.add('BUG', 'own saved data not visible offline')
    page.goto('http://localhost:5757/?tab=supplements'); page.wait_for_timeout(2000)
    if ver() != 'v9.9.999': f.add('BUG', f'offline open with ?tab= failed: {ver()!r}')
    # back online: fresh again from the server
    ctx.set_offline(False)
    open(html, 'w').write(s)
    page.goto('http://localhost:5757/'); page.wait_for_timeout(2500)
    if ver() != v_online: f.add('BUG', f'back online but still stale: {ver()} (expected {v_online})')
    if errs: f.add('JS-exception', str(errs[:3]))
    b.close()
print('findings', len(f)); sys.exit(1 if f else 0)
