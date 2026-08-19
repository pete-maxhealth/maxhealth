#!/usr/bin/env python3
# MARKER: SW_ROUTE_FIX_2026-07-10 — if this line is missing, you have the wrong file
"""
MaxHealth - Local Server
Runs on localhost:5757 in Termux (auto-started via Termux:Boot).
Bridges the HTML app and the data pipeline — no Termux interaction needed.

Endpoints:
  GET  /ping              — health check
  GET  /combined          — serve combined.csv
  GET  /status            — pipeline run status + log
  GET  /run               — trigger pipeline (?device=all|withings|ringconn|amazfit&dry_run=true)
  GET  /sync              — full sync: move exports from Download, run pipeline, serve combined.csv
  GET  /inbox             — list files in inbox
  GET  /pattern-signals   — Day 2 signals for wearables (meal windows, sleep, activity, HRV)

Usage:
  cd /storage/emulated/0/maxhealth/app
  python server.py
"""

import os
import re
import sys
try:
    import pyzipper
    HAS_PYZIPPER = True
except ImportError:
    HAS_PYZIPPER = False
import json
import glob
import shutil
import subprocess
import threading
import http.server
import urllib.parse
import zipfile
from datetime import datetime

# ── Phase 14: Pattern Detection for Wearables ──────────────────────────────────
try:
    from pattern_detector import PatternDetector
    HAS_PATTERN_DETECTOR = True
except ImportError:
    HAS_PATTERN_DETECTOR = False

# ─── PATHS ────────────────────────────────────────────────────────────────────
APP_DIR    = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR   = os.path.dirname(APP_DIR)                        # /storage/emulated/0/maxhealth
DATA_DIR   = os.path.join(ROOT_DIR, 'data')
TABLES_DIR = os.path.join(DATA_DIR, 'tables')
INBOX_DIR  = os.path.join(DATA_DIR, 'inbox')
BACKUP_DIR = os.path.join(DATA_DIR, 'backup')
# Resolves via Termux's own storage symlink first (~/storage/downloads,
# created by termux-setup-storage) rather than trusting the hardcoded
# absolute path blindly. On virtually every real device this symlink
# points to exactly /storage/emulated/0/Download anyway - the actual
# value here doesn't usually change - but going through the symlink means
# a genuinely missing/never-granted storage permission shows up as a
# clear, specific error at startup, rather than the app silently scanning
# an inaccessible or wrong folder and just reporting "nothing found",
# which is much harder to diagnose (this is exactly what took real back-
# and-forth to track down when it happened, even though that particular
# case turned out to be a stale app folder, not this).
_TERMUX_DOWNLOADS_SYMLINK = os.path.expanduser('~/storage/downloads')
if os.path.isdir(_TERMUX_DOWNLOADS_SYMLINK):
    DOWNLOAD = _TERMUX_DOWNLOADS_SYMLINK
elif os.path.isdir('/storage/emulated/0/Download'):
    DOWNLOAD = '/storage/emulated/0/Download'
else:
    DOWNLOAD = '/storage/emulated/0/Download'  # fallback path even though it doesn't exist yet - move_exports_to_inbox() reports the read failure clearly rather than this line silently picking something wrong
    print("WARNING: Could not find the Downloads folder via ~/storage/downloads or /storage/emulated/0/Download.", file=sys.stderr)
    print("Run 'termux-setup-storage' and grant the permission prompt, then restart the server.", file=sys.stderr)
LOGS_DIR   = os.path.join(ROOT_DIR, 'logs')
COMBINED   = os.path.join(TABLES_DIR, 'combined.csv')
MASTER_CSV      = os.path.join(TABLES_DIR, 'master.csv')
LIBRARY_CSV     = os.path.join(TABLES_DIR, 'library.csv')
SUPPLEMENTS_CSV = os.path.join(TABLES_DIR, 'supplements.csv')
RECIPES_CSV     = os.path.join(TABLES_DIR, 'recipes.csv')
ROUTINES_CSV    = os.path.join(TABLES_DIR, 'routines.csv')
STRENGTH_CSV    = os.path.join(TABLES_DIR, 'strength.csv')

TRACKER    = os.path.join(APP_DIR, 'maxhealth.html')
LOG_FILE   = os.path.join(LOGS_DIR, 'pipeline.log')
PORT       = 5757

# ─── ENSURE FOLDER STRUCTURE ─────────────────────────────────────────────────
for _dir in [TABLES_DIR, INBOX_DIR, BACKUP_DIR, LOGS_DIR]:
    os.makedirs(_dir, exist_ok=True)

