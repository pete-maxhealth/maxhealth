"""Clip: send and receive by code, LIVE from v3.10.1439 (Premium to send, anyone can receive free). Sam demo persona, Worker replaced by an in-clip stand-in (same screens as the real Worker). Alba. Re-cut 20 Nov 2026 to replace the coming-soon clip."""
import sys, re, json, base64; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from clip_lib import run_clip, sheet
LINES = [
 "Moving your data to another phone or PC used to mean scanning codes. Now there is a quicker way: send it by code.",
 "On the first device, tap Send by code. The app locks your data on the phone, then shows a code of sixteen letters and numbers.",
 "On the other device, open Receive by code and type it in. The first half finds the transfer. The second half is the key, and it never leaves your devices, so nobody else can read what was sent.",
 "You see a preview first. Nothing is replaced, and you can undo the whole transfer.",
 "No internet? Save a locked file with your own passphrase and send it any way you like. Receiving is free for anyone. Sending is a Premium feature. Sample data shown. Not medical advice.",
]
tok = base64.urlsafe_b64encode(json.dumps({'id': 'x', 'tier': 'premium', 'exp': 4102444800}).encode()).decode().rstrip('=') + '.sig'
STORE = {}
def worker(route):
    b = json.loads(route.request.post_data or '{}'); a = b.get('action')
    def ans(c, o): route.fulfill(status=c, content_type='application/json', headers={'access-control-allow-origin': '*'}, body=json.dumps(o))
    if a == 'xfer_put': STORE['K7QM2R9X'] = b['blob']; return ans(200, {'ok': True, 'code': 'K7QM2R9X', 'ttl': 600})
    if a == 'xfer_get':
        blob = STORE.pop(str(b.get('code')), None); return ans(200, {'ok': True, 'blob': blob}) if blob else ans(404, {'ok': False, 'error': 'No transfer with that code.'})
    ans(400, {'ok': False})
def setup(h):
    p = h.page; p.context.route(re.compile(r'workers\.dev/licence'), worker)
    p.evaluate("localStorage.setItem('mh_xfer_code','1'); localStorage.setItem('mh_licence', %s); var l=loadLibrary(); l.push({name:'Sam sourdough, 2 slices',kcal:230,protein:8,carbs:44,fat:2,per100:false}); saveLibrary(l); window._sentName='Sam sourdough, 2 slices';" % json.dumps(tok))
def s0(h):
    h.tap('#maintab-settings', 0.8); h.tap('#settingstab-import', 1.0); h.page.evaluate("mhxOpen()"); h.wait(1.0)
    h.page.evaluate("_mhx.sel={library:true}; mhxRender()"); h.wait(0.5)
    h.page.evaluate("document.getElementById('mhXferOverlay').scrollTo({top:9999,behavior:'smooth'})"); h.wait(2)
def s1(h): h.tap('button:has-text("Send by code")', 5.0)
def s2(h):
    code = h.page.inner_text('#mhxCode').replace('-', ''); h.wait(1.5)
    h.page.evaluate("var l=loadLibrary().filter(x=>x.name!==window._sentName); saveLibrary(l)")   # the 'other device' does not have it yet
    h.tap('button:has-text("Done")', 0.6); h.page.evaluate("document.getElementById('mhXferOverlay').scrollTo({top:9999,behavior:'smooth'})"); h.wait(0.8)
    h.tap('button:has-text("Receive by code")', 0.8); h.tap('#mhxCodeIn', 0.3); h.page.locator('#mhxCodeIn').press_sequentially(code, delay=130); h.wait(0.8)
    h.tap('button:has-text("Get it")', 4.0)
def s3(h): h.page.evaluate("document.getElementById('mhXferOverlay').scrollTo({top:0})"); h.wait(1); h.page.evaluate("document.getElementById('mhXferOverlay').scrollTo({top:400,behavior:'smooth'})"); h.wait(3.5)
def s4(h):
    h.page.evaluate("mhxBackHome()"); h.wait(0.6); h.page.evaluate("document.getElementById('mhXferOverlay').scrollTo({top:9999,behavior:'smooth'})"); h.wait(3)
run_clip('code_transfer', LINES, [s0, s1, s2, s3, s4], 'http://localhost:5757/?demo=sam', setup=setup)
sheet('code_transfer', [6, 14, 24, 36, 44])
