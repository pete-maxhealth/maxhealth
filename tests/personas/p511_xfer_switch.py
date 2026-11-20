"""Persona 511 (v3.10.1435): ?xfer=1 / ?xfer=0 switch the hidden code transfer on and off; no parameter changes nothing."""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    br = pw.chromium.launch(); ctx = br.new_context(viewport={'width': 390, 'height': 900}, service_workers='block'); pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    def flag(url):
        pg.goto(url); pg.wait_for_timeout(1500); return pg.evaluate("localStorage.getItem('mh_xfer_code')")
    flag('http://localhost:5757/') is None or f.add('FAIL', 'flag set with no parameter')
    flag('http://localhost:5757/?xfer=1') == '1' or f.add('FAIL', '?xfer=1 did not switch on')
    flag('http://localhost:5757/') == '1' or f.add('FAIL', 'flag lost on a plain reload')
    pg.evaluate("state.onboarded=true; saveState(); var o=document.getElementById('onboardingOverlay'); if(o) o.style.display='none'"); pg.evaluate("mhxOpen()"); pg.wait_for_timeout(300)
    'by code' in pg.inner_text('#mhXferOverlay').lower() or f.add('FAIL', 'code section missing with switch on')
    flag('http://localhost:5757/?xfer=0') is None or f.add('FAIL', '?xfer=0 did not switch off')
    for e in errs: f.add('JS-exception', e)
print('findings', len(f))
