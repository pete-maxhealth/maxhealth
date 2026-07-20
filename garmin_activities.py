"""
garmin_activities.py — parser for Garmin Connect's "Export CSV" activities file
(the per-workout summary export, distinct from garmin.py's daily wellness JSON).

IMPORTANT — unit ambiguity in Garmin's own export:
Garmin's CSV does not include an explicit units column. Distance and pace units
depend on each activity's own device/display settings at the time it was recorded,
and can genuinely differ row-to-row in the same file (confirmed in Pete's actual
sample: a running activity's distance value matches its "5K" title only if read
as kilometres, while the same file's cycling row shows "15.5 mph" — implying
miles for that row instead). Silently assuming one global unit would be wrong
some fraction of the time. This parser detects units per-row from context where
possible and explicitly flags anything it can't determine confidently, rather
than guessing.
"""

import csv
import re
from datetime import datetime


def _detect_pace_unit(pace_str):
    """Returns 'mph', 'kmh', or None if the pace field doesn't self-identify."""
    if not pace_str:
        return None
    if 'mph' in pace_str.lower():
        return 'mph'
    if 'kmh' in pace_str.lower() or 'km/h' in pace_str.lower():
        return 'kmh'
    return None  # bare "MM:SS" pace — ambiguous, could be min/km or min/mi


def _guess_distance_unit_from_title(title, activity_type):
    """
    Best-effort hint only, not a confident answer — e.g. a title containing
    '5K' strongly suggests kilometres for that specific activity. Returns
    'km', 'mi', or None if no hint is available.
    """
    if not title:
        return None
    if re.search(r'\b\d+\s*k\b', title, re.IGNORECASE):
        return 'km'
    if re.search(r'\bmile', title, re.IGNORECASE):
        return 'mi'
    return None


def _parse_duration_to_seconds(time_str):
    """HH:MM:SS -> total seconds. Returns None if unparseable."""
    if not time_str:
        return None
    parts = time_str.split(':')
    try:
        parts = [int(p) for p in parts]
    except ValueError:
        return None
    if len(parts) == 3:
        h, m, s = parts
    elif len(parts) == 2:
        h, m, s = 0, parts[0], parts[1]
    else:
        return None
    return h * 3600 + m * 60 + s


def parse_garmin_activities_csv(filepath):
    """
    Parses a Garmin "Export CSV" activities file. Returns a list of dicts,
    one per activity, each carrying an explicit `distance_unit_confidence`
    field ('confirmed' / 'guessed' / 'unknown') so the caller — and ultimately
    whoever reviews the import — knows which rows need a manual check rather
    than silently trusting a guess.
    """
    results = []
    with open(filepath, 'r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            activity_type = (row.get('Activity Type') or '').strip()
            title = (row.get('Title') or '').strip()
            date_raw = (row.get('Date') or '').strip()

            try:
                date_parsed = datetime.strptime(date_raw, '%d-%b-%Y %I:%M %p')
                date_iso = date_parsed.strftime('%Y-%m-%d')
                time_of_day = date_parsed.strftime('%H:%M')
            except ValueError:
                date_iso = None
                time_of_day = None

            pace_str = (row.get('Avg Pace') or '').strip()
            pace_unit = _detect_pace_unit(pace_str)
            title_hint = _guess_distance_unit_from_title(title, activity_type)

            if pace_unit == 'mph':
                distance_unit, confidence = 'mi', 'confirmed'
            elif pace_unit == 'kmh':
                distance_unit, confidence = 'km', 'confirmed'
            elif title_hint:
                distance_unit, confidence = title_hint, 'guessed'
            else:
                distance_unit, confidence = None, 'unknown'

            try:
                distance = float(row.get('Distance') or 0)
            except ValueError:
                distance = None

            try:
                calories = int(float(row.get('Calories') or 0))
            except ValueError:
                calories = None

            def _int_or_none(key):
                v = row.get(key)
                try:
                    return int(v) if v not in (None, '') else None
                except ValueError:
                    return None

            results.append({
                'activity_type':    activity_type,
                'title':            title,
                'date':             date_iso,
                'time_of_day':      time_of_day,
                'date_raw':         date_raw,
                'distance':         distance,
                'distance_unit':    distance_unit,
                'distance_unit_confidence': confidence,
                'calories':         calories,
                'duration_seconds': _parse_duration_to_seconds(row.get('Time')),
                'avg_hr':           _int_or_none('Avg HR'),
                'max_hr':           _int_or_none('Max HR'),
                'avg_pace_raw':     pace_str,
                'best_pace_raw':    (row.get('Best Pace') or '').strip(),
                'elevation_gain_m': _int_or_none('Elevation Gain'),
                'elevation_loss_m': _int_or_none('Elevation Loss'),
                'avg_cadence':      _int_or_none('Avg Cadence'),
                'max_cadence':      _int_or_none('Max Cadence'),
                'strokes':          _int_or_none('Strokes'),  # swimming only
                'training_effect':  row.get('Training Effect'),
                'source':           'GARMIN',
            })

    return results


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print('Usage: python garmin_activities.py <path-to-activities-export.csv>')
        sys.exit(1)
    activities = parse_garmin_activities_csv(sys.argv[1])
    print(f'Parsed {len(activities)} activities:\n')
    for a in activities:
        flag = '' if a['distance_unit_confidence'] == 'confirmed' else f" ⚠ unit {a['distance_unit_confidence']}"
        print(f"  {a['date']} — {a['activity_type']}: {a['distance']}{a['distance_unit'] or '?'}{flag}, "
              f"{a['calories']}kcal, {a['duration_seconds']}s, avg HR {a['avg_hr']}")