# ─── CORS HEADERS ─────────────────────────────────────────────────────────────
CORS = {
    'Access-Control-Allow-Origin':  '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
}

# ─── PIPELINE STATE ───────────────────────────────────────────────────────────
pipeline_lock    = threading.Lock()
pipeline_running = False
pipeline_log     = []
pipeline_result  = None   # 'ok' | 'error' | None


def _log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    line = f'[{ts}] {msg}\n'
    pipeline_log.append(line)
    print(line, end='', flush=True)


def move_exports_to_inbox():
    """
    Scan Download folder for wearable exports and move to inbox.
    Returns (moved_count, needs_zarchiver).
    Mirrors the logic in sync.sh.
    """
    os.makedirs(INBOX_DIR, exist_ok=True)
    moved = 0
    needs_zarchiver = False
    unmatched_zips = []  # zip files seen but not recognised as any known device - reported at the end so a mismatch is visible in-app immediately, not just as a silent "nothing found"
    unmatched_json = []  # same, for the Health Connect bridge app's JSON exports

    try:
        files = os.listdir(DOWNLOAD)
    except Exception as e:
        _log(f'Could not read Download folder: {e}')
        return 0, False

    for name in files:
        src  = os.path.join(DOWNLOAD, name)
        dest = os.path.join(INBOX_DIR, name)
        lower = name.lower()

        is_export = False

        # Zepp/Amazfit — numeric prefix zip
        if name[0].isdigit() and lower.endswith('.zip'):
            is_export = True
            needs_zarchiver = True

        # RingConn — Data Export-Pete-*.zip
        elif lower.startswith('data export') and lower.endswith('.zip'):
            is_export = True

        # Withings — real export filenames are data_{ACCOUNT_NAME}_{timestamp}.zip,
        # so a check hardcoded to one specific name ('data_pet_', from testing
        # only against Pete's own export) silently rejected every other family
        # member's real export with the exact same, correct file structure.
        # This is the same fix as extractors/withings.py's _looks_like_withings_zip -
        # duplicated here rather than imported since this file only needs the one
        # small check, not the rest of that module.
        elif any(lower.startswith(p) for p in ('export_', 'data_export', 'withings', 'healthmate')) \
                and lower.endswith('.zip'):
            is_export = True
        elif re.match(r'^data_[a-z]+_\d+\.zip$', lower):
            is_export = True

        # Health Connect bridge app — writes health_connect_export_*.json
        # directly (not a zip - JSON, since the bridge app controls its own
        # export format completely, unlike the other devices' proprietary
        # export tools).
        elif re.match(r'^health_connect_export_.*\.json$', lower):
            is_export = True

        if is_export:
            if os.path.exists(dest):
                _log(f'Skipped — {name} already in inbox')
            else:
                shutil.move(src, dest)
                _log(f'Moved {name} → inbox')
                moved += 1
        elif lower.endswith('.zip'):
            # A real zip that didn't match any known pattern - exactly the
            # situation that took a manual Python check on Jill's device to
            # diagnose last time, because the only feedback anyone had was
            # "nothing found in Download", with no way to see WHY a real file
            # sitting right there wasn't recognised. Reported below so this
            # is visible in the app's own Sync log directly, without needing
            # separate device access or a standalone script to find out.
            unmatched_zips.append((name, src))
        elif lower.endswith('.json'):
            # Same reasoning as unmatched_zips above, for the Health Connect
            # bridge app's JSON export specifically.
            unmatched_json.append((name, src))

    if moved == 0 and unmatched_zips:
        _log(f'Found {len(unmatched_zips)} zip file(s) in Download that don\'t match any known device pattern:')
        for name, path in unmatched_zips:
            try:
                size = os.path.getsize(path)
                size_str = f'{size:,} bytes'
            except Exception:
                size_str = 'size unknown'
            detail = f'  {name} ({size_str})'
            try:
                with zipfile.ZipFile(path) as zf:
                    inner = zf.namelist()
                    has_aggregates = any('aggregates_steps' in n.lower() for n in inner)
                    has_ringconn_activity = any('activity' in n.lower() and n.lower().endswith('.csv') for n in inner)
                    if has_aggregates:
                        detail += ' — opens fine, contains aggregates_steps.csv (looks like a genuine Withings export that the filename check missed - tell Max the exact filename above)'
                    elif has_ringconn_activity:
                        detail += ' — opens fine, contains an activity CSV (may be a RingConn export with an unexpected filename)'
                    else:
                        detail += f' — opens fine, {len(inner)} file(s) inside, no recognised device signature found'
            except Exception as e:
                detail += f' — could NOT open as a zip ({e}) - the download may be incomplete or corrupted, try exporting again'
            _log(detail)

    if moved == 0 and unmatched_json:
        _log(f'Found {len(unmatched_json)} JSON file(s) in Download that don\'t match the Health Connect export pattern:')
        for name, path in unmatched_json:
            try:
                size = os.path.getsize(path)
                size_str = f'{size:,} bytes'
            except Exception:
                size_str = 'size unknown'
            detail = f'  {name} ({size_str})'
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    parsed = json.load(f)
                if isinstance(parsed, dict) and 'days' in parsed:
                    detail += ' — opens fine, has a \'days\' key (looks like a genuine Health Connect export that the filename check missed - tell Max the exact filename above)'
                else:
                    detail += ' — opens fine as JSON, but no recognised Health Connect structure found'
            except Exception as e:
                detail += f' — could NOT parse as JSON ({e}) - the export may be incomplete, try syncing the bridge app again'
            _log(detail)

    # Check for pre-extracted Zepp folders
    zepp_dirs = ('ACTIVITY', 'SLEEP', 'HEARTRATE_AUTO')
    if any(os.path.isdir(os.path.join(INBOX_DIR, d)) for d in zepp_dirs):
        _log('Zepp pre-extracted folders found in inbox')
        needs_zarchiver = False

    return moved, needs_zarchiver


