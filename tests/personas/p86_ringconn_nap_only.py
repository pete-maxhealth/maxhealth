"""Persona 86: a RingConn day holding only a daytime nap must not become that day's night (it would outrank and wipe Zepp's real night); the nap goes to sleep_nap_min."""
import sys, os, io, csv, zipfile; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
f = Findings()
H = ['Start Time', 'End Time', 'Time Asleep(min)', 'Sleep Stages - Awake(min)', 'Sleep Stages - REM(min)', 'Sleep Stages - Light Sleep(min)', 'Sleep Stages - Deep Sleep(min)']
def mk(header, rows):
    s = io.StringIO(); w = csv.writer(s); w.writerow(header); [w.writerow(r) for r in rows]; return s.getvalue()
sessions = [
    ['2026-09-06 22:35:00', '2026-09-07 06:40:00', 440, 20, 90, 250, 80],   # the night, filed under its bedtime date
    ['2026-09-07 11:00:00', '2026-09-07 13:30:00', 127, 23, 20, 82, 25],     # next day: ONLY a nap
]
with fresh_server() as root:
    act = mk(['Date', 'Steps', 'Calories(kcal)'], [['2026-09-06', 5000, 200], ['2026-09-07', 3000, 100]])
    slp = mk(H, sessions)
    with zipfile.ZipFile(os.path.join(root, 'data', 'inbox', 'Data Export-Test-2026-09-06-2026-09-07.zip'), 'w') as z:
        z.writestr('Activity-Test-1.csv', act); z.writestr('Sleep-Test-1.csv', slp)
        z.writestr('Vital Signs-Test-1.csv', mk(['Date', 'Avg. Heart Rate(bpm)', 'Min. Heart Rate(bpm)', 'Max. Heart Rate(bpm)', 'Avg. HRV(ms)', 'Avg. Spo2(%)'], [[d, 60, 50, 90, 40, 96] for d in ['2026-09-06', '2026-09-07']]))
    rc, out = run_pipeline(root)
    if rc != 0: f.add('BUG', f'pipeline failed: {out[-300:]}')
    c = read_combined(root)
    g = lambda d, k: (c.get(d) or {}).get(k, '')
    if g('2026-09-06', 'sleep_duration') != '440': f.add('BUG', f"night wrong: {g('2026-09-06','sleep_duration')}")
    if g('2026-09-07', 'sleep_duration') not in ('', None): f.add('BUG', f"nap-only day must have no night, got {g('2026-09-07','sleep_duration')}")
    if g('2026-09-07', 'sleep_nap_min') != '127': f.add('BUG', f"nap should be 127, got {g('2026-09-07','sleep_nap_min')}")
print('findings', len(f)); sys.exit(1 if f else 0)
