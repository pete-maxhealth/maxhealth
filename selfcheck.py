#!/usr/bin/env python3
"""
selfcheck.py - MaxedHealth system health check (01/10/26).

Runs on the phone (plain Python, no browser needed). Looks at:
  - combined.csv: present, integrity (duplicate dates, non-numeric values), how fresh it is
  - pipeline.log: errors / warnings in the last 7 days, grouped by message
  - error_log.json: JavaScript errors the app itself recorded (no health values - see
    the capture code in maxhealth.html), new vs repeating
  - backups: newest backup age
Writes data/selfcheck.json and returns the same dict. Status mapping:
  green  -> "Nothing to worry about"
  amber  -> "One to know"
  red    -> "One to watch"
Usage:  python3 selfcheck.py            (prints a short report)
        python3 selfcheck.py --json     (machine-readable)
The server exposes it at GET /selfcheck.
"""
import csv, glob, json, os, sys
from datetime import datetime, timedelta

_HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(_HERE)
DATA = os.path.join(BASE, 'data')
COMBINED = os.path.join(DATA, 'tables', 'combined.csv')
PIPE_LOG = os.path.join(BASE, 'logs', 'pipeline.log')
ERROR_LOG = os.path.join(DATA, 'error_log.json')
BACKUP_DIR = os.path.join(DATA, 'backup')
OUT = os.path.join(DATA, 'selfcheck.json')
LABELS = {'green': 'Nothing to worry about', 'amber': 'One to know', 'red': 'One to watch'}


def _read_combined():
    try:
        with open(COMBINED, newline='', encoding='utf-8') as f:
            return list(csv.DictReader(f))
    except Exception:
        return None


def check_combined(items):
    rows = _read_combined()
    if rows is None:
        items.append(('amber', 'No combined.csv yet - no device data has been synced.'))
        return {'rows': 0}
    info = {'rows': len(rows)}
    seen, dupes, bad = set(), 0, 0
    for r in rows:
        d = r.get('date', '')
        if d in seen:
            dupes += 1
        seen.add(d)
        for fld in ('weight', 'steps', 'sleep_duration', 'hr_avg'):
            v = r.get(fld, '')
            if v not in ('', None):
                try:
                    float(v)
                except ValueError:
                    bad += 1
    if dupes or bad:
        items.append(('red', f'combined.csv integrity: {dupes} duplicate date(s), {bad} non-numeric value(s).'))
    dates = sorted(d for d in seen if len(d) == 10)
    if dates:
        info['newest'] = dates[-1]
        try:
            age = (datetime.now().date() - datetime.strptime(dates[-1], '%Y-%m-%d').date()).days
            info['newest_age_days'] = age
            if age > 3:
                items.append(('amber', f'Newest data is {age} days old ({dates[-1]}) - has syncing stopped?'))
        except ValueError:
            pass
    return info


def check_pipeline_log(items, days=7):
    info = {'errors': 0, 'warnings': 0}
    try:
        lines = open(PIPE_LOG, encoding='utf-8').read().splitlines()
    except Exception:
        return info
    cutoff = datetime.now() - timedelta(days=days)
    errs, warns = {}, {}
    last24 = 0
    for ln in lines:
        parts = [p.strip() for p in ln.split('|')]
        if len(parts) < 5:
            continue
        try:
            ts = datetime.strptime(parts[0], '%Y-%m-%d %H:%M:%S')
        except ValueError:
            continue
        if ts < cutoff:
            continue
        level, msg = parts[3].lower(), f'{parts[1]}: {parts[4]}'[:140]
        if level == 'error':
            errs[msg] = errs.get(msg, 0) + 1
            if ts > datetime.now() - timedelta(days=1):
                last24 += 1
        elif level == 'warn':
            # "No data returned" for a device the person doesn't own is normal noise
            if 'No data returned' in msg or 'No extractor' in msg or 'No ' in parts[4][:3] and 'export found' in parts[4]:
                continue
            warns[msg] = warns.get(msg, 0) + 1
    info['errors'], info['warnings'] = sum(errs.values()), sum(warns.values())
    for msg, n in sorted(errs.items(), key=lambda x: -x[1])[:3]:
        items.append(('red' if last24 else 'amber', f'Pipeline error x{n} this week: {msg}'))
    for msg, n in sorted(warns.items(), key=lambda x: -x[1])[:3]:
        items.append(('amber', f'Pipeline warning x{n} this week: {msg}'))
    return info


