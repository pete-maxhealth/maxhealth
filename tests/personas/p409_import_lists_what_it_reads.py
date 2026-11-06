"""Persona 409: Settings > Data > Export/Import lists what Import can bring in (v3.10.1305). Pete: "needs listing in both imports and exports or it could be missed".
Covers: the Import list is built from the same rows as the Export ticks (same labels, none missing), the "?" opens the note, the note is not inside a label,
Open a file button and export ticks still work, survives reload, Spanish lead. Invented data, demo persona."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.dismiss())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay').style.display='none'"); ev("startDemoMode('doris')"); page.wait_for_timeout(1800)
    for rnd in (1, 2):
        ev("switchTabById('import')"); page.wait_for_timeout(700)
        ex = ev("[...document.querySelectorAll('#bulkDsList label')].map(l=>{const sp=l.querySelector('span'); const c=sp?[...sp.childNodes].find(n=>n.nodeType===3&&n.textContent.trim()):null; return (c?c.textContent:l.innerText.split('\\n')[0]).trim().replace(/\\s*\\(all of the above.*$/,'')})")
        txt = ev("(document.getElementById('bulkImportCan')||{}).textContent||''")
        if not txt: f.add('BUG', f'{rnd}: no Can bring in list'); break
        if len(ex) < 12: f.add('BUG', f'{rnd}: export list too short {ex}')
        for l in ex:
            if l not in txt: f.add('BUG', f'{rnd}: "{l}" is exported but not listed for import: {txt[:200]}')
        if ev("!!document.querySelector('#bulkImportCan').closest('label')"): f.add('BUG', f'{rnd}: list sits inside a label')
        ev("document.querySelector('#bulkImportCan [onclick*=bulkimportcan]').click()"); page.wait_for_timeout(300)
        shown = ev("(document.getElementById('bulkImportCan').innerText||'').includes('Nothing is added until you confirm') && !!document.querySelector('#bulkImportCan [id^=help-]') && getComputedStyle(document.querySelector('#bulkImportCan [id^=help-]')).display!=='none'")
        if not shown: f.add('BUG', f'{rnd}: ? did not open the note')
        if not ev("!!document.getElementById('bulkImportFileInput') && document.querySelectorAll('#bulkDsList input.bulkDs').length>=12"): f.add('BUG', f'{rnd}: import/export controls missing')
        if rnd == 1: page.reload(); page.wait_for_timeout(1800); ev("document.getElementById('onboardingOverlay').style.display='none'"); ev("startDemoMode('doris')"); page.wait_for_timeout(1800)
    ev("mhLangSet('es')"); page.wait_for_timeout(2500); ev("switchTabById('import')"); page.wait_for_timeout(600)
    if 'Se puede traer' not in ev("document.getElementById('bulkImportCan').innerText"): f.add('BUG', 'Spanish lead missing')
    if errs: f.add('BUG', f'page errors {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
