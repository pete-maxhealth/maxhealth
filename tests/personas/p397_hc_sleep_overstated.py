"""Persona 397: a Health Connect night whose stated total is the whole time in bed
(launcher <= 1.7.0) is corrected to the real asleep minutes, through the real pipeline.
Invented numbers only. Normal, unexplained-gap and no-stage nights must pass through untouched."""
import sys; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
f = Findings()
D = days(6)
rows = [
    # 0: overstated - total is bed->wake (00:40-08:10 = 450), stages 375, awake 62 -> asleep 375, eff 83.3
    dict(date=D[0], steps=5000, sleep_duration=450, sleep_deep=75, sleep_light=230, sleep_rem=70, sleep_wake=62, bedtime='00:40', wake_time='08:10', sleep_efficiency=100),
    # 1: normal - total equals the stages (+5): untouched
    dict(date=D[1], steps=5000, sleep_duration=380, sleep_deep=75, sleep_light=230, sleep_rem=70, sleep_wake=40, bedtime='23:30', wake_time='06:20', sleep_efficiency=88.5),
    # 2: gap NOT explained by awake time (200 over, only 20 awake): untouched
    dict(date=D[2], steps=5000, sleep_duration=575, sleep_deep=75, sleep_light=230, sleep_rem=70, sleep_wake=20, bedtime='23:00', wake_time='08:35', sleep_efficiency=95),
    # 3: no stage data: untouched
    dict(date=D[3], steps=5000, sleep_duration=430),
    # 4: crosses midnight, overstated: bed 22:50 -> wake 06:30 = 460, stages 390, awake 66
    dict(date=D[4], steps=5000, sleep_duration=460, sleep_deep=80, sleep_light=240, sleep_rem=70, sleep_wake=66, bedtime='22:50', wake_time='06:30', sleep_efficiency=100),
    # 5: stages but no clock times: efficiency from asleep + awake
    dict(date=D[5], steps=5000, sleep_duration=450, sleep_deep=70, sleep_light=230, sleep_rem=70, sleep_wake=70),
]
with fresh_server() as root:
    write_hc_export(root, rows)
    rc, out = run_pipeline(root)
    if rc: f.add('BUG', 'pipeline failed: ' + out[-300:])
    c = read_combined(root)
    def g(d, k):
        v = c.get(d, {}).get(k, ''); return float(v) if v not in ('', None) else None
    def expect(d, k, want, tol=0.15):
        v = g(d, k)
        if v is None or abs(v - want) > tol: f.add('BUG', f'{d} {k}={v} expected {want}')
    expect(D[0], 'sleep_duration', 375); expect(D[0], 'sleep_efficiency', 83.3)
    expect(D[1], 'sleep_duration', 380); expect(D[1], 'sleep_efficiency', 88.5)
    expect(D[2], 'sleep_duration', 575); expect(D[2], 'sleep_efficiency', 95)
    expect(D[3], 'sleep_duration', 430)
    if g(D[3], 'sleep_efficiency') is not None: f.add('BUG', 'no-stage night gained an efficiency figure')
    expect(D[4], 'sleep_duration', 390); expect(D[4], 'sleep_efficiency', 84.8)
    expect(D[5], 'sleep_duration', 370); expect(D[5], 'sleep_efficiency', 84.1)
    for d in D:
        if g(d, 'sleep_deep') is None and d != D[3]: f.add('BUG', f'{d} stage minutes lost')
print('findings', len(f)); sys.exit(1 if f else 0)
