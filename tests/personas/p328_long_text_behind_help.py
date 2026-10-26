"""Persona 328 (v3.10.1221): long explanatory text on report cards sits behind a "?" (Pete, 26/10: sleep card showed paragraphs under the tiles).
On every Reports card: no plain-text block longer than 100 characters is visible by default; the "?" opens it and closes it; short lines stay visible; it survives changing the date range."""
import sys, os; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings(); os.makedirs('/tmp/p328', exist_ok=True)
IDS = ['sleep-report-content', 'fasting-report-content', 'outcomes-report-content', 'sleep-ketosis-content', 'weight-protocol-content', 'treatment-analysis-section']
JS = """(id) => { const r = document.getElementById(id); if (!r || getComputedStyle(r).display === 'none') return {absent: true};
  const vis = [...r.querySelectorAll('div')].filter(d => !d.closest('.mh-fold') && !d.querySelector('div,button,input,select,canvas,svg,table,a') && !d.id && (d.textContent||'').trim().length > 100 && parseFloat(getComputedStyle(d).fontSize) <= 13.5).map(d => d.textContent.trim().slice(0, 60));
  return {long: vis, qs: r.querySelectorAll('.mh-fold').length}; }"""
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("startDemoMode('alex')"); page.wait_for_timeout(2500)
    ev("[0,2,4,6,9,12,16,20,25,30,35].forEach(i => { const d = state.history[i]; if (d) d.notes = (d.notes ? d.notes + ', ' : '') + 'Chemotherapy'; }); saveState()")
    ev("switchTabById('reports')"); page.wait_for_timeout(900); ev("setReportRange(0, document.getElementById('rpt-range-all'))"); page.wait_for_timeout(700)
    # Pete's real case: findings lines of 100-200 characters under the Sleep tiles. Add three like his, plus one short line, then fold.
    ev("""(()=>{ const r = document.getElementById('sleep-report-content'); const mk = (txt) => { const d = document.createElement('div'); d.style.cssText = 'font-size:12px;margin-top:6px;'; d.textContent = txt; r.appendChild(d); };
      mk('Best night: 10h13 on 01/12/25. Shortest: 1h55 on 06/07/26.');
      mk('After a night under 6 hours, calories eaten that day averaged 3228 kcal against 2892 kcal after 7 hours or more (114 and 51 days). (Early Stage: an association in your own data, not proof of cause.)');
      mk('After very active days (steps well above your usual), next-night sleep averaged 5h37 against 6h08 otherwise (106 and 238 days). (Early Stage: an association in your own data, not proof of cause.)');
      mhFoldLongText('sleep-report-content'); })()""")
    if 'Best night' not in ev("(() => { const r = document.getElementById('sleep-report-content'); return [...r.querySelectorAll('div')].filter(d => !d.closest('.mh-fold') && d.textContent.startsWith('Best night')).map(d => d.textContent).join('')})()"): f.add('BUG', 'a short line stays visible')
    folds = 0
    for rid in IDS:
        d = ev(JS, rid)
        if d.get('absent'): continue
        if d['long']: f.add('BUG', f'{rid}: long text still showing: {d["long"]}')
        folds += d['qs']
    if folds == 0: f.add('BUG', 'at least one card (Sleep) folds long text behind a ?')
    # toggle
    if folds:
        ev("document.querySelector('#sleep-report-content .mh-q').click()"); page.wait_for_timeout(200)
        if ev("getComputedStyle(document.querySelector('#sleep-report-content .mh-fold')).display") != 'block': f.add('BUG', 'tapping ? opens the text')
        el = page.query_selector('#sleep-report-content'); el.scroll_into_view_if_needed(); page.screenshot(path='/tmp/p328/sleep_open.png')
        ev("document.querySelector('#sleep-report-content .mh-q').click()")
        if ev("getComputedStyle(document.querySelector('#sleep-report-content .mh-fold')).display") != 'none': f.add('BUG', 'tapping ? again closes it')
        page.screenshot(path='/tmp/p328/sleep_closed.png')
    # still folded after the range changes
    ev("setReportRange(30, document.getElementById('rpt-range-30'))"); page.wait_for_timeout(600)
    for rid in IDS:
        d = ev(JS, rid)
        if not d.get('absent') and d['long']: f.add('BUG', f'{rid}: long text shows again after a range change: {d["long"]}')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
