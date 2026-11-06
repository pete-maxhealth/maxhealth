"""Persona 421: undo for a CSV upload saved in the browser (no server), v3.10.1319. Pete 6 Nov: PC list item "bulk undo for CSV upload".
Covers: after an upload the Undo row shows with the day count and the toast offers Undo; undoing removes new days and puts overlapping days back as they were, in the history and the stored CSV;
a second upload no longer clobbers the stored CSV with just its own rows (found while building this); a day edited after the upload is left alone and reported; the row survives a reload,
disappears once used, and a second undo does nothing; the button looks like its neighbours (same class) in light and dark; no page errors. Invented data, fresh (non-demo) browser."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
A = "date,weight,steps\n2026-10-05,84.2,6100\n2026-10-06,83.9,7000\n"
B = "date,weight,steps\n2026-10-05,70.0,100\n2026-10-08,82.0,5000\n"
C = "date,weight\n2026-10-09,81.0\n2026-10-10,80.5\n"
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 1280, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.dismiss()); ev = page.evaluate
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay').style.display='none'"); ev("switchTabById('import')"); page.wait_for_timeout(900)
    ev("_serverOnline = false")
    up = lambda name, txt: (page.set_input_files('#manualCsvUploadInput', files=[{'name': name, 'mimeType': 'text/csv', 'buffer': txt.encode()}]), page.wait_for_timeout(1400))
    row = lambda d: ev(f"(()=>{{const r=mhCloudHistoryRow('{d}'); return r?{{w:r.weight,s:r.steps}}:null}})()")
    cache = lambda: ev("localStorage.getItem('mh_combined_csv_cache')||''")
    undo_row = lambda: ev("(()=>{const e=document.getElementById('manualCsvUndoRow'); return e&&getComputedStyle(e).display!=='none'?e.textContent.trim():''})()")
    ncache = lambda: len([l for l in cache().strip().split('\n') if l]) - 1
    if undo_row(): f.add('BUG', '1: undo row shown before any upload')
    up('a.csv', A)
    if '2 days' not in undo_row(): f.add('BUG', f'2: undo row after upload A: "{undo_row()}"')
    if 'Undo' not in ev("document.querySelector('.toast, #toast, [class*=toast]')?.textContent||''"): f.add('BUG', '3: the toast has no Undo')
    ev("mhCsvUndo()"); page.wait_for_timeout(500)
    if row('2026-10-05') or row('2026-10-06'): f.add('BUG', f'4: undo of the first upload left days behind: {row("2026-10-05")} {row("2026-10-06")}')
    if ncache() != 0: f.add('BUG', f'5: stored CSV still has {ncache()} rows after undoing everything')
    if undo_row(): f.add('BUG', '6: undo row still showing after it was used')
    ev("mhCsvUndo()"); page.wait_for_timeout(300)   # nothing to undo: no error
    # upload A, then B overlapping one day and adding one
    up('a.csv', A); up('b.csv', B)
    if ncache() != 3: f.add('BUG', f'7: after two uploads the stored CSV has {ncache()} days, expected 3 (it is only keeping the last upload\'s rows)')
    if not row('2026-10-05') or float(row('2026-10-05')['w']) != 70.0: f.add('BUG', f'8: B did not overwrite day 1: {row("2026-10-05")}')
    if '2 days' not in undo_row(): f.add('BUG', f'9: undo row after B: "{undo_row()}"')
    ev("mhCsvUndo()"); page.wait_for_timeout(500)
    r = row('2026-10-05')
    if not r or float(r['w']) != 84.2 or float(r['s']) != 6100: f.add('BUG', f'10: undo of B did not put day 1 back: {r}')
    if row('2026-10-08'): f.add('BUG', '11: undo of B left its new day 2026-10-08')
    if not row('2026-10-06'): f.add('BUG', '12: undo of B removed a day from upload A')
    c = cache()
    if '2026-10-08' in c or '84.2' not in c or '70.0' in c: f.add('BUG', f'13: stored CSV after undoing B: {c!r}')
    # a day edited after the upload is left alone
    up('c.csv', C)
    ev("(()=>{const h=state.history.find(x=>mhCsvIso(x)==='2026-10-09'); h.weight=99; saveState()})()")
    ev("mhCsvUndo()"); page.wait_for_timeout(500)
    if not row('2026-10-09') or float(row('2026-10-09')['w']) != 99: f.add('BUG', f'14: a day edited since the upload was not left alone: {row("2026-10-09")}')
    if row('2026-10-10'): f.add('BUG', '15: the untouched uploaded day was not removed')
    msg = ev("(document.getElementById('manualEntryOutput')||{}).textContent||''")
    if '1 day' not in msg or 'changed since' not in msg: f.add('BUG', f'16: result message: {msg}')
    # survives a reload
    up('c.csv', C); page.reload(); page.wait_for_timeout(1800)
    ev("document.getElementById('onboardingOverlay').style.display='none'"); ev("switchTabById('import')"); page.wait_for_timeout(900)
    ev("loadManualEntryForDate(new Date().toISOString().slice(0,10))"); page.wait_for_timeout(500)
    if '2 days' not in undo_row(): f.add('BUG', f'17: undo row after a reload: "{undo_row()}"')
    # looks like its neighbours, both themes
    cls = ev("[document.querySelector('#manualCsvUndoRow button').className, document.querySelector('button[onclick=\"triggerManualCsvUpload()\"]').className]")
    if cls[0] != cls[1]: f.add('BUG', f'18: undo button class {cls[0]} vs neighbour {cls[1]}')
    for th in ('light', 'dark'):
        ev(f"document.documentElement.setAttribute('data-theme','{th}')"); page.wait_for_timeout(300)
        page.locator('#manualCsvUndoRow').scroll_into_view_if_needed(); page.locator('#manualCsvUploadInput').locator('xpath=..').screenshot(path=f'/tmp/claude-0/p421_{th}.png')
    if errs: f.add('BUG', f'page errors {errs[:3]}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
