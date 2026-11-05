"""Persona 401: an import can be undone (v3.10.1297). Pete (5 Nov): put 13 non-nutritional items on the shelf by pressing add, thinking they would just leave the list.
Covers: undo removes exactly what the import added, brings the review list back, leaves later changes alone, the Undo link shows on the list and goes after use. Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay').style.display='none'")
    ev("mhStockTrack('Zzqx Existing Rice',{base:'g'}); mhStockSetLevel(mhShopKey('Zzqx Existing Rice'),500)")
    ev("switchTabById('shop'); mhOrdOpen('order')"); page.wait_for_timeout(300)
    ev("t=>mhOrdLoad(t,'test')", "1 x Zzqx Oat Biscuits 300g\t£1.20\n1 x Zzqx Washing Pods 30\t£4.00\n1 x Zzqx Bin Bags 20\t£2.00"); page.wait_for_timeout(500)
    ev("mhOrdKindSet(1,'nonfood'); mhOrdKindSet(2,'nonfood'); mhOrdSet(1,'amount','30'); mhOrdSet(2,'amount','20'); mhOrdTick(0,false)")
    keys = lambda: ev("Object.values(mhStockLoad().items).map(i=>i.name).sort().join('|')")
    before = keys(); ev("mhOrdApply()"); page.wait_for_timeout(500)
    after = keys()
    if 'Washing Pods' not in after or 'Bin Bags' not in after: f.add('BUG', f'1: the import added the two non-food lines: {after}')
    ev("mhStockSetLevel(mhShopKey('Zzqx Existing Rice'),400)")   # a later change that undo must not touch
    ev("mhShopView('list')"); page.wait_for_timeout(400)
    if not ev("!!document.getElementById('mhOrdUndoRow')"): f.add('BUG', '2: the list offers Undo the last import')
    page.screenshot(path='/tmp/p401.png')
    ev("mhOrdUndo()"); page.wait_for_timeout(500)
    now = keys()
    if 'Washing Pods' in now or 'Bin Bags' in now: f.add('BUG', f'3: undo removes what the import added: {now}')
    if ev("mhStockLoad().items[mhShopKey('Zzqx Existing Rice')].level") != 400: f.add('BUG', '4: a later change is left alone')
    if not ev("!!localStorage.getItem('mh_ord_draft_v1')"): f.add('BUG', '5: the review list is back after undo')
    if ev("!!mhOrdUndoGet()") or ev("!!document.getElementById('mhOrdUndoRow')"): f.add('BUG', '6: the Undo link goes once used')
    ev("switchTabById('shop'); mhOrdOpen('order')"); page.wait_for_timeout(500)
    if 'Oat Biscuits' not in ev("document.body.innerText"): f.add('BUG', '7: pressing Import carries on with the list')
    if errs: f.add('BUG', f'page errors {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
