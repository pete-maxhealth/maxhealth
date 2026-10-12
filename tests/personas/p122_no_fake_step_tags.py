"""Persona 122: device read-outs in old notes ('12,345 steps, 7.1h sleep, HRV 40') never become picker tags ('000 steps', '345 steps'); a one-time repair rewrites '12,345 steps' to '12345 steps'; real tags still appear; the importer no longer writes thousands separators."""
import sys; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev = page.evaluate
    ev("""state.history=[{date:'01/10/26',log:[],totals:{kcal:0},notes:'12,345 steps, 7.1h sleep, HRV 40, Treatment: Massage'},{date:'02/10/26',log:[],totals:{kcal:0},notes:'10,000 steps|active day, Exercise: 6.3k steps, Exercise: Swim'}]; localStorage.removeItem('mh_mig_step_commas'); mhFixStepCommas();""")
    notes = ev("state.history.map(h=>h.notes)")
    if '12,345' in notes[0] or '10,000' in notes[1]: f.add('BUG', f'commas not repaired {notes}')
    names = ev("Object.values(mhTagDays()).map(v=>v.name)")
    for bad in ['12', '345 steps', '000 steps', '7.1h sleep', 'HRV 40', 'Exercise: 6.3k steps']:
        if bad in names: f.add('BUG', f'noise tag offered: {bad} in {names}')
    if not any('12345' in n for n in names) and any('steps' in n.lower() and 'exercise' not in n.lower() for n in names): f.add('BUG', f'a steps read-out still a tag: {names}')
    for good in ['Treatment: Massage', 'Exercise: Swim']:
        if good not in names: f.add('BUG', f'real tag lost: {good} in {names}')
    if "${steps} steps" not in open('maxhealth.html').read(): f.add('BUG', 'importer still formats steps with separators')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
