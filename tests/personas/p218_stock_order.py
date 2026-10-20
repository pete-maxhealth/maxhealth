"""Persona 218: start stock from an order (v3.10.1123). Paste or choose a recent order and stock starts from it: quantity x the pack size in
the name (multipacks, kg, litres), counts read from names marked 'check', blanks left for the person (never guessed), order-page noise ignored,
substituted lines use what was sent, non-food and never-runs-out lines unticked, names linked to the library and remembered for next time,
existing counts left / added / replaced as chosen, bad amounts skipped with a message, nothing saved until the button. Invented data only."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
ORDER = """Order: 70000012345678
Sat 17 Oct 2026 10:00 AM to 11:00 AM
1 Example Street, TOWN, AB1 2CD
£120.00 (estimated)
Your order
Substitutes & unavailable
You ordered
1 x Brandx Rice Pouch Chicken 220g
0.22kg
£1.40
We sent
2 x STORE MICRO RICE 250g
£1.40
Rest of order
Dairy (3 items)
2 x STORE British Mature Cheddar 400g
0.4kg
Any 2 for £5
Write a review
£5
5 x STORE Fresh Double Cream 600ml
0.6lt
£15
2 x STORE British Milk Whole 2 Litres
2lt
1 x STORE 12 Free Range Medium Eggs
12ea
Tinned
1 x STORE Baked Beans in Tomato Sauce 4 x 410g
1.64kg
6 x Brandy Firestick 5 x 20g (100g)
1 x STORE Iceberg Lettuce
1ea
3 x STORE Chicken Breast Fillets 1kg
1 x STORE Garlic Paste 210g
2 x STORE Soft Toilet Roll 9 Pack
Shopping total £309.74
Total £303.91
Payment method
•••• 1234
"""
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("""saveLibrary([
      {id:'l1',name:'Cheddar',kcal:410,protein:25,carbs:0.1,fat:34,portion:'100g',useCount:5},
      {id:'l4',name:'Double Cream',kcal:450,protein:2,carbs:2.5,fat:48,portion:'100ml',useCount:9},
      {id:'l3',name:'Chicken Breast',kcal:165,protein:31,carbs:0,fat:3.6,portion:'100g',useCount:9}
    ])""")
    ev("mhShopOpen()")
    rows = ev("t=>mhOrdParse(t,'Asda')", ORDER)
    by = lambda frag: next((r for r in rows if frag.lower() in r['name'].lower()), None)
    names = ' | '.join(r['name'] for r in rows)
    for noise in ('Example Street', '£', 'Order:', 'Write a review', 'Payment', '1234', 'Brandx'):
        if noise in names: f.add('BUG', f'1: order-page noise or a substituted-out line became an item: {noise}')
    if not by('MICRO RICE') or by('MICRO RICE')['amount'] != '500 g': f.add('BUG', f'1: the substitute that was SENT is used: 2 x 250 g = 500 g: {by("MICRO RICE")}')
    chk = lambda frag, amt, base: (by(frag) or {}).get('amount') == amt and (by(frag) or {}).get('base') == base
    if not chk('Cheddar', '800 g', 'g'): f.add('BUG', f'1: 2 x 400 g = 800 g: {by("Cheddar")}')
    if not chk('Double Cream', '3000 ml', 'ml'): f.add('BUG', f'1: 5 x 600 ml = 3000 ml: {by("Double Cream")}')
    if not chk('Milk', '4000 ml', 'ml'): f.add('BUG', f'1: 2 x 2 Litres = 4000 ml: {by("Milk")}')
    if not chk('Beans', '1640 g', 'g'): f.add('BUG', f'1: 4 x 410 g = 1640 g: {by("Beans")}')
    if not chk('Firestick', '600 g', 'g'): f.add('BUG', f'1: 6 x (5 x 20 g) = 600 g: {by("Firestick")}')
    if not chk('Chicken Breast', '3000 g', 'g'): f.add('BUG', f'1: 3 x 1 kg = 3000 g: {by("Chicken Breast")}')
    e = by('Eggs')
    if not e or e['amount'] != '12' or not e['check'] or e['base'] != 'each': f.add('BUG', f'1: a count in the name is read but marked check: {e}')
    l = by('Lettuce')
    if not l or l['amount'] != '' or l['on']: f.add('BUG', f'1: a line with no size or count is left blank and unticked, never guessed: {l}')
    t = by('Toilet Roll')
    if not t or t['kind'] != 'nonfood' or t['base'] != 'each' or t['amount'] != '18' or not t['on']: f.add('BUG', f'1: toilet roll is not food: counted as items (2 x 9 = 18), ticked: {t}')
    g = by('Garlic')
    if not g or g['on'] or not g['never']: f.add('BUG', f'1: garlic paste is a never-runs-out food and not ticked: {g}')
    c = by('Cheddar')
    if c and c['track'] != 'Cheddar': f.add('BUG', f'1: linked to the library name Cheddar: {c["track"]} ({c["from"]})')
    if (by('Double Cream') or {}).get('track') != 'Double Cream': f.add('BUG', f'1: linked to Double Cream: {(by("Double Cream") or {}).get("track")}')
    if (by('Chicken Breast') or {}).get('track') != 'Chicken Breast': f.add('BUG', f'1: Chicken Breast Fillets linked to Chicken Breast: {(by("Chicken Breast") or {}).get("track")}')
    # plain list and CSV forms
    plain = ev("t=>mhOrdParse(t,'Asda')", "milk\ncheddar 200g\neggs")
    if len(plain) != 3 or not all(r['check'] for r in plain if not r['amount'] or r['amount'] == '1'): f.add('BUG', f'2: a plain list is read, quantities marked check: {plain}')
    csv = ev("t=>mhOrdParse(t,'Asda')", 'item,qty,size\nGouda,2,300g\nButter,1,250g\n')
    if [(r['track'], r['amount']) for r in csv] != [('Gouda', '600 g'), ('Butter', '250 g')]: f.add('BUG', f'2: CSV with item, qty, size: {[(r["track"], r["amount"]) for r in csv]}')
    if ev("t=>mhOrdParse(t,'Asda').length", "Total £5\n£1.20\n"): f.add('BUG', '2: nothing to read gives no rows')

    # UI flow: nothing saved until the button
    if 'Start stock from an order' in ev("mhStockCardHtml(mhShopLoad())"): f.add('BUG', '3: while the module is off the card only offers to turn it on')
    ev("mhStockSetOn(true)")
    if 'Start stock from an order' not in ev("mhStockCardHtml(mhShopLoad())"): f.add('BUG', '3: the Stock control card has the button')
    ev("mhOrdOpen()"); page.wait_for_timeout(300)
    if not ev("!!document.getElementById('mhOrdText')"): f.add('BUG', '3: the paste box shows')
    else:
        page.fill('#mhOrdText', ORDER); page.click('#mhOrdRead'); page.wait_for_timeout(400)
        if page.locator('[data-ord]').count() != len(rows): f.add('BUG', f'3: one row per line: {page.locator("[data-ord]").count()} vs {len(rows)}')
        if ev("Object.keys(mhStockLoad().items).length"): f.add('BUG', '3: reading the order must not save anything')
        if not ev("!!document.getElementById('mhOrdGo')"): f.add('BUG', '3: the start button shows')
        # type an amount for the lettuce and tick it; edit a track-as name
        ev("()=>{const i=_shopUi.ord.rows.findIndex(r=>/Lettuce/.test(r.name)); mhOrdSet(i,'amount','1'); mhOrdTick(i,true)}")
        ev("()=>{const i=_shopUi.ord.rows.findIndex(r=>/Beans/.test(r.name)); mhOrdSet(i,'track','Baked Beans')}")
        ev("()=>{const i=_shopUi.ord.rows.findIndex(r=>/Firestick/.test(r.name)); mhOrdSet(i,'amount','banana')}")
        page.click('#mhOrdGo'); page.wait_for_timeout(500)
    o = ev("mhStockLoad()"); it = lambda n: o['items'].get(ev("n=>mhShopKey(n)", n))
    ch = it('Cheddar')
    if not ch or ch['level'] != 800 or ch['base'] != 'g' or ch['pack'] != 400: f.add('BUG', f'4: cheddar tracked at 800 g with a 400 g pack: {ch}')
    if not it('Double Cream') or it('Double Cream')['level'] != 3000 or it('Double Cream')['base'] != 'ml': f.add('BUG', f'4: cream 3000 ml: {it("Double Cream")}')
    if not it('Baked Beans (Asda)') or it('Baked Beans (Asda)')['level'] != 1640: f.add('BUG', f'4: the edited name is used, new names get the shop on the end: {it("Baked Beans (Asda)")}')
    tr = next((v for v in o['items'].values() if 'Toilet' in v['name']), None)
    if not tr or tr['level'] != 18 or tr['base'] != 'each' or not tr.get('nonFood'): f.add('BUG', f'4: non-food is tracked in items and flagged: {tr}')
    if not it('Eggs') and not any('Eggs' in v['name'] for v in o['items'].values()): f.add('BUG', '4: eggs tracked in each')
    if it('Cheddar') and it('Cheddar').get('shop') != 'Asda' and it('Cheddar').get('shop') != ev("mhShopLoad().shop"): f.add('BUG', f'4: shop set: {it("Cheddar").get("shop")}')
    lt = next((v for v in o['items'].values() if 'Lettuce' in v['name']), None)
    if not lt or lt['level'] != 1 or lt['base'] != 'each': f.add('BUG', f'4: the amount typed for lettuce is used: {lt}')
    if any('Garlic' in v['name'] for v in o['items'].values()): f.add('BUG', '4: unticked lines must not be tracked')
    if any('Firestick' in v['name'] for v in o['items'].values()): f.add('BUG', '4: an unreadable typed amount is skipped, not guessed')
    if any(v.get('reorder') is not None for v in o['items'].values()): f.add('BUG', '4: reorder levels are never invented')
    msg = ev("(document.getElementById('mhShopMsg')||{}).textContent") or ''
    if 'Stock started for' not in msg or 'skipped' not in msg: f.add('BUG', f'4: the result is reported with what was skipped: {msg}')
    if ev("_shopUi.view") != 'list': f.add('BUG', '4: returns to the list')
    # remembered link
    rows2 = ev("t=>mhOrdParse(t,'Asda')", "1 x STORE Fresh Double Cream 600ml\n1 x STORE Baked Beans in Tomato Sauce 4 x 410g")
    b2 = next((r for r in rows2 if 'Beans' in r['name']), None)
    if not b2 or b2['track'] != 'Baked Beans (Asda)' or b2['from'] != 'remembered': f.add('BUG', f'5: an edited link is remembered for the next order: {b2}')
    # existing counts: leave / add / replace
    if not all(r['mode'] == 'leave' for r in rows2 if r['existing']): f.add('BUG', '5: already-tracked lines default to leave as they are')
    def go(mode):
        ev("t=>mhOrdLoad(t,'x')", "1 x STORE Fresh Double Cream 600ml"); ev("m=>{_shopUi.ord.rows[0].mode=m; _shopUi.ord.dupOk=true}", mode); ev("mhOrdApply()")
        return ev("mhStockLoad().items[mhShopKey('Double Cream')].level")
    if go('leave') != 3000: f.add('BUG', '5: leave keeps the count')
    if go('add') != 3600: f.add('BUG', '5: add puts 600 ml on top')
    if go('set') != 600: f.add('BUG', '5: replace sets 600 ml')
    ev("()=>{const o=mhStockLoad(); if(o.items[mhShopKey('Cheddar')]) {o.items[mhShopKey('Cheddar')].base='each'; mhStockSave(o)}}")
    ev("t=>mhOrdLoad(t,'x')", "1 x STORE British Mature Cheddar 400g"); ev("mhOrdApply()")
    if ev("mhStockLoad().items[mhShopKey('Cheddar')].level") != 800: f.add('BUG', '5: a unit clash is refused, count untouched')
    if 'g' in (ev("_shopUi.msg") or '') is False: pass
    # backups carry nothing new (no new keys)
    if errs: f.add('JS-exception', errs[0])
print('\n'.join(f'{a}: {b}' for a, b in f) or 'PASS')
sys.exit(1 if f else 0)
