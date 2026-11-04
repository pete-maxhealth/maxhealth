"""Persona 381: My cupboards offers possible duplicates and lets you keep one (v3.10.1267).
Pete (4 Nov): "Duplicates everywhere!" (Asda Frozen Mushrooms / Frozen Mushrooms (Asda); Asda Frozen Cauliflower / Cauliflower Frozen (Asda)) - "3 yes please" to a duplicates check with merge.
Covers: the pairs found (shop-in-name, word order, plurals, sizes), NOT found (different foods, food vs non-nutritional), the tile and its count, keep one (the other removed, Undo brings it back), a want on the list kept under the food you kept, not-duplicates remembered after a reload, close, nothing offered when there are none. Invented data; real taps."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("mhShopOpen()"); page.wait_for_timeout(300)
    foods = [('Zzqx Asda Frozen Mushrooms', 'Asda', 1150), ('Zzqx Frozen Mushrooms (Asda)', 'Asda', 950), ('Zzqx Asda Frozen Cauliflower', 'Asda', 2000), ('Zzqx Cauliflower Frozen (Asda)', 'Asda', 3000),
             ('Zzqx Chicken Mince', 'Asda', 500), ('Zzqx Chicken Breast', 'Asda', 400), ('Zzqx Beef Stock Cubes (12 x)', 'Asda', 60), ('Zzqx Beef Stock Cube', 'Asda', 40)]
    for n, sh, l in foods: ev(f"mhStockTrack('{n}',{{base:'g',shop:'{sh}'}}); mhStockSetLevel(mhShopKey('{n}'),{l})")
    ev("mhStockAddNonFood('Zzqx Frozen Mushrooms Bags')"); ev("try{mhStkBack()}catch(e){}")
    ev("localStorage.removeItem('mh_stock_notdupes'); localStorage.setItem('mh_shop_pane','stock'); _shopUi.view='list'; mhShopRender()"); page.wait_for_timeout(300)
    pairs = lambda: sorted(ev("mhStockDupePairs().map(p=>[p.a.name,p.b.name].sort().join(' | '))"))
    got = pairs()
    want = sorted(['Zzqx Asda Frozen Mushrooms | Zzqx Frozen Mushrooms (Asda)', 'Zzqx Asda Frozen Cauliflower | Zzqx Cauliflower Frozen (Asda)', 'Zzqx Beef Stock Cube | Zzqx Beef Stock Cubes (12 x)'])
    if got != want: f.add('BUG', f'1: the pairs offered: {got}')
    ev("mhCbTab('all'); mhCbFoldAll(true)"); page.wait_for_timeout(300)
    label = ev("[...document.querySelectorAll('#stockctlCard .mh-tiles button')].map(b=>b.innerText.trim()).find(t=>/duplicate/i.test(t))||''")
    if '(3)' not in label: f.add('BUG', f'2: the tile shows the count: {label!r}')
    def tap(sel):
        ev("document.querySelectorAll('.toast').forEach(t=>t.style.display='none')")
        bb = page.locator(sel).first.bounding_box(); page.mouse.move(bb['x'] + bb['width'] / 2, bb['y'] + bb['height'] / 2); page.mouse.down(); page.mouse.up(); page.wait_for_timeout(450)
    ev("document.getElementById('stockctlCard').scrollIntoView()"); tap('#stockctlCard .mh-tiles button:has-text("duplicates")')
    if not ev("!!document.getElementById('stkDupeModal')"): f.add('BUG', '3: tapping the tile opens the box')
    txt = ev("(document.getElementById('stkDupeModal')?.innerText||'').toLowerCase()")
    if '1 of 3' not in txt or 'not added' not in txt: f.add('BUG', f'4: the box says 1 of 3 and that the stock is not added: {txt[:160]!r}')
    # a want on the list under the food that will be removed
    first = ev("window._stkDupes[0].a.key + '|' + window._stkDupes[0].b.key"); ka, kb = first.split('|')
    ev(f"(()=>{{const s=mhShopLoad(); mhShopSetAdd(s, mhStockLoad().items['{kb}'].name, 'own'); mhShopSave(s)}})()")
    nameA = ev(f"mhStockLoad().items['{ka}'].name")
    tap('#stkDupeModal [data-act="keepA"]')
    if ev(f"!!mhStockLoad().items['{kb}']"): f.add('BUG', '5: keep A removes B')
    if not ev(f"!!mhStockLoad().items['{ka}']"): f.add('BUG', '6: keep A keeps A')
    if not ev(f"mhShopLoad().items.some(i=>i.key==='{ka}' && i.name===mhStockLoad().items['{ka}'].name)") or ev(f"mhShopLoad().items.some(i=>i.key==='{kb}')"): f.add('BUG', '7: the want on the list moves to the food you kept')
    if '1 of 2' not in ev("(document.getElementById('stkDupeModal')?.innerText||'').toLowerCase()"): f.add('BUG', '8: the next pair comes up')
    ev("document.querySelector('#toast .toast-undo')?.click()"); page.wait_for_timeout(400)
    if not ev(f"!!mhStockLoad().items['{kb}']"): f.add('BUG', '9: Undo brings the removed food back')
    # not duplicates is remembered
    ev("window._stkDupes = mhStockDupePairs(); mhStockDupeRender()"); page.wait_for_timeout(200)
    n0 = len(pairs()); tap('#stkDupeModal [data-act="no"]')
    if len(pairs()) != n0 - 1: f.add('BUG', f'10: not duplicates takes that pair off ({n0} -> {len(pairs())})')
    page.reload(); page.wait_for_timeout(1200); ev("mhShopOpen()"); page.wait_for_timeout(300)
    if len(pairs()) != n0 - 1: f.add('BUG', f'11: and it stays off after a reload: {len(pairs())}')
    # close, and the unrelated foods are never offered
    ev("mhStockDupeOpen()"); page.wait_for_timeout(200)
    if ev("!!document.getElementById('stkDupeModal')"): tap('#stkDupeModal [data-act="close"]')
    if ev("!!document.getElementById('stkDupeModal')"): f.add('BUG', '12: Close shuts the box')
    bad = [p for p in pairs() if 'Chicken' in p or 'Bags' in p]
    if bad: f.add('BUG', f'13: different foods / non-nutritional are not offered: {bad}')
    ev("localStorage.setItem('mh_stock_notdupes', JSON.stringify(window._stkDupes ? [] : []))")
    page.screenshot(path='/tmp/p381.png')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
