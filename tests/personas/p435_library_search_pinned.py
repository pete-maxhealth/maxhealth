"""Persona 435: the Library search and its All / Ingredients / Recipes filter are always open and pinned at the top of the Library (v3.10.1333).
Pete (9 Nov 2026): library search "sticky and non hideable ... it always needs to be open". They sat inside the hideable Food Library card, so hiding it took the search away.
Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
SHOT = '/tmp/claude-0/-home-claude/c032a46b-68f2-5aea-a854-98f1a5b7657c/scratchpad/p435_%s.png'
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); page = b.new_context(viewport={'width': 390, 'height': 800}, service_workers='block', device_scale_factor=2).new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("saveLibrary(Array.from({length:40},(_,i)=>({id:'l'+i,name:'Zzqx Food '+String(i).padStart(2,'0'),kcal:100+i,protein:5,carbs:3,fat:2,portion:'100g',useCount:i})))")
    ev("saveRecipes([{id:'r1',name:'Zzqx Stew',ingredients:[],servings:2}])")
    ev("switchTab('log', document.getElementById('maintab-log')); switchSubTab('log','library', document.getElementById('logtab-library'))"); page.wait_for_timeout(700)
    inside = ev("!!document.querySelector('#lib-food-wrap #librarySearch, #lib-food-wrap #libraryFilter')")
    if inside: f.add('BUG', '1: the search and filter are still inside the hideable Food Library card')
    if not ev("!!document.querySelector('#libraryScroll > #libraryControls #librarySearch') && !!document.querySelector('#libraryControls #libraryFilter')"): f.add('BUG', '2: search and filter are in the pinned box at the top of the Library')
    # 3 hiding the Food Library card does not take the search away
    ev("toggleSection('lib-food','lib-food-wrap','lib-food-icon')"); page.wait_for_timeout(300)
    vis = lambda: ev("(()=>{const e=document.getElementById('librarySearch'); const r=e.getBoundingClientRect(); return r.height>0 && getComputedStyle(e).visibility!=='hidden'})()")
    if not vis(): f.add('BUG', '3: search stays visible with Food Library hidden')
    ev("toggleSection('lib-food','lib-food-wrap','lib-food-icon')"); page.wait_for_timeout(300)
    # 4 pinned while scrolling a long list
    ev("document.getElementById('libraryScroll').scrollTo(0, 900)"); page.wait_for_timeout(400)
    r = ev("(()=>{const c=document.getElementById('libraryControls').getBoundingClientRect(), s=document.getElementById('libraryScroll').getBoundingClientRect(); return [Math.round(c.top-s.top), c.height>0, Math.round(document.getElementById('libraryScroll').scrollTop)]})()")
    if r[2] < 300: f.add('BUG', f'4a: the test did not scroll far enough: {r}')
    elif abs(r[0]) > 2: f.add('BUG', f'4b: the controls scrolled away instead of staying pinned ({r})')
    page.screenshot(path=SHOT % 'scrolled_light')
    # 5 it works from there: filter to recipes, type a search, clear
    ev("document.getElementById('libraryFilter').value='recipes'; renderLibrary()"); page.wait_for_timeout(300)
    if ev("getComputedStyle(document.getElementById('dashSection-libFood')).display") != 'none' or ev("getComputedStyle(document.getElementById('dashSection-libRecipes')).display") == 'none': f.add('BUG', '5a: Recipes only hides the foods and keeps the recipes')
    ev("document.getElementById('libraryFilter').value='all'; renderLibrary()")
    page.fill('#librarySearch', 'Food 07'); page.wait_for_timeout(500)
    txt = ev("document.getElementById('libraryIngredientsList').innerText")
    if 'Zzqx Food 07' not in txt or 'Zzqx Food 08' in txt: f.add('BUG', f'5b: typing in the pinned search filters the list: {txt[:80]!r}')
    page.fill('#librarySearch', ''); page.wait_for_timeout(300)
    # 6 dark theme look
    ev("document.documentElement.setAttribute('data-theme','dark')"); ev("document.getElementById('libraryScroll').scrollTo(0, 600)"); page.wait_for_timeout(300)
    page.screenshot(path=SHOT % 'scrolled_dark')
    # 7 reordering the sections leaves the controls on top
    ev("moveLibrarySection('food','up')"); page.wait_for_timeout(300)
    if not ev("!!(document.getElementById('libraryControls').compareDocumentPosition(document.getElementById('dashSection-libRecipes')) & Node.DOCUMENT_POSITION_FOLLOWING) && !!(document.getElementById('libraryControls').compareDocumentPosition(document.getElementById('dashSection-libFood')) & Node.DOCUMENT_POSITION_FOLLOWING)"): f.add('BUG', '7: after reordering, the controls are still above every section')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(x) for x in f]; sys.exit(1 if f else 0)