def run_pipeline(device=None, dry_run=False, auto_sync=False):
    """Run update_health.py in a background thread, capturing output."""
    global pipeline_running, pipeline_log, pipeline_result

    with pipeline_lock:
        if pipeline_running:
            return False
        pipeline_running = True
        pipeline_log = []
        pipeline_result = None

    def _run():
        global pipeline_running, pipeline_result

        try:
            # ── Move exports if auto_sync ──────────────────────────────────
            if auto_sync:
                _log('Step 1/2 — Scanning Download for exports...')
                moved, needs_zarchiver = move_exports_to_inbox()

                if needs_zarchiver:
                    _log('Zepp zip detected — AES-256 encrypted.')
                    _log('Extract with ZArchiver first, then sync again.')
                    _log('Open ZArchiver → navigate to inbox → tap zip → extract → enter Zepp password')
                    pipeline_result = 'needs_zarchiver'
                    return

                if moved == 0:
                    # Check inbox already has files
                    inbox_items = [f for f in os.listdir(INBOX_DIR) if f != 'old'] if os.path.exists(INBOX_DIR) else []
                    if not inbox_items:
                        _log('Nothing found in Download or inbox.')
                        _log('Export from your wearable app first, then sync again.')
                        pipeline_result = 'empty'
                        return
                    else:
                        _log(f'{len(inbox_items)} item(s) already in inbox')

                _log('Step 2/2 — Running pipeline...')
            else:
                _log('Running pipeline...')

            # ── Run pipeline ───────────────────────────────────────────────
            cmd = [sys.executable, os.path.join(APP_DIR, 'update_health.py')]
            if device:
                cmd += ['--device', device]
            if dry_run:
                cmd += ['--dry-run']

            _log(f'Command: {" ".join(cmd)}')

            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=APP_DIR
            )

            for line in proc.stdout:
                pipeline_log.append(line)

            proc.wait()

            if proc.returncode == 0:
                _log('Pipeline complete ✓')
                pipeline_result = 'ok'
            else:
                _log(f'Pipeline error (exit code {proc.returncode})')
                pipeline_result = 'error'

        except Exception as e:
            _log(f'Exception: {str(e)}')
            pipeline_result = 'error'
        finally:
            pipeline_running = False

    threading.Thread(target=_run, daemon=True).start()
    return True


