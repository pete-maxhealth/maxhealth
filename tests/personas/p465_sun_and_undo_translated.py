"""Persona 465 (v3.10.1379): the Sun theme note and the Statistics delete / put-back toasts are translated (Spanish, German checked) with the times and the name filled in; English unchanged. Demo persona."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    ctx = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block'); page = ctx.new_page(); ev = page.evaluate
    page.on('pageerror', lambda e: f.add('JS-exception', str(e)[:300])); page.on('dialog', lambda d: d.dismiss())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500); ev("startDemoMode('doris')"); page.wait_for_timeout(2500)
    ev("switchTabById('manage')"); page.wait_for_timeout(600)
    ev("applyTheme('sun')"); page.wait_for_timeout(500)
    en = ev("document.getElementById('sunThemeNote').textContent")
    if not en.startswith('Sun: light from') or '{0}' in en: f.add('BUG', f'1: English Sun note wrong: {en!r}')
    for lang, start in (('es', 'Sol:'), ('de', 'Sonne:')):
        ev(f"mhLangSet('{lang}')"); page.wait_for_timeout(2500)
        ev("switchTabById('manage')"); page.wait_for_timeout(600); ev("applyTheme('sun')"); page.wait_for_timeout(400)   # the language switch reloads the demo, which resets its theme
        t = ev("document.getElementById('sunThemeNote').textContent")
        if not t.startswith(start) or '{' in t or 'Sun:' in t: f.add('BUG', f'2: {lang} Sun note not translated or placeholder left: {t!r}')
        d = ev("mhLangT('\"{0}\" deleted').replace('{0}', 'Steps')"); b = ev("mhLangT('\"{0}\" put back in the Library').replace('{0}', 'Steps')")
        if 'deleted' in d or 'put back' in b or '{' in d + b or 'Steps' not in d + b: f.add('BUG', f'3: {lang} toasts: {d!r} {b!r}')
    ev("mhLangSet('en')"); page.wait_for_timeout(2000)
print('findings', len(f))
for x in f: print(x)
sys.exit(1 if f else 0)
