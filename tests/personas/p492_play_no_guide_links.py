"""Persona 492 (v3.10.1410): in the Google Play build (?src=play) the GBM patient guide is not linked anywhere in the app (buttons, inline links, the
GKI note, the tour-card source), while the normal web app still links it everywhere. Invented data only."""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
PROBE = """(()=>{
  const vis=e=>{const r=e.getBoundingClientRect();return getComputedStyle(e).display!=='none'};
  const links=[...document.querySelectorAll('a[href="gbm_patient_guide.html"]')];
  const txt=[...document.querySelectorAll('.mh-guide-txt')];
  return {links:links.length, linksShown:links.filter(vis).length, txt:txt.length, txtShown:txt.filter(vis).length,
          tc:mhTcSrcLink(MH_TC_GUIDE), other:mhTcSrcLink({t:'Other',u:'x.html'})}})()"""
def run(pw, url, label):
    b = pw.chromium.launch(); errs = []
    page = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block').new_page()
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page.goto(url); page.wait_for_timeout(1200)
    page.evaluate("localStorage.setItem('mh_condition','gbm'); state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    page.evaluate("updateCarbZonesCondition(); updateDashboard()"); page.wait_for_timeout(300)
    r = page.evaluate(PROBE); b.close(); errs and f.add('FAIL', f'{label} page errors {errs}'); return r
with fresh_server() as root, sync_playwright() as pw:
    n = run(pw, 'http://localhost:5757/', 'web')
    n['linksShown'] >= 3 or f.add('FAIL', f'web app lost its guide links: {n}')
    n['txtShown'] >= 2 or f.add('FAIL', f'web app lost the guide wording: {n}')
    '<a ' in n['tc'] or f.add('FAIL', 'web tour source should be a link')
    p = run(pw, 'http://localhost:5757/?src=play', 'play')
    p['linksShown'] == 0 or f.add('FAIL', f'Play build still shows {p["linksShown"]} guide link(s)')
    p['txtShown'] == 0 or f.add('FAIL', 'Play build still shows guide wording')
    '<a ' not in p['tc'] and 'patient guide' in p['tc'] or f.add('FAIL', f'Play tour source should be plain text: {p["tc"]}')
    '<a ' in p['other'] or f.add('FAIL', 'other tour sources must stay links in Play')
print('findings', len(f))
