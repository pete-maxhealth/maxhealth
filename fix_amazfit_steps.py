#!/usr/bin/env python3
"""
fix_amazfit_steps.py
One-off correction pass for historical steps/distance/calories_active values
in combined.csv that were locked in too early by the old fill-only merge
logic (see amazfit.py v3.10.14 fix).

This does NOT touch sleep, HR, weight, or any other field — only the three
fields Amazfit is the sole source for. It force-overwrites them with
whatever your latest Zepp export actually says, regardless of what's
currently in combined.csv.

Usage:
  python3 fix_amazfit_steps.py <export.zip> <combined.csv> [password]

A backup of combined.csv is written first as combined.csv.bak-<timestamp>
before anything is changed.
"""

import csv
import sys
import shutil
from datetime import datetime

# Reuse the real extractor logic so we match exactly what production uses
sys.path.insert(0, '.')
from amazfit import open_zip, extract_activity, _str


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 fix_amazfit_steps.py <export.zip> <combined.csv> [password]")
        sys.exit(1)

    zip_path = sys.argv[1]
    csv_path = sys.argv[2]
    password = sys.argv[3] if len(sys.argv) > 3 else None

    print(f"Reading Amazfit export: {zip_path}")
    zf = open_zip(zip_path, password)
    activity = extract_activity(zf)
    print(f"  Found activity data for {len(activity)} days")

    # Backup first — non-negotiable before mutating real data
    ts = datetime.now().strftime('%Y%m%d-%H%M%S')
    backup_path = f"{csv_path}.bak-{ts}"
    shutil.copy2(csv_path, backup_path)
    print(f"Backup written: {backup_path}")

    # Load existing combined.csv
    with open(csv_path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    FIELDS_TO_FIX = ['steps', 'distance_m', 'calories_active']
    for f in FIELDS_TO_FIX:
        if f not in fieldnames:
            print(f"  [warn] Field '{f}' not found in combined.csv — skipping it")

    changes = []
    by_date = {r['date']: r for r in rows}

    for date, act in activity.items():
        if date not in by_date:
            continue  # new date — let the normal sync handle it, not this script
        row = by_date[date]
        for field, act_key in (('steps', 'steps'), ('distance_m', 'distance'), ('calories_active', 'calories')):
            if field not in fieldnames:
                continue
            new_val = act.get(act_key)
            if new_val is None:
                continue
            old_val = row.get(field, '')
            new_val_str = _str(new_val)
            if new_val_str != old_val:
                changes.append((date, field, old_val, new_val_str))
                row[field] = new_val_str

    if not changes:
        print("No corrections needed — combined.csv already matches the export.")
        return

    print(f"\n{len(changes)} corrections found:")
    for date, field, old, new in changes:
        print(f"  {date}  {field}: '{old}' -> '{new}'")

    confirm = input(f"\nApply these {len(changes)} corrections to {csv_path}? [y/N] ").strip().lower()
    if confirm != 'y':
        print("Aborted — no changes written. (Backup still saved, can be deleted.)")
        return

    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in sorted(by_date.values(), key=lambda r: r['date']):
            writer.writerow(row)

    print(f"\n✓ Done. {len(changes)} values corrected in {csv_path}")
    print(f"  Backup kept at: {backup_path}")


if __name__ == '__main__':
    main()
