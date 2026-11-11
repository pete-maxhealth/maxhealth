"""Persona 400: adding some of an order to the cupboards: ticked rows go in; unticked rows are left out with an Undo way back (v3.10.1296, changed by v3.10.1350).
Pete (5 Nov): imported a shopping list to restock, ticked only the non-nutritional lines, pressed add, and the rest of the list was gone with no way back.
Covers: partial add keeps the unticked rows waiting, survives a reload, a later add of the rest clears the list, adding everything still clears at once, skipped (no amount) rows stay. Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
TXT = "1 x Zzqx Oat Biscuits 300g\t£1.20\n2 x Zzqx Hazel Spread 350g\t£3.00\n1 x Zzqx Washing Pods 30\t£4.00"
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay').style.display='none'")
    def start(k=0):
        ev("switchTabById('shop'); mhOrdOpen('order')"); page.wait_for_timeout(300)
        ev("t=>mhOrdLoad(t,'test')", TXT.replace('Zzqx', 'Zzqx' + 'abcdef'[k])); page.wait_for_timeout(500)
    start()
    ev("mhOrdKindSet(2,'nonfood')"); ev("mhOrdSet(2,'amount','2')")
    ev("mhOrdTick(0,false); mhOrdTick(1,false)"); ev("mhOrdApply()"); page.wait_for_timeout(500)
    # v3.10.1350 (Pete, 10 Nov): once everything the person ticked is in, the unticked lines are left out and the import finishes. The way back for them is Undo (v3.10.1296 kept them waiting).
    if ev("!!_shopUi.ord"): f.add('BUG', '1: with only unticked lines left after the add, the import finishes')
    msg = ev("document.body.innerText")
    if 'Stock started for 1 item' not in msg or '2 left out' not in msg: f.add('BUG', f'2: message says how many were left out: {msg[:400]}')
    if not ev("(()=>{const u=mhOrdUndoGet();return !!(u&&u.draft)})()"): f.add('BUG', '3: Undo remembers the whole list, so the left-out lines can come back')
    ev("mhOrdUndo()"); page.wait_for_timeout(400)
    if not ev("!!localStorage.getItem('mh_ord_draft_v1')"): f.add('BUG', '3b: after Undo the list is saved again')
    page.reload(); page.wait_for_timeout(1500); ev("document.getElementById('onboardingOverlay')&&(document.getElementById('onboardingOverlay').style.display='none')")
    ev("switchTabById('shop'); mhOrdOpen(_shopUi.ordKind||'order')"); page.wait_for_timeout(500)
    names = ev("document.body.innerText")
    if 'Oat Biscuits' not in names or 'Hazel Spread' not in names: f.add('BUG', '4: after Undo and a reload the rest of the list is there')
    page.screenshot(path='/tmp/p400.png')
    # now add the rest
    ev("mhOrdTick(0,true); mhOrdTick(1,true); mhOrdSet(0,'amount','300 g'); mhOrdSet(1,'amount','700 g')"); ev("mhOrdApply()"); page.wait_for_timeout(500)
    if ev("!!_shopUi.ord") or ev("!!localStorage.getItem('mh_ord_draft_v1')"): f.add('BUG', '5: once everything is added the list clears')
    # everything at once clears straight away
    start(1); ev("mhOrdKindSet(2,'nonfood')"); ev("mhOrdSet(0,'amount','300 g'); mhOrdSet(1,'amount','700 g'); mhOrdSet(2,'amount','2')"); ev("mhOrdApply()"); page.wait_for_timeout(500)
    if ev("!!_shopUi.ord"): f.add('BUG', '6: adding every row clears the list as before')
    # a row without an amount is skipped and stays
    start(2); ev("mhOrdSet(0,'amount','300 g'); mhOrdSet(1,'amount',''); mhOrdKindSet(2,'nonfood'); mhOrdSet(2,'amount','2')"); ev("mhOrdApply()"); page.wait_for_timeout(500)
    st = ev("_shopUi.ord&&_shopUi.ord.rows.map(r=>!!r.done)")
    if st != [True, False, True]: f.add('BUG', f'7: the row with no amount stays waiting: {st}')
    if errs: f.add('BUG', f'page errors {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
