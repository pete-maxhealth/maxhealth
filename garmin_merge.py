"""
garmin_merge.py — merges Garmin wellness + activities data into the pipeline's
daily combined structure, applying the precedence rule Pete confirmed:
Garmin's own recorded activity calories override the app's MET-based estimate
for any exercise session Garmin actually captured. Wellness fields (steps,
resting HR, etc.) still go through the existing user-configurable device
precedence system already built into the app — this script only handles the
one new rule that's specifically about activity calories.
"""

import json
from garmin import parse_garmin_export
from garmin_activities import parse_garmin_activities_csv


def merge_garmin_day(wellness_row, activities_for_day, met_estimate_kcal=None):
    """
    Combines one day's wellness data with any Garmin-recorded activities for
    that date. Returns a dict with an explicit `activity_kcal_source` field so
    it's always traceable which number was actually used and why — never a
    silent substitution.
    """
    garmin_activity_kcal = sum(a['calories'] for a in activities_for_day if a['calories'])

    if activities_for_day and garmin_activity_kcal > 0:
        activity_kcal = garmin_activity_kcal
        source = 'GARMIN_RECORDED'
    elif met_estimate_kcal is not None:
        activity_kcal = met_estimate_kcal
        source = 'MET_ESTIMATE'
    else:
        activity_kcal = 0
        source = 'NONE'

    return {
        'date':                  wellness_row['date'] if wellness_row else activities_for_day[0]['date'],
        'steps':                 wellness_row['steps'] if wellness_row else None,
        'resting_hr':            wellness_row['resting_hr'] if wellness_row else None,
        'activity_kcal':         activity_kcal,
        'activity_kcal_source':  source,
        'met_estimate_kcal':     met_estimate_kcal,       # kept for comparison/audit even when overridden
        'garmin_activity_kcal':  garmin_activity_kcal if activities_for_day else None,
        'activities':            [a['activity_type'] for a in activities_for_day],
        'total_kcal_with_bmr':   (wellness_row['bmr_kcal'] + activity_kcal) if wellness_row else None,
    }


def run_merge(wellness_json_path, activities_csv_path, met_estimates=None):
    """
    met_estimates: optional {date: kcal} dict representing what the app's own
    MET-based calculation would have produced, for comparison — in production
    this would come from the app's actual activity log for that day, not a
    hardcoded dict.
    """
    met_estimates = met_estimates or {}

    wellness_days = parse_garmin_export(wellness_json_path)
    wellness_by_date = {d['date']: d for d in wellness_days}

    activities = parse_garmin_activities_csv(activities_csv_path)
    activities_by_date = {}
    for a in activities:
        activities_by_date.setdefault(a['date'], []).append(a)

    all_dates = sorted(set(wellness_by_date) | set(activities_by_date))
    merged = []
    for date in all_dates:
        merged.append(merge_garmin_day(
            wellness_by_date.get(date),
            activities_by_date.get(date, []),
            met_estimates.get(date),
        ))
    return merged


if __name__ == '__main__':
    # Simulating what the app's own MET-based estimates might have been for
    # these same days, purely so the precedence rule has something real to
    # override and the comparison is visible — not real app output.
    fake_met_estimates = {
        '2026-07-06': 210,   # app's own walking MET-estimate, higher than Garmin's real 145
        '2026-07-07': 280,   # app's own running MET-estimate, lower than Garmin's real 320
        '2026-07-09': 350,   # app's own cycling MET-estimate, lower than Garmin's real 390
    }

    results = run_merge(
        'test_garmin_wellness.json',
        'test_garmin_activities.csv',
        fake_met_estimates,
    )

    print(f"{'Date':<12} {'Steps':<7} {'RestHR':<7} {'Activity kcal':<14} {'Source':<16} {'MET est.':<9} {'Garmin real':<12} Activities")
    print("-" * 100)
    for r in results:
        print(f"{r['date']:<12} {str(r['steps'] or '-'):<7} {str(r['resting_hr'] or '-'):<7} "
              f"{r['activity_kcal']:<14} {r['activity_kcal_source']:<16} "
              f"{str(r['met_estimate_kcal'] or '-'):<9} {str(r['garmin_activity_kcal'] or '-'):<12} "
              f"{', '.join(r['activities']) or '-'}")
