"""Persona 422: undo for a CSV upload made WITH the server running (v3.10.1320). Pete 6 Nov: "yes please" to server-mode undo.
Real server.py on a temporary copy with invented data. Covers: upload A then B (overlapping one day, adding one), undo B puts the overlapping day back in the manual entries, combined.csv and
field attribution, removes the day B added, leaves A's other day alone, writes safety copies, clears the record, hides the button; the app's own history matches; a day whose manual value was changed
after the upload is left alone and counted; undo with nothing to undo is refused cleanly; no page errors."""
import sys, re, csv, json, glob; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
U = 'http://localhost:5757'
f = Findings(); chk = lambda ok, msg: None if ok else f.add('BUG', msg)
A = b"date,weight,steps\n2026-10-05,84.2,6100\n2026-10-06,83.9,7000\n"
B = b"date,weight,steps\n2026-10-05,70.0,100\n2026-10-08,82.0,5000\n"
C = b"date,weight,steps\n2026-10-09,81.0,300\n2026-10-10,80.5,400\n"
def boot(b):
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block'); ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:160])); pg.goto(U + '/'); pg.wait_for_timeout(1200); return pg, errs
def onboard(pg):
    pg.evaluate("onboardNext(2)"); pg.fill('#onboardName', 'Test'); pg.evaluate("onboardNext(3)")
    pg.evaluate("obSetSex('female')"); pg.fill('#onboardAge', '40'); pg.fill('#onboardHeight', '165')
    pg.fill('#onboardWeight', '70'); pg.fill('#onboardTarget', '65')
    pg.evaluate("onboardNext(4)"); pg.evaluate("obSetActivity('light')"); pg.evaluate("obSetGoal('lose')")
    pg.evaluate("onboardNext(5)"); pg.evaluate("obSetCondition('general')")
    pg.evaluate("onboardNext(6)"); pg.evaluate("onboardFinish()"); pg.wait_for_timeout(1200)
def goto_manual(pg):
    pg.click("[onclick^=\"switchTab('settings'\"]"); pg.click("[onclick^=\"switchSubTab('settings','import'\"]"); pg.wait_for_timeout(400)
def upload_csv(pg, root, name, content):
    p = os.path.join(root, name); open(p, 'wb').write(content)
    pg.set_input_files('#manualCsvUploadInput', p); pg.wait_for_timeout(500)
    for _ in range(180):
        t = pg.inner_text('#manualEntryOutput')
        if t[:1] in '✓✗': break
        pg.wait_for_timeout(500)
    pg.wait_for_timeout(1200); return pg.inner_text('#manualEntryOutput')
with fresh_server() as root, sync_playwright() as pw:
    comb = lambda: {r['date']: r for r in csv.DictReader(open(os.path.join(root, 'data', 'tables', 'combined.csv'), encoding='utf-8'))} if os.path.exists(os.path.join(root, 'data', 'tables', 'combined.csv')) else {}
    man = lambda: {e['date']: e for e in json.load(open(os.path.join(root, 'data', 'inbox', 'manual_entry.json')))} if os.path.exists(os.path.join(root, 'data', 'inbox', 'manual_entry.json')) else {}
    srcs = lambda: json.load(open(os.path.join(root, 'data', 'field_sources.json'))) if os.path.exists(os.path.join(root, 'data', 'field_sources.json')) else {}
    w = lambda d: float(comb()[d]['weight']) if d in comb() and comb()[d].get('weight') else None
    undo_row = lambda: pg.evaluate("(()=>{const e=document.getElementById('manualCsvUndoRow'); return e&&getComputedStyle(e).display!=='none'?e.textContent.trim():''})()")
    hist = lambda d: pg.evaluate(f"(()=>{{const h=state.history.find(x=>mhCsvIso(x)==='{d}'); return h?String(h.weight):null}})()")
    b = pw.chromium.launch(); pg, errs = boot(b); onboard(pg); goto_manual(pg)
    r = pg.evaluate("fetch('/undo-manual-bulk',{method:'POST',body:'{}'}).then(r=>r.status)")
    chk(r == 404, f'1: undo with nothing to undo returned {r}, expected 404')
    t = upload_csv(pg, root, 'a.csv', A); chk('Uploaded 2 day' in t, f'2: upload A said: {t}')
    chk(w('2026-10-05') == 84.2 and w('2026-10-06') == 83.9, f'3: combined after A: {w("2026-10-05")} {w("2026-10-06")}')
    pre_sources = json.dumps(srcs().get('2026-10-05'), sort_keys=True)
    t = upload_csv(pg, root, 'b.csv', B); chk('Uploaded 2 day' in t, f'4: upload B said: {t}')
    chk(w('2026-10-05') == 70.0 and w('2026-10-08') == 82.0, f'5: combined after B: {w("2026-10-05")} {w("2026-10-08")}')
    chk('2 days' in undo_row(), f'6: undo row after B: "{undo_row()}"')
    chk(os.path.exists(os.path.join(root, 'data', 'csv_upload_undo.json')), '7: no undo record on the server after B')
    pg.click('#manualCsvUndoRow button'); pg.wait_for_timeout(2500)
    chk(w('2026-10-05') == 84.2, f'8: undo did not put day 1 back in combined.csv: {w("2026-10-05")}')
    chk('2026-10-08' not in comb(), '9: undo left the day B added in combined.csv')
    chk(w('2026-10-06') == 83.9, f'10: undo touched upload A\'s other day: {w("2026-10-06")}')
    m = man(); chk(float(m.get('2026-10-05', {}).get('weight', 0)) == 84.2, f'11: manual entry for day 1 is {m.get("2026-10-05")}')
    chk('2026-10-08' not in m, '12: manual entry for the added day not removed')
    chk('2026-10-06' in m, '13: manual entry for upload A\'s other day lost')
    chk(json.dumps(srcs().get('2026-10-05'), sort_keys=True) == pre_sources, f'14: field attribution for day 1 is {srcs().get("2026-10-05")}, was {pre_sources}')
    chk(not os.path.exists(os.path.join(root, 'data', 'csv_upload_undo.json')), '15: undo record still there after use')
    chk(len(glob.glob(os.path.join(root, 'data', 'backup', 'undo', '*_pre_undo_combined.csv'))) == 1, '16: no safety copy of combined.csv before the undo')
    chk(not undo_row(), f'17: undo button still showing: "{undo_row()}"')
    chk(hist('2026-10-05') in ('84.2',) and hist('2026-10-08') is None, f'18: the app history after undo: {hist("2026-10-05")} / {hist("2026-10-08")}')
    # changed since: hand-change a manual value after upload C, then undo
    t = upload_csv(pg, root, 'c.csv', C); chk('Uploaded 2 day' in t, f'19: upload C said: {t}')
    mp = os.path.join(root, 'data', 'inbox', 'manual_entry.json'); es = json.load(open(mp))
    for e in es:
        if e['date'] == '2026-10-09': e['weight'] = 99.0
    json.dump(es, open(mp, 'w'))
    pg.click('#manualCsvUndoRow button'); pg.wait_for_timeout(2500)
    chk('2026-10-10' not in comb(), '20: the untouched uploaded day was not removed')
    chk('2026-10-09' in man() and float(man()['2026-10-09']['weight']) == 99.0, f'21: the day changed since the upload was not left alone: {man().get("2026-10-09")}')
    out = pg.inner_text('#manualEntryOutput'); chk('1 day' in out and 'changed since' in out, f'22: result message: {out}')
    if errs: f.add('BUG', f'page errors {errs[:3]}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
