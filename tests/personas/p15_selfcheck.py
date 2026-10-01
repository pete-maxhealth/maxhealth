"""Persona 15: the self-check. A healthy install reads 'Nothing to worry about'; seeded faults are named;
a real JS error in the page ends up in error_log.json (deduplicated) and the Settings line."""
import sys, re, urllib.request; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright
U = 'http://localhost:5757'
f = Findings()
chk = lambda ok, msg: None if ok else f.add('BUG', msg)
def get(p): return json.loads(urllib.request.urlopen(U + p, timeout=15).read())
def post(p, b): return json.loads(urllib.request.urlopen(urllib.request.Request(U + p, json.dumps(b).encode(), {'Content-Type': 'application/json'}), timeout=10).read())

with fresh_server() as root, sync_playwright() as pw:
    # A. healthy install with fresh data and a backup
    write_hc_export(root, [dict(date=d, steps=6000, sleep_duration=420, hr_avg=65, weight=80.0) for d in days(10)])
    run_pipeline(root); run_pipeline(root)
    r = get('/selfcheck')
    print('healthy:', r['status'], r['headline'], [i['text'][:60] for i in r['items']])
    chk(r['status'] == 'green', f'healthy install not green: {r["items"]}')
    chk(r['combined']['rows'] == 10, f'wrong row count {r["combined"]}')
    # B. seeded faults
    cp = os.path.join(root, 'data', 'tables', 'combined.csv')
    txt = open(cp).read().splitlines(); hdr = txt[0].split(',')
    wi = hdr.index('weight'); row = txt[1].split(','); row[wi] = 'abc'; txt.append(','.join(txt[2].split(',')))   # non-numeric weight + a duplicate date
    txt[1] = ','.join(row); open(cp, 'w').write('\n'.join(txt) + '\n')
    r = get('/selfcheck'); chk(r['status'] == 'red' and any('integrity' in i['text'] for i in r['items']), f'corruption not flagged red: {r["status"]} {r["items"]}')
    old = (datetime.now() - timedelta(days=12)).strftime('%Y-%m-%d %H:%M:%S') if False else None
    # C. a real JS error in the page is recorded once per signature, counted, and shown in Settings
    b = pw.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    pg = ctx.new_page(); pg.goto(U + '/'); pg.wait_for_timeout(1500)
    for _ in range(3): pg.evaluate("setTimeout(() => { throw new Error('boom test error 123456789') }, 0)"); pg.wait_for_timeout(300)
    pg.evaluate("setTimeout(() => Promise.reject(new Error('rejected test')), 0)"); pg.wait_for_timeout(600)
    log = json.load(open(os.path.join(root, 'data', 'error_log.json')))
    boom = [e for e in log if 'boom test error' in e['msg']]
    chk(len(boom) == 1 and boom[0]['count'] == 3, f'JS error not deduplicated/counted: {log}')
    chk(boom and '123456789' not in boom[0]['msg'], 'long number not redacted from the stored error message')
    chk(any('rejected test' in e['msg'] for e in log), 'unhandled promise rejection not recorded')
    r = get('/selfcheck'); chk(any('app error' in i['text'] for i in r['items']), f'app errors not in self-check: {r["items"]}')
    # D. the Settings line
    pg.evaluate("onboardNext(2)"); pg.fill('#onboardName', 'T'); pg.evaluate("onboardNext(3)"); pg.evaluate("obSetSex('male')"); pg.fill('#onboardAge', '40'); pg.fill('#onboardHeight', '178'); pg.fill('#onboardWeight', '80'); pg.fill('#onboardTarget', '75')
    pg.evaluate("onboardNext(4)"); pg.evaluate("obSetActivity('light')"); pg.evaluate("obSetGoal('lose')"); pg.evaluate("onboardNext(5)"); pg.evaluate("obSetCondition('general')"); pg.evaluate("onboardNext(6)"); pg.evaluate("onboardFinish()"); pg.wait_for_timeout(1200)
    pg.click("[onclick^=\"switchTab('settings'\"]"); pg.wait_for_timeout(800); pg.evaluate("initSettings()"); pg.wait_for_timeout(1500)
    t = pg.inner_text('#selfCheckDisplay'); print('settings line:', t.replace('\n', ' | ')[:120])
    chk(t and 'Checking' not in t and 'undefined' not in t, f'Settings system-health line: {t!r}')
    b.close()
    # E. errors are in the backup rotation
    write_hc_export(root, [dict(date=days(1)[0], steps=7777, sleep_duration=400, hr_avg=60, weight=79.0)]); run_pipeline(root)
    chk(any(x.startswith('error_log_') for x in os.listdir(os.path.join(root, 'data', 'backup'))), 'error_log.json not in backups')
print('findings', len(f)); sys.exit(1 if f else 0)
