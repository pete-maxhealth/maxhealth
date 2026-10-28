"""Persona 343 (v3.10.1230): Reports tidy-up. Sleep sits inside Sleep & Ketosis, Treatment Analysis + Sessions are one card, Ask AI + Query Builder are one card (Ask about this period), Export & Share is renamed and points to Settings > Data. Each part keeps its own data-driven show/hide; the outer card follows its parts; an older saved card order still loads; reload keeps it all. Invented data."""
import sys, re, json; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
src = open(__file__.rsplit('/',1)[0] + '/p181_sleep_outcomes.py').read()
seed = src[src.index('ev("""(()=>{\n      const d=(n)'):src.index("    S = ev(")]
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 900}, service_workers='block')
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:200])); ev = page.evaluate
    old = ['rpt-summary','rpt-insights-box','activitycredit','rpt-askai','rpt-query','rpt-export','rpt-sleepketo','rpt-fasting','rpt-weightproto','rpt-treatment','rpt-sessions','rpt-gbm','rpt-research']
    page.add_init_script("localStorage.setItem('mh_reorder_reports', %s)" % json.dumps(json.dumps(old[::-1])))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    exec(seed)
    ev("switchTabById('reports')"); page.wait_for_timeout(600); ev("renderReports()"); page.wait_for_timeout(500)
    for outer, parts in (('rpt-sleepcard', ['sleep-report-section', 'sleep-ketosis-section']), ('rpt-treatmentcard', ['treatment-analysis-section', 'treatment-sessions-section'])):
        for p in parts:
            if not ev(f"!!document.querySelector('#{outer} #{p}')"): f.add('BUG', f'{p} should sit inside {outer}')
    if not ev("document.getElementById('sleep-report-section').style.display === 'block'"): f.add('BUG', 'Sleep part not shown with 60 nights of data')
    if ev("getComputedStyle(document.getElementById('rpt-sleepcard')).display") == 'none': f.add('BUG', 'Sleep & Ketosis card hidden although a part has data')
    if ev("getComputedStyle(document.getElementById('rpt-treatmentcard')).display") != 'none': f.add('BUG', 'Treatment card shown with no treatment data')
    # a part going away hides the card when it was the last one; coming back shows it
    ev("document.getElementById('sleep-report-section').style.display='none'; document.getElementById('sleep-ketosis-section').style.display='none'"); page.wait_for_timeout(100)
    if ev("getComputedStyle(document.getElementById('rpt-sleepcard')).display") != 'none': f.add('BUG', 'card should hide when no part has data')
    ev("document.getElementById('treatment-sessions-section').style.display='block'"); page.wait_for_timeout(100)
    if ev("getComputedStyle(document.getElementById('rpt-treatmentcard')).display") == 'none': f.add('BUG', 'Treatment card should show when Sessions has data')
    ev("renderReports()"); page.wait_for_timeout(300)
    # ask + query
    if not ev("!!document.querySelector('#rpt-askai-wrap #rpt-query-wrap')"): f.add('BUG', 'Query Builder should sit inside Ask about this period')
    if 'Ask about this period' not in ev("document.getElementById('title-rpt-askai').textContent"): f.add('BUG', 'merged card title')
    ev("toggleSection('rpt-query','rpt-query-wrap','rpt-query-icon')"); page.wait_for_timeout(100)
    a = ev("getComputedStyle(document.getElementById('rpt-query-wrap')).display")
    ev("toggleSection('rpt-query','rpt-query-wrap','rpt-query-icon')"); page.wait_for_timeout(100)
    if a == ev("getComputedStyle(document.getElementById('rpt-query-wrap')).display"): f.add('BUG', 'Query Builder fold does not toggle')
    # export rename + pointer to Data
    t = ev("document.getElementById('title-rpt-export').textContent")
    if 'Make a report to hand to someone' not in t: f.add('BUG', f'export title {t!r}')
    if 'Settings → Data' not in ev("document.getElementById('rpt-export-wrap').textContent"): f.add('BUG', 'export card does not point to Data')
    # every top-level card still has move/hide controls; folded parts do not
    for k in ('rpt-askai', 'rpt-sleepketo', 'rpt-treatment', 'rpt-export'):
        if not ev(f"!!document.getElementById('title-{k}')"): f.add('BUG', f'missing title {k}')
    cnt = ev("(window._reorderableSections && window._reorderableSections.reports) || []")
    for gone in ('rpt-query', 'rpt-sessions', 'rpt-sleep'):
        if gone in cnt: f.add('BUG', f'{gone} is still a separate reorderable card')
    # search finds merged parts
    ev("siteSearchOpenSettings('rpt-askai','reports','insights')"); page.wait_for_timeout(800)
    # reload keeps everything
    page.reload(); page.wait_for_timeout(1500); ev("switchTabById('reports')"); page.wait_for_timeout(600)
    if not ev("!!document.querySelector('#rpt-askai-wrap #rpt-query-wrap')"): f.add('BUG', 'after reload Query Builder is not inside Ask')
    if errs: f.add('JS-exception', errs[0])
    b.close()
bad = any(s in ('BUG', 'JS-exception') for s, _ in f); print('BUGS' if bad else 'OK', len(f)); sys.exit(1 if bad else 0)
