"""Persona 474 (v3.10.1391): the live fasting-card lines (since last meal, goal, usual times) are built from translated pieces: Spanish shows no English fragments; English unchanged. Demo persona, invented data."""
import sys, re; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
def run(lang):
    with sync_playwright() as pw:
        b = pw.chromium.launch(); errs = []
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
        ctx.route(re.compile(r'https://(cdn\.jsdelivr\.net|cdnjs\.cloudflare\.com|fonts\.(googleapis|gstatic)\.com)/.*'), lambda r: r.abort())
        page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:160]))
        page.goto('http://localhost:5757/'); page.wait_for_timeout(800)
        page.evaluate(f"localStorage.setItem('mh_lang','{lang}')"); page.reload(); page.wait_for_timeout(1500)
        page.evaluate("startDemoMode('doris')"); page.wait_for_timeout(1500)
        page.evaluate("mhRenderFastingCard()"); page.wait_for_timeout(500)
        t = page.evaluate("['fastNowSub','fastUsualLine'].map(i=>(document.getElementById(i)||{}).textContent||'').join(' | ')")
        errs and f.add('FAIL', f'{lang} errors {errs}')
        b.close(); return t
with fresh_server() as root:
    en = run('en'); print(en)
    es = run('es'); print(es)
    ('since your last meal' in en or 'Log a meal' in en or 'No meal' in en) or f.add('FAIL', 'English line missing')
    for w in ('since your last', 'goal ', 'Your usual', 'first meal', 'the last', 'biggest meal', 'logged days'):
        w in es and f.add('FAIL', f'Spanish still has "{w}": {es[:160]}')
print('findings', len(f)); sys.exit(1 if f else 0)
