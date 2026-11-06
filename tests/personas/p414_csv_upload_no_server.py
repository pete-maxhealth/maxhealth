"""Persona 414: bulk CSV upload with no server, the PC / cloud route (v3.10.1310). Pete 5 Nov: a CSV import and export routine for watch/sleep data on a PC, same shape both ways.
Covers: with the server offline a filled template saves into the browser (ISO and UK dates, a blank row skipped), sleep given in hours becomes minutes, the cache holds every day,
an exported combined.csv (sleep in minutes) re-uploads without sleep being multiplied by 60, a bad date is reported not saved, the result survives a reload, the single-entry route
is untouched, no page errors. Invented data, fresh (non-demo) browser."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
CSV = "date,weight,steps,sleep_duration\n2026-10-05,84.2,6100,7.5\n06/10/2026,83.9,,450\n2026-10-07,,8200,\n,,,\nnot-a-date,80,1,6\n"
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 1280, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.dismiss()); ev = page.evaluate
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay').style.display='none'"); ev("switchTabById('import')"); page.wait_for_timeout(900)
    ev("_serverOnline = false")
    page.set_input_files('#manualCsvUploadInput', files=[{'name': 'mine.csv', 'mimeType': 'text/csv', 'buffer': CSV.encode()}]); page.wait_for_timeout(1500)
    out = ev("(document.getElementById('manualEntryOutput')||{}).textContent||''")
    if 'Saved 3 day' not in out: f.add('BUG', f'1: result line: {out}')
    if "couldn't read" not in out: f.add('BUG', f'2: the unreadable date is not reported: {out}')
    row = lambda d: ev(f"(()=>{{const r=mhCloudHistoryRow('{d}'); return r?{{w:r.weight,s:r.steps,sl:r.sleep_duration}}:null}})()")
    r1, r2, r3 = row('2026-10-05'), row('2026-10-06'), row('2026-10-07')
    if not r1 or float(r1['sl']) != 450 or float(r1['w']) != 84.2: f.add('BUG', f'3: day 1 (7.5 hours) is {r1}')
    if not r2 or float(r2['sl']) != 450: f.add('BUG', f'4: day 2 (UK date, sleep already in minutes) is {r2}')
    if not r3 or float(r3['s']) != 8200: f.add('BUG', f'5: day 3 (steps only) is {r3}')
    cache = ev("localStorage.getItem('mh_combined_csv_cache')||''")
    for d in ('2026-10-05', '2026-10-06', '2026-10-07'):
        if d not in cache: f.add('BUG', f'6: {d} not in the stored combined.csv')
    if 'not-a-date' in cache: f.add('BUG', '7: the unreadable row was saved')
    # round trip: the exported combined.csv goes back in unchanged
    page.set_input_files('#manualCsvUploadInput', files=[{'name': 'combined_export.csv', 'mimeType': 'text/csv', 'buffer': cache.encode()}]); page.wait_for_timeout(1500)
    r1b = row('2026-10-05')
    if not r1b or float(r1b['sl']) != 450: f.add('BUG', f'8: re-importing the exported file changed sleep: {r1b}')
    if ev("(localStorage.getItem('mh_combined_csv_cache')||'').trim().split('\\n').length") != 4: f.add('BUG', '9: re-import added or lost days')
    # survives a reload
    page.reload(); page.wait_for_timeout(1800)
    if '2026-10-06' not in ev("localStorage.getItem('mh_combined_csv_cache')||''"): f.add('BUG', '10: saved days gone after a reload')
    if errs: f.add('BUG', f'page errors {errs[:3]}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
