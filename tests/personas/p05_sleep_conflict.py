"""Persona 5: two devices disagree about sleep; then the person corrects it by hand."""
import sys, time, urllib.request; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
f = Findings()
D = days(2)[0]  # yesterday
def post(path, body):
    r = urllib.request.Request('http://localhost:5757' + path, json.dumps(body).encode(), {'Content-Type': 'application/json'})
    return json.loads(urllib.request.urlopen(r, timeout=30).read())
def wait_idle():
    for _ in range(60):
        s = json.loads(urllib.request.urlopen('http://localhost:5757/status').read())
        if not s['running']: return
        time.sleep(0.5)
def sleep_of(root): return (read_combined(root).get(D) or {}).get('sleep_duration')
def expect(label, got, want):
    ok = got not in (None, '') and abs(float(got) - want) < 1
    print(('ok  ' if ok else 'FAIL'), label, '->', got, '(want', want, ')')
    if not ok: f.add('BUG', f'{label}: sleep_duration={got}, expected {want}')

ring = {D: dict(steps=7000, kcal=300, sleep_min=383, deep=60, light=240, rem=70, awake=25, hr=62, hrmin=48, hrmax=110, hrv=48, spo2=96)}
hc = lambda mins: [dict(date=D, steps=7100, sleep_duration=mins, hr_avg=63)]

with fresh_server() as root:
    # 1. RingConn says 6h23, Health Connect (merged records) says 13h32 -> the ring wins
    write_ringconn_zip(root, ring); write_hc_export(root, hc(812)); run_pipeline(root)
    expect('1. ring 383 vs HC 812: ring wins', sleep_of(root), 383)

with fresh_server() as root:
    # 2. Same source corrects itself: HC first sends 812, later 317 -> must update, not stay stale
    write_hc_export(root, hc(812)); run_pipeline(root); expect('2a. HC first value', sleep_of(root), 812)
    write_hc_export(root, hc(317)); run_pipeline(root); expect('2b. HC corrected value replaces stale one', sleep_of(root), 317)

with fresh_server() as root:
    # 3. Manual entry beats every device, survives resyncs, even if precedence is set to put Manual last
    write_ringconn_zip(root, ring); write_hc_export(root, hc(812)); run_pipeline(root)
    post('/save-manual-entry', dict(date=D, sleep_duration=400)); wait_idle()
    expect('3a. manual 400 saved', sleep_of(root), 400)
    write_ringconn_zip(root, {D: {**ring[D], 'sleep_min': 390}}); write_hc_export(root, hc(500)); run_pipeline(root)
    expect('3b. manual survives a device resync', sleep_of(root), 400)
    post('/save-precedence', {'source_precedence': {'sleep': ['ringconn', 'health_connect', 'manual']}}); wait_idle()
    write_hc_export(root, hc(555)); run_pipeline(root)
    expect('3c. manual wins even when precedence lists it last', sleep_of(root), 400)
    # 4. Removing the manual value lets the device value through again
    post('/save-manual-entry', dict(date=D, steps=7000)); wait_idle(); run_pipeline(root)
    got = sleep_of(root); print('4. (info) after the manual sleep value is cleared, combined.csv keeps', got, '- manual values are sticky by design')

print('findings', len(f)); sys.exit(1 if f else 0)
