"""Persona 87: the Today 'Daily Steps' total is saved as a PROVISIONAL manual value: a floor for today (shows while above the devices, a device at or above it takes over, Health Connect never beats it), a gap-filler on earlier days; Manual Entry screen values stay absolute."""
import sys, os, json, time; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
from datetime import date
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    iso = date.today().isoformat()
    os.makedirs(os.path.join(root, 'data', 'tables'), exist_ok=True)
    # a device figure already on today's row
    open(os.path.join(root, 'data', 'tables', 'combined.csv'), 'w').write('date,steps,source\n%s,4277,amazfit\n' % iso)
    json.dump({iso: {'steps': 'amazfit'}}, open(os.path.join(root, 'data', 'field_sources.json'), 'w'))
    errs = []
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 844}, service_workers='block').new_page()
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("localStorage.setItem('mh_onboarded','1')"); page.reload(); page.wait_for_timeout(2500)
    page.evaluate("saveDailySteps('6k')"); page.wait_for_timeout(1500)
    mf = os.path.join(root, 'data', 'inbox', 'manual_entry.json'); arch = os.path.join(root, 'data', 'inbox', 'old')
    ok = False
    for _ in range(20):
        c = read_combined(root)
        if (c.get(iso) or {}).get('steps') in ('6000', '6000.0'): ok = True; break
        time.sleep(1)
    if not ok: f.add('BUG', f"typed total did not reach combined.csv: {(read_combined(root).get(iso) or {}).get('steps')}")
    fs = json.load(open(os.path.join(root, 'data', 'field_sources.json')))
    if fs.get(iso, {}).get('steps') != 'manual': f.add('BUG', f"steps not attributed to manual: {fs.get(iso)}")
    if errs: f.add('BUG', f'page errors: {errs[:2]}')

# ---- merge rules, directly ----
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
import update_health as U
P = U.DEFAULT_PRECEDENCE if hasattr(U, 'DEFAULT_PRECEDENCE') else None
prec = {'steps': ['manual', 'garmin', 'withings', 'ringconn', 'amazfit', 'health_connect']}
U.METRIC_FIELDS['steps'] = ['steps']
def merge(existing, srcs, prov, today='2026-10-11', fs=None):
    fs = {'2026-10-11': {'steps': 'amazfit'}} if fs is None else {d: dict(v) for d, v in fs.items()}
    return U.merge_with_precedence({k: dict(v) for k, v in existing.items()}, srcs, prec, fs, provisional=prov, today_iso=today)
D = '2026-10-11'
ex = {D: {'date': D, 'steps': '4277'}}
man = {'manual': {D: {'date': D, 'steps': '6000'}}}
r, fs = merge(ex, man, {D: {'steps'}})
if r[D]['steps'] != '6000' or fs[D]['steps'] != 'manual': f.add('BUG', f'manual above stale device should show: {r[D]["steps"]} {fs[D]}')
r2, fs2 = merge(r, {**man, 'amazfit': {D: {'date': D, 'steps': '7000'}}}, {D: {'steps'}}, fs=fs)
if r2[D]['steps'] != '7000' or fs2[D]['steps'] != 'amazfit': f.add('BUG', f'device above manual should take over: {r2[D]["steps"]} {fs2[D]}')
r3, fs3 = merge(r, {**man, 'amazfit': {D: {'date': D, 'steps': '5000'}}}, {D: {'steps'}}, fs=fs)
if r3[D]['steps'] != '6000' or fs3[D]['steps'] != 'manual': f.add('BUG', f'device below manual should not win today: {r3[D]["steps"]} {fs3[D]}')
r4, fs4 = merge(r, {**man, 'health_connect': {D: {'date': D, 'steps': '9185'}}}, {D: {'steps'}}, fs=fs)
if r4[D]['steps'] != '9185': f.add('BUG', f'today Health Connect is the daytime snapshot and may beat the typed total: {r4[D]["steps"]}')
r4b, _ = merge(r, {**man, 'health_connect': {D: {'date': D, 'steps': '3000'}}}, {D: {'steps'}}, fs=fs)
if r4b[D]['steps'] != '6000': f.add('BUG', f'typed total above Health Connect must stay today: {r4b[D]["steps"]}')
r4c, fs4c = merge({D: {'date': D, 'steps': '9185'}}, {**man, 'health_connect': {D: {'date': D, 'steps': '9185'}}}, {D: {'steps'}}, today='2026-10-12', fs={D: {'steps': 'health_connect'}})
if r4c[D]['steps'] != '6000': f.add('BUG', f'after the day, doubled Health Connect must not replace the typed total: {r4c[D]["steps"]}')
r4d, fs4d = merge(r4c, {**man, 'health_connect': {D: {'date': D, 'steps': '9185'}}, 'ringconn': {D: {'date': D, 'steps': '5400'}}}, {D: {'steps'}}, today='2026-10-12', fs=fs4c)
if r4d[D]['steps'] != '5400': f.add('BUG', f'the ring figure must replace a typed total after the day: {r4d[D]["steps"]}')
r5, fs5 = merge(r, man, {D: {'steps'}}, fs=fs)   # same inputs again (the pipeline re-reads the file each run)
if r5[D]['steps'] != '6000' or fs5[D]['steps'] != 'manual': f.add('BUG', f'idempotent re-run lost the manual attribution: {r5[D]["steps"]} {fs5[D]}')
r6, fs6 = merge(r3, {**man, 'amazfit': {D: {'date': D, 'steps': '5000'}}}, {D: {'steps'}}, today='2026-10-12', fs=fs3)   # the day is over
if r6[D]['steps'] != '5000' or fs6[D]['steps'] != 'amazfit': f.add('BUG', f'after the day ends the device must win: {r6[D]["steps"]} {fs6[D]}')
r7, fs7 = merge(r, man, None, fs=fs)   # not provisional: absolute
r8, fs8 = merge(r7, {**man, 'amazfit': {D: {'date': D, 'steps': '7000'}}}, None, fs=fs7)
if r8[D]['steps'] != '6000' or fs8[D]['steps'] != 'manual': f.add('BUG', f'Manual Entry screen values must stay absolute: {r8[D]["steps"]}')
print('findings', len(f)); sys.exit(1 if f else 0)
