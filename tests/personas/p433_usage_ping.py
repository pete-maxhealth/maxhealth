"""Persona 433: the app tells the developer's Worker once a day, anonymously, that an install is in use (GET /ping with the random device code and version only); not in demo mode; not twice in a day; a failure is retried next open; an older Worker (405) is harmless."""
import sys, json, re; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
PING = 'https://maxhealth-ai.bogginsuk.workers.dev/ping'
def session(mode, demo=False, reopen=False, preday=None):
    seen = []
    with fresh_server() as root, sync_playwright() as pw:
        ctx = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block')
        page = ctx.new_page(); errs = []
        page.on('pageerror', lambda e: errs.append(str(e)[:200]))
        def h(route):
            r = route.request; cors = {'access-control-allow-origin': '*', 'access-control-allow-headers': 'X-MH-Device', 'access-control-allow-methods': 'GET, POST, OPTIONS'}
            if r.method == 'OPTIONS': return route.fulfill(status=204, headers=cors)
            seen.append({'method': r.method, 'url': r.url, 'headers': dict(r.headers), 'body': r.post_data})
            if mode == 'fail': return route.abort()
            route.fulfill(status=405 if mode == 'old' else 204, headers=cors, body='')
        ctx.route(re.compile(r'https://maxhealth-ai\.bogginsuk\.workers\.dev/ping.*'), h)
        page.goto('http://localhost:5757/'); page.wait_for_timeout(800)
        if preday: page.evaluate("d=>localStorage.setItem('mh_ping_day',d)", preday)
        page.evaluate("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1200)
        if demo: page.evaluate("localStorage.setItem('mh_demo_active','1'); localStorage.removeItem('mh_ping_day')")   # set after the reload: a stale demo flag is cleared at start-up
        page.evaluate("mhUsagePing()"); page.wait_for_timeout(900)
        day = page.evaluate("localStorage.getItem('mh_ping_day')")
        dev = page.evaluate("localStorage.getItem('mh_device_id')")
        ver = page.evaluate("APP_VERSION")
        if reopen:
            page.evaluate("mhUsagePing()"); page.wait_for_timeout(600)
        if errs: f.add('BUG', f'page errors {errs[:2]}')
        return seen, day, dev, ver
# normal: one GET carrying only the device code and the version
seen, day, dev, ver = session('ok', reopen=True)
if len(seen) != 1: f.add('BUG', f'expected exactly 1 ping in a day, saw {len(seen)}')
else:
    s = seen[0]
    if s['method'] != 'GET': f.add('BUG', 'ping is not a GET (an older Worker would treat a POST as an AI call)')
    if s['headers'].get('x-mh-device') != dev: f.add('BUG', f"ping device code {s['headers'].get('x-mh-device')!r} is not the install's code {dev!r}")
    if not s['url'].endswith('?v=' + ver.lstrip('v')): f.add('BUG', f"version not sent as ?v=: {s['url']}")
    if s['body']: f.add('BUG', 'ping carried a body')
    extra = [k for k in s['headers'] if k.startswith('x-mh-') and k != 'x-mh-device']
    if extra: f.add('BUG', f'unexpected app headers on the ping {extra}')
if not day: f.add('BUG', 'ping day not remembered after success')
# a new day pings again
seen, day, dev, ver = session('ok', preday='2000-01-01')
if len(seen) < 1: f.add('BUG', 'no ping on a new day')
# demo mode never pings
seen, day, dev, ver = session('ok', demo=True)
if seen: f.add('BUG', 'demo mode pinged the developer')
# failure: not remembered, so it retries next open
seen, day, dev, ver = session('fail')
if day: f.add('BUG', 'a failed ping was marked as done')
# older Worker answers 405: treated as done, no retry storm
seen, day, dev, ver = session('old', reopen=True)
if len(seen) != 1 or not day: f.add('BUG', f'older Worker handling wrong: pings={len(seen)} day={day}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
