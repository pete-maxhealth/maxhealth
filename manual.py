"""
extractors/manual.py

Reads data/inbox/manual_entry.json — written by server.py's own
/save-manual-entry endpoint (Settings/Import → Manual Entry screen in
maxhealth.html), NOT dropped in by the user like a Zepp/Garmin export.
This extractor's only job is to turn that file into the same
{date: row_dict} shape every other device produces, via the standard
run(inbox, password=None, dry_run=False) contract run_extractor() in
update_health.py calls.

Field mapping — deliberately matches SOURCE_FIELDS['manual'] in
update_health.py exactly: weight, steps, hr_avg, hrv, spo2, sleep_duration.
Scope matches the manual entry form's own fields (raised directly: "weight,
steps, HR, HRV, SpO2, sleep duration") - headline figures only, not
withings-style body-comp breakdowns or sleep-stage detail the form doesn't
collect.

Units: sleep_duration is written in MINUTES to match every other device's
convention and update_health.py's own VALIDATION_RANGES (0-1440), same as
health_connect.py - the form itself may show hours to the person, but
converts to minutes before this file is ever written (see
saveManualEntry() in maxhealth.html).

Deploy note: like amazfit.py/garmin.py/garmin_merge.py elsewhere in this
repo, this file's real home is app/extractors/manual.py on the device — a
folder OUTSIDE app/maxhealth/ (this git repo's checkout), per README.md's
own directory tree. mh_autoupdate.sh only resets app/maxhealth/ via git,
so it never reaches app/extractors/ — this file needs copying there by
hand once, the same way the other extractor files presumably were.
"""

import json
import os


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
        # just because one value was corrected - the form and
        # /save-manual-entry both already follow this same "omit means
        # don't touch" contract, this just carries it through.
        for field in ('weight', 'steps', 'hr_avg', 'hrv', 'spo2', 'sleep_duration'):
            if entry.get(field) is not None:
                row[field] = entry[field]

        rows.append(row)

    return rows
