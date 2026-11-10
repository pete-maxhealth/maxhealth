"""Persona 441 (v3.10.1340): a pipeline warning "Overlapping sleep sessions for <night>" stops showing in System health once that night
has been settled in the app (the launcher logs the overlap again on every sync, so Dismiss kept losing). Another night still shows."""
import sys, os, json, urllib.request; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from datetime import datetime, timedelta
U = 'http://localhost:5757'; f = Findings()
def get(p): return json.loads(urllib.request.urlopen(U + p, timeout=15).read())
def line(ts, msg): return f"{ts.strftime('%Y-%m-%d %H:%M:%S')} | health_connect | x | WARN | {msg}\n"
with fresh_server() as root:
    write_hc_export(root, [dict(date=d, steps=6000, sleep_duration=420, hr_avg=65, weight=80.0) for d in days(10)]); run_pipeline(root)
    log = os.path.join(root, 'logs', 'pipeline.log'); os.makedirs(os.path.dirname(log), exist_ok=True)
    with open(log, 'a') as fh:
        for i in range(9): fh.write(line(datetime.now() - timedelta(hours=1 + i), 'Overlapping sleep sessions for 2026-11-09, needs resolution'))
    pw = lambda: [i['text'] for i in get('/selfcheck')['items'] if 'Pipeline' in i['text']]
    if not pw(): f.add('BUG', '1: an unsettled night is reported')
    os.makedirs(os.path.join(root, 'data'), exist_ok=True)
    json.dump({'2026-11-09': 'x|2026-11-08T23:00|2026-11-09T06:00'}, open(os.path.join(root, 'data', 'sleep_conflicts_resolved.json'), 'w'))
    if pw(): f.add('BUG', f'2: the settled night still shows: {pw()}')
    with open(log, 'a') as fh: fh.write(line(datetime.now(), 'Overlapping sleep sessions for 2026-11-10, needs resolution'))
    got = pw()
    if len(got) != 1 or '2026-11-10' not in got[0]: f.add('BUG', f'3: a different, unsettled night still shows: {got}')
    with open(log, 'a') as fh: fh.write(line(datetime.now(), 'Some other pipeline warning'))
    if not any('other pipeline warning' in x for x in pw()): f.add('BUG', '4: other warnings are untouched')
print('findings', len(f)); [print(v) for v in f]; sys.exit(1 if f else 0)
