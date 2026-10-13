"""Persona 127: the app sends an anonymous device id (and a licence token if set) to the shared proxy only once the Worker has said it accepts them; an older Worker is never sent extra headers; the remaining starter count is stored and shown in Settings."""
import sys, json; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
PROXY = 'https://maxhealth-ai.bogginsuk.workers.dev/'
def run(accepts):
    seen = []
    with fresh_server() as root, sync_playwright() as pw:
        ctx = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block')
        page = ctx.new_page(); errs = []
        page.on('pageerror', lambda e: errs.append(str(e)[:200]))
        def h(route):
            r = route.request
            cors = {'access-control-allow-origin': '*', 'access-control-expose-headers': 'X-MH-Remaining, X-MH-Tier'}
            if r.method == 'GET':
                (route.fulfill(status=405, headers=cors, body='Method not allowed') if accepts else route.abort())  # an older Worker fails the CORS preflight
            elif r.method == 'OPTIONS':
                route.fulfill(status=204, headers={**cors, 'access-control-allow-methods': 'POST, OPTIONS', 'access-control-allow-headers': 'Content-Type, X-MH-Device, X-MH-Licence' if accepts else 'Content-Type'})
            else:
                seen.append(dict(r.headers))
                route.fulfill(status=200, content_type='application/json', headers={**cors, 'x-mh-remaining': '42', 'x-mh-tier': 'starter'} if accepts else cors, body=json.dumps({'content': [{'type': 'text', 'text': 'hi'}]}))
        ctx.route(PROXY + '**', h); ctx.route(PROXY, h)
        page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
        page.evaluate("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
        post = "fetch('%s',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'}).then(r=>r.status)" % PROXY.rstrip('/')
        page.evaluate(post); page.wait_for_timeout(800)          # first call: probe fires, call goes plain
        page.evaluate("localStorage.setItem('mh_licence','tok.sig')")
        page.evaluate(post); page.wait_for_timeout(800)          # second call: probe result known
        st = page.evaluate("[localStorage.getItem('mh_device_id'), localStorage.getItem('mh_ai_allowance')]")
        page.evaluate("switchTab('settings'); switchSubTab('settings','manage')"); page.wait_for_timeout(500)
        page.evaluate("mhAllowanceRefresh()")
        line = page.evaluate("(()=>{const e=document.getElementById('aiAllowanceLine');return e?[e.style.display,e.textContent]:null})()")
        if errs: f.add('BUG', f'page errors {errs[:2]}')
        return seen, st, line
seen, st, line = run(True)
if len(seen) < 2: f.add('BUG', f'expected 2 proxy posts, saw {len(seen)}')
else:
    if 'x-mh-device' in seen[0]: f.add('BUG', 'device header sent before the Worker was known to accept it')
    d = seen[1].get('x-mh-device', '')
    if len(d) < 16: f.add('BUG', f'no device id on the 2nd call: {d!r}')
    if seen[1].get('x-mh-licence') != 'tok.sig': f.add('BUG', 'licence header not sent')
if not st[0] or '"remaining":42' not in (st[1] or ''): f.add('BUG', f'allowance not stored {st}')
if not line or line[0] != 'block' or '42' not in line[1]: f.add('BUG', f'allowance line not shown {line}')
seen, st, line = run(False)
if any('x-mh-device' in s or 'x-mh-licence' in s for s in seen): f.add('BUG', 'extra headers sent to a Worker that does not accept them')
if len(seen) < 2: f.add('BUG', 'calls to an older Worker did not go through')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
