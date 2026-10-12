"""Persona 123: the server puts the `mhstart` command back when it is missing, and never overwrites an existing one."""
import sys, os, tempfile
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'server.py')).read()
i = src.index('MHSTART_SCRIPT = '); j = src.index('def ensure_scheduled_jobs')
ns = {'os': os, 'APP_DIR': '/storage/emulated/0/maxhealth/app/maxhealth'}; exec(src[i:j], ns)
bad = []
d = tempfile.mkdtemp()
if not ns['ensure_mhstart'](d): bad.append('did not write when missing')
p = os.path.join(d, 'bin', 'mhstart')
t = open(p).read() if os.path.exists(p) else ''
if not os.access(p, os.X_OK): bad.append('not executable')
if 'python server.py' not in t or '/storage/emulated/0/maxhealth/app/maxhealth' not in t: bad.append('script content wrong')
open(p, 'w').write('custom'); 
if ns['ensure_mhstart'](d) or open(p).read() != 'custom': bad.append('overwrote an existing mhstart')
print('findings', len(bad)); [print(('BUG', b)) for b in bad]; sys.exit(1 if bad else 0)
