#!/usr/bin/env python3
"""
extractors/amazfit.py
MaxHealth Pipeline — Amazfit / Zepp Extractor

Reads a Zepp data export zip (AES-256 encrypted, password required)
and outputs a combined.csv-compatible daily summary.

Zepp export structure:
  ACTIVITY/         — daily steps, distance, calories
  SLEEP/            — daily sleep stages (deep, light, REM, wake) in minutes
  HEARTRATE_AUTO/   — continuous HR readings (~5-min intervals)
  BODY/             — body composition (weight, BMI, fat%, etc.) — if populated
  SPORT/            — individual workout sessions
  ACTIVITY_MINUTE/  — per-minute step data (not used in daily summary)
  SLEEP_MINUTE/     — per-minute sleep stage data (not used in daily summary)
  HEARTRATE/        — manual HR readings (usually empty)
  HEALTH_DATA/      — body measurements (usually empty)
  USER/             — account metadata

Output columns (matching combined.csv schema):
  date, steps, sleep_duration, sleep_deep, sleep_light, sleep_rem,
  sleep_wake, hr_avg, hr_min, hr_max, weight, source

Usage:
  python3 amazfit.py <export.zip> [password] [--out combined.csv]

  password: your Zepp account password (shown in Zepp app at export time)
            defaults to checking ZEPP_PASSWORD env var
            if omitted, assumes zip is unencrypted

  --out: path to write/append output CSV
         defaults to ./amazfit_extracted.csv

  --append: if combined.csv already exists, merge by date
            (Amazfit fills in; existing values from other sources take precedence
             per pipeline source precedence rules)
"""

import argparse
import csv
import io
import os
import sys
import zipfile
from collections import defaultdict
from datetime import datetime, timezone


# ── helpers ──────────────────────────────────────────────────────────────────

def open_zip(path, password=None):
    """Open zip, with or without password. Returns ZipFile object."""
    zf = zipfile.ZipFile(path, 'r')
    if password:
        zf.setpassword(password.encode('utf-8'))
    return zf


def read_csv_from_zip(zf, filename, password=None):
    """
    Read a CSV from inside the zip. Returns list of dicts.
    Handles UTF-8 BOM (Zepp adds one). Returns [] if file missing or empty.
    """
    try:
        raw = zf.read(filename)
    except KeyError:
        return []
    except RuntimeError as e:
        print(f"  [warn] Could not read {filename}: {e}", file=sys.stderr)
        return []

    text = raw.decode('utf-8-sig')  # strips BOM if present
    lines = text.strip().splitlines()
    if len(lines) < 2:
        return []  # header only or empty

    reader = csv.DictReader(lines)
    return list(reader)


def find_csv_in_folder(zf, folder_prefix):
    """Find the first CSV in a given folder prefix inside the zip."""
    for name in zf.namelist():
        if name.startswith(folder_prefix) and name.endswith('.csv') and '/' in name[len(folder_prefix):] is False:
            return name
    # fallback: any csv under that prefix
    for name in zf.namelist():
        if name.startswith(folder_prefix) and name.endswith('.csv'):
            return name
    return None


# ── extractors ───────────────────────────────────────────────────────────────

def extract_activity(zf):
    """
    ACTIVITY: daily steps, distance, calories.
    Returns dict keyed by date string (YYYY-MM-DD).
    """
    fname = find_csv_in_folder(zf, 'ACTIVITY/')
    if not fname:
        print("  [info] No ACTIVITY data found", file=sys.stderr)
        return {}

    rows = read_csv_from_zip(zf, fname)
    result = {}
    for row in rows:
        date = row.get('date', '').strip()
        if not date:
            continue
        result[date] = {
            'steps':    _int(row.get('steps')),
            'distance': _int(row.get('distance')),   # metres
            'calories': _int(row.get('calories')),
        }
    print(f"  [ok] ACTIVITY: {len(result)} days", file=sys.stderr)
    return result


