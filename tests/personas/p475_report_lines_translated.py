"""Persona 475 (v3.10.1392): generated report lines (When you eat counts, weekend sleep, Move association help) translate in Spanish without English fragments. Demo persona."""
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
    page.evaluate("typeof renderWhenEat==='function' && renderWhenEat()"); page.wait_for_timeout(400)
    page.evaluate("typeof renderExerciseReport==='function' && renderExerciseReport()")
    txt = page.evaluate("Array.from(document.querySelectorAll(\"body *:not(script):not(style)\")).filter(e=>!e.children.length).map(e=>e.textContent).join(\" | \")")
    ('gramos' in txt.lower() or 'Gramos' in txt) or f.add('FAIL', 'Spanish When-you-eat count line not found (test not exercising it)')
    for w in ('Grams a day, from', 'biggest meal is', 'a new one after an hour', 'Small numbers, and plenty', 'rest days.'):
        w in txt and f.add('FAIL', f'still English: {w}')
    errs and f.add('FAIL', f'errors {errs}')
    b.close()
print('findings', len(f)); sys.exit(1 if f else 0)
