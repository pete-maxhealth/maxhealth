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
  POST /save-precedence   — merge source_precedence into pipeline_prefs.json (Settings → Device Precedence)
  GET  /manual-entry?date=YYYY-MM-DD — held (combined.csv) + manual values for a date (Manual Entry screen)
  POST /save-manual-entry — save a manual entry for a date, triggers a pipeline run
  POST /save-manual-entries-bulk — save many dates at once (CSV template upload), one pipeline run
  POST /clear-manual-entry — undo a manual override (date, fields?) — see its own docstring for real limits
  GET  /manual-entry-log  — audit trail of manual entry saves (capped, self-trimming)
  GET  /sleep-conflicts   — pending sleep-source overlaps awaiting a decision (comparison card)
  POST /resolve-sleep-conflict — apply/skip a sleep-overlap decision for one date

Usage:
  cd /storage/emulated/0/maxhealth/app/maxhealth
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
import csv
import glob
import shutil
import subprocess
import threading
import time
import http.server
import urllib.parse
import zipfile
from datetime import datetime, timedelta

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
# Same file update_health.py's own PREFS_FILE resolves to — both derive
# from the same MaxHealth root (this file's ROOT_DIR two levels up from
# app/maxhealth/, update_health.py's BASE one level up from app/), so this
# is deliberately not re-derived independently; a change to either path
# scheme needs both updated together or they'll silently diverge.
PREFS_JSON      = os.path.join(DATA_DIR, 'pipeline_prefs.json')
DEVICES_JSON    = os.path.join(DATA_DIR, 'devices.json')
ERROR_LOG_JSON  = os.path.join(DATA_DIR, 'error_log.json')
USER_EXT_DIR    = os.path.join(DATA_DIR, 'extractors')
# Written by the native launcher's HealthConnectBridge.kt (Kotlin, not this
# repo) when it detects two sleep sources genuinely overlapping for the same
# night and can't resolve it algorithmically — see that file's
# resolveSleepHours() doc comment for why. Same DATA_DIR both sides already
# share, so no new path convention is being introduced here.
SLEEP_CONFLICTS_JSON = os.path.join(DATA_DIR, 'sleep_conflicts_pending.json')
# Same file extractors/manual.py reads via run(inbox) - INBOX_DIR is this
# file's own already-derived path, so no separate cross-check comment is
# needed the way PREFS_JSON above needs one (that one is independently
# derived by update_health.py; this one is built from a path THIS file
# already owns).
MANUAL_ENTRY_JSON = os.path.join(INBOX_DIR, 'manual_entry.json')
# Audit trail of every manual entry save (28/09/26, raised directly: "A log
# file is produced and managed automatically so they don't grow too big") -
# deliberately separate from MANUAL_ENTRY_JSON itself, which only ever holds
# the CURRENT value per date (get overwritten, not appended - see
# save_manual_entry() below) and so can't answer "what did this used to
# say" or "when was this last changed" on its own.
MANUAL_ENTRY_LOG_JSON = os.path.join(DATA_DIR, 'manual_entry_log.json')
MAX_MANUAL_LOG_ENTRIES = 200  # trimmed on every write - see save_manual_entry()
# update_health.py's own per-date, per-field source attribution (same path
# it independently derives as FIELD_SOURCES_FILE — needs to stay in sync,
# same caveat as PREFS_JSON above). Read/cleared by clear_manual_entry()
# below so "undo" can actually reopen a field to a future real device sync,
# not just stop showing a stale manual value in this screen.
FIELD_SOURCES_JSON = os.path.join(DATA_DIR, 'field_sources.json')

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
pending_manual_run = False
pipeline_log     = []
pipeline_result  = None   # 'ok' | 'error' | None


def _is_garmin_zip(path):
    """Looks inside a zip for Garmin Connect's DI_CONNECT folder (extractors/garmin.py)."""
    try:
        import zipfile as _zf
        with _zf.ZipFile(path) as z:
            return any('di_connect' in n.lower() or 'di-connect' in n.lower() for n in z.namelist())
    except Exception:
        return False


def _log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    line = f'[{ts}] {msg}\n'
    pipeline_log.append(line)
    # pipeline_log (read by the app via /status) is the only copy this
    # actually needs — the print() below is a convenience for anyone
    # watching this process's own stdout (e.g. tailing a launcher log).
    # If stdout's reader is gone (BrokenPipeError/OSError — seen in
    # practice when the process backgrounding this server drops its
    # output pipe mid-sync), that must never be allowed to escape: it
    # previously killed the whole pipeline thread mid-scan, leaving
    # pipeline_running=False but pipeline_result stuck at None forever —
    # the app's poll loop has no terminal state to land on, so the UI
    # sits on "SYNCING..." indefinitely with no error ever surfaced,
    # even though pipeline_log (and therefore /status's log text) still
    # has the real detail, right up to and including this very message.
    try:
        print(line, end='', flush=True)
    except (BrokenPipeError, OSError):
        pass


def _load_devices():
    try:
        with open(DEVICES_JSON, 'r', encoding='utf-8') as f:
            d = json.load(f)
        return d if isinstance(d, dict) else {}
    except Exception:
        return {}


