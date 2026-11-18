"""Persona 501 (v3.10.1425): the Add Food form (Library "+ Add Food Manually", a category's "add new item", a flagged recipe ingredient) offers the same routes
as Log: search online, AI, barcode, label photo, with typing as the last resort. The form steps aside while the panel is open, comes back if cancelled, and a
saved result carries on as typing would (category tag, recipe ingredient). Invented data, no network."""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept()); page.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    modal = lambda: ev("document.getElementById('addFoodModal').classList.contains('open')")
    panel = lambda: ev("document.getElementById('foodSearchOverlay').classList.contains('open')")
    def saved(name):   # what the panel's Save does, with an invented per-100 g food
        ev("""n=>{_selectedFoodItem={name:n,brand:'',kcal:100,prot:5,carb:10,fat:2,fibre:1,polyols:0,satFat:0,sugars:0,salt:0,qty:''}; _lastFoodSourceType='search'; saveFoodToLibraryFromPanel();}""", name); page.wait_for_timeout(300)
    # 1 standalone
    ev("openAddFoodModal()"); page.wait_for_timeout(200)
    labs = ev("[...document.querySelectorAll('#addFoodRoutes button')].map(b=>b.textContent.trim())")
    for need in ('Search online', 'Try AI', 'Scan barcode', 'Read a label'):
        any(need in x for x in labs) or f.add('FAIL', f'Add Food: missing {need}: {labs}')
    gap = ev("(()=>{const a=document.getElementById('addFoodName').getBoundingClientRect(), r=document.getElementById('addFoodRoutes').getBoundingClientRect(); return Math.round(r.top-a.bottom)})()")
    gap < 40 or f.add('FAIL', f'routes are {gap}px below the name box')
    # a route needs a name first
    ev("mhAddFoodFind('search')"); page.wait_for_timeout(200); (modal() and not panel()) or f.add('FAIL', 'Search online with no name should ask for one, not open')
    ev("document.getElementById('addFoodName').value='Zzqx Oat bar'; mhAddFoodFind('search')"); page.wait_for_timeout(400)
    (panel() and not modal()) or f.add('FAIL', f'search route: panel {panel()} modal {modal()}')
    ev("closeFoodSearch()"); page.wait_for_timeout(700)
    (modal() and ev("document.getElementById('addFoodName').value") == 'Zzqx Oat bar') or f.add('FAIL', 'cancelling the panel must bring the form back with the name')
    ev("mhAddFoodFind('search')"); page.wait_for_timeout(400); saved('Zzqx Oat bar')
    (not modal() and ev("loadLibrary().some(x=>x.name.toLowerCase()==='zzqx oat bar')")) or f.add('FAIL', 'saved result should close the form and be in the library')
    # 2 category
    ev("openAddFoodModalForCategory('snacks')"); ev("document.getElementById('addFoodName').value='Zzqx Seed mix'; mhAddFoodFind('ai')"); page.wait_for_timeout(400); saved('Zzqx Seed mix')
    ev("loadLibrary().find(x=>x.name.toLowerCase()==='zzqx seed mix')?.categories?.includes('snacks')") or f.add('FAIL', 'category add: the new food should carry the category')
    # 3 recipe ingredient
    ev("_recipeIngredients=[{name:'⚠️ Zzqx Tahini — add nutrition',amount:30,kcal:0,protein:0,carbs:0,fat:0}]; openAddFoodModalForRecipeIngredient(0)"); page.wait_for_timeout(200)
    ev("mhAddFoodFind('search')"); page.wait_for_timeout(400); saved('Zzqx Tahini')
    ing = ev("_recipeIngredients[0]")
    (ing['name'].lower() == 'zzqx tahini' and ing['kcal'] == 30) or f.add('FAIL', f'recipe ingredient not filled from the saved food: {ing}')
    # typing still works as the last resort
    ev("openAddFoodModal()"); ev("addFoodName.value='Plinth Typed'; addFoodKcal.value=100; addFoodProt.value=5; addFoodCarbs.value=10; addFoodPortion.value='100g'; confirmAddFood()"); page.wait_for_timeout(300)
    ev("loadLibrary().some(x=>x.name.toLowerCase()==='plinth typed')") or f.add('FAIL', 'typing the values still has to work')
    if errs: f.add('FAIL', f'page errors {errs[:3]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
