"""Persona 210: Shopping complete adds what you bought (v3.10.1119). Pete ticks whey, cream, eggs and milk at Asda and taps Shopping
complete. Covers: only tracked items reach the review; the usual pack size is prefilled for items whose stock is known; an item whose
stock is unknown gets no prefill (never guessed) and is set from what Pete says he has; typing either units ("2 packs", "500 g") works;
an empty box leaves that item alone; a bad entry no longer stops the others: the good rows go in, the bad one stays and names the problem (v3.10.1422); 0 bought and Skip this one leave an item alone; Leave stock as it was
changes nothing; restocking clears the running-low state so it can trigger again later; the review survives a reload via the stock card."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("localStorage.setItem('mh_shop_pane','both')"); ev("document.getElementById('onboardingOverlay')?.remove()"); ev("mhShopOpen()"); ev("window.confirm=()=>true")
    ev("mhStockTrack('Whey protein',{base:'g',pack:750,serving:25,shop:'Asda'})"); ev("mhStockTrack('Double Cream (Asda)',{base:'ml',pack:300,shop:'Asda'})"); ev("mhStockTrack('Eggs',{base:'each',pack:6,shop:'Asda'})")
    wk, ck, ek = [ev("n=>mhShopKey(n)", n) for n in ('Whey protein', 'Double Cream (Asda)', 'Eggs')]
    lv = lambda k: ev("k=>mhStockLoad().items[k].level", k)
    def setup():
        ev("([a,b,c])=>{mhStockSetLevel(a,100);mhStockSetLevel(b,50);const o=mhStockLoad();o.items[c].level=null;delete o.review;mhStockSave(o);}", [wk, ck, ek])
        ev("""()=>{const s=mhShopLoad();s.items=[];['Whey protein','Double Cream (Asda)','Eggs','Milk'].forEach(n=>mhShopSetAdd(s,n,'own','',null));
          s.items.forEach(i=>{i.checked=true;i.shop=s.shop;});mhShopSave(s);}""")
        ev("mhShopComplete()"); page.click("#appModalConfirm"); page.wait_for_timeout(200)
    def box(k): return page.locator(f'input[data-k="{k}"]')
    setup()
    if ev("_shopUi.view") != 'stockbought': f.add('BUG', 'Shopping complete with tracked items must go to the review step')
    txt = page.inner_text('#mhShopPane')
    if page.locator('[data-bought] >> text=Milk').count(): f.add('BUG', 'an untracked item must not be in the stock review')
    if box(wk).input_value() != '750 g' or box(ck).input_value() != '300 ml': f.add('BUG', f'known-stock items prefill their usual pack: {box(wk).input_value()!r} {box(ck).input_value()!r}')
    if box(ek).input_value() != '': f.add('BUG', 'an item whose stock is unknown must not be prefilled (never guess)')
    if ev("mhShopLoad().items.some(i=>i.checked)"): f.add('BUG', 'the basket must still be emptied')
    # v3.10.1422: a bad entry no longer holds back the rest. The good rows go in, only the bad one stays and names its problem (was: stop everything)
    box(ck).fill('2 packs'); box(wk).fill('5'); box(ek).fill('4'); page.click('#mhBoughtDone'); page.wait_for_timeout(150)
    if (lv(wk), lv(ck), lv(ek)) != (100, 650, 4): f.add('BUG', f'the good rows go in, the bad one is left alone: {(lv(wk), lv(ck), lv(ek))}')
    if 'Add a unit' not in page.inner_text('#mhShopPane'): f.add('BUG', 'the problem must be named on the row')
    if ev("_shopUi.view") != 'stockbought' or ev("mhStockLoad().review.length") != 1: f.add('BUG', 'only the row that still needs you stays on the screen')
    if not page.locator('[data-bgtdone]').count(): f.add('BUG', 'the screen says some stock was updated')
    box(wk).fill('0'); page.click('#mhBoughtDone'); page.wait_for_timeout(150)
    if lv(wk) != 100: f.add('BUG', f'0 bought leaves that item alone: {lv(wk)}')
    if ev("_shopUi.view") != 'list' or ev("mhStockLoad().review"): f.add('BUG', 'after updating, return to the list and clear the review')
    # Skip this one takes a row out without touching its stock
    setup(); page.click('[data-bought] >> nth=0 >> text=Skip this one'); page.wait_for_timeout(150)
    if ev("mhStockLoad().review.length") != 2 or (lv(wk), lv(ck)) != (100, 50): f.add('BUG', 'Skip this one drops only that row and changes no stock')
    # leave as it was
    setup(); page.click('text=Leave stock as it was'); page.wait_for_timeout(150)
    if (lv(wk), lv(ck)) != (100, 50) or ev("mhStockLoad().review"): f.add('BUG', 'Leave stock as it was must change nothing')
    # defaults applied as typed; units either way; running low clears on restock
    ev("([a])=>{mhStockSetReorder(a,125);mhStockSetLevel(a,100);}", [wk]); ev("mhStockSweep()")
    if not ev("k=>mhShopLoad().items.some(i=>i.key===k)", wk) or not ev("k=>mhStockLoad().items[k].lowFlag", wk): f.add('BUG', 'precondition: low whey should be on the list')
    setup(); ev("([a])=>{mhStockSetLevel(a,100)}", [wk]); setup()
    page.click('#mhBoughtDone'); page.wait_for_timeout(150)
    if lv(wk) != 850: f.add('BUG', f'accepting the prefilled pack adds 750 g to 100 g: {lv(wk)}')
    if ev("k=>mhStockLoad().items[k].lowFlag", wk): f.add('BUG', 'restocking must clear the running-low state')
    # survives reload via the stock card
    setup(); page.reload(); page.wait_for_timeout(1200); ev("document.getElementById('onboardingOverlay')?.remove()"); ev("mhShopOpen()"); page.wait_for_timeout(300)
    if 'Add what you bought' not in page.inner_text('#mhShopPane'): f.add('BUG', 'a pending review must still be reachable from the stock card after a reload')
    if errs: f.add('BUG', f'page errors {errs[:3]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
