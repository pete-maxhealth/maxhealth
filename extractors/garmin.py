"""
extractors/garmin.py  (01/10/26)

Garmin extractor for the MaxedHealth pipeline - standard run(inbox, password=None,
dry_run=False) contract, returns a list of {date: ..., field: ...} dicts.

IMPORTANT - NOT YET VERIFIED AGAINST A REAL EXPORT. Written from the schemas the
existing garmin.py parser already handles plus Garmin Connect's "Export Your Data"
bundle layout as documented/seen in the wild. Every lookup is deliberately tolerant
(several key spellings, missing keys skipped, bad rows skipped) so a field-name
surprise degrades to "that metric is blank" rather than a crash. First real Garmin
user's export should be dropped in tests/personas fixtures and the aliases below
adjusted.

Two kinds of input are recognised in the inbox:

 1. Wellness JSON - garmin*.json: a list of day objects, a single day object, or
    {"dailySummaries": [...]} (unofficial Connect API and official Health API
    schemas, via garmin.parse_garmin_export).
 2. Garmin Connect data-export zip - any zip containing a DI_CONNECT / DI-Connect
    folder. Read from it:
      *UDSFile*.json     daily summaries   (steps, distance, kcal, resting/min/max HR)
      *sleepData.json    nightly sleep     (deep/light/REM/awake seconds)

Units out: sleep_* in MINUTES (sleep_duration = deep+light+REM = time ASLEEP, same
convention as every other source), distance_m metres, calories in kcal.
"""

import glob
import json
import os
import sys
import zipfile
from collections import defaultdict


def _date(v):
    """'2026-07-05', '2026-07-05T00:00:00.0' or {'date': ...} -> 'YYYY-MM-DD' (or None)."""
    if isinstance(v, dict):
        v = v.get('date') or v.get('calendarDate')
    if not isinstance(v, str) or len(v) < 10:
        return None
    d = v[:10]
    return d if d[4] == '-' and d[7] == '-' else None


def _num(day, *keys):
    for k in keys:
        v = day.get(k)
        if isinstance(v, bool):
            continue
        if isinstance(v, (int, float)):
            return v
        if isinstance(v, str):
            try:
                return float(v)
            except ValueError:
                pass
    return None


def _from_daily(day):
    """One daily-summary object (any Garmin spelling) -> partial pipeline row."""
    d = _date(day.get('calendarDate'))
    if not d:
        return None
    row = {'date': d}
    row['steps'] = _num(day, 'totalSteps', 'steps')
    row['distance_m'] = _num(day, 'totalDistanceMeters', 'distanceInMeters')
    row['calories_active'] = _num(day, 'activeKilocalories', 'activeCalories')
    row['hr_resting'] = _num(day, 'restingHeartRate', 'restingHeartRateInBeatsPerMinute')
    row['hr_min'] = _num(day, 'minHeartRate', 'minHeartRateInBeatsPerMinute')
    row['hr_max'] = _num(day, 'maxHeartRate', 'maxHeartRateInBeatsPerMinute')
    row['hr_avg'] = _num(day, 'averageHeartRateInBeatsPerMinute')
    return row


def _from_sleep(night):
    d = _date(night.get('calendarDate'))
    if not d:
        return None
    deep = _num(night, 'deepSleepSeconds')
    light = _num(night, 'lightSleepSeconds')
    rem = _num(night, 'remSleepSeconds', 'remSleepDurationInSeconds')
    awake = _num(night, 'awakeSleepSeconds')
    if deep is None and light is None and rem is None:
        return None
    asleep = (deep or 0) + (light or 0) + (rem or 0)
    row = {'date': d, 'sleep_duration': round(asleep / 60)}
    if deep is not None: row['sleep_deep'] = round(deep / 60)
    if light is not None: row['sleep_light'] = round(light / 60)
    if rem is not None: row['sleep_rem'] = round(rem / 60)
    if awake is not None: row['sleep_wake'] = round(awake / 60)
    return row


def _json_items(text):
    """A Garmin JSON file -> list of dict items (list, single object or {'dailySummaries': [...]})."""
    try:
        data = json.loads(text)
    except (ValueError, TypeError):
        return []
    if isinstance(data, dict) and isinstance(data.get('dailySummaries'), list):
        data = data['dailySummaries']
    if isinstance(data, dict):
        data = [data]
    return [x for x in data if isinstance(x, dict)] if isinstance(data, list) else []


def is_garmin_zip(path):
    """True if the zip looks like a Garmin Connect data export (used by server.py too)."""
    try:
        with zipfile.ZipFile(path) as z:
            return any('di_connect' in n.lower() or 'di-connect' in n.lower() for n in z.namelist())
    except Exception:
        return False


def run(inbox, password=None, dry_run=False):
    merged = defaultdict(dict)
    used = []

    def add(row):
        if row:
            d = row['date']
            for k, v in row.items():
                if v is not None:
                    merged[d][k] = v

    # 1. Wellness JSON files
    for p in sorted(glob.glob(os.path.join(inbox, '*.json'))):
        name = os.path.basename(p).lower()
        if 'garmin' not in name or name.startswith('health_connect'):
            continue
        try:
            with open(p, encoding='utf-8') as f:
                items = _json_items(f.read())
        except OSError as e:
            print(f"  [garmin] could not read {name}: {e}", file=sys.stderr)
            continue
        for it in items:
            add(_from_daily(it))
        used.append(name)

    # 2. Garmin Connect data-export zips
    for p in sorted(glob.glob(os.path.join(inbox, '*.zip'))):
        if not is_garmin_zip(p):
            continue
        try:
            with zipfile.ZipFile(p) as z:
                for n in z.namelist():
                    nl = n.lower()
                    if not nl.endswith('.json'):
                        continue
                    if 'udsfile' in nl:
                        for it in _json_items(z.read(n).decode('utf-8-sig', 'replace')):
                            add(_from_daily(it))
                    elif 'sleepdata' in nl:
                        for it in _json_items(z.read(n).decode('utf-8-sig', 'replace')):
                            add(_from_sleep(it))
        except Exception as e:
            print(f"  [garmin] could not read {os.path.basename(p)}: {e}", file=sys.stderr)
            continue
        used.append(os.path.basename(p))

    if not merged:
        return []
    print(f"  [garmin] {len(merged)} days from {', '.join(used)}", file=sys.stderr)
    return [{**row, 'source': 'garmin'} for _, row in sorted(merged.items())]
