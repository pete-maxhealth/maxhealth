"""
extractors/manual.py

Reads data/inbox/manual_entry.json — written by server.py's own
/save-manual-entry and /save-manual-entries-bulk endpoints (Settings/Import
→ Manual Entry screen in maxhealth.html), NOT dropped in by the user like a
Zepp/Garmin export. This extractor's only job is to turn that file into the
same {date: row_dict} shape every other device produces, via the standard
run(inbox, password=None, dry_run=False) contract run_extractor() in
update_health.py calls.

Field mapping — deliberately matches SOURCE_FIELDS['manual'] in
update_health.py exactly: every real combined.csv column except 'date' and
'source' (widened 28/09/26 from the original 6 headline fields — see that
file's own comment on why). The Manual Entry screen only shows whichever of
these a person has actually opted into via their own "construct CSV"
template, so in practice most entries will still only ever carry a handful
of these keys - this file just needs to be ready to carry any of them.

Units: every minute-based field (sleep_duration, sleep_deep/light/rem/wake,
snoring_min) is written in MINUTES to match every other device's convention
and update_health.py's own VALIDATION_RANGES - the form itself may show
some of these in friendlier units to the person, but converts before this
file is ever written (see saveManualEntry() in maxhealth.html).

Deploy note: like amazfit.py/garmin.py/garmin_merge.py elsewhere in this
repo, this file's real home is app/extractors/manual.py on the device — a
folder OUTSIDE app/maxhealth/ (this git repo's checkout), per README.md's
own directory tree. mh_autoupdate.sh only resets app/maxhealth/ via git,
so it never reaches app/extractors/ — this file needs copying there by
hand once, the same way the other extractor files presumably were.
"""

import json
import os

# Kept as a literal list, deliberately not imported from update_health.py's
# SOURCE_FIELDS['manual'] — extractors are meant to be standalone modules
# run_extractor() loads dynamically (see update_health.py), and importing
# the pipeline's own module back into an extractor would be a real circular
# dependency the first time update_health.py imported extractors eagerly
# rather than dynamically. The two lists are meant to match exactly; if one
# changes, the other needs updating too (same manual-sync obligation that
# already exists between this file and server.py's own FIELD_NAMES).
MANUAL_FIELDS = (
    'weight', 'bmi', 'fat_pct', 'fat_mass_kg', 'muscle_pct', 'muscle_mass_kg',
    'bone_mass_kg', 'hydration_kg', 'water_pct', 'pwv',
    'hrv', 'hrv_min', 'hrv_max', 'spo2', 'spo2_min', 'spo2_max',
    'sleep_duration', 'sleep_deep', 'sleep_light', 'sleep_rem', 'sleep_wake',
    'sleep_onset', 'sleep_efficiency', 'sleep_hr_avg', 'sleep_hr_min', 'sleep_hr_max',
    'snoring_min', 'bedtime', 'wake_time',
    'steps', 'distance_m', 'calories_active', 'calories_passive', 'elevation_m',
    'hr_avg', 'hr_min', 'hr_max', 'hr_resting',
)


def run(inbox, password=None, dry_run=False):
    entry_path = os.path.join(inbox, 'manual_entry.json')

    if not os.path.exists(entry_path):
        # Normal, not an error — nothing has ever been saved through the
        # Manual Entry screen yet, or every past entry has already been
        # archived by a prior successful run (see update_health.py's
        # archive_inbox(), called the same way for every other device's
        # inbox file once it's been processed).
        return []

    try:
        with open(entry_path, 'r') as f:
            entries = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"  [manual] Could not read {entry_path}: {e}")
        return []

    if not isinstance(entries, list):
        print(f"  [manual] Expected a JSON list in {entry_path}, got {type(entries).__name__}")
        return []

    rows = []
    for entry in entries:
        date = entry.get('date')
        if not date:
            continue  # validate_row() in update_health.py rejects rows with no valid date anyway

        row = {'date': date}

        # Only include a field if the person actually typed a value for it -
        # an explicit null/missing means "no manual override for this
        # field", not zero. This is what lets manual entry sit first in
        # every metric's DEFAULT_PRECEDENCE (see update_health.py's own
        # comment on that) without blanking out every OTHER field on a date
        # just because one value was corrected - the form, the bulk CSV
        # path, and /save-manual-entry all already follow this same "omit
        # means don't touch" contract, this just carries it through.
        for field in MANUAL_FIELDS:
            if entry.get(field) is not None:
                row[field] = entry[field]

        rows.append(row)

    return rows
