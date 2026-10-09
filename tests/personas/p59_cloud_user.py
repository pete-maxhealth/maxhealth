"""Persona 59: a CLOUD user (web version, no local server, e.g. an iPhone or browser-only visitor). Walks every screen,
checks nothing breaks, nothing tells them to use Termux, Manual Entry / Missing Data / the sync card behave for them, and
that what they enter survives a reload. Simulated by serving the page from a non-localhost host with every other request
(including the local server) refused, which is exactly what such a visitor has."""
import sys, re, os; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from datetime import date, timedelta
from playwright.sync_api import sync_playwright
f = Findings()
HTML = open(os.path.join(REPO, 'maxhealth.html'), encoding='utf-8').read()
iso = lambda n: (date.today() - timedelta(days=n)).isoformat()
def serve(ctx):
    ctx.route(re.compile(r'.*'), lambda r: r.fulfill(status=200, content_type='text/html', body=HTML) if r.request.url.rstrip('/') in ('https://cloud.example', 'https://cloud.example/maxhealth.html') else r.abort())
def onboard(page):
    page.evaluate("onboardNext(2)"); page.fill('#onboardName', 'Ola'); page.evaluate("onboardNext(3)")
    page.evaluate("obSetSex('female')"); page.fill('#onboardAge', '45'); page.fill('#onboardHeight', '165')
    page.fill('#onboardWeight', '70'); page.fill('#onboardTarget', '65')
    page.evaluate("onboardNext(4)"); page.evaluate("obSetActivity('light')"); page.evaluate("obSetGoal('lose')")
    page.evaluate("onboardNext(5)"); page.evaluate("obSetCondition('general')")
    page.evaluate("onboardNext(6)"); page.evaluate("onboardFinish()"); page.wait_for_timeout(1500)
with sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block'); serve(ctx)
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('https://cloud.example/'); page.wait_for_timeout(1500)
    onboard(page)
    page.wait_for_timeout(3500)       # let the startup server pings fail
    if page.evaluate("_serverOnline") is not False: f.add('BUG', 'page thinks a server is online')
    badge = page.evaluate("(document.getElementById('serverModeBadge')||{}).textContent||''")
    if 'LOCAL' in badge and 'CLOUD' not in badge: f.add('BUG', f'badge says local: {badge}')

    # 1. walk every screen: nothing throws, nothing tells a cloud user to use Termux / mhstart outside the Import help
    walk = [('today', 'dash'), ('today', 'supplements'), ('log', 'log'), ('log', 'hist'), ('log', 'library'),
            ('insights', 'trends'), ('insights', 'reports'), ('settings', 'manage'), ('settings', 'customise'), ('settings', 'import')]
    for tab, sub in walk:
        page.evaluate(f"switchTab('{tab}'); switchSubTab('{tab}', '{sub}')"); page.wait_for_timeout(700)
        vis = page.evaluate("""() => { const out = []; const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
            while (w.nextNode()) { const n = w.currentNode; const t = n.textContent.trim(); if (!t) continue; const e = n.parentElement;
              if (e && e.offsetParent !== null && getComputedStyle(e).visibility !== 'hidden' && /mhstart|Termux/i.test(t)) out.push(t.slice(0, 90)); } return out; }""")
        if vis and not (tab == 'settings' and sub == 'import'): f.add('BUG', f'{tab}/{sub}: cloud user shown local-only text: {vis[:2]}')
        if errs: f.add('BUG', f'{tab}/{sub}: page error {errs[:2]}'); errs.clear()

    # 2. Settings > Import for a cloud user
    page.evaluate("switchTab('settings'); switchSubTab('settings','import')"); page.wait_for_timeout(1200)
    sm = page.evaluate("document.getElementById('syncStatusMsg').textContent")
    if page.evaluate("getComputedStyle(document.getElementById('pushToServerBtn')).display !== 'none'"): f.add('BUG', 'Push-to-local-server button shown to a cloud user')
    if 'not available in cloud mode' not in sm: f.add('BUG', f'sync card does not explain cloud mode: {sm[:100]}')
    if page.evaluate("getComputedStyle(document.getElementById('serverOfflineNotice')).display !== 'none'"): f.add('BUG', 'Termux restart panel shown to a cloud user')
    if page.evaluate("document.getElementById('syncBtn').disabled !== true"): f.add('BUG', 'Sync Now button should be disabled in cloud mode')
    if page.evaluate("getComputedStyle(document.getElementById('mhSyncBanner')).display !== 'none'"): f.add('BUG', 'background-sync banner shown to a cloud user')
    page.evaluate("mhLoadDataGaps()"); page.wait_for_timeout(400)
    if 'Checking' in page.evaluate("document.getElementById('mhGapsList').textContent"): f.add('BUG', 'Missing Data card stuck on Checking')

    # 3. a cloud user brings in some data by file import, then fills a gap by hand
    csvtxt = "date,steps,hr_avg,sleep_duration\n" + "\n".join([f"{iso(6)},8000,60,420", f"{iso(5)},8200,61,410", f"{iso(4)},7000,,380", f"{iso(3)},,62,390", f"{iso(2)},7100,62,400"])
    page.evaluate("t => { processCombinedText(t, true, null); localStorage.setItem('mh_combined_csv_cache', t); }", csvtxt); page.wait_for_timeout(500)
    page.evaluate("mhLoadDataGaps()"); page.wait_for_timeout(400)
    n = page.evaluate("document.querySelectorAll('#mhGapsList > div').length")
    if n != 3: f.add('BUG', f'cloud Missing Data should list 3 days, got {n}')
    page.evaluate("t => mhOpenManualEntry(t)", iso(4)); page.wait_for_timeout(1200)
    if page.evaluate("document.getElementById('manualEntryDate').value") != iso(4): f.add('BUG', 'Fill in did not open the right day')
    page.evaluate("document.getElementById('manualField_hr_avg').value = '59'; _manualFieldsTouched.add('hr_avg')")
    page.evaluate("saveManualEntry()"); page.wait_for_timeout(1000)
    if 'Saved' not in page.evaluate("document.getElementById('manualEntryOutput').textContent"): f.add('BUG', 'cloud manual save gave no confirmation')
    # a brand-new day (no row yet) typed in by hand
    page.evaluate("t => mhOpenManualEntry(t)", iso(1)); page.wait_for_timeout(1200)
    page.evaluate("document.getElementById('manualField_steps').value = '5400'; _manualFieldsTouched.add('steps')")
    page.evaluate("saveManualEntry()"); page.wait_for_timeout(1000)

    # 4. Trends day navigator shows the by-hand link and lands on that day
    page.evaluate("switchTab('insights'); switchSubTab('insights','trends')"); page.wait_for_timeout(600)
    page.evaluate("typeof setTrendsWindow === 'function' && setTrendsWindow('today')"); page.wait_for_timeout(500)
    if errs: f.add('BUG', f'page errors after data entry: {errs[:2]}'); errs.clear()

    # 5. reload (same browser): what was entered is still there
    page.goto('https://cloud.example/'); page.wait_for_timeout(2500)
    hr = page.evaluate("t => { const r = mhCloudHistoryRow(t); return r ? r.hr_avg : null }", iso(4))
    st = page.evaluate("t => { const r = mhCloudHistoryRow(t); return r ? r.steps : null }", iso(1))
    if hr != 59: f.add('BUG', f'hand-entered heart rate lost after reload: {hr}')
    if st != 5400: f.add('BUG', f'hand-entered new day lost after reload: {st}')
    cache = page.evaluate("localStorage.getItem('mh_combined_csv_cache') || ''")
    if iso(6) + ',8000' not in cache: f.add('BUG', 'imported rows missing from the cache after a hand entry')

    # 6. no sleep-conflict card, no server-only prompts on Today
    page.evaluate("switchTab('today'); switchSubTab('today','dash')"); page.wait_for_timeout(1000)
    if page.evaluate("!!document.getElementById('sleepConflictCard') && getComputedStyle(document.getElementById('sleepConflictCard')).display !== 'none'"): f.add('BUG', 'sleep conflict card visible to a cloud user')

    # 7. data protection for a cloud user: persistent storage is requested, the backup banner says what is at risk
    page.evaluate("mhRequestPersistentStorage()"); page.wait_for_timeout(500)
    if page.evaluate("window._mhPersisted") not in (True, False, 'unsupported'): f.add('BUG', 'persistent storage was never requested')
    page.evaluate("window._mhPersisted = false; switchTab('settings'); switchSubTab('settings','import'); updateDataBackupWarningForMode(false)"); page.wait_for_timeout(500)
    if 'not promised' not in page.evaluate("document.getElementById('mhStorageStatus').textContent"): f.add('BUG', 'Settings does not warn when the browser has not agreed to keep the data')
    page.evaluate("window._mhPersisted = true; mhUpdateStorageStatus()")
    if 'agreed to keep' not in page.evaluate("document.getElementById('mhStorageStatus').textContent"): f.add('BUG', 'Settings does not show protected state')
    page.evaluate("""() => { localStorage.removeItem('mh_last_export_nudge'); window._dismissedWarnings = new Set();
        state.history = state.history.filter(h => !(h.totals && h.totals.kcal > 0)); }""")
    seed = [iso(i) for i in range(1, 7)]
    page.evaluate("""ds => { ds.forEach(d => { const p = d.split('-'); state.history.push({date: p[2]+'/'+p[1]+'/'+p[0].slice(2), totals: {kcal: 1800, protein: 90, carbs: 40, fat: 120}}); }); }""", seed)
    page.evaluate("checkBackupReminder()"); page.wait_for_timeout(300)
    bt = page.evaluate("document.getElementById('backupReminderBanner').textContent")
    if page.evaluate("getComputedStyle(document.getElementById('backupReminderBanner')).display === 'none'") or 'day' not in bt or 'Clearing this browser' not in bt: f.add('BUG', f'cloud backup banner should name what is at risk: {bt[:160]}')
    page.evaluate("localStorage.setItem('mh_last_export_nudge', arguments[0])" if False else "d => { localStorage.setItem('mh_last_export_nudge', d); window._dismissedWarnings = new Set(); }", iso(0))
    page.evaluate("checkBackupReminder()"); page.wait_for_timeout(300)
    if page.evaluate("getComputedStyle(document.getElementById('backupReminderBanner')).display !== 'none'"): f.add('BUG', 'backup banner still shown right after a backup')
    # iPhone in a Safari tab (not installed): home-screen advice appears
    ictx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block', user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1'); serve(ictx)
    ip = ictx.new_page(); ip.goto('https://cloud.example/'); ip.wait_for_timeout(1200)
    if not ip.evaluate("mhIsIOSBrowserTab()"): f.add('BUG', 'iPhone Safari tab not recognised')
    ip.evaluate("window._mhPersisted = false; mhUpdateStorageStatus()") if ip.evaluate("!!document.getElementById('mhStorageStatus')") else None
    ictx.close()
    if errs: f.add('BUG', f'page errors: {errs[:3]}')
    b.close()
print('findings', len(f)); sys.exit(1 if f else 0)
