"""Persona 167 (v3.10.1066): an abandoned demo whose saved backup came from an OLDER app version (no tdee / carb-ceiling fields) must not delete
the real account's confirmed TDEE and carb ceiling when the newer version cleans up on the next load. (Real case: Pete's mh_tdee 3400 and
mh_ceil_standard 50 vanished between his 11 and 15 Oct backups.)"""
import sys, re, json; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
bad = []
def check(n, ok, info=''):
    print(('PASS ' if ok else 'FAIL ') + n + (f'  {info}' if info and not ok else ''))
    if not ok: bad.append(n)
with fresh_server() as root, sync_playwright() as pw:
    br = pw.chromium.launch(); ctx = br.new_context(service_workers='block'); page = ctx.new_page()
    page.on('dialog', lambda d: d.dismiss()); errs = []; page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); page.evaluate("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev = page.evaluate
    ev("""localStorage.setItem('mh_tdee','3400'); localStorage.setItem('mh_ceil_standard','50'); localStorage.setItem('mh_condition','gbm'); localStorage.setItem('mh_target_kcal','3400');
      localStorage.setItem('mh_demo_active','1');
      localStorage.setItem('mh_demo_backup', JSON.stringify({kcal:'3400', protein:'167', carbs:'50', name:'Pete', condition:'gbm', goal:'maintain'}));   // an old-format backup: no tdee, ceilStd, priv, extraTargets""")
    page.reload(); page.wait_for_timeout(2500)
    r = ev("({tdee:localStorage.getItem('mh_tdee'),ceil:localStorage.getItem('mh_ceil_standard'),cond:localStorage.getItem('mh_condition'),kcal:localStorage.getItem('mh_target_kcal'),act:localStorage.getItem('mh_demo_active')})")
    check('confirmed TDEE survives an old-format backup', r['tdee'] == '3400', str(r))
    check('carb ceiling survives', r['ceil'] == '50', str(r))
    check('fields the backup does carry are still restored', r['cond'] == 'gbm' and r['kcal'] == '3400', str(r))
    check('demo marker cleared', r['act'] is None, str(r))
    # explicit null still removes (the real account genuinely had none)
    ev("""localStorage.setItem('mh_tdee','1970'); localStorage.setItem('mh_demo_active','1');
      localStorage.setItem('mh_demo_backup', JSON.stringify({kcal:'3400', tdee:null}));""")
    page.reload(); page.wait_for_timeout(2500)
    check('an explicit null still removes a demo value', ev("localStorage.getItem('mh_tdee')") is None)
    check('no JS errors', not errs, str(errs[:2]))
print('p167:', 'ALL PASS' if not bad else f'{len(bad)} FAIL: {bad}'); sys.exit(1 if bad else 0)