def extract_sleep(zf):
    """
    SLEEP: daily sleep summary — deep/light/REM/wake in minutes, total duration.
    Returns dict keyed by date string.
    """
    fname = find_csv_in_folder(zf, 'SLEEP/')
    if not fname:
        print("  [info] No SLEEP data found", file=sys.stderr)
        return {}

    rows = read_csv_from_zip(zf, fname)
    result = {}
    for row in rows:
        date = row.get('date', '').strip()
        if not date:
            continue
        deep    = _int(row.get('deepSleepTime'))
        light   = _int(row.get('shallowSleepTime'))
        rem     = _int(row.get('REMTime'))
        wake    = _int(row.get('wakeTime'))
        total   = (deep or 0) + (light or 0) + (rem or 0)  # minutes; exclude wake
        result[date] = {
            'sleep_duration': total,    # minutes of actual sleep
            'sleep_deep':     deep,
            'sleep_light':    light,
            'sleep_rem':      rem,
            'sleep_wake':     wake,
        }
    print(f"  [ok] SLEEP: {len(result)} days", file=sys.stderr)
    return result


def extract_heartrate(zf):
    """
    HEARTRATE_AUTO: continuous HR readings. Aggregates to daily avg/min/max.
    Returns dict keyed by date string.
    """
    fname = find_csv_in_folder(zf, 'HEARTRATE_AUTO/')
    if not fname:
        print("  [info] No HEARTRATE_AUTO data found", file=sys.stderr)
        return {}

    rows = read_csv_from_zip(zf, fname)
    by_date = defaultdict(list)
    for row in rows:
        date = row.get('date', '').strip()
        hr   = _int(row.get('heartRate'))
        if date and hr and hr > 0:
            by_date[date].append(hr)

    result = {}
    for date, readings in by_date.items():
        result[date] = {
            'hr_avg': round(sum(readings) / len(readings)),
            'hr_min': min(readings),
            'hr_max': max(readings),
        }
    print(f"  [ok] HEARTRATE_AUTO: {len(result)} days ({sum(len(v) for v in by_date.values())} readings)", file=sys.stderr)
    return result


def extract_body(zf):
    """
    BODY: body composition from Amazfit smart scale.
    Returns dict keyed by date string. Uses most recent reading per day.
    Fields: weight (kg), bmi, fatRate (%), muscleRate (%), bodyWaterRate (%), boneMass (kg)
    """
    fname = find_csv_in_folder(zf, 'BODY/')
    if not fname:
        return {}

    rows = read_csv_from_zip(zf, fname)
    if not rows:
        return {}

    result = {}
    for row in rows:
        # BODY uses 'time' (datetime), not 'date'
        ts = row.get('time', '').strip()
        if not ts:
            continue
        date = ts[:10]  # extract YYYY-MM-DD
        result[date] = {
            'weight':     _float(row.get('weight')),
            'bmi':        _float(row.get('bmi')),
            'fat_pct':    _float(row.get('fatRate')),
            'muscle_pct': _float(row.get('muscleRate')),
            'water_pct':  _float(row.get('bodyWaterRate')),
            'bone_mass':  _float(row.get('boneMass')),
        }
    if result:
        print(f"  [ok] BODY: {len(result)} days", file=sys.stderr)
    return result


def extract_sport(zf):
    """
    SPORT: individual workout sessions.
    Not merged into daily summary — returned separately for future use.
    """
    fname = find_csv_in_folder(zf, 'SPORT/')
    if not fname:
        return []

    rows = read_csv_from_zip(zf, fname)
    if rows:
        print(f"  [info] SPORT: {len(rows)} sessions (not merged into daily summary)", file=sys.stderr)
    return rows


# ── merge & output ────────────────────────────────────────────────────────────

