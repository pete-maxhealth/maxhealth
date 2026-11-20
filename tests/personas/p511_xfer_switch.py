"""Persona 511 (v3.10.1435, updated 1439): the code transfer is on by default; ?xfer=0 switches it off in that browser, ?xfer=1 on, ?xfer=default back to normal."""
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
    shows = lambda: (pg.evaluate("state.onboarded=true; saveState(); var o=document.getElementById('onboardingOverlay'); if(o) o.style.display='none'"), pg.evaluate("mhxOpen()"), pg.wait_for_timeout(300), 'by code' in pg.inner_text('#mhXferOverlay').lower())[-1]
    flag('http://localhost:5757/') is None or f.add('FAIL', 'flag stored with no parameter')
    shows() or f.add('FAIL', 'code section missing by default')
    flag('http://localhost:5757/?xfer=0') == '0' or f.add('FAIL', '?xfer=0 did not store off')
    shows() and f.add('FAIL', 'code section showing after ?xfer=0')
    flag('http://localhost:5757/') == '0' or f.add('FAIL', 'off lost on a plain reload')
    flag('http://localhost:5757/?xfer=1') == '1' or f.add('FAIL', '?xfer=1 did not switch on')
    shows() or f.add('FAIL', 'code section missing after ?xfer=1')
    flag('http://localhost:5757/?xfer=default') is None or f.add('FAIL', '?xfer=default did not clear')
    shows() or f.add('FAIL', 'code section missing after ?xfer=default')
    for e in errs: f.add('JS-exception', e)
print('findings', len(f))
