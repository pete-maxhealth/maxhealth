"""Persona 86: RingConn sessions are grouped into nights (gap under 2 h joins) and filed under the WAKE date; a daytime short session is a nap; a nap-only day has no night (so it cannot outrank Zepp); Withings does not claim RingConn's zip. Uses the real 10-11 Oct 2026 pattern."""
import sys, os, io, csv, zipfile; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
f = Findings()
H = ['Start Time', 'End Time', 'Time Asleep(min)', 'Sleep Stages - Awake(min)', 'Sleep Stages - REM(min)', 'Sleep Stages - Light Sleep(min)', 'Sleep Stages - Deep Sleep(min)']
def mk(header, rows):
    s = io.StringIO(); w = csv.writer(s); w.writerow(header); [w.writerow(r) for r in rows]; return s.getvalue()
sessions = [
    ['2026-10-10 04:51:11', '2026-10-10 08:18:41', 180, 15, 35, 95, 50],    # tail of the night before (wake 10th)
    ['2026-10-10 22:18:01', '2026-10-11 04:25:31', 335, 10, 105, 145, 85],  # night begins
    ['2026-10-11 05:30:34', '2026-10-11 08:18:04', 127, 23, 20, 82, 25],    # same night, 65 min later: joined
    ['2026-10-12 11:00:00', '2026-10-12 13:30:00', 127, 23, 20, 82, 25],    # daytime nap only
]
with fresh_server() as root:
    act = mk(['Date', 'Steps', 'Calories(kcal)'], [[d, 5000, 200] for d in ('2026-10-10', '2026-10-11', '2026-10-12')])
    vit = mk(['Date', 'Avg. Heart Rate(bpm)', 'Min. Heart Rate(bpm)', 'Max. Heart Rate(bpm)', 'Avg. HRV(ms)', 'Avg. Spo2(%)'], [[d, 60, 50, 90, 40, 96] for d in ('2026-10-10', '2026-10-11', '2026-10-12')])
    with zipfile.ZipFile(os.path.join(root, 'data', 'inbox', 'Data Export-Test-2026-10-10-2026-10-12.zip'), 'w') as z:
        z.writestr('Activity-Test-1.csv', act); z.writestr('Sleep-Test-1.csv', mk(H, sessions)); z.writestr('Vital Signs-Test-1.csv', vit)
    rc, out = run_pipeline(root)
    if rc != 0: f.add('BUG', f'pipeline failed: {out[-300:]}')
    c = read_combined(root)
    g = lambda d, k: (c.get(d) or {}).get(k, '')
    if g('2026-10-10', 'sleep_duration') != '180': f.add('BUG', f"10 Oct (the earlier night's tail) should be 180, got {g('2026-10-10','sleep_duration')}")
    if g('2026-10-11', 'sleep_duration') != '462': f.add('BUG', f"11 Oct night should join to 462, got {g('2026-10-11','sleep_duration')}")
    if g('2026-10-11', 'sleep_deep') != '110' or g('2026-10-11', 'sleep_rem') != '125': f.add('BUG', f"joined stages wrong deep={g('2026-10-11','sleep_deep')} rem={g('2026-10-11','sleep_rem')}")
    if g('2026-10-11', 'sleep_nap_min') not in ('', None): f.add('BUG', 'a broken night must not also be a nap')
    if g('2026-10-12', 'sleep_duration') not in ('', None): f.add('BUG', f"nap-only day must have no night, got {g('2026-10-12','sleep_duration')}")
    if g('2026-10-12', 'sleep_nap_min') != '127': f.add('BUG', f"nap should be 127, got {g('2026-10-12','sleep_nap_min')}")
print('findings', len(f)); sys.exit(1 if f else 0)