def merge_daily(activity, sleep, heartrate, body):
    """
    Combine all sources into one dict keyed by date.
    Any field that is None means 'no data' — will be written as empty string.
    """
    all_dates = sorted(set(
        list(activity.keys()) +
        list(sleep.keys()) +
        list(heartrate.keys()) +
        list(body.keys())
    ))

    rows = []
    for date in all_dates:
        act  = activity.get(date, {})
        slp  = sleep.get(date, {})
        hr   = heartrate.get(date, {})
        bod  = body.get(date, {})

        # Build source tag
        sources = []
        if act:  sources.append('amazfit_activity')
        if slp:  sources.append('amazfit_sleep')
        if hr:   sources.append('amazfit_hr')
        if bod:  sources.append('amazfit_body')

        rows.append({
            'date':            date,
            'steps':           act.get('steps'),
            'distance_m':      act.get('distance'),
            'calories_active': act.get('calories'),
            'sleep_duration':  slp.get('sleep_duration'),
            'sleep_deep':      slp.get('sleep_deep'),
            'sleep_light':     slp.get('sleep_light'),
            'sleep_rem':       slp.get('sleep_rem'),
            'sleep_wake':      slp.get('sleep_wake'),
            'hr_avg':          hr.get('hr_avg'),
            'hr_min':          hr.get('hr_min'),
            'hr_max':          hr.get('hr_max'),
            'weight':          bod.get('weight'),
            'bmi':             bod.get('bmi'),
            'fat_pct':         bod.get('fat_pct'),
            'muscle_pct':      bod.get('muscle_pct'),
            'source':          '+'.join(sources),
        })

    return rows


FIELDNAMES = [
    'date', 'steps', 'distance_m', 'calories_active',
    'sleep_duration', 'sleep_deep', 'sleep_light', 'sleep_rem', 'sleep_wake',
    'hr_avg', 'hr_min', 'hr_max',
    'weight', 'bmi', 'fat_pct', 'muscle_pct',
    'source',
]


