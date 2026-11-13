"""Persona 486 (v3.10.1404): shorter first run. A start link (?start=...) skips the long condition list; the 'How do you like to eat?' screen keeps its words
behind a '?' (help text, translated). A new user with no link still sees the condition list. Nothing real is changed by walking it. Invented data only."""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
BLOCK = re.compile(r'https://(cdn\.jsdelivr\.net|cdnjs\.cloudflare\.com|fonts\.(googleapis|gstatic)\.com)/.*')
def mk(pw):
    b = pw.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block'); ctx.route(BLOCK, lambda r: r.abort())
    page = ctx.new_page(); errs = []; page.on('pageerror', lambda e: errs.append(str(e)[:160])); return b, page, errs
def shown(ev):
    return ev("[...document.querySelectorAll('.onboard-step')].filter(s=>getComputedStyle(s).display!=='none').map(s=>s.id)")
with fresh_server() as r, sync_playwright() as pw:
    # 1. start link: step 4 -> 5 is skipped straight to the way-of-eating chooser
    b, page, errs = mk(pw); ev = page.evaluate
    page.goto('http://localhost:5757/?start=lowcarb&lang=en'); page.wait_for_timeout(2500)
    ev("onboardNext(4)"); ev("onboardNext(5)")
    s = shown(ev); s == ['step5b'] or f.add('FAIL', f'start link did not skip the condition list: {s}')
    ev("_obCondition") == 'strict_keto' or f.add('FAIL', 'condition from the link lost')
    ev("onboardNext('5c')"); s = shown(ev); s == ['step5c'] or f.add('FAIL', f'5c not reached: {s}')
    vis = ev("document.getElementById('step5c').innerText")
    'Your condition and goal set your requirements' in vis and f.add('FAIL', 'long intro still visible on 5c')
    'merge into it and skip anything' in vis and f.add('FAIL', 'long starter-foods text still visible on 5c')
    ev("document.querySelectorAll('#step5c [id^=help-]').length") == 2 or f.add('FAIL', 'expected two ? helps on 5c')
    ev("document.querySelectorAll('#step5c [id^=help-]').forEach(e=>{e.previousElementSibling&&0})")
    for hid in ('help-ob5cintro', 'help-ob5cpool'):
        ev(f"document.getElementById('{hid}').previousElementSibling.click()") if ev(f"!!document.getElementById('{hid}')") else f.add('FAIL', hid + ' missing')
        'visible' if ev(f"getComputedStyle(document.getElementById('{hid}')).display") != 'none' else f.add('FAIL', hid + ' did not open on tap')
    ev("document.getElementById('help-ob5cpool').innerText").startswith('About 150') or f.add('FAIL', 'pool help text wrong')
    # finish and check it is saved
    ev("onboardNext(6)"); ev("localStorage.getItem('mh_condition')") == 'strict_keto' or f.add('FAIL', 'condition not saved after skipping')
    errs and f.add('FAIL', f'page errors {errs}'); b.close()
    # 2. no link: the long condition list is still shown
    b, page, errs = mk(pw); ev = page.evaluate
    page.goto('http://localhost:5757/?lang=en'); page.wait_for_timeout(2500)
    ev("onboardNext(4)"); ev("onboardNext(5)")
    s = shown(ev); s == ['step5'] or f.add('FAIL', f'no-link user lost the condition list: {s}')
    ev("document.querySelectorAll('[id^=ob-condBtn-]').length") >= 5 or f.add('FAIL', 'condition buttons missing')
    errs and f.add('FAIL', f'page errors {errs}'); b.close()
    # 3. Spanish: both helps and the short lines translate
    b, page, errs = mk(pw); ev = page.evaluate
    page.goto('http://localhost:5757/?start=lose'); page.wait_for_timeout(800)
    ev("localStorage.setItem('mh_lang','es')"); page.reload(); page.wait_for_timeout(2500)
    ev("onboardNext(5)"); ev("onboardNext('5c')"); page.wait_for_timeout(500)
    t = ev("document.getElementById('step5c').innerText")
    'Elige una forma de comer' in t or f.add('FAIL', f'intro not Spanish: {t[:200]}')
    'Unos 150 alimentos' in t or f.add('FAIL', 'pool line not Spanish')
    ev("document.getElementById('help-ob5cintro').previousElementSibling.click()"); page.wait_for_timeout(200)
    'Tu condición y tu objetivo' in ev("document.getElementById('help-ob5cintro').innerText") or f.add('FAIL', 'intro help not Spanish')
    errs and f.add('FAIL', f'page errors {errs}'); b.close()
for x in f.items if hasattr(f, 'items') else []: pass
print('findings', len(f))