def _clean_devices(d):
    """Validate/normalise a devices.json body. Only plain strings, bounded sizes."""
    def names(v):
        out = []
        for x in (v if isinstance(v, list) else []):
            if isinstance(x, str) and x.strip() and len(x) <= 60 and x.strip() not in out:
                out.append(x.strip())
        return out[:50]
    pats = []
    for p in (d.get('patterns') if isinstance(d.get('patterns'), list) else []):
        if not isinstance(p, dict):
            continue
        dev = str(p.get('device', '')).strip()[:60]
        text = str(p.get('contains', '')).strip().lower()[:80]
        ext = str(p.get('ext', '')).strip().lower()[:10]
        if ext and not ext.startswith('.'):
            ext = '.' + ext
        if dev and text and len(pats) < 100:
            pats.append({'device': dev, 'contains': text, 'ext': ext})
    return {'custom': names(d.get('custom')), 'retired': names(d.get('retired')), 'patterns': pats}


def _matches_user_pattern(lower):
    for p in _load_devices().get('patterns', []):
        t = p.get('contains', '')
        e = p.get('ext', '')
        if t and t in lower and (not e or lower.endswith(e)):
            return p.get('device')
    return None


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

        # Garmin Connect "Export Your Data" bundle (a zip containing DI_CONNECT/...) or a
        # garmin*.json wellness file (01/10/26). The zip's own name is just a hash, so it
        # is recognised by LOOKING INSIDE it, not by filename.
        if (lower.endswith('.zip') and _is_garmin_zip(src)) or (lower.endswith('.json') and 'garmin' in lower):
            is_export = True

        # Zepp/Amazfit — numeric prefix zip
        elif name[0].isdigit() and lower.endswith('.zip'):
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

        # 01/10/26 — user-defined file patterns (Settings -> device precedence -> File pattern).
        # Lets a person teach the sweep a new device, or a changed export filename,
        # without a code change. Checked last so built-in rules keep their meaning.
        if not is_export and _matches_user_pattern(lower):
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
        global pipeline_running, pipeline_result, pending_manual_run

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
            # A manual correction saved while this run was in progress: apply it now.
            if pending_manual_run:
                pending_manual_run = False
                run_pipeline(device='manual')

    threading.Thread(target=_run, daemon=True).start()
    return True


# ── Scheduled jobs self-install (01/10/26) ────────────────────────────────────
# A fresh launcher install only gets the watchdog cron line, so a new user never got
# app updates or the 30-minute merge. On startup (Termux only) add whichever of those
# two lines is missing. Existing lines are never changed or removed.
def ensure_scheduled_jobs(force=False):
    home = os.path.expanduser('~')
    if not (force or os.environ.get('MH_FORCE_CRON_SETUP') or '/com.termux/' in home):
        return []
    ct = shutil.which('crontab')
    if not ct:
        return []
    added = []
    try:
        src = os.path.join(APP_DIR, 'mh_autoupdate.sh')
        dst = os.path.join(home, 'mh_autoupdate.sh')
        if os.path.exists(src) and not os.path.exists(dst):
            shutil.copyfile(src, dst); os.chmod(dst, 0o755); added.append('mh_autoupdate.sh')
        r = subprocess.run([ct, '-l'], capture_output=True, text=True, timeout=15)
        current = r.stdout if r.returncode == 0 else ''
        lines = current.rstrip('\n').split('\n') if current.strip() else []
        want = [
            ('update_health.py', '*/30 * * * * cd %s && python3 update_health.py >> %s 2>&1' % (APP_DIR, os.path.join(LOGS_DIR, 'cron_pipeline.log'))),
            ('mh_autoupdate', '5,35 * * * * ~/mh_autoupdate.sh'),
        ]
        if os.path.exists(os.path.join(home, 'mh_watchdog.sh')):
            want.append(('mh_watchdog', '* * * * * ~/mh_watchdog.sh'))
        for marker, line in want:
            if not any(marker in l and not l.lstrip().startswith('#') for l in lines):
                lines.append(line); added.append(marker)
        if any(a != 'mh_autoupdate.sh' for a in added):
            os.makedirs(LOGS_DIR, exist_ok=True)
            subprocess.run([ct, '-'], input='\n'.join(lines) + '\n', text=True, timeout=15)
        if added:
            print('  [setup] added scheduled jobs:', ', '.join(added))
    except Exception as e:
        print('  [setup] could not check scheduled jobs:', e)
    return added


