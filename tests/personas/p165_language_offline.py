"""Persona 165 (v3.10.1063): a language chosen with NO internet and no cached copy still translates, because the app's own server
supplies lang/<code>.json (it used to be fetched from GitHub only, so airplane mode stayed English)."""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
bad = []
def check(n, ok, info=''):
    print(('PASS ' if ok else 'FAIL ') + n + (f'  {info}' if info and not ok else ''))
    if not ok: bad.append(n)
with fresh_server() as root, sync_playwright() as pw:
    br = pw.chromium.launch(); ctx = br.new_context(viewport={'width': 430, 'height': 900}, service_workers='block'); page = ctx.new_page()
    errs = []; page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.dismiss())
    page.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())   # everything outside the phone is unreachable
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); page.evaluate("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev = page.evaluate
    for code, word in [('de', 'Einstellungen'), ('fr', 'Réglages'), ('es', 'Ajustes')]:
        ev("localStorage.clear(); state.onboarded=true; saveState()"); 
        ev(f"localStorage.setItem('mh_lang','{code}')"); page.reload(); page.wait_for_timeout(3500)
        nav = ev("document.getElementById('maintab-settings') ? document.getElementById('maintab-settings').innerText : ''")
        check(f'{code}: tab bar translated offline with no cache', nav and 'SETTINGS' not in nav.upper() and 'Settings' not in nav, repr(nav))
        check(f'{code}: dictionary loaded', ev("!!(MH_L && MH_L.dict)") is True)
    check('no JS errors', not errs, str(errs[:2]))
print('p165:', 'ALL PASS' if not bad else f'{len(bad)} FAIL: {bad}'); sys.exit(1 if bad else 0)
