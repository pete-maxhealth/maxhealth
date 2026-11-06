"""Persona 412: the browser-storage notice names the right backup route and covers PCs (v3.10.1308). Covers: on a non-local host the Data screen shows the storage warning,
its "?" text mentions "Full app backup" under Settings, Data, Export (not the old "Full App State on the Import tab"), says PC / this computer, the Full app backup tick box
it points at really exists in the export list, the tick-nothing toast names the same item, no page errors. Invented data, demo persona."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 1280, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.dismiss()); ev = page.evaluate
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay').style.display='none'")
    ev("switchTabById('import')"); page.wait_for_timeout(1000)
    ev("updateDataBackupWarningForMode(false)"); page.wait_for_timeout(300)
    t = ev("(document.getElementById('help-databackupwarning')||{}).textContent||''")
    if not t: f.add('BUG', '1: no storage notice text')
    else:
        if 'Full App State' in t: f.add('BUG', '2: old "Full App State" wording is back')
        if 'Full app backup' not in t: f.add('BUG', '3: does not name Full app backup')
        if 'PC' not in t and 'computer' not in t: f.add('BUG', '4: does not cover PC users')
    has = ev("(()=>{const e=document.getElementById('bulkDsList'); return e?[...e.querySelectorAll('label')].some(l=>/Full app backup/.test(l.innerText)):'nolist'})()")
    if has is False: f.add('BUG', '5: Full app backup tick box not found in the export list')
    ev("document.querySelector('#dataBackupWarningHeadline [onclick*=databackupwarning]').click()"); page.wait_for_timeout(300)
    if ev("getComputedStyle(document.getElementById('help-databackupwarning')).display")=='none': f.add('BUG', '7: tapping the ? on the storage notice does not open its text (non-local host)')
    ev("mhExportSelected && (document.querySelectorAll('.bulkDs').forEach(c=>c.checked=false), mhExportSelected(false))"); page.wait_for_timeout(300)
    toast = ev("(document.getElementById('toast')||{}).innerText||''")
    if toast and 'Full App State' in toast: f.add('BUG', f'6: toast uses the old name: {toast}')
    if errs: f.add('BUG', f'page errors {errs[:3]}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
