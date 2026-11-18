"""Persona 500: Library A-Z works with Ingredients and Recipes (v3.10.1423). Pete: "you could have either ingredients or recipes, but selecting
atoz means they'd both vanish". A-Z is no longer a chip: the letter strip shows with All, Ingredients and Recipes, builds its letters from the
list in view, and a letter jumps in that list. An old saved A-Z view means All."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("""()=>{const l=loadLibrary();['Apple','Banana','Cheddar'].forEach(n=>l.push({name:n,cal:50,p:1,c:10,f:0,fibre:1,unit:'g',per:100}));saveLibrary(l);
      saveRecipes([{id:'r1',name:'Zucchini bake',ingredients:[],steps:[]},{id:'r2',name:'Yoghurt pot',ingredients:[],steps:[]}]);}""")
    ev("switchTab('log'); switchSubTab('log','library')"); page.wait_for_timeout(700)
    chips = ev("[...document.querySelectorAll('#mhTopicBar-library .mh-grp-chip')].map(e=>e.textContent.trim())")
    if any('A' in c and 'Z' in c for c in chips) or len(chips) != 4 or any('Food Library' in c for c in chips): f.add('BUG', f'no A-Z chip: {chips}')
    vis = lambda id: ev("id=>{const e=document.getElementById(id);return !!e&&!e.classList.contains('mh-grp-hide')}", id)
    letters = lambda: ev("[...document.querySelectorAll('#libraryAlphaNav button')].map(b=>b.textContent.trim()).join('')")
    for t in ('all', 'ingredients', 'recipes'):
        ev("t=>mhLibTopicSet(t)", t); page.wait_for_timeout(250)
        if not vis('dashSection-libAZ'): f.add('BUG', f'the letter strip shows with {t}')
    if letters() != 'YZ': f.add('BUG', f'with Recipes the letters are the recipes: {letters()!r}')
    if not vis('dashSection-libRecipes') or vis('dashSection-libIngredients'): f.add('BUG', 'Recipes view shows recipes only')
    ev("mhLibTopicSet('ingredients')"); page.wait_for_timeout(250)
    if 'A' not in letters() or 'Z' in letters(): f.add('BUG', f'with Ingredients the letters are the ingredients: {letters()!r}')
    if not vis('dashSection-libIngredients') or vis('dashSection-libRecipes'): f.add('BUG', 'Ingredients view shows ingredients only')
    ev("mhLibTopicSet('tools')"); page.wait_for_timeout(250)
    if vis('dashSection-libAZ'): f.add('BUG', 'the strip is hidden with Tools')
    ev("mhLibTopicSet('recipes')"); page.wait_for_timeout(250); ev("jumpToLibraryLetter('Z')"); page.wait_for_timeout(900)
    if not ev("(()=>{const r=document.querySelector('#recipeList [id^=recipe-row-]');return !!r})()"): f.add('BUG', 'recipe rows exist')
    if ev("localStorage.setItem('mh_topic_library','az'); mhLibTopicGet()") != 'all': f.add('BUG', 'a saved A-Z view means All')
    page.screenshot(path='/tmp/p500.png')
    if errs: f.add('BUG', f'page errors {errs[:3]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
