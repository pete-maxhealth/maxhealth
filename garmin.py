"""
garmin.py — Garmin daily wellness data parser for the MaxedHealth pipeline.

Handles the two JSON schema variants seen in practice:
  1. Unofficial Connect API (get_user_summary) — what you'll get from a
     personal export or a script using the `garminconnect` Python wrapper.
  2. Official Health API webhook (dailySummaries array) — enterprise/partner
     access only, included here defensively in case Garmin's export format
     ever shifts toward this shape, or a webhook-based integration is added later.

Field names differ meaningfully between the two (restingHeartRate vs
restingHeartRateInBeatsPerMinute, activeCalories vs activeKilocalories, etc.)
so this reads via a field-alias map rather than hardcoding one schema's names.

Usage:
    from garmin import parse_garmin_day
    row = parse_garmin_day(json_obj)   # returns a normalised dict, or None
"""

import json


# Each canonical field maps to the possible source key names, checked in order.
# Add new aliases here if Garmin's export format changes rather than touching
# the parsing logic itself.
FIELD_ALIASES = {
    'date':               ['calendarDate'],
    'steps':              ['steps', 'totalSteps'],
    'distance_m':         ['distanceInMeters'],
    'resting_hr':         ['restingHeartRateInBeatsPerMinute', 'restingHeartRate'],
    'min_hr':             ['minHeartRateInBeatsPerMinute', 'minHeartRate'],
    'max_hr':             ['maxHeartRateInBeatsPerMinute', 'maxHeartRate'],
    'avg_hr':             ['averageHeartRateInBeatsPerMinute'],  # only present in the official schema
    'active_kcal':        ['activeKilocalories', 'activeCalories'],
    'bmr_kcal':           ['bmrKilocalories', 'bmrCalories'],
    'total_kcal':         ['totalCalories'],  # unofficial schema only; official gives active+bmr separately
    'floors_climbed':     ['floorsClimbed'],
    'moderate_active_s':  ['moderateIntensityDurationInSeconds'],
    'vigorous_active_s':  ['vigorousIntensityDurationInSeconds'],
    'avg_stress':         ['averageStressLevel'],
    'max_stress':         ['maxStressLevel'],
    'rem_sleep_s':        ['remSleepDurationInSeconds'],  # official schema only — unofficial summary has no sleep fields
}


def _get_field(day_obj, canonical_key):
    """Try each alias in order, return the first present (including 0, but not None)."""
    for alias in FIELD_ALIASES[canonical_key]:
        if alias in day_obj and day_obj[alias] is not None:
            return day_obj[alias]
    return None


def parse_garmin_day(day_obj):
    """
    Normalise a single day's Garmin wellness JSON (either schema variant) into
    the flat dict shape the rest of the pipeline expects.

    Returns None if the object doesn't look like a valid daily summary at all
    (missing date) — callers should skip rather than write a garbage row.
    """
    date = _get_field(day_obj, 'date')
    if not date:
        return None

    active_kcal = _get_field(day_obj, 'active_kcal') or 0
    bmr_kcal    = _get_field(day_obj, 'bmr_kcal') or 0
    total_kcal  = _get_field(day_obj, 'total_kcal')
    # Unofficial schema gives a direct total; official schema only gives the
    # two components — derive the total rather than leaving it blank.
    if total_kcal is None:
        total_kcal = active_kcal + bmr_kcal

    rem_sleep_s = _get_field(day_obj, 'rem_sleep_s')

    return {
        'date':             date,
        'steps':            _get_field(day_obj, 'steps'),
        'distance_m':       _get_field(day_obj, 'distance_m'),
        'resting_hr':       _get_field(day_obj, 'resting_hr'),
        'min_hr':           _get_field(day_obj, 'min_hr'),
        'max_hr':           _get_field(day_obj, 'max_hr'),
        'avg_hr':           _get_field(day_obj, 'avg_hr'),
        'active_kcal':      active_kcal,
        'bmr_kcal':         bmr_kcal,
        'total_kcal':       total_kcal,
        'floors_climbed':   _get_field(day_obj, 'floors_climbed'),
        'active_minutes':   round(((_get_field(day_obj, 'moderate_active_s') or 0)
                                  + (_get_field(day_obj, 'vigorous_active_s') or 0)) / 60),
        'avg_stress':       _get_field(day_obj, 'avg_stress'),
        'max_stress':       _get_field(day_obj, 'max_stress'),
        # Only the official schema carries any sleep field, and even that is
        # REM-only, not total sleep duration — this is NOT a substitute for
        # RingConn's sleep data, just an extra data point where available.
        'rem_sleep_hours':  round(rem_sleep_s / 3600, 2) if rem_sleep_s else None,
        'source':           'GARMIN',
    }


def parse_garmin_export(filepath):
    """
    Parse a Garmin bulk-export JSON file (or a single day's JSON, or a
    dailySummaries-wrapped payload) into a list of normalised day dicts.
    Handles: a bare list of day objects, a single day object, or the
    official {"dailySummaries": [...]} wrapper.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if isinstance(data, dict) and 'dailySummaries' in data:
        raw_days = data['dailySummaries']
    elif isinstance(data, list):
        raw_days = data
    elif isinstance(data, dict):
        raw_days = [data]
    else:
        raw_days = []

    parsed = []
    for day in raw_days:
        row = parse_garmin_day(day)
        if row:
            parsed.append(row)
        else:
            print(f'[garmin] Skipped a malformed day entry (no date field): {str(day)[:100]}')

    return parsed


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print('Usage: python garmin.py <path-to-garmin-export.json>')
        sys.exit(1)
    results = parse_garmin_export(sys.argv[1])
    print(f'Parsed {len(results)} day(s):')
    for r in results:
        print(f"  {r['date']}: {r['steps']} steps, resting HR {r['resting_hr']}, "
              f"{r['total_kcal']} kcal, avg stress {r['avg_stress']}")
