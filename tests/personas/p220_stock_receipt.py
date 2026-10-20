"""Persona 220: receipts into stock (v3.10.1123). A till receipt (item codes, tax letters, "2 @ 3.50", weight lines, 24CT, 12RL, discounts,
totals/card/loyalty lines), an e-mailed receipt with prices on their own lines, "Qty:" lines, "2 x name price" lines, lb/oz, and tables
(columns found from the values, or chosen by the person when unsure). The receipt route ADDS on top of stock, never makes a new list;
new names get "(Shop)" on the end, library foods keep their name; non-food (toilet roll, bin bags) is tracked in items and goes on the list
as non-food when low; bought things come off the shopping list; an unmatched line can be matched by hand or created through Add Food,
which saves to the library only (nothing logged) and lands back on the import. A photo of a receipt goes through the same reader.
Invented data only."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
TILL = """COSTCO WHOLESALE 123
1 Example Road, TOWN AB1 2CD
Member 111122223333
17/10/2026 14:32
E 1111111 KS ORG EGGS 24CT 12.99 A
E 2222222 STREAKY BACON 2KG 14.99 A
E 3333333 YOG GREEK 1KG 3.50 A
2 @ 3.50
 7.00
E 4444444 BNLS CHKN BRST 17.49 A
1.234 kg @ £8.00/kg
TPD/4444444 -2.00
E 5555555 TOILET TISSUE 30RL 18.99 A
SUBTOTAL 56.97
TAX 0.00
TOTAL 56.97
VISA CARD 56.97
ITEMS SOLD 5
THANK YOU
"""
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("""saveLibrary([
      {id:'l1',name:'Cheddar',kcal:410,protein:25,carbs:0.1,fat:34,portion:'100g',useCount:5},
      {id:'l2',name:'Eggs',kcal:143,protein:12,carbs:0.7,fat:10,portion:'100g',useCount:5},
      {id:'l3',name:'Greek Yoghurt',kcal:97,protein:9,carbs:4,fat:5,portion:'100g',useCount:5},
      {id:'l4',name:'Chicken Breast',kcal:165,protein:31,carbs:0,fat:3.6,portion:'100g',useCount:9},
      {id:'l5',name:'Yeast Spread',kcal:260,protein:28,carbs:20,fat:1,portion:'100g',useCount:2}
    ])""")
    ev("mhShopOpen()")
    P = lambda t, shop='Costco': ev("([t,s])=>mhOrdParse(t,s)", [t, shop])
    A = lambda rows, frag: next((r for r in rows if frag.lower() in (r['name'] + ' ' + r['track']).lower()), None)
    # 1: a till receipt
    rows = P(TILL); names = ' | '.join(r['name'] for r in rows)
    for noise in ('TOTAL', 'VISA', 'Member', 'COSTCO', 'THANK', 'TPD', 'SUBTOTAL', 'TAX', '56.97', '14.99', '12.99', '1111111'):
        if noise in names: f.add('BUG', f'1: receipt noise, price or item code leaked into a name: {noise} :: {names}')
    if len(rows) != 5: f.add('BUG', f'1: five items on the receipt: {len(rows)} :: {names}')
    g = lambda frag: A(rows, frag) or {}
    if g('Eggs').get('amount') != '24' or g('Eggs').get('base') != 'each' or g('Eggs').get('track') != 'Eggs': f.add('BUG', f'1: KS ORG EGGS 24CT is 24 eggs linked to Eggs: {g("Eggs")}')
    if g('Bacon').get('amount') != '2000 g': f.add('BUG', f'1: 2KG bacon is 2000 g: {g("Bacon")}')
    if g('Yoghurt').get('amount') != '2000 g' or g('Yoghurt').get('track') != 'Greek Yoghurt': f.add('BUG', f'1: YOG GREEK 1KG, then "2 @ 3.50" = 2 x 1 kg linked to Greek Yoghurt: {g("Yoghurt")}')
    ch = A(rows, 'Chicken') or {}
    if ch.get('amount') != '1234 g' or ch.get('track') != 'Chicken Breast': f.add('BUG', f'1: the weighed 1.234 kg is used, BNLS CHKN BRST read as chicken breast: {ch}')
    tt = A(rows, 'Tissue') or {}
    if tt.get('kind') != 'nonfood' or tt.get('amount') != '30' or tt.get('base') != 'each' or not tt.get('on'): f.add('BUG', f'1: toilet tissue 30RL is non-food, 30 items, ticked: {tt}')
    # 2: other receipt shapes
    em = P("Cheddar 400g\n£2.50\nButter 250g\n£1.80\n")
    if [(r['track'], r['amount']) for r in em] != [('Cheddar', '400 g'), ('Butter', '250 g')]: f.add('BUG', f'2: e-mail receipt, price on its own line: {[(r["track"], r["amount"]) for r in em]}')
    q = P("Double Cream 300ml   1.20\nQty: 3\nEggs 6 pack  1.00\n")
    if (A(q, 'Cream') or {}).get('amount') != '900 ml' or (A(q, 'Eggs') or {}).get('amount') != '6': f.add('BUG', f'2: "Qty: 3" line: {[(r["name"], r["amount"]) for r in q]}')
    nx = P("2 x Cheddar 400g 5.98\n1 x Butter 250g 1.80\n")
    if [(r['track'], r['amount']) for r in nx] != [('Cheddar', '800 g'), ('Butter', '250 g')]: f.add('BUG', f'2: "2 x name price" lines: {[(r["track"], r["amount"]) for r in nx]}')
    lb = P("CHEDDAR 2LB 7.50\nHAM 8OZ 2.00\n")
    if [r['amount'] for r in lb] != ['907.18 g', '226.8 g']: f.add('BUG', f'2: lb and oz: {[r["amount"] for r in lb]}')
    if ev("t=>mhOrdParse(t,'Asda').length", "Total £5\n£1.20\n"): f.add('BUG', '2: nothing to read gives no rows')
    # 3: tables
    tb = P("5000111122223\tCheddar\t2\t400g\t5.98\n5000111122224\tButter\t1\t250g\t1.80\n")
    if [(r['track'], r['amount']) for r in tb] != [('Cheddar', '800 g'), ('Butter', '250 g')]: f.add('BUG', f'3: table with a code, name, qty, size and price column: {[(r["track"], r["amount"]) for r in tb]}')
    hd = P("Product,Qty,Weight,Total\nCheddar,2,400g,5.98\nButter,1,250g,1.80\n")
    if [(r['track'], r['amount']) for r in hd] != [('Cheddar', '800 g'), ('Butter', '250 g')]: f.add('BUG', f'3: headed CSV: {[(r["track"], r["amount"]) for r in hd]}')
    UNSURE = "cheddar\tdairy\tfridge\nbutter\tdairy\tfridge\n"
    if ev("t=>mhRcpTable(t).sure", UNSURE): f.add('BUG', '3: three text columns cannot be told apart, so it must ask')
    # 4: the map step in the UI
    ev("mhOrdOpen('receipt')"); page.wait_for_timeout(200)
    if not ev("!!document.getElementById('mhOrdText')"): f.add('BUG', '4: the paste box shows')
    else:
        page.fill('#mhOrdText', UNSURE); page.click('#mhOrdRead'); page.wait_for_timeout(300)
        if not ev("!!document.getElementById('mhOrdMapGo')"): f.add('BUG', '4: unsure columns show the which-column-is-which step')
        else:
            ev("mhOrdRole(1,'n')"); ev("mhOrdRole(0,'x')"); ev("mhOrdRole(2,'x')"); page.wait_for_timeout(100)
            if ev("_shopUi.ord.roles.join()") != 'x,n,x': f.add('BUG', f'4: the chosen columns are kept: {ev("_shopUi.ord.roles.join()")}')
            page.click('#mhOrdMapGo'); page.wait_for_timeout(300)
            r4 = ev("_shopUi.ord && _shopUi.ord.rows ? _shopUi.ord.rows.map(r=>r.track).join() : 'none'")
            if 'Dairy' not in r4: f.add('BUG', f'4: names come from the column the person chose: {r4}')
            if ev("_shopUi.ord.kind") != 'receipt': f.add('BUG', '4: still the receipt route after mapping')
    # 5: photo goes through the same reader
    ev("window._cap=null; window.callHealthAI = async (p,o)=>{window._cap={p,img:!!o.image}; return {ok:true,text:'MILK 2L 1.50\\nEGGS 12 3.00'}}; 0")
    txt = ev("mhOrdReadPhoto({base64:'x',mimeType:'image/jpeg'})")
    cap = ev("window._cap")
    if txt != 'MILK 2L 1.50\nEGGS 12 3.00' or not cap or not cap['img'] or 'Do not add' not in cap['p']: f.add('BUG', f'5: photo text via the AI, told not to guess: {txt} {cap}')
    ph = P(txt)
    if [r['amount'] for r in ph] != ['2000 ml', '12']: f.add('BUG', f'5: the photo text reads like any receipt: {[r["amount"] for r in ph]}')

    # 6: the receipt route adds on top; non-food; shop suffix; list clean-up
    ev("""()=>{ ['Cheddar','Toilet Roll (Asda)'].forEach((n,i)=>{ mhStockTrack(n,{base: i? 'each':'g', pack: i? 9:400, shop:'Asda'}); });
      mhStockSetLevel(mhShopKey('Cheddar'),400); mhStockSetReorder(mhShopKey('Cheddar'),500);
      mhStockSetLevel(mhShopKey('Toilet Roll (Asda)'),4); mhStockSetReorder(mhShopKey('Toilet Roll (Asda)'),5);
      const o=mhStockLoad(); o.items[mhShopKey('Toilet Roll (Asda)')].nonFood=true; mhStockSave(o); mhStockSweep(); }""")
    sl = ev("mhShopLoad().items.map(i=>[i.name,i.nonFood,i.cat])")
    if not any(n == 'Toilet Roll (Asda)' and nf and c == 'nonfood' for n, nf, c in sl): f.add('BUG', f'6: a non-food item that runs low goes on the list as non-food: {sl}')
    if not any(n == 'Cheddar' for n, nf, c in sl): f.add('BUG', f'6: low cheddar is on the list: {sl}')
    RC = "ASDA\nCHEDDAR 400G 2.50\nTOILET ROLL 9 PACK 4.00\nBIN BAGS 20 PACK 2.00\nBAKED BEANS 410G 0.80\n17 Oct 2026\n"
    ev("mhOrdOpen('receipt')"); page.fill('#mhOrdText', RC); page.click('#mhOrdRead'); page.wait_for_timeout(400)
    d = ev("({kind:_shopUi.ord.kind, shop:_shopUi.ord.shop, suffix:_shopUi.ord.suffix, clear:_shopUi.ord.clearList, bought:_shopUi.ord.bought, n:_shopUi.ord.rows.length, modes:_shopUi.ord.rows.map(r=>r.mode)})")
    if d['kind'] != 'receipt' or d['shop'] != 'Asda' or not d['suffix'] or not d['clear'] or d['n'] != 4: f.add('BUG', f'6: receipt route, shop read from the text, suffix and list clean-up on: {d}')
    if d['bought'] != '2026-10-17': f.add('BUG', f'6: the date in the text is the bought date: {d["bought"]}')
    if d['modes'][0] != 'add': f.add('BUG', f'6: an already-tracked food defaults to ADD on a receipt: {d["modes"]}')
    nm = ev("_shopUi.ord.rows.map(r=>mhOrdName(r,_shopUi.ord))")
    if nm[0] != 'Cheddar' or 'Bin Bags (Asda)' not in nm or 'Baked Beans (Asda)' not in nm or 'Toilet Roll (Asda)' not in nm: f.add('BUG', f'6: new names get (Asda), library foods keep theirs: {nm}')
    ev("mhOrdSuffix(false)")
    if 'Bin Bags' not in ev("_shopUi.ord.rows.map(r=>mhOrdName(r,_shopUi.ord))"): f.add('BUG', '6: suffix off leaves the plain name')
    ev("mhOrdSuffix(true)")
    ev("mhOrdShopAdd('Costco')")
    if 'Baked Beans (Costco)' not in ev("_shopUi.ord.rows.map(r=>mhOrdName(r,_shopUi.ord))"): f.add('BUG', '6: changing the shop changes the suffix')
    ev("mhOrdShopAdd('Asda')")
    if not page.locator('[data-saveas]').count(): f.add('BUG', '6: the screen says what a name will be saved as')
    page.click('#mhOrdGo'); page.wait_for_timeout(500)
    o = ev("mhStockLoad()"); it = lambda n: o['items'].get(ev("n=>mhShopKey(n)", n))
    if (it('Cheddar') or {}).get('level') != 800: f.add('BUG', f'6: 400 g + 400 g = 800 g: {it("Cheddar")}')
    if (it('Toilet Roll (Asda)') or {}).get('level') != 13: f.add('BUG', f'6: 4 rolls + 9 = 13 (typed name matches the tracked one): {it("Toilet Roll (Asda)")}')
    bb = it('Bin Bags (Asda)')
    if not bb or bb['level'] != 20 or bb['base'] != 'each' or not bb.get('nonFood'): f.add('BUG', f'6: bin bags tracked as 20 items, non-food: {bb}')
    if (it('Baked Beans (Asda)') or {}).get('level') != 410: f.add('BUG', f'6: beans 410 g: {it("Baked Beans (Asda)")}')
    sl2 = ev("mhShopLoad().items.map(i=>i.name)")
    if 'Cheddar' in sl2 or 'Toilet Roll (Asda)' in sl2: f.add('BUG', f'6: what was bought comes off the shopping list: {sl2}')
    msg = ev("(document.getElementById('mhShopMsg')||{}).textContent") or ''
    if 'Added 4 items to stock' not in msg or 'taken off your list' not in msg: f.add('BUG', f'6: the result says added and taken off: {msg}')
    if ev("Object.keys(mhShopLoad()).includes('recipe') && 0"): pass
    # next time the same line is remembered, with its shop
    nx2 = ev("t=>mhOrdParse(t,'Asda')", "BAKED BEANS 410G 0.80\nBIN BAGS 20 PACK 2.00\n")
    if [r['track'] for r in nx2] != ['Baked Beans (Asda)', 'Bin Bags (Asda)'] or not all(r['existing'] for r in nx2): f.add('BUG', f'6: next time the lines find what is already tracked: {[(r["track"], r["existing"]) for r in nx2]}')

    # 7: manual match and create new (library only, back to the list)
    RC2 = "MYSTERY SPREAD 300G 2.00\nNUT LOAF 400G 3.00\nCHEDDAR 200G 1.50\n"
    ev("mhOrdOpen('receipt')"); page.fill('#mhOrdText', RC2); page.click('#mhOrdRead'); page.wait_for_timeout(400)
    i0 = ev("_shopUi.ord.rows.findIndex(r=>/MYSTERY/.test(r.name))"); i1 = ev("_shopUi.ord.rows.findIndex(r=>/NUT LOAF/.test(r.name))")
    if not ev("_shopUi.ord.rows[%d].from === ''" % i0): f.add('BUG', '7: an unknown food shows as new/unmatched')
    if 'not matched' not in page.locator('#mhShopBody, body').first.inner_text(): f.add('BUG', '7: the screen counts the unmatched lines')
    page.locator('[data-ord="%d"] button:has-text("Match")' % i0).click(); page.wait_for_timeout(200)
    if not page.locator('#mhOrdPickList button:has-text("Yeast Spread")').count(): f.add('BUG', '7: the match list offers library foods that share a word: Yeast Spread')
    page.fill('#mhOrdPickQ', 'chick'); page.wait_for_timeout(200)
    if 'Chicken Breast' not in page.locator('#mhOrdPickList').inner_text(): f.add('BUG', '7: searching in the match list')
    page.fill('#mhOrdPickQ', 'yeast'); page.wait_for_timeout(200); page.locator('#mhOrdPickList button:has-text("Yeast Spread")').click(); page.wait_for_timeout(200)
    r0 = ev("(i=>{const r=_shopUi.ord.rows[i]; return {t:r.track,f:r.from,p:!!_shopUi.ord.pick}})", i0) if False else ev("i=>{const r=_shopUi.ord.rows[i]; return {t:r.track,f:r.from,p:!!_shopUi.ord.pick}}", i0)
    if r0['t'] != 'Yeast Spread' or r0['f'] != 'picked by you' or r0['p']: f.add('BUG', f'7: picking a food sets the line and closes the list: {r0}')
    before = ev("JSON.stringify(state)"); nlib = ev("loadLibrary().length")
    page.locator('[data-ord="%d"] button:has-text("Create new")' % i1).click(); page.wait_for_timeout(300)
    if not ev("document.getElementById('addFoodModal').classList.contains('open')"): f.add('BUG', '7: Create new opens the Add Food form')
    if ev("document.getElementById('addFoodName').value") != 'Nut Loaf (Asda)': f.add('BUG', f'7: Add Food starts with the name and shop suffix: {ev("document.getElementById(%s).value" % repr("addFoodName"))}')
    if ev("document.getElementById('addFoodKcal').value") != '': f.add('BUG', '7: nutrition is never filled in for you')
    ev("document.getElementById('addFoodKcal').value='300'; document.getElementById('addFoodProt').value='20'; document.getElementById('addFoodCarbs').value='10'; document.getElementById('addFoodFat').value='15'; document.getElementById('addFoodPortion').value='100g'; document.getElementById('addFoodPer').value='portion'")
    ev("confirmAddFood()"); page.wait_for_timeout(500)
    if ev("loadLibrary().length") != nlib + 1 or not ev("loadLibrary().some(l=>l.name==='Nut Loaf (Asda)')"): f.add('BUG', '7: the new food is saved to the library')
    if ev("document.getElementById('addFoodModal').classList.contains('open')"): f.add('BUG', '7: the form closes after saving')
    if ev("_shopUi.view") != 'orderimport' or not ev("!!_shopUi.ord"): f.add('BUG', f'7: back on the import list, import kept: {ev("_shopUi.view")}')
    r1 = ev("i=>{const r=_shopUi.ord.rows[i]; return {t:r.track,f:r.from,on:r.on}}", i1)
    if r1['t'] != 'Nut Loaf (Asda)' or 'just saved' not in r1['f']: f.add('BUG', f'7: the line now points at the new food: {r1}')
    if ev("JSON.stringify(state)") != before: f.add('BUG', '7: creating a food from the import must not log anything (save only)')
    if not page.locator('[data-ord="%d"]' % i1).count(): f.add('BUG', '7: the import list is on screen again')
    if ev("mhOrdName(_shopUi.ord.rows[%d], _shopUi.ord)" % i1) != 'Nut Loaf (Asda)': f.add('BUG', '7: a food now in the library is not given a second suffix')
    # cancelling Add Food leaves the line alone
    ev("mhOrdCreate(%d)" % i0); ev("closeAddFoodModal()")
    if ev("_addFoodOrdContext") is not None: f.add('BUG', '7: cancelling Add Food forgets the import context')
    ev("mhOrdApply()"); page.wait_for_timeout(300)
    if not ev("mhStockLoad().items[mhShopKey('Nut Loaf (Asda)')]"): f.add('BUG', '7: the created food is tracked when the import is applied')
    if errs: f.add('JS-exception', errs[0])
print('\n'.join(f'{a}: {b}' for a, b in f) or 'PASS')
sys.exit(1 if f else 0)
