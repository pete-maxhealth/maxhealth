"""Persona 332 (v3.10.1225): logging a recipe that makes more than one serving asks how many were cooked, so stock matches the pot.
Pete: "When a recipe is for 4, stock needs to be for 4". Covers: first log asks (default = recipe servings) and OK takes the whole batch off with
leftovers kept; the next serving asks nothing and takes nothing more; Cancel keeps the old behaviour (only what was eaten); cooking fewer than eaten
takes the extra share; a 1-serving recipe never asks; the suggested-recipe doorway and the custom-servings prompt ask too; deleting the entry gives the
leftover back; the prompt is the same dialog the Cooked a batch button uses."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()"); ev("mhShopOpen()")
    ev("""localStorage.setItem('mh_recipes', JSON.stringify([
      {id:'r1',name:'Bolognese bake',servings:4,ingredients:[{name:'Beef mince',amount:800,kcal:1600,protein:160,fat:100,carbs:0}]},
      {id:'r2',name:'Single omelette',servings:1,ingredients:[{name:'Beef mince',amount:100,kcal:200,protein:20,fat:10,carbs:0}]}]))""")
    ev("mhStockTrack('Beef mince',{base:'g',pack:1000,shop:'Asda'})")
    mk = ev("n=>mhShopKey(n)", 'Beef mince')
    lv = lambda: ev("k=>mhStockLoad().items[k].level", mk)
    cooked = lambda: ev("mhStockLoad().cooked && mhStockLoad().cooked.r1 || 0")
    reset = lambda: (ev("k=>{mhStockSetLevel(k,1000); const o=mhStockLoad(); o.cooked={}; o.cookedUse={}; mhStockSave(o); state.todayLog=[]}", mk))
    prompt = lambda: page.query_selector('#appPromptInput')
    def ask(label):
        page.wait_for_timeout(700); el = prompt()
        if not el: f.add('BUG', f'{label}: no "how many did you cook" prompt appeared'); return None
        return el
    def answer(el, v):
        el.fill(str(v)); page.click('#appModalConfirm'); page.wait_for_timeout(500)
    # 1 first log asks; default is what the recipe makes; OK takes the whole batch
    reset(); ev("()=>logRecipe('r1',1)"); el = ask('first log')
    if el:
        if el.input_value() != '4': f.add('BUG', f'default should be the recipe servings (4): {el.input_value()}')
        txt = page.inner_text('.app-modal')
        if 'did you cook' not in txt or 'Cancel takes off only what you ate' not in txt: f.add('BUG', f'prompt wording: {txt[:200]}')
        page.screenshot(path='/tmp/p332_prompt.png')
        answer(el, 4)
        if lv() != 200: f.add('BUG', f'cooking 4 of 4 takes 800 g: {lv()}')
        if cooked() != 3: f.add('BUG', f'4 cooked, 1 eaten: 3 left over: {cooked()}')
    # 2 the next serving asks nothing and takes nothing more
    ev("()=>logRecipe('r1',1)"); page.wait_for_timeout(700)
    if prompt(): f.add('BUG', 'a second serving from a cooked batch must not ask again'); page.click('#appModalCancel')
    if lv() != 200 or cooked() != 2: f.add('BUG', f'second serving takes nothing more, 2 left: {lv()} {cooked()}')
    # 3 deleting that entry gives the leftover back
    ev("()=>_doDeleteLogEntry(state.todayLog[state.todayLog.length-1].id)")
    if cooked() != 3: f.add('BUG', f'deleting the entry gives the serving back: {cooked()}')
    # 4 Cancel keeps the old behaviour: only what was eaten
    reset(); ev("()=>logRecipe('r1',1)"); el = ask('cancel case')
    if el: page.click('#appModalCancel'); page.wait_for_timeout(500)
    if lv() != 800 or cooked() != 0: f.add('BUG', f'Cancel takes only the eaten serving (200 g), no leftovers: {lv()} {cooked()}')
    # 5 cook 2, eat 1
    reset(); ev("()=>logRecipe('r1',1)"); el = ask('cook 2')
    if el: answer(el, 2)
    if lv() != 600 or cooked() != 1: f.add('BUG', f'cook 2 of 4, eat 1: 400 g off, 1 left: {lv()} {cooked()}')
    # 6 cooked fewer than eaten: the extra share comes off too
    reset(); ev("()=>logRecipe('r1',3)"); el = ask('cook 2 eat 3')
    if el: answer(el, 2)
    if lv() != 400 or cooked() != 0: f.add('BUG', f'cook 2, eat 3: 400 g + the extra 1/3 of 600 g = 600 g off: {lv()} {cooked()}')
    # 7 one-serving recipe never asks
    reset(); ev("()=>logRecipe('r2',1)"); page.wait_for_timeout(700)
    if prompt(): f.add('BUG', 'a 1-serving recipe must not ask'); page.click('#appModalCancel')
    if lv() != 900: f.add('BUG', f'1-serving recipe takes 100 g: {lv()}')
    # 8 suggested-recipe doorway asks too
    reset(); ev("()=>{window._pendingLibraryCombos=[{type:'recipe',recipe:loadRecipes()[0],servings:2}];logSuggestedCombo(0)}"); el = ask('suggested doorway')
    if el: answer(el, 4)
    if lv() != 200 or cooked() != 2: f.add('BUG', f'suggested doorway, cook 4 eat 2: {lv()} {cooked()}')
    # 9 custom-servings prompt asks too
    reset(); ev("()=>{promptRecipeServings('r1')}"); page.wait_for_timeout(500)
    el = prompt()
    if not el: f.add('BUG', 'custom servings prompt did not open')
    else:
        el.fill('1'); page.click('#appModalConfirm'); page.wait_for_timeout(500)
        ev("()=>logSuggestedCombo(window._pendingLibraryCombos.length-1)"); el = ask('custom servings review')
        if el: answer(el, 4)
        if lv() != 200 or cooked() != 3: f.add('BUG', f'custom-servings (review card) path: {lv()} {cooked()}')
    # 10 stock counting off: nothing asks
    reset(); ev("()=>{const o=mhStockLoad(); o.enabled=false; mhStockSave(o);}"); ev("()=>logRecipe('r1',1)"); page.wait_for_timeout(700)
    if prompt(): f.add('BUG', 'counting is off: must not ask'); page.click('#appModalCancel')
    if errs: f.add('BUG', f'page errors {errs[:3]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
