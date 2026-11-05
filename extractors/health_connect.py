"""
extractors/health_connect.py  (v1.4, 01/10/26)

Reads data/inbox/health_connect_export.json — written directly by the native
Android launcher's HealthConnectBridge.kt — and turns it into the same
{date: row_dict} shape every other device produces, via the standard
run(inbox, password=None, dry_run=False) contract.

v1.4: now a pass-through. Previously this file hand-listed four fields
(steps, hr_avg, weight, sleep_duration) and silently dropped anything else the
launcher sent, which meant HRV, SpO2 and active calories added on 30/09/26
could never reach combined.csv. Now every key the launcher writes that is also
in SOURCE_FIELDS['health_connect'] (update_health.py) is passed through, so
adding a metric needs no change here — only the launcher and that list.

Units: sleep_duration/sleep_deep/light/rem/wake are MINUTES; bedtime and
wake_time are "HH:MM" local strings; distance_m metres; calories in kcal.
"""

import json
import os

# Mirror of SOURCE_FIELDS['health_connect'] in update_health.py. Kept here (not
# imported) so this file stays standalone; update_health.py's own per-field
# whitelist and validation still apply afterwards.
FIELDS = [
    'steps', 'distance_m', 'calories_active', 'calories_passive',
    'sleep_duration', 'sleep_deep', 'sleep_light', 'sleep_rem', 'sleep_wake',
    'sleep_efficiency', 'bedtime', 'wake_time',
    'hr_avg', 'hr_min', 'hr_max', 'hr_resting',
    'hrv', 'hrv_min', 'hrv_max', 'spo2', 'spo2_min', 'spo2_max',
    'weight',
]

# Fields that are averages/measurements, not exact counts: stored to 1 decimal place.
ROUND_1DP = {'hr_avg', 'hrv', 'hrv_min', 'hrv_max', 'spo2', 'spo2_min', 'spo2_max', 'sleep_efficiency'}


def _hhmm(v):
    try:
        h, m = str(v).split(':'); return int(h) * 60 + int(m)
    except (ValueError, AttributeError):
        return None


def fix_overstated_sleep(row):
    """v1.5 (05/11/26): launchers up to 1.7.0 can report sleep_duration as the whole
    time in bed (bed -> wake) with efficiency 100, even when the same night carries
    real deep/light/REM minutes. Asleep time is those three stages. Only corrected
    when the gap between the stated total and the stages is fully explained by the
    recorded awake time (+15 min of slack for unstaged edges), so a total that
    legitimately differs (nap, other device) is never touched. Efficiency is then
    asleep / time in bed (bed -> wake clock times, else asleep + awake)."""
    try:
        asleep = row['sleep_deep'] + row['sleep_light'] + row['sleep_rem']
        total = row['sleep_duration']
        wake = row.get('sleep_wake') or 0
    except (KeyError, TypeError):
        return row
    if not all(isinstance(x, (int, float)) for x in (asleep, total, wake)) or asleep <= 0:
        return row
    excess = total - asleep
    if excess <= 10 or excess > wake + 15:
        return row
    row['sleep_duration'] = asleep
    bed, wk = _hhmm(row.get('bedtime')), _hhmm(row.get('wake_time'))
    in_bed = (wk - bed) % 1440 if bed is not None and wk is not None else asleep + wake
    if in_bed > 0:
        row['sleep_efficiency'] = round(min(100.0, asleep * 100.0 / in_bed), 1)
    return row


def run(inbox, password=None, dry_run=False):
    export_path = os.path.join(inbox, 'health_connect_export.json')

    if not os.path.exists(export_path):
        return []

    try:
        with open(export_path, 'r') as f:
            entries = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"  [health_connect] Could not read {export_path}: {e}")
        return []

    if not isinstance(entries, list):
        print(f"  [health_connect] Expected a JSON list in {export_path}, got {type(entries).__name__}")
        return []

    rows = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue  # a stray null/number/string in the list - skip it, keep the rest
        date = entry.get('date')
        if not date:
            continue  # validate_row() rejects rows with no valid date anyway

        row = {'date': date}
        for field in FIELDS:
            if entry.get(field) is not None:
                v = entry[field]
                # Averages arrive as long floats (HRV 27.29901960784314); keep 1 decimal.
                if isinstance(v, float) and field in ROUND_1DP:
                    v = round(v, 1)
                row[field] = v
        rows.append(fix_overstated_sleep(row))

    return rows
