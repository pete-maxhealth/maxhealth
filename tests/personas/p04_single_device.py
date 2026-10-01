"""Persona 4: people with exactly ONE device, syncing a week of data through the real pipeline."""
import sys; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
f = Findings()

def check(label, rows, expect):  # expect: {field: (lo, hi)} applied to every day
    if len(rows) < 7: f.add('BUG', f'{label}: only {len(rows)} days in combined.csv (expected 7)')
    for d, r in rows.items():
        for fld, (lo, hi) in expect.items():
            v = r.get(fld, '')
            if v in ('', None): f.add('BUG', f'{label} {d}: {fld} missing'); continue
            if not lo <= float(v) <= hi: f.add('BUG', f'{label} {d}: {fld}={v} outside {lo}-{hi}')

# --- Health Connect only (e.g. a Samsung/Pixel phone, no ring) ---
with fresh_server() as root:
    write_hc_export(root, [dict(date=d, steps=6000+i*100, distance_m=4500, calories_active=300, sleep_duration=420+i,
        sleep_deep=70, sleep_light=250, sleep_rem=90, sleep_wake=20, hr_avg=70, hr_resting=58, hrv=45, spo2=96, weight=80.5)
        for i, d in enumerate(days(7))])
    rc, out = run_pipeline(root)
    print('HC-only pipeline rc', rc)
    if rc: f.add('BUG', 'HC-only pipeline failed: ' + out[-300:])
    check('HC-only', read_combined(root), dict(steps=(1000, 30000), sleep_duration=(300, 600), hr_avg=(40, 120), weight=(40, 200)))
    if 'health_connect | extract  | warn' in out or 'No extractor found' in out: f.add('BUG', 'HC-only: extractor warning: ' + [l for l in out.splitlines() if 'No extractor' in l][0][-110:])

# --- RingConn only, on a FRESH install (no app/extractors folder outside the repo) ---
with fresh_server() as root:
    write_ringconn_zip(root, {d: dict(steps=7000, kcal=320, sleep_min=383, deep=60, light=240, rem=70, awake=25, hr=62, hrmin=48, hrmax=110, hrv=48, spo2=96.5)
                              for d in days(7)})
    rc, out = run_pipeline(root)
    print('RingConn-only pipeline rc', rc)
    if 'No extractor found' in out: f.add('BUG', 'RingConn-only: extractor warning: ' + [l for l in out.splitlines() if 'No extractor' in l][0][-110:])
    check('RingConn-only', read_combined(root), dict(steps=(1000, 30000), sleep_duration=(300, 600), hrv=(10, 200), spo2=(80, 100)))

print('findings', len(f)); sys.exit(1 if f else 0)
