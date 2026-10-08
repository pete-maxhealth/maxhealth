"""Persona 56: the app notices when the launcher's background sync has stopped (from its diary) and says what to do; selfcheck reports it."""
import sys, re, os, json, urllib.request; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright
f = Findings()
def diary(root, minutes_ago, lines=3):
    t = datetime.now() - timedelta(minutes=minutes_ago)
    with open(os.path.join(root, 'data', 'sync_service_debug.log'), 'w') as fh:
        for i in range(lines):
            ts = (t - timedelta(minutes=30 * (lines - 1 - i))).strftime('%Y-%m-%d %H:%M:%S')
            fh.write(f'[{ts}] onCreate\n[{ts}] sync complete: steps=1\n[{ts}] onDestroy\n')
def status():
    return json.loads(urllib.request.urlopen('http://localhost:5757/sync-status').read())
with fresh_server() as root, sync_playwright() as pw:
    os.makedirs(os.path.join(root, 'data'), exist_ok=True)
    diary(root, 20)
    a = status().get('launcher_age_minutes')
    if a is None or not 15 <= a <= 25: f.add('BUG', f'fresh diary should read about 20 minutes, got {a}')
    diary(root, 400)
    a = status().get('launcher_age_minutes')
    if a is None or not 395 <= a <= 405: f.add('BUG', f'stale diary should read about 400 minutes, got {a}')
    os.remove(os.path.join(root, 'data', 'sync_service_debug.log'))
    if status().get('launcher_age_minutes') is not None: f.add('BUG', 'no diary should read as unknown, not stalled')
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:160]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200)
    page.evaluate("onboardNext(2)"); page.fill('#onboardName', 'Ola'); page.evaluate("onboardNext(3)")
    page.evaluate("obSetSex('male')"); page.fill('#onboardAge', '58'); page.fill('#onboardHeight', '176')
    page.fill('#onboardWeight', '82'); page.fill('#onboardTarget', '78')
    page.evaluate("onboardNext(4)"); page.evaluate("obSetActivity('light')"); page.evaluate("obSetGoal('lose')")
    page.evaluate("onboardNext(5)"); page.evaluate("obSetCondition('general')")
    page.evaluate("onboardNext(6)"); page.evaluate("onboardFinish()"); page.wait_for_timeout(1500)
    vis = lambda: page.evaluate("getComputedStyle(document.getElementById('mhSyncBanner')).display !== 'none'")
    diary(root, 20); page.evaluate("mhCheckSyncHealth()"); page.wait_for_timeout(700)
    if vis(): f.add('BUG', 'banner shown although the sync ran 20 minutes ago')
    diary(root, 400); page.evaluate("mhCheckSyncHealth()"); page.wait_for_timeout(700)
    if not vis(): f.add('BUG', 'banner not shown although the sync last ran 400 minutes ago')
    if '6 hours' not in page.evaluate("document.getElementById('mhSyncBannerTitle').textContent") and '7 hours' not in page.evaluate("document.getElementById('mhSyncBannerTitle').textContent"): f.add('BUG', 'banner should say how long')
    page.evaluate("mhSyncHelpOpen()")
    t = page.evaluate("document.getElementById('mhSyncHelp').textContent")
    for w in ('No restrictions', 'Alarms', 'Autostart', 'Lock the app', 'Manual Entry'):
        if w not in t: f.add('BUG', f'help sheet missing: {w}')
    page.evaluate("document.getElementById('mhSyncHelpDate').value = '2026-10-04'")
    page.evaluate("mhOpenManualEntry()"); page.wait_for_timeout(1200)
    if page.evaluate("!!document.getElementById('mhSyncHelp')"): f.add('BUG', 'manual entry link did not close the help sheet')
    import datetime as _dt
    want = '2026-10-04'
    got = page.evaluate("document.getElementById('manualEntryDate').value")
    if got != want: f.add('BUG', f'manual entry date should be the picked day {want}, got {got}')
    if not page.evaluate("document.getElementById('imp-manual-wrap').offsetParent !== null"): f.add('BUG', 'manual entry section not visible after the link')
    page.evaluate("mhSyncHelpOpen()")
    page.evaluate("document.getElementById('mhSyncHelp').remove(); mhSyncBannerDismiss()")
    if vis(): f.add('BUG', 'dismiss did not hide the banner')
    page.evaluate("mhCheckSyncHealth()"); page.wait_for_timeout(700)
    if vis(): f.add('BUG', 'banner came back the same day after being dismissed')
    page.evaluate("localStorage.removeItem('mh_syncbanner_dismissed')"); diary(root, 20); page.evaluate("mhCheckSyncHealth()"); page.wait_for_timeout(700)
    if vis(): f.add('BUG', 'banner stayed after the sync recovered')
    # selfcheck reports it
    diary(root, 400)
    sc = json.loads(urllib.request.urlopen('http://localhost:5757/selfcheck').read())
    if not any('background sync' in i['text'] for i in sc.get('items', [])): f.add('BUG', f'selfcheck did not mention the stalled sync: {sc.get("items")}')
    diary(root, 20)
    sc = json.loads(urllib.request.urlopen('http://localhost:5757/selfcheck').read())
    if any('background sync' in i['text'] for i in sc.get('items', [])): f.add('BUG', 'selfcheck complained although the sync is healthy')
    # per-day link in the Trends day navigator
    page.evaluate("switchTab('trends')"); page.wait_for_timeout(500)
    page.evaluate("shiftTrendsDay(-1); shiftTrendsDay(-1); shiftTrendsDay(-1)"); page.wait_for_timeout(500)
    if not page.evaluate("!!document.getElementById('trendsDayEdit')"): f.add('BUG', 'no per-day edit link in the day navigator')
    page.evaluate("document.getElementById('trendsDayEdit').click()"); page.wait_for_timeout(1200)
    want3 = (_dt.date.today() - _dt.timedelta(days=3)).isoformat()
    got3 = page.evaluate("document.getElementById('manualEntryDate').value")
    if got3 != want3: f.add('BUG', f'per-day link should open {want3}, got {got3}')
    if errs: f.add('BUG', f'page errors: {errs[:3]}')
    b.close()
print('findings', len(f)); sys.exit(1 if f else 0)