# ─── REQUEST HANDLER ──────────────────────────────────────────────────────────
class MaxHealthHandler(http.server.BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        pass  # Suppress default request logging

    def send_json(self, data, status=200):
        body = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        for k, v in CORS.items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def send_cors(self):
        self.send_response(204)
        for k, v in CORS.items():
            self.send_header(k, v)
        self.end_headers()

    def do_OPTIONS(self):
        self.send_cors()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path   = parsed.path

        content_type = self.headers.get('Content-Type', '')
        try:
            length = int(self.headers.get('Content-Length', 0))
            raw = self.rfile.read(length) if length > 0 else b''
        except Exception:
            self.send_json({'error': 'Could not read body'}, 400)
            return

        # CSV endpoints — handle raw text directly
        if path in ('/save-library-csv', '/save-supplements-csv', '/save-recipes-csv', '/save-routines-csv', '/save-strength-csv'):
            try:
                csv_data = raw.decode('utf-8')
                os.makedirs(TABLES_DIR, exist_ok=True)
                targets = {
                    '/save-library-csv': LIBRARY_CSV,
                    '/save-supplements-csv': SUPPLEMENTS_CSV,
                    '/save-recipes-csv': RECIPES_CSV,
                    '/save-routines-csv': ROUTINES_CSV,
                    '/save-strength-csv': STRENGTH_CSV,
                }
                target = targets[path]
                with open(target, 'w', encoding='utf-8') as lf:
                    lf.write(csv_data)
                rows = len([l for l in csv_data.strip().split('\n') if l]) - 1
                self.send_json({'status': 'ok', 'rows': rows})
            except Exception as e:
                self.send_json({'error': str(e)}, 400)
            return

        try:
            body = json.loads(raw) if raw else {}
        except Exception:
            self.send_json({'error': 'Invalid JSON body'}, 400)
            return

        # ── POST /save-nutrition — save a single day row ──────────────────────
        if path == '/save-nutrition':
            date    = body.get('date', '').strip()
            kcal    = body.get('kcal', 0)
            protein = body.get('protein', 0)
            carbs   = body.get('carbs', 0)
            fat     = body.get('fat', 0)
            notes   = body.get('notes', '').strip()

            if not date or not kcal:
                self.send_json({'error': 'date and kcal are required'}, 400)
                return

            updated = save_nutrition_row(date, kcal, protein, carbs, fat, notes)
            self.send_json({
                'status': 'ok',
                'action': 'updated' if updated else 'added',
                'row': f"{date}|{kcal}|{protein}|{carbs}|{fat}|{notes}"
            })

        # ── POST /save-nutrition-bulk — save multiple rows at once ────────────
        elif path == '/save-nutrition-bulk':
            rows = body.get('rows', [])
            if not rows:
                self.send_json({'error': 'rows array is required'}, 400)
                return

            results = []
            for r in rows:
                date    = r.get('date', '').strip()
                kcal    = r.get('kcal', 0)
                protein = r.get('protein', 0)
                carbs   = r.get('carbs', 0)
                fat     = r.get('fat', 0)
                notes   = r.get('notes', '').strip()
                if date and kcal:
                    updated = save_nutrition_row(date, kcal, protein, carbs, fat, notes)
                    results.append({'date': date, 'action': 'updated' if updated else 'added'})

            self.send_json({'status': 'ok', 'saved': len(results), 'results': results})



        elif path == '/extract-zepp':
            if not HAS_PYZIPPER:
                self.send_json({'error': 'pyzipper not installed — run: pip install pyzipper --break-system-packages'}, 500)
                return
            try:
                password = body.get('password', '').strip()
                if not password:
                    self.send_json({'error': 'Password required'}, 400)
                    return
                # Find Zepp zips in inbox
                zepp_zips = []
                if os.path.exists(INBOX_DIR):
                    for name in os.listdir(INBOX_DIR):
                        if name[0].isdigit() and name.lower().endswith('.zip'):
                            zepp_zips.append(os.path.join(INBOX_DIR, name))
                if not zepp_zips:
                    self.send_json({'error': 'No Zepp zip found in inbox'}, 404)
                    return
                extracted = []
                errors = []
                for zip_path in zepp_zips:
                    try:
                        with pyzipper.AESZipFile(zip_path) as zf:
                            zf.pwd = password.encode('utf-8')
                            zf.extractall(INBOX_DIR)
                        extracted.append(os.path.basename(zip_path))
                        # Move zip to old
                        old_dir = os.path.join(INBOX_DIR, 'old')
                        os.makedirs(old_dir, exist_ok=True)
                        import shutil
                        shutil.move(zip_path, os.path.join(old_dir, os.path.basename(zip_path)))
                    except Exception as e:
                        errors.append(f"{os.path.basename(zip_path)}: {str(e)}")
                if errors and not extracted:
                    self.send_json({'error': 'Wrong password or corrupt zip: ' + '; '.join(errors)}, 400)
                else:
                    self.send_json({'status': 'ok', 'extracted': extracted, 'errors': errors})
            except Exception as e:
                self.send_json({'error': str(e)}, 500)

        # ── POST /save-full-backup — full JSON state, with rotation ───────────
        # BACKUP_DIR has existed since the folder structure was first set up
        # (created on every startup, line 59) but nothing ever actually wrote
        # to it - the 5 tables got real server persistence via their own CSV
        # endpoints, but the full JSON state (today's log, full history,
        # everything exportAll() already builds client-side) never had a
        # server-side home at all, only ever a local browser download.
        elif path == '/save-full-backup':
            try:
                os.makedirs(BACKUP_DIR, exist_ok=True)
                date_str = datetime.now().strftime('%Y-%m-%d')
                backup_path = os.path.join(BACKUP_DIR, f'maxhealth_backup_{date_str}.json')
                with open(backup_path, 'w', encoding='utf-8') as f:
                    json.dump(body, f, ensure_ascii=False)

                # 7-day rotation - same principle as the Settings Change Log
                # (keep the last week, not unbounded growth from routine use).
                # One file per calendar day, so at most 7 exist regardless of
                # how many times a save fires on any given day.
                existing = sorted(glob.glob(os.path.join(BACKUP_DIR, 'maxhealth_backup_*.json')))
                if len(existing) > 7:
                    for old_file in existing[:-7]:
                        try:
                            os.remove(old_file)
                        except Exception:
                            pass

                self.send_json({'status': 'ok', 'file': os.path.basename(backup_path), 'kept': min(len(existing), 7)})
            except Exception as e:
                self.send_json({'error': str(e)}, 500)

        else:
            self.send_json({'error': f'Unknown POST endpoint: {path}'}, 404)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path   = parsed.path
        params = urllib.parse.parse_qs(parsed.query)

        if path == '/ws-probe' and self.headers.get('Upgrade','').lower() == 'websocket':
            import hashlib, base64
            key = self.headers.get('Sec-WebSocket-Key','')
            accept = base64.b64encode(
                hashlib.sha1((key + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11').encode()).digest()
            ).decode()
            self.send_response(101)
            self.send_header('Upgrade', 'websocket')
            self.send_header('Connection', 'Upgrade')
            self.send_header('Sec-WebSocket-Accept', accept)
            for k, v in CORS.items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(bytes([0x88, 0x00]))
            return

        # ── Health check ──────────────────────────────────────────────────
        # ── GET /list-backups — dates available for restore ────────────────
        # Companion to /save-full-backup: that endpoint writes the files,
        # this one lets the client show the person what's actually available
        # before restoring, rather than blindly grabbing "the latest" with
        # no visibility. A destructive operation (restore overwrites
        # everything) deserves that visibility.
        if path == '/list-backups':
            try:
                os.makedirs(BACKUP_DIR, exist_ok=True)
                files = sorted(glob.glob(os.path.join(BACKUP_DIR, 'maxhealth_backup_*.json')), reverse=True)
                backups = []
                for f in files:
                    date_str = os.path.basename(f).replace('maxhealth_backup_', '').replace('.json', '')
                    backups.append({'date': date_str, 'size': os.path.getsize(f)})
                self.send_json({'backups': backups})
            except Exception as e:
                self.send_json({'error': str(e)}, 500)
            return

        # ── GET /system-status — self-update/watchdog diagnostics ──────────
        # Lets someone check whether auto-update and the watchdog are
        # genuinely working from inside the app itself - a single tap in
        # App Health Check - rather than needing Termux command-line access,
        # which is exactly the barrier that made this hard to debug
        # remotely (a non-technical user on a different device can't easily
        # be walked through typing terminal commands over a phone call).
        # Fixed, hardcoded commands only - no user input reaches subprocess,
        # so there's no injection risk despite this being a live shell call.
        if path == '/system-status':
            try:
                result = {}

                log_path = os.path.expanduser('~/mh_autoupdate.log')
                if os.path.exists(log_path):
                    with open(log_path, 'r', errors='replace') as f:
                        lines = f.readlines()
                    result['autoupdate_log_tail'] = ''.join(lines[-15:])
                    result['autoupdate_log_lines_total'] = len(lines)
                else:
                    result['autoupdate_log_tail'] = None

                try:
                    cron_out = subprocess.run(['crontab', '-l'], capture_output=True, text=True, timeout=5)
                    result['crontab'] = cron_out.stdout if cron_out.returncode == 0 else f'(crontab -l failed: {cron_out.stderr.strip()})'
                except Exception as e:
                    result['crontab'] = f'(could not run crontab -l: {e})'

                try:
                    crond_out = subprocess.run(['pgrep', '-f', 'crond'], capture_output=True, text=True, timeout=5)
                    result['crond_running'] = bool(crond_out.stdout.strip())
                except Exception as e:
                    result['crond_running'] = None
                    result['crond_check_error'] = str(e)

                try:
                    server_out = subprocess.run(['pgrep', '-f', 'python.*server.py'], capture_output=True, text=True, timeout=5)
                    result['server_process_count'] = len(server_out.stdout.strip().split('\n')) if server_out.stdout.strip() else 0
                except Exception as e:
                    result['server_process_count'] = None

                self.send_json(result)
            except Exception as e:
                self.send_json({'error': str(e)}, 500)
            return

        # ── GET /load-full-backup?date=YYYY-MM-DD — restore source ─────────
        # Defaults to the most recent backup if no date given. Read-only -
        # this just returns the JSON; the client decides what to do with it
        # (confirmation modal, then the actual restore into state/library/
        # recipes/routines happens entirely client-side).
        if path == '/load-full-backup':
            try:
                os.makedirs(BACKUP_DIR, exist_ok=True)
                date_param = params.get('date', [None])[0]
                if date_param:
                    backup_path = os.path.join(BACKUP_DIR, f'maxhealth_backup_{date_param}.json')
                    if not os.path.exists(backup_path):
                        self.send_json({'error': f'No backup found for {date_param}'}, 404)
                        return
                else:
                    files = sorted(glob.glob(os.path.join(BACKUP_DIR, 'maxhealth_backup_*.json')), reverse=True)
                    if not files:
                        self.send_json({'error': 'No backups exist yet'}, 404)
                        return
                    backup_path = files[0]
                with open(backup_path, 'r', encoding='utf-8') as f:
                    data = f.read()
                body = data.encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(body)))
                for k, v in CORS.items():
                    self.send_header(k, v)
                self.end_headers()
                self.wfile.write(body)
            except Exception as e:
                self.send_json({'error': str(e)}, 500)
            return


        if path == '/ping':
            self.send_json({'status': 'ok', 'version': '2.0', 'combined_exists': os.path.exists(COMBINED)})

        # ── Full sync (move exports + run pipeline) ───────────────────────
        elif path == '/sync':
            if pipeline_running:
                self.send_json({'status': 'running', 'message': 'Pipeline already running'})
                return
            run_pipeline(auto_sync=True)
            self.send_json({'status': 'started', 'message': 'Sync started — poll /status for progress'})

        # ── Run pipeline only (no Download scan) ─────────────────────────
        elif path == '/run':
            device  = params.get('device',  [None])[0]
            dry_run = params.get('dry_run', ['false'])[0].lower() == 'true'
            if pipeline_running:
                self.send_json({'error': 'Pipeline already running'}, 409)
                return
            run_pipeline(device=device, dry_run=dry_run)
            self.send_json({'status': 'started', 'device': device or 'all', 'dry_run': dry_run})

        # ── Pipeline status ───────────────────────────────────────────────
        elif path == '/status':
            self.send_json({
                'running': pipeline_running,
                'result':  pipeline_result,
                'log':     ''.join(pipeline_log[-100:]),
            })

        # ── Serve combined.csv ────────────────────────────────────────────
        elif path == '/combined':
            if not os.path.exists(COMBINED):
                self.send_json({'error': 'combined.csv not found — run sync first'}, 404)
                return
            with open(COMBINED, 'r', encoding='utf-8') as f:
                content = f.read()
            body = content.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/csv')
            self.send_header('Content-Length', str(len(body)))
            for k, v in CORS.items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(body)

        # Mirrors /combined exactly, for the same reason - strength.csv only
        # ever lives server-side (auto-saved on every workout log), so a
        # client-side "backup to Downloads" button needs a real way to fetch
        # it back, same as combined.csv already has.
        elif path == '/strength':
            if not os.path.exists(STRENGTH_CSV):
                self.send_json({'error': 'strength.csv not found — log a workout first'}, 404)
                return
            with open(STRENGTH_CSV, 'r', encoding='utf-8') as f:
                content = f.read()
            body = content.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/csv')
            self.send_header('Content-Length', str(len(body)))
            for k, v in CORS.items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(body)

        # ── Pattern Signals for Wearables (Phase 14) ─────────────────────
        # Generates Day 2 signals + full pattern reports from meal/wearable data
        # Used by Zepp OS watchapp and Wear OS companions
        elif path == '/pattern-signals':
            if not HAS_PATTERN_DETECTOR:
                self.send_json({'error': 'pattern_detector not available'}, 501)
                return
            
            try:
                # Find the most recent backup (for today's meal log)
                backup_files = sorted(glob.glob(os.path.join(BACKUP_DIR, 'maxhealth_backup_*.json')), reverse=True)
                backup_path = backup_files[0] if backup_files else None
                
                if not backup_path or not os.path.exists(COMBINED) or not os.path.exists(MASTER_CSV):
                    self.send_json({
                        'error': 'Required data files not found',
                        'needed': ['combined.csv', 'master.csv', 'recent backup']
                    }, 404)
                    return
                
                detector = PatternDetector(MASTER_CSV, COMBINED, backup_path)
                signals = detector.generate_day_2_signals()
                self.send_json(signals)
            except Exception as e:
                self.send_json({'error': f'Pattern detection failed: {str(e)}'}, 500)
            return

        # ── Inbox status ──────────────────────────────────────────────────
        elif path == '/inbox':
            items = []
            if os.path.exists(INBOX_DIR):
                items = [f for f in os.listdir(INBOX_DIR) if f != 'old']
            self.send_json({'items': items, 'count': len(items)})

        elif path == '/manifest.json':
            # Serve a localhost-specific manifest so PWA installs point to localhost:5757
            import json as _json
            manifest = {
                'name': 'MaxedHealth',
                'short_name': 'MaxedHealth',
                'description': 'Personal health intelligence — nutrition tracking, wearable data, AI meal logging.',
                'start_url': f'http://localhost:{PORT}',
                'scope': f'http://localhost:{PORT}',
                'display': 'standalone',
                'background_color': '#0a0c0f',
                'theme_color': '#0a0c0f',
                'orientation': 'portrait-primary',
                'icons': [
                    {'src': f'http://localhost:{PORT}/icons/icon-96.png',  'sizes': '96x96',   'type': 'image/png'},
                    {'src': f'http://localhost:{PORT}/icons/icon-192.png', 'sizes': '192x192', 'type': 'image/png', 'purpose': 'any maskable'},
                    {'src': f'http://localhost:{PORT}/icons/icon-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'any maskable'},
                ],
                'categories': ['health', 'fitness', 'medical']
            }
            body = _json.dumps(manifest).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/manifest+json')
            self.send_header('Content-Length', str(len(body)))
            for k, v in CORS.items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(body)

        elif path == '/sw.js':
            # Service worker must be served for Chrome to consider this page
            # installable as a PWA — this route was missing entirely, meaning
            # every registration attempt silently 404'd and Chrome correctly
            # refused to offer "Install" (it showed "This app cannot be
            # installed" instead). no-store here too, matching the reasoning
            # for maxhealth.html itself — a stuck stale service worker is
            # exactly the kind of bug that's painful to diagnose after the fact.
            sw_path = os.path.join(APP_DIR, 'sw.js')
            if not os.path.exists(sw_path):
                self.send_json({'error': 'sw.js not found at ' + sw_path}, 404)
                return
            with open(sw_path, 'rb') as f:
                body = f.read()
            self.send_response(200)
            self.send_header('Content-Type', 'application/javascript; charset=utf-8')
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
            self.send_header('Content-Length', str(len(body)))
            for k, v in CORS.items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(body)

        elif path.startswith('/icons/'):
            # Serve icon files from the maxhealth app directory
            icon_name = os.path.basename(path)
            icon_path = os.path.join(APP_DIR, 'icons', icon_name)
            if os.path.exists(icon_path):
                with open(icon_path, 'rb') as f:
                    body = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'image/png')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            else:
                self.send_json({'error': 'Icon not found'}, 404)

        elif path == '/' or path == '/maxhealth':
            if not os.path.exists(TRACKER):
                self.send_json({'error': 'maxhealth.html not found at ' + TRACKER}, 404)
                return
            with open(TRACKER, 'rb') as f:
                body = f.read()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
            self.send_header('Content-Length', str(len(body)))
            for k, v in CORS.items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(body)

        elif path.startswith('/docs/') or (path.endswith('.html') and path.count('/') == 1):
            # Serve any static HTML file directly in the maxhealth app
            # directory - previously only carer.html and
            # gbm_patient_guide.html were allowed by explicit name here,
            # meaning every other static page (why-free.html,
            # user-guide.html, changelog.html) 404'd with "Unknown endpoint"
            # despite genuinely existing on disk, simply because nobody had
            # manually added its filename to this list yet.
            #
            # APP_DIR is os.path.dirname(__file__) - i.e. it already IS the
            # maxhealth folder server.py itself lives in, not its parent.
            # The original code (and my first attempt at this fix) both
            # appended an extra 'maxhealth' segment on top of that, building
            # a path like ".../maxhealth/maxhealth/why-free.html" that never
            # existed - confirmed live via debug prints against the actual
            # running process before landing on this.
            safe = path.lstrip('/')
            allowed_dir = os.path.normpath(APP_DIR)
            file_path = os.path.normpath(os.path.join(allowed_dir, safe))
            # Guards against path traversal (e.g. "/../../etc/passwd.html")
            # now that this accepts any filename rather than a fixed list -
            # the resolved path must still land inside the intended directory.
            if file_path.startswith(allowed_dir) and os.path.exists(file_path) and file_path.endswith('.html'):
                with open(file_path, 'rb') as f:
                    body = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(body)))
                for k, v in CORS.items():
                    self.send_header(k, v)
                self.end_headers()
                self.wfile.write(body)
            else:
                self.send_json({'error': f'Unknown endpoint: {path}'}, 404)

        elif path == '/save-library':
            # Broken, unreachable-in-practice dead code - LIBRARY_JSON was
            # never actually defined anywhere in this file, so this would
            # throw NameError if ever genuinely hit. Superseded entirely by
            # /save-library-csv (POST) and /library (GET), which the app
            # actually uses and which work correctly. Removed rather than
            # left as a broken trap for a future debugging session.
            self.send_json({'error': 'Deprecated - use /save-library-csv instead'}, 410)

        elif path == '/load-library':
            self.send_json({'error': 'Deprecated - use /library instead'}, 410)


        elif path in ('/library', '/supplements', '/recipes', '/routines', '/strength'):
            # Mirrors the save side's dict-driven approach exactly (see the
            # /save-*-csv handler above). Previously library/supplements/
            # strength each had their own near-identical GET handler, while
            # recipes and routines had NONE at all — meaning anything saved
            # there could never be read back once lost from localStorage,
            # even though it was safely sitting in the CSV the whole time.
            # One table, one handler, all five datasets treated consistently.
            csv_sources = {
                '/library':     LIBRARY_CSV,
                '/supplements': SUPPLEMENTS_CSV,
                '/recipes':     RECIPES_CSV,
                '/routines':    ROUTINES_CSV,
                '/strength':    STRENGTH_CSV,
            }
            source = csv_sources[path]
            if os.path.exists(source):
                with open(source, 'r', encoding='utf-8') as lf:
                    body = lf.read().encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'text/csv')
                self.send_header('Content-Length', str(len(body)))
                for k, v in CORS.items():
                    self.send_header(k, v)
                self.end_headers()
                self.wfile.write(body)
            else:
                self.send_json({'status': 'empty'})

        else:
            self.send_json({'error': f'Unknown endpoint: {path}'}, 404)


