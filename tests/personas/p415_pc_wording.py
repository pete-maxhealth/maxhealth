"""Persona 415: PC wording (v3.10.1311). Pete 6 Nov: on a PC it said "phone" in places (Restore from backup, Export/Import).
Covers: on a desktop browser the Data screen lines for the backup note, Restore, Check the daily backups and Push to the local server do not say phone; on an Android phone they still do;
the storage line and the "behind" line say computer on a PC and phone on a phone; the Restore from a backup file button and Export boxes are still there; no page errors. Invented data, demo persona."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
PC = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
AND = 'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Mobile Safari/537.36'
IDS = ['mhBackupLivesNote', 'mhRestoreNote', 'mhCheckBackupsBtn', 'pushToServerBtn']
def run(b, ua, w, touch, pc):
    ctx = b.new_context(viewport={'width': w, 'height': 900}, user_agent=ua, has_touch=touch, is_mobile=touch, service_workers='block'); page = ctx.new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.dismiss()); ev = page.evaluate
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay').style.display='none'"); ev("startDemoMode('doris')"); page.wait_for_timeout(1800)
    ev("switchTabById('import')"); page.wait_for_timeout(900)
    for i in IDS:
        t = ev(f"(document.getElementById('{i}')||{{}}).textContent||''")
        if not t: f.add('BUG', f'1: {i} missing'); continue
        has = 'phone' in t.lower()
        if pc and has: f.add('BUG', f'2: PC still says phone in {i}: {t[:80]}')
        if not pc and not has and i != 'mhCheckBackupsBtn' or (not pc and i == 'mhCheckBackupsBtn' and not has): f.add('BUG', f'3: phone lost its wording in {i}: {t[:80]}')
    w = ev("mhDeviceWord()")
    if w != ('computer' if pc else 'phone'): f.add('BUG', f'4: mhDeviceWord is {w}')
    if not ev("!!document.querySelector('button[onclick*=mhOpenRestorePicker], button[onclick*=Restore], #bulkDsList')"): f.add('BUG', '5: Restore / Export controls missing')
    if errs: f.add('BUG', f'page errors {errs[:3]}')
    ctx.close()
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch()
    run(b, PC, 1280, False, True)
    run(b, AND, 390, True, False)
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
