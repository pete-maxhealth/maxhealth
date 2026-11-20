"""Persona 514 (20 Nov 2026): a user's own AI key never leaves the phone: not in the full backup, not in a code/QR transfer, not in the settings that transfer carries."""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    br = pw.chromium.launch(); ctx = br.new_context(viewport={'width': 390, 'height': 900}, service_workers='block'); pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    pg.goto('http://localhost:5757/'); pg.wait_for_timeout(2500)
    r = pg.evaluate("""()=>{ localStorage.setItem('mh_apikey','sk-ant-TESTKEY123'); localStorage.setItem('mh_openai_key','sk-TESTOPENAI'); localStorage.setItem('mh_provider','claude');
      const full = JSON.stringify(buildFullBackupPayload()), x = JSON.stringify(mhxCollect({settings:true, library:true, recipes:true, history:true, routines:true, supplements:true}));
      return {full: /TESTKEY123|TESTOPENAI/.test(full), mhx: /TESTKEY123|TESTOPENAI/.test(x)} }""")
    r['full'] and f.add('FAIL', 'own API key found in the full backup')
    r['mhx'] and f.add('FAIL', 'own API key found in a transfer payload')
    for e in errs: f.add('JS-exception', e)
print('findings', len(f))
