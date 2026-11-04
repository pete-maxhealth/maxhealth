"""Persona 395: Polyols has a box on Manual entry, the Missed day form and the Save-to-library dialog (v3.10.1288).
Covers: typed polyols stored as typed on each route and reaching the day total; blank stays not recorded (manual, library) / 0 (missed day); boxes reset between uses. Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    page = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block').new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    # 1 manual entry
    ev("state.todayLog=[]; showManualEntryForm('Zzqx cake')")
    page.wait_for_timeout(300)
    if not ev("!!document.getElementById('mePolyols')"): f.add('BUG', '1: Manual entry has a Polyols box')
    else:
        ev("document.getElementById('meKcal').value='300'; document.getElementById('mePolyols').value='6.34'"); ev("confirmManualEntry()")
        if ev("state.todayLog.slice(-1)[0].polyols") != 6.3: f.add('BUG', '1b: polyols stored as typed (6.3): ' + str(ev("state.todayLog.slice(-1)[0].polyols")))
        ev("showManualEntryForm('Zzqx plain')"); ev("document.getElementById('meKcal').value='100'"); ev("confirmManualEntry()")
        if ev("'polyols' in state.todayLog.slice(-1)[0]"): f.add('BUG', '1c: blank polyols is not recorded, not 0')
    # 2 missed day
    ev("openMissedDayModal()"); page.wait_for_timeout(300); ev("setMissedMode('manual')")
    if not ev("!!document.getElementById('missedPolyols')"): f.add('BUG', '2: Missed day has a Polyols box')
    else:
        ev("document.getElementById('missedDayDate').value='01/01/20'; document.getElementById('missedKcal').value='500'; document.getElementById('missedProtein').value='20'; document.getElementById('missedCarbs').value='10'; document.getElementById('missedPolyols').value='4.5'; document.getElementById('missedNotes').value='zzqx'")
        ev("saveMissedDay()"); page.wait_for_timeout(400)
        d = ev("state.history.find(h=>h.date==='01/01/20')")
        if not d or d['totals'].get('polyols') != 4.5 or d['log'][0].get('polyols') != 4.5: f.add('BUG', '2b: missed-day polyols on the line and the total: ' + str(d and d['totals']))
        ev("openMissedDayModal()"); ev("setMissedMode('manual')"); page.wait_for_timeout(200)
        if ev("document.getElementById('missedPolyols').value") != '': f.add('BUG', '2c: box clears on reopen')
        page.screenshot(path='/tmp/p395_missed.png')
        ev("closeMissedDayModal()")
    # 3 save to library
    ev("promptSaveToLibrary({name:'Zzqx sweet', kcal:100, protein:1, carbs:20, fat:1, fibre:2, polyols:3, portion:'100g'})"); page.wait_for_timeout(300)
    if ev("document.getElementById('saveModalPolyolsEdit')?.value") != '3': f.add('BUG', '3: Save dialog shows the polyols it was given: ' + str(ev("document.getElementById('saveModalPolyolsEdit')?.value")))
    ev("document.getElementById('saveModalPolyolsEdit').value='7'"); ev("confirmSaveToLibrary()"); page.wait_for_timeout(400)
    lib = ev("loadLibrary().find(x=>/zzqx/i.test(x.name))")
    if not lib or lib.get('polyols') != 7: f.add('BUG', '3b: saved food keeps edited polyols: ' + str(lib and lib.get('polyols')))
    if errs: f.add('BUG', f'page errors {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
