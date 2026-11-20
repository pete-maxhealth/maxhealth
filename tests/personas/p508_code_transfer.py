"""Persona 508 (v3.10.1434, UNRELEASED feature, flag mh_xfer_code): send by code (Premium) and receive by code (anyone). Worker replaced by an in-test stand-in with the same rules. Invented data."""
import sys, re, json, base64; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
STORE = {}; CALLS = []
def worker(route):
    b = json.loads(route.request.post_data or '{}'); a = b.get('action'); CALLS.append(a)
    def ans(code, o): route.fulfill(status=code, content_type='application/json', headers={'access-control-allow-origin': '*'}, body=json.dumps(o))
    if a == 'xfer_put':
        if not b.get('token'): return ans(403, {'ok': False, 'error': 'Licence not valid'})
        code = 'ABCD2345'; STORE[code] = b['blob']; return ans(200, {'ok': True, 'code': code, 'ttl': 600})
    if a == 'xfer_get':
        blob = STORE.pop(str(b.get('code')), None)
        return ans(200, {'ok': True, 'blob': blob}) if blob else ans(404, {'ok': False, 'error': 'No transfer with that code. It may have timed out.'})
    ans(400, {'ok': False})
tok = base64.urlsafe_b64encode(json.dumps({'id': 'x', 'tier': 'premium', 'exp': 4102444800}).encode()).decode().rstrip('=') + '.sig'
def boot(br, premium, flag=True):
    ctx = br.new_context(viewport={'width': 390, 'height': 900}, service_workers='block'); pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort()); pg.route(re.compile(r'workers\.dev/licence'), worker)
    pg.goto('http://localhost:5757/'); pg.wait_for_timeout(2500)
    pg.evaluate("state.onboarded=true; saveState(); var o=document.getElementById('onboardingOverlay'); if(o) o.style.display='none'; window.appConfirm=function(m,y){y&&y();}")
    pg.evaluate("localStorage.setItem('mh_xfer_code','%s')" % ('1' if flag else '0'))
    if premium: pg.evaluate("localStorage.setItem('mh_licence', %s)" % json.dumps(tok))
    return ctx, pg, errs
