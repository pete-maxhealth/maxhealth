"""Persona 195: Raj in Spanish, whole app. Statistics, Reports, Trends and Settings > Data must carry no known English UI phrases, short patterns take numbers with units (50g, 1h01), and the bedtime sentence never shows a fractional clock time."""
import sys, os, re; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
ENGLISH = ['Ask your own data', 'Top 10 foods', 'Carb adherence', 'AVERAGE NIGHT', 'EXAMPLE ONLY', 'Your usual meal times', 'Your usual sleep', 'Backup & restore', 'Connect devices',
           'Eating window', 'Every fast', 'WHAT YOU DID', 'ACTIVE DAYS', 'What seems to move what', 'Premium syncs these', 'Your whole weight history', 'Protein misses', 'Ketogenic ratio',
           'Starter packs', 'Wearable devices', 'Nutrition history (meals)', 'Download all fasts', 'Best night:', 'of nights', 'looks helpful', 'ceiling 50g', 'target 120g']
SCREENS = [('insights', 'trends'), ('insights', 'stats'), ('insights', 'reports'), ('settings', 'import')]
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.dismiss())
    def serve(route):
        p = os.path.join(ROOT, 'lang', route.request.url.split('/lang/')[1].split('?')[0])
        route.fulfill(status=200, content_type='application/json', body=open(p, 'rb').read()) if os.path.exists(p) else route.fulfill(status=404, body='')
    page.route('**/raw.githubusercontent.com/**/lang/*.json', serve)
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev("startDemoMode('raj')"); page.wait_for_timeout(1500)
    ev("mhLangSet('es')"); page.wait_for_timeout(4000)
    ev("trendsWindow='30'")
    for tab, sub in SCREENS:
        ev(f"switchTab('{tab}', document.getElementById('maintab-{tab}'))"); page.wait_for_timeout(500)
        ev(f"(()=>{{const e=document.getElementById('{tab}tab-{sub}'); switchSubTab('{tab}','{sub}',e)}})()"); page.wait_for_timeout(2500)
        ev("(()=>{const b=[...document.querySelectorAll('button')].find(b=>b.offsetParent&&/Open all|Abrir todo/.test(b.textContent)); if(b) b.click()})()"); page.wait_for_timeout(1500)
        txt = ev("document.querySelector('.view.active').innerText")
        for e in ENGLISH:
            if e in txt: f.add('BUG', f'{tab}/{sub}: English left: {e!r}')
        if re.search(r'\d{1,2}:\d{2}\.\d{3,}', txt): f.add('BUG', f'{tab}/{sub}: fractional clock time')
        if len(txt) < 200: f.add('BUG', f'{tab}/{sub}: screen did not render ({len(txt)} chars)')
    if ev("mhClock(1.7*60+0.4)") != ev("mhClock(Math.round(1.7*60+0.4))"): f.add('BUG', 'mhClock does not round')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
