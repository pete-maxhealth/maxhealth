"""Persona 150: while a demo runs (or is about to resume after a language change) the real server CSVs are never fetched or merged, and the page is veiled during the resume so the person's own theme and figures never flash."""
import sys; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    hits = []
    page.on('request', lambda r: hits.append(r.url) if ('/combined' in r.url or '/master' in r.url) else None)
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    ev = page.evaluate
    ev("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev("startDemoMode('barry')"); page.wait_for_timeout(1200)
    hits.clear()
    n0 = ev("state.history.length")
    ev("autoLoadCombined()"); ev("autoImportCombinedIfStale()"); ev("restoreMissingHistoryDaysFromServer()"); page.wait_for_timeout(1500)
    if hits: f.add('BUG', f'server CSV fetched during demo: {hits[:2]}')
    if ev("state.history.length") != n0: f.add('BUG', 'history changed by a server sync during the demo')
    ev("exitDemoMode()"); page.wait_for_timeout(800)
    # veil during a language-change resume
    ev("startDemoMode('barry')"); page.wait_for_timeout(800)
    ev("sessionStorage.setItem('mh_demo_resume','barry')")
    page.reload(wait_until='commit')
    seen = False
    for _ in range(8):
        try:
            if page.evaluate("!!document.getElementById('mhResumeVeil')"): seen = True; break
        except Exception: pass
        page.wait_for_timeout(50)
    if not seen: f.add('BUG', 'no veil while the demo resumes')
    page.wait_for_timeout(3500)
    if ev("!!document.getElementById('mhResumeVeil')"): f.add('BUG', 'veil never removed')
    if not ev("_demoMode"): f.add('BUG', 'demo did not resume')
    if ev("getComputedStyle(document.body).visibility") != 'visible': f.add('BUG', 'page still hidden after resume')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
