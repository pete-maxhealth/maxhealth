#!/usr/bin/env python3
"""
extractors/withings.py
MaxHealth Pipeline — Withings Extractor

Reads a Withings Health Mate data export zip and extracts daily summaries.

Withings export structure (from Health Mate → Download My Data):
  raw_tracker_*      — activity: steps, distance, calories, elevation
  raw_sleep_*        — sleep: start/end, deep/light/REM/wake duration
  raw_heart_rate_*   — heart rate measurements
  raw_weight_*       — weight, fat%, muscle%, bone mass, hydration
  raw_spo2_*         — blood oxygen

Columns output (matching combined.csv schema):
  date, steps, distance_m, calories_active,
  sleep_duration, sleep_deep, sleep_light, sleep_rem, sleep_wake,
  hr_avg, hr_min, hr_max, hrv,
  weight, bmi, fat_pct, muscle_pct, spo2,
  source
"""

import csv
import io
import os
import sys
import zipfile
import glob
from collections import defaultdict
from datetime import datetime


def run(inbox, password=None, dry_run=False):
    """
    Pipeline entry point.
    Scans inbox for Withings export zip, extracts daily summaries.

    Handles two export formats from Health Mate:
      Legacy: raw_tracker_*.csv, raw_sleep_*.csv, raw_heart_rate_*.csv, raw_weight_*.csv
      New:    Activity-*.txt, Sleep-*.txt, Vital Signs-*.txt
    Also reads loose .txt files already extracted to the inbox folder.
    Returns list of dicts, one per date.
    """
    activity = {}
    sleep    = {}
    heartrate = {}
    weight   = {}
    spo2     = {}

    # ── Check for loose Activity/Sleep/Vital Signs files in inbox (.txt or .csv) ──
    loose_files = (
        glob.glob(os.path.join(inbox, 'Activity-*.txt')) +
        glob.glob(os.path.join(inbox, 'Activity-*.csv')) +
        glob.glob(os.path.join(inbox, 'Sleep-*.txt')) +
        glob.glob(os.path.join(inbox, 'Sleep-*.csv')) +
        glob.glob(os.path.join(inbox, 'Vital Signs-*.txt')) +
        glob.glob(os.path.join(inbox, 'Vital Signs-*.csv')) +
        glob.glob(os.path.join(inbox, 'Vital_Signs-*.csv'))
    )
    if loose_files:
        print(f"  [withings] Found {len(loose_files)} loose file(s) in inbox — reading directly", file=sys.stderr)
        for path in loose_files:
            name = os.path.basename(path).lower()
            with open(path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            if 'activity' in name:
                activity = _parse_activity_txt(content) or activity
            elif 'sleep' in name:
                sleep = _parse_sleep_txt(content) or sleep
            elif 'vital' in name or 'heart' in name or 'spo2' in name:
                hr, sp = _parse_vitals_txt(content)
                heartrate = hr or heartrate
                spo2 = sp or spo2

        if any([activity, sleep, heartrate, weight, spo2]):
            rows = _merge_daily(activity, sleep, heartrate, weight, spo2)
            print(f"  [withings] {len(rows)} daily records from loose files", file=sys.stderr)
            return rows

    # ── Find Withings zip ────────────────────────────────────
    zips = glob.glob(os.path.join(inbox, '*.zip'))

    # Priority 1: name clearly identifies Withings
    withings_zips = [z for z in zips if
                     os.path.basename(z).lower().startswith('export_') or
                     os.path.basename(z).lower().startswith('data_export') or
                     os.path.basename(z).lower().startswith('data_pet_') or
                     'withings' in os.path.basename(z).lower() or
                     'healthmate' in os.path.basename(z).lower()]

    # Priority 2: any zip that isn't a numeric Zepp zip or named for another device
    if not withings_zips:
        other_devices = ['ringconn', 'ring_', 'garmin', 'amazfit', 'zepp', 'oura', 'fitbit', 'data_pet']
        withings_zips = [z for z in zips if
                         not os.path.basename(z)[0].isdigit() and
                         not any(d in os.path.basename(z).lower() for d in other_devices)]

    # Priority 3: peek inside any remaining zip for Withings signatures
    if not withings_zips:
        for z in zips:
            try:
                with zipfile.ZipFile(z) as zf:
                    names = [n.lower() for n in zf.namelist()]
                    if any('raw_tracker' in n or 'raw_weight' in n or 'raw_sleep' in n
                           or 'activity' in n or 'vital' in n for n in names):
                        withings_zips.append(z)
                        break
            except Exception:
                pass

    if not withings_zips:
        print(f"  [withings] No Withings export found in {inbox}", file=sys.stderr)
        print(f"  [withings] Files in inbox: {[os.path.basename(f) for f in glob.glob(os.path.join(inbox,'*'))]}", file=sys.stderr)
        return []

    zip_path = max(withings_zips, key=os.path.getmtime)
    print(f"  [withings] Using: {os.path.basename(zip_path)}", file=sys.stderr)

    try:
        zf = zipfile.ZipFile(zip_path, 'r')
    except Exception as e:
        print(f"  [withings] Could not open zip: {e}", file=sys.stderr)
        return []

    with zf:
        names_lower = [n.lower() for n in zf.namelist()]

        # Detect format: new named csv/txt OR legacy raw_ csv
        # New format: Activity-*.csv, Sleep-*.csv, Vital Signs-*.csv (or .txt)
        has_new_format = any(
            ('activity' in n or 'vital signs' in n or 'vital_signs' in n) and
            (n.endswith('.csv') or n.endswith('.txt'))
            for n in names_lower
            if not n.startswith('raw_') and not n.startswith('aggregate')
        )
        has_legacy = any('raw_tracker' in n for n in names_lower)

        if has_new_format:
            print(f"  [withings] Detected new Health Mate export format (.csv)", file=sys.stderr)
            for name in zf.namelist():
                nl = name.lower()
                if nl.startswith('raw_') or nl.startswith('aggregate'):
                    continue  # Skip legacy files even if present
                content = zf.read(name).decode('utf-8-sig')
                if 'activity' in nl and (nl.endswith('.csv') or nl.endswith('.txt')):
                    activity = _parse_activity_txt(content) or activity
                elif 'sleep' in nl and (nl.endswith('.csv') or nl.endswith('.txt')):
                    sleep = _parse_sleep_txt(content) or sleep
                elif ('vital' in nl or 'heart' in nl or 'spo2' in nl) and (nl.endswith('.csv') or nl.endswith('.txt')):
                    hr, sp = _parse_vitals_txt(content)
                    heartrate = hr or heartrate
                    spo2 = sp or spo2
            # Also extract weight from weight.csv if present
            weight = _extract_weight_csv(zf) or weight
        elif has_legacy:
            print(f"  [withings] Detected legacy Health Mate export format", file=sys.stderr)
            activity  = _extract_activity(zf)
            sleep     = _extract_sleep(zf)
            heartrate = _extract_heartrate(zf)
            weight    = _extract_weight(zf)
            spo2      = _extract_spo2(zf)
        else:
            # Try aggregates format (data_PET_ zips with aggregates_steps.csv etc)
            has_aggregates = any('aggregates_steps' in n.lower() for n in zf.namelist())
            if has_aggregates:
                print(f"  [withings] Detected aggregates format", file=sys.stderr)
                activity  = _extract_aggregates(zf) or activity
                sleep     = _extract_sleep_csv(zf) or sleep
                heartrate = _extract_hr_csv(zf) or heartrate
                weight    = _extract_weight_csv(zf) or weight
                spo2      = _extract_spo2_csv(zf) or spo2
            else:
                activity  = _extract_activity(zf) or activity
                sleep     = _extract_sleep(zf) or sleep
                heartrate = _extract_heartrate(zf) or heartrate
                weight    = _extract_weight(zf) or weight
                spo2      = _extract_spo2(zf) or spo2

    if not any([activity, sleep, heartrate, weight, spo2]):
        print("  [withings] No data extracted", file=sys.stderr)
        return []

    rows = _merge_daily(activity, sleep, heartrate, weight, spo2)
    print(f"  [withings] {len(rows)} daily records assembled", file=sys.stderr)
    return rows


def _parse_activity_txt(content):
    """Parse Activity-Pete-*.txt: Date, Steps, Calories(kcal)"""
    result = {}
    try:
        reader = csv.DictReader(content.strip().splitlines())
        for row in reader:
            date = _date(row.get('Date') or row.get('date'))
            if not date:
                continue
            result[date] = {
                'steps':           _int(row.get('Steps') or row.get('steps')),
                'calories_active': _int(row.get('Calories(kcal)') or row.get('calories')),
            }
        if result:
            print(f"  [withings] Activity (txt): {len(result)} days", file=sys.stderr)
    except Exception as e:
        print(f"  [withings] Activity txt parse error: {e}", file=sys.stderr)
    return result


def _parse_sleep_txt(content):
    """
    Parse Sleep-Pete-*.txt:
    Start Time, End Time, Falling Asleep Time, Wake-up time,
    Sleep Time Ratio(%), Time Asleep(min),
    Sleep Stages - Awake(min), Sleep Stages - REM(min),
    Sleep Stages - Light Sleep(min), Sleep Stages - Deep Sleep(min)
    """
    result = {}
    try:
        reader = csv.DictReader(content.strip().splitlines())
        for row in reader:
            # Use Start Time date as the sleep date
            start = row.get('Start Time') or row.get('start_time') or ''
            date = _date(start[:10]) if start else None
            if not date:
                continue
            result[date] = {
                'sleep_duration': _int(row.get('Time Asleep(min)') or row.get('time_asleep')),
                'sleep_wake':     _int(row.get('Sleep Stages - Awake(min)')),
                'sleep_rem':      _int(row.get('Sleep Stages - REM(min)')),
                'sleep_light':    _int(row.get('Sleep Stages - Light Sleep(min)')),
                'sleep_deep':     _int(row.get('Sleep Stages - Deep Sleep(min)')),
            }
        if result:
            print(f"  [withings] Sleep (txt): {len(result)} days", file=sys.stderr)
    except Exception as e:
        print(f"  [withings] Sleep txt parse error: {e}", file=sys.stderr)
    return result


def _parse_vitals_txt(content):
    """
    Parse Vital Signs-Pete-*.txt:
    Date, Avg. Heart Rate(bpm), Min. Heart Rate(bpm), Max. Heart Rate(bpm),
    Avg. Spo2(%), Min. Spo2(%), Max. Spo2(%),
    Avg. HRV(ms), Min. HRV(ms), Max. HRV(ms)
    """
    heartrate = {}
    spo2 = {}
    try:
        reader = csv.DictReader(content.strip().splitlines())
        for row in reader:
            date = _date(row.get('Date') or row.get('date'))
            if not date:
                continue
            hr_avg = _int(row.get('Avg. Heart Rate(bpm)'))
            hr_min = _int(row.get('Min. Heart Rate(bpm)'))
            hr_max = _int(row.get('Max. Heart Rate(bpm)'))
            hrv    = _int(row.get('Avg. HRV(ms)'))
            # SpO2 comes as "96%" — strip %
            spo2_raw = str(row.get('Avg. Spo2(%)') or '').replace('%','').strip()
            spo2_val = _float(spo2_raw) if spo2_raw else None

            if hr_avg:
                heartrate[date] = {
                    'hr_avg': hr_avg,
                    'hr_min': hr_min,
                    'hr_max': hr_max,
                    'hrv':    hrv,
                }
            if spo2_val:
                spo2[date] = {'spo2': spo2_val}

        if heartrate:
            print(f"  [withings] Vitals (txt): {len(heartrate)} days HR, {len(spo2)} days SpO2", file=sys.stderr)
    except Exception as e:
        print(f"  [withings] Vitals txt parse error: {e}", file=sys.stderr)
    return heartrate, spo2


def _read_csv(zf, prefix):
    """Find and read the first CSV in the zip matching prefix."""
    for name in zf.namelist():
        if os.path.basename(name).startswith(prefix) and name.endswith('.csv'):
            raw = zf.read(name).decode('utf-8-sig')
            lines = raw.strip().splitlines()
            if len(lines) < 2:
                return []
            return list(csv.DictReader(lines))
    return []


def _extract_aggregates(zf):
    """Extract activity from aggregates_steps.csv"""
    rows = _read_csv(zf, 'aggregates_steps')
    result = {}
    for row in rows:
        date = _date(row.get('date') or row.get('Date'))
        if not date: continue
        result[date] = {
            'steps':           _int(row.get('value') or row.get('steps')),
        }
    # Also get calories
    cal_rows = _read_csv(zf, 'aggregates_calories_earned')
    for row in cal_rows:
        date = _date(row.get('date') or row.get('Date'))
        if not date: continue
        if date not in result: result[date] = {}
        result[date]['calories_active'] = _int(row.get('value'))
    if result:
        print(f"  [withings] Activity (aggregates): {len(result)} days", file=sys.stderr)
    return result


def _extract_sleep_csv(zf):
    """Extract sleep from sleep.csv"""
    rows = _read_csv(zf, 'sleep')
    result = {}
    for row in rows:
        start = row.get('startdate') or row.get('from') or row.get('date') or ''
        date  = _date(start[:10]) if start else None
        if not date: continue
        def sec_to_min(k): return round(_int(row.get(k) or 0) / 60) if row.get(k) else None
        deep  = sec_to_min('deepsleepduration')
        light = sec_to_min('lightsleepduration')
        rem   = sec_to_min('remsleepduration')
        wake  = sec_to_min('wakeupduration')
        result[date] = {
            'sleep_duration': (deep or 0) + (light or 0) + (rem or 0),
            'sleep_deep':     deep,
            'sleep_light':    light,
            'sleep_rem':      rem,
            'sleep_wake':     wake,
        }
    if result:
        print(f"  [withings] Sleep (csv): {len(result)} days", file=sys.stderr)
    return result


def _extract_hr_csv(zf):
    """Extract HR from raw_hr_hr.csv"""
    rows = _read_csv(zf, 'raw_hr_hr')
    by_date = defaultdict(list)
    for row in rows:
        date = _date(row.get('date') or row.get('Date') or row.get('timestamp') or (row.get('start') or '')[:10])
        hr   = _int(row.get('value') or row.get('heart_rate') or row.get('hr'))
        if date and hr and hr > 30:
            by_date[date].append(hr)
    result = {}
    for date, readings in by_date.items():
        result[date] = {
            'hr_avg': round(sum(readings)/len(readings)),
            'hr_min': min(readings),
            'hr_max': max(readings),
        }
    # HRV from raw_hr_HR RMS SD
    hrv_rows = _read_csv(zf, 'raw_hr_HR RMS SD')
    if not hrv_rows:
        hrv_rows = _read_csv(zf, 'raw_hr_HR_RMS_SD')
    for row in hrv_rows:
        date = _date((row.get('date') or row.get('Date') or row.get('start') or '')[:10])
        hrv  = _float(row.get('value'))
        if date and hrv:
            if date not in result: result[date] = {}
            result[date]['hrv'] = round(hrv)
    if result:
        print(f"  [withings] HR (csv): {len(result)} days", file=sys.stderr)
    return result


def _extract_weight_csv(zf):
    """Extract weight from weight.csv"""
    rows = _read_csv(zf, 'weight')
    result = {}
    for row in rows:
        date = _date(row.get('date') or row.get('Date'))
        if not date: continue
        result[date] = {
            'weight':     _float(row.get('weight') or row.get('Weight')),
            'bmi':        _float(row.get('bmi') or row.get('BMI')),
            'fat_pct':    _float(row.get('fat_ratio') or row.get('fat_mass_weight')),
            'muscle_pct': _float(row.get('muscle_mass') or row.get('muscle_mass_weight')),
        }
    if result:
        print(f"  [withings] Weight (csv): {len(result)} days", file=sys.stderr)
    return result


def _extract_spo2_csv(zf):
    """Extract SpO2 from manual_spo2.csv or aggregates_manual_spo2.csv"""
    rows = _read_csv(zf, 'manual_spo2') or _read_csv(zf, 'aggregates_manual_spo2')
    result = {}
    for row in rows:
        date = _date(row.get('date') or row.get('Date'))
        spo2 = _float(row.get('value') or row.get('spo2') or row.get('SPO2'))
        if date and spo2:
            result[date] = {'spo2': spo2}
    if result:
        print(f"  [withings] SpO2 (csv): {len(result)} days", file=sys.stderr)
    return result


def _extract_activity(zf):
    rows = _read_csv(zf, 'raw_tracker_')
    result = {}
    for row in rows:
        date = _date(row.get('date') or row.get('Date') or row.get('start'))
        if not date:
            continue
        result[date] = {
            'steps':           _int(row.get('steps') or row.get('Steps')),
            'distance_m':      _int(row.get('distance') or row.get('Distance')),
            'calories_active': _int(row.get('calories') or row.get('active_calories')),
        }
    if result:
        print(f"  [withings] Activity: {len(result)} days", file=sys.stderr)
    return result


def _extract_sleep(zf):
    rows = _read_csv(zf, 'raw_sleep_')
    result = {}
    for row in rows:
        date = _date(row.get('date') or row.get('from'))
        if not date:
            continue
        deep  = _int(row.get('deepsleepduration') or row.get('deep_sleep'))
        light = _int(row.get('lightsleepduration') or row.get('light_sleep'))
        rem   = _int(row.get('remsleepduration')   or row.get('rem_sleep'))
        wake  = _int(row.get('wakeupduration')      or row.get('wake'))
        # Withings reports in seconds — convert to minutes
        def to_min(v): return round(v / 60) if v else None
        result[date] = {
            'sleep_duration': (to_min(deep) or 0) + (to_min(light) or 0) + (to_min(rem) or 0),
            'sleep_deep':     to_min(deep),
            'sleep_light':    to_min(light),
            'sleep_rem':      to_min(rem),
            'sleep_wake':     to_min(wake),
        }
    if result:
        print(f"  [withings] Sleep: {len(result)} days", file=sys.stderr)
    return result


def _extract_heartrate(zf):
    rows = _read_csv(zf, 'raw_heart_rate_')
    by_date = defaultdict(list)
    for row in rows:
        date = _date(row.get('date') or row.get('timestamp'))
        hr   = _int(row.get('heart_rate') or row.get('value'))
        if date and hr and hr > 0:
            by_date[date].append(hr)

    result = {}
    for date, readings in by_date.items():
        result[date] = {
            'hr_avg': round(sum(readings) / len(readings)),
            'hr_min': min(readings),
            'hr_max': max(readings),
        }
    if result:
        print(f"  [withings] Heart rate: {len(result)} days", file=sys.stderr)
    return result


def _extract_weight(zf):
    rows = _read_csv(zf, 'raw_weight_')
    result = {}
    for row in rows:
        date = _date(row.get('date') or row.get('Date'))
        if not date:
            continue
        result[date] = {
            'weight':     _float(row.get('weight') or row.get('Weight')),
            'bmi':        _float(row.get('bmi') or row.get('BMI')),
            'fat_pct':    _float(row.get('fat_ratio') or row.get('fatmassweight')),
            'muscle_pct': _float(row.get('muscle_mass') or row.get('musclemass')),
        }
    if result:
        print(f"  [withings] Weight: {len(result)} days", file=sys.stderr)
    return result


def _extract_spo2(zf):
    rows = _read_csv(zf, 'raw_spo2_')
    by_date = defaultdict(list)
    for row in rows:
        date = _date(row.get('date') or row.get('timestamp'))
        val  = _float(row.get('spo2') or row.get('value'))
        if date and val and val > 0:
            by_date[date].append(val)

    result = {}
    for date, readings in by_date.items():
        result[date] = {'spo2': round(sum(readings) / len(readings), 1)}
    if result:
        print(f"  [withings] SpO2: {len(result)} days", file=sys.stderr)
    return result


def _merge_daily(activity, sleep, heartrate, weight, spo2):
    all_dates = sorted(set(
        list(activity) + list(sleep) + list(heartrate) + list(weight) + list(spo2)
    ))
    rows = []
    for date in all_dates:
        act = activity.get(date, {})
        slp = sleep.get(date, {})
        hr  = heartrate.get(date, {})
        wt  = weight.get(date, {})
        sp  = spo2.get(date, {})

        sources = []
        if act: sources.append('withings_activity')
        if slp: sources.append('withings_sleep')
        if hr:  sources.append('withings_hr')
        if wt:  sources.append('withings_weight')
        if sp:  sources.append('withings_spo2')

        rows.append({
            'date':            date,
            'steps':           act.get('steps'),
            'distance_m':      act.get('distance_m'),
            'calories_active': act.get('calories_active'),
            'sleep_duration':  slp.get('sleep_duration'),
            'sleep_deep':      slp.get('sleep_deep'),
            'sleep_light':     slp.get('sleep_light'),
            'sleep_rem':       slp.get('sleep_rem'),
            'sleep_wake':      slp.get('sleep_wake'),
            'hr_avg':          hr.get('hr_avg'),
            'hr_min':          hr.get('hr_min'),
            'hr_max':          hr.get('hr_max'),
            'hrv':             hr.get('hrv'),
            'weight':          wt.get('weight'),
            'bmi':             wt.get('bmi'),
            'fat_pct':         wt.get('fat_pct'),
            'muscle_pct':      wt.get('muscle_pct'),
            'spo2':            sp.get('spo2'),
            'source':          'withings',
        })
    return rows


def _date(val):
    if not val:
        return None
    val = str(val).strip()
    for fmt in ('%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%d/%m/%Y'):
        try:
            return datetime.strptime(val[:10], fmt[:len(val[:10])]).\
                   strftime('%Y-%m-%d')
        except ValueError:
            continue
    return val[:10] if len(val) >= 10 else None

def _int(val):
    try: return int(float(val)) if val not in (None, '', 'null') else None
    except: return None

def _float(val):
    try: return float(val) if val not in (None, '', 'null') else None
    except: return None
