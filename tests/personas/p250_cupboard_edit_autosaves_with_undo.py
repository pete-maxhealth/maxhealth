"""Persona 250: the cupboard edit screen saves as you change things and has an Undo that stays on screen (v3.10.1145). Pete: Save/Cancel are used "randomly", and
overwriting a figure then wondering what it was is the real problem. Existing items autosave; Undo steps back; a bad value is refused and nothing is overwritten;
a NEW item still has one Add button; Cancel is now Back. Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("mhShopOpen()"); ev("mhStockTrack('Zzqx Flour',{base:'g',pack:1000,shop:'Asda'}); mhStockSetLevel(mhShopKey('Zzqx Flour'),800)")
    K = "mhShopKey('Zzqx Flour')"
    def level(): return ev("mhStockLoad().items[%s].level" % K)
    ev("mhStockEditView(%s)" % K); page.wait_for_timeout(300)
    txt = ev("document.getElementById('mhShopPane').innerText")
    if page.locator('#mhStkSave').count(): f.add('BUG', '1: no Save button on an existing item')
    if 'Cancel' in txt: f.add('BUG', '2: no Cancel (it is Back)')
    if not page.locator('button:has-text("Back")').count(): f.add('BUG', '3: a Back button')
    if page.locator('#mhStkUndo').count(): f.add('BUG', '4: nothing to undo yet, so no Undo')
    # change the stock: saved straight away, Undo appears and says what it will put back
    page.fill('#mhStkLevel', '500'); page.press('#mhStkLevel', 'Tab'); page.wait_for_timeout(300)
    if level() != 500: f.add('BUG', f'5: the change is saved as you make it: {level()}')
    bar = ev("document.getElementById('mhStkSaved')?.innerText||''")
    if '800' not in bar or '500' not in bar or not page.locator('#mhStkUndo').count(): f.add('BUG', f'6: a saved line shows old and new, with Undo: {bar!r}')
    # second change, then undo twice walks back
    page.fill('#mhStkLevel', '300'); page.press('#mhStkLevel', 'Tab'); page.wait_for_timeout(300)
    if level() != 300: f.add('BUG', f'7: second change saved: {level()}')
    page.click('#mhStkUndo'); page.wait_for_timeout(300)
    if level() != 500: f.add('BUG', f'8: Undo puts back the previous value: {level()}')
    if ev("document.getElementById('mhStkLevel').value") != '500': f.add('BUG', '9: and the box shows it')
    page.click('#mhStkUndo'); page.wait_for_timeout(300)
    if level() != 800: f.add('BUG', f'10: Undo again goes back to the original: {level()}')
    if page.locator('#mhStkUndo').count(): f.add('BUG', '11: nothing left to undo')
    # a bad value is refused and nothing is overwritten
    page.fill('#mhStkLevel', 'abc'); page.press('#mhStkLevel', 'Tab'); page.wait_for_timeout(300)
    if level() != 800: f.add('BUG', f'12: a bad value does not overwrite: {level()}')
    if not page.locator('#mhStkErr').count(): f.add('BUG', '13: and it says why')
    # another field: kept-in, with undo restoring it
    page.fill('#mhStkLevel', '800'); page.select_option('#mhStkStore', 'fridge'); page.wait_for_timeout(300)
    if ev("mhStockLoad().items[%s].store" % K) != 'fridge': f.add('BUG', '14: kept-in saves as you pick it')
    page.click('#mhStkUndo'); page.wait_for_timeout(300)
    if ev("mhStockLoad().items[%s].store || ''" % K) != '': f.add('BUG', '15: Undo restores where it is kept')
    # Back leaves what was saved
    page.fill('#mhStkLevel', '650'); page.press('#mhStkLevel', 'Tab'); page.wait_for_timeout(300)
    page.click('button:has-text("Back")'); page.wait_for_timeout(300)
    if level() != 650: f.add('BUG', f'16: Back keeps what you changed: {level()}')
    # a NEW item still has one explicit button and creates nothing until you press it
    ev("mhStockEditView(mhShopKey('Zzqx Sugar'), 'Zzqx Sugar')"); page.wait_for_timeout(300)
    if not page.locator('#mhStkSave:has-text("Add to my cupboards")').count(): f.add('BUG', '17: a new item has an Add button')
    page.select_option('#mhStkBase', 'g'); page.fill('#mhStkLevel', '200'); page.press('#mhStkLevel', 'Tab'); page.wait_for_timeout(300)
    if ev("!!mhStockLoad().items[mhShopKey('Zzqx Sugar')]"): f.add('BUG', '18: nothing is created until Add is pressed')
    page.click('#mhStkSave'); page.wait_for_timeout(300)
    if ev("(mhStockLoad().items[mhShopKey('Zzqx Sugar')]||{}).level") != 200: f.add('BUG', '19: Add creates it')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
