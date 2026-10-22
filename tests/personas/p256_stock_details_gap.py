"""Persona 256: nothing reaches the shopping system half-filled without saying so (v3.10.1152). Pete: adding food to a shop must make sure the stock and portion details the list
needs are there, whatever route added it. A food with no amount, no reorder level or no serving is "needs details": flagged on its row, counted on the cupboards card, a filter
chip, and after a bulk add they are shown at once. Non-nutritional items are exempt. Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("""(()=>{const l=loadLibrary(); l.push({name:'Zzqx Heylo Wrap',portion:'60 g',kcal:150,protein:5,fat:3,carbs:25},{name:'Zzqx Full Food',portion:'100 g',kcal:100,protein:1,fat:1,carbs:1}); localStorage.setItem(LIBRARY_KEY, JSON.stringify(l));
      mhStockTrack('Zzqx Full Food',{base:'g',serving:100}); mhStockSetLevel(mhShopKey('Zzqx Full Food'),500); mhStockSetReorder(mhShopKey('Zzqx Full Food'),100);
      mhStockTrack('Zzqx Loo Roll',{base:'each'}); const o=mhStockLoad(); o.items[mhShopKey('Zzqx Loo Roll')].nonFood=true; mhStockSave(o);})()""")
    if ev("mhStockGaps(mhStockLoad().items[mhShopKey('Zzqx Full Food')]).length") != 0: f.add('BUG', '1: a complete food has no gaps')
    if ev("mhStockGaps(mhStockLoad().items[mhShopKey('Zzqx Loo Roll')]).length") != 0: f.add('BUG', '2: non-nutritional items need nothing')
    ev("mhStockTrack('Zzqx Bare',{base:'g'})")
    g = ev("mhStockGaps(mhStockLoad().items[mhShopKey('Zzqx Bare')])")
    if g != ['how much you have', 'when to reorder', 'one serving']: f.add('BUG', f'3: a bare food lists what is missing: {g}')
    if ev("mhStockGapCount()") != 1: f.add('BUG', '4: counted')
    ev("switchTabById('shop')"); page.wait_for_timeout(300)
    card = ev("mhStockCardHtml(mhShopLoad())")
    if '1 need details' not in card: f.add('BUG', '5: the cupboards card says how many need details')
    ev("mhSlGaps()"); page.wait_for_timeout(300)
    names = page.locator('#mhSlRows [data-sl]').evaluate_all("els=>els.map(e=>e.dataset.n)")
    if names != ['Zzqx Bare']: f.add('BUG', f'6: the Needs details chip lists only those: {names}')
    if 'Still to add' not in page.inner_text('#mhSlRows'): f.add('BUG', '7: the row says what is missing')
    # bulk add: tick the library food, add to a shop: it lands incomplete and is shown straight away
    ev("(()=>{const st=mhSlState(); st.f='all'; st.q='heylo wrap'; mhShopView('stocklist');})()"); page.wait_for_timeout(300)
    page.click('#mhSlBulk button:has-text("Tick all shown")'); page.click('#mhSlBulk button:has-text("Add to my cupboards")'); page.wait_for_timeout(400)
    if ev("mhSlState().f") != 'gaps': f.add('BUG', '8: after adding, the foods that need details are shown')
    if 'need details' not in ev("document.getElementById('mhShopMsg')?.innerText||''"): f.add('BUG', '9: and it says so')
    # filling everything in clears the gap
    k = ev("mhShopKey('Zzqx Bare')")
    ev("(k=>{mhStockSetLevel(k,200); mhStockSetReorder(k,50); const o=mhStockLoad(); o.items[k].serving=25; mhStockSave(o);})", k)
    if ev("mhStockGaps(mhStockLoad().items[%r]).length" % k) != 0: f.add('BUG', '10: filled in, it needs nothing more')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
