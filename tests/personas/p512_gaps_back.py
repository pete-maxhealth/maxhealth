"""Persona 512 (v3.10.1436): a day picked from Settings > Data > Missing Data gets a "Back to missing days" button on the Manual Entry card; it returns to the list (refreshed, button hidden). A day opened another way has no such button."""
import sys, re, datetime; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
def dmy(d): return d.strftime('%d/%m/%y')
with fresh_server() as root, sync_playwright() as pw:
    br = pw.chromium.launch(); ctx = br.new_context(viewport={'width': 390, 'height': 900}, service_workers='block'); pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    pg.goto('http://localhost:5757/'); pg.wait_for_timeout(2500)
    t = datetime.date.today()
    pg.evaluate("""(rows) => { state.onboarded = true; state.history = (state.history || []).filter(h => false); rows.forEach(r => state.history.push(r)); saveState(); var o = document.getElementById('onboardingOverlay'); if (o) o.style.display = 'none'; }""",
        [{'date': dmy(t - datetime.timedelta(days=9)), 'steps': 8000, 'hr_resting': 60, 'sleep_duration': 420, 'totals': {'kcal': 1800}}] +
        [{'date': dmy(t - datetime.timedelta(days=k)), 'steps': 0, 'totals': {'kcal': 1500}} for k in (3, 4)])
    pg.evaluate("siteSearchOpenSettings('imp-gaps', 'import')"); pg.wait_for_timeout(900); pg.evaluate("async () => { _serverOnline = false; await mhLoadDataGaps(); }"); pg.wait_for_timeout(600)
    rows = pg.locator('#mhGapsList > div'); n = rows.count()
    n >= 2 or f.add('FAIL', f'expected at least 2 missing days listed, got {n}: ' + pg.inner_text('#mhGapsList')[:200])
    vis = lambda: pg.evaluate("(function(){var b=document.getElementById('mhGapsBackBtn'); return !!b && b.style.display!=='none'})()")
    vis() and f.add('FAIL', 'back button showing before any day picked')
    if n:
        rows.first.click(); pg.wait_for_timeout(1200)
        vis() or f.add('FAIL', 'no back button after picking a day from the list')
        pg.evaluate("_serverOnline = false; document.getElementById('mhGapsBackBtn').click()"); pg.wait_for_timeout(1200)
        vis() and f.add('FAIL', 'back button still showing after going back')
        pg.locator('#mhGapsList > div').count() >= 1 or f.add('FAIL', 'list empty after going back')
        top = pg.evaluate("(function(){var e=document.getElementById('title-imp-gaps'); var r=e.getBoundingClientRect(); return r.top})()")
        -50 < top < 700 or f.add('FAIL', f'Missing Data card not brought into view (top={top})')
    # opened another way: no back button
    pg.evaluate("mhOpenManualEntry(1)"); pg.wait_for_timeout(1200)
    vis() and f.add('FAIL', 'back button showing for a day opened without the list')
    for e in errs: f.add('JS-exception', e)
print('findings', len(f))
