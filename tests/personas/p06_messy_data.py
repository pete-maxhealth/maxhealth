"""Persona 6: bad exports and long gaps. The pipeline must never crash or store garbage."""
import sys; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
f = Findings()
inbox = lambda root: os.path.join(root, 'data', 'inbox', 'health_connect_export.json')

# A. corrupt / odd files: must not crash, must not wipe existing good data
with fresh_server() as root:
    write_hc_export(root, [dict(date=d, steps=5000, sleep_duration=420) for d in days(5)]); run_pipeline(root)
    good = read_combined(root); print('baseline days:', len(good))
    for label, payload in [('empty file', ''), ('truncated json', '[{"date": "2026-09-'), ('not a list', '{"a":1}'),
                           ('empty list', '[]'), ('null rows', '[null, 1, "x"]')]:
        open(inbox(root), 'w').write(payload)
        rc, out = run_pipeline(root)
        if rc != 0 or 'Traceback' in out: f.add('BUG', f'{label}: pipeline crashed: ' + out[-250:])
        now = read_combined(root)
        if len(now) < len(good): f.add('BUG', f'{label}: combined.csv lost rows ({len(good)} -> {len(now)})')

# B. impossible values must be rejected, not stored
with fresh_server() as root:
    d = days(3)
    write_hc_export(root, [
        dict(date=d[0], steps=-500, sleep_duration=0, hr_avg=300, spo2=140, weight=0.5),
        dict(date=d[1], steps=999999999, sleep_duration=5000, hr_avg=-5, hrv=-3),
        dict(date='2999-01-01', steps=5000), dict(date='not-a-date', steps=5000), dict(steps=5000),
        dict(date=d[2], steps='abc', sleep_duration='', hr_avg=None, weight=82.0)])
    rc, out = run_pipeline(root)
    if rc != 0 or 'Traceback' in out: f.add('BUG', 'impossible values crashed the pipeline: ' + out[-250:])
    c = read_combined(root)
    limits = dict(steps=(0, 200000), sleep_duration=(1, 1440), hr_avg=(20, 250), spo2=(50, 100), weight=(20, 400), hrv=(1, 400))
    for dt, row in c.items():
        for fld, (lo, hi) in limits.items():
            v = row.get(fld, '')
            if v not in ('', None) and not lo <= float(v) <= hi: f.add('BUG', f'{dt}: stored impossible {fld}={v}')
    for bad in ('2999-01-01', 'not-a-date'):
        if bad in c: f.add('BUG', f'stored a row dated {bad}')
    print('rows kept from messy file:', sorted(c))

# C. user returns after a 45-day gap; old history must survive and the app must open cleanly
with fresh_server() as root:
    old = days(10, end=date.today() - timedelta(days=45))
    write_hc_export(root, [dict(date=x, steps=6000, sleep_duration=400, weight=81.0) for x in old]); run_pipeline(root)
    write_hc_export(root, [dict(date=x, steps=7000, sleep_duration=430, weight=80.0) for x in days(3)]); run_pipeline(root)
    c = read_combined(root)
    if len(c) != 13: f.add('BUG', f'gap persona: expected 13 rows (10 old + 3 new), got {len(c)}')
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch(); page = b.new_context(viewport={'width': 390, 'height': 844}).new_page()
        page.on('pageerror', lambda e: f.add('JS-exception', str(e)[:160]))
        page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
        page.evaluate("onboardNext(2)"); page.fill('#onboardName', 'Back'); page.evaluate("onboardNext(3)")
        page.evaluate("onboardFinish()"); page.wait_for_timeout(1500)
        sync = page.evaluate("fetch('/sync-status').then(r=>r.json())")
        print('sync-status after export just written:', sync)
        b.close()
print('findings', len(f)); sys.exit(1 if f else 0)
