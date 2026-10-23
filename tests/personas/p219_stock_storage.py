"""Persona 219: fridge / freezer / cupboard (v3.10.1123). Whether a food is frozen cannot be known from its name, so each food has a 'kept in'
switch (cupboard, fridge, freezer); kept foods get a use-by date when bought: the food's OWN length if set (milk 5 days, remembered per food and
per place), else the suggested length from Stock rules (fridge 3, freezer 90, both adjustable). A date typed by hand is never overwritten.
Order import: a 'Frozen' section heading marks lines as freezer, dates count from the order's own date, the choice is remembered for next time."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from datetime import date, timedelta
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("localStorage.setItem('mh_shop_pane','both')")   # these tests look at the list and the cupboards together (v3.10.1177)
    ev("""saveLibrary([{id:'a',name:'Whole Milk',kcal:60,protein:3.4,carbs:4.7,fat:3.6,portion:'100ml'},{id:'b',name:'Sliced Mushrooms',kcal:22,protein:3,carbs:0.5,fat:0.3,portion:'100g'},{id:'c',name:'Rice',kcal:130,protein:2.7,carbs:28,fat:0.3,portion:'100g'}])""")
    ev("mhShopOpen()")
    K = lambda n: ev("n=>mhShopKey(n)", n); it = lambda n: ev("n=>mhStockLoad().items[mhShopKey(n)]", n)
    day = lambda n: ev("n=>mhAddDaysISO(n)", n)
    for n, b in (('Whole Milk', 'ml'), ('Sliced Mushrooms', 'g'), ('Rice', 'g')): ev("([n,b])=>mhStockTrack(n,{base:b,shop:'Asda'})", [n, b])
    # 1 defaults and rules
    r = ev("mhRulesLoad()")
    if r['fridgeItem'] != 3 or r['freezerItem'] != 90: f.add('BUG', f'1: suggested fridge 3 / freezer 90 days: {r}')
    # 2 buying a fridge food sets a date, a cupboard food does not
    ev("k=>mhStockSetLevel(k,1000)", K('Whole Milk')); ev("k=>mhStockSetLevel(k,500)", K('Rice'))
    if it('Whole Milk').get('useBy'): f.add('BUG', '2: no place set means no date')
    ev("k=>mhStockSetStore(k,'fridge')", K('Whole Milk'))
    m = it('Whole Milk')
    if m.get('store') != 'fridge' or m.get('useBy') != day(3) or not m.get('useByAuto'): f.add('BUG', f'2: milk in the fridge gets today + 3 days: {m}')
    # own length remembered: milk lasts 5
    ev("k=>mhStockSetStore(k,'fridge',5)", K('Whole Milk'))
    if it('Whole Milk').get('useBy') != day(5): f.add('BUG', f'3: milk set to 5 days gets today + 5: {it("Whole Milk")}')
    if it('Whole Milk')['life'].get('fridge') != 5: f.add('BUG', '3: the 5 days are remembered on the food')
    ev("k=>mhStockAdjust(k,-1000,'log','x')", K('Whole Milk'))
    if it('Whole Milk').get('useBy'): f.add('BUG', '3: running out clears the date')
    ev("k=>mhStockAdjust(k,2000,'bought','shop')", K('Whole Milk'))
    if it('Whole Milk').get('useBy') != day(5) or it('Whole Milk')['level'] != 2000: f.add('BUG', f'3: buying again uses the remembered 5 days: {it("Whole Milk")}')
    ev("k=>mhStockSetStore(k,'fridge',5)", K('Whole Milk'))
    ev("()=>{const o=mhStockLoad(); const i=o.items[mhShopKey('Whole Milk')]; i.useBy='" + day(2) + "'; mhStockSave(o)}")
    ev("k=>mhStockSetStore(k,'fridge',5)", K('Whole Milk'))
    if it('Whole Milk').get('useBy') != day(2): f.add('BUG', '3: saving the same place and length again must not reset the countdown')
    # 4 freezer and moving between places
    ev("k=>mhStockSetLevel(k,600)", K('Sliced Mushrooms')); ev("k=>mhStockSetStore(k,'freezer')", K('Sliced Mushrooms'))
    mu = it('Sliced Mushrooms')
    if mu.get('useBy') != day(90): f.add('BUG', f'4: frozen mushrooms get today + 90: {mu}')
    ev("k=>mhStockSetStore(k,'fridge')", K('Sliced Mushrooms'))
    if it('Sliced Mushrooms').get('useBy') != day(3): f.add('BUG', '4: thawed into the fridge: today + 3')
    ev("k=>mhStockSetStore(k,'freezer')", K('Sliced Mushrooms'))
    ev("k=>mhStockSetStore(k,'',undefined)", K('Sliced Mushrooms'))
    if it('Sliced Mushrooms').get('useBy') or it('Sliced Mushrooms').get('store'): f.add('BUG', '4: back to the cupboard clears the dates it worked out')
    # a hand-typed date is never overwritten
    ev("k=>mhStockSetUseBy(k,'" + day(20) + "')", K('Sliced Mushrooms')); ev("k=>mhStockSetStore(k,'freezer')", K('Sliced Mushrooms'))
    if it('Sliced Mushrooms').get('useBy') != day(20): f.add('BUG', '4: a date typed by hand wins over the calculated one')
    ev("k=>mhStockSetStore(k,'',undefined)", K('Sliced Mushrooms'))
    if it('Sliced Mushrooms').get('useBy') != day(20): f.add('BUG', '4: moving to the cupboard keeps a date typed by hand')
    ev("k=>mhStockSetUseBy(k,null)", K('Sliced Mushrooms'))
    # 5 rules are adjustable and apply
    ev("mhRulesKeepSet('fridgeItem',4)"); ev("mhRulesKeepSet('freezerItem',120)")
    if ev("mhRulesLoad().fridgeItem") != 4 or ev("mhRulesLoad().freezerItem") != 120: f.add('BUG', '5: the suggested lengths are adjustable')
    ev("mhRulesKeepSet('fridgeItem',0)"); ev("mhRulesKeepSet('freezerItem',3)")
    if ev("mhRulesLoad().fridgeItem") != 4 or ev("mhRulesLoad().freezerItem") != 120: f.add('BUG', '5: nonsense lengths are refused')
    ev("k=>mhStockSetStore(k,'freezer')", K('Sliced Mushrooms'))
    if it('Sliced Mushrooms').get('useBy') != day(120): f.add('BUG', f'5: the changed freezer length applies: {it("Sliced Mushrooms")}')
    ev("_shopUi.rulesOpen=true")
    h = ev("mhRulesHtml()")
    if 'data-rule-keep="fridgeItem"' not in h or 'data-rule-keep="freezerItem"' not in h: f.add('BUG', '5: Stock rules panel shows both lengths')
    ev("mhRulesReset()")
    # 6 row icon cycles
    h = ev("mhStockCardHtml(mhShopLoad())")
    if 'data-store=' not in h or 'mhStockStoreCycle' not in h: f.add('BUG', '6: each stock row has the kept-in icon')
    ev("k=>mhStockSetStore(k,'',undefined)", K('Rice'))
    ev("k=>mhStockStoreCycle(k)", K('Rice')); a = it('Rice').get('store')
    ev("k=>mhStockStoreCycle(k)", K('Rice')); b = it('Rice').get('store')
    ev("k=>mhStockStoreCycle(k)", K('Rice')); c = it('Rice').get('store')
    if (a, b, c) != ('fridge', 'freezer', None): f.add('BUG', f'6: tapping cycles cupboard > fridge > freezer > cupboard: {(a, b, c)}')
    # 7 edit form
    ev("k=>mhStockEditView(k)", K('Whole Milk')); page.wait_for_timeout(300)
    if not ev("!!document.getElementById('mhStkStore')") or not ev("!!document.getElementById('mhStkLife')"): f.add('BUG', '7: the edit form has Kept in and Lasts (days)')
    else:
        before = it('Whole Milk')['useBy']
        ev("mhStockFormSave()"); page.wait_for_timeout(200)
        if it('Whole Milk')['useBy'] != before: f.add('BUG', '7: saving the form unchanged must not reset the date')
        ev("k=>mhStockEditView(k)", K('Whole Milk')); page.wait_for_timeout(200)
        ev("_shopUi.stk.life='6'; mhStockFormSave()")
        if it('Whole Milk')['life']['fridge'] != 6 or it('Whole Milk')['useBy'] != day(6): f.add('BUG', f'7: a new length from the form is saved and applied: {it("Whole Milk")}')
    # 8 order import: frozen heading, remembered place, dates from the order date
    od = date.today() - timedelta(days=2); fmt = f"{od.day} {od.strftime('%b')} {od.year}"
    ORDER = f"""Order: 70000012345678
