"""Persona 7: a Garmin-only user. Their Garmin Connect export (hash-named zip) lands in Downloads."""
import sys, zipfile; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
f = Findings()
ds = days(7)
uds = [dict(calendarDate=d + 'T00:00:00.0', totalSteps=8000 + i * 50, totalDistanceMeters=6200.0, activeKilocalories=410,
            restingHeartRate=55, minHeartRate=48, maxHeartRate=150) for i, d in enumerate(ds)]
sleep = [dict(calendarDate=d, deepSleepSeconds=3600, lightSleepSeconds=14400, remSleepSeconds=5400, awakeSleepSeconds=1200) for d in ds]

def build_zip(path):
    with zipfile.ZipFile(path, 'w') as z:
        z.writestr('DI_CONNECT/DI-Connect-Aggregator/UDSFile_2026-09-01_2026-10-01.json', json.dumps(uds))
        z.writestr('DI_CONNECT/DI-Connect-Wellness/2026-09-01_2026-10-01_1_sleepData.json', json.dumps(sleep))
        z.writestr('DI_CONNECT/DI-Connect-User/user_profile.json', '{}')

# A. the real flow: file in Downloads -> server moves it to inbox (must NOT be mistaken for a Zepp zip) -> pipeline
with fresh_server() as root:
    dl = os.path.join(root, 'Download'); os.makedirs(dl)
    build_zip(os.path.join(dl, '3f9c1d2e-aaaa-bbbb-cccc-0123456789ab.zip'))   # hash name starting with a digit
    r = subprocess.run([sys.executable, '-c', f"import server; server.DOWNLOAD={dl!r}; print(server.move_exports_to_inbox())"],
                       cwd=os.path.join(root, 'app'), capture_output=True, text=True, timeout=60)
    print('sweep:', r.stdout.strip()[-80:])
    if not os.path.exists(os.path.join(root, 'data', 'inbox', '3f9c1d2e-aaaa-bbbb-cccc-0123456789ab.zip')):
        f.add('BUG', 'Garmin export zip in Downloads was not moved to the inbox: ' + (r.stdout + r.stderr)[-200:])
    else:
        rc, out = run_pipeline(root)
        c = read_combined(root)
        print('garmin days in combined.csv:', len(c))
        if len(c) < 7: f.add('BUG', f'only {len(c)} Garmin days reached combined.csv; log: ' + out[-300:])
        for d, row in c.items():
            for fld, lo, hi in (('steps', 1000, 40000), ('sleep_duration', 300, 600), ('hr_resting', 30, 100), ('distance_m', 100, 100000)):
                v = row.get(fld, '')
                if v in ('', None) or not lo <= float(v) <= hi: f.add('BUG', f'{d}: {fld}={v!r}')
        d0 = ds[0]
        if c.get(d0) and round(float(c[d0].get('sleep_duration') or 0)) != 390: f.add('BUG', 'sleep should be deep+light+REM=390 min, got ' + str(c[d0].get('sleep_duration')))

# B. plain wellness JSON (unofficial Connect API schema) named garmin_*.json
with fresh_server() as root:
    day = [dict(calendarDate=d, steps=5000, distanceInMeters=3900.0, activeCalories=180, restingHeartRate=58) for d in ds[:3]]
    json.dump(day, open(os.path.join(root, 'data', 'inbox', 'garmin_wellness.json'), 'w'))
    rc, out = run_pipeline(root); c = read_combined(root)
    if len(c) != 3: f.add('BUG', f'garmin json: {len(c)} rows, expected 3')

# C. garbage inside a Garmin zip must not crash the pipeline
with fresh_server() as root:
    with zipfile.ZipFile(os.path.join(root, 'data', 'inbox', '9abc.zip'), 'w') as z:
        z.writestr('DI_CONNECT/DI-Connect-Aggregator/UDSFile_x.json', '[{"calendarDate": null}, 5, "x", {"calendarDate":"2026-09-30T00:00:00.0","totalSteps":"abc"}]')
        z.writestr('DI_CONNECT/DI-Connect-Wellness/y_sleepData.json', 'not json at all')
    rc, out = run_pipeline(root)
    if rc or 'Traceback' in out: f.add('BUG', 'garbage Garmin zip crashed the pipeline: ' + out[-250:])
print('findings', len(f)); sys.exit(1 if f else 0)
