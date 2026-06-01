#!/usr/bin/env python3
"""
MaxHealth - Local Server
Runs on localhost:5757 in Termux (auto-started via Termux:Boot).
Bridges the HTML app and the data pipeline — no Termux interaction needed.

Endpoints:
  GET  /ping       — health check
  GET  /combined   — serve combined.csv
  GET  /status     — pipeline run status + log
  GET  /run        — trigger pipeline (?device=all|withings|ringconn|amazfit&dry_run=true)
  GET  /sync       — full sync: move exports from Download, run pipeline, serve combined.csv
  GET  /inbox      — list files in inbox

Usage:
  cd /storage/emulated/0/maxhealth/app
  python server.py
"""

import os
import sys
import json
import glob
import shutil
import subprocess
import threading
import http.server
import urllib.parse
from datetime import datetime

# ─── PATHS ────────────────────────────────────────────────────────────────────
APP_DIR    = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR   = os.path.dirname(APP_DIR)                        # /storage/emulated/0/maxhealth
DATA_DIR   = os.path.join(ROOT_DIR, 'data')
TABLES_DIR = os.path.join(DATA_DIR, 'tables')
INBOX_DIR  = os.path.join(DATA_DIR, 'inbox')
BACKUP_DIR = os.path.join(DATA_DIR, 'backup')
DOWNLOAD   = '/storage/emulated/0/Download'
LOGS_DIR   = os.path.join(ROOT_DIR, 'logs')
COMBINED   = os.path.join(TABLES_DIR, 'combined.csv')
MASTER_CSV      = os.path.join(TABLES_DIR, 'master.csv')
LIBRARY_CSV     = os.path.join(TABLES_DIR, 'library.csv')
SUPPLEMENTS_CSV = os.path.join(TABLES_DIR, 'supplements.csv')

TRACKER    = os.path.join(APP_DIR, 'maxhealth', 'maxhealth.html')
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

        # Withings
        elif any(lower.startswith(p) for p in ('export_', 'data_export', 'data_pet_', 'withings', 'healthmate')) \
                and lower.endswith('.zip'):
            is_export = True

        if is_export:
            if os.path.exists(dest):
                _log(f'Skipped — {name} already in inbox')
            else:
                shutil.move(src, dest)
                _log(f'Moved {name} → inbox')
                moved += 1

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

        try:
            length = int(self.headers.get('Content-Length', 0))
            body   = json.loads(self.rfile.read(length)) if length > 0 else {}
        except Exception:
            self.send_json({'error': 'Invalid JSON body'}, 400)
            return

        # ── POST /save-nutrition — save a single day row ──────────────────────
        if path == '/save-nutrition':
            date    = body.get('date', '').strip()
            kcal    = body.get('kcal', 0)
            protein = body.get('protein', 0)
            carbs   = body.get('carbs', 0)
            notes   = body.get('notes', '').strip()

            if not date or not kcal:
                self.send_json({'error': 'date and kcal are required'}, 400)
                return

            updated = save_nutrition_row(date, kcal, protein, carbs, notes)
            self.send_json({
                'status': 'ok',
                'action': 'updated' if updated else 'added',
                'row': f"{date}|{kcal}|{protein}|{carbs}|{notes}"
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
                notes   = r.get('notes', '').strip()
                if date and kcal:
                    updated = save_nutrition_row(date, kcal, protein, carbs, notes)
                    results.append({'date': date, 'action': 'updated' if updated else 'added'})

            self.send_json({'status': 'ok', 'saved': len(results), 'results': results})

        elif path == '/save-library-csv':
            try:
                length = int(self.headers.get('Content-Length', 0))
                csv_data = self.rfile.read(length).decode('utf-8')
                os.makedirs(TABLES_DIR, exist_ok=True)
                with open(LIBRARY_CSV, 'w', encoding='utf-8') as lf:
                    lf.write(csv_data)
                rows = len([l for l in csv_data.strip().split('\n') if l]) - 1
                self.send_json({'status': 'ok', 'rows': rows})
            except Exception as e:
                self.send_json({'error': str(e)}, 400)

        elif path == '/save-supplements-csv':
            try:
                length = int(self.headers.get('Content-Length', 0))
                csv_data = self.rfile.read(length).decode('utf-8')
                os.makedirs(TABLES_DIR, exist_ok=True)
                with open(SUPPLEMENTS_CSV, 'w', encoding='utf-8') as lf:
                    lf.write(csv_data)
                rows = len([l for l in csv_data.strip().split('\n') if l]) - 1
                self.send_json({'status': 'ok', 'rows': rows})
            except Exception as e:
                self.send_json({'error': str(e)}, 400)

        else:
            self.send_json({'error': f'Unknown POST endpoint: {path}'}, 404)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path   = parsed.path
        params = urllib.parse.parse_qs(parsed.query)

        # ── Health check ──────────────────────────────────────────────────
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

        elif path.startswith('/icons/'):
            # Serve icon files from the maxhealth app directory
            icon_name = os.path.basename(path)
            icon_path = os.path.join(APP_DIR, 'maxhealth', 'icons', icon_name)
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

        elif path.startswith('/docs/') or path in ('/carer.html', '/gbm_patient_guide.html'):
            # Serve static HTML files from the maxhealth app directory
            safe = path.lstrip('/')
            file_path = os.path.join(APP_DIR, 'maxhealth', safe)
            if os.path.exists(file_path) and file_path.endswith('.html'):
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
            import json as _json, urllib.parse as _up
            data_str = _up.parse_qs(_up.urlparse(self.path).query).get('data', [''])[0]
            if data_str:
                try:
                    lib = _json.loads(_up.unquote(data_str))
                    os.makedirs(TABLES_DIR, exist_ok=True)
                    with open(LIBRARY_JSON, 'w', encoding='utf-8') as lf:
                        _json.dump(lib, lf, ensure_ascii=False)
                    self.send_json({'status': 'ok', 'count': len(lib)})
                except Exception as e:
                    self.send_json({'error': str(e)}, 400)
            else:
                self.send_json({'error': 'No data'}, 400)

        elif path == '/load-library':
            if os.path.exists(LIBRARY_JSON):
                with open(LIBRARY_JSON, 'r', encoding='utf-8') as lf:
                    lib_data = lf.read()
                body = lib_data.encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(body)))
                for k, v in CORS.items():
                    self.send_header(k, v)
                self.end_headers()
                self.wfile.write(body)
            else:
                self.send_json([])


        elif path == '/library':
            if os.path.exists(LIBRARY_CSV):
                with open(LIBRARY_CSV, 'r', encoding='utf-8') as lf:
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

        elif path == '/supplements':
            if os.path.exists(SUPPLEMENTS_CSV):
                with open(SUPPLEMENTS_CSV, 'r', encoding='utf-8') as lf:
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

def save_nutrition_row(date, kcal, protein, carbs, notes=''):
    """
    Append or update a row in master.csv.
    Format: DD/MM/YY|kcal|protein|carbs|notes
    If the date already exists, the row is updated in place.
    """
    os.makedirs(TABLES_DIR, exist_ok=True)
    row = f"{date}|{kcal}|{protein}|{carbs}|{notes}"

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
