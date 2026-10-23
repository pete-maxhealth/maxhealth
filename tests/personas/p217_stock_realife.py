"""Persona 217: stock meets real life (v3.10.1123). Use-by dates (items and cooked batches, freeze/thaw, bin), 'used or binned' waste,
'ate out' logs that never touch stock, planned meals reserving stock, suggested servings capped to what stock covers, peppers being
vegetables not spices, the library-recipe builder and 'try something new' respecting the cupboards, and the transfer file carrying dates."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("localStorage.setItem('mh_shop_pane','both')")   # these tests look at the list and the cupboards together (v3.10.1177)
    ev("""saveLibrary([
      {id:'l1',name:'Cheddar',kcal:410,protein:25,carbs:0.1,fat:34,portion:'100g',useCount:5},
      {id:'l2',name:'Gouda',kcal:356,protein:25,carbs:2,fat:27,portion:'100g',useCount:5},
      {id:'l3',name:'Chicken Breast',kcal:165,protein:31,carbs:0,fat:3.6,portion:'100g',useCount:9},
      {id:'l7',name:'Butter',kcal:740,protein:0.5,carbs:0.5,fat:82,portion:'10g',useCount:9},
      {id:'l8',name:'Beef Mince',kcal:250,protein:26,carbs:0,fat:17,portion:'100g',useCount:9},
      {id:'l9',name:'Red Pepper',kcal:31,protein:1,carbs:6,fat:0.3,portion:'100g',useCount:1}
    ])""")
    ev("""localStorage.setItem('mh_recipes', JSON.stringify([
      {id:'r1',name:'Cheesy chicken',servings:2,ingredients:[{name:'Chicken Breast',amount:300,unit:'g',kcal:495,protein:93,fat:11,carbs:0},{name:'Gouda',amount:60,unit:'g',kcal:214,protein:15,fat:16,carbs:1.2}]},
      {id:'r2',name:'Butter beef',servings:2,ingredients:[{name:'Beef Mince',amount:400,unit:'g',kcal:1000,protein:104,fat:68,carbs:0},{name:'Butter',amount:20,unit:'g',kcal:148,protein:0.1,fat:16.4,carbs:0.1}]}
    ]))""")
    ev("""()=>{const r=JSON.parse(localStorage.getItem('mh_recipes'));r.forEach(x=>{x.total=x.ingredients.reduce((a,i)=>({kcal:a.kcal+(+i.kcal||0),protein:a.protein+(+i.protein||0),carbs:a.carbs+(+i.carbs||0),fat:a.fat+(+i.fat||0)}),{kcal:0,protein:0,carbs:0,fat:0})});localStorage.setItem('mh_recipes',JSON.stringify(r))}""")
    def run(kind='both'):
        ev("window.__p=''; window.callHealthAI=async(p)=>{window.__p=p; return {ok:true,text:'{\"combos\":[]}'}}")
        ev("document.querySelectorAll('.chat-bubble').forEach(b=>b.remove())")
        ev("k=>suggestMealFromLibrary(k)", kind); page.wait_for_timeout(500)
        p = ev("window.__p") or ''
        lib = p.split('LIBRARY (individual ingredients):')[1].split('RECIPES:')[0] if 'LIBRARY (individual' in p else ''
        rec = p.split('RECIPES:')[1].split('Respond ONLY')[0] if 'RECIPES:' in p else ''
        return p, lib, rec
    K = lambda n: ev("n=>mhShopKey(n)", n)
    st = lambda n: ev("n=>mhStockLoad().items[mhShopKey(n)]", n)
    lvl = lambda n, v: ev("([k,v])=>mhStockSetLevel(k,v)", [K(n), v])
    for n, b, pk in (('Cheddar', 'g', 400), ('Gouda', 'g', 300), ('Chicken Breast', 'g', 1000), ('Butter', 'g', 250), ('Beef Mince', 'g', 500)):
        ev("([n,b,pk])=>mhStockTrack(n,{base:b,pack:pk,shop:'Asda'})", [n, b, pk])
    lvl('Cheddar', 300); lvl('Gouda', 0); lvl('Chicken Breast', 800); lvl('Butter', 200); lvl('Beef Mince', 800)
    day = lambda n: ev("n=>mhAddDaysISO(n)", n)

    # 1 use-by on items
    if not ev("([k,d])=>mhStockSetUseBy(k,d)", [K('Butter'), day(1)]): f.add('BUG', '1: set a use-by')
    if 'USE UP FIRST' not in run()[0] or 'Butter' not in run()[0].split('USE UP FIRST')[1][:200]: f.add('BUG', '1: an item due tomorrow is named in USE UP FIRST')
    if 'Butter' not in ev("mhStockExtrasHtml(mhStockLoad())"): f.add('BUG', '1: the stock card shows a Use soon strip')
    if ev("k=>mhStockRowExtra(mhStockLoad().items[k],{})", K('Butter')).find('use by tomorrow') < 0: f.add('BUG', '1: the row says use by tomorrow')
    ev("([k,d])=>mhStockSetUseBy(k,d)", [K('Butter'), day(-1)]); p, lib, rec = run()
    if 'Butter' in lib: f.add('BUG', '1: butter is past its use-by and must not be offered')
    if 'Butter beef' in rec: f.add('BUG', '1: a recipe needing past-use-by butter is not offered')
    if ev("k=>mhHaveCheck('Butter','10 g',null,mhStockLoad(),'hide')").get('why') != 'past its use-by': f.add('BUG', '1: have-check names the reason')
    if 'bin it' not in ev("mhStockExtrasHtml(mhStockLoad())"): f.add('BUG', '1: past-use-by items offer to be binned')
    ev("k=>mhStockAdjust(k,250,'bought','shop')", K('Butter'))
    if st('Butter').get('useBy'): f.add('BUG', '1: buying more clears the old use-by date')
    if 'Butter' not in run()[1]: f.add('BUG', '1: butter is offered again once restocked')
    lvl('Butter', 200); ev("([k,d])=>mhStockSetUseBy(k,d)", [K('Butter'), day(5)]); lvl('Butter', 150)
    if st('Butter').get('useBy') != day(5): f.add('BUG', '1: a stock-take alone does not clear the date')
    lvl('Butter', 200); ev("k=>mhStockAdjust(k,-200,'log','y')", K('Butter'))
    if st('Butter').get('useBy'): f.add('BUG', '1: running an item out clears its date')
    lvl('Butter', 200)
    # edit form field
    ev("k=>mhStockEditView(k)", K('Butter')); page.wait_for_timeout(300)
    if not ev("!!document.getElementById('mhStkUseBy')"): f.add('BUG', '1: the edit form has a use-by date field')
    else:
        ev("_shopUi.stk.useBy='" + day(3) + "'; mhStockFormSave()")
        if st('Butter').get('useBy') != day(3): f.add('BUG', f'1: saving the form stores the date: {st("Butter")}')
    ev("([k,d])=>mhStockSetUseBy(k,d)", [K('Butter'), None])

    # 2 cooked batches
    if ev("mhRulesLoad().fridge") != 2 or ev("mhRulesLoad().frozen") != 90: f.add('BUG', '2: suggested keeping times are 2 and 90 days')
    ev("mhStockCooked('r1',2)")
    o = ev("mhStockLoad()")
    if (o.get('cookedBy') or {}).get('r1') != day(2): f.add('BUG', f'2: a fresh batch is eat-by in 2 days: {o.get("cookedBy")}')
    if 'eat by' not in ev("mhCookedByText(mhStockLoad(),'r1')"): f.add('BUG', '2: eat-by text')
    if 'LEFTOVERS READY' not in run()[2] or 'eat by' not in run()[2]: f.add('BUG', '2: leftovers go to the AI with their eat-by date')
    ev("mhCookedFreezeToggle('r1')"); o = ev("mhStockLoad()")
    if o['cookedBy']['r1'] != day(90) or not (o.get('cookedFrozen') or {}).get('r1'): f.add('BUG', '2: freezing moves the date out 90 days')
    ev("mhCookedFreezeToggle('r1')"); o = ev("mhStockLoad()")
    if o['cookedBy']['r1'] != day(2) or (o.get('cookedFrozen') or {}).get('r1'): f.add('BUG', '2: thawing puts it back to the fridge time')
    ev("mhRulesKeepSet('fridge',4)")
    if ev("mhRulesLoad().fridge") != 4: f.add('BUG', '2: fridge days are adjustable')
    ev("mhRulesKeepSet('fridge',0)")
    if ev("mhRulesLoad().fridge") != 4: f.add('BUG', '2: nonsense fridge days are refused')
    ev("mhRulesKeepSet('fridge',2)")
    # past eat-by: no longer counts as ready leftovers
    ev("()=>{const o=mhStockLoad(); o.cookedBy.r1='" + day(-1) + "'; mhStockSave(o)}")
    p, lib, rec = run()
    if 'LEFTOVERS READY' in rec: f.add('BUG', '2: leftovers past their eat-by date are not offered as ready')
    if '⚠' not in ev("mhCookedByText(mhStockLoad(),'r1')"): f.add('BUG', '2: past eat-by is flagged')
    # bin
    ev("mhCookedBinAsk('r1')"); page.wait_for_timeout(300)
    if not ev("!!document.getElementById('appModalConfirm')"): f.add('BUG', '2: binning leftovers asks first')
    else: ev("document.getElementById('appModalConfirm').click()")
    page.wait_for_timeout(300)
    if (ev("mhStockLoad().cooked||{}") or {}).get('r1'): f.add('BUG', '2: confirming removes the cooked batch')
    if (ev("mhStockLoad().cookedBy||{}") or {}).get('r1'): f.add('BUG', '2: binning clears its eat-by date')
    if 'Cheesy chicken' not in ' '.join(w['n'] for w in ev("mhWasteSummary(mhStockLoad())")): f.add('BUG', '2: binned leftovers appear in the waste summary')

    # 3 waste
    lvl('Beef Mince', 800)
    took = ev("k=>mhStockWaste(k,200)", K('Beef Mince'))
    if took != 200 or st('Beef Mince')['level'] != 600: f.add('BUG', f'3: binning 200 g takes 200 g off: {took} {st("Beef Mince")}')
    took = ev("k=>mhStockWaste(k,null)", K('Beef Mince'))
    if took != 600 or st('Beef Mince')['level'] != 0: f.add('BUG', f'3: binning all takes everything off: {took}')
    if ev("k=>mhStockWaste(k,50)", K('Beef Mince')): f.add('BUG', '3: nothing left to bin')
    if 'Beef Mince' not in ' '.join(w['n'] for w in ev("mhWasteSummary(mhStockLoad())")): f.add('BUG', '3: waste summary lists it')
    if 'waste' not in [l['s'] for l in ev("mhStockLoad().ledger")]: f.add('BUG', '3: waste is a ledger line')
    if 'Used up or binned' not in ev("mhStockCardHtml(mhShopLoad())"): f.add('BUG', '3: each stock row has a used-up/binned button')
    if 'Used up or binned in the last 30 days' not in ev("mhStockExtrasHtml(mhStockLoad())"): f.add('BUG', '3: the card summarises recent waste')
    lvl('Beef Mince', 800)

    # 4 ate out
    lvl('Chicken Breast', 800)
    chick = "[{name:'Chicken Breast',amount:'200g',kcal:330,protein:62,fat:7,carbs:0}]"
    ev("()=>logFoods(" + chick + ",'chicken takeaway')"); page.wait_for_timeout(200)
    if st('Chicken Breast')['level'] != 800: f.add('BUG', f'4: a takeaway must not touch stock: {st("Chicken Breast")["level"]}')
    if not ev("state.todayLog[state.todayLog.length-1].noStock"): f.add('BUG', '4: the entry is marked as ate-out')
    ev("()=>logFoods(" + chick + ",'chicken at home')"); page.wait_for_timeout(200)
    if st('Chicken Breast')['level'] != 600: f.add('BUG', f'4: a home meal takes 200 g off: {st("Chicken Breast")["level"]}')
    eid = ev("state.todayLog[state.todayLog.length-1].id")
    ev("i=>mhStockAteOutToggle(i)", eid)
    if st('Chicken Breast')['level'] != 800: f.add('BUG', f'4: tapping ate-out puts the stock back: {st("Chicken Breast")["level"]}')
    ev("i=>mhStockAteOutToggle(i)", eid)
    if st('Chicken Breast')['level'] != 600: f.add('BUG', '4: tapping again takes it off once more')
    ev("i=>mhStockAteOutToggle(i)", eid)
    ev("i=>{const e=state.todayLog.find(x=>x.id==i); mhStockResync(e,todayStr())}", eid)
    if st('Chicken Breast')['level'] != 800: f.add('BUG', '4: editing an ate-out entry must not take stock off')
    ev("i=>mhStockReverse(i)", eid)
    if 'data-ateout' not in ev("document.getElementById('logEntries').innerHTML"): ev("updateDashboard()")
    if 'data-ateout' not in ev("document.getElementById('logEntries').innerHTML"): f.add('BUG', '4: log rows carry the ate-out button when stock is tracked')
    if not ev("mhAteOutText('lunch at the pub',[])") or ev("mhAteOutText('chicken and rice',[])") or ev("mhAteOutText('public speaking snack',[])"):
        f.add('BUG', '4: ate-out wording: pub yes, plain meal no, "public" no')
    ev("()=>{state.todayLog=[]; saveState()}"); lvl('Chicken Breast', 800)

    # 5 planned meals reserve stock
    ev("mhStockSetReorder(mhShopKey('Chicken Breast'),400)")
    today = ev("mhISO()")
    plan = "[{name:'Chicken Breast',amount:'500g',kcal:825,protein:155,fat:18,carbs:0}]"
    p, lib, rec = run()
    if 'Cheesy chicken' not in rec: f.add('BUG', '5: before planning, Cheesy chicken is makeable')
    ev("()=>mhPlanAdd(" + plan + ",'Chicken dinner',{date:'" + today + "',time:'18:00'})"); page.wait_for_timeout(200)
    if ev("mhPlanReserved()").get(K('Chicken Breast')) != 500: f.add('BUG', f'5: the plan reserves 500 g: {ev("mhPlanReserved()")}')
    if 'planned' not in ev("k=>mhStockRowExtra(mhStockLoad().items[k],mhPlanReserved())", K('Chicken Breast')): f.add('BUG', '5: the row shows what is planned')
    if st('Chicken Breast').get('lowFlag') is not True: f.add('BUG', '5: 800 - 500 = 300 is under the reorder level, so it joins the list')
    if not any(i['key'] == K('Chicken Breast') for i in ev("mhShopLoad().items")): f.add('BUG', '5: chicken is on the shopping list because of the plan')
    plan2 = "[{name:'Chicken Breast',amount:'750g',kcal:1237,protein:232,fat:27,carbs:0}]"
    ev("()=>{localStorage.removeItem('mh_planned_v1')}"); ev("()=>mhPlanAdd(" + plan2 + ",'Big chicken',{date:'" + today + "',time:'19:00'})")
    p, lib, rec = run()
    if 'Chicken Breast' in lib: f.add('BUG', '5: only 100 g is free after the plan, below the 100 g portion check? hidden when short')
    if 'Cheesy chicken' in rec: f.add('BUG', '5: 100 g free cannot make Cheesy chicken (150 g a serving)')
    if 'set aside for planned meals' not in p: f.add('BUG', '5: the AI is told stock is set aside for plans')
    ev("()=>{localStorage.removeItem('mh_planned_v1')}"); p, lib, rec = run()
    if 'Cheesy chicken' not in rec: f.add('BUG', '5: with the plan gone Cheesy chicken is back')
    if st('Chicken Breast')['level'] != 800: f.add('BUG', '5: suggestions must never change the real stock level')

    # 6 servings cap
    lvl('Chicken Breast', 800); lvl('Cheddar', 300)
    p, lib, rec = run()
    if 'STOCK COVERS: up to' not in rec: f.add('BUG', f'6: recipes say how many servings stock covers: {rec[:300]}')
    ev("()=>{window.__sf=mhSuggestFilter(loadLibrary(),loadRecipes())}")
    cover = ev("window.__sf.notes['cheesy chicken'].cover")
    if cover is None or cover > 12 or cover < 1: f.add('BUG', f'6: cover is a sensible number: {cover}')
    lvl('Chicken Breast', 350)
    ev("()=>{window.__sf=mhSuggestFilter(loadLibrary(),loadRecipes())}")
    cover = ev("window.__sf.notes['cheesy chicken'].cover")
    if cover != 2: f.add('BUG', f'6: 350 g chicken at 150 g a serving covers 2: {cover}')
    ev("()=>{document.querySelectorAll('.chat-bubble').forEach(b=>b.remove()); renderLibraryComboSuggestions({combos:[{recipe:'Cheesy chicken',servings:5,note:'x'}]}, loadLibrary(), loadRecipes(), window.__sf)}")
    page.wait_for_timeout(300)
    html = ev("[...document.querySelectorAll('.chat-bubble')].map(b=>b.innerHTML).join('')")
    if 'data-servings-cut' not in html or '2 serving' not in html: f.add('BUG', '6: a suggested 5 servings is cut to the 2 stock covers')
    if ev("window._pendingLibraryCombos[0].servings") != 2: f.add('BUG', '6: the cut servings are what gets logged')

    # 7 peppers
    cat = lambda n: ev("n=>detectFoodCategory(n)", n)
    for n, want in (('Red Pepper', ['vegetable']), ('Peppers', ['vegetable']), ('Stuffed pepper', ['vegetable']), ('Yellow Bell Pepper', ['vegetable'])):
        if cat(n) != want: f.add('BUG', f'7: {n} is a vegetable, got {cat(n)}')
    for n in ('Black Pepper', 'Pepper', 'Red pepper flakes', 'Ground white pepper', 'Peppercorns'):
        if 'herbs and spices' not in cat(n): f.add('BUG', f'7: {n} stays a spice, got {cat(n)}')
    if ev("mhIsNever('Red Pepper', mhCatsOfName('Red Pepper'), null)"): f.add('BUG', '7: red pepper must not be treated as never-runs-out')
    ev("mhStockTrack('Red Pepper',{base:'g',pack:300,shop:'Asda'})"); lvl('Red Pepper', 0)
    if 'Red Pepper' in run()[1]: f.add('BUG', '7: counted red pepper at 0 g is hidden, not waved through as a spice')

    # 8 recipe builders respect the cupboards
    lvl('Gouda', 0); lvl('Beef Mince', 800)
    if [l for l in run()[0].split('\n') if 'Gouda' in l and 'NEEDS SWAP' not in l]: f.add('BUG', '8: out-of-stock Gouda must not appear anywhere in the next-meal prompt, including usage hints')
    ev("window.__p=''; window.callHealthAI=async(p)=>{window.__p=p; return {ok:true,text:'{}'}}")
    ev("submitRecipeFromLibrary()"); page.wait_for_timeout(500); p = ev("window.__p") or ''
    if not p: f.add('BUG', '8: library recipe builder reached the AI')
    elif 'Gouda' in p: print('  ctx:', [l[:160] for l in p.split('\n') if 'Gouda' in l][:3]); f.add('BUG', '8: out-of-stock Gouda must not be offered to the library recipe builder')
    elif 'Cheddar' not in p: f.add('BUG', '8: in-stock Cheddar is offered')
    ev("window.__p=''; document.getElementById('recipeDiscoverInput').value='a curry'; submitRecipeDiscover()"); page.wait_for_timeout(500); p = ev("window.__p") or ''
    if "CUPBOARDS" not in p or 'Cheddar' not in p: f.add('BUG', f'8: try-something-new is told what is in the cupboards: {p[:200]}')
    ev("()=>{const o=mhStockLoad(); o.items={}; mhStockSave(o)}")
    ev("window.__p=''; document.getElementById('recipeDiscoverInput').value='a curry'; submitRecipeDiscover()"); page.wait_for_timeout(500); p = ev("window.__p") or ''
    if 'CUPBOARDS' in p: f.add('BUG', '8: nothing tracked, nothing said')

    # 9 transfer file carries the dates
    for n, b, pk in (('Chicken Breast', 'g', 1000),): ev("([n,b,pk])=>mhStockTrack(n,{base:b,pack:pk,shop:'Asda'})", [n, b, pk])
    lvl('Chicken Breast', 800); ev("mhStockCooked('r1',2)")
    pack = ev("mhStockExport('Test')")
    if not pack or 'r1' not in (pack.get('cookedBy') or {}): f.add('BUG', f'9: the transfer file carries eat-by dates: {pack and list(pack)}')
    else:
        ev("p=>mhStockImportApply(p)", pack)
        if (ev("mhStockLoad().cookedBy") or {}).get('r1') != day(2): f.add('BUG', '9: importing restores the eat-by date')

    # 10 rules panel
    ev("_shopUi.rulesOpen=true")
    h = ev("mhRulesHtml()")
    if 'data-rule-keep="fridge"' not in h or 'data-rule-keep="frozen"' not in h: f.add('BUG', '10: Stock rules panel has the keeping times')
    if errs: f.add('JS-exception', errs[0])
print('\n'.join(f'{a}: {b}' for a, b in f) or 'PASS')
sys.exit(1 if f else 0)