# ── crond keep-alive (05/10/26) ───────────────────────────────────────────────
# Pete's phone: crond had silently died (auto-update log stopped dead on 2 Oct), so the
# watchdog that restarts this server and the update/merge jobs never ran again - the
# server then died and the app showed 'Site cannot be reached'. While this server is
# alive it now checks every minute that crond is running and restarts it if not, and
# re-takes the wake-lock once at startup. Termux only.
def crond_check_once():
    """Returns 'running', 'started', or 'skipped'."""
    pg = shutil.which('pgrep'); cd = shutil.which('crond')
    if not (pg and cd):
        return 'skipped'
    try:
        r = subprocess.run([pg, '-x', 'crond'], capture_output=True, text=True, timeout=5)
        if r.stdout.strip():
            return 'running'
        subprocess.Popen([cd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        try:
            with open(os.path.join(os.path.expanduser('~'), 'mh_watchdog.log'), 'a') as f:
                f.write('%s: crond was not running - started by server\n' % time.strftime('%a %b %d %H:%M:%S %Z %Y'))
        except Exception:
            pass
        return 'started'
    except Exception:
        return 'skipped'

def _crond_loop():
    wl = shutil.which('termux-wake-lock')
    if wl:
        try: subprocess.Popen([wl], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception: pass
    while True:
        crond_check_once()
        time.sleep(60)


# ── Health Connect auto-merge (01/10/26) ──────────────────────────────────────
# The launcher drops health_connect_export.json into the inbox every 30 minutes, but
# merging it into combined.csv depended on a separate cron job that a new install does
# not necessarily have. The server now notices a new/changed export itself and merges
# it, so a new user gets data flowing with no cron setup at all. Only the Health
# Connect extractor runs here (a single-device run never sweeps the rest of the inbox).
HC_WATCH_SECONDS = int(os.environ.get('MH_HC_WATCH_SECONDS', '60'))
_hc_last_seen = None

def _newest_hc_export_mtime():
    newest = None
    try:
        for n in os.listdir(INBOX_DIR):
            if n.lower().startswith('health_connect_export') and n.lower().endswith('.json'):
                m = os.path.getmtime(os.path.join(INBOX_DIR, n))
                if newest is None or m > newest:
                    newest = m
    except Exception:
        pass
    return newest

def hc_watch_once():
    """One check: merge if a Health Connect export is newer than the last one handled.
    Returns True if a merge was started."""
    global _hc_last_seen
    m = _newest_hc_export_mtime()
    if m is None or m == _hc_last_seen:
        return False
    if pipeline_running:
        return False            # try again next tick; do not mark as seen
    if run_pipeline(device='health_connect'):
        _hc_last_seen = m
        return True
    return False

def _hc_watch_loop():
    global _hc_last_seen
    time.sleep(5)
    while True:
        try:
            hc_watch_once()
        except Exception as e:
            print('  [hc-watch]', e)
        time.sleep(HC_WATCH_SECONDS)


def run_manual_pipeline():
    """Apply manual entries now, or queue it to run the moment the current run ends.
    Returns True if started immediately. (01/10/26: a correction saved during a sync was
    never applied, so the device value came back.)"""
    global pending_manual_run
    with pipeline_lock:
        busy = pipeline_running
        if busy:
            pending_manual_run = True
    if busy:
        return False
    return run_pipeline(device='manual')


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

        # ── POST /save-precedence — merge source_precedence into pipeline_prefs.json ──
        # The Settings → Device Precedence screen previously only wrote to the
        # browser's own localStorage, which update_health.py's load_prefs()
        # has no access to at all — every reorder made there was silently
        # doing nothing to real syncs. This is the missing other half: the
        # one place a browser save actually reaches the file the pipeline's
        # get_precedence() reads. Merges rather than overwrites pipeline_prefs.json
        # wholesale, since load_prefs()'s own docstring ("source precedence
        # etc.") leaves room for other keys to live in this same file later.
        if path == '/save-precedence':
            try:
                incoming = body.get('source_precedence', {})
                if not isinstance(incoming, dict):
                    self.send_json({'error': 'source_precedence must be an object'}, 400)
                    return
                os.makedirs(DATA_DIR, exist_ok=True)
                prefs = {}
                if os.path.exists(PREFS_JSON):
                    try:
                        with open(PREFS_JSON, 'r', encoding='utf-8') as f:
                            prefs = json.load(f)
                    except Exception:
                        prefs = {}  # corrupt/unreadable existing file — don't let it block a fresh save
                existing_prec = prefs.get('source_precedence', {})
                if not isinstance(existing_prec, dict):
                    existing_prec = {}
                existing_prec.update(incoming)
                prefs['source_precedence'] = existing_prec
                with open(PREFS_JSON, 'w', encoding='utf-8') as f:
                    json.dump(prefs, f, indent=2)
                self.send_json({'status': 'ok', 'source_precedence': existing_prec})
            except Exception as e:
                self.send_json({'error': str(e)}, 400)
            return

        # ── POST /log-client-error — the app reports a JS error it caught (01/10/26) ──
        # Body: {sig, kind, msg, src, line, v}. Stored de-duplicated by `sig` with a count and
        # first/last seen, capped at 200 entries. Messages are already truncated and have long
        # digit runs removed client-side, so no health values are kept.
        if path == '/log-client-error':
            try:
                sig = str(body.get('sig', ''))[:300]
                if not sig:
                    self.send_json({'error': 'sig required'}, 400)
                    return
                log = []
                if os.path.exists(ERROR_LOG_JSON):
                    try:
                        with open(ERROR_LOG_JSON, 'r', encoding='utf-8') as f:
                            log = json.load(f)
                        if not isinstance(log, list):
                            log = []
                    except Exception:
                        log = []
                now = datetime.now().isoformat(timespec='seconds')
                e = next((x for x in log if x.get('sig') == sig), None)
                if e:
                    e['count'] = e.get('count', 1) + 1
                    e['last'] = now
                    e['v'] = str(body.get('v', ''))[:20]
                else:
                    log.append({'sig': sig, 'kind': str(body.get('kind', ''))[:20], 'msg': str(body.get('msg', ''))[:200],
                                'src': str(body.get('src', ''))[:120], 'line': body.get('line'), 'v': str(body.get('v', ''))[:20],
                                'count': 1, 'first': now, 'last': now})
                    log = log[-200:]
                os.makedirs(DATA_DIR, exist_ok=True)
                with open(ERROR_LOG_JSON, 'w', encoding='utf-8') as f:
                    json.dump(log, f)
                self.send_json({'status': 'ok'})
            except Exception as ex:
                self.send_json({'error': str(ex)}, 400)
            return

        # ── POST /save-devices — custom devices, retired list, file patterns ──
        if path == '/save-devices':
            try:
                clean = _clean_devices(body if isinstance(body, dict) else {})
                os.makedirs(DATA_DIR, exist_ok=True)
                with open(DEVICES_JSON, 'w', encoding='utf-8') as f:
                    json.dump(clean, f, indent=2)
                self.send_json({'status': 'ok', **clean})
            except Exception as e:
                self.send_json({'error': str(e)}, 400)
            return

        # ── POST /save-manual-entry — Manual Entry screen ──────────────────────
        # Body: {date, weight?, steps?, hr_avg?, hrv?, spo2?, sleep_duration?} -
        # any field can be omitted or null, meaning "no manual override for
        # this field" (see save_manual_entry()'s own comment). Writes to the
        # real pipeline inbox and an audit log, then kicks off a pipeline run
        # the same way the app's own Sync button does, so the entry is folded
        # into combined.csv immediately rather than sitting in the inbox until
        # something else happens to trigger a sync.
        if path == '/save-manual-entry':
            try:
                date_str = (body.get('date') or '').strip()
                if not date_str:
                    self.send_json({'error': 'date is required'}, 400)
                    return
                fields = {k: body.get(k) for k in FIELD_NAMES}
                if not any(v is not None for v in fields.values()):
                    self.send_json({'error': 'At least one field must have a value'}, 400)
                    return
                fields, problems = prepare_manual_entry(date_str, fields)
                if not fields:
                    self.send_json({'error': 'Nothing saved: ' + '; '.join(problems or ['no usable values'])}, 400)
                    return
                cleaned = save_manual_entry(date_str, fields)
                triggered = run_manual_pipeline()
                self.send_json({'status': 'ok', 'date': date_str, 'saved': cleaned, 'rejected': problems, 'pipeline_triggered': triggered})
            except Exception as e:
                self.send_json({'error': str(e)}, 400)
            return

        # ── POST /save-manual-entries-bulk — CSV template upload ───────────────
        # Body: {entries: [{date, weight?, steps?, ...}, ...]} - the same shape
        # as a row-per-date "Download CSV template" file once parsed client-side
        # (see parseAndUploadManualCsv() in maxhealth.html). Exists so filling in
        # many days at once (the actual point of a downloadable template - "used
        # as a regular way to import for Apple users via cloud and for devices
        # without data export capabilities") doesn't mean N separate HTTP round
        # trips and N separate pipeline runs: every date is written via the same
        # save_manual_entry() a single date-at-a-time save uses (identical
        # validation, identical audit-log diffing, so a bulk upload leaves
        # exactly the same trail a person manually typing each day would have),
        # then the pipeline runs once at the end for the whole batch.
        if path == '/save-manual-entries-bulk':
            try:
                raw_entries = body.get('entries')
                if not isinstance(raw_entries, list) or not raw_entries:
                    self.send_json({'error': 'entries must be a non-empty list'}, 400)
                    return
                if len(raw_entries) > 400:
                    # Generous ceiling, not a real expected case - a person
                    # filling in a CSV template by hand isn't going to have
                    # thousands of rows, and this keeps one bad upload from
                    # rewriting MANUAL_ENTRY_JSON/the audit log hundreds of
                    # times in a single request.
                    self.send_json({'error': 'Too many rows in one upload (max 400) — split into smaller batches'}, 400)
                    return
                saved = []
                skipped = []
                rejected = []
                for raw in raw_entries:
                    date_str = (raw.get('date') or '').strip() if isinstance(raw, dict) else ''
                    if not date_str:
                        skipped.append(raw)
                        continue
                    fields = {k: raw.get(k) for k in FIELD_NAMES}
                    if not any(v is not None for v in fields.values()):
                        skipped.append(raw)  # blank row in the template — nothing to save, not an error
                        continue
                    fields, problems = prepare_manual_entry(date_str, fields)
                    if problems:
                        rejected.extend(f'{date_str}: {x}' for x in problems)
                    if not fields:
                        skipped.append(raw)
                        continue
                    cleaned = save_manual_entry(date_str, fields)
                    saved.append({'date': date_str, 'saved': cleaned})
                triggered = run_manual_pipeline() if saved else False
                self.send_json({'status': 'ok', 'saved': saved, 'skipped_count': len(skipped), 'rejected': rejected[:20], 'pipeline_triggered': triggered})
            except Exception as e:
                self.send_json({'error': str(e)}, 400)
            return

        # ── POST /clear-manual-entry — undo a manual override ──────────────────
        # Body: {date, fields?} - omit fields to clear the whole date. Read
        # clear_manual_entry()'s own docstring before assuming this reverts
        # combined.csv's value - it doesn't, and can't: the pipeline never
        # re-reads a device's already-archived export to recompute a field.
        # This only stops the manual value being re-applied/re-offered going
        # forward and re-opens that field to a future real sync.
        if path == '/clear-manual-entry':
            try:
                date_str = (body.get('date') or '').strip()
                if not date_str:
                    self.send_json({'error': 'date is required'}, 400)
                    return
                fields = body.get('fields')  # optional list — None/empty clears the whole date
                removed, entry_fully_removed = clear_manual_entry(date_str, fields)
                if not removed:
                    self.send_json({'error': f'No manual entry found for {date_str}'}, 404)
                    return
                self.send_json({'status': 'ok', 'date': date_str, 'cleared': removed, 'entry_fully_removed': entry_fully_removed})
            except Exception as e:
                self.send_json({'error': str(e)}, 400)
            return

        # ── POST /resolve-sleep-conflict — comparison card's per-instance choice ──
        # Body: {date, resolution}, resolution one of:
        #   {"type": "use_source", "source": "<matches a session's source>"} — use that
        #     session's own duration for the date, written the same way a Manual
        #     Entry save already works (save_manual_entry), so it goes through
        #     the real pipeline/precedence/audit-log machinery rather than a
        #     parallel path.
        #   {"type": "sum"} — the person judges both sessions genuinely happened
        #     (e.g. a device double-booked a nap awkwardly) — add them.
        #   {"type": "skip"} — don't record anything for this date; just clear
        #     it from the pending list so it stops being asked about today (it
        #     WILL be asked again if a future sync re-detects the same overlap
        #     for this date — see the "leave the switch active" note below).
        # Deliberately no "remember this choice for next time" option — every
        # future genuine overlap, even for the same two sources, gets its own
        # fresh prompt. Different nights can have different dead batteries,
        # different sensor misses; a rule that sounded right for one night
        # isn't guaranteed right for the next one, so nothing here is ever
        # auto-applied without being asked.
        if path == '/resolve-sleep-conflict':
            try:
                date_str = (body.get('date') or '').strip()
                resolution = body.get('resolution') or {}
                if not date_str:
                    self.send_json({'error': 'date is required'}, 400)
                    return
                res_type = resolution.get('type')
                if res_type not in ('use_source', 'sum', 'skip'):
                    self.send_json({'error': 'resolution.type must be use_source, sum, or skip'}, 400)
                    return

                pending = []
                if os.path.exists(SLEEP_CONFLICTS_JSON):
                    try:
                        with open(SLEEP_CONFLICTS_JSON, 'r', encoding='utf-8') as f:
                            loaded = json.load(f)
                        if isinstance(loaded, list):
                            pending = loaded
                    except Exception:
                        pending = []
                match = next((c for c in pending if c.get('date') == date_str), None)
                if not match:
                    self.send_json({'error': f'No pending sleep conflict found for {date_str}'}, 404)
                    return

                chosen_minutes = None
                chosen_label = 'skipped'
                if res_type == 'use_source':
                    source = resolution.get('source')
                    session = next((s for s in match.get('sessions', []) if s.get('source') == source), None)
                    if not session:
                        self.send_json({'error': f'source "{source}" not found in this conflict'}, 400)
                        return
                    chosen_minutes = session.get('duration_minutes')
                    chosen_label = source
                elif res_type == 'sum':
                    chosen_minutes = sum(s.get('duration_minutes', 0) for s in match.get('sessions', []))
                    chosen_label = 'sum of both'

                # Remove from the pending queue either way — resolved or
                # explicitly skipped, it shouldn't keep nagging on this same
                # detection. A fresh overlap (even same date, re-synced) gets
                # re-queued by the Kotlin side and will show up again.
                remaining = [c for c in pending if c.get('date') != date_str]
                os.makedirs(DATA_DIR, exist_ok=True)
                with open(SLEEP_CONFLICTS_JSON, 'w', encoding='utf-8') as f:
                    json.dump(remaining, f, indent=2)

                pipeline_triggered = False
                if chosen_minutes is not None:
                    save_manual_entry(date_str, {'sleep_duration': chosen_minutes})
                    pipeline_triggered = run_manual_pipeline()

                # Paired with the Kotlin side's detection log line — same file,
                # same format, so both halves of the story sit together.
                try:
                    os.makedirs(LOGS_DIR, exist_ok=True)
                    log_path = os.path.join(LOGS_DIR, 'pipeline.log')
                    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    line = f"{ts} | {'health_connect':<10} | {'sleep':<8} | {'OK':<6} | Sleep overlap for {date_str} resolved — chose {chosen_label}"
                    existing = []
                    if os.path.exists(log_path):
                        with open(log_path, 'r', encoding='utf-8') as f:
                            existing = f.read().splitlines()
                    combined = (existing + [line])[-500:]
                    with open(log_path, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(combined) + '\n')
                except Exception:
                    pass  # logging must never block the actual resolution

                self.send_json({
                    'status': 'ok',
                    'date': date_str,
                    'resolution': res_type,
                    'sleep_duration_minutes': chosen_minutes,
                    'pipeline_triggered': pipeline_triggered,
                })
            except Exception as e:
                self.send_json({'error': str(e)}, 400)
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
            # 01/10/26 - no longer needs pyzipper: extractors/_winzip_aes.py reads Zepp's
            # WinZip-AES zip with the standard library (pyzipper is still used when installed).
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
                        if HAS_PYZIPPER:
                            with pyzipper.AESZipFile(zip_path) as zf:
                                zf.pwd = password.encode('utf-8')
                                zf.extractall(INBOX_DIR)
                        else:
                            sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'extractors'))
                            import _winzip_aes
                            with _winzip_aes.open_aes_zip(zip_path, password) as zf:
                                for member in zf.namelist():
                                    if member.endswith('/'):
                                        continue
                                    norm = os.path.normpath(member)
                                    if os.path.isabs(norm) or norm.startswith('..'):
                                        continue   # never write outside the inbox
                                    dest = os.path.join(INBOX_DIR, norm)
                                    os.makedirs(os.path.dirname(dest), exist_ok=True)
                                    with open(dest, 'wb') as out:
                                        out.write(zf.read(member))
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
                # 01/10/26 - one file per day meant a browser wipe followed by opening the app
                # (which backs up "today") replaced the day's good backup with an EMPTY one,
                # destroying the very copy the restore screen exists to bring back. A new
                # backup that is far smaller than the one already saved today is refused.
                new_json = json.dumps(body, ensure_ascii=False)
                if os.path.exists(backup_path):
                    old_size = os.path.getsize(backup_path)
                    if old_size > 2000 and len(new_json.encode('utf-8')) < old_size * 0.5:
                        self.send_json({'status': 'kept-existing', 'file': os.path.basename(backup_path),
                                        'reason': 'new backup is under half the size of today\'s existing one - not replaced'})
                        return
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(new_json)

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

        # ── Health Connect sync age (01/10/26) ────────────────────────────
        # Newest health_connect_export*.json the launcher has written, whether
        # still in inbox/ or already archived to inbox/old/. Lets the app say
        # "last data 3h ago" so a silently stalled background sync is visible.
        elif path == '/selfcheck':
            try:
                import selfcheck as _sc
                self.send_json(_sc.run_selfcheck())
            except Exception as ex:
                self.send_json({'error': str(ex)}, 500)

        elif path == '/devices':
            d = _load_devices()
            clean = _clean_devices(d)
            clean['exists'] = os.path.exists(DEVICES_JSON)
            builtin = {'withings', 'ringconn', 'garmin', 'amazfit', 'health_connect', 'manual'}
            try:
                keys = sorted(f[:-3] for f in os.listdir(USER_EXT_DIR) if f.endswith('.py') and not f.startswith('_'))
            except Exception:
                keys = []
            try:
                with open(PREFS_JSON, 'r', encoding='utf-8') as f:
                    sp = json.load(f).get('source_precedence')
                if isinstance(sp, dict):
                    clean['source_precedence'] = sp
            except Exception:
                pass
            clean['user_extractors'] = [{'key': k, 'overrides_builtin': k in builtin} for k in keys]
            self.send_json(clean)

        elif path == '/sync-status':
            newest = None
            for d in (INBOX_DIR, os.path.join(INBOX_DIR, 'old')):
                try:
                    for n in os.listdir(d):
                        if n.lower().startswith('health_connect_export') and n.lower().endswith('.json'):
                            m = os.path.getmtime(os.path.join(d, n))
                            if newest is None or m > newest:
                                newest = m
                except OSError:
                    pass
            self.send_json({
                'health_connect_last': newest,
                'age_minutes': None if newest is None else int((time.time() - newest) / 60),
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
            # combined.csv changes every ~30 min via cron and the app polls
            # it on every open - explicit no-cache headers so no HTTP cache
            # anywhere (browser disk cache, an intermediate proxy) can ever
            # serve a stale copy, regardless of what caching options the
            # client's own fetch call does or doesn't set.
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            for k, v in CORS.items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(body)

        # ── GET /manual-entry?date=YYYY-MM-DD — prefill for the Manual Entry
        # screen. Returns what's already known for that date from two places:
        # `held` (combined.csv's current merged row - real device data, or a
        # prior manual entry's own effect once it's been through a sync) and
        # `manual` (the raw, currently-saved manual override for that date, if
        # any - lets the form distinguish "this field's shown value came from
        # a device" from "this is what I typed in last time", since a device
        # reading and Pete's own manual correction can genuinely differ).
        elif path == '/manual-entry':
            date_str = params.get('date', [''])[0].strip()
            if not date_str:
                self.send_json({'error': 'date query param is required'}, 400)
                return
            self.send_json({
                'date': date_str,
                'held': read_combined_row_for_date(date_str),
                'manual': get_manual_entry_for_date(date_str),
            })

        # ── GET /sleep-conflicts — pending sleep-source overlaps waiting on a
        # decision, queued by HealthConnectBridge.kt on the Kotlin side. Read
        # fresh on every app open (not cached), so a resolution made from
        # another device shows up immediately rather than the stale list
        # lingering until next sync.
        elif path == '/sleep-conflicts':
            conflicts = []
            if os.path.exists(SLEEP_CONFLICTS_JSON):
                try:
                    with open(SLEEP_CONFLICTS_JSON, 'r', encoding='utf-8') as f:
                        loaded = json.load(f)
                    if isinstance(loaded, list):
                        conflicts = loaded
                except Exception:
                    pass
            self.send_json({'conflicts': conflicts})

        # ── GET /manual-entry-log — audit trail for the Advanced
        # Troubleshooting Tools viewer (mirrors the Rollover/Settings-Change
        # log pattern already used elsewhere for viewing a capped log file).
        elif path == '/manual-entry-log':
            log_entries = []
            if os.path.exists(MANUAL_ENTRY_LOG_JSON):
                try:
                    with open(MANUAL_ENTRY_LOG_JSON, 'r', encoding='utf-8') as f:
                        loaded = json.load(f)
                    if isinstance(loaded, list):
                        log_entries = loaded
                except Exception:
                    pass
            self.send_json({'entries': log_entries})

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

        # Bundled third-party libraries (01/10/26) - Chart.js ships with the app so
        # charts work offline / on first run with no internet. Only exact filenames
        # that exist in lib/ are served (basename, so no path traversal).
        elif path.startswith('/lib/'):
            lib_name = os.path.basename(path)
            lib_path = os.path.join(APP_DIR, 'lib', lib_name)
            if lib_name.endswith('.js') and os.path.isfile(lib_path):
                with open(lib_path, 'rb') as f:
                    body = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'application/javascript; charset=utf-8')
                self.send_header('Content-Length', str(len(body)))
                self.send_header('Cache-Control', 'public, max-age=86400')
                self.end_headers()
                self.wfile.write(body)
            else:
                self.send_json({'error': 'Library not found'}, 404)

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


# ─── MANUAL DATA ENTRY (28/09/26) ──────────────────────────────────────────────
# Backs the Settings/Import → Manual Entry screen. Raised directly: "expand the
# pipeline setup to house a manual entry screen which gets any live measures
# from today or last recorded as initial values to overwrite... You could pick
# an entry date and the form would populate any held data." Three moving parts:
#   1. MANUAL_ENTRY_JSON - what extractors/manual.py itself reads (the actual
#      pipeline input, one entry per date, same shape as Health Connect's own
#      inbox file).
#   2. MANUAL_ENTRY_LOG_JSON - a separate append-only audit trail of every save
#      (what changed, when), capped at MAX_MANUAL_LOG_ENTRIES so it can't grow
#      unbounded - this is the "log file... managed automatically" part.
#   3. combined.csv itself, read directly for "populate any held data" - the
#      form should show what's already known for a date (from real devices),
#      not just what was typed manually before.
# Widened (28/09/26) from the original 6 headline fields to the full
# combined.csv column set (everything ALL_FIELDS in update_health.py has
# except 'date' and 'source') - the Manual Entry screen itself only shows
# whichever of these a person has opted into via their own "construct CSV"
# field template (mh_manual_template_fields in maxhealth.html), but the
# server side needs to accept any of them so someone with body-comp or
# sleep-stage data isn't capped at the original 6 just because that's all
# the first build wired up. Must be kept in sync with manual.py's own
# MANUAL_FIELDS and update_health.py's SOURCE_FIELDS['manual'] - all three
# are meant to describe exactly the same set.
FIELD_NAMES = [
    'weight', 'bmi', 'fat_pct', 'fat_mass_kg', 'muscle_pct', 'muscle_mass_kg',
    'bone_mass_kg', 'hydration_kg', 'water_pct', 'pwv',
    'hrv', 'hrv_min', 'hrv_max', 'spo2', 'spo2_min', 'spo2_max',
    'sleep_duration', 'sleep_deep', 'sleep_light', 'sleep_rem', 'sleep_wake',
    'sleep_onset', 'sleep_efficiency', 'sleep_hr_avg', 'sleep_hr_min', 'sleep_hr_max',
    'snoring_min', 'bedtime', 'wake_time',
    'steps', 'distance_m', 'calories_active', 'calories_passive', 'elevation_m',
    'hr_avg', 'hr_min', 'hr_max', 'hr_resting',
]

def read_combined_row_for_date(date_str):
    """Returns {field: value} for one date from combined.csv, or {} if not found/no file."""
    if not os.path.exists(COMBINED):
        return {}
    try:
        with open(COMBINED, 'r', encoding='utf-8', newline='') as f:
            for row in csv.DictReader(f):
                if row.get('date') == date_str:
                    return {k: row[k] for k in FIELD_NAMES if row.get(k)}
    except Exception:
        pass
    return {}

def load_manual_entries():
    if not os.path.exists(MANUAL_ENTRY_JSON):
        return []
    try:
        with open(MANUAL_ENTRY_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []

def get_manual_entry_for_date(date_str):
    for entry in load_manual_entries():
        if entry.get('date') == date_str:
            return entry
    return None

def prepare_manual_entry(date_str, fields):
    """01/10/26 - checked at SAVE time (the pipeline used to be the only place a bad value was
    caught, silently, so the person was told "Saved" for a weight of 700 kg or a date of
    05/10/2026 that never reached their data). Returns (clean_fields, problems) where
    problems is a list of plain-English strings. A bad date rejects the whole row."""
    problems = []
    try:
        d = datetime.strptime(date_str, '%Y-%m-%d').date()
    except Exception:
        return {}, [f'"{date_str}" is not a valid date (use YYYY-MM-DD)']
    if d > (datetime.now() + timedelta(days=1)).date():
        return {}, [f'{date_str} is in the future']
    try:
        import update_health as _uh
        ranges = _uh.VALIDATION_RANGES
    except Exception:
        ranges = {}
    clean = {}
    for k in FIELD_NAMES:
        v = fields.get(k)
        if v is None:
            continue
        if k in ranges and isinstance(v, (int, float)):
            lo, hi = ranges[k]
            if not (lo <= v <= hi):
                problems.append(f'{k} {v} is outside the believable range {lo}-{hi}')
                continue
        clean[k] = v
    return clean, problems


def save_manual_entry(date_str, fields):
    """
    Writes/replaces MANUAL_ENTRY_JSON's entry for date_str with `fields`
    (only keys in FIELD_NAMES with a non-None value are kept — an omitted or
    null field means "no manual override", matching extractors/manual.py's
    own "only include a field if present" contract). Also appends a diffed
    audit-log entry, trimmed to MAX_MANUAL_LOG_ENTRIES.

    Returns the cleaned fields dict actually written.
    """
    os.makedirs(INBOX_DIR, exist_ok=True)
    cleaned = {k: fields[k] for k in FIELD_NAMES if fields.get(k) is not None}

    entries = load_manual_entries()
    previous = None
    kept = []
    for entry in entries:
        if entry.get('date') == date_str:
            previous = entry
            continue  # dropped — replaced by the new entry below
        kept.append(entry)
    new_entry = {'date': date_str, **cleaned}
    kept.append(new_entry)
    with open(MANUAL_ENTRY_JSON, 'w', encoding='utf-8') as f:
        json.dump(kept, f, indent=2)

    # ── Audit log — diffed against whatever this date held before ──────────
    changes = {}
    prev_fields = previous or {}
    for k in FIELD_NAMES:
        old_val = prev_fields.get(k)
        new_val = cleaned.get(k)
        if old_val != new_val:
            changes[k] = {'from': old_val, 'to': new_val}
    log_entries = []
    if os.path.exists(MANUAL_ENTRY_LOG_JSON):
        try:
            with open(MANUAL_ENTRY_LOG_JSON, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
            if isinstance(loaded, list):
                log_entries = loaded
        except Exception:
            log_entries = []
    log_entries.append({
        'timestamp': datetime.now().isoformat(),
        'date': date_str,
        'changes': changes,
    })
    # Trim from the front — oldest entries drop first, same convention as
    # update_health.py's own flush_log()/MAX_LOG_LINES for pipeline.log.
    if len(log_entries) > MAX_MANUAL_LOG_ENTRIES:
        log_entries = log_entries[-MAX_MANUAL_LOG_ENTRIES:]
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(MANUAL_ENTRY_LOG_JSON, 'w', encoding='utf-8') as f:
        json.dump(log_entries, f, indent=2)

    return cleaned

def clear_manual_entry(date_str, fields=None):
    """
    Removes a date's manual override — either specific fields (`fields` given)
    or the whole entry (`fields` None/empty).

    IMPORTANT, real limitation (found via Pete's own first live test,
    28/09/26): this can only do two things —
      1. Remove the value from MANUAL_ENTRY_JSON, so it's no longer offered
         as a manual override on the next pipeline run and no longer
         pre-fills the Manual Entry form as "your last manual entry".
      2. Reset FIELD_SOURCES_JSON's attribution for that field back to
         unknown, so a FUTURE real device sync for that date is free to set
         it again (merge_with_precedence() in update_health.py treats
         unknown attribution as priority 999 — always safely overwritable).
    It CANNOT restore whatever value/source combined.csv held before the
    manual save. update_health.py's pipeline is forward-merge-only — it
    only ever reads a device's CURRENT inbox export, then archives it
    (archive_inbox()); it never re-reads historical exports to "recompute"
    a field, so there is no live source left to revert to for a date whose
    real export has already been processed and archived. The only way back
    to the exact prior value is a timestamped combined.csv snapshot from
    data/backup/ (backup_files() takes one before every pipeline write) —
    this function doesn't touch those, on purpose, so they stay a reliable
    fallback regardless of what this does.

    Returns (removed_fields, entry_fully_removed).
    """
    entries = load_manual_entries()
    target = None
    kept = []
    for entry in entries:
        if entry.get('date') == date_str:
            target = entry
            continue
        kept.append(entry)

    if target is None:
        return [], False

    if fields:
        removed = [f for f in fields if f in target and f != 'date']
        remaining = {k: v for k, v in target.items() if k == 'date' or k not in fields}
        entry_fully_removed = len(remaining) <= 1  # only 'date' left
        if not entry_fully_removed:
            kept.append(remaining)
    else:
        removed = [k for k in target if k != 'date']
        entry_fully_removed = True

    with open(MANUAL_ENTRY_JSON, 'w', encoding='utf-8') as f:
        json.dump(kept, f, indent=2)

    # Reset field_sources.json attribution for the cleared fields, so a
    # future real sync isn't still blocked by a manual claim that no longer
    # exists. Missing/corrupt file is treated as nothing to clear - same
    # "unknown is fine, always overwritable" fallback update_health.py's own
    # merge_with_precedence() already uses for untracked rows.
    try:
        if os.path.exists(FIELD_SOURCES_JSON):
            with open(FIELD_SOURCES_JSON, 'r', encoding='utf-8') as f:
                field_sources = json.load(f)
            date_sources = field_sources.get(date_str, {})
            changed = False
            for field in removed:
                if date_sources.get(field) == 'manual':
                    del date_sources[field]
                    changed = True
            if changed:
                if date_sources:
                    field_sources[date_str] = date_sources
                else:
                    field_sources.pop(date_str, None)
                tmp_path = FIELD_SOURCES_JSON + '.tmp'
                with open(tmp_path, 'w', encoding='utf-8') as f:
                    json.dump(field_sources, f, indent=2, sort_keys=True)
                os.replace(tmp_path, FIELD_SOURCES_JSON)
    except Exception:
        pass  # best-effort - the manual_entry.json removal above is the part that matters most

    # Audit trail — same log, so "cleared" shows up alongside "changed"
    # rather than vanishing from the history with no record it happened.
    log_entries = []
    if os.path.exists(MANUAL_ENTRY_LOG_JSON):
        try:
            with open(MANUAL_ENTRY_LOG_JSON, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
            if isinstance(loaded, list):
                log_entries = loaded
        except Exception:
            log_entries = []
    log_entries.append({
        'timestamp': datetime.now().isoformat(),
        'date': date_str,
        'cleared': removed,
    })
    if len(log_entries) > MAX_MANUAL_LOG_ENTRIES:
        log_entries = log_entries[-MAX_MANUAL_LOG_ENTRIES:]
    with open(MANUAL_ENTRY_LOG_JSON, 'w', encoding='utf-8') as f:
        json.dump(log_entries, f, indent=2)

    return removed, entry_fully_removed


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
    threading.Thread(target=_hc_watch_loop, daemon=True).start()
    ensure_scheduled_jobs()
    if '/com.termux/' in os.path.expanduser('~') or os.environ.get('MH_FORCE_CROND_CHECK'):
        threading.Thread(target=_crond_loop, daemon=True).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n  Server stopped.')
        server.server_close()


if __name__ == '__main__':
    main()
