"""Persona 216: meal suggestions only use what can be made (v3.10.1123). Next meal idea / Balance my macros / category picker all go through
suggestMealFromLibrary, which must filter its lists by stock before the AI sees them. This test replaces callHealthAI, runs the real function
and reads the prompt it would have sent. Covers: out/short foods hidden; foods not counted still offered in 'hide' but not in 'strict'; herbs and
spices not counted always offered, counted ones obey their count; recipes offered only when every ingredient is in stock, swappable for a
counted like-for-like with close macros (never a carbier or a different meat), or already cooked and waiting; a recipe with a missing figure is
never offered; 'off' changes nothing; nothing tracked changes nothing; the nothing-fits message; the footer and the setting being saved/restored."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("window._mhLibQuiet=true"); ev("localStorage.setItem('mh_shop_pane','both')"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("""saveLibrary([
      {id:'l1',name:'Cheddar',kcal:410,protein:25,carbs:0.1,fat:34,portion:'100g',useCount:5},
      {id:'l2',name:'Gouda',kcal:356,protein:25,carbs:2,fat:27,portion:'100g',useCount:5},
      {id:'l3',name:'Chicken Breast',kcal:165,protein:31,carbs:0,fat:3.6,portion:'100g',useCount:9},
      {id:'l4',name:'Double Cream',kcal:450,protein:2,carbs:2.5,fat:48,portion:'100ml',useCount:9},
      {id:'l5',name:'Dried Oregano',kcal:265,protein:9,carbs:27,fat:4,portion:'1g',useCount:1},
      {id:'l6',name:'Black Pepper',kcal:251,protein:10,carbs:64,fat:3,portion:'1g',useCount:1},
      {id:'l7',name:'Butter',kcal:740,protein:0.5,carbs:0.5,fat:82,portion:'10g',useCount:9},
      {id:'l8',name:'Beef Mince',kcal:250,protein:26,carbs:0,fat:17,portion:'100g',useCount:9}
    ])""")
    ev("""localStorage.setItem('mh_recipes', JSON.stringify([
      {id:'r1',name:'Cheesy chicken',servings:2,ingredients:[{name:'Chicken Breast',amount:300,unit:'g',kcal:495,protein:93,fat:11,carbs:0},{name:'Gouda',amount:60,unit:'g',kcal:214,protein:15,fat:16,carbs:1.2},{name:'Dried Oregano',amount:2,unit:'g',kcal:5,protein:0,fat:0,carbs:0.5}]},
      {id:'r2',name:'Cream chicken',servings:2,ingredients:[{name:'Chicken Breast',amount:300,unit:'g',kcal:495,protein:93,fat:11,carbs:0},{name:'Double Cream',amount:100,unit:'ml',kcal:450,protein:2,fat:48,carbs:2.5}]},
      {id:'r3',name:'Figureless stew',servings:2,ingredients:[{name:'Chicken Breast',amount:300,unit:'g',kcal:495,protein:93,fat:11,carbs:0},{name:'Mystery sauce',amount:50,unit:'g',kcal:'',protein:'',fat:'',carbs:''}]},
      {id:'r4',name:'Beef bake',servings:2,ingredients:[{name:'Beef Mince',amount:400,unit:'g',kcal:1000,protein:104,fat:68,carbs:0}]}
    ]))""")
    ev("""()=>{const r=JSON.parse(localStorage.getItem('mh_recipes'));r.forEach(x=>{x.total=x.ingredients.reduce((a,i)=>({kcal:a.kcal+(+i.kcal||0),protein:a.protein+(+i.protein||0),carbs:a.carbs+(+i.carbs||0),fat:a.fat+(+i.fat||0)}),{kcal:0,protein:0,carbs:0,fat:0});});localStorage.setItem('mh_recipes',JSON.stringify(r));}""")
    def run(kind='both', comp=None):
        """Run the real function with a fake AI; return the prompt it built (or '' if the AI was never called) and the page text added."""
        ev("window.__p=''; window.callHealthAI=async(p)=>{window.__p=p; return {ok:true,text:'{\"combos\":[]}'}}")
        ev("document.querySelectorAll('.chat-bubble').forEach(b=>b.remove())")
        ev("([k,c])=>suggestMealFromLibrary(k,c)", [kind, comp]); page.wait_for_timeout(500)
        p = ev("window.__p") or ''; lib = p.split('LIBRARY (individual ingredients):')[1].split('RECIPES:')[0] if 'LIBRARY (individual' in p else ''
        rec = p.split('RECIPES:')[1].split('Respond ONLY')[0] if 'RECIPES:' in p else ''
        return p, lib, rec
    K = lambda n: ev("n=>mhShopKey(n)", n)
    # 0 nothing tracked: nothing changes, nothing hidden
    p, lib, rec = run()
    for n in ('Cheddar', 'Gouda', 'Chicken Breast', 'Butter', 'Beef Mince', 'Dried Oregano'):
        if n not in lib: f.add('BUG', f'0: nothing is tracked, so {n} must still be offered')
    for r in ('Cheesy chicken', 'Cream chicken', 'Beef bake'):
        if r not in rec: f.add('BUG', f'0: nothing tracked, recipe {r} must still be offered')
    if 'Figureless stew' in rec: pass   # untracked: filter inactive, as before (not this feature's business)
    # track some
    ev("mhStockTrack('Cheddar',{base:'g',pack:400,shop:'Asda'})"); ev("mhStockTrack('Gouda',{base:'g',pack:300,shop:'Asda'})"); ev("mhStockTrack('Chicken Breast',{base:'g',pack:1000,shop:'Asda'})")
    ev("mhStockTrack('Double Cream',{base:'ml',pack:300,shop:'Asda'})"); ev("mhStockTrack('Butter',{base:'g',pack:250,shop:'Asda'})"); ev("mhStockTrack('Dried Oregano',{base:'g',pack:10,shop:'Asda'})")
    lvl = lambda n, v: ev("([k,v])=>mhStockSetLevel(k,v)", [K(n), v])
    lvl('Cheddar', 300); lvl('Gouda', 0); lvl('Chicken Breast', 800); lvl('Double Cream', 50); lvl('Butter', 200); lvl('Dried Oregano', 5)
    # 1 hide mode (default): out/short hidden, uncounted shown, herbs/spices uncounted shown
    if ev("mhSuggestMode()") != 'hide': f.add('BUG', '1: default mode is hide')
    p, lib, rec = run()
    if 'Gouda' in lib: f.add('BUG', '1: Gouda is out (0 g) and must not be offered')
    if 'Cheddar' not in lib or 'Chicken Breast' not in lib or 'Butter' not in lib: f.add('BUG', '1: counted foods with enough must be offered')
    if 'Beef Mince' not in lib: f.add('BUG', '1: Beef Mince is not counted: hide mode assumes it is in the cupboard')
    if 'Black Pepper' not in lib: f.add('BUG', '1: Black Pepper (spice, uncounted) always counts as in')
    if 'Double Cream' in lib: f.add('BUG', '1: 50 ml cream cannot cover the 100 ml portion: short, must be hidden')
    # recipes: Cheesy chicken needs Gouda (out) -> swap to Cheddar (counted, in stock, same category, close macros, carbs lower)
    if 'Cheesy chicken' not in rec: f.add('BUG', f'1: Cheesy chicken should be offered with Gouda swapped for Cheddar: {rec[:300]}')
    elif 'NEEDS SWAP: Gouda for Cheddar' not in rec: f.add('BUG', f'1: the swap must be stated to the AI: {rec[:300]}')
    if 'Figureless stew' in rec: f.add('BUG', '1: a recipe with an ingredient that has no figures is never offered')
    if 'Beef bake' not in rec: f.add('BUG', '1: Beef bake: mince uncounted, assumed in')
    if 'STOCK: these lists have already been limited' not in p: f.add('BUG', '1: the prompt tells the AI the lists are limited to stock')
    # cream: need for 1 serving of Cream chicken = 100/2 = 50 ml; level 50 covers it exactly. Make it short to prove the block
    lvl('Double Cream', 40); p, lib, rec = run()
    if 'Cream chicken' in rec: f.add('BUG', '1b: 40 ml cream cannot cover 50 ml for one serving and there is no swap: not offered')
    lvl('Double Cream', 60); p, lib, rec = run()
    if 'Cream chicken' not in rec: f.add('BUG', '1c: 60 ml cream covers one serving')
    # swap gate: if Cheddar is a carbier / different macros it must not be offered. Make Cheddar carby: carbs 8 vs Gouda 2 -> refuse
    ev("()=>{const l=loadLibrary();l.find(x=>x.name==='Cheddar').carbs=20;saveLibrary(l);}"); p, lib, rec = run()
    if 'Cheesy chicken' in rec: f.add('BUG', '2: a swap that adds carbs must not be offered (Cheddar at 20 g vs Gouda 2 g per 100 g)')
    ev("()=>{const l=loadLibrary();l.find(x=>x.name==='Cheddar').carbs=0.1;saveLibrary(l);}")
    # swap needs a COUNTED substitute: untrack Cheddar -> no swap
    ev("()=>{const o=mhStockLoad();delete o.items[mhShopKey('Cheddar')];localStorage.setItem(MH_STOCK_KEY,JSON.stringify(o));}"); p, lib, rec = run()
    if 'Cheesy chicken' in rec: f.add('BUG', '2: a swap target that is not counted in stock must not be used')
    ev("mhStockTrack('Cheddar',{base:'g',pack:400,shop:'Asda'})"); lvl('Cheddar', 300)
    # 3 cooked leftovers make a recipe available even with nothing in stock
    lvl('Chicken Breast', 0); lvl('Butter', 0)
    p, lib, rec = run()
    if 'Cheesy chicken' in rec or 'Cream chicken' in rec: f.add('BUG', '3: chicken is out, recipes using it are not offered')
    if 'Chicken Breast' in lib: f.add('BUG', '3: chicken out must be hidden')
    ev("()=>{const o=mhStockLoad();o.cooked={r2:2};localStorage.setItem(MH_STOCK_KEY,JSON.stringify(o));}"); p, lib, rec = run()
    if 'Cream chicken' not in rec or 'LEFTOVERS READY: 2' not in rec: f.add('BUG', f'3: 2 cooked servings waiting make it offerable and say so: {rec[:300]}')
    ev("()=>{const o=mhStockLoad();o.cooked={};localStorage.setItem(MH_STOCK_KEY,JSON.stringify(o));}"); lvl('Chicken Breast', 800); lvl('Butter', 200)
    # 4 herbs and spices: counted ones obey their count
    lvl('Dried Oregano', 0); p, lib, rec = run()
    if 'Dried Oregano' in lib: f.add('BUG', '4: a counted spice at 0 is out, like anything else')
    if 'Black Pepper' not in lib: f.add('BUG', '4: uncounted spices stay in')
    lvl('Dried Oregano', 5)
    # 5 strict: only counted foods (plus herbs and spices)
    ev("mhSuggestSetMode('strict')"); p, lib, rec = run()
    if 'Beef Mince' in lib: f.add('BUG', '5: strict: Beef Mince is not counted, must not be offered')
    if 'Black Pepper' not in lib: f.add('BUG', '5: strict: uncounted spices still count as in')
    if 'Cheddar' not in lib: f.add('BUG', '5: strict: counted food in stock is offered')
    if 'Beef bake' in rec: f.add('BUG', '5: strict: a recipe with an uncounted ingredient is not offered')
    # 6 off: everything, exactly as before
    ev("mhSuggestSetMode('off')"); p, lib, rec = run()
    for n in ('Gouda', 'Double Cream', 'Beef Mince', 'Cheddar'):
        if n not in lib: f.add('BUG', f'6: off mode offers everything, missing {n}')
    if 'Figureless stew' not in rec or 'STOCK: these lists' in p: f.add('BUG', '6: off mode is the old behaviour (all recipes, no stock line)')
    # 7 settings: saved, in the key the backups carry, and shown in the Stock card
    if ev("JSON.parse(localStorage.getItem('mh_shopping_suggest_v1')).mode") != 'off': f.add('BUG', '7: mode saved in mh_shopping_suggest_v1')
    ev("mhSuggestSetMode('hide')"); ev("mhShopOpen()"); page.wait_for_timeout(300)
    if page.locator('#mhSuggestMode').count() != 1 or page.locator('#mhSuggestMode').input_value() != 'hide': f.add('BUG', '7: the Stock card shows the setting')
    if 'mh_shopping_suggest_v1' not in ev("Object.keys(_collectBackupSettings().settings||_collectBackupSettings())"): f.add('BUG', '7: the setting travels in backups')
    # 8 nothing makes a meal: friendly message with a way out
    ev("saveLibrary([{id:'z1',name:'Gouda',kcal:356,protein:25,carbs:2,fat:27,portion:'100g',useCount:5}])"); ev("localStorage.setItem('mh_recipes','[]')")
    ev("mhSuggestSetMode('hide')"); p, lib, rec = run(); txt = ev("[...document.querySelectorAll('.chat-bubble')].map(b=>b.textContent).join(' | ')")
    if p: f.add('BUG', '8: nothing makeable: the AI must not be called')
    if 'Nothing in your cupboards makes a meal' not in txt or 'Suggest from everything instead' not in txt: f.add('BUG', '8: the nothing-fits message with a way out is shown')
    # 9 footer on a real result
    ev("saveLibrary([{id:'c1',name:'Cheddar',kcal:410,protein:25,carbs:0.1,fat:34,portion:'100g',useCount:5},{id:'c2',name:'Gouda',kcal:356,protein:25,carbs:2,fat:27,portion:'100g',useCount:5}])")
    ev("window.callHealthAI=async()=>({ok:true,text:'{\"combos\":[{\"items\":[\"Cheddar\"],\"note\":\"cheesy\"}]}'})"); ev("document.querySelectorAll('.chat-bubble').forEach(b=>b.remove())")
    ev("suggestMealFromLibrary('both')"); page.wait_for_timeout(600); txt = ev("[...document.querySelectorAll('.chat-bubble')].map(b=>b.textContent).join(' | ')")
    if 'Only suggesting what you can make' not in txt or 'Show everything' not in txt: f.add('BUG', '9: a result shows the footer with Show everything')
    if 'Gouda' in txt.split("Here's what fits")[-1]: pass
    # ---- stock rules (borrowed-from-AI defaults, user adjustable) ----
    ev("""saveLibrary([
      {id:'a1',name:'Salt',kcal:0,protein:0,carbs:0,fat:0,portion:'1g',useCount:5},
      {id:'a2',name:'Cream Of Tartar',kcal:258,protein:0,carbs:61,fat:0,portion:'1g',useCount:1},
      {id:'a3',name:'Olive Oil',kcal:900,protein:0,carbs:0,fat:100,useCount:5},
      {id:'a4',name:'Plain Flour',kcal:350,protein:10,carbs:73,fat:1,useCount:5},
      {id:'a5',name:'Dried Thyme',kcal:276,protein:9,carbs:64,fat:7,portion:'1g',useCount:1}
    ])""")
    ev("localStorage.setItem('mh_recipes', JSON.stringify([{id:'q1',name:'Salted loaf',servings:2,total:{kcal:360,protein:10,carbs:73,fat:1},ingredients:[{name:'Plain Flour',amount:100,unit:'g',kcal:350,protein:10,fat:1,carbs:73},{name:'Salt',amount:1,unit:'tsp',kcal:0,protein:0,fat:0,carbs:0},{name:'Cream Of Tartar',amount:2,unit:'g',kcal:5,protein:0,fat:0,carbs:1.2}]}]))")
    ev("localStorage.removeItem('mh_shopping_rules_v1'); mhSuggestSetMode('strict')")
    for n, b, pk in (('Olive Oil', 'g', 500), ('Plain Flour', 'g', 1000)): ev("([n,b,pk])=>mhStockTrack(n,{base:b,pack:pk,shop:'Asda'})", [n, b, pk])
    lvl('Olive Oil', 10); lvl('Plain Flour', 80)
    p, lib, rec = run()
    if 'Salt' not in lib or 'Cream of Tartar' not in lib or 'Dried Thyme' not in lib: f.add('BUG', f'10: never-run-out foods (salt, cream of tartar by name, thyme by category) are offered even in strict mode: {lib[:300]}')
    if 'Olive Oil' in lib: f.add('BUG', '10: oils and fats default to a 15 g go: 10 g cannot cover it, hidden')
    if 'Plain Flour' in lib: f.add('BUG', '10: anything else falls back to 100 g: 80 g cannot cover it, hidden')
    lvl('Olive Oil', 20); lvl('Plain Flour', 200); p, lib, rec = run()
    if 'Olive Oil' not in lib or 'Plain Flour' not in lib: f.add('BUG', '11: 20 g covers a 15 g go and 200 g covers 100 g')
    if 'Salted loaf' not in rec: f.add('BUG', f'11: salt (1 tsp) and cream of tartar never run out but are still ingredients: the loaf is offered: {rec[:200]}')
    # rules are editable
    ev("mhRulesPortionSet('fat','1 tsp')"); lvl('Olive Oil', 6); p, lib, rec = run()
    if 'Olive Oil' not in lib: f.add('BUG', '12: a teaspoon is 5 g: 6 g of oil covers it once the fat rule is 1 tsp')
    if ev("mhRulesLoad().portion.fat.n") != 5: f.add('BUG', '12: 1 tsp saved as 5 g')
    ev("mhRulesPortionSet('*','50 g')"); lvl('Plain Flour', 60); p, lib, rec = run()
    if 'Plain Flour' not in lib: f.add('BUG', '12: the fallback is editable: 60 g covers 50 g')
    ev("mhRulesPortionSet('fat','banana')")
    if ev("mhRulesLoad().portion.fat.n") != 5: f.add('BUG', '12: an invalid amount changes nothing')
    ev("mhRulesNeverDel('cream of tartar')"); p, lib, rec = run()
    if 'Cream of Tartar' in lib or 'Salted loaf' in rec: f.add('BUG', '13: take cream of tartar off the never-runs-out list and strict mode no longer offers it (it is not counted)')
    ev("mhRulesNeverCatToggle('herbs and spices')"); p, lib, rec = run()
    if 'Dried Thyme' in lib: f.add('BUG', '13: switching the herbs and spices category off makes uncounted thyme a normal uncounted food')
    # counted never-run-out food is checked like any other
    ev("mhRulesNeverAdd"); ev("document.getElementById('mhRulesNeverIn')&&0")
    ev("mhRulesReset()")
    if ev("JSON.stringify(mhRulesLoad())") != ev("JSON.stringify(mhRulesDefaults())"): f.add('BUG', '14: reset returns the suggested defaults')
    ev("mhStockTrack('Salt',{base:'g',pack:500,shop:'Asda'})"); lvl('Salt', 0); p, lib, rec = run()
    if 'Salt' in lib: f.add('BUG', '14: salt that you counted yourself and is at 0 is out like anything else')
    # UI
    ev("_shopUi.rulesOpen=false; mhShopOpen()"); page.wait_for_timeout(300)
    if page.locator('#mhRulesBox').count() != 1 or page.locator('[data-rule-row]').count() != 0: f.add('BUG', '15: Stock rules is a collapsed section in the Stock control card')
    page.locator('#mhRulesBox > div').first.click(); page.wait_for_timeout(300)
    if page.locator('[data-rule-row]').count() < 16: f.add('BUG', '15: opening it lists a portion row per category plus the fallback')
    page.fill('#mhRulesNeverIn', 'Bicarbonate Of Soda'); page.locator('#mhRulesNeverIn + button').click(); page.wait_for_timeout(300)
    if 'bicarbonate of soda' not in ev("mhRulesLoad().neverNames"): f.add('BUG', '15: the Add button puts the food on the never-runs-out list')
    if 'mh_shopping_rules_v1' not in ev("Object.keys(_collectBackupSettings().settings||_collectBackupSettings())"): f.add('BUG', '15: rules travel in backups')
    # ---- portions left, pace, batches ----
    ev("mhRulesReset()"); ev("mhStockTrack('Plain Flour',{base:'g',pack:1000,shop:'Asda'})"); lvl('Plain Flour', 600)
    txt = ev("k=>mhStockPortionText(mhStockLoad().items[k])", K('Plain Flour'))
    if txt != ' (≈ 6 × 100 g)': f.add('BUG', f'16: 600 g with no portion reads 6 x 100 g (fallback): {txt!r}')
    ev("mhStockTrack('Olive Oil',{base:'g',pack:500,shop:'Asda'})"); lvl('Olive Oil', 150)
    txt = ev("k=>mhStockPortionText(mhStockLoad().items[k])", K('Olive Oil'))
    if txt != ' (≈ 10 × 15 g)': f.add('BUG', f'16: oils use the 15 g category default: {txt!r}')
    ev("mhRulesPortionSet('fat','1 tbsp')"); ev("mhRulesPortionSet('fat','10 g')")
    if ev("k=>mhStockPortionText(mhStockLoad().items[k])", K('Olive Oil')) != ' (≈ 15 × 10 g)': f.add('BUG', '16: the user override wins over the suggestion')
    ev("mhStockTrack('Plain Flour',{base:'g',pack:1000,serving:25,shop:'Asda'})")
    if ev("k=>mhStockPortionText(mhStockLoad().items[k])", K('Plain Flour')) != '': f.add('BUG', '16: an item with its own serving shows servings via mhStockFmt, not the default')
    # pace: 4 logs on 4 different days, 100 g each, 400 g left
    ev("""()=>{const o=mhStockLoad(),k=mhShopKey('Plain Flour'),it=o.items[k];it.level=400;it.since=Date.now()-6*864e5;o.ledger=[];[5,4,3,1].forEach(d=>o.ledger.push({k,d:-100,t:Date.now()-d*864e5,s:'log',e:'x'+d}));localStorage.setItem(MH_STOCK_KEY,JSON.stringify(o));}""")
    txt = ev("k=>mhStockPaceText(mhStockLoad().items[k])", K('Plain Flour'))
    if 'about 6 days' not in txt: f.add('BUG', f'17: 400 g left, 400 g used over 6 days -> about 6 days: {txt!r}')
    ev("""()=>{const o=mhStockLoad(),k=mhShopKey('Plain Flour');o.ledger=o.ledger.slice(0,2);localStorage.setItem(MH_STOCK_KEY,JSON.stringify(o));}""")
    if ev("k=>mhStockPaceText(mhStockLoad().items[k])", K('Plain Flour')) != '': f.add('BUG', '17: fewer than 3 uses, no pace is claimed')
    # batches: 2 batches of 300 g with 650 g in stock
    ev("localStorage.setItem('mh_recipes', JSON.stringify([{id:'b1',name:'Flat bread',servings:4,total:{kcal:100,protein:1,carbs:1,fat:1},ingredients:[{name:'Plain Flour',amount:300,unit:'g',kcal:1,protein:1,fat:1,carbs:1}]}]))")
    lvl('Plain Flour', 650); n = ev("mhStockRecipeNote(loadRecipes()[0])")
    if 'covers 2 batches' not in n: f.add('BUG', f'18: 650 g covers 2 batches of 300 g: {n}')
    lvl('Plain Flour', 100); n = ev("mhStockRecipeNote(loadRecipes()[0])")
    if 'data-stock-swap' not in n or "reviewRecipeBeforeLogging('b1',1)" not in n: f.add('BUG', f'18: a short ingredient links to the existing review-and-swap screen: {n}')
    lvl('Plain Flour', 300); n = ev("mhStockRecipeNote(loadRecipes()[0])")
    if 'covers a batch' not in n: f.add('BUG', f'18: 300 g covers a batch: {n}')
    # ---- swaps you have made before ----
    ev("""saveLibrary([
      {id:'s1',name:'Rump Steak',kcal:150,protein:22,carbs:0,fat:7,portion:'100g',useCount:5},
      {id:'s2',name:'Lemon Jam',kcal:250,protein:0,carbs:62,fat:0,portion:'100g',useCount:1},
      {id:'s3',name:'Cheddar',kcal:410,protein:25,carbs:0.1,fat:34,portion:'100g',useCount:5},
      {id:'s4',name:'Gouda',kcal:356,protein:25,carbs:2,fat:27,portion:'100g',useCount:5}
    ])""")
    ev("localStorage.setItem('mh_recipes', JSON.stringify([{id:'w1',name:'Steak supper',servings:1,total:{kcal:150,protein:22,carbs:0,fat:7},ingredients:[{name:'Rump Steak',amount:100,unit:'g',kcal:150,protein:22,fat:7,carbs:0}]},{id:'w2',name:'Cheesy toastie',servings:1,total:{kcal:356,protein:25,carbs:2,fat:27},ingredients:[{name:'Gouda',amount:100,unit:'g',kcal:356,protein:25,fat:27,carbs:2}]}]))")
    ev("localStorage.removeItem('mh_shopping_swaps_v1'); mhSuggestSetMode('hide')")
    ev("mhStockTrack('Rump Steak',{base:'g',pack:500,shop:'Asda'})"); ev("mhStockTrack('Lemon Jam',{base:'g',pack:300,shop:'Asda'})"); ev("mhStockTrack('Cheddar',{base:'g',pack:400,shop:'Asda'})"); ev("mhStockTrack('Gouda',{base:'g',pack:300,shop:'Asda'})")
    lvl('Rump Steak', 0); lvl('Lemon Jam', 200); lvl('Cheddar', 300); lvl('Gouda', 0)
    p, lib, rec = run()
    if 'Steak supper' in rec: f.add('BUG', '19: steak is out and lemon jam is not a known swap: not offered')
    if 'Cheesy toastie' not in rec or 'Gouda for Cheddar' not in rec: f.add('BUG', '19: gouda -> cheddar is a like-for-like swap')
    # the user swaps steak for lemon jam (their choice) through the real swap function
    ev("()=>{const ing={name:'Rump Steak',amount:100};_substituteRecipeIngredient(ing,()=>{});const f=loadLibrary().find(x=>x.name==='Lemon Jam');_libPickerTarget.onPick(f);}")
    mem = ev("mhSwapsBefore('Rump Steak')")
    if not mem or mem[0]['name'] != 'Lemon Jam': f.add('BUG', f'19: a swap made in the builder is remembered: {mem}')
    p, lib, rec = run()
    if 'Steak supper' not in rec or 'Rump Steak for Lemon Jam' not in rec or 'made this swap before' not in rec: f.add('BUG', f'19: a remembered swap is offered even though it fails the like-for-like and macro checks (their choice): {rec[:300]}')
    lvl('Lemon Jam', 0); p, lib, rec = run()
    if 'Steak supper' in rec: f.add('BUG', '19: a remembered swap still needs to be in the cupboard')
    lvl('Lemon Jam', 200)
    # picker trawl row
    ev("()=>_openSubstitutePicker('Rump Steak',()=>{})"); page.wait_for_timeout(300)
    trawl = ev("document.getElementById('mhSwapTrawl')?document.getElementById('mhSwapTrawl').textContent:''")
    if 'Lemon Jam' not in trawl or 'Your usual swaps' not in trawl: f.add('BUG', f'20: the picker shows swaps you have made before: {trawl!r}')
    ev("()=>_openSubstitutePicker('Gouda',()=>{})"); page.wait_for_timeout(300)
    trawl = ev("document.getElementById('mhSwapTrawl')?document.getElementById('mhSwapTrawl').textContent:''")
    if 'Cheddar' not in trawl or 'in stock' not in trawl or 'In your cupboards now' not in trawl: f.add('BUG', f'20: the picker shows like-for-likes you have counted: {trawl!r}')
    if page.locator('#mhSwapTrawl').count() != 1: f.add('BUG', '20: only one trawl row, never stacked')
    if 'mh_shopping_swaps_v1' not in ev("Object.keys(_collectBackupSettings().settings||_collectBackupSettings())"): f.add('BUG', '20: swap memory travels in backups')
    if errs: f.add('JS-exception', errs[0])
print('\n'.join(f'{a}: {b}' for a, b in f) or 'PASS')
sys.exit(1 if f else 0)
