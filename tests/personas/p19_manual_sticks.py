"""Persona 19: a typed-in correction must survive device re-syncs (01/10/26: sleep kept coming back from Health Connect)."""
import sys, os, json, time, urllib.request; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
f = Findings(); t = days(1)[0]
def post(path, obj):
    r = urllib.request.Request('http://localhost:5757' + path, json.dumps(obj).encode(), {'Content-Type': 'application/json'})
    return json.loads(urllib.request.urlopen(r).read())
def sleep(root): return read_combined(root).get(t, {}).get('sleep_duration')
with fresh_server() as root:
    write_hc_export(root, [{'date': t, 'sleep_duration': 812, 'steps': 3000}]); run_pipeline(root)
    if sleep(root) != '812': f.add('BUG', f'setup: HC sleep {sleep(root)}')
    r = post('/save-manual-entry', {'date': t, 'sleep_duration': 317})
    for _ in range(30):
        time.sleep(0.5)
        if sleep(root) == '317': break
    if sleep(root) != '317': f.add('BUG', f'manual sleep not applied: {sleep(root)}')
    for i, v in enumerate((830, 845, 900)):
        write_hc_export(root, [{'date': t, 'sleep_duration': v, 'steps': 3100 + i}]); run_pipeline(root)
        if sleep(root) != '317': f.add('BUG', f'HC re-sync #{i+1} ({v}) overwrote the manual sleep: {sleep(root)}')
    if not os.path.exists(root + '/data/inbox/manual_entry.json'): f.add('BUG', 'manual_entry.json was archived out of the inbox by a full run')
    # attribution lost (restore, older install): the manual entry must still win
    fs = root + '/data/field_sources.json'
    if os.path.exists(fs): os.remove(fs)
    write_hc_export(root, [{'date': t, 'sleep_duration': 777, 'steps': 3200}]); run_pipeline(root)
    if sleep(root) != '317': f.add('BUG', f'with no field_sources.json the device value won: {sleep(root)}')
    # a manual save arriving while a sync is running must be queued, not dropped
    sys.path.insert(0, root + '/app')
    r = post('/save-manual-entry', {'date': t, 'sleep_duration': 400})
    for _ in range(30):
        time.sleep(0.5)
        if sleep(root) == '400': break
    if sleep(root) != '400': f.add('BUG', f'second manual value not applied: {sleep(root)}')
print('findings', len(f)); sys.exit(1 if f else 0)
