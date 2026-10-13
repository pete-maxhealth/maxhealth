"""Persona 135: pattern signals (pattern_detector.py v2) describe YOUR routine against YOUR baseline, say honestly when they are still building, never use universal grades, read meal times from the whole history, ignore placeholder meals, handle midnight and unsorted data."""
import sys, os, csv, json, tempfile; sys.path.insert(0, __file__.rsplit('/', 1)[0]); sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from datetime import datetime, timedelta
from harness import Findings
from pattern_detector import PatternDetector
f = Findings(); tmp = tempfile.mkdtemp(); today = datetime.now().date()
COLS = ['date', 'steps', 'sleep_duration', 'sleep_deep', 'sleep_light', 'sleep_rem', 'hrv', 'spo2', 'bedtime', 'wake_time']
def write(rows, name='c.csv', shuffle=False):
    p = os.path.join(tmp, name); rows = list(reversed(rows)) if shuffle else rows
    with open(p, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=COLS); w.writeheader(); [w.writerow({k: r.get(k, '') for k in COLS}) for r in rows]
    return p
def days(n, **kw):
    out = []
    for i in range(n, 0, -1):
        d = today - timedelta(days=i); r = {'date': d.isoformat(), 'steps': 6000, 'sleep_duration': 420, 'sleep_deep': 60, 'sleep_light': 250, 'sleep_rem': 110, 'hrv': 45, 'bedtime': '23:00', 'wake_time': '06:00'}
        r.update({k: (v(i) if callable(v) else v) for k, v in kw.items()}); out.append(r)
    return out
def backup(hist_days=0, today_times=(), extra=None):
    hist = []
    for i in range(1, hist_days + 1):
        d = (today - timedelta(days=i)).strftime('%d/%m/%y')
        hist.append({'date': d, 'log': [{'time': t, 'description': 'meal', 'kcal': 400} for t in ('08:00', '13:00', '19:00')]})
    if extra: hist.extend(extra)
    p = os.path.join(tmp, 'b.json'); json.dump({'state': {'history': hist, 'todayLog': [{'time': t, 'description': 'x', 'kcal': 300} for t in today_times]}}, open(p, 'w')); return p
M = os.path.join(tmp, 'm.csv'); open(M, 'w').write('date\n')
def run(rows, b=None, **k):
    return PatternDetector(M, write(rows, **k), b or backup()).generate_current_signals()

# 1. one big day in a flat fortnight is not "regular exercise"; no pattern label at all
rows = days(14, steps=lambda i: 9500 if i == 3 else 6000); a = run(rows)['activity_pattern']
if 'pattern' in a or 'Regular exercise' in json.dumps(a): f.add('BUG', f'exercise label returned {a}')
if a.get('usual_steps') != '6,000': f.add('BUG', f'usual steps {a.get("usual_steps")}')
# 2. HRV: personal baseline, no universal grades
h = run(days(14, hrv=45))['hrv_baseline']
if h.get('status') != 'within your usual range': f.add('BUG', f'stable HRV status {h}')
if any(w in json.dumps(h) for w in ('Excellent', 'Good', 'Fair', '"Low"')): f.add('BUG', 'HRV graded on a universal scale')
h = run(days(14, hrv=lambda i: 45 if i > 1 else 30))['hrv_baseline']
if h.get('status') != 'below your usual range': f.add('BUG', f'HRV drop not noticed {h}')
h = run(days(14, hrv=20))['hrv_baseline']
if h.get('status') != 'within your usual range': f.add('BUG', f'a naturally low HRV was judged low {h}')
h = run(days(4, hrv=45))['hrv_baseline']
if 'building' not in h.get('status', ''): f.add('BUG', f'HRV not marked building {h}')
# 3. meals from whole history, placeholder ignored, thin history stays quiet
b = backup(5, extra=[{'date': (today - timedelta(days=6)).strftime('%d/%m/%y'), 'log': [{'time': '23:59', 'description': 'Restored from server backup', 'kcal': 2000}]}])
mw = PatternDetector(M, write(days(3)), b).generate_current_signals()
if set(mw['meal_windows']) != {'Breakfast', 'Lunch', 'Dinner'}: f.add('BUG', f'meal windows {mw["meal_windows"]}')
if mw['meal_windows'].get('Breakfast') != '08:00-08:00': f.add('BUG', f'breakfast window {mw["meal_windows"]}')
if any('23:59' in v for v in mw['meal_windows'].values()): f.add('BUG', 'placeholder meal used')
if mw['meal_timing'].get('typical_first_meal') != '08:00' or mw['meal_timing'].get('typical_last_meal') != '19:00': f.add('BUG', f'meal timing {mw["meal_timing"]}')
if run(days(3), backup(2))['meal_windows']: f.add('BUG', 'windows reported from only two days')
# 4. midnight: 23:50 / 00:10 bedtimes average to midnight with a small spread
s = run(days(8, bedtime=lambda i: '23:50' if i % 2 else '00:10'))['sleep_circadian']
if s.get('typical_bedtime') not in ('00:00', '23:59', '00:01'): f.add('BUG', f'midnight mean {s.get("typical_bedtime")}')
if s.get('regularity') != 'very regular': f.add('BUG', f'regularity {s.get("regularity")}')
if any(w in json.dumps(s) for w in ('Excellent', '"Good"', '"Fair"')): f.add('BUG', 'sleep graded')
s = run(days(8, bedtime=lambda i: ['21:00', '01:30', '23:00', '03:00'][i % 4]))['sleep_circadian']
if s.get('regularity') != 'varies a lot': f.add('BUG', f'erratic bedtimes called {s.get("regularity")}')
# 5. unsorted file: latest rows still win; impossible sleep dropped
rows = days(12, steps=lambda i: 3000 if i > 7 else 9000); a = run(rows, shuffle=True)['activity_pattern']
if a.get('this_week_vs_usual') is None or 'higher' not in a.get('this_week_vs_usual', ''): f.add('BUG', f'shuffled rows trend {a}')
s = run(days(5, sleep_duration=lambda i: 5000 if i == 1 else 420))['sleep_circadian']
if s.get('duration') != '7h00m': f.add('BUG', f'impossible sleep value used {s}')
# 6. empty and tiny inputs never raise, and say they are building
try:
    e = PatternDetector(M, write([]), backup()).generate_current_signals()
    if e['confidence'] != 'learning' or 'building' not in e['status'].lower(): f.add('BUG', f'empty status {e["status"]}')
    PatternDetector('/nope', '/nope', '/nope').generate_full_pattern_report()
except Exception as x: f.add('BUG', f'raised on empty input: {x}')
t = run(days(2))
if t['confidence'] != 'learning' or t['signals_available']['hrv']: f.add('BUG', 'two days called established')
# 7. a full history reaches "established"
full = PatternDetector(M, write(days(14)), backup(14)).generate_current_signals()
if full['confidence'] != 'established': f.add('BUG', f'full data not established: {full["status"]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
