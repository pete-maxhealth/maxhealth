#!/usr/bin/env python3
"""
MaxedHealth Pattern Detector (v2, Oct 2026)

Learns *your* routine from *your* data and reports it back honestly.

Principles (the first version broke all of these, see BACKLOG.md):
  * No fixed cut-offs for personal measures. HRV, sleep and steps are compared with the
    person's own baseline, never with a universal "Excellent / Good / Low" scale.
  * Every signal says how many days it is built from and stays "building" until it has enough.
  * Meal timing comes from the whole logged history, not just today.
  * Placeholder rows (restored-from-backup entries at 23:59) are ignored.
  * Descriptive only. Nothing here diagnoses anything or tells you to change what you do.

Public interface is unchanged: PatternDetector(master_csv, combined_csv, backup_json) with
generate_current_signals(), generate_day_2_signals() (alias), generate_full_pattern_report(),
infer_lifestyle_context().
"""

import csv
import json
import math
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional

MIN_MEAL_DAYS = 3        # days of meal times before a window is reported
MIN_NIGHTS = 3           # nights before a sleep baseline is reported
MIN_HRV_DAYS = 7         # days before HRV is compared with a baseline
MIN_STEP_DAYS = 7        # days before steps are compared with a baseline
TREND_DAYS = 7           # recent window for "this week vs usual"
CHANGE_FLAG = 0.20       # a 20% change from your usual is worth mentioning
MEAL_HISTORY_DAYS = 28
WEARABLE_HISTORY_DAYS = 30


def _hhmm_to_min(s) -> Optional[int]:
    """'07:45', '7:45', '2026-10-01 23:10:00' or '2026-10-01T23:10' -> minutes since midnight."""
    if not s:
        return None
    s = str(s).strip()
    if 'T' in s:
        s = s.split('T', 1)[1]
    elif ' ' in s:
        s = s.split(' ', 1)[1]
    try:
        parts = s.split(':')
        h, m = int(parts[0]), int(parts[1])
        if 0 <= h < 24 and 0 <= m < 60:
            return h * 60 + m
    except (ValueError, IndexError):
        pass
    return None


def _fmt(minutes: float) -> str:
    minutes = int(round(minutes)) % 1440
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def _circ_mean(minutes: List[int]) -> float:
    """Mean time of day, correct across midnight (23:50 and 00:10 average to 00:00)."""
    ang = [m / 1440 * 2 * math.pi for m in minutes]
    s = sum(math.sin(a) for a in ang) / len(ang)
    c = sum(math.cos(a) for a in ang) / len(ang)
    return (math.atan2(s, c) % (2 * math.pi)) / (2 * math.pi) * 1440


def _circ_spread(minutes: List[int]) -> float:
    """Typical distance (minutes) from the circular mean."""
    mu = _circ_mean(minutes)
    d = [min(abs(m - mu), 1440 - abs(m - mu)) for m in minutes]
    return statistics.pstdev(d) if len(d) > 1 else 0.0


def _num(v) -> Optional[float]:
    try:
        if v is None or str(v).strip() == '':
            return None
        return float(v)
    except (TypeError, ValueError):
        return None