def write_output(rows, out_path, append_mode=False):
    """
    Write extracted rows to CSV.
    In append mode, reads existing file and merges by date —
    Amazfit fills gaps; existing values from other sources are preserved.
    """
    if append_mode and os.path.exists(out_path):
        existing = {}
        with open(out_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing[row['date']] = row

        # Merge: for each amazfit row, only fill fields that are empty in existing
        merged = dict(existing)
        new_count = 0
        filled_count = 0
        # Fields Amazfit is the SOLE source for (per pipeline precedence rules:
        # RingConn owns HRV/sleep/SpO2/HR, Withings owns weight/body comp,
        # Amazfit owns activity/steps/elevation). For these, always take the
        # latest Amazfit value rather than fill-only — Zepp's daily activity
        # totals can be incomplete on first sync and correct themselves on a
        # later export, and a stale low value should not be locked in forever.
        AMAZFIT_EXCLUSIVE = {'steps', 'distance_m', 'calories_active'}

        for row in rows:
            date = row['date']
            if date not in merged:
                merged[date] = {k: _str(v) for k, v in row.items()}
                new_count += 1
            else:
                ex = merged[date]
                changed = False
                for field, value in row.items():
                    if field in ('date', 'source'):
                        continue
                    if value is None:
                        continue
                    if field in AMAZFIT_EXCLUSIVE:
                        # Overwrite if different, not just if empty
                        if _str(value) != ex.get(field, ''):
                            ex[field] = _str(value)
                            changed = True
                    elif not ex.get(field):
                        ex[field] = _str(value)
                        changed = True
                if changed:
                    # Append source tag
                    existing_src = ex.get('source', '')
                    new_src = row.get('source', '')
                    if new_src and new_src not in existing_src:
                        ex['source'] = f"{existing_src}+{new_src}" if existing_src else new_src
                    filled_count += 1

        all_rows = sorted(merged.values(), key=lambda r: r['date'])

        # Ensure all fieldnames present (existing CSV may have more columns)
        all_fields = list(reader.fieldnames or FIELDNAMES) if False else None
        # Re-read fieldnames
        with open(out_path, 'r', newline='', encoding='utf-8') as f:
            all_fields = csv.DictReader(f).fieldnames or FIELDNAMES
        # Add any new Amazfit fields not already present
        for fn in FIELDNAMES:
            if fn not in all_fields:
                all_fields.append(fn)

        with open(out_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=all_fields, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(all_rows)

        print(f"\n  Merged into {out_path}:", file=sys.stderr)
        print(f"    {new_count} new dates added", file=sys.stderr)
        print(f"    {filled_count} existing dates supplemented", file=sys.stderr)

    else:
        with open(out_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction='ignore')
            writer.writeheader()
            for row in rows:
                writer.writerow({k: _str(v) for k, v in row.items()})

        print(f"\n  Written {len(rows)} rows to {out_path}", file=sys.stderr)


# ── type helpers ──────────────────────────────────────────────────────────────

def _int(val):
    try:
        return int(val) if val not in (None, '', 'null') else None
    except (ValueError, TypeError):
        return None

def _float(val):
    try:
        return float(val) if val not in (None, '', 'null') else None
    except (ValueError, TypeError):
        return None

def _str(val):
    return '' if val is None else str(val)


# ── pipeline interface ────────────────────────────────────────────────────────

def _flatten_zepp_folder(inbox):
    """If inbox contains a numeric Zepp folder (e.g. 7084918973_...), 
    move its contents up to inbox level automatically."""
    import re
    for item in os.listdir(inbox):
        item_path = os.path.join(inbox, item)
        if os.path.isdir(item_path) and re.match(r'^\d+_\d+$', item) and item != 'old':
            subfolders = os.listdir(item_path)
            if any(f in subfolders for f in ['ACTIVITY', 'SLEEP', 'HEARTRATE_AUTO']):
                print(f"  [amazfit] Auto-flattening Zepp folder: {item}", file=sys.stderr)
                for sub in subfolders:
                    src = os.path.join(item_path, sub)
                    dst = os.path.join(inbox, sub)
                    if not os.path.exists(dst):
                        shutil.move(src, dst)
                # Remove now-empty numbered folder
                try:
                    os.rmdir(item_path)
                except:
                    pass
                print(f"  [amazfit] Flattened — subfolders now in inbox", file=sys.stderr)

def run(inbox, password=None, dry_run=False):
    """
    Pipeline entry point. Called by update_health.py.

    Handles two cases:
      1. Pre-extracted folders in inbox (e.g. from ZArchiver) — detected first
      2. Zip file in inbox — opened with optional password

    inbox:    path to /data/inbox/
    password: zip password (only needed for encrypted zip)
    dry_run:  if True, return data without side effects

    Returns list of dicts, one per date.
    """
    import glob as _glob

    # ── Case 1: Pre-extracted folders already in inbox ───────────────────────
    # ZArchiver and other tools extract directly to inbox — detect this first
    activity_dir  = os.path.join(inbox, 'ACTIVITY')
    sleep_dir     = os.path.join(inbox, 'SLEEP')
    hr_dir        = os.path.join(inbox, 'HEARTRATE_AUTO')

    if os.path.isdir(activity_dir) or os.path.isdir(sleep_dir) or os.path.isdir(hr_dir):
        print(f"  [amazfit] Found pre-extracted Zepp folders in inbox — reading directly", file=sys.stderr)

        # Create a temporary zip-like interface using folder paths
        class FolderZip:
            """Mimics zipfile.ZipFile interface for pre-extracted folder structure."""
            def __init__(self, base):
                self.base = base
            def namelist(self):
                names = []
                for root, dirs, files in os.walk(self.base):
                    for f in files:
                        rel = os.path.relpath(os.path.join(root, f), self.base)
                        names.append(rel.replace(os.sep, '/'))
                return names
            def read(self, name):
                path = os.path.join(self.base, name.replace('/', os.sep))
                with open(path, 'rb') as f:
                    return f.read()
            def __enter__(self): return self
            def __exit__(self, *a): pass

        zf = FolderZip(inbox)
        activity  = extract_activity(zf)
        sleep     = extract_sleep(zf)
        heartrate = extract_heartrate(zf)
        body      = extract_body(zf)

        if not any([activity, sleep, heartrate, body]):
            print("  [amazfit] No data found in extracted folders", file=sys.stderr)
            return []

        rows = merge_daily(activity, sleep, heartrate, body)
        return rows

    # ── Case 2: Zip file in inbox ─────────────────────────────────────────────
    zips = _glob.glob(os.path.join(inbox, '*.zip'))

    # Priority 1: name clearly identifies Zepp/Amazfit
    zepp_zips = [z for z in zips if
                 os.path.basename(z)[0].isdigit() or
                 'amazfit' in os.path.basename(z).lower() or
                 'zepp' in os.path.basename(z).lower()]

    # Priority 2: peek inside zip for Amazfit folder signatures
    if not zepp_zips:
        for z in zips:
            try:
                with zipfile.ZipFile(z) as zf:
                    names = [n.upper() for n in zf.namelist()]
                    if any(folder in '/'.join(names) for folder in
                           ['ACTIVITY/', 'SLEEP/', 'HEARTRATE_AUTO/', 'SPORT/']):
                        zepp_zips.append(z)
                        break
            except Exception:
                pass

    if not zepp_zips:
        print(f"  [amazfit] No Amazfit/Zepp export found in {inbox}", file=sys.stderr)
        print(f"  [amazfit] Expected: zip with numeric prefix (e.g. 7084918973_....zip)", file=sys.stderr)
        print(f"  [amazfit] Or pre-extracted ACTIVITY/, SLEEP/, HEARTRATE_AUTO/ folders", file=sys.stderr)
        print(f"  [amazfit] Files in inbox: {[os.path.basename(f) for f in _glob.glob(os.path.join(inbox,'*'))]}", file=sys.stderr)
        return []

    zip_path = max(zepp_zips, key=os.path.getmtime)
    print(f"  [amazfit] Using: {os.path.basename(zip_path)}", file=sys.stderr)

    try:
        zf = open_zip(zip_path, password)
    except Exception as e:
        print(f"  [amazfit] Could not open zip: {e}", file=sys.stderr)
        print(f"  [amazfit] Tip: Use ZArchiver to extract the zip to the inbox folder first", file=sys.stderr)
        return []

    with zf:
        activity  = extract_activity(zf)
        sleep     = extract_sleep(zf)
        heartrate = extract_heartrate(zf)
        body      = extract_body(zf)

    if not any([activity, sleep, heartrate, body]):
        print("  [amazfit] No data extracted — check password or extract with ZArchiver first", file=sys.stderr)
        return []

    rows = merge_daily(activity, sleep, heartrate, body)
    return rows


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Extract Amazfit/Zepp export zip into MaxHealth pipeline CSV'
    )
    parser.add_argument('zip_path', help='Path to Zepp export .zip file')
    parser.add_argument('password', nargs='?', default=None,
                        help='Zip password (or set ZEPP_PASSWORD env var)')
    parser.add_argument('--out', default='amazfit_extracted.csv',
                        help='Output CSV path (default: amazfit_extracted.csv)')
    parser.add_argument('--append', action='store_true',
                        help='Merge into existing combined.csv, filling gaps only')
    args = parser.parse_args()

    password = args.password or os.environ.get('ZEPP_PASSWORD')

    print(f"MaxHealth — Amazfit/Zepp Extractor", file=sys.stderr)
    print(f"  Input:  {args.zip_path}", file=sys.stderr)
    print(f"  Output: {args.out}", file=sys.stderr)
    print(f"  Mode:   {'append/merge' if args.append else 'new file'}", file=sys.stderr)
    print(f"  Encrypted: {'yes' if password else 'no'}", file=sys.stderr)
    print("", file=sys.stderr)

    try:
        zf = open_zip(args.zip_path, password)
    except zipfile.BadZipFile as e:
        print(f"Error: Could not open zip: {e}", file=sys.stderr)
        sys.exit(1)

    with zf:
        activity  = extract_activity(zf)
        sleep     = extract_sleep(zf)
        heartrate = extract_heartrate(zf)
        body      = extract_body(zf)
        _sport    = extract_sport(zf)   # extracted but not merged yet

    if not any([activity, sleep, heartrate, body]):
        print("\nNo data extracted. Check zip contents and password.", file=sys.stderr)
        sys.exit(1)

    rows = merge_daily(activity, sleep, heartrate, body)
    print(f"\n  {len(rows)} daily records assembled", file=sys.stderr)

    write_output(rows, args.out, append_mode=args.append)
    print("\nDone.", file=sys.stderr)


if __name__ == '__main__':
    main()
