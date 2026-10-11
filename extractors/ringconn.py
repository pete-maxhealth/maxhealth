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
        print(f"  [ringconn] Expected: 'Data Export-<name>-*.zip' with 3 CSV files", file=sys.stderr)
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
            'sleep_nap_min':   slp.get('sleep_nap_min'),
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


# v3.10.962: RingConn records ONE night as several sessions whenever you wake and drop off again (for example
# 22:18-04:25, then 05:30-08:18). Sessions used to be filed by their own START date, so one night was split across two
# dates and its second half, alone on the wake date, outranked Zepp for sleep and replaced the real night.
# Now: sessions are sorted by start time; a session that begins less than NAP_JOIN_GAP_MIN after the previous one ended
# is part of the same night (durations and stages added); a short session (under 3 h) that STARTS in daytime
# (08:00-18:59) is a nap, not part of a night. A night is filed under the day you WOKE (its end date), the same
# convention as every other source. Per date: the longest night is the night; other short ones go to sleep_nap_min;
# another long one (3 h or more) is ignored, as before.
NAP_MAX_MIN = 180
NAP_JOIN_GAP_MIN = 120

def _parse_dt(v):
    v = str(v or '').strip()
    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%dT%H:%M:%S'):
        try:
            return datetime.strptime(v[:19], fmt)
        except ValueError:
            continue
    return None

_STAGE_KEYS = ('sleep_wake', 'sleep_rem', 'sleep_light', 'sleep_deep')

def _add_stages(into, st):
    for k in _STAGE_KEYS:
        v = st.get(k)
        if v is not None:
            into[k] = (into.get(k) or 0) + v

def _parse_sleep(content):
    from datetime import timedelta
    result = {}
    try:
        reader = csv.DictReader(content.strip().splitlines())
        timed, untimed = [], []
        for row in reader:
            start = row.get('Start Time') or row.get('start_time') or row.get('Date') or ''
            if not start:
                continue
            start_str = str(start).strip()
            dt = _parse_dt(start_str)
            duration = _int(row.get('Time Asleep(min)') or row.get('time_asleep') or row.get('Duration'))
            stages = {
                'sleep_wake':  _int(row.get('Sleep Stages - Awake(min)') or row.get('Awake')),
                'sleep_rem':   _int(row.get('Sleep Stages - REM(min)') or row.get('REM')),
                'sleep_light': _int(row.get('Sleep Stages - Light Sleep(min)') or row.get('Light')),
                'sleep_deep':  _int(row.get('Sleep Stages - Deep Sleep(min)') or row.get('Deep')),
            }
            end = _parse_dt(row.get('End Time') or row.get('end_time'))
            if dt and not end and duration:
                end = dt + timedelta(minutes=duration + (stages['sleep_wake'] or 0))
            if dt and end:
                timed.append({'start': dt, 'end': end, 'dur': duration, 'st': stages})
            else:
                untimed.append({'date': dt.strftime('%Y-%m-%d') if dt else _date(start_str[:10]),
                                'dur': duration, 'st': stages})

        # Group the timed sessions into nights and naps.
        groups = []   # each: {'nap': bool, 'start', 'end', 'dur', 'st'}
        for x in sorted(timed, key=lambda t: t['start']):
            is_nap = bool(x['dur'] and x['dur'] < NAP_MAX_MIN and 8 <= x['start'].hour < 19)
            last = groups[-1] if groups else None
            if (not is_nap and last and not last['nap']
                    and (x['start'] - last['end']).total_seconds() / 60 <= NAP_JOIN_GAP_MIN):
                last['end'] = max(last['end'], x['end'])
                last['dur'] = (last['dur'] or 0) + (x['dur'] or 0)
                _add_stages(last['st'], x['st'])
                continue
            g = {'nap': is_nap, 'start': x['start'], 'end': x['end'], 'dur': x['dur'] or 0, 'st': {}}
            _add_stages(g['st'], x['st'])
            groups.append(g)

        by_date = {}
        for g in groups:
            by_date.setdefault(g['end'].strftime('%Y-%m-%d'), []).append(g)
        for u in untimed:     # no usable times: keep the old behaviour, filed under its own date, never joined
            if u['date']:
                by_date.setdefault(u['date'], []).append({'nap': False, 'dur': u['dur'] or 0, 'st': dict(u['st'])})

        for date, gl in by_date.items():
            nights = sorted([g for g in gl if not g['nap']], key=lambda g: g['dur'] or 0, reverse=True)
            nap = sum(g['dur'] or 0 for g in gl if g['nap'])
            if nights:
                main = nights[0]
                row = {'sleep_duration': main['dur'] or None}
                for k in _STAGE_KEYS: row[k] = main['st'].get(k)
                nap += sum(g['dur'] or 0 for g in nights[1:] if (g['dur'] or 0) < NAP_MAX_MIN)
            else:
                row = {'sleep_duration': None, **{k: None for k in _STAGE_KEYS}}
            row['sleep_nap_min'] = nap or None
            result[date] = row
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