class PatternDetector:
    def __init__(self, master_csv_path: str, combined_csv_path: str, today_log_json: str):
        self.master_csv = master_csv_path
        self.combined_csv = combined_csv_path
        self.today_log_json = today_log_json
        self.meals: List[Dict] = []
        self.wearable_data: Dict[str, Dict] = {}

    # ── dates ──────────────────────────────────────────────────────────
    def parse_date(self, date_str: str) -> Optional[datetime]:
        for fmt in ("%d/%m/%y", "%d/%m/%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(str(date_str).strip(), fmt)
            except ValueError:
                continue
        return None

    # ── loading ────────────────────────────────────────────────────────
    def load_meal_data(self, days_back: int = MEAL_HISTORY_DAYS) -> List[Dict]:
        """Meal times from the whole logged history (state.history[].log) plus today's log."""
        try:
            with open(self.today_log_json, 'r') as f:
                backup = json.load(f)
        except Exception:
            self.meals = []
            return []
        state = backup.get('state', backup) if isinstance(backup, dict) else {}
        today = datetime.now().date()
        cutoff = today - timedelta(days=days_back)
        meals: List[Dict] = []

        def add(date_obj, entry):
            t = _hhmm_to_min(entry.get('time'))
            desc = str(entry.get('description', '') or '')
            if t is None:
                return
            if entry.get('time') == '23:59' and 'Restored from server backup' in desc:
                return                                    # placeholder, not a real meal time
            if (_num(entry.get('kcal')) or 0) <= 0 and not desc.strip():
                return
            meals.append({'date': date_obj.strftime('%d/%m/%y'), 'time': _fmt(t), 'minutes': t,
                          'description': desc, 'kcal': _num(entry.get('kcal')) or 0})

        for day in state.get('history', []) or []:
            d = self.parse_date(day.get('date', ''))
            if d and cutoff <= d.date() <= today:
                for e in day.get('log', []) or []:
                    add(d, e)
        for e in state.get('todayLog', []) or []:
            add(datetime.combine(today, datetime.min.time()), e)
        self.meals = meals
        return meals

    def load_wearable_data(self, days_back: int = WEARABLE_HISTORY_DAYS) -> Dict[str, Dict]:
        """The most recent days_back dated rows of combined.csv, sorted by date (not file order)."""
        try:
            with open(self.combined_csv, 'r') as f:
                rows = list(csv.DictReader(f))
        except Exception:
            self.wearable_data = {}
            return {}
        dated = []
        for r in rows:
            d = self.parse_date(r.get('date', ''))
            if d:
                dated.append((d, r))
        dated.sort(key=lambda x: x[0])
        out: Dict[str, Dict] = {}
        for d, r in dated[-days_back:]:
            sleep = _num(r.get('sleep_duration'))          # minutes
            if sleep is not None and not (0 < sleep <= 1000):
                sleep = None                                 # impossible value: drop, don't average it in
            steps = _num(r.get('steps'))
            hrv = _num(r.get('hrv'))
            out[d.strftime('%Y-%m-%d')] = {
                'steps': int(steps) if steps and steps > 0 else 0,
                'sleep_duration': sleep or 0,
                'bedtime': r.get('bedtime', ''), 'wake_time': r.get('wake_time', ''),
                'hrv': hrv if hrv and hrv > 0 else 0,
                'sleep_deep': _num(r.get('sleep_deep')) or 0,
                'sleep_light': _num(r.get('sleep_light')) or 0,
                'sleep_rem': _num(r.get('sleep_rem')) or 0,
            }
        self.wearable_data = out
        return out

    # ── meals ──────────────────────────────────────────────────────────
    @staticmethod
    def _meal_label(minutes: float) -> str:
        if 4 * 60 <= minutes < 11 * 60:
            return 'Breakfast'
        if 11 * 60 <= minutes < 15 * 60 + 30:
            return 'Lunch'
        if 17 * 60 <= minutes < 22 * 60 + 30:
            return 'Dinner'
        return 'Snacks'

    def detect_meal_windows(self) -> Dict[str, str]:
        """Typical windows per meal across all logged days. Needs MIN_MEAL_DAYS days per window."""
        if not self.meals:
            return {}
        times = sorted((m['minutes'], m['date']) for m in self.meals)
        clusters, cur = [], [times[0]]
        for t in times[1:]:
            if t[0] - cur[-1][0] <= 90:
                cur.append(t)
            else:
                clusters.append(cur); cur = [t]
        clusters.append(cur)
        windows: Dict[str, List] = {}
        for c in clusters:
            days = {d for _, d in c}
            if len(days) < MIN_MEAL_DAYS:
                continue
            mins = [m for m, _ in c]
            label = self._meal_label(statistics.median(mins))
            windows.setdefault(label, []).extend(mins)
        out = {}
        for label in ('Breakfast', 'Lunch', 'Dinner', 'Snacks'):
            if label in windows:
                m = sorted(windows[label])
                lo, hi = m[len(m) // 10], m[-1 - len(m) // 10]      # trim the extremes
                out[label] = f"{_fmt(lo)}-{_fmt(hi)}"
        return out

    def meal_timing_summary(self) -> Dict[str, str]:
        """Typical first and last meal of the day (useful for overnight-fast planning)."""
        by_day: Dict[str, List[int]] = {}
        for m in self.meals:
            by_day.setdefault(m['date'], []).append(m['minutes'])
        # today is incomplete, so leave it out of "last meal"
        today = datetime.now().strftime('%d/%m/%y')
        full = {d: v for d, v in by_day.items() if d != today}
        if len(full) < MIN_MEAL_DAYS:
            return {'status': f"building ({len(full)} of {MIN_MEAL_DAYS} days)"}
        first = [min(v) for v in full.values()]
        last = [max(v) for v in full.values()]
        return {'typical_first_meal': _fmt(statistics.median(first)),
                'typical_last_meal': _fmt(statistics.median(last)),
                'days': str(len(full))}

    # ── sleep ──────────────────────────────────────────────────────────
    def detect_sleep_circadian(self) -> Dict[str, str]:
        """Your typical sleep, how regular it is, and how the last few nights compare. No grades."""
        nights = [(d, v) for d, v in sorted(self.wearable_data.items()) if v['sleep_duration'] > 0]
        if len(nights) < MIN_NIGHTS:
            return {'status': f"building ({len(nights)} of {MIN_NIGHTS} nights)"} if nights else {}
        durs = [v['sleep_duration'] for _, v in nights]
        med = statistics.median(durs)
        res = {'nights': str(len(nights)), 'duration': f"{int(med // 60)}h{int(med % 60):02d}m",
               'basis': 'your median'}
        beds = [m for m in (_hhmm_to_min(v['bedtime']) for _, v in nights) if m is not None]
        wakes = [m for m in (_hhmm_to_min(v['wake_time']) for _, v in nights) if m is not None]
        if len(beds) >= MIN_NIGHTS:
            res['typical_bedtime'] = _fmt(_circ_mean(beds))
            res['bedtime_spread'] = f"±{int(round(_circ_spread(beds)))} min"
        if len(wakes) >= MIN_NIGHTS:
            res['typical_wake'] = _fmt(_circ_mean(wakes))
        if len(beds) >= MIN_NIGHTS:
            sp = _circ_spread(beds)
            res['regularity'] = 'very regular' if sp <= 20 else ('fairly regular' if sp <= 45 else 'varies a lot')
        stages = [(v['sleep_deep'], v['sleep_light'], v['sleep_rem']) for _, v in nights if v['sleep_deep'] + v['sleep_light'] + v['sleep_rem'] > 0]
        if len(stages) >= MIN_NIGHTS:
            tot = [sum(s) for s in stages]
            res['typical_deep_pct'] = f"{statistics.median([s[0] / t * 100 for s, t in zip(stages, tot)]):.0f}%"
            res['typical_rem_pct'] = f"{statistics.median([s[2] / t * 100 for s, t in zip(stages, tot)]):.0f}%"
            res['stage_note'] = 'Wearables estimate sleep stages roughly; use for your own trend only.'
        if len(durs) >= TREND_DAYS + MIN_NIGHTS:
            recent, earlier = statistics.median(durs[-3:]), statistics.median(durs[:-3])
            if earlier and abs(recent - earlier) / earlier >= CHANGE_FLAG:
                res['recent_vs_usual'] = 'last 3 nights shorter than usual' if recent < earlier else 'last 3 nights longer than usual'
            else:
                res['recent_vs_usual'] = 'in line with your usual'
        return res

    # ── activity ───────────────────────────────────────────────────────
    def detect_activity_patterns(self) -> Dict[str, str]:
        """Your usual daily steps, weekday vs weekend, and this week against your usual."""
        days = [(d, v['steps']) for d, v in sorted(self.wearable_data.items()) if v['steps'] > 0]
        if not days:
            return {}
        steps = [s for _, s in days]
        res = {'days': str(len(steps)), 'usual_steps': f"{int(statistics.median(steps)):,}", 'basis': 'your median'}
        if len(steps) < MIN_STEP_DAYS:
            res['status'] = f"building ({len(steps)} of {MIN_STEP_DAYS} days)"
            return res
        wk = [s for d, s in days if self.parse_date(d).weekday() < 5]
        we = [s for d, s in days if self.parse_date(d).weekday() >= 5]
        if len(wk) >= 3 and len(we) >= 2:
            res['weekday_usual'] = f"{int(statistics.median(wk)):,}"
            res['weekend_usual'] = f"{int(statistics.median(we)):,}"
        if len(steps) >= TREND_DAYS + 3:
            recent = statistics.median(steps[-TREND_DAYS:]); earlier = statistics.median(steps[:-TREND_DAYS])
            if earlier and abs(recent - earlier) / earlier >= CHANGE_FLAG:
                res['this_week_vs_usual'] = 'noticeably higher than usual' if recent > earlier else 'noticeably lower than usual'
            else:
                res['this_week_vs_usual'] = 'in line with your usual'
        # an unusually active day is one well above YOUR usual, so flat weeks report none
        hi = statistics.median(steps) * 1.5
        res['unusually_active_days'] = f"{sum(1 for s in steps if s > hi)} of {len(steps)}"
        return res

    # ── HRV ────────────────────────────────────────────────────────────
    def detect_hrv_baseline(self) -> Dict[str, str]:
        """Your own HRV baseline and where the latest reading sits against it. No universal scale."""
        vals = [v['hrv'] for _, v in sorted(self.wearable_data.items()) if v['hrv'] > 0]
        if not vals:
            return {}
        latest = vals[-1]
        if len(vals) < MIN_HRV_DAYS:
            return {'latest_hrv': f"{latest:.0f}ms", 'status': f"building your baseline ({len(vals)} of {MIN_HRV_DAYS} days)"}
        base = vals[:-1]
        med = statistics.median(base)
        mad = statistics.median([abs(v - med) for v in base]) or max(med * 0.05, 1.0)
        band = max(mad * 1.4826 * 1.5, med * 0.08)           # about 1.5 usual spreads, never narrower than 8%
        if latest < med - band:
            pos = 'below your usual range'
        elif latest > med + band:
            pos = 'above your usual range'
        else:
            pos = 'within your usual range'
        return {'baseline_hrv': f"{med:.0f}ms", 'usual_range': f"{med - band:.0f}-{med + band:.0f}ms",
                'latest_hrv': f"{latest:.0f}ms", 'status': pos, 'days': str(len(vals)),
                'note': 'HRV differs a lot between people and devices, so only your own trend is meaningful.'}

    # ── assembly ───────────────────────────────────────────────────────
    def generate_current_signals(self) -> Dict:
        self.load_meal_data()
        self.load_wearable_data()
        meal_windows = self.detect_meal_windows()
        sleep = self.detect_sleep_circadian()
        activity = self.detect_activity_patterns()
        hrv = self.detect_hrv_baseline()
        meal_days = {m['date'] for m in self.meals}
        day_number = max(len(meal_days | set(self.wearable_data.keys())), 1)
        avail = {
            'meal_windows': bool(meal_windows),
            'sleep': bool(sleep.get('duration')),
            'sleep_regularity': bool(sleep.get('regularity')),
            'activity': bool(activity.get('usual_steps')) and 'status' not in activity,
            'hrv': bool(hrv.get('baseline_hrv')),
        }
        core = ['meal_windows', 'sleep', 'activity', 'hrv']
        ready = sum(1 for k in core if avail[k])
        if ready == 0:
            status = "Still building. Keep logging meals and syncing your devices; each signal says how many days it needs."
        elif ready < len(core):
            waiting = [k.replace('_', ' ') for k in core if not avail[k]]
            status = f"{ready} of {len(core)} signals ready, still building: {', '.join(waiting)}."
        else:
            status = f"All {len(core)} signals ready, compared with your own history."
        return {'timestamp': datetime.now().isoformat(),
                'confidence': 'learning' if ready < len(core) else 'established',
                'meal_windows': meal_windows, 'meal_timing': self.meal_timing_summary(),
                'sleep_circadian': sleep, 'activity_pattern': activity, 'hrv_baseline': hrv,
                'day_number': day_number, 'signals_available': avail, 'status': status}

    def generate_day_2_signals(self) -> Dict:
        """Old name kept so existing callers keep working."""
        return self.generate_current_signals()

    def generate_full_pattern_report(self) -> Dict:
        sig = self.generate_current_signals()
        return {'timestamp': sig['timestamp'],
                'confidence': 'high' if sig['confidence'] == 'established' and sig['day_number'] >= 14 else 'learning',
                'learned_patterns': {'meal_windows': sig['meal_windows'], 'meal_timing': sig['meal_timing'],
                                     'sleep_circadian': sig['sleep_circadian'], 'activity': sig['activity_pattern'],
                                     'hrv': sig['hrv_baseline']},
                'lifestyle_context': self.infer_lifestyle_context(),
                'day_number': sig['day_number'], 'status': sig['status']}

    def infer_lifestyle_context(self) -> Dict[str, str]:
        a = self.detect_activity_patterns()
        ctx = {}
        if 'unusually_active_days' in a:
            ctx['unusually_active_days'] = a['unusually_active_days']
        if 'this_week_vs_usual' in a:
            ctx['activity_this_week'] = a['this_week_vs_usual']
        return ctx


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 4:
        print("Usage: pattern_detector.py <master.csv> <combined.csv> <backup.json>")
        sys.exit(1)
    d = PatternDetector(sys.argv[1], sys.argv[2], sys.argv[3])
    print(json.dumps(d.generate_full_pattern_report(), indent=2))
