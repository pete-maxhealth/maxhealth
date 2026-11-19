"""Persona 509 (v3.10.1434, unreleased feature): send/receive by code strings translated in all eight languages (tools/lang_add_v1434_code_transfer.py), on the home, send, receive screens and the demo coming-soon line. Run from the repo root."""
import sys, json, re, base64; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings(); chk = lambda ok, m: None if ok else f.add('BUG', m)
LANGS = ['es', 'de', 'fr', 'tr', 'pt', 'it', 'pl', 'nl']
tok = base64.urlsafe_b64encode(json.dumps({'id': 'x', 'tier': 'premium', 'exp': 4102444800}).encode()).decode().rstrip('=') + '.sig'
HOME = ['BY CODE, NO CAMERA', 'Type a code on the other device. Works over the internet, on any phone or PC.', '🔢 Send by code', '⌨ Receive by code']
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    for l in LANGS:
        d = json.load(open(f'lang/{l}.json', encoding='utf-8'))
        ctx = b.new_context(viewport={'width': 390, 'height': 900}, service_workers='block'); page = ctx.new_page(); ev = page.evaluate
        page.on('pageerror', lambda e: errs.append(l + ' ' + str(e)[:160])); page.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
        page.route(re.compile(r'workers\.dev/licence'), lambda r: r.fulfill(status=200, content_type='application/json', body=json.dumps({'ok': True, 'code': 'ABCD2345', 'ttl': 600})))
        page.goto('http://localhost:5757/'); page.wait_for_timeout(800); ev(f"localStorage.setItem('mh_lang','{l}'); localStorage.setItem('mh_xfer_code','1'); localStorage.setItem('mh_licence', {json.dumps(tok)})"); page.reload(); page.wait_for_timeout(1500)
        ev("state.onboarded=true; saveState(); document.getElementById('onboardingOverlay')?.remove()")
        ev("mhxOpen()"); page.wait_for_timeout(700); t = page.inner_text('#mhXferOverlay')
        for k in HOME: chk(d[k] in t, f'{l} home: {k[:30]!r} not translated')
        ev("mhxCodeSend()"); page.wait_for_timeout(3500); t = page.inner_text('#mhXferOverlay')
        for k in ['TYPE THIS ON THE OTHER DEVICE', 'Valid for 10 minutes, and works once. Keep this screen open. The data is locked with the second half of this code, which is never sent anywhere.']: chk(d[k] in t, f'{l} send: {k[:30]!r} not translated')
        ev("mhxCodeAsk()"); page.wait_for_timeout(700); t = page.inner_text('#mhXferOverlay')
        for k in ['THE CODE SHOWN ON THE OTHER DEVICE', 'Get it', 'You see a preview before anything is added.']: chk(d[k] in t, f'{l} receive: {k[:30]!r} not translated')
        page.fill('#mhxCodeIn', 'ABC'); ev("mhxCodeGet()"); page.wait_for_timeout(500)
        chk(d['That is not a full code. It has 16 letters and numbers, shown in four groups.'] in page.inner_text('#mhxCodeInfo'), f'{l}: short-code message not translated')
        ctx.close()
        ctx = b.new_context(viewport={'width': 390, 'height': 900}, service_workers='block'); page = ctx.new_page()
        page.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort()); page.goto('http://localhost:5757/?demo=doris'); page.wait_for_timeout(800)
        page.evaluate(f"localStorage.setItem('mh_lang','{l}')"); page.goto('http://localhost:5757/?demo=doris'); page.wait_for_timeout(3500); page.evaluate("mhxOpen()"); page.wait_for_timeout(700)
        chk(d['⭐ Premium, coming soon: type a code on the other device to send or receive over the internet, on any phone or PC. Anyone will be able to receive.'] in page.inner_text('#mhXferOverlay'), f'{l}: demo coming-soon line not translated')
        ctx.close()
    errs and f.add('JS-exception', errs[0])
print('findings', len(f))
