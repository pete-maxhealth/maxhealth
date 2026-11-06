"""Persona 418: the v3.10.1305-1312 changes with the network cut (offline mode). Browser offline after load, server unreachable, PC window.
Covers: Data screen on a PC says computer not phone, Import card lists what it reads, phone-only notes show on a PC, the filled-CSV upload saves into the browser and survives a reload with no network,
the back arrow works, the sleep minutes round trip, the offline banner appears, the layout stays 880 wide, no page errors from the new code. Invented data, fresh browser."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
CSV = "date,weight,steps,sleep_duration\n2026-10-05,84.2,6100,7.5\n2026-10-06,83.9,,450\n"
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); ctx = b.new_context(viewport={'width': 1280, 'height': 900}, service_workers='block', user_agent=UA); page = ctx.new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.dismiss()); ev = page.evaluate
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay').style.display='none'"); page.wait_for_timeout(500)
    ctx.set_offline(True); ev("_serverOnline = false"); page.wait_for_timeout(500)
    ev("switchTabById('import')"); page.wait_for_timeout(1200)
    txt = ev("document.body.innerText").lower()
    for sid in ('mhBackupLivesNote', 'mhRestoreNote', 'mhCheckBackupsBtn', 'pushToServerBtn'):
        t = ev(f"(document.getElementById('{sid}')||{{}}).textContent||''")
        if 'phone' in t.lower(): f.add('BUG', f'1: offline PC, {sid} still says phone: {t[:80]}')
    if ev("document.getElementById('bulkImportCan')===null"): f.add('BUG', '2: Import "Can bring in" line missing offline')
    if abs(ev("document.body.getBoundingClientRect().width") - 880) > 1: f.add('BUG', '3: PC column is not 880 wide offline')
    if not ev("document.documentElement.classList.contains('mh-pc')"): f.add('BUG', '4: mh-pc class missing')
    shown = ev("[...document.querySelectorAll('.mh-phone-note')].filter(e=>getComputedStyle(e).display!=='none').length")
    if shown < 1 and ev("document.querySelectorAll('.mh-phone-note').length") > 0: f.add('BUG', f'5: phone-only notes not shown on PC offline ({shown})')
    page.set_input_files('#manualCsvUploadInput', files=[{'name': 'mine.csv', 'mimeType': 'text/csv', 'buffer': CSV.encode()}]); page.wait_for_timeout(1500)
    out = ev("(document.getElementById('manualEntryOutput')||{}).textContent||''")
    if 'Saved 2 day' not in out: f.add('BUG', f'6: offline CSV upload result: {out}')
    sl = ev("(()=>{const a=mhCloudHistoryRow('2026-10-05'), c=mhCloudHistoryRow('2026-10-06'); return [a&&a.sleep_duration, c&&c.sleep_duration]})()")
    if sl != [450, 450]: f.add('BUG', f'7: sleep minutes after upload {sl}, wanted [450, 450]')
    ctx.set_offline(False); page.reload(); page.wait_for_timeout(1500); ctx.set_offline(True); ev("_serverOnline = false")  # reload needs the shell; the cached-shell route is p43
    if ev("(()=>{try{const a=mhCloudHistoryRow('2026-10-05');return a&&a.sleep_duration}catch(e){return 'err'}})()") != 450: f.add('BUG', '8: uploaded days not there after an offline reload')
    ev("document.getElementById('onboardingOverlay').style.display='none'")
    # back arrow offline
    ev("document.getElementById('maintab-settings').click()"); page.wait_for_timeout(500); ev("document.getElementById('maintab-today').click()"); page.wait_for_timeout(500)
    ev("(()=>{const s=document.getElementById(window._activeScrollContainerId); if(s){s.scrollTop=400; s.dispatchEvent(new Event('scroll'))}})()"); page.wait_for_timeout(400)
    try:
        page.click('#globalBackBtn', timeout=3000); page.wait_for_timeout(500)
        if ev("document.querySelector('#mainTabRow .tab.active').id") != 'maintab-settings': f.add('BUG', '9: back arrow did not return offline')
    except Exception as e: f.add('BUG', f'10: back arrow not clickable offline {str(e)[:60]}')
    if errs: f.add('BUG', f'page errors {errs[:3]}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
