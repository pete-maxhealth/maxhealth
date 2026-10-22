"""Persona 255: the Add foods screen (v3.10.1151). Pete: pick a shop from ALL his shops (used on this trip or not) and everything goes there; search with words in any
order, closest matches when nothing fits; one bar always on screen; the blocks have show/hide and reorder. Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 700}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("""(()=>{const l=loadLibrary(); for(let i=0;i<30;i++) l.push({name:'Zzqx Filler '+i,portion:'100 g',kcal:100,protein:1,fat:1,carbs:1});
      l.push({name:'Zzqx Heylo Other',portion:'100 g',kcal:100,protein:1,fat:1,carbs:1}); l.push({name:'Zzqx Heylo Flatbread',portion:'1 serving',kcal:150,protein:5,fat:3,carbs:25}); localStorage.setItem(LIBRARY_KEY, JSON.stringify(l));
      const s=mhShopLoad(); ['Zzqhey','Zzqtesco'].forEach(n=>{ if(!s.shops.includes(n)) s.shops.push(n); }); mhShopSave(s); mhStockTrack('Zzqx Seed',{base:'g'});})()""")
    ev("switchTabById('shop')"); page.wait_for_timeout(300)
    ev("(()=>{const st=mhSlState(); st.q=''; st.f='all'; st.shop=''; mhShopView('stocklist');})()"); page.wait_for_timeout(300)
    chips = ev("[...document.querySelectorAll('[data-slshop]')].map(e=>e.dataset.slshop)")
    if not {'Zzqhey', 'Zzqtesco'} <= set(chips) or len(chips) != ev("mhShopLoad().shops.length"): f.add('BUG', f'1: every shop is offered, used on the list or not: {chips}')
    page.click('[data-slshop="Zzqtesco"]'); page.wait_for_timeout(200)
    if ev("mhSlShop()") != 'Zzqtesco' or ev("mhShopLoad().shop") == 'Zzqtesco': f.add('BUG', '2: picking a shop sets where things go without changing the list you are shopping')
    bg = ev("getComputedStyle(document.querySelector('[data-slshop=\"Zzqtesco\"]')).backgroundColor"), ev("getComputedStyle(document.querySelector('[data-slshop=\"Zzqhey\"]')).backgroundColor")
    if bg[0] == bg[1]: f.add('BUG', '3: the chosen shop is highlighted')
    # word search, any order, closest fallback
    ev("mhSlQ('flatbread heylo')"); page.wait_for_timeout(300)
    n = page.locator('#mhSlRows [data-sl]').all_inner_texts()
    if len(n) != 1 or 'Zzqx Heylo Flatbread' not in n[0]: f.add('BUG', f'4: words in any order find it: {n}')
    ev("mhSlQ('zzqx heylo order flatbread')"); page.wait_for_timeout(300)
    n = ' '.join(page.locator('#mhSlRows [data-sl]').all_inner_texts())
    if 'Zzqx Heylo Flatbread' not in n or 'closest' not in page.inner_text('body'): f.add('BUG', '5: when nothing fits every word, the closest come first and it says so')
    ev("mhSlQ('')"); page.wait_for_timeout(300)
    # the bar is hidden until something is ticked, then stays on screen while scrolling a long list; the search box stays reachable
    if ev("getComputedStyle(document.getElementById('mhSlBulk')).display") != 'none': f.add('BUG', '6: the action bar stays hidden until something is ticked')
    ev("mhSlPickAll(true)"); page.wait_for_timeout(200)
    if ev("getComputedStyle(document.getElementById('mhSlQBox')).position") != 'sticky': f.add('BUG', '6: the search box is pinned so it is always within reach')
    page.evaluate("window.scrollTo(0, 400)"); page.wait_for_timeout(200)
    b = ev("(()=>{const r=document.getElementById('mhSlBulk').getBoundingClientRect(); return [r.top, r.bottom, innerHeight];})()")
    if not (b[1] <= b[2] + 1 and b[0] > 0): f.add('BUG', f'6: the action bar is on screen while scrolling: {b}')
    # show/hide and reorder of the blocks
    page.evaluate("window.scrollTo(0, 0)"); first = ev("[...document.querySelectorAll('[id^=mhAddf_]')].map(e=>e.id)")
    ev("mhAddfMove('ways','up')"); page.wait_for_timeout(200)
    after = ev("[...document.querySelectorAll('[id^=mhAddf_]')].map(e=>e.id)")
    if first != ['mhAddf_find', 'mhAddf_ways'] or after != ['mhAddf_ways', 'mhAddf_find']: f.add('BUG', f'7: blocks reorder: {first} {after}')
    ev("mhAddfHide('ways')"); page.wait_for_timeout(200)
    if page.locator('#mhAddf_ways').count() or not page.locator('#mhAddfShow_ways').count(): f.add('BUG', '8: a block hides and leaves a Show row')
    ev("mhShopView('list')"); ev("mhShopView('stocklist')"); page.wait_for_timeout(300)
    if page.locator('#mhAddf_ways').count(): f.add('BUG', '9: hidden stays hidden')
    page.click('#mhAddfShow_ways'); page.wait_for_timeout(200)
    if not page.locator('#mhAddf_ways').count(): f.add('BUG', '10: Show brings it back')
    # new food goes to the highlighted shop
    ev("mhSlQ('Zzqx Brand New Thing')"); page.wait_for_timeout(200); page.click('#mhSlNew button'); page.wait_for_timeout(300)
    if ev("_shopUi.stk && _shopUi.stk.shop") != 'Zzqtesco': f.add('BUG', '11: a new food defaults to the highlighted shop')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
