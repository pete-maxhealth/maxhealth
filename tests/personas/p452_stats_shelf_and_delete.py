"""Persona 452: a statistic can be taken off the display and kept (Put back in Library -> shelf in the Library, Put back brings it home), Delete is a real delete with an Undo, shelf survives a reload and is in the backup (v3.10.1367). Invented data."""
import sys, json; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("localStorage.setItem('mh_stats_seeded','1'); localStorage.setItem('mh_stats_defs','[]'); switchTab('insights'); switchSubTab('insights','statistics')"); page.wait_for_timeout(500)
    ev("mhStatLibAdd(0); mhStatLibAdd(1); mhStatLibAdd(2); mhStatCloseBuilder()"); page.wait_for_timeout(300)
    names = lambda: ev("mhStatLoad().map(d => d.name)")
    shelf = lambda: ev("mhStatShelfLoad().map(d => d.name)")
    n0 = names()
    if len(n0) != 3: f.add('BUG', f'0: set-up: {n0}')
    victim = ev("mhStatLoad()[1].id"); vname = n0[1]
    # the card shows both buttons, with clear words
    ev(f"mhStatToggle && 0"); card = ev(f"document.getElementById('stcard-{victim}').innerText")
    if 'Put back in Library' not in card or 'Delete' not in card: f.add('BUG', f'1: the card needs "Put back in Library" and "Delete": {card[-120:]!r}')
    # 2: put back in Library -> off the list, on the shelf, Undo returns it in the same place
    ev(f"mhStatShelve('{victim}')"); page.wait_for_timeout(300)
    if vname in names() or shelf() != [vname]: f.add('BUG', f'2: shelving: list {names()} shelf {shelf()}')
    if ev(f"!!document.getElementById('stcard-{victim}')"): f.add('BUG', '2b: the card is still on screen')
    page.locator('#toast .toast-undo').first.click(timeout=4000) if page.locator('#toast .toast-undo').count() else f.add('BUG', '3: no Undo on the toast')
    page.wait_for_timeout(300)
    if names() != n0 or shelf(): f.add('BUG', f'3b: Undo did not restore: {names()} / {shelf()}')
    # 4: shelve again, see it in the Library shelf, put it back via the Library
    ev(f"mhStatShelve('{victim}')"); page.wait_for_timeout(200); ev("mhStatLibraryOpen()"); page.wait_for_timeout(300)
    lib = ev("document.getElementById('mhStatLibPanel').innerText")
    if 'Taken off my statistics (1)' not in lib or vname not in lib or 'Put back' not in lib: f.add('BUG', f'4: the Library shelf is missing: {lib[:200]!r}')
    if '📥 on your shelf' not in lib: f.add('BUG', '4b: the ready-made entry should say it is on your shelf')
    # reload: the shelf is still there
    page.reload(); page.wait_for_timeout(1500); ev = page.evaluate
    if shelf() != [vname]: f.add('BUG', f'5: shelf after reload: {shelf()}')
    # in the backup
    bk = ev("buildFullBackupPayload()"); bks = json.dumps(bk)
    if 'mh_stats_shelf' not in bks: f.add('BUG', '6: the shelf is not in the backup')
    # 7: put back from the Library -> back at the top of the list
    ev("switchTab('insights'); switchSubTab('insights','statistics'); mhStatLibraryOpen()"); page.wait_for_timeout(300)
    ev(f"mhStatUnshelve('{victim}')"); page.wait_for_timeout(300)
    if names()[0] != vname or shelf(): f.add('BUG', f'7: put back: {names()} / {shelf()}')
    # 8: real delete, Undo comes back at the same place
    ids = ev("mhStatLoad().map(d => d.id)"); i = 1; did = ids[i]; dname = names()[i]
    ev(f"mhStatDelete('{did}')"); page.wait_for_timeout(300)
    if dname in names() or len(names()) != 2: f.add('BUG', f'8: delete: {names()}')
    if shelf(): f.add('BUG', f'8b: a deleted statistic went to the shelf: {shelf()}')
    if ev("!!document.querySelector('.app-modal, #appModal')"): f.add('BUG', '8c: delete still asks "are you sure"')
    page.locator('#toast .toast-undo').first.click(timeout=4000); page.wait_for_timeout(300)
    if names()[i] != dname or len(names()) != 3: f.add('BUG', f'9: Undo of delete: {names()}')
    # 10: delete from the shelf, with Undo
    ev(f"mhStatShelve('{did}')"); page.wait_for_timeout(200); ev(f"mhStatShelfDelete('{did}')"); page.wait_for_timeout(200)
    if shelf(): f.add('BUG', f'10: shelf delete: {shelf()}')
    page.locator('#toast .toast-undo').first.click(timeout=4000); page.wait_for_timeout(200)
    if len(shelf()) != 1: f.add('BUG', f'10b: Undo of shelf delete: {shelf()}')
    # 11: a shelved statistic is not pinned to Today or shared
    ev(f"mhStatUnshelve('{did}')"); ev(f"mhStatTogglePin('{did}')"); ev(f"mhStatShelve('{did}')"); page.wait_for_timeout(200)
    if ev("mhStatPinnedDefs().some(d => d.id === '" + did + "')"): f.add('BUG', '11: a shelved statistic is still pinned to Today')
    if errs: f.add('BUG', f'page errors: {errs[:2]}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
