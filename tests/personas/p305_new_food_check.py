"""Persona 305: a food newly saved to the Library that My cupboards does not know is asked about once per batch; Later puts it in Filtered with 0 stock; release is blocked until how it is counted, reorder level, shop and where it lives are filled in; renames, starter foods and big batches never ask (v3.10.1207). Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()"); ev("localStorage.setItem('mh_shop_pane','both')")
    ev("window.__asks=[]; window.__choice='later'; window.appConfirm=(m,ok,cancel,d,l)=>{ window.__asks.push(m); if(window.__choice==='later'){cancel&&cancel()} else {ok&&ok()} }")
    base = "{id:'%s',name:'%s',kcal:100,protein:5,carbs:5,fat:5,portion:'%s'}"
    lib0 = [base % ('a', 'Zzqx Existing', '100g')]
    ev("saveLibrary(%s)" % str(lib0).replace("'", '"') if False else "saveLibrary([" + base % ('a', 'Zzqx Existing', '100g') + "])")
    ev("mhStockTrack('Zzqx Existing',{base:'g',shop:'Asda'}); mhStockSetLevel(mhShopKey('Zzqx Existing'),100)")
    ev("saveLibrary([" + base % ('a', 'Zzqx Existing', '100g') + "," + base % ('b', 'Zzqx Newone', '100g') + "," + base % ('c', 'Zzqx Slice', '1 slice') + "])"); page.wait_for_timeout(1600)
    asks = [a for a in (ev("window.__asks") or []) if a and 'New in your Library' in a]
    if len(asks) != 1: f.add('BUG', f'one question for the whole batch, got {len(asks)}')
    elif 'Zzqx Newone' not in asks[0] or 'Zzqx Slice' not in asks[0]: f.add('BUG', f'the question names the new foods: {asks[0][:200]}')
    for n in ['Zzqx Newone', 'Zzqx Slice']:
        it = ev("mhStockLoad().items[mhShopKey(%r)]" % n)
        if not it or not it.get('held') or not it.get('onboard') or it.get('level') != 0: f.add('BUG', f'{n}: in Filtered with 0 stock: {it}')
    if ev("mhStockMissing(mhStockLoad().items[mhShopKey('Zzqx Newone')]).join()") != 'reorder level,shop': f.add('BUG', 'Newone needs reorder level and shop')
    if 'how it is counted' not in ev("mhStockMissing(mhStockLoad().items[mhShopKey('Zzqx Slice')]).join()"): f.add('BUG', 'a food with no g/ml portion needs its unit chosen')
    ev("mhStockSweep()")
    if ev("mhShopLoad().items.length") != 0: f.add('BUG', 'nothing on the shopping list')
    # release blocked until complete
    k = ev("mhShopKey('Zzqx Newone')")
    ev("_shopUi.heldSel={%r:true}; mhShopHeldRelease()" % k)
    if not ev("mhStockLoad().items[%r].held" % k): f.add('BUG', 'release is blocked while details are missing')
    ev("mhStockTrack('Zzqx Newone',{base:'g',shop:'Asda'}); mhStockSetReorder(%r,200); mhStockSetStore(%r,'cupboard',0)" % (k, k))
    ev("_shopUi.heldSel={%r:true}; mhShopHeldRelease()" % k)
    it = ev("mhStockLoad().items[%r]" % k)
    if it.get('held') or it.get('onboard'): f.add('BUG', f'released once all details are in: {it}')
    # rename never asks
    n_before = len([a for a in (ev("window.__asks") or []) if a and "New in your Library" in a])
    ev("saveLibrary([" + base % ('a', 'Zzqx Existing', '100g') + "," + base % ('b', 'Zzqx Renamed', '100g') + "," + base % ('c', 'Zzqx Slice', '1 slice') + "])"); page.wait_for_timeout(1500)
    if len([a for a in (ev("window.__asks") or []) if a and "New in your Library" in a]) != n_before: f.add('BUG', 'a rename does not ask')
    # starter foods never ask
    ev("window._mhLibQuiet=true; saveLibrary([" + base % ('a', 'Zzqx Existing', '100g') + "," + base % ('d', 'Zzqx Starter', '100g') + "])"); ev("window._mhLibQuiet=false"); page.wait_for_timeout(1500)
    if len([a for a in (ev("window.__asks") or []) if a and "New in your Library" in a]) != n_before: f.add('BUG', 'starter foods do not ask')
    # a huge batch does not ask
    big = ",".join(base % ('x%d' % i, 'Zzqx Bulk %d' % i, '100g') for i in range(60))
    ev("saveLibrary([" + base % ('a', 'Zzqx Existing', '100g') + "," + big + "])"); page.wait_for_timeout(1500)
    if len([a for a in (ev("window.__asks") or []) if a and "New in your Library" in a]) != n_before: f.add('BUG', 'more than 50 at once does not ask')
    # Complete now opens the form
    ev("window.__choice='now'"); ev("saveLibrary([" + base % ('a', 'Zzqx Existing', '100g') + "," + base % ('n', 'Zzqx Fresh', '100g') + "])"); page.wait_for_timeout(1600)
    if not ev("!!_shopUi.stk && _shopUi.stk.key===mhShopKey('Zzqx Fresh')"): f.add('BUG', 'Complete now opens its details form')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
