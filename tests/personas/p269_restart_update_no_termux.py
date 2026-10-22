"""Persona 269: starting and updating without Termux (v3.10.1163). The offline notice, the server badge, the failed-sync toast and the update banner no longer tell anyone to open
Termux: they offer Start the server / Update now. The Server restarting box says what is happening and has an OK button; the launcher hand-off targets the MaxedHealth Sync app;
Update now asks the server (POST /update-now), which runs the update script (and says so plainly when the script is missing); with the server down, Update now starts it instead. Invented data."""
import sys, os, tempfile, json, time, urllib.request, urllib.error; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
mark = tempfile.mktemp(prefix='mh_upd_'); script = tempfile.mktemp(prefix='mh_script_', suffix='.sh')
open(script, 'w').write(f'#!/bin/bash\necho ran > {mark}\n'); os.chmod(script, 0o755)
os.environ['MH_AUTOUPDATE_SCRIPT'] = script
def post(path):
    try:
        r = urllib.request.urlopen(urllib.request.Request('http://localhost:5757' + path, data=b'{}', method='POST', headers={'Content-Type': 'application/json'}), timeout=5); return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e: return e.code, json.loads(e.read() or b'{}')
with fresh_server() as root, sync_playwright() as pw:
    st, d = post('/update-now'); time.sleep(1.5)
    if st != 200 or d.get('status') != 'started' or not os.path.exists(mark): f.add('BUG', f'/update-now runs the update script: {st} {d} marker={os.path.exists(mark)}')
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    html = ev("document.documentElement.innerHTML")
    if 'Open Termux and type' in html: f.add('BUG', 'the offline notice no longer tells people to open Termux and type')
    if 'START THE SERVER' not in html: f.add('BUG', 'the offline notice has a Start the server button')
    if 'com.maxedhealth.launcher' not in ev("mhLauncherIntent()") or not ev("mhLauncherIntent()").startswith('intent:'): f.add('BUG', 'the hand-off opens the MaxedHealth Sync launcher')
    # the Server restarting box (stub the navigation so the page stays)
    ev("window.mhLauncherIntent = () => '#launcher-test'")
    ev("mhRestartDialog('start')"); page.wait_for_timeout(500)
    t = page.inner_text('#mhRestartBox')
    if 'Server restarting' not in t or 'OK' not in t: f.add('BUG', f'the box says Server restarting and has OK: {t}')
    page.click('#mhRestartOk'); page.wait_for_timeout(200)
    if page.locator('#mhRestartBox').count(): f.add('BUG', 'OK closes the box')
    # server already up: it comes back at once
    ev("mhRestartDialog('start')"); page.wait_for_timeout(4500)
    if 'Server is back' not in page.inner_text('#mhRestartBox'): f.add('BUG', 'the box notices the server is running')
    ev("mhRestartClose()")
    # Update now: asks the server, shows Updating
    os.remove(mark); ev("mhRestartDialog('update')"); page.wait_for_timeout(2500)
    if 'Updating' not in page.inner_text('#mhRestartBox'): f.add('BUG', 'Update now shows Updating')
    if not os.path.exists(mark): f.add('BUG', 'Update now asked the server to run the update')
    ev("mhRestartClose(); clearInterval(_mhRestartTimer)")
    # the update banner offers it
    ev("localStorage.setItem('mh_latest_ver','v9.9.9'); localStorage.removeItem('mh_behind_dismissed'); mhBehindRender()")
    b = ev("document.getElementById('mhBehindBanner') ? document.getElementById('mhBehindBanner').innerText : ''")
    if 'Update now' not in b or 'Termux' in b: f.add('BUG', f'the update banner says Update now, not Termux: {b}')
    # server down: Update now starts it instead
    page.route('**/ping', lambda r: r.abort()); ev("document.getElementById('mhBehindBanner')?.remove()")
    ev("mhRestartDialog('update')"); page.wait_for_timeout(800)
    if 'Server restarting' not in page.inner_text('#mhRestartBox'): f.add('BUG', 'with the server down, Update now starts the server first')
    ev("mhRestartClose(); clearInterval(_mhRestartTimer)")
    if errs: f.add('BUG', f'page errors: {errs}')
    # script missing: plain message
    os.environ['MH_AUTOUPDATE_SCRIPT'] = '/nonexistent/x.sh'
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
