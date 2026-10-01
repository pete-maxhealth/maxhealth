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
