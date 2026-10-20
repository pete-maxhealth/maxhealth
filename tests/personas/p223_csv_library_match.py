"""Persona 223: the CSV import finds foods in the library the way the order reader does, and stops asking about everyday groceries (v3.10.1124).
Pete's real case: "COOK by ASDA Cook by Mediterranean Veg Mix 500g" is "Asda Mediterranean Frozen Vegetables" in his library, which the strict
CSV match could not see (range name, "Veg" for "Vegetables", extra words). Covers: that line is offered as "Same as <library name>" with the
tick OFF (a loose match is never linked for you); Accept all suggestions turns it on and the shopping item takes the library name; a line
nothing in the library resembles gets no suggestion; coffee, squash, bread and a squash-like word are sure to be food and no longer ask;
Toilet roll still asks (non-food is spotted, never decided for you); "tea towel" is not mistaken for tea; an unknown name (Zorblax) still
asks; and the button on the review screen now says Non-nutritional, not "Not food"."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()"); ev("mhShopOpen()")
    LIB = 'Asda Mediterranean Frozen Vegetables'
    ev("l=>saveLibrary(l.concat(loadLibrary()))", [{'name': LIB, 'kcal': 30, 'protein': 1.5, 'fat': 0.5, 'carbs': 4, 'portion': '100g'}]); nlib = ev("loadLibrary().length")
    csv = ('Item,Qty,Shop\nCOOK by ASDA Cook by Mediterranean Veg Mix 500g,3,Asda\nASDA Gold Roasted Coffee 200g,1,Asda\nVimto Real Fruit Squash 2 Litre,1,Asda\n'
           'Warburtons Medium Toastie Soft & Sliced White Loaf 800g,2,Asda\nToilet roll 9 pack,1,Asda\nTea towels,1,Asda\nZorblax,,Asda\nGlorbnak Pie,,Asda\n')
    ev("t=>mhShopCsvLoad(t,'order.csv')", csv); page.wait_for_timeout(200)
    by = {r['name']: r for r in ev("_shopUi.csv.rows")}
    v = by['COOK by ASDA Cook by Mediterranean Veg Mix 500g']
    if v['match'].get('options') != [LIB] or v['link'] != LIB: f.add('BUG', f'the library food is offered for the Veg Mix line: {v["match"]} link={v["link"]}')
    if v['linkOn']: f.add('BUG', 'a loose library match must not be linked for you: the tick starts off')
    if not v['kindSure']: f.add('BUG', 'a line that matches a library food is sure to be food')
    for n in ('ASDA Gold Roasted Coffee 200g', 'Vimto Real Fruit Squash 2 Litre', 'Warburtons Medium Toastie Soft & Sliced White Loaf 800g'):
        if not by[n]['kindSure'] or by[n]['kind'] != 'food': f.add('BUG', f'everyday grocery should not ask whether it is food: {n}')
        if by[n]['link'] or by[n]['linkOn']: f.add('BUG', f'nothing in the library resembles it, so no suggestion: {n}')
    if by['Toilet roll 9 pack']['kind'] != 'nonfood' or by['Toilet roll 9 pack']['kindSure']: f.add('BUG', 'toilet roll is spotted as non-food but still confirmed')
    if by['Tea towels']['kind'] != 'nonfood' or by['Tea towels']['kindSure']: f.add('BUG', 'tea towels must not be taken for tea')
    for n in ('Zorblax', 'Glorbnak Pie'):
        if by[n]['kindSure']: f.add('BUG', f'a name nobody knows must still ask: {n}')
    # the screen: the suggestion shows, the button wording is the new one
    txt = page.inner_text('#mhShopPane')
    if 'Same as' not in txt or LIB not in txt: f.add('BUG', f'the review shows "Same as {LIB}": {txt[:300]}')
    if 'Non-nutritional' not in txt: f.add('BUG', 'the review button says Non-nutritional')
    if 'Not food' in txt: f.add('BUG', 'the old wording Not food is still on the review screen')
    if ev("document.querySelector('[data-csv^=\"COOK by\"] input[type=checkbox]')?.checked"): f.add('BUG', 'the Same-as tick starts off')
    # accept the suggestions: now it links, and the item that reaches the list carries the library name
    for n in ('Toilet roll 9 pack', 'Tea towels', 'Zorblax', 'Glorbnak Pie'):
        page.click(f'[data-csv="{n}"] button:has-text("{"Non-nutritional" if "oilet" in n or "owel" in n else "Food"}")')
    page.click('button:has-text("Accept all suggestions")'); page.wait_for_timeout(150)
    if not ev("_shopUi.csv.rows[0].linkOn"): f.add('BUG', 'Accept all suggestions turns the tick on')
    page.click('#mhCsvGo'); page.wait_for_timeout(300)
    names = ev("mhShopLoad().items.map(i=>i.name)")
    if LIB not in names or any(n.startswith('COOK by') for n in names): f.add('BUG', f'the accepted link puts the library name on the list: {names}')
    if ev("loadLibrary().length") != nlib: f.add('BUG', 'an import never changes the food library')
    if errs: f.add('BUG', f'page errors: {errs[:3]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