with fresh_server() as root, sync_playwright() as pw:
    br = pw.chromium.launch()
    # flag off: nothing about codes shows
    c0, p0, e0 = boot(br, True, flag=False); p0.evaluate("mhxOpen()"); p0.wait_for_timeout(300)
    'BY CODE' in p0.inner_text('#mhXferOverlay') and f.add('FAIL', 'code buttons visible with the flag off'); c0.close()
    # demo persona: shown as Premium coming soon with the register-interest link, no working buttons
    dc = br.new_context(viewport={'width': 390, 'height': 900}, service_workers='block'); dp = dc.new_page(); derr = []
    dp.on('pageerror', lambda e: derr.append(str(e)[:200])); dp.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    dp.goto('http://localhost:5757/?demo=doris'); dp.wait_for_timeout(3500); dp.evaluate("mhxOpen()"); dp.wait_for_timeout(300)
    dt = dp.inner_text('#mhXferOverlay'); 'coming soon' in dt or f.add('FAIL', 'demo: no coming-soon line')
    'Send by code' in dt and f.add('FAIL', 'demo: working Send button shown')
    dp.locator('#mhXferOverlay a:has-text("Register interest")').count() == 1 or f.add('FAIL', 'demo: no Register interest link')
    'tally.so' in (dp.get_attribute('#mhXferOverlay a:has-text("Register interest")', 'href') or '') or f.add('FAIL', 'demo: link is not the Tally form')
    for e in derr: f.add('JS-exception', e)
    dc.close()
    sc, sp, serr = boot(br, True); rc, rp, rerr = boot(br, False)
    sp.evaluate("var l=loadLibrary(); l.push({name:'Invented Test Loaf',kcal:250,protein:9,carbs:41,fat:3,per100:true}); saveLibrary(l); mhxOpen(); _mhx.sel={library:true}; mhxRender()"); sp.wait_for_timeout(400)
    'Send by code' in sp.inner_text('#mhXferOverlay') or f.add('FAIL', 'sender sees no Send by code button')
    sp.evaluate("mhxCodeSend()"); sp.wait_for_function("document.getElementById('mhxCode') && /-/.test(document.getElementById('mhxCode').innerText)", timeout=20000)
    code = sp.inner_text('#mhxCode'); re.fullmatch(r'[A-HJ-NP-Z2-9]{4}(-[A-HJ-NP-Z2-9]{4}){3}', code) or f.add('FAIL', 'code format: ' + code)
    code.replace('-', '')[:8] == 'ABCD2345' or f.add('FAIL', 'first half should be the Worker code')
    ''.join(STORE.values()) and 'Invented' in ''.join(STORE.values()) and f.add('FAIL', 'plain text reached the Worker')
    # free receiver: no Send, but can receive
    rp.evaluate("mhxOpen()"); rp.wait_for_timeout(300)
    t = rp.inner_text('#mhXferOverlay'); '(Premium)' in t or f.add('FAIL', 'free user should see Send by code marked Premium')
    n0 = len(CALLS); rp.evaluate("mhxCodeSend()"); rp.wait_for_timeout(300)
    len(CALLS) == n0 or f.add('FAIL', 'free send reached the Worker')
    'Premium' in rp.inner_text('#mhXferOverlay') or f.add('FAIL', 'no Premium message on free send')
    # wrong key half: refused, nothing added (the one-time copy is used up, so re-send for the real test)
    rp.evaluate("mhxCodeAsk()"); rp.wait_for_timeout(200)
    wrong = code.replace('-', '')[:8] + ('A' if code[-1] != 'A' else 'B') * 8
    rp.fill('#mhxCodeIn', wrong); rp.evaluate("mhxCodeGet()"); rp.wait_for_timeout(2500)
    'unlock' in rp.inner_text('#mhXferOverlay') or f.add('FAIL', 'wrong key half not explained: ' + rp.inner_text('#mhxCodeInfo'))
    any(x.get('name') == 'Invented Test Loaf' for x in rp.evaluate("loadLibrary()")) and f.add('FAIL', 'wrong key still added data')
    # used-up code
    rp.fill('#mhxCodeIn', code); rp.evaluate("mhxCodeGet()"); rp.wait_for_timeout(1500)
    'No transfer' in rp.inner_text('#mhxCodeInfo') or f.add('FAIL', 'used-up code not reported: ' + rp.inner_text('#mhxCodeInfo'))
    # bad shape
    rp.fill('#mhxCodeIn', 'ABC'); rp.evaluate("mhxCodeGet()"); rp.wait_for_timeout(300)
    'full code' in rp.inner_text('#mhxCodeInfo') or f.add('FAIL', 'short code not explained')
    # real run
    sp.evaluate("mhxBackHome(); mhxCodeSend()"); sp.wait_for_function("/-/.test(document.getElementById('mhxCode').innerText)", timeout=20000); code = sp.inner_text('#mhxCode')
    rp.fill('#mhxCodeIn', code.lower()); rp.evaluate("mhxCodeGet()"); rp.wait_for_timeout(3000)
    'Invented Test Loaf' in rp.inner_text('#mhXferOverlay') or rp.evaluate("_mhx.view") == 'review' or f.add('FAIL', 'no preview after a right code: ' + rp.inner_text('#mhxCodeInfo'))
    rp.evaluate("mhxDoApply()"); rp.wait_for_timeout(800)
    n = len([x for x in rp.evaluate("loadLibrary()") if x.get('name') == 'Invented Test Loaf']); n == 1 or f.add('FAIL', f'food not added once: {n}')
    rp.evaluate("mhxUndo()"); rp.wait_for_timeout(800)
    any(x.get('name') == 'Invented Test Loaf' for x in rp.evaluate("loadLibrary()")) and f.add('FAIL', 'undo did not remove it')
    # neighbouring: reload keeps working, nothing stored on the receiver about the code
    rp.reload(); rp.wait_for_timeout(2000); rp.evaluate("mhxOpen()"); 'Phone to phone' in rp.inner_text('#mhXferOverlay') or f.add('FAIL', 'screen broken after reload')
    for e in serr + rerr: f.add('JS-exception', e)
print('worker calls', CALLS)
print('findings', len(f))
