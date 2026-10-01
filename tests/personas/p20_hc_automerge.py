"""Persona 20: a Health Connect export dropped by the launcher is merged by the server itself - no cron needed."""
import sys, os, time, subprocess, shutil, tempfile, socket; sys.path.insert(0, __file__.rsplit('/',1)[0])
import harness
from harness import *
f = Findings(); t = days(1)[0]
os.environ['MH_HC_WATCH_SECONDS'] = '2'      # inherited by the server subprocess
def wait(root, pred, secs=25):
    for _ in range(secs * 2):
        time.sleep(0.5)
        if pred(read_combined(root).get(t, {})): return True
    return False
with fresh_server() as root:
    write_hc_export(root, [{'date': t, 'steps': 4321, 'sleep_duration': 400}])
    if not wait(root, lambda r: r.get('steps') == '4321'): f.add('BUG', 'a new Health Connect export was not merged by the server')
    write_hc_export(root, [{'date': t, 'steps': 5555, 'sleep_duration': 400}])
    os.utime(root + '/data/inbox/health_connect_export.json', (time.time() + 5, time.time() + 5))
    if not wait(root, lambda r: r.get('steps') == '5555'): f.add('BUG', 'an updated Health Connect export was not merged')
    log = open(root + '/data/inbox/../logs/pipeline.log').read() if os.path.exists(root + '/data/logs/pipeline.log') else ''
print('findings', len(f)); sys.exit(1 if f else 0)
