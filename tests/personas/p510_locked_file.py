"""Persona 510 (v3.10.1434, UNRELEASED, flag mh_xfer_code): Save as locked file (Premium) and Open a locked file (anyone). Invented data. Run from the repo root."""
import sys, re, json, base64, os, tempfile; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
tok = base64.urlsafe_b64encode(json.dumps({'id': 'x', 'tier': 'premium', 'exp': 4102444800}).encode()).decode().rstrip('=') + '.sig'
def boot(br, premium):
    ctx = br.new_context(viewport={'width': 390, 'height': 900}, service_workers='block', accept_downloads=True); pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    pg.goto('http://localhost:5757/'); pg.wait_for_timeout(2500)
    pg.evaluate("state.onboarded=true; saveState(); var o=document.getElementById('onboardingOverlay'); if(o) o.style.display='none'; localStorage.setItem('mh_xfer_code','1')")
    if premium: pg.evaluate("localStorage.setItem('mh_licence', %s)" % json.dumps(tok))
    return ctx, pg, errs
has = lambda pg: any(x.get('name') == 'Invented Locked Loaf' for x in pg.evaluate("loadLibrary()"))
with fresh_server() as root, sync_playwright() as pw:
    br = pw.chromium.launch(); sc, sp, se = boot(br, True); rc, rp, re_ = boot(br, False)
    sp.evaluate("var l=loadLibrary(); l.push({name:'Invented Locked Loaf',kcal:250,protein:9,carbs:41,fat:3,per100:true}); saveLibrary(l); mhxOpen(); _mhx.sel={library:true}; mhxRender()"); sp.wait_for_timeout(400)
    t = sp.inner_text('#mhXferOverlay'); 'Save as locked file' in t and 'Open a locked file' in t or f.add('FAIL', 'buttons missing')
    # free user cannot save
    rp.evaluate("mhxOpen()"); rp.wait_for_timeout(300); '(Premium)' in rp.inner_text('#mhXferOverlay') or f.add('FAIL', 'free user: Save not marked Premium')
    rp.evaluate("mhxFileSend()"); rp.wait_for_timeout(300); rp.locator('#appPromptInput').count() and f.add('FAIL', 'free user got a passphrase prompt'); 'Premium' in rp.inner_text('#mhXferOverlay') or f.add('FAIL', 'no Premium message')
    # too-short passphrase
    sp.evaluate("mhxFileSend()"); sp.wait_for_selector('#appPromptInput'); sp.fill('#appPromptInput', 'short'); sp.click('#appModalConfirm'); sp.wait_for_timeout(500)
    'too short' in sp.inner_text('#mhXferOverlay') or f.add('FAIL', 'short passphrase accepted')
    # real save
    sp.evaluate("mhxFileSend()"); sp.wait_for_selector('#appPromptInput'); sp.fill('#appPromptInput', 'correct horse battery')
    with sp.expect_download(timeout=30000) as dl: sp.click('#appModalConfirm')
    path = os.path.join(tempfile.mkdtemp(), 'locked.json'); dl.value.save_as(path); raw = open(path).read()
    'Invented' in raw and f.add('FAIL', 'plain text in the locked file'); obj = json.loads(raw); obj.get('mhxsealed') == 1 or f.add('FAIL', 'file marker missing')
    # wrong passphrase adds nothing
    rp.evaluate("mhxOpen()"); rp.wait_for_timeout(300); rp.set_input_files('#mhxFileIn', path); rp.wait_for_selector('#appPromptInput'); rp.fill('#appPromptInput', 'wrong passphrase!'); rp.click('#appModalConfirm'); rp.wait_for_timeout(3000)
    has(rp) and f.add('FAIL', 'wrong passphrase added data'); rp.evaluate("_mhx.view") == 'review' and f.add('FAIL', 'wrong passphrase reached the preview')
    # not a locked file
    junk = os.path.join(os.path.dirname(path), 'junk.json'); open(junk, 'w').write('{"hello":1}')
    rp.set_input_files('#mhxFileIn', junk); rp.wait_for_timeout(600); rp.locator('#appPromptInput').count() and f.add('FAIL', 'junk file asked for a passphrase')
    # right passphrase, preview, apply once, undo
    rp.set_input_files('#mhxFileIn', path); rp.wait_for_selector('#appPromptInput'); rp.fill('#appPromptInput', 'correct horse battery'); rp.click('#appModalConfirm'); rp.wait_for_timeout(3500)
    rp.evaluate("_mhx.view") == 'review' or f.add('FAIL', 'no preview after the right passphrase')
    rp.evaluate("mhxDoApply()"); rp.wait_for_timeout(800)
    sum(1 for x in rp.evaluate("loadLibrary()") if x.get('name') == 'Invented Locked Loaf') == 1 or f.add('FAIL', 'food not added exactly once')
    rp.evaluate("mhxUndo()"); rp.wait_for_timeout(800); has(rp) and f.add('FAIL', 'undo did not remove it')
    for e in se + re_: f.add('JS-exception', e)
print('findings', len(f))
