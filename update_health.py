#!/usr/bin/env python3
"""
update_health.py
MaxedHealth Pipeline — Main Entry Point

Usage:
  python update_health.py                          # process all devices
  python update_health.py --device withings        # specific device
  python update_health.py --device amazfit --password YOUR_PASSWORD
  python update_health.py --dry-run                # preview, no writes
  python update_health.py --restore backup_file.csv

Reads exports from:  /storage/emulated/0/MaxHealth/data/inbox/
Writes merged data:  /storage/emulated/0/MaxHealth/data/tables/combined.csv
Backups:             /storage/emulated/0/MaxHealth/data/backup/
Log:                 /storage/emulated/0/MaxHealth/pipeline.log
"""

import argparse
import csv
import glob
import json
import os
import shutil
import sys
from datetime import datetime

# ── Path constants ────────────────────────────────────────────────────────────
# Derive BASE from script location — update_health.py lives in app/
# so BASE (MaxHealth root) is two levels up: app/ → MaxHealth/
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE       = os.path.dirname(_SCRIPT_DIR)           # /storage/emulated/0/MaxHealth
INBOX      = os.path.join(BASE, 'data', 'inbox')
TABLES     = os.path.join(BASE, 'data', 'tables')
BACKUP_DIR = os.path.join(BASE, 'data', 'backup')
LOG_FILE   = os.path.join(BASE, 'logs', 'pipeline.log')
COMBINED   = os.path.join(TABLES, 'combined.csv')
NUTRITION  = os.path.join(TABLES, 'nutrition.csv')
PREFS_FILE = os.path.join(BASE, 'data', 'pipeline_prefs.json')

MAX_BACKUPS   = 7
MAX_LOG_LINES = 500

# ── Source precedence (default order, user-configurable via prefs) ─────────────
DEFAULT_PRECEDENCE = {
    'weight':   ['withings', 'manual', 'ringconn', 'amazfit'],
    'hrv':      ['ringconn', 'withings', 'garmin'],
    'sleep':    ['ringconn', 'withings', 'garmin', 'amazfit'],
    'steps':    ['garmin', 'withings', 'ringconn', 'amazfit'],
    'spo2':     ['ringconn', 'withings'],
    'hr':       ['ringconn', 'amazfit', 'withings', 'garmin'],
}

# Fields each source provides (used for precedence resolution)
SOURCE_FIELDS = {
    'withings': ['weight', 'bmi', 'fat_pct', 'fat_mass_kg', 'muscle_pct', 'muscle_mass_kg',
                 'bone_mass_kg', 'hydration_kg', 'pwv',
                 'hrv', 'hrv_min', 'hrv_max', 'spo2', 'spo2_min', 'spo2_max',
                 'sleep_duration', 'sleep_deep', 'sleep_light', 'sleep_rem', 'sleep_wake',
                 'sleep_onset', 'sleep_efficiency', 'sleep_hr_avg', 'sleep_hr_min', 'sleep_hr_max',
                 'snoring_min', 'bedtime', 'wake_time',
                 'steps', 'distance_m', 'calories_active', 'calories_passive', 'elevation_m',
                 'hr_avg', 'hr_min', 'hr_max'],
    'ringconn': ['hrv', 'hrv_min', 'hrv_max', 'spo2', 'spo2_min', 'spo2_max',
                 'sleep_duration', 'sleep_deep', 'sleep_light', 'sleep_rem', 'sleep_wake',
                 'sleep_onset', 'sleep_efficiency', 'bedtime', 'wake_time',
                 'steps', 'distance_m', 'calories_active',
                 'hr_avg', 'hr_min', 'hr_max'],
    'garmin':   ['steps', 'distance_m', 'calories_active', 'elevation_m',
                 'sleep_duration', 'sleep_deep', 'sleep_light', 'sleep_rem', 'sleep_wake',
                 'hr_avg', 'hr_min', 'hr_max', 'hrv'],
    'amazfit':  ['steps', 'distance_m', 'calories_active',
                 'sleep_duration', 'sleep_deep', 'sleep_light', 'sleep_rem', 'sleep_wake',
                 'bedtime', 'wake_time', 'hr_avg', 'hr_min', 'hr_max',
                 'weight', 'bmi', 'fat_pct', 'muscle_pct', 'water_pct', 'bone_mass_kg'],
}

