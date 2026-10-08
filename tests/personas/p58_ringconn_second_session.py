"""Persona 58: RingConn second sleep session under one date: a broken night is added to the night, a far-away short session is a nap (own field), a long second session is ignored as before."""
import sys, os, io, csv, zipfile; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
f = Findings()
H = ['Start Time', 'End Time', 'Time Asleep(min)', 'Sleep Stages - Awake(min)', 'Sleep Stages - REM(min)', 'Sleep Stages - Light Sleep(min)', 'Sleep Stages - Deep Sleep(min)']
def mk(header, rows):
    s = io.StringIO(); w = csv.writer(s); w.writerow(header); [w.writerow(r) for r in rows]; return s.getvalue()
sessions = [
    # 2026-09-01: plain single night
    ['2026-09-01 00:30:00', '2026-09-01 06:30:00', 350, 10, 80, 200, 70],
    # 2026-09-02: broken night - main 00:30-05:00, woke, slept again 05:40-07:00 (gap 40 min): joined
    ['2026-09-02 00:30:00', '2026-09-02 05:00:00', 260, 10, 60, 150, 50],
    ['2026-09-02 05:40:00', '2026-09-02 07:00:00', 70, 10, 15, 40, 15],
    # 2026-09-03: night plus an afternoon nap 14:00-15:00 (hours away): nap
    ['2026-09-03 00:30:00', '2026-09-03 06:30:00', 350, 10, 80, 200, 70],
    ['2026-09-03 14:00:00', '2026-09-03 15:00:00', 55, 5, 5, 40, 10],
    # 2026-09-04: a second LONG session (a different night under the same date label): ignored, longest kept, no nap
    ['2026-09-04 00:10:00', '2026-09-04 05:00:00', 280, 10, 60, 160, 60],
    ['2026-09-04 23:10:00', '2026-09-05 06:00:00', 400, 10, 90, 230, 80],
]
with fresh_server() as root:
    days_ = ['2026-09-01', '2026-09-02', '2026-09-03', '2026-09-04']
    act = mk(['Date', 'Steps', 'Calories(kcal)'], [[d, 5000, 200] for d in days_])
    slp = mk(H, sessions)
    vit = mk(['Date', 'Avg. Heart Rate(bpm)', 'Min. Heart Rate(bpm)', 'Max. Heart Rate(bpm)', 'Avg. HRV(ms)', 'Avg. Spo2(%)'], [[d, 60, 50, 90, 40, 96] for d in days_])
    with zipfile.ZipFile(os.path.join(root, 'data', 'inbox', 'Data Export-Test-2026-09-01-2026-09-04.zip'), 'w') as z:
        z.writestr('Activity-Test-1.csv', act); z.writestr('Sleep-Test-1.csv', slp); z.writestr('Vital Signs-Test-1.csv', vit)
    rc, out = run_pipeline(root)
    if rc != 0: f.add('BUG', f'pipeline failed: {out[-300:]}')
    c = read_combined(root)
    g = lambda d, k: (c.get(d) or {}).get(k, '')
    if g('2026-09-01', 'sleep_duration') != '350' or g('2026-09-01', 'sleep_nap_min') not in ('', None): f.add('BUG', f"plain night wrong: {g('2026-09-01','sleep_duration')} nap={g('2026-09-01','sleep_nap_min')}")
    if g('2026-09-02', 'sleep_duration') != '330': f.add('BUG', f"broken night should join to 330, got {g('2026-09-02','sleep_duration')}")
    if g('2026-09-02', 'sleep_deep') != '65' or g('2026-09-02', 'sleep_rem') != '75': f.add('BUG', f"joined stages wrong: deep={g('2026-09-02','sleep_deep')} rem={g('2026-09-02','sleep_rem')}")
    if g('2026-09-02', 'sleep_nap_min') not in ('', None): f.add('BUG', 'broken night must not also be a nap')
    if g('2026-09-03', 'sleep_duration') != '350' or g('2026-09-03', 'sleep_nap_min') != '55': f.add('BUG', f"nap day wrong: night={g('2026-09-03','sleep_duration')} nap={g('2026-09-03','sleep_nap_min')}")
    if g('2026-09-04', 'sleep_duration') != '400' or g('2026-09-04', 'sleep_nap_min') not in ('', None): f.add('BUG', f"long second session should leave the longest only: {g('2026-09-04','sleep_duration')} nap={g('2026-09-04','sleep_nap_min')}")
print('findings', len(f)); sys.exit(1 if f else 0)
