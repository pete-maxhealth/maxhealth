"""Persona 513 (v3.10.1438): Phone to phone share list has Select all / Unselect all; a typed code gets its dashes by itself; a new screen or message starts at the top."""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    br = pw.chromium.launch(); ctx = br.new_context(viewport={'width': 390, 'height': 700}, service_workers='block'); pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    pg.goto('http://localhost:5757/?xfer=1'); pg.wait_for_timeout(2500)
    pg.evaluate("state.onboarded=true; saveState(); var o=document.getElementById('onboardingOverlay'); if(o) o.style.display='none'"); pg.evaluate("mhxOpen()"); pg.wait_for_timeout(400)
    n = lambda: pg.evaluate("MHX_SCOPES.filter(s=>_mhx.sel[s[0]]).length")
    tot = pg.evaluate("MHX_SCOPES.length")
    pg.get_by_role('button', name='Unselect all').click(); pg.wait_for_timeout(200); n() == 0 or f.add('FAIL', f'Unselect all left {n()} ticked')
    pg.get_by_role('button', name='Select all', exact=True).click(); pg.wait_for_timeout(200); n() == tot or f.add('FAIL', f'Select all gave {n()} of {tot}')
    # not premium: Send by code, scrolled down, ends at the top with the message and a toast
    pg.evaluate("document.getElementById('mhXferOverlay').scrollTop = 99999"); pg.wait_for_timeout(200)
    pg.evaluate("mhxCodeSend()"); pg.wait_for_timeout(500)
    st = pg.evaluate("document.getElementById('mhXferOverlay').scrollTop"); st == 0 or f.add('FAIL', f'not at the top after the Premium message (scrollTop {st})')
    'Premium feature' in pg.inner_text('#mhXferOverlay') or f.add('FAIL', 'Premium message missing')
    # dashes
    pg.evaluate("mhxCodeAsk()"); pg.wait_for_timeout(300)
    pg.fill('#mhxCodeIn', ''); pg.type('#mhxCodeIn', 'ab3x kqm7-zz2y n45w')
    v = pg.input_value('#mhxCodeIn'); v == 'AB3X-KQM7-ZZ2Y-N45W' or f.add('FAIL', f'dashes not added: {v}')
    pg.fill('#mhxCodeIn', ''); pg.type('#mhxCodeIn', 'abcd12'); v = pg.input_value('#mhxCodeIn'); v == 'ABCD-12' or f.add('FAIL', f'partial wrong: {v}')
    for e in errs: f.add('JS-exception', e)
print('findings', len(f))
