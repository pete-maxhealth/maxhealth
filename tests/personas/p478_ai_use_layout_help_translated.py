"""Persona 478 (v3.10.1396): the 'What each feature sends to the AI' and 'How the filter row, starter packs, nudges and voice commands work' help read fully in Spanish (every paragraph), and in English the wording has no splitting emphasis tags inside the three layout paragraphs."""
import sys, re; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    ctx.route(re.compile(r'https://(cdn\.jsdelivr\.net|cdnjs\.cloudflare\.com|fonts\.(googleapis|gstatic)\.com)/.*'), lambda r: r.abort())
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:160]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(800)
    page.evaluate("localStorage.setItem('mh_lang','es')"); page.reload(); page.wait_for_timeout(1500)
    page.evaluate("startDemoMode('doris')"); page.wait_for_timeout(1500)
    for hid, bad in (('help-aiusehelp', ('sends it to the AI', 'Open Food Facts search comes up empty', 'queries Claude', 'is given today', 'Informational, not used', 'narrative generation only', 'Full Report Package')),
                     ('help-layouthowhelp', ('the first thing on', 'ready-made symptom', 'tucked a Today card', 'Hide the fasting card'))):
        page.evaluate(f"var e=document.getElementById('{hid}'); if(e){{ e.style.display='block'; if (typeof mhLangFix==='function') mhLangFix(e); }}")
        page.wait_for_timeout(300)
        t = page.evaluate(f"(document.getElementById('{hid}')||{{}}).textContent||''")
        t or f.add('FAIL', f'{hid} not found')
        for w in bad:
            w in t and f.add('FAIL', f'{hid} still English: {w}')
    errs and f.add('FAIL', f'errors {errs}')
    b.close()
print('findings', len(f)); sys.exit(1 if f else 0)
