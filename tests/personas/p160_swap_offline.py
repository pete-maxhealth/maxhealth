"""Persona 160: swapping a recipe ingredient offline. When the old ingredient's name matches nothing, the picker must still
list the whole library to browse (no dead end), say online search needs internet, and picking one must swap it in."""
import sys, re; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    br = pw.chromium.launch()
    for pid in ['alex', 'raj']:
        ctx = br.new_context(viewport={'width': 430, 'height': 900}, service_workers='block'); page = ctx.new_page(); page.on('pageerror', lambda e: f.add('JS-exception', str(e)[:160]))
        page.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
        page.goto('http://localhost:5757/'); page.wait_for_timeout(1200)
        page.evaluate("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
        page.evaluate(f"startDemoMode('{pid}')"); page.wait_for_timeout(2500)
        page.evaluate("window.dispatchEvent(new Event('offline'))")
        page.evaluate("Object.defineProperty(navigator,'onLine',{get:()=>false,configurable:true})")
        page.evaluate("""() => { _recipeIngredients = [{name:'Zzqx Unmatched Thing', amount:100, kcal:100, protein:5, fat:5, carbs:5, fibre:0, polyols:0, _base:{kcal:100,protein:5,carbs:5,fat:5,fibre:0,polyols:0,baseG:100}}];
          try { renderRecipeIngredients(); } catch (e) {} substituteBuilderIngredient(0); }""")
        page.wait_for_timeout(800)
        r = page.evaluate("""() => { const el = document.getElementById('recipeLibPickerList'); const rows = el ? el.querySelectorAll('[onclick*="_libPickerItemChosen"]').length : -1;
                                    return {rows, txt: el ? el.innerText.slice(0, 200) : '(no list)'}; }""")
        print(pid, r['rows'], 'rows;', r['txt'].replace('\n', ' | ')[:150])
        if r['rows'] < 40: f.add('FAIL', f'{pid}: picker shows only {r["rows"]} items when nothing matches the typed name')
        if 'needs internet' not in r['txt']: f.add('FAIL', f'{pid}: no honest offline message')
        if 'Search online instead' in r['txt']: f.add('FAIL', f'{pid}: still offering online search while offline')
        # the realistic case: swapping an ingredient that IS in the library (pre-filled name matches only itself)
        page.evaluate("document.getElementById('recipeLibPickerList') && closeRecipeLibPicker()")
        r2 = page.evaluate("""() => { const lib = loadLibrary(); const it = lib.find(l => /chicken breast/i.test(l.name)) || lib[0];
          _recipeIngredients = [Object.assign({}, _libItemToScalableIngredient(it, 100))]; substituteBuilderIngredient(0);
          const el = document.getElementById('recipeLibPickerList'); const rows = [...el.querySelectorAll('[onclick*="_libPickerItemChosen"]')].map(x => x.innerText.split('\\n')[0]);
          return {name: it.name, rows: rows.length, first: rows.slice(0, 4), head: /other options/i.test(el.innerText)}; }""")
        print(pid, 'in-library swap:', r2)
        if r2['rows'] < 40 or not r2['head']: f.add('FAIL', f'{pid}: swapping an in-library ingredient only offers {r2["rows"]} items')
        page.evaluate("closeRecipeLibPicker()")
        page.evaluate("substituteBuilderIngredient(0)"); page.wait_for_timeout(300)
        # pick the first listed item, ingredient must change
        page.evaluate("document.querySelector('#recipeLibPickerList [onclick*=\"_libPickerItemChosen\"]').click()"); page.wait_for_timeout(600)
        nm = page.evaluate("_recipeIngredients[0] && _recipeIngredients[0].name")
        if not nm or 'Zzqx' in nm: f.add('FAIL', f'{pid}: swap did not happen ({nm})')
        else: print(pid, 'swapped in:', nm)
        ctx.close()
    br.close()
print('findings', len(f))
sys.exit(1 if f else 0)