# Map metric category → combined.csv fields
METRIC_FIELDS = {
    'weight': ['weight', 'bmi', 'fat_pct', 'fat_mass_kg', 'muscle_pct', 'muscle_mass_kg',
               'bone_mass_kg', 'hydration_kg', 'pwv'],
    'hrv':    ['hrv', 'hrv_min', 'hrv_max'],
    'sleep':  ['sleep_duration', 'sleep_deep', 'sleep_light', 'sleep_rem', 'sleep_wake',
               'sleep_onset', 'sleep_efficiency', 'bedtime', 'wake_time',
               'sleep_hr_avg', 'sleep_hr_min', 'sleep_hr_max', 'snoring_min'],
    'steps':  ['steps', 'distance_m', 'calories_active', 'calories_passive', 'elevation_m'],
    'spo2':   ['spo2', 'spo2_min', 'spo2_max'],
    'hr':     ['hr_avg', 'hr_min', 'hr_max'],
}

ALL_FIELDS = [
    'date',
    'steps', 'distance_m', 'calories_active', 'calories_passive', 'elevation_m',
    'sleep_duration', 'sleep_deep', 'sleep_light', 'sleep_rem', 'sleep_wake',
    'sleep_onset', 'sleep_efficiency', 'bedtime', 'wake_time',
    'sleep_hr_avg', 'sleep_hr_min', 'sleep_hr_max', 'snoring_min',
    'hr_avg', 'hr_min', 'hr_max',
    'hrv', 'hrv_min', 'hrv_max',
    'spo2', 'spo2_min', 'spo2_max',
    'weight', 'bmi',
    'fat_pct', 'fat_mass_kg',
    'muscle_pct', 'muscle_mass_kg',
    'bone_mass_kg', 'hydration_kg', 'water_pct',
    'pwv',
    'source',
]


# ── Logging ───────────────────────────────────────────────────────────────────

_log_buffer = []

def log(device, operation, status, message):
    """Write a structured log entry."""
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"{ts} | {device:<10} | {operation:<8} | {status:<6} | {message}"
    _log_buffer.append(line)
    print(line)

def flush_log():
    """Append buffered log entries to the log file, keeping max lines."""
    if not _log_buffer:
        return
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    # Read existing
    existing = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            existing = f.read().splitlines()
    combined = existing + _log_buffer
    # Trim to max
    if len(combined) > MAX_LOG_LINES:
        combined = combined[-MAX_LOG_LINES:]
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(combined) + '\n')


# ── Preferences ───────────────────────────────────────────────────────────────

