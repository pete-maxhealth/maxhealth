"""Persona 76: the Data tab is simple: one export/import card (Select all / Unselect all, zip or separate), no duplicate Export All, Restore is its own card, Manual Pipeline sits inside Sync Wearable Data, coverage lives with Missing Data."""
import sys, re, json, zipfile, io; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block', accept_downloads=True)
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("""() => { localStorage.setItem('mh_onboarded','1');
      saveLibrary([{id:'l1',name:'Oats',kcal:380,protein:13,carbs:60,fat:7,portion:'40g',locked:true,source:'label'}]);
      saveSymptomDefs([{id:'sy1',name:'Headache',active:true}]); switchTab('import'); }"""); page.wait_for_timeout(700)
    page.evaluate("mhTopicSet('import','all')")
    # --- structure
    ids = page.evaluate("[...document.querySelectorAll('#view-import [id]')].map(e => e.id)")
    for gone in ('title-imp-master', 'title-imp-databulk', 'title-imp-preview'):
        if gone in ids: f.add('BUG', f'{gone} should be gone (folded into another card)')
    for need in ('title-set-databackup', 'title-imp-restore', 'title-imp-sync', 'title-imp-gaps'):
        if need not in ids: f.add('BUG', f'missing {need}')
    nExp = page.evaluate("[...document.querySelectorAll('#view-import button')].filter(b => /export all/i.test(b.textContent)).length")
    if nExp: f.add('BUG', f'{nExp} separate "Export All" buttons still on the Data tab')
    if not page.evaluate("!!document.querySelector('#imp-sync-wrap #imp-advanced-wrap')"): f.add('BUG', 'Manual Pipeline should sit inside Sync Wearable Data')
    if not page.evaluate("!!document.querySelector('#imp-gaps-wrap #dataPreviewContent')"): f.add('BUG', 'coverage summary should live in Missing Data')
    if page.evaluate("!!document.querySelector('#imp-restore-wrap') && !!document.querySelector('#set-databackup-wrap #imp-restore-wrap')"): f.add('BUG', 'Restore must be its own card, not inside the export card')
    # --- select all / unselect all
    n = page.evaluate("document.querySelectorAll('#bulkDsList .bulkDs').length")
    if n < 12: f.add('BUG', f'expected the full list of exportable things, found {n}')
    page.evaluate("mhBulkSelect(false)")
    if page.evaluate("getBulkSelectedDatasets().length") != 0: f.add('BUG', 'Unselect all left some ticked')
    page.evaluate("mhBulkSelect(true)")
    if page.evaluate("getBulkSelectedDatasets().length") != n: f.add('BUG', 'Select all missed some')
    # --- zip export holds one file per ticked thing
    page.evaluate("mhBulkSelect(false); document.querySelector('#bulkDsList .bulkDs[value=library]').checked = true; document.querySelector('#bulkDsList .bulkDs[value=symptoms]').checked = true; document.querySelector('#bulkDsList .bulkDs[value=fullstate]').checked = true;")
    with page.expect_download(timeout=15000) as dl: page.evaluate("mhExportSelected(false)")
    path = dl.value.path(); z = zipfile.ZipFile(path); names = z.namelist()
    if not any(n.startswith('library') for n in names) or not any('setup' in n for n in names) or not any('backup' in n for n in names): f.add('BUG', f'zip is missing things: {names}')
    if any(n.startswith('master') or n.startswith('combined') for n in names): f.add('BUG', f'zip holds things that were not ticked: {names}')
    # --- separate files
    page.evaluate("document.querySelector('input[name=bulkFmt][value=separate]').click(); mhBulkSelect(false); document.querySelector('#bulkDsList .bulkDs[value=library]').checked = true;")
    with page.expect_download(timeout=15000) as dl2: page.evaluate("mhExportSelected(false)")
    if not dl2.value.suggested_filename.startswith('library'): f.add('BUG', f'separate export wrong file: {dl2.value.suggested_filename}')
    # --- nothing ticked
    page.evaluate("mhBulkSelect(false)")
    page.evaluate("mhExportSelected(false)"); page.wait_for_timeout(300)
    # --- round trip: import that zip into a fresh phone (backup asks to restore, library previews)
    b2 = pw.chromium.launch(); c2 = b2.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    c2.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    p2 = c2.new_page(); p2.on('pageerror', lambda e: errs.append(str(e)[:200]))
    p2.goto('http://localhost:5757/'); p2.wait_for_timeout(1200); p2.evaluate("localStorage.setItem('mh_onboarded','1'); switchTab('import')"); p2.wait_for_timeout(500)
    data = open(path, 'rb').read()
    p2.evaluate("""async (arr) => { const f = new File([new Uint8Array(arr)], 'maxedhealth_export.zip'); await mhImportFiles([f]); }""", list(data)); p2.wait_for_timeout(800)
    if not p2.query_selector('#restoreConfirmModal'): f.add('BUG', 'a zip holding a full backup should ask to restore')
    if not p2.query_selector('#mhPackModal'): f.add('BUG', 'a zip holding a library/setup should open the preview')
    b2.close()
    # --- restore from a backup file
    page.evaluate("document.getElementById('restoreConfirmModal')?.remove()")
    page.evaluate("""() => { mhConfirmRestore(JSON.parse(JSON.stringify({state: state, exportedAt: '2026-10-01T00:00:00Z'})), 'x.json'); }"""); page.wait_for_timeout(200)
    if '2026-10-01' not in page.inner_text('#restoreConfirmModal'): f.add('BUG', 'restore confirmation should name the backup date')
    page.click('#mhRestoreNo')
    if page.query_selector('#restoreConfirmModal'): f.add('BUG', 'Cancel should close the restore confirmation')
    if errs: f.add('BUG', f'page errors: {errs[:2]}')
    b.close()
print('findings', len(f)); sys.exit(1 if f else 0)
