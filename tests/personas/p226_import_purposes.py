"""Persona 226: one Import button with three purposes (v3.10.1124). Pete: "do we just need the one button, and is there a hint of what can and cannot be imported?",
"can it be re-run for a different list, and de-dupe?". Covers: the Add section and the cupboards section each have a single Import button (no separate CSV, receipt
and order buttons) and both open the same screen with the right purpose chosen; the screen asks "What is this?" with three choices and shows a What-can-I-import hint;
a headed CSV with a Shop column and a Food-or-not column is read as such; the "list to shop for" purpose puts the lines on the shopping list under their own shops (a new
shop is made), keeps non-nutritional things non-nutritional, leaves the cupboards completely alone, hides the storage and bought-on controls, and a second run adds nothing
twice; the "just bought" purpose adds to the cupboards; pasting the SAME receipt again is noticed (even with different spacing and capitals), the counts do not move until
"Add it again anyway" is ticked, a different receipt is not flagged, and the fingerprint survives a reload."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 3000}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    txt = lambda sel: ev("(s)=>document.querySelector(s)?.innerText || ''", sel)
    lvl = lambda part: ev("(p)=>{const it=Object.values(mhStockLoad().items).find(x=>x.name.toLowerCase().includes(p)); return it ? it.level : null}", part)

    # 1. one button in each place, both open the same screen with the right purpose
    ev("mhShopOpen(); _shopUi.addOpen = true; mhShopRender()"); page.wait_for_timeout(300)
    add_txt = txt('#shopaddCard')
    if '📥 Import' not in add_txt or 'Import a CSV' in add_txt: f.add('BUG', f'the Add section has one Import button, no separate CSV button: {add_txt[-160:]!r}')
    ev("mhStockTrack('Whole Milk',{base:'ml',pack:2000,serving:null,shop:'Asda'}); mhStockSetLevel(mhShopKey('Whole Milk'),1000); mhShopRender()"); page.wait_for_timeout(200)
    st = txt('#stockctlCard')
    if '📥 Import a receipt or order' not in st or 'Start stock from an order' in st or 'Add a receipt to stock' in st: f.add('BUG', f'the cupboards section has one Import button: {st[-300:]!r}')
    page.click('#shopaddCard .mh-tile:has-text("Import")'); page.wait_for_timeout(250)
    if ev("_shopUi.view") != 'orderimport' or ev("document.querySelector('#mhOrdPurpose input:checked')?.value") != 'list': f.add('BUG', 'the Add section opens Import with "a list to shop for" chosen')
    ev("mhShopView('list')"); page.click('#stockctlCard .mh-tile:has-text("Import")'); page.wait_for_timeout(250)
    if ev("document.querySelector('#mhOrdPurpose input:checked')?.value") != 'receipt': f.add('BUG', 'the cupboards section opens Import with "I have just bought this" chosen')
    # 2. the question and the hint
    if ev("document.querySelectorAll('#mhOrdPurpose input[type=radio]').length") != 3: f.add('BUG', 'three purposes to choose from')
    hint = txt('#mhOrdHint')
    for must in ('What can I import?', 'Works', 'Does not', 'PDF', 'nothing is saved'):
        if must.lower() not in hint.lower(): f.add('BUG', f'the hint says {must!r}: {hint[:200]!r}')

    # 3. a list to shop for: headed CSV with Shop and Type columns
    ev("mhOrdOpen('list')")
    csv = 'Item,Qty,Shop,Type\nGarlic Bread 300g,2,Asda,Food\nBin bags 40 pack,1,Tesco,Non-food\nCheddar 400g,1,Tesco,\nZorblax widget,1,Asda,Non-food\n'
    stock_before = ev("JSON.stringify(mhStockLoad().items)")
    ev("t=>mhOrdLoad(t,'your file')", csv); page.wait_for_timeout(250)
    d = ev("_shopUi.ord")
    if not d or d.get('stage') or [r['shop'] for r in d['rows']] != ['Asda', 'Tesco', 'Tesco', 'Asda']: f.add('BUG', f'the Shop column is read per line: {d and [r.get("shop") for r in d.get("rows", [])]}')
    elif [r['kind'] for r in d['rows']][:2] != ['food', 'nonfood'] or d['rows'][3]['kind'] != 'nonfood': f.add('BUG', f'the Food or not column is read: {[r["kind"] for r in d["rows"]]}')
    body = txt('#mhShopPane')
    if 'Kept in' in body or ev("!!document.getElementById('mhOrdBought')") or 'Put 4 items on my list' not in body: f.add('BUG', f'list mode hides storage and bought-on and says what it will do: {body[-300:]!r}')
    ev("mhOrdApply()"); page.wait_for_timeout(300)
    items = ev("mhShopLoad().items.map(i=>[i.name,i.shop,!!i.nonFood])")
    got = {n: (sh, nf) for n, sh, nf in items}
    if not any(k.startswith('Garlic Bread') and v == ['Asda', False] for k, v in map(lambda kv: (kv[0], list(kv[1])), got.items())): f.add('BUG', f'garlic bread is on the list under Asda: {items}')
    if not any(k.startswith('Bin Bags') and v[0] == 'Tesco' and v[1] for k, v in got.items()): f.add('BUG', f'bin bags are on the list under Tesco as non-nutritional: {items}')
    if 'Tesco' not in ev("mhShopLoad().shops"): f.add('BUG', 'a new shop from the file is made')
    if ev("JSON.stringify(mhStockLoad().items)") != stock_before: f.add('BUG', 'a list import leaves the cupboards completely alone')
    n_list = len(items)
    ev("mhOrdOpen('list')"); ev("t=>mhOrdLoad(t,'your file')", csv); ev("mhOrdApply()"); page.wait_for_timeout(250)
    if ev("mhShopLoad().items.length") != n_list: f.add('BUG', 'running the same list again adds nothing twice')
    if 'already on it' not in (ev("document.getElementById('mhShopMsg')?.innerText") or ''): f.add('BUG', 'it says how many were already on the list')

    # 4. just bought: adds to the cupboards, then the same receipt twice
    rec = '2 x STORE Fresh Skimmed Milk 2L\n1 x STORE Mature Cheddar 400g\n'
    ev("mhOrdOpen('receipt')"); ev("t=>mhOrdLoad(t,'x')", rec); ev("mhOrdApply()"); page.wait_for_timeout(300)
    milk1, ched1 = lvl('skimmed'), lvl('cheddar')
    if milk1 != 4000 or ched1 != 400: f.add('BUG', f'a receipt adds to the cupboards: milk {milk1}, cheddar {ched1}')
    rec2 = '2 x STORE   FRESH skimmed milk 2L\n\n1 x STORE Mature Cheddar 400g'
    ev("mhOrdOpen('receipt')"); ev("t=>mhOrdLoad(t,'x')", rec2); page.wait_for_timeout(250)
    if not ev("!!document.getElementById('mhOrdDup')") or 'You added this on' not in txt('#mhOrdDup'): f.add('BUG', 'the same receipt is noticed, even with different spacing and capitals')
    ev("mhOrdApply()"); page.wait_for_timeout(250)
    if lvl('skimmed') != milk1 or lvl('cheddar') != ched1: f.add('BUG', 'the counts must not move until the repeat is confirmed')
    if ev("_shopUi.view") != 'orderimport': f.add('BUG', 'a blocked repeat stays on the screen')
    page.check('#mhOrdDupOk'); page.wait_for_timeout(150); ev("mhOrdApply()"); page.wait_for_timeout(300)
    if lvl('skimmed') != milk1 + 4000: f.add('BUG', f'ticking Add it again anyway adds it: {lvl("skimmed")}')
    ev("mhOrdOpen('receipt')"); ev("t=>mhOrdLoad(t,'x')", '1 x STORE Smooth Peanut Butter 340g'); page.wait_for_timeout(200)
    if ev("!!document.getElementById('mhOrdDup')"): f.add('BUG', 'a different receipt is not flagged')
    ev("_shopUi.ord=null; mhShopView('list')")
    # 5. the fingerprint is kept with the stock
    page.reload(); page.wait_for_timeout(1200)
    ev("mhShopOpen(); mhOrdOpen('receipt')"); ev("t=>mhOrdLoad(t,'x')", rec); page.wait_for_timeout(250)
    if not ev("!!document.getElementById('mhOrdDup')"): f.add('BUG', 'the fingerprint survives a reload')
    if errs: f.add('BUG', f'page errors: {errs[:3]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
