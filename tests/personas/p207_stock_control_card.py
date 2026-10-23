"""Persona 207: the Stock control area under the Shopping list (v3.10.1118). Covers the standard card controls (a ? help icon, then
the same ▲ ▼ 👁 and "▾ hide" as every other card): fold remembers, the help opens, hide leaves a way back, move swaps it with the
list and remembers; tracking an ingredient through the form (counted in, pack, serving, shop, amount, reorder level, either unit);
clear messages instead of guesses (no counting unit, servings with no serving size); a low item shows LOW and lands on the list with a
"running low" tag; the picker of what you use most starts tracking in one choice; stop tracking asks first."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()"); ev("mhShopOpen()"); page.wait_for_timeout(300)
    ev("localStorage.setItem('mh_shop_pane','both')")   # these tests look at the list and the cupboards together (v3.10.1177)
    ev("mhShopRender()")
    ev("window.mhShopIsShut = (f, k) => (f && k in f) ? !!f[k] : false")   # list aisles start closed (v3.10.1172)
    def txt(sel): return ev("(s)=>document.querySelector(s)?.textContent || ''", sel)
    def vis(sel): return ev("(s)=>{const e=document.querySelector(s); return !!e && getComputedStyle(e).display!=='none'}", sel)
    def modal(which): ev("(i)=>document.getElementById(i)?.click()", which); page.wait_for_timeout(200)

    # A. the standard card controls
    if not ev("MH_CARD_FOLDS.includes('stockctl')"): f.add('BUG', 'stockctl should be registered with the card fold list')
    if not vis('#stockctlCard'): f.add('BUG', 'the Stock control card should show under the list')
    else:
        head = ev("document.querySelector('#stockctlCard .water-header')?.innerText || ''")
        if '🏠 my cupboards' not in head.lower() or '?' not in head: f.add('BUG', f'title and the ? help icon expected: {head!r}')
        ctl = ev("document.querySelector('#stockctlCard .mh-ctl')?.innerText.replace(/\\s+/g,' ').trim() || ''")
        if ctl != '▲ ▼ 👁 ▾ hide': f.add('BUG', f'controls should be the standard layout "▲ ▼ 👁 ▾ hide", got {ctl!r}')
    if vis('#stockctlDetail'): f.add('BUG', 'help text should be closed by default')
    ev("mhCardInfo('stockctl')")
    if not vis('#stockctlDetail'): f.add('BUG', 'the ? should open the help')
    ev("mhCardInfo('stockctl')")
    ev("mhCardBody('stockctl')"); ev("mhShopRender()")
    if vis('#stockctlBody') or '▸ show' not in txt('#stockctlBodyIcon'): f.add('BUG', 'fold should close the body, show "▸ show", and survive a re-render')
    ev("mhCardBody('stockctl')")
    if not vis('#stockctlBody'): f.add('BUG', 'fold should open again')
    ev("mhStockCtlHide()")
    if vis('#stockctlCard') or not vis('#mhStockShow'): f.add('BUG', 'hiding should remove the card and leave a way back')
    ev("mhStockCtlHide()")
    if not vis('#stockctlCard'): f.add('BUG', 'the way back should bring the card back')
    pos = lambda: ev("()=>{const c=document.getElementById('stockctlCard'), l=document.getElementById('mhShopChips'); return c && l ? (c.compareDocumentPosition(l) & Node.DOCUMENT_POSITION_FOLLOWING ? 'stock-first' : 'list-first') : 'missing'}")
    if pos() != 'list-first': f.add('BUG', f'by default the list comes first: {pos()}')
    ev("mhStockCtlMove('up')"); ev("mhStockCtlMove('up')")   # three sections now (list, add, stock): two steps up passes both
    if pos() != 'stock-first': f.add('BUG', 'moving up should put the stock area above the list')
    ev("mhShopOpen()")
    if pos() != 'stock-first': f.add('BUG', 'the order should be remembered')
    ev("mhStockCtlMove('down')"); ev("mhStockCtlMove('down')")
    if pos() != 'list-first': f.add('BUG', 'moving down should put it back below the list')

    # B. track an ingredient through the form
    ev("mhShopView('stockadd')"); page.wait_for_timeout(150)
    page.fill('#mhStockQ', 'Whey protein'); page.wait_for_timeout(150)
    if not vis('#mhStockTypedNew'): f.add('BUG', 'typing a new name should offer to track it as typed')
    page.click('#mhStockTypedNew'); page.wait_for_timeout(200)
    if not vis('#mhStkBase'): f.add('BUG', 'the setup form should open'); 
    # no counting unit chosen: clear message, nothing saved
    page.click('#mhStkSave'); page.wait_for_timeout(150)
    if 'Choose how this is counted' not in txt('#mhStkErr'): f.add('BUG', f'saving with no counting unit should say so: {txt("#mhStkErr")!r}')
    page.select_option('#mhStkBase', 'g'); page.wait_for_timeout(100)
    page.fill('#mhStkPack', '750'); page.fill('#mhStkLevel', '5'); page.select_option('#mhStkLevelU', 'serving')
    page.click('#mhStkSave'); page.wait_for_timeout(150)
    if 'serving' not in txt('#mhStkErr').lower(): f.add('BUG', f'servings with no serving size should be refused with a clear message: {txt("#mhStkErr")!r}')
    page.fill('#mhStkServ', '25'); page.fill('#mhStkReorder', '5'); page.select_option('#mhStkReorderU', 'serving')
    page.fill('#mhStkLevel', '30'); page.select_option('#mhStkLevelU', 'serving')
    page.click('#mhStkSave'); page.wait_for_timeout(250)
    row = ev("document.querySelector('[data-stock=\"Whey protein\"]')?.innerText.replace(/\\s+/g,' ') || ''")
    if '750 g (30 servings)' not in row or 'reorder at 125 g (5 servings)' not in row: f.add('BUG', f'the card should show the amount and reorder level both ways: {row!r}')
    if 'LOW' in row: f.add('BUG', 'a full tub is not low')
    it = ev("Object.values(mhStockLoad().items)[0]")
    if not it or it['level'] != 750 or it['reorder'] != 125 or it['pack'] != 750 or it['serving'] != 25 or it['base'] != 'g': f.add('BUG', f'stored as base units: {it}')

    # C. running low: LOW chip, onto the list with a tag
    ev("(k)=>mhStockEditView(k)", it['key']); page.wait_for_timeout(150)
    page.select_option('#mhStkLevelU', 'g'); page.fill('#mhStkLevel', '100'); page.press('#mhStkLevel', 'Tab'); page.wait_for_timeout(250)   # existing items save as you change them (v3.10.1145)
    page.click('button:has-text("Back")'); page.wait_for_timeout(250)   # autosaved: Back returns to the list
    row = ev("document.querySelector('[data-stock=\"Whey protein\"]')?.innerText.replace(/\\s+/g,' ') || ''")
    if 'LOW' not in row: f.add('BUG', f'100 g is under the 125 g reorder level so it should say LOW: {row!r}')
    on = ev("mhShopLoad().items.filter(i=>i.name==='Whey protein').map(i=>i.src)")
    if on != ['stock']: f.add('BUG', f'a low item should land on the list once, from stock: {on}')
    if 'running low' not in ev("document.querySelector('#mhShopPane [data-item=\"Whey protein\"]')?.innerText || ''"): f.add('BUG', 'the list row should say running low')
    if '1 low' not in txt('#stockctlCard'): f.add('BUG', 'the card summary should count the low items')

    # D. the picker of what you use most: one choice starts tracking
    ev("saveLibrary([{name:'Greek Yoghurt',kcal:97,protein:9,carbs:4,fat:5,portion:'150g',category:'dairy',useCount:9}])")
    ev("mhShopView('stocksuggest')"); page.wait_for_timeout(200)
    if not vis('[data-n="Greek Yoghurt"]'): f.add('BUG', 'the picker should offer what you use most')
    else:
        page.select_option('[data-n="Greek Yoghurt"] select', 'g'); page.wait_for_timeout(200)
        if ev("!!document.querySelector('[data-n=\"Greek Yoghurt\"]')"): f.add('BUG', 'once chosen it should leave the picker')
        if not ev("Object.values(mhStockLoad().items).some(i=>i.name==='Greek Yoghurt' && i.base==='g' && i.level===null)"): f.add('BUG', 'choosing a unit should start tracking with no amounts guessed')

    # E. stop tracking asks first
    ev("(k)=>mhStockEditView(k)", it['key']); page.wait_for_timeout(150)
    page.click('button:has-text("Remove from my cupboards")'); page.wait_for_timeout(200)
    if not ev("!!document.querySelector('.app-modal-overlay')"): f.add('BUG', 'stop tracking should ask first')
    modal('appModalCancel')
    if not ev("(k)=>!!mhStockLoad().items[k]", it['key']): f.add('BUG', 'cancel should keep it tracked')
    ev("(k)=>mhStockEditView(k)", it['key']); page.wait_for_timeout(150)
    page.click('button:has-text("Remove from my cupboards")'); page.wait_for_timeout(200); modal('appModalConfirm')
    if ev("(k)=>!!mhStockLoad().items[k]", it['key']): f.add('BUG', 'confirming should stop tracking')
    if not ev("mhShopLoad().items.some(i=>i.name==='Whey protein')"): f.add('BUG', 'stopping tracking must not touch the shopping list')
    if errs: f.add('BUG', f'page errors {errs[:3]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
