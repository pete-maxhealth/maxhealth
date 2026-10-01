"""Persona 12: manual entry - the typed form and the CSV template route (Excel-style files, UK dates,
European separators). What the person is told must match what actually reached combined.csv."""
import sys, re; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
U = 'http://localhost:5757'
f = Findings()
chk = lambda ok, msg: None if ok else f.add('BUG', msg)
ds = days(10); D0, D1, D2 = ds[-1], ds[-2], ds[-3]
def boot(b):
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:160]))
    pg.goto(U + '/'); pg.wait_for_timeout(1200); return pg, errs
def onboard(pg):
    pg.evaluate("onboardNext(2)"); pg.fill('#onboardName', 'Test'); pg.evaluate("onboardNext(3)")
    pg.evaluate("obSetSex('female')"); pg.fill('#onboardAge', '40'); pg.fill('#onboardHeight', '165')
    pg.fill('#onboardWeight', '70'); pg.fill('#onboardTarget', '65')
    pg.evaluate("onboardNext(4)"); pg.evaluate("obSetActivity('light')"); pg.evaluate("obSetGoal('lose')")
    pg.evaluate("onboardNext(5)"); pg.evaluate("obSetCondition('general')")
    pg.evaluate("onboardNext(6)"); pg.evaluate("onboardFinish()"); pg.wait_for_timeout(1200)
def goto_manual(pg):
    pg.click("[onclick^=\"switchTab('settings'\"]"); pg.click("[onclick^=\"switchSubTab('settings','import'\"]"); pg.wait_for_timeout(400)
def wait_pipeline(pg, secs=20):
    for _ in range(secs * 2):
        if not pg.evaluate("fetch('/status').then(r=>r.json()).then(d=>d.running)"): return
        pg.wait_for_timeout(500)
def upload_csv(pg, root, name, content_bytes):
    p = os.path.join(root, name); open(p, 'wb').write(content_bytes)
    pg.set_input_files('#manualCsvUploadInput', p); pg.wait_for_timeout(500)
    for _ in range(180):
        t = pg.inner_text('#manualEntryOutput')
        if t[:1] in '✓✗': break
        pg.wait_for_timeout(500)
    pg.wait_for_timeout(800)
    return pg.inner_text('#manualEntryOutput')