def load_prefs():
    """Load user preferences (source precedence etc.) from JSON file."""
    if os.path.exists(PREFS_FILE):
        try:
            with open(PREFS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def get_precedence(prefs):
    """Return effective source precedence, merging user overrides with defaults."""
    prec = dict(DEFAULT_PRECEDENCE)
    user_prec = prefs.get('source_precedence', {})
    for metric, order in user_prec.items():
        if metric in prec:
            prec[metric] = order
    return prec


# ── Backup ────────────────────────────────────────────────────────────────────

def backup_files():
    """Copy combined.csv, nutrition.csv, master.csv and library.json to backup dir with timestamp."""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    backed_up = []

    MASTER      = os.path.join(TABLES, 'master.csv')
    LIBRARY     = os.path.join(TABLES, 'library.json')
    SUPPLEMENTS = os.path.join(TABLES, 'supplements.json')

    for src_path, name, ext in [
        (COMBINED,     'combined',     'csv'),
        (NUTRITION,    'nutrition',    'csv'),
        (MASTER,       'master',       'csv'),
        (LIBRARY,      'library',      'json'),
        (SUPPLEMENTS,  'supplements',  'json'),
    ]:
        if os.path.exists(src_path):
            dst = os.path.join(BACKUP_DIR, f"{name}_{ts}.{ext}")
            shutil.copy2(src_path, dst)
            backed_up.append(dst)

    # Trim to MAX_BACKUPS per file type
    for prefix, ext in [('combined','csv'),('nutrition','csv'),('master','csv'),('library','json'),('supplements','json')]:
        pattern = os.path.join(BACKUP_DIR, f"{prefix}_*.{ext}")
        files = sorted(glob.glob(pattern))
        while len(files) > MAX_BACKUPS:
            os.remove(files.pop(0))

    if backed_up:
        log('pipeline', 'backup', 'ok', f"Backed up {len(backed_up)} file(s) to {BACKUP_DIR}")
    return backed_up


def restore_backup(backup_path):
    """Restore a backup file to its original location."""
    fname = os.path.basename(backup_path)
    if fname.startswith('combined_'):
        dest = COMBINED
    elif fname.startswith('nutrition_'):
        dest = NUTRITION
    else:
        print(f"Error: Cannot determine destination for {fname}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copy2(backup_path, dest)
    log('pipeline', 'restore', 'ok', f"Restored {fname} → {dest}")
    flush_log()
    print(f"\nRestored: {dest}")


# ── CSV helpers ───────────────────────────────────────────────────────────────

def read_combined():
    """Read existing combined.csv into dict keyed by date."""
    if not os.path.exists(COMBINED):
        return {}
    rows = {}
    with open(COMBINED, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows[row['date']] = dict(row)
    return rows

def write_combined(rows_by_date, dry_run=False, existing_count=0):
    """Write merged data to combined.csv."""
    all_rows = sorted(rows_by_date.values(), key=lambda r: r.get('date', ''))

    if dry_run:
        print(f"\n[dry-run] Would write {len(all_rows)} rows to {COMBINED}")
        for row in all_rows[:5]:
            print(f"  {row.get('date')} | steps={row.get('steps')} | "
                  f"sleep={row.get('sleep_duration')} | source={row.get('source')}")
        if len(all_rows) > 5:
            print(f"  ... and {len(all_rows)-5} more rows")
        return

    # Safety check — never write fewer rows than we started with
    if existing_count > 0 and len(all_rows) < existing_count:
        log('pipeline', 'write', 'error',
            f"ABORTED: would write {len(all_rows)} rows but existing file has {existing_count} — refusing to shrink")
        log('pipeline', 'write', 'error',
            f"This usually means validation dropped rows. Check pipeline.log for validation warnings.")
        return

    os.makedirs(TABLES, exist_ok=True)
    tmp_path = COMBINED + '.tmp'
    with open(tmp_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=ALL_FIELDS, extrasaction='ignore')
        writer.writeheader()
        for row in all_rows:
            writer.writerow({k: row.get(k, '') for k in ALL_FIELDS})
    # Atomic rename — prevents partial writes from corrupting the file
    os.replace(tmp_path, COMBINED)

    log('pipeline', 'write', 'ok', f"combined.csv written ({len(all_rows)} rows)")


# ── Data validation ───────────────────────────────────────────────────────────

VALIDATION_RANGES = {
    'weight':         (30, 300),
    'steps':          (0, 100000),
    'sleep_duration': (0, 1440),
    'sleep_deep':     (0, 720),
    'sleep_light':    (0, 720),
    'sleep_rem':      (0, 720),
    'hr_avg':         (20, 250),
    'hr_min':         (20, 250),
    'hr_max':         (20, 300),
    'hrv':            (0, 300),
    'spo2':           (50, 100),
    'bmi':            (10, 70),
    'fat_pct':        (1, 70),
}

def validate_row(row, device):
    """Validate a data row. Returns (cleaned_row, warnings).
    Only returns None for rows with completely invalid dates.
    Never drops a row just because a field value is out of range — clears the field instead.
    """
    warnings = []
    cleaned = dict(row)

    # Date format — only hard failure
    date = row.get('date', '')
    try:
        datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        warnings.append(f"Invalid date format: '{date}' — skipping row")
        return None, warnings

    # Value ranges — clear bad values but keep the row
    for field, (lo, hi) in VALIDATION_RANGES.items():
        val = row.get(field, '')
        if val == '' or val is None:
            continue
        try:
            fval = float(val)
            if not (lo <= fval <= hi):
                warnings.append(f"{field}={val} out of range [{lo},{hi}] — cleared")
                cleaned[field] = ''
        except (ValueError, TypeError):
            warnings.append(f"{field}='{val}' not numeric — cleared")
            cleaned[field] = ''

    return cleaned, warnings


# ── Source precedence merge ───────────────────────────────────────────────────

def merge_with_precedence(existing_rows, new_rows_by_source, precedence):
    """
    Merge new data into existing rows using source precedence rules.

    existing_rows: dict {date: row_dict}
    new_rows_by_source: dict {source_name: {date: row_dict}}
    precedence: dict {metric_category: [source, ...]}

    For each date and each field:
    - If existing row has no value: fill from highest-priority source that has it
    - If existing row has a value: only overwrite if a higher-priority source provides it
    - Never leave a field empty if any source has data for it

    Returns merged rows dict.
    """
    merged = dict(existing_rows)

    # Collect all dates across all sources
    all_dates = set(merged.keys())
    for source_rows in new_rows_by_source.values():
        all_dates.update(source_rows.keys())

    for date in all_dates:
        if date not in merged:
            merged[date] = {'date': date}

        row = merged[date]
        sources_used = set()
        if row.get('source'):
            sources_used = set(row['source'].split('+'))

        # For each metric category, apply precedence field by field
        for metric, prio_sources in precedence.items():
            fields = METRIC_FIELDS.get(metric, [])

            for field in fields:
                existing_val = row.get(field)

                # Try sources in priority order
                for source in prio_sources:
                    source_rows = new_rows_by_source.get(source, {})
                    if date not in source_rows:
                        continue
                    src_val = source_rows[date].get(field)
                    if not src_val:
                        continue

                    if not existing_val:
                        # Field is empty — fill it from this source
                        row[field] = src_val
                        sources_used.add(source)
                        break
                    else:
                        # Field already has a value — only overwrite if this is
                        # a higher-priority source than whatever set it originally
                        current_source = row.get('source', '')
                        current_priority = next(
                            (i for i, s in enumerate(prio_sources) if s in current_source),
                            999
                        )
                        new_priority = prio_sources.index(source)
                        if new_priority < current_priority:
                            row[field] = src_val
                            sources_used.add(source)
                        break  # Don't check lower-priority sources for this field

        row['source'] = '+'.join(sorted(sources_used)) if sources_used else row.get('source', '')
        merged[date] = row

    return merged


# ── Device extractors ─────────────────────────────────────────────────────────

def run_extractor(device, inbox, password=None, dry_run=False):
    """
    Run a device extractor. Returns {date: row_dict} or {} on failure.
    Extractors live in extractors/ subdirectory.
    """
    extractor_path = os.path.join(os.path.dirname(__file__), 'extractors', f'{device}.py')

    if not os.path.exists(extractor_path):
        log(device, 'extract', 'warn',  f"No extractor found at {extractor_path}")
        return {}

    import importlib.util
    spec = importlib.util.spec_from_file_location(f'extractors.{device}', extractor_path)
    mod  = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception as e:
        log(device, 'extract', 'error', f"Failed to load extractor: {e}")
        return {}

    try:
        # Each extractor exposes run(inbox, password=None) → list of dicts
        rows_list = mod.run(inbox, password=password, dry_run=dry_run)
        if not rows_list:
            log(device, 'extract', 'warn', 'No data returned')
            return {}

        # Validate rows
        rows_by_date = {}
        warn_count = 0
        for row in rows_list:
            cleaned, warnings = validate_row(row, device)
            for w in warnings:
                log(device, 'validate', 'warn', w)
                warn_count += 1
            if cleaned:
                rows_by_date[cleaned['date']] = cleaned

        log(device, 'extract', 'ok',
            f"{len(rows_by_date)} days extracted" +
            (f", {warn_count} validation warnings" if warn_count else ""))
        return rows_by_date

    except Exception as e:
        log(device, 'extract', 'error', f"Extractor raised exception: {e}")
        import traceback
        traceback.print_exc()
        return {}


# ── Integrity check ───────────────────────────────────────────────────────────

def check_integrity(rows_by_date):
    """
    Check for duplicate dates and corrupted entries in combined.csv.
    Returns list of issue strings.
    """
    issues = []
    seen_dates = {}
    for date, row in rows_by_date.items():
        # Duplicate check (shouldn't happen in a dict, but catches re-imports)
        if date in seen_dates:
            issues.append(f"Duplicate date: {date}")
        seen_dates[date] = True

        # Corrupted: date key doesn't match row date field
        if row.get('date') != date:
            issues.append(f"Date mismatch: key={date} row.date={row.get('date')}")

        # Corrupted: non-numeric value in numeric field
        for field in ['weight', 'steps', 'sleep_duration', 'hr_avg']:
            val = row.get(field, '')
            if val and val != '':
                try:
                    float(val)
                except (ValueError, TypeError):
                    issues.append(f"{date}: {field}='{val}' is not numeric")

    return issues


# ── Main ──────────────────────────────────────────────────────────────────────

KNOWN_DEVICES = ['withings', 'ringconn', 'garmin', 'amazfit']

def main():
    parser = argparse.ArgumentParser(description='MaxedHealth Data Pipeline')
    parser.add_argument('--device',   help='Run specific device extractor only')
    parser.add_argument('--password', help='Password for encrypted exports (e.g. Amazfit/Zepp)')
    parser.add_argument('--dry-run',  action='store_true', help='Preview only — no files written')
    parser.add_argument('--restore',  help='Restore a backup file (path to backup CSV)')
    parser.add_argument('--check',    action='store_true', help='Run integrity check on existing combined.csv')
    args = parser.parse_args()

    print("MaxedHealth Pipeline", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print(f"  Inbox:  {INBOX}")
    print(f"  Tables: {TABLES}")
    print()

    # ── Restore mode ──
    if args.restore:
        restore_backup(args.restore)
        return

    # ── Integrity check mode ──
    if args.check:
        existing = read_combined()
        if not existing:
            print("No combined.csv found.")
            return
        issues = check_integrity(existing)
        if issues:
            print(f"Found {len(issues)} issue(s):")
            for issue in issues:
                print(f"  ⚠ {issue}")
                log('pipeline', 'integrity', 'warn', issue)
        else:
            print(f"✓ Integrity check passed — {len(existing)} rows, no issues found")
            log('pipeline', 'integrity', 'ok', f"{len(existing)} rows checked, no issues")
        flush_log()
        return

    # ── Normal pipeline run ──
    prefs = load_prefs()
    precedence = get_precedence(prefs)

    # Determine which devices to run
    if args.device:
        devices = [args.device]
    else:
        # Auto-detect: run all devices that have files in inbox
        devices = []
        for device in KNOWN_DEVICES:
            # Check if inbox has any likely file for this device
            inbox_files = os.listdir(INBOX) if os.path.exists(INBOX) else []
            # Always try all known devices — extractors handle missing files gracefully
            devices.append(device)

    if not devices:
        print("No devices to process.")
        flush_log()
        return

    # Read existing combined.csv
    existing = read_combined()
    if existing:
        log('pipeline', 'read', 'ok', f"Loaded existing combined.csv ({len(existing)} rows)")

        # Integrity check on load
        issues = check_integrity(existing)
        if issues:
            for issue in issues:
                log('pipeline', 'integrity', 'warn', issue)
            print(f"\n⚠ {len(issues)} integrity issue(s) found in existing data — see log.")

    # Run extractors
    new_rows_by_source = {}
    for device in devices:
        password = args.password if device == 'amazfit' else None
        # Also check env var
        if not password and device == 'amazfit':
            password = os.environ.get('ZEPP_PASSWORD')

        rows = run_extractor(device, INBOX, password=password, dry_run=args.dry_run)
        if rows:
            new_rows_by_source[device] = rows

    if not new_rows_by_source:
        print("\nNo new data extracted from any device.")
        print("Check that export files are in the inbox folder:")
        print(f"  {INBOX}")
        # Still archive inbox files — they were processed, just yielded no new data
        if not args.dry_run:
            archive_inbox()
        flush_log()
        return

    # Merge with precedence
    merged = merge_with_precedence(existing, new_rows_by_source, precedence)

    new_dates = len(merged) - len(existing)
    log('pipeline', 'merge', 'ok',
        f"{len(merged)} total rows ({new_dates:+d} new dates, "
        f"{len(merged)-len(existing)-new_dates} supplemented)")

    # Backup before writing
    if not args.dry_run:
        backup_files()

    # Write output
    write_combined(merged, dry_run=args.dry_run, existing_count=len(existing))

    # Archive processed inbox files to data/inbox/old/
    if not args.dry_run:
        archive_inbox()

    if not args.dry_run:
        print(f"\n✓ Done. Import {COMBINED} in the MaxedHealth app → Import tab.")

    flush_log()


def archive_inbox():
    """
    Move all files and folders from inbox to inbox/old/ after a successful run.
    Creates inbox/old/ if needed. Logs each move. Leaves files in place on error.
    """
    old_dir = os.path.join(INBOX, 'old')
    os.makedirs(old_dir, exist_ok=True)

    moved = 0
    for item in os.listdir(INBOX):
        if item == 'old':
            continue  # Never move the old/ folder itself
        src = os.path.join(INBOX, item)
        dst = os.path.join(old_dir, item)

        # If destination already exists, add timestamp suffix
        if os.path.exists(dst):
            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            name, ext = os.path.splitext(item)
            dst = os.path.join(old_dir, f"{name}_{ts}{ext}")

        try:
            shutil.move(src, dst)
            log('pipeline', 'archive', 'ok', f"Moved {item} → inbox/old/")
            moved += 1
        except Exception as e:
            log('pipeline', 'archive', 'warn', f"Could not move {item}: {e}")
            print(f"  [warn] Could not archive {item}: {e}", file=sys.stderr)

    if moved:
        print(f"  [archive] {moved} item(s) moved to inbox/old/")


if __name__ == '__main__':
    main()
