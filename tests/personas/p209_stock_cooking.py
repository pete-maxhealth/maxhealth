"""Persona 209: cooking a batch (v3.10.1119). Pete cooks a 4-serving bolognese using 800 g mince, 200 ml cream. Covers: the recipe card
saying stock is short / covers a batch; "Cooked a batch" taking the whole recipe off (grams only; ml/count left alone and said so);
logging servings of that recipe afterwards taking nothing more; logging more servings than were cooked taking only the extra share;
deleting the entry giving the cooked credit back; a recipe never cooked taking stock when logged; and the suggested-recipe doorway."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()"); ev("mhShopOpen()")
    ev("""localStorage.setItem('mh_recipes', JSON.stringify([{id:'r1',name:'Bolognese bake',servings:4,ingredients:[
      {name:'Beef mince',amount:800,kcal:1600,protein:160,fat:100,carbs:0},{name:'Double Cream (Asda)',amount:200,kcal:800,protein:4,fat:80,carbs:6},{name:'Onion',amount:100,kcal:40,protein:1,fat:0,carbs:9}]}]))""")
    ev("mhStockTrack('Beef mince',{base:'g',pack:1000,shop:'Asda'})"); ev("mhStockTrack('Double Cream (Asda)',{base:'ml',pack:300,shop:'Asda'})")
    mk, ck = ev("n=>mhShopKey(n)", 'Beef mince'), ev("n=>mhShopKey(n)", 'Double Cream (Asda)')
    lv = lambda k: ev("k=>mhStockLoad().items[k].level", k)
    cooked = lambda: ev("mhStockLoad().cooked && mhStockLoad().cooked.r1 || 0")
    ev("([a,b])=>{mhStockSetLevel(a,500);mhStockSetLevel(b,300);}", [mk, ck])
    note = ev("mhStockRecipeNote(loadRecipes()[0])")
    if 'short of Beef mince' not in note: f.add('BUG', f'500 g of mince cannot cover 800 g, the card must say so: {note}')
    ev("([a])=>mhStockSetLevel(a,1000)", [mk]); note = ev("mhStockRecipeNote(loadRecipes()[0])")
    if 'covers a batch' not in note: f.add('BUG', f'1000 g covers 800 g: {note}')
    # card has the button
    html = ev("(()=>{renderRecipeList();return document.getElementById('recipeList').innerHTML})()")
    if 'Cooked a batch' not in html: f.add('BUG', 'recipe card needs the Cooked a batch button')
    # cook the batch
    ev("()=>mhStockCooked('r1',4)")
    if lv(mk) != 200: f.add('BUG', f'cooking 4 of 4 servings should take 800 g: {lv(mk)}')
    if lv(ck) != 300: f.add('BUG', 'cream is counted in ml and the recipe is in grams: left alone, never guessed')
    if cooked() != 4: f.add('BUG', f'4 cooked servings should be waiting: {cooked()}')
    # eat 1 serving: nothing more comes off
    ev("()=>logRecipe('r1',1)"); page.wait_for_timeout(200)
    if lv(mk) != 200: f.add('BUG', f'eating from a cooked batch must not take the mince twice: {lv(mk)}')
    if cooked() != 3: f.add('BUG', f'one cooked serving used, 3 left: {cooked()}')
    # deleting that entry gives the credit back
    ev("()=>_doDeleteLogEntry(state.todayLog[state.todayLog.length-1].id)")
    if cooked() != 4 or lv(mk) != 200: f.add('BUG', f'deleting the entry must give the cooked serving back: {cooked()} {lv(mk)}')
    # log 6 servings when only 4 cooked: the extra 2 of 6 come off (1200 g x 1/3 = 400 g)
    ev("([a])=>mhStockSetLevel(a,1000)", [mk]); ev("()=>logRecipe('r1',6)"); page.wait_for_timeout(200)
    if lv(mk) != 600: f.add('BUG', f'6 servings with 4 cooked: only the 2 extra (400 g) comes off: {lv(mk)}')
    if cooked() != 0: f.add('BUG', 'all cooked credit should be used')
    # never cooked: logging takes stock
    ev("()=>{state.todayLog=[];}"); ev("([a])=>mhStockSetLevel(a,1000)", [mk]); ev("()=>logRecipe('r1',1)"); page.wait_for_timeout(700); page.locator('#appModalCancel').last.click(); page.wait_for_timeout(300)   # v3.10.1225: asks how many were cooked; Cancel = only what was eaten
    if lv(mk) != 800: f.add('BUG', f'a recipe never cooked takes its share when logged (Cancel on the cooked question): {lv(mk)}')
    page.evaluate("document.querySelectorAll('.app-modal-overlay').forEach(e=>e.remove())")   # the cream-in-ml question this recipe also raises
    # suggested-recipe doorway
    ev("([a])=>mhStockSetLevel(a,1000)", [mk]); ev("()=>{window._pendingLibraryCombos=[{type:'recipe',recipe:loadRecipes()[0],servings:2}];logSuggestedCombo(0)}"); page.wait_for_timeout(700); page.locator('#appModalCancel').last.click(); page.wait_for_timeout(300)
    page.evaluate("document.querySelectorAll('.app-modal-overlay').forEach(e=>e.remove())")
    if lv(mk) != 600: f.add('BUG', f'the suggested-recipe doorway must take stock too: {lv(mk)}')
    if errs: f.add('BUG', f'page errors {errs[:3]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
