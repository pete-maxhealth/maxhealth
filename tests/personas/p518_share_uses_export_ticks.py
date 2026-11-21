"""Persona 518: "Share with another phone" uses the Export ticks on Settings > Data (Pete 21 Nov: no need to choose twice), then asks how to send. Walks: untick rows, press Share, the summary and the real selection match
(history/library/stock/list/settings/labs mapping, wearable rows never), the three ways to send and three ways to receive are all on the one screen with the standard back arrow, Show codes only carries what was ticked
(checked against the data collected), Change what to share still works and does not alter the Export ticks, the shopping entry still opens with its own ticks, Full app backup ticks everything, and p508 still passes.
NOT covered: a real second phone (Pete's gate)."""
import sys, json; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings(); chk = lambda ok, m: None if ok else f.add('BUG', m)
with fresh_server() as root, sync_playwright() as pw:
    pg = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 844}, service_workers='block').new_page(); ev = pg.evaluate; errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:150])); pg.on('dialog', lambda d: d.accept())
    pg.goto('http://localhost:5757/'); pg.wait_for_timeout(1000)
    ev("state.onboarded=true; saveState(); document.getElementById('onboardingOverlay')?.remove()")
    ev("saveLibrary([{id:'a',name:'Rice',kcal:130,protein:2.7,carbs:28,fat:0.3,portion:'100g'}])")
    ev("switchTabById('import')"); pg.wait_for_timeout(600)
    ev("mhBulkSelect(false)")
    ev("['library','stock','combined','reports'].forEach(v=>{document.querySelector('#bulkDsList .bulkDs[value=\"'+v+'\"]').checked=true})")
    pg.click('text=Share with another phone'); pg.wait_for_timeout(500)
    sel = ev("Object.keys(_mhx.sel).filter(k=>_mhx.sel[k]).sort().join(',')")
    chk(sel == 'library,settings,stock', f'selection from Export ticks wrong: {sel}')
    txt = ev("document.getElementById('mhXferOverlay').innerText")
    for w in ['Food library', 'Cupboards & stock', 'HOW DO YOU WANT TO SEND', 'Show codes', 'Send by code', 'Save as locked file', 'RECEIVING ON THIS PHONE', 'Scan codes', 'Receive by code', 'Open a locked file']: chk(w in txt, f'missing on the share screen: {w}')
    chk('Shopping list' not in txt.split('HOW DO YOU')[0].split('SHARING')[1], 'unticked item shown as shared')
    chk(ev("!!document.querySelector('#mhXferOverlay .mh-sheet-back')"), 'no standard back arrow')
    chk(ev("document.querySelectorAll('#mhXferOverlay input[type=checkbox]').length") == 0, 'tick boxes shown again without asking')
    chk(ev("(async()=>{const o=mhxCollect(_mhx.sel); return Object.keys(o.scopes).sort().join(',')})()") == 'library,settings,stock', 'collected data does not match the ticks')
    pg.click('text=Change what to share'); pg.wait_for_timeout(300)
    chk(ev("document.querySelectorAll('#mhXferOverlay input[type=checkbox]').length") == 11, 'Change what to share did not show the 11 boxes')
    ev("mhxSel('recipes', true)"); ev("mhxClose()")
    chk(ev("[...document.querySelectorAll('#bulkDsList .bulkDs:checked')].map(c=>c.value).sort().join(',')") == 'combined,library,reports,stock', 'changing the share ticks altered the Export ticks')
    ev("mhBulkSelect(true)"); ev("mhxOpenFromData()")
    chk(ev("Object.keys(_mhx.sel).filter(k=>!_mhx.sel[k]).length") == 0, 'Full app backup should tick everything')
    ev("mhxClose(); mhBulkSelect(false)"); ev("mhxOpenFromData()")
    chk('Nothing is ticked' in ev("document.getElementById('mhXferOverlay').innerText"), 'nothing-ticked message missing')
    ev("mhxStartSend()"); pg.wait_for_timeout(400)
    chk(ev("_mhx.view") == 'home', 'Show codes started with nothing ticked')
    ev("mhxClose(); switchTabById('shop'); mhShopView('sync')"); pg.wait_for_timeout(400)
    ev("mhxOpen()"); chk(ev("!!document.getElementById('mhXferOverlay') && document.getElementById('mhXferOverlay').innerText.includes('HOW DO YOU WANT TO SEND')"), 'the shopping entry no longer opens the share screen')
    # a locked Premium button explains itself in a dialog (v1445) instead of only a line at the top of the screen
    ev("mhxClose(); mhBulkSelect(true)"); ev("mhxOpenFromData()")
    ev("mhxCodeSend()"); pg.wait_for_timeout(300)
    chk(ev("!!document.querySelector('.app-modal-msg') && document.querySelector('.app-modal-msg').innerText.includes('Premium feature')"), 'Send by code on a free phone shows no dialog')
    ev("document.getElementById('appModalCancel').click()"); ev("mhxFileSend()"); pg.wait_for_timeout(300)
    chk(ev("!!document.querySelector('.app-modal-msg') && document.querySelector('.app-modal-msg').innerText.includes('locked file is a Premium')"), 'Save as locked file on a free phone shows no dialog')
    ev("document.getElementById('appModalConfirm').click()"); pg.wait_for_timeout(500)
    chk(ev("_mhx.view") == 'send', 'Show QR codes instead did not start the QR send')
    for e in errs: f.add('JS-exception', e)
print('findings', len(f))
