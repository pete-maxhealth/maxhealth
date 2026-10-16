"""Persona 178 (v3.10.1076): exercise appears in the carer link (minutes per day, weekly line) and the weekly summary export."""
import sys, re, json, base64, urllib.parse; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
bad = []
def check(n, ok, info=''):
    print(('PASS ' if ok else 'FAIL ') + n + (f'  {info}' if info and not ok else ''))
    if not ok: bad.append(n)
with fresh_server() as root, sync_playwright() as pw:
    br = pw.chromium.launch(); ctx = br.new_context(viewport={'width': 430, 'height': 900}, service_workers='block'); page = ctx.new_page()
    errs = []; page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.dismiss())
    page.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); page.evaluate("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev = page.evaluate; ev("startDemoMode('alex')"); page.wait_for_timeout(2300)
    ev("document.getElementById('maintab-insights').click()"); page.wait_for_timeout(300)
    ev("generateCarerLink()")
    ta = ev("document.querySelector('#carerLinkOutput textarea')?.value || ''")
    check('carer link generated', 'carer.html#' in ta)
    payload = json.loads(urllib.parse.unquote(base64.b64decode(ta.split('#')[1]).decode('latin1')) if False else base64.b64decode(ta.split('#')[1]).decode('utf-8'))
    exdays = [d for d in payload['history'] if d.get('ex')]
    check('payload carries minutes on active days only', len(exdays) > 5 and all(isinstance(d['ex'], int) and d['ex'] > 0 for d in exdays) and any('ex' not in d for d in payload['history']))
    p2 = ctx.new_page(); p2.on('pageerror', lambda e: errs.append('carer ' + str(e)[:200]))
    p2.goto('http://localhost:5757/carer.html#' + ta.split('#')[1]); p2.wait_for_timeout(1200)
    t = p2.evaluate("document.body.innerText").lower()
    check('carer view shows the weekly exercise line', 'active day' in t and 'of exercise' in t, t[:100])
    check('carer view still shows daily log', 'daily log' in t)
    # weekly summary export text
    ev("_exportMode='personal'; generateWeeklySummary()"); page.wait_for_timeout(300)
    txt = ev("window._weeklySummaryText || ''")
    check('weekly summary text carries exercise', 'Exercise:' in txt or ev("document.getElementById('exportOutput').innerText.includes('🏋️')"), txt[:100])
    check('no JS errors', not errs, str(errs[:2]))
print('p178:', 'ALL PASS' if not bad else f'{len(bad)} FAIL: {bad}'); sys.exit(1 if bad else 0)
