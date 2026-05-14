#!/usr/bin/env python3
"""
extractors/ringconn.py
MaxHealth Pipeline — RingConn Extractor

Reads a RingConn CSV export and extracts daily summaries.

RingConn exports a CSV from the RingConn app (Profile → Export Data).
The export contains daily summary rows with sleep, HRV, SpO2, steps, HR.

Expected columns (RingConn app export):
  Date, Steps, Calories, Distance(m),
  SleepDuration(min), DeepSleep(min), LightSleep(min), REMSleep(min), WakeTime(min),
  AvgHR, MinHR, MaxHR, HRV, AvgSpO2
"""

import csv
import glob
import os
import sys
from datetime import datetime


def run(inbox, password=None, dry_run=False):
    """
    Pipeline entry point.
    Scans inbox for RingConn export.

    RingConn exports as 'Data Export-Pete-YYYY-MM-DD-YYYY-MM-DD.zip'
    containing exactly 3 files:
      Activity-Pete-*.csv  — steps, calories
      Sleep-Pete-*.csv     — sleep stages
      Vital Signs-Pete-*.csv — HR, SpO2, HRV

    Returns list of dicts, one per date.
    """
    import zipfile as _zf

    zips = glob.glob(os.path.join(inbox, '*.zip'))

    # Detect RingConn zip: 'Data Export-' prefix with exactly 3 csv files inside
    ringconn_zip = None
    for z in sorted(zips, key=os.path.getmtime, reverse=True):
        name = os.path.basename(z).lower()
        if not name.startswith('data export'):
            continue
        try:
            with _zf.ZipFile(z) as zf:
                inner = [n for n in zf.namelist() if n.lower().endswith('.csv')]
                if len(inner) == 3 and any('activity' in n.lower() for n in inner):
                    ringconn_zip = z
                    break
        except Exception:
            continue

    if not ringconn_zip:
        print(f"  [ringconn] No RingConn export found in {inbox}", file=sys.stderr)
        print(f"  [ringconn] Expected: 'Data Export-Pete-*.zip' with 3 CSV files", file=sys.stderr)
        print(f"  [ringconn] Files in inbox: {[os.path.basename(f) for f in glob.glob(os.path.join(inbox,'*'))]}", file=sys.stderr)
        return []

    print(f"  [ringconn] Using: {os.path.basename(ringconn_zip)}", file=sys.stderr)

    activity  = {}
    sleep     = {}
    vitals    = {}

    try:
        with _zf.ZipFile(ringconn_zip) as zf:
            for name in zf.namelist():
                nl = name.lower()
                content = zf.read(name).decode('utf-8-sig')
                if 'activity' in nl:
                    activity = _parse_activity(content)
                elif 'sleep' in nl:
                    sleep = _parse_sleep(content)
                elif 'vital' in nl:
                    vitals = _parse_vitals(content)
    except Exception as e:
        print(f"  [ringconn] Could not read zip: {e}", file=sys.stderr)
        return []

    if not any([activity, sleep, vitals]):
        print("  [ringconn] No data extracted", file=sys.stderr)
        return []

    # Merge by date
    all_dates = sorted(set(list(activity) + list(sleep) + list(vitals)))
    rows = []
    for date in all_dates:
        act = activity.get(date, {})
        slp = sleep.get(date, {})
        vit = vitals.get(date, {})
        rows.append({
            'date':            date,
            'steps':           act.get('steps'),
            'calories_active': act.get('calories'),
            'sleep_duration':  slp.get('sleep_duration'),
            'sleep_deep':      slp.get('sleep_deep'),
            'sleep_light':     slp.get('sleep_light'),
            'sleep_rem':       slp.get('sleep_rem'),
            'sleep_wake':      slp.get('sleep_wake'),
            'hr_avg':          vit.get('hr_avg'),
            'hr_min':          vit.get('hr_min'),
            'hr_max':          vit.get('hr_max'),
            'hrv':             vit.get('hrv'),
            'spo2':            vit.get('spo2'),
            'source':          'ringconn',
        })

    print(f"  [ringconn] {len(rows)} daily records assembled", file=sys.stderr)
    return rows


def _parse_activity(content):
    result = {}
    try:
        reader = csv.DictReader(content.strip().splitlines())
        for row in reader:
            date = _date(row.get('Date') or row.get('date'))
            if not date: continue
            result[date] = {
                'steps':    _int(row.get('Steps') or row.get('steps')),
                'calories': _int(row.get('Calories(kcal)') or row.get('Calories') or row.get('calories')),
            }
        print(f"  [ringconn] Activity: {len(result)} days", file=sys.stderr)
    except Exception as e:
        print(f"  [ringconn] Activity parse error: {e}", file=sys.stderr)
    return result


def _parse_sleep(content):
    result = {}
    try:
        reader = csv.DictReader(content.strip().splitlines())
        for row in reader:
            start = row.get('Start Time') or row.get('start_time') or row.get('Date') or ''
            date  = _date(start[:10]) if start else None
            if not date: continue
            result[date] = {
                'sleep_duration': _int(row.get('Time Asleep(min)') or row.get('time_asleep') or row.get('Duration')),
                'sleep_wake':     _int(row.get('Sleep Stages - Awake(min)') or row.get('Awake')),
                'sleep_rem':      _int(row.get('Sleep Stages - REM(min)') or row.get('REM')),
                'sleep_light':    _int(row.get('Sleep Stages - Light Sleep(min)') or row.get('Light')),
                'sleep_deep':     _int(row.get('Sleep Stages - Deep Sleep(min)') or row.get('Deep')),
            }
        print(f"  [ringconn] Sleep: {len(result)} days", file=sys.stderr)
    except Exception as e:
        print(f"  [ringconn] Sleep parse error: {e}", file=sys.stderr)
    return result


def _parse_vitals(content):
    hr_result  = {}
    try:
        reader = csv.DictReader(content.strip().splitlines())
        for row in reader:
            date = _date(row.get('Date') or row.get('date'))
            if not date: continue
            spo2_raw = str(row.get('Avg. Spo2(%)') or row.get('SpO2') or '').replace('%','').strip()
            hr_result[date] = {
                'hr_avg': _int(row.get('Avg. Heart Rate(bpm)') or row.get('HR')),
                'hr_min': _int(row.get('Min. Heart Rate(bpm)')),
                'hr_max': _int(row.get('Max. Heart Rate(bpm)')),
                'hrv':    _int(row.get('Avg. HRV(ms)') or row.get('HRV')),
                'spo2':   _float(spo2_raw) if spo2_raw else None,
            }
        print(f"  [ringconn] Vitals: {len(hr_result)} days", file=sys.stderr)
    except Exception as e:
        print(f"  [ringconn] Vitals parse error: {e}", file=sys.stderr)
    return hr_result

def _date(val):
    if not val:
        return None
    val = str(val).strip()
    for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d'):
        try:
            return datetime.strptime(val[:10], fmt).strftime('%Y-%m-%d')
        except ValueError:
            continue
    return val[:10] if len(val) >= 10 else None

def _int(val):
    try: return int(float(val)) if val not in (None, '', 'null') else None
    except: return None

def _float(val):
    try: return float(val) if val not in (None, '', 'null') else None
    except: return None
