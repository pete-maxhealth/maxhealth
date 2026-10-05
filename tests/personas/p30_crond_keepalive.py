"""Persona 30: server restarts a dead crond (Pete's phone: crond silently died, nothing restarted the server)."""
import sys, os, subprocess, tempfile; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
f = Findings()
d = tempfile.mkdtemp()
def w(n, body):
    open(os.path.join(d, n), 'w').write(body); os.chmod(os.path.join(d, n), 0o755)
w('pgrep', '#!/bin/sh\nexit 1\n'); w('crond', '#!/bin/sh\ntouch %s/ran\n' % d)
here = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env = dict(os.environ, PATH=d + ':' + os.environ['PATH'], HOME=d)
r = subprocess.run([sys.executable, '-c', 'import server,time;print(server.crond_check_once());time.sleep(1)'], cwd=here, env=env, capture_output=True, text=True, timeout=30)
if 'started' not in r.stdout: f.add('BUG', 'dead crond not restarted: ' + r.stdout[-200:] + r.stderr[-200:])
if not os.path.exists(os.path.join(d, 'ran')): f.add('BUG', 'crond was never launched')
w('pgrep', '#!/bin/sh\necho 123\n')
r = subprocess.run([sys.executable, '-c', 'import server;print(server.crond_check_once())'], cwd=here, env=env, capture_output=True, text=True, timeout=30)
if 'running' not in r.stdout: f.add('BUG', 'running crond not recognised: ' + r.stdout[-200:])
print('findings', len(f)); sys.exit(1 if f else 0)
