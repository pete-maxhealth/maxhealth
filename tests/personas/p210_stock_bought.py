"""Persona 210: Shopping complete adds what you bought (v3.10.1119). Pete ticks whey, cream, eggs and milk at Asda and taps Shopping
complete. Covers: only tracked items reach the review; the usual pack size is prefilled for items whose stock is known; an item whose
stock is unknown gets no prefill (never guessed) and is set from what Pete says he has; typing either units ("2 packs", "500 g") works;
an empty box leaves that item alone; a bad entry stops everything (no half-applied update) and names the problem; Leave stock as it was
changes nothing; restocking clears the running-low state so it can trigger again later; the review survives a reload via the stock card."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()"); ev("mhShopOpen()"); ev("window.confirm=()=>true")
    ev("mhStockTrack('Whey protein',{base:'g',pack:750,serving:25,shop:'Asda'})"); ev("mhStockTrack('Double Cream (Asda)',{base:'ml',pack:300,shop:'Asda'})"); ev("mhStockTrack('Eggs',{base:'each',pack:6,shop:'Asda'})")
    wk, ck, ek = [ev("n=>mhShopKey(n)", n) for n in ('Whey protein', 'Double Cream (Asda)', 'Eggs')]
    lv = lambda k: ev("k=>mhStockLoad().items[k].level", k)
    def setup():
        ev("([a,b,c])=>{mhStockSetLevel(a,100);mhStockSetLevel(b,50);const o=mhStockLoad();o.items[c].level=null;delete o.review;mhStockSave(o);}", [wk, ck, ek])
        ev("""()=>{const s=mhShopLoad();s.items=[];['Whey protein','Double Cream (Asda)','Eggs','Milk'].forEach(n=>mhShopSetAdd(s,n,'own','',null));
          s.items.forEach(i=>{i.checked=true;i.shop=s.shop;});mhShopSave(s);}""")
        ev("mhShopComplete()"); page.wait_for_timeout(200)
    def box(k): return page.locator(f'input[data-k="{k}"]')
    setup()
    if ev("_shopUi.view") != 'stockbought': f.add('BUG', 'Shopping complete with tracked items must go to the review step')
    txt = page.inner_text('#mhShopPane')
    if 'Milk' in txt: f.add('BUG', 'an untracked item must not be in the stock review')
    if box(wk).input_value() != '750 g' or box(ck).input_value() != '300 ml': f.add('BUG', f'known-stock items prefill their usual pack: {box(wk).input_value()!r} {box(ck).input_value()!r}')
    if box(ek).input_value() != '': f.add('BUG', 'an item whose stock is unknown must not be prefilled (never guess)')
    if ev("mhShopLoad().items.some(i=>i.checked)"): f.add('BUG', 'the basket must still be emptied')
    # bad entry stops everything
    box(ck).fill('2 packs'); box(wk).fill('5'); page.click('#mhBoughtDone'); page.wait_for_timeout(150)
    if (lv(wk), lv(ck)) != (100, 50): f.add('BUG', f'a bad entry must stop everything, nothing half-applied: {(lv(wk), lv(ck))}')
    if 'Add a unit' not in page.inner_text('#mhShopPane'): f.add('BUG', 'the problem must be named on the row')
    box(wk).fill(''); box(ek).fill('4'); page.click('#mhBoughtDone'); page.wait_for_timeout(150)
    if lv(ck) != 650: f.add('BUG', f'50 ml + 2 packs of 300 ml = 650: {lv(ck)}')
    if lv(wk) != 100: f.add('BUG', f'an emptied box leaves that item alone: {lv(wk)}')
    if lv(ek) != 4: f.add('BUG', f'unknown stock is set from what Pete says he has: {lv(ek)}')
    if ev("_shopUi.view") != 'list' or ev("mhStockLoad().review"): f.add('BUG', 'after updating, return to the list and clear the review')
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