def check_error_log(items, days=7):
    info = {'recorded': 0, 'new_this_week': 0}
    try:
        log = json.load(open(ERROR_LOG, encoding='utf-8'))
    except Exception:
        return info
    if not isinstance(log, list):
        return info
    info['recorded'] = len(log)
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    recent = [e for e in log if e.get('last', '') >= cutoff]
    new = [e for e in recent if e.get('first', '') >= cutoff]
    info['new_this_week'] = len(new)
    for e in sorted(recent, key=lambda e: -e.get('count', 1))[:3]:
        tag = 'New' if e in new else 'Repeating'
        items.append(('amber', f"{tag} app error x{e.get('count', 1)} (v{str(e.get('v', '?')).lstrip('v')}): {e.get('msg', '')[:100]}"))
    return info


def check_backups(items):
    files = glob.glob(os.path.join(BACKUP_DIR, '*'))
    if not files:
        # A brand-new install has nothing to back up until a second change arrives; only worry once data is old
        try:
            old_data = (datetime.now().timestamp() - os.path.getmtime(COMBINED)) > 2 * 86400
        except OSError:
            old_data = False
        if old_data:
            items.append(('amber', 'No backups found yet.'))
        return {'newest_hours': None}
    newest = max(os.path.getmtime(f) for f in files)
    hours = (datetime.now().timestamp() - newest) / 3600
    if hours > 72:
        items.append(('amber', f'Newest backup is {hours/24:.0f} days old.'))
    return {'newest_hours': round(hours, 1)}


def launcher_last_run_age_minutes(data_dir=None):
    """Minutes since the Android launcher's background sync service last started (from its own diary), or None if unknown.
    A healthy launcher starts it every 30 minutes. Reads only the tail of the file."""
    path = os.path.join(data_dir or DATA, 'sync_service_debug.log')
    try:
        with open(path, 'rb') as f:
            f.seek(0, os.SEEK_END)
            size = f.tell()
            f.seek(max(0, size - 16384))
            tail = f.read().decode('utf-8', 'ignore')
    except OSError:
        return None
    last = None
    for line in tail.splitlines():
        if line.startswith('[') and ' onCreate' in line:
            try:
                last = datetime.strptime(line[1:20], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                pass
    if last is None:
        return None
    return max(0, int((datetime.now() - last).total_seconds() // 60))


LAUNCHER_FIX = ('Check MaxedHealth Sync: Battery > No restrictions, Alarms & reminders allowed, Autostart on (if your phone has it), '
                'and the app locked in recent apps, then open it once.')


def check_launcher_sync(items):
    age = launcher_last_run_age_minutes()
    if age is None:
        return {'launcher_age_minutes': None}
    if age >= 24 * 60:
        items.append(('red', f'The background sync has not run for {age // 60 // 24} days. {LAUNCHER_FIX}'))
    elif age >= 180:
        items.append(('amber', f'The background sync last ran {age // 60}h ago (it should run every 30 minutes). {LAUNCHER_FIX}'))
    return {'launcher_age_minutes': age}


def run_selfcheck(write=True):
    items = []
    out = {'checked': datetime.now().isoformat(timespec='seconds'),
           'combined': check_combined(items), 'pipeline_log': check_pipeline_log(items),
           'app_errors': check_error_log(items), 'backups': check_backups(items), 'launcher_sync': check_launcher_sync(items)}
    rank = {'green': 0, 'amber': 1, 'red': 2}
    status = 'green'
    for lvl, _ in items:
        if rank[lvl] > rank[status]:
            status = lvl
    out['status'] = status
    out['headline'] = LABELS[status]
    out['items'] = [{'level': l, 'text': t} for l, t in items]
    if write:
        try:
            os.makedirs(DATA, exist_ok=True)
            with open(OUT, 'w', encoding='utf-8') as f:
                json.dump(out, f, indent=2)
        except Exception:
            pass
    return out


if __name__ == '__main__':
    r = run_selfcheck()
    if '--json' in sys.argv:
        print(json.dumps(r, indent=2))
    else:
        print(f"{r['headline']}  ({r['status']})  - checked {r['checked']}")
        for it in r['items']:
            print(f"  [{it['level']}] {it['text']}")
        print(f"  combined: {r['combined']}  pipeline log: {r['pipeline_log']}  app errors: {r['app_errors']}  backups: {r['backups']}")
