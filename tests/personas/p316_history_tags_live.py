"""Persona 316 (v3.10.1215): the History edit screen's occasion tags are live - a custom tag used on another day appears as a chip, a rename from Manage tags shows up, a deleted one goes."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("startDemoMode('alex')"); page.wait_for_timeout(2500)
    ev("switchTabById('history'); renderHistory()"); page.wait_for_timeout(1500)
    chips = lambda: ev("(function(){ document.querySelectorAll('.hist-day-totals-edit').forEach(x=>x.remove()); const d = document.querySelector('.hist-day-date').textContent.trim(); editHistDayTotalsByDate(d); const el = document.querySelector('[id^=histTagPicker-]'); return el ? el.innerText.replace(/\\s+/g,' ') : 'NOPICKER'; })()")
    ev("state.history[1].notes = (state.history[1].notes ? state.history[1].notes + ', ' : '') + 'Zzqx Dentist'; saveState()")
    c = chips()
    if c == 'NOPICKER': f.add('BUG', 'history edit opens with the tag picker')
    elif 'Zzqx Dentist' not in c: f.add('BUG', f'a custom tag used on another day appears in the History tag picker: {c}')
    ev("mhTagRename('zzqx dentist','Zzqx Optician')"); c = chips()
    if 'Zzqx Optician' not in c or 'Zzqx Dentist' in c: f.add('BUG', f'a renamed tag shows its new name only: {c}')
    ev("state.history[1].notes = state.history[1].notes + ', device data, Steps 8000, 8123 steps, 7.5h sleep, HRV 55'; saveState()"); c = chips()
    for bad in ['device data', 'Steps 8000', '8123', 'sleep', 'HRV']:
        if bad in c: f.add('BUG', f'device-written notes are not offered as tags: {bad!r} in {c}')
    ev("mhTagDelete('zzqx optician')"); c = chips()
    if 'Zzqx' in c: f.add('BUG', f'a deleted tag is gone from the picker: {c}')
    if 'Hospital day' not in c: f.add('BUG', 'the standard chips are still there')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
