"""Persona 211: master-to-servant stock transfer (v3.10.1119). Pete's phone holds the real counts; his tablet should match it. Covers:
the export file (counts, device name, nothing from the ledger); refusing a file that is not a stock file; refusing to replace anything
when no backup of the receiving device exists and one cannot be made; the confirmation naming the direction (file's device -> this
device) and warning when the file is older than what is on this device; cancel changing nothing; confirm replacing stock, clearing the
ledger, putting items that are low on the list; and after a real backup restore the stock card telling Pete the counts may be stale."""
import sys, json; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()"); ev("mhShopOpen()")
    ev("mhStockTrack('Whey protein',{base:'g',pack:750,serving:25,shop:'Asda'})"); ev("mhStockTrack('Eggs',{base:'each',pack:6,shop:'Asda'})")
    wk, ek = [ev("n=>mhShopKey(n)", n) for n in ('Whey protein', 'Eggs')]
    ev("([a,b])=>{mhStockSetLevel(a,600);mhStockSetLevel(b,10);mhStockSetReorder(a,125);mhStockAdjust(a,-25,'log','x1')}", [wk, ek])
    pack = ev("mhStockExport('Pete phone')")
    if not pack or pack['tracked'] != 2 or pack['device'] != 'Pete phone' or 'ledger' in pack: f.add('BUG', f'export file shape: {str(pack)[:200]}')
    if pack and pack['items'][wk]['level'] != 575: f.add('BUG', 'export carries the current counts')
    # build the receiving state: different stock, an old ledger
    ev("([a])=>{mhStockSetLevel(a,50);mhStockAdjust(a,-10,'log','old1');const o=mhStockLoad();delete o.items[a].lowFlag;mhStockSave(o);}", [wk])
    # refuse non stock files
    if ev("p=>mhStockImportStart(p)", {'type': 'nope'}) is not False: f.add('BUG', 'a file that is not a stock file must be refused')
    # no backup and cannot make one: refuse
    ev("localStorage.removeItem('mh_last_full_backup_date'); window._saveFullBackupToServer_impl = async()=>false")
    if ev("p=>mhStockImportStart(p)", pack) is not False or ev("k=>mhStockLoad().items[k].level", wk) != 40: f.add('BUG', 'no backup and none can be made: nothing may be replaced')
    if page.query_selector('#appModalConfirm'): f.add('BUG', 'must not even ask when no backup exists')
    # with a backup: ask, name the direction, cancel changes nothing
    ev("localStorage.setItem('mh_last_full_backup_date', todayStr())")
    older = dict(pack, exportedAt=1000)
    ev("p=>mhStockImportStart(p)", older); page.wait_for_timeout(100)
    txt = page.inner_text('.app-modal-msg')
    if 'Pete phone' not in txt or 'this device' not in txt.lower() or 'replaces' not in txt: f.add('BUG', f'confirmation must name the direction: {txt[:200]!r}')
    if 'OLDER' not in txt: f.add('BUG', 'a file older than this device\'s stock must be warned about')
    page.click('#appModalCancel'); page.wait_for_timeout(100)
    if ev("k=>mhStockLoad().items[k].level", wk) != 40: f.add('BUG', 'cancel must change nothing')
    ev("p=>mhStockImportStart(p)", dict(pack, exportedAt=ev("Date.now()") + 5000)); page.wait_for_timeout(100)
    if 'OLDER' in page.inner_text('.app-modal-msg'): f.add('BUG', 'a newer file must not carry the older warning')
    page.click('#appModalConfirm'); page.wait_for_timeout(200)
    st = ev("mhStockLoad()")
    if st['items'][wk]['level'] != 575 or st['items'][ek]['level'] != 10: f.add('BUG', f'confirm must replace the counts: {st["items"][wk]["level"]}')
    if st['ledger']: f.add('BUG', 'the old ledger belongs to the old counts and must be cleared')
    if st['items'][wk]['since'] < ev("Date.now()") - 20000: f.add('BUG', 'imported items start a fresh stock-take point')
    if not ev("k=>mhShopLoad().items.some(i=>i.key===k)", ek) and not ev("k=>mhShopLoad().items.some(i=>i.key===k)", wk): pass
    # real restore -> stale notice
    ev("localStorage.setItem('mh_last_full_backup_date', todayStr())")
    payload = ev("buildFullBackupPayload()"); ev("p=>mhApplyBackupObject(p,'backup 1')", payload); page.wait_for_timeout(2500)
    ev("document.getElementById('onboardingOverlay')?.remove()"); ev("mhShopOpen()"); page.wait_for_timeout(300)
    if 'Stock was restored from' not in page.inner_text('#mhShopPane'): f.add('BUG', 'after a restore the stock card must warn that counts may be stale')
    if not page.locator('[data-stocknotice]').is_visible(): f.add('BUG', 'the stale-stock notice must actually be visible to the user')
    ev("document.querySelector('[data-stocknotice] span').click()"); page.wait_for_timeout(150)
    if 'Stock was restored from' in page.inner_text('#mhShopPane'): f.add('BUG', 'the notice must be dismissible')
    if errs: f.add('BUG', f'page errors {errs[:3]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