Sat {fmt} 10:00 AM to 11:00 AM
Milk, Butter & Eggs (1 item)
1 x STORE Whole Milk 2 Litres
Frozen Vegetables (2 items)
2 x STORE Sliced Mushrooms 600g
1 x STORE Broccoli Florets 1kg
Rice (1 item)
1 x STORE Basmati Rice 500g
"""
    ev("t=>mhOrdLoad(t,'x')", ORDER)
    bought = ev("_shopUi.ord.bought")
    if bought != od.isoformat(): f.add('BUG', f'8: the order date is read as the bought date: {bought} vs {od}')
    rows = ev("_shopUi.ord.rows"); by = lambda fr: next((x for x in rows if fr in x['name']), None)
    if (by('Mushrooms') or {}).get('store') != 'freezer' or (by('Broccoli') or {}).get('store') != 'freezer': f.add('BUG', f'8: lines under a Frozen heading are marked freezer: {[(x["name"], x["store"]) for x in rows]}')
    if (by('Basmati') or {}).get('store'): f.add('BUG', '8: a line with no frozen clue is left in the cupboard, never guessed')
    if (by('Milk') or {}).get('store') != 'fridge' or (by('Milk') or {}).get('storeNote') != 'as before': f.add('BUG', f'8: a food already kept in the fridge stays there: {by("Milk")}')
    ev("()=>{const R=_shopUi.ord.rows; R.find(r=>/Milk/.test(r.name)).mode='add'; R.find(r=>/Mushrooms/.test(r.name)).mode='set'}")
    ev("mhOrdApply()")
    mu = it('Sliced Mushrooms')
    want = (od + timedelta(days=90)).isoformat()
    if not mu or mu.get('store') != 'freezer' or mu.get('useBy') != want: f.add('BUG', f'8: frozen mushrooms use-by = order date + 90 days ({want}): {mu}')
    ml = it('Whole Milk')
    if ml.get('useBy') != (od + timedelta(days=6)).isoformat(): f.add('BUG', f'8: milk added on top counts from the order date with its own 6 days: {ml.get("useBy")}')
    bro = next((v for v in ev("mhStockLoad().items").values() if 'Broccoli' in v['name']), None)
    if not bro or bro.get('store') != 'freezer': f.add('BUG', f'8: a new frozen food is tracked as freezer: {bro}')
    ev("t=>mhOrdLoad(t,'x')", "Frozen Vegetables (1 item)\n1 x STORE Sliced Mushrooms 600g\n")
    if (ev("_shopUi.ord.rows[0].store")) != 'freezer' or ev("_shopUi.ord.rows[0].storeNote") != 'as before': f.add('BUG', '8: next order remembers it is frozen')
    ev("mhOrdOpen()"); ev("t=>mhOrdLoad(t,'x')", ORDER); page.wait_for_timeout(300)
    if page.locator('select[onchange*="\'store\'"]').count() < 3: f.add('BUG', '8: every order line has a kept-in choice')
    if not ev("!!document.getElementById('mhOrdBought')"): f.add('BUG', '8: the bought date is shown and editable')
    if errs: f.add('JS-exception', errs[0])
print('\n'.join(f'{a}: {b}' for a, b in f) or 'PASS')
sys.exit(1 if f else 0)
