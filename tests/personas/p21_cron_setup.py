"""Persona 21: the server adds the missing scheduled jobs on a fresh install, and leaves an existing crontab alone."""
import sys, os, tempfile, stat; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
f = Findings()
tmp = tempfile.mkdtemp(); store = tmp + '/cron.txt'; home = tmp + '/home'; os.makedirs(home); os.makedirs(tmp + '/bin')
open(tmp + '/bin/crontab', 'w').write('#!/bin/sh\nF="%s"\nif [ "$1" = "-l" ]; then [ -f "$F" ] && cat "$F" || exit 1; else cat > "$F"; fi\n' % store)
os.chmod(tmp + '/bin/crontab', 0o755)
os.environ['PATH'] = tmp + '/bin:' + os.environ['PATH']; os.environ['HOME'] = home; os.environ['MH_FORCE_CRON_SETUP'] = '1'
sys.path.insert(0, REPO); import server
def cron(): return open(store).read() if os.path.exists(store) else ''
added = server.ensure_scheduled_jobs()
c = cron()
if 'update_health.py' not in c or 'mh_autoupdate' not in c: f.add('BUG', f'fresh install did not get both jobs: {c!r}')
if not os.path.exists(home + '/mh_autoupdate.sh'): f.add('BUG', 'mh_autoupdate.sh not installed')
again = server.ensure_scheduled_jobs()
if cron() != c or any(a != 'x' and a for a in again): f.add('BUG', f'second run changed things: {again} {cron()!r}')
# Pete's real crontab: nothing may change
real = ("*/30 * * * * cd /storage/emulated/0/maxhealth/app/maxhealth && python3 update_health.py >> /x/cron_pipeline.log 2>&1\n"
       "5,35 * * * * ~/mh_autoupdate.sh\n* * * * * ~/mh_watchdog.sh\n")
open(store, 'w').write(real); server.ensure_scheduled_jobs()
if cron() != real: f.add('BUG', f'an existing crontab was altered: {cron()!r}')
# watchdog-only (what the launcher provisions): both are added, watchdog line kept
open(store, 'w').write('* * * * * ~/mh_watchdog.sh\n'); server.ensure_scheduled_jobs()
c = cron()
if 'mh_watchdog' not in c or 'update_health.py' not in c or 'mh_autoupdate' not in c: f.add('BUG', f'watchdog-only crontab not completed: {c!r}')
# a commented-out line must not count as present
open(store, 'w').write('# 5,35 * * * * ~/mh_autoupdate.sh\n* * * * * ~/mh_watchdog.sh\n'); server.ensure_scheduled_jobs()
if cron().count('mh_autoupdate') < 2: f.add('BUG', 'a commented-out job was treated as installed')
print('findings', len(f)); sys.exit(1 if f else 0)
