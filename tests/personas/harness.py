"""Persona test harness: fresh server + empty data dir + headless Chromium.
Records console errors, page errors and failed requests for every persona run."""
import os, shutil, subprocess, sys, tempfile, time, socket
from contextlib import contextmanager
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@contextmanager
def fresh_server(port=5757):
    root = tempfile.mkdtemp(prefix='mh_persona_')
    app = os.path.join(root, 'app')
    shutil.copytree(REPO, app, ignore=shutil.ignore_patterns('.git', 'tests', '__pycache__', 'docs', 'apk'))
    os.makedirs(os.path.join(root, 'data', 'inbox'), exist_ok=True)
    log = open(os.path.join(root, 'server.log'), 'w')
    p = subprocess.Popen([sys.executable, 'server.py'], cwd=app, stdout=log, stderr=subprocess.STDOUT)
    for _ in range(50):
        try:
            socket.create_connection(('127.0.0.1', port), 0.2).close(); break
        except OSError: time.sleep(0.2)
    try:
        yield root
    finally:
        p.terminate(); p.wait(5)

class Findings(list):
    def add(self, sev, msg): self.append((sev, msg)); print(f'  [{sev}] {msg}')

def watch(page, findings):
    page.on('console', lambda m: findings.add('console-error', m.text[:200]) if m.type == 'error' else None)
    page.on('pageerror', lambda e: findings.add('JS-exception', str(e)[:200]))
    page.on('requestfailed', lambda r: findings.add('request-failed', f'{r.url[:90]} {r.failure}'))

import csv, io, json, zipfile
from datetime import date, timedelta

def days(n, end=None):
    end = end or date.today()
    return [(end - timedelta(days=i)).isoformat() for i in range(n - 1, -1, -1)]

def run_pipeline(root, *args):
    """Run update_health.py exactly as the server does, against root/data. Returns (rc, output)."""
    r = subprocess.run([sys.executable, os.path.join(root, 'app', 'update_health.py'), *args],
                       cwd=os.path.join(root, 'app'), capture_output=True, text=True, timeout=120)
    return r.returncode, r.stdout + r.stderr

def read_combined(root):
    p = os.path.join(root, 'data', 'tables', 'combined.csv')
    if not os.path.exists(p): return {}
    with open(p, newline='', encoding='utf-8') as f:
        return {r['date']: r for r in csv.DictReader(f)}

def write_hc_export(root, rows):
    with open(os.path.join(root, 'data', 'inbox', 'health_connect_export.json'), 'w') as f:
        json.dump(rows, f)

def write_ringconn_zip(root, per_day):
    """per_day: {date: dict(steps, kcal, sleep_min, deep, light, rem, awake, hr, hrmin, hrmax, hrv, spo2)}"""
    def mk(header, rows):
        s = io.StringIO(); w = csv.writer(s); w.writerow(header); [w.writerow(r) for r in rows]; return s.getvalue()
    act = mk(['Date', 'Steps', 'Calories(kcal)'], [[d, v['steps'], v['kcal']] for d, v in per_day.items()])
    slp = mk(['Start Time', 'Time Asleep(min)', 'Sleep Stages - Awake(min)', 'Sleep Stages - REM(min)',
              'Sleep Stages - Light Sleep(min)', 'Sleep Stages - Deep Sleep(min)'],
             [[f'{d} 23:10:00', v['sleep_min'], v['awake'], v['rem'], v['light'], v['deep']] for d, v in per_day.items()])
    vit = mk(['Date', 'Avg. Heart Rate(bpm)', 'Min. Heart Rate(bpm)', 'Max. Heart Rate(bpm)', 'Avg. HRV(ms)', 'Avg. Spo2(%)'],
             [[d, v['hr'], v['hrmin'], v['hrmax'], v['hrv'], v['spo2']] for d, v in per_day.items()])
    with zipfile.ZipFile(os.path.join(root, 'data', 'inbox', 'Data Export-Test-2026-01-01-2026-12-31.zip'), 'w') as z:
        z.writestr('Activity-Test-1.csv', act); z.writestr('Sleep-Test-1.csv', slp); z.writestr('Vital Signs-Test-1.csv', vit)