# ─── NUTRITION SAVE ──────────────────────────────────────────────────────────

def save_nutrition_row(date, kcal, protein, carbs, fat=0, notes=''):
    """
    Append or update a row in master.csv.
    Format: DD/MM/YY|kcal|protein|carbs|fat|notes
    If the date already exists, the row is updated in place.
    """
    os.makedirs(TABLES_DIR, exist_ok=True)
    row = f"{date}|{kcal}|{protein}|{carbs}|{fat}|{notes}"

    # Read existing rows
    existing = []
    if os.path.exists(MASTER_CSV):
        with open(MASTER_CSV, 'r', encoding='utf-8') as f:
            existing = [line.rstrip('\n') for line in f if line.strip()]

    # Check if date already exists
    updated = False
    for i, line in enumerate(existing):
        if line.startswith(date + '|'):
            existing[i] = row
            updated = True
            break

    if not updated:
        existing.append(row)

    # Sort by date (DD/MM/YY → sortable)
    def sort_key(line):
        parts = line.split('|')
        if not parts:
            return ''
        d = parts[0].split('/')
        if len(d) == 3:
            return f'20{d[2]}-{d[1]}-{d[0]}'
        return parts[0]

    existing.sort(key=sort_key)

    with open(MASTER_CSV, 'w', encoding='utf-8') as f:
        f.write('\n'.join(existing) + '\n')

    return updated


# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    os.makedirs(LOGS_DIR, exist_ok=True)
    print(f'''
╔══════════════════════════════════════╗
║       MAXHEALTH SERVER v2.0          ║
╚══════════════════════════════════════╝

  Listening on http://localhost:{PORT}

  Endpoints:
    /ping      — health check
    /sync      — full sync (move + pipeline)
    /status    — pipeline status + log
    /combined  — serve combined.csv
    /inbox     — inbox contents
    /run       — pipeline only
    /save-nutrition      (POST) — save/update one nutrition day
    /save-nutrition-bulk (POST) — save multiple nutrition days

  Auto-started via Termux:Boot.
  Press Ctrl+C to stop.
''')

    server = http.server.HTTPServer(('127.0.0.1', PORT), MaxHealthHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n  Server stopped.')
        server.server_close()


if __name__ == '__main__':
    main()
