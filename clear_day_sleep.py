#!/usr/bin/env python3
"""One-off repair: blank the sleep figures for one day (default today) in combined.csv and forget which device they came
from, so the next pipeline run can fill them from the best source again. Use after a wrong sleep figure took the day
(for example a RingConn nap that replaced Zepp's night before v3.10.962), then put the right exports back in the inbox.
Usage: python3 clear_day_sleep.py [YYYY-MM-DD]. A dated backup of both files is made first. Other fields are untouched."""
import csv, json, os, shutil, sys, time
from datetime import date
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import update_health as U          # same paths the pipeline itself uses
CSV, FS = U.COMBINED, U.FIELD_SOURCES_FILE
day = sys.argv[1] if len(sys.argv) > 1 else date.today().isoformat()
FIELDS = ['sleep_duration', 'sleep_deep', 'sleep_light', 'sleep_rem', 'sleep_wake', 'sleep_onset', 'sleep_efficiency',
          'bedtime', 'wake_time', 'sleep_nap_min']
ts = time.strftime('%Y%m%d_%H%M%S')
for p in (CSV, FS):
    if os.path.exists(p): shutil.copy2(p, p + '.bak_' + ts)
with open(CSV, newline='', encoding='utf-8') as f:
    rd = csv.DictReader(f); cols = rd.fieldnames; rows = list(rd)
hit = False
for r in rows:
    if r.get('date') == day:
        hit = True
        print('before:', {k: r.get(k) for k in FIELDS})
        for k in FIELDS:
            if k in r: r[k] = ''
if not hit:
    sys.exit(f'No row for {day} in combined.csv - nothing changed.')
with open(CSV + '.tmp', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
os.replace(CSV + '.tmp', CSV)
if os.path.exists(FS):
    d = json.load(open(FS, encoding='utf-8'))
    for k in FIELDS: (d.get(day) or {}).pop(k, None)
    json.dump(d, open(FS + '.tmp', 'w', encoding='utf-8'), indent=2, sort_keys=True); os.replace(FS + '.tmp', FS)
print(f'Cleared sleep figures for {day}. Backups saved beside the files (.bak_{ts}).')
