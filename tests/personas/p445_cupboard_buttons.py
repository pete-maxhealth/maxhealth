"""Persona 445 (v3.10.1362): the My cupboards buttons were tidied (Pete, 10 Nov): no separate "Add a food" tile, Check the cupboards only when foods need details, Possible duplicates only when there are pairs, and the three transfer links are one "Move to another device" that opens QR / Send / Receive."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("localStorage.setItem('mh_shop_pane','stock')")
    ev("(()=>{const o=mhStockLoad(); o.enabled=true; mhStockSave(o)})()")
    ev("['Zzqx Rice','Zzqx Beans'].forEach(n=>{mhStockTrack(n,{base:'g',shop:'Asda'}); mhStockSetLevel(mhShopKey(n),400)})")
    ev("mhShopOpen()"); page.wait_for_timeout(500)
    tiles = lambda: ev("[...document.querySelectorAll('#stockctlCard .mh-tiles button')].map(b=>b.innerText.trim())")
    t = tiles()
    if any('Add a food' in x for x in t): f.add('BUG', f'1: the separate Add a food tile is gone: {t}')
    if not any('Import' in x for x in t): f.add('BUG', f'2: Import stays: {t}')
    if any('duplicate' in x.lower() for x in t) and ev("mhStockDupePairs().length") == 0: f.add('BUG', f'3: no duplicates, no tile: {t}')
    if ev("mhStockGapCount()") == 0 and any('Check the cupboards' in x for x in t): f.add('BUG', f'4: nothing needs details, no Check tile: {t}')
    ev("mhStockTrack('Zzqx Gap',{base:'g'}); mhShopRender()"); page.wait_for_timeout(300)
    t = tiles()
    if ev("mhStockGapCount()") > 0 and not any('Check the cupboards' in x for x in t): f.add('BUG', f'5: foods need details, the Check tile shows: {t}')
    if ev("[...document.querySelectorAll('#stockctlCard span')].some(e=>/^(📤 Send stock and list to another device|📥 Receive stock and list)$/.test(e.innerText.trim()))"): f.add('BUG', '6: the transfer links are folded into one')
    if not page.locator('#mhMoveLink').count(): f.add('BUG', '7: a Move to another device link')
    else:
        page.evaluate("document.getElementById('mhMoveLink').scrollIntoView()"); page.click('#mhMoveLink'); page.wait_for_timeout(200)
        vis = ev("getComputedStyle(document.getElementById('mhMoveChoices')).display")
        txt = ev("document.getElementById('mhMoveChoices').innerText")
        if vis == 'none' or not all(w in txt for w in ('Phone to phone', 'Send stock', 'Receive stock')): f.add('BUG', f'8: the link opens the three ways: {vis} {txt!r}')
        page.click('#mhMoveLink'); page.wait_for_timeout(150)
        if ev("getComputedStyle(document.getElementById('mhMoveChoices')).display") != 'none': f.add('BUG', '9: a second tap folds it again')
        page.click('#mhMoveLink'); page.wait_for_timeout(150); page.click('#mhMoveChoices button:has-text("Phone to phone")'); page.wait_for_timeout(500)
        if not ev("!!document.querySelector('#mhxOverlay, [id^=mhx]')"): f.add('BUG', '10: Phone to phone (QR) still opens')
    if errs: f.add('BUG', f'errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
