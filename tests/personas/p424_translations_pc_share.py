"""Persona 424: the v3.10.1309-1321 strings are translated (tools/lang_add_pc_share.py). Pete 7 Nov: "crack on" with the translations.
Covers, in all eight languages: the share hint and its "?" steps (naming the buttons as that pack does), the CSV undo button with a day count (singular and plural), the "imported" toast and the Undo label,
the undo result message (four shapes); English is unchanged; every pack still parses. Not walked here: the PC "Phone only" notes, the data-stays-on-device row and the storage/save toasts (entries are in the packs, not looked at rendered)."""
import sys, json, re, glob, subprocess; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from datetime import date, timedelta
from playwright.sync_api import sync_playwright
f = Findings(); chk = lambda ok, m: None if ok else f.add('BUG', m)
LANGS = ['es', 'de', 'fr', 'tr', 'pt', 'it', 'pl', 'nl']
for l in LANGS:
    new = json.load(open(f'lang/{l}.json', encoding='utf-8')); old = json.loads(subprocess.check_output(['git', 'show', f'HEAD~0:lang/{l}.json'])) if False else {}
    chk(len(new) > 1800, f'0: {l} pack looks short: {len(new)}')
dmy = lambda n: (date.today() - timedelta(days=n)).strftime('%d/%m/%Y')
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    for l in LANGS:
        d = json.load(open(f'lang/{l}.json', encoding='utf-8')); btn = re.sub(r'^\W+', '', d['👁 GENERATE CARER VIEW LINK']); prv = d['Preview']
        ctx = b.new_context(viewport={'width': 1280, 'height': 900}, service_workers='block'); page = ctx.new_page(); ev = page.evaluate
        page.on('pageerror', lambda e: errs.append(l + ' ' + str(e)[:160]))
        page.goto('http://localhost:5757/'); page.wait_for_timeout(800); ev(f"localStorage.setItem('mh_lang','{l}')"); page.reload(); page.wait_for_timeout(1500)
        ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
        ev("switchTab('settings'); try{switchSubTab('settings','manage')}catch(e){}; mhShareRender()"); page.wait_for_timeout(700)
        hint = ev("document.getElementById('shareMoreHint').childNodes[0].nodeValue"); chk(hint.strip() == d['Want to share more or less? Tick or untick above, then make a new link.'], f'1 {l}: hint {hint!r}')
        steps = ev("document.getElementById('help-sharemore')?.textContent||''"); chk(btn in steps and prv in steps and 'GENERATE CARER' not in steps, f'2 {l}: steps text: {steps[:120]!r}')
        ev("document.getElementById('manualCsvUndoRow') || (()=>{const e=document.createElement('div'); e.id='manualCsvUndoRow'; document.body.appendChild(e)})()")
        for n, key in ((2, '↩ Undo the last upload ({1} days)'), (1, '↩ Undo the last upload ({1} day)')):
            ev(f"localStorage.setItem('mh_csv_undo', JSON.stringify({{at: Date.now(), dates: {json.dumps(['2026-10-0' + str(i + 1) for i in range(n)])}, prior: {{}}, priorRow: {{}}, after: {{}}}})); mhCsvUndoRender()"); page.wait_for_timeout(300)
            t = ev("document.querySelector('#manualCsvUndoRow button')?.textContent||''"); chk(t.strip() == d[key].replace('{1}', str(n)), f'3 {l}/{n}: undo button {t!r}')
        ev("showToast('3 day(s) imported ✓', 'Undo', () => {}, 15000)"); page.wait_for_timeout(300)
        tt = ev("[...document.querySelectorAll('.toast, #toast, [class*=toast]')].map(e=>e.textContent).join('|')")
        chk(d['{1} day(s) imported ✓'].replace('{1}', '3') in tt and d['Undo'] in tt, f'4 {l}: toast {tt!r}')
        for msg, key, parts in (('Upload undone: 2 days put back.', 'Upload undone: {1} days put back.', ('2',)), ('Upload undone: 1 day put back.', 'Upload undone: {1} day put back.', ('1',)),
                                ('Upload undone: 2 days put back; 1 left as they are because they changed since.', 'Upload undone: {1} days put back; {2} left as they are because they changed since.', ('2', '1')),
                                ('Upload undone: 1 day put back; 3 left as they are because they changed since.', 'Upload undone: {1} day put back; {2} left as they are because they changed since.', ('1', '3'))):
            ev(f"(()=>{{const e=document.createElement('div'); e.className='zz-msg'; e.textContent={json.dumps(msg)}; document.body.appendChild(e)}})()"); page.wait_for_timeout(200)
            got = ev("[...document.querySelectorAll('.zz-msg')].pop().textContent"); want = d[key].replace('{1}', parts[0]).replace('{2}', parts[-1] if len(parts) > 1 else '')
            chk(got == want, f'5 {l}: undo message {got!r} wanted {want!r}')
        ev("document.querySelectorAll('.zz-msg').forEach(e=>e.remove())")
        ctx.close()
    # English untouched
    page = b.new_context(viewport={'width': 1280, 'height': 900}, service_workers='block').new_page(); ev = page.evaluate; page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()"); ev("switchTab('settings'); try{switchSubTab('settings','manage')}catch(e){}; mhShareRender()"); page.wait_for_timeout(500)
    chk('Want to share more or less?' in ev("document.getElementById('shareMoreHint').textContent"), '6: English hint changed')
    if errs: f.add('BUG', f'page errors {errs[:3]}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