with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); pg, errs = boot(b); onboard(pg); goto_manual(pg)
    # --- typed entry, like a person: pick a date, type weight and sleep in hours
    pg.evaluate("document.getElementById('manualEntryDate').value='%s'" % D0)
    pg.evaluate("loadManualEntryForDate('%s')" % D0); pg.wait_for_timeout(700)
    fields = pg.evaluate("_manualTemplateFields")
    print('template fields:', fields[:8])
    chk('weight' in fields, 'default manual template has no weight field')
    # saving with nothing typed must not write anything
    pg.evaluate("saveManualEntry()"); pg.wait_for_timeout(400)
    chk(not os.path.exists(os.path.join(root, 'data', 'inbox', 'manual_entry.json')), 'saving an untouched form wrote a manual entry')
    for key, val in (('weight', '71.4'), ('sleep_duration', '7.5'), ('steps', '8123')):
        if key in fields: pg.fill(f'#manualField_{key}', val)
    pg.evaluate("saveManualEntry()"); pg.wait_for_timeout(500); wait_pipeline(pg); pg.wait_for_timeout(1200)
    c = read_combined(root)
    chk(D0 in c and abs(float(c[D0].get('weight') or 0) - 71.4) < 0.01, f'typed weight did not reach combined.csv: {c.get(D0)}')
    if 'sleep_duration' in fields: chk(c.get(D0, {}).get('sleep_duration') in ('450', '450.0'), f'7.5h sleep stored as {c.get(D0, {}).get("sleep_duration")} (want 450 min)')
    chk(c.get(D0, {}).get('source') == 'manual', f'source should be manual, got {c.get(D0, {}).get("source")}')
    shown = pg.evaluate("state.history.find(h => /%s/.test(JSON.stringify(h.date))) ? 1 : 0" % D0[-2:]) if False else None
    # out-of-range value must be refused without losing the rest
    pg.evaluate("document.getElementById('manualEntryDate').value='%s'" % D1); pg.evaluate("loadManualEntryForDate('%s')" % D1); pg.wait_for_timeout(500)
    pg.fill('#manualField_weight', '700'); pg.fill('#manualField_steps', '5000')
    pg.evaluate("saveManualEntry()"); pg.wait_for_timeout(500); wait_pipeline(pg); pg.wait_for_timeout(1000)
    c = read_combined(root)
    chk(D1 in c and c[D1].get('steps') in ('5000', '5000.0'), f'valid field lost when another was out of range: {c.get(D1)}')
    chk(not c.get(D1, {}).get('weight') or float(c[D1]['weight']) < 400, 'a 700 kg weight was accepted into combined.csv')
    msg = pg.inner_text('#manualEntryOutput')
    chk('NOT saved' in msg and 'weight' in msg, f'person was not told the 700 kg weight was refused: {msg[:140]!r}')
    # future date
    pg.evaluate("document.getElementById('manualEntryDate').value='2031-01-01'"); pg.evaluate("loadManualEntryForDate('2031-01-01')"); pg.wait_for_timeout(400)
    pg.fill('#manualField_steps', '4000'); pg.evaluate("saveManualEntry()"); pg.wait_for_timeout(500); wait_pipeline(pg)
    chk('2031-01-01' not in read_combined(root), 'a manual entry dated 2031 reached combined.csv')

    # --- CSV template route -------------------------------------------------
    hdr = 'date,weight,steps,sleep_duration'
    def uk(d): y, m, dd = d.split('-'); return f'{dd}/{m}/{y}'
    cases = {
      'plain':      ('\n'.join([hdr, f'{ds[0]},70.1,6001,7.0', f'{ds[1]},70.2,6002,6.5']).encode(), [ds[0], ds[1]]),
      'excel_bom_crlf': (('\ufeff' + '\r\n'.join([hdr, f'{ds[2]},70.3,6003,7.0']) + '\r\n').encode('utf-8'), [ds[2]]),
      'caps_header_spaces': ('\n'.join(['Date, Weight , Steps', f'{ds[3]}, 70.4 , 6004']).encode(), [ds[3]]),
      'uk_dates':   ('\n'.join([hdr, f'{uk(ds[4])},70.5,6005,7.0']).encode(), [ds[4]]),
      'semicolons': ('\n'.join(['date;weight;steps', f'{ds[5]};70,6;6006']).encode(), [ds[5]]),
      'thousands':  ('\n'.join([hdr, f'{ds[6]},70.7,"6,007",7.0']).encode(), [ds[6]]),
      'bad_date_tells_user': ('\n'.join([hdr, '31/02/2026,70,5000,7']).encode(), []),
      'blank_and_junk_rows': ('\n'.join([hdr, ',,,', f'{ds[7]},,,', f'{ds[8]},abc,6008,', 'not a row at all']).encode(), [ds[8]]),
    }
    for name, (content, want) in cases.items():
        pg3, e3 = boot(b); onboard(pg3); goto_manual(pg3)
        out = upload_csv(pg3, root, f'{name}.csv', content)
        comb = read_combined(root); got = set(comb)
        ok = all(d in comb and (comb[d].get('steps') or comb[d].get('weight')) for d in want)
        print(f'  csv {name:20s} -> {"OK" if ok else "MISSING"}  | {out[:90]!r}')
        if name == 'bad_date_tells_user':
            chk("couldn't read the date" in out or 'No usable rows' in out, f'bad date gave no clear message: {out[:120]!r}'); continue
        if not ok:
            f.add('BUG', f'CSV "{name}": expected {want} in combined.csv, got {sorted(got)}; person was told: {out[:120]!r}')
        elif name == 'thousands':
            row = comb.get(ds[6], {}); chk(row.get('steps') in ('6007', '6007.0'), f'"6,007" steps stored as {row.get("steps")}')
        elif name == 'semicolons':
            row = comb.get(ds[5], {}); chk(row.get('weight') in ('70.6',), f'"70,6" kg stored as {row.get("weight")}')
        elif name == 'uk_dates':
            row = comb.get(ds[4], {}); chk(row.get('steps') in ('6005', '6005.0'), f'UK-date row stored as {row}')
        errs += e3
    # a year-plus of daily data (Apple Health style export) in one go
    big = '\n'.join([hdr] + [f'{d},70,5000,7' for d in days(500)])
    pg4, e4 = boot(b); onboard(pg4); goto_manual(pg4)
    out = upload_csv(pg4, root, 'big.csv', big.encode())
    n = len(read_combined(root))
    print('  500-row csv ->', n, 'rows in combined |', out[:100])
    chk(n >= 480, f'a 500-day CSV imported only {n} rows; person was told: {out[:120]!r}')
    chk(not errs, f'JS errors: {errs}')
    b.close()
print('findings', len(f)); sys.exit(1 if any(s == 'BUG' for s, _ in f) else 0)
