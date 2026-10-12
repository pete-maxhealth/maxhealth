"""Persona 109: tag manager. Rename fixes every day, renaming onto an existing tag merges (case-insensitive), delete removes everywhere, activity summaries and tag notes survive, UI works."""
import sys; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("localStorage.setItem('mh_onboarded','1')"); page.reload(); page.wait_for_timeout(1500)
    ev = page.evaluate
    ev("""(()=>{ state.history=[{date:'01/10/26',notes:'massage, 30min walk, Travel',tagNotes:{massage:'neck'}},{date:'02/10/26',notes:'Massage session'},{date:'03/10/26',notes:'MASSAGE, Massage session'},{date:'04/10/26',notes:'standard'}]; state.notes='massage'; })()""")
    ev("mhTagRename('Massage session','Massage')")
    n = ev("state.history.map(d=>d.notes)")
    if n[1] != 'Massage' or n[2] != 'MASSAGE': f.add('BUG', f'merge result {n}')
    if n[0] != 'massage, 30min walk, Travel': f.add('BUG', f'untouched day changed {n[0]}')
    if n[3] != 'standard': f.add('BUG', f'standard changed {n[3]}')
    ev("mhTagRename('massage','Treatment: Massage')")
    n = ev("state.history.map(d=>d.notes)")
    if n[0] != 'Treatment: Massage, 30min walk, Travel' or n[1] != 'Treatment: Massage' or n[2] != 'Treatment: Massage': f.add('BUG', f'rename {n}')
    if ev("state.notes") != 'Treatment: Massage': f.add('BUG', 'today not renamed')
    if ev("state.history[0].tagNotes['Treatment: Massage']") != 'neck': f.add('BUG', 'tag note lost')
    ev("mhTagDelete('travel')")
    if 'Travel' in ev("state.history[0].notes"): f.add('BUG', 'delete')
    if '30min walk' not in ev("state.history[0].notes"): f.add('BUG', 'activity summary lost')
    # UI
    ev("mhTagsManage()"); page.wait_for_timeout(200)
    if 'Treatment: Massage' not in ev("document.getElementById('mhTagsModal').innerText"): f.add('BUG', 'modal list')
    page.click('#mhTagsModal .mh-tag-ren'); page.fill('#mhTagsModal .mh-tag-new', 'Treatment: Acupuncture'); page.click('#mhTagsModal .mh-tag-save'); page.wait_for_timeout(200)
    if ev("state.history[1].notes") != 'Treatment: Acupuncture': f.add('BUG', 'UI rename')
    page.click('#mhTagsModal .mh-tag-del'); page.wait_for_timeout(200)
    if 'Acupuncture' in ev("state.history.map(d=>d.notes).join('|')"): f.add('BUG', 'UI delete')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
