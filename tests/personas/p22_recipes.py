"""Persona 22: recipes. Build with the real builder, survive a browser wipe via the server copy, log a serving."""
import sys, re, json; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
BLOCK = re.compile(r'^https?://(?!localhost)')

def onboard(page):
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200)
    page.evaluate("onboardNext(2)"); page.fill('#onboardName', 'Rae'); page.evaluate("onboardNext(3)")
    page.evaluate("obSetSex('female')"); page.fill('#onboardAge', '40'); page.fill('#onboardHeight', '165')
    page.fill('#onboardWeight', '68'); page.fill('#onboardTarget', '64')
    page.evaluate("onboardNext(4)"); page.evaluate("obSetActivity('light')"); page.evaluate("obSetGoal('maintain')")
    page.evaluate("onboardNext(5)"); page.evaluate("obSetCondition('general')")
    page.evaluate("onboardNext(6)"); page.evaluate("onboardFinish()"); page.wait_for_timeout(1200)

ING = [('Lentils', 230, 18, 1, 40, 8, 0), ('Olive oil', 120, 0, 13.6, 0, 0, 0), ('Sweetener', 10, 0, 0, 4, 0, 3)]
STEPS = ['Rinse the lentils', 'Simmer | 20 minutes']
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    ctx.route(BLOCK, lambda r: r.abort())
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:150]))
    onboard(page)
    page.evaluate("openRecipeBuilder()"); page.wait_for_timeout(400)
    page.fill('#recipeName', 'lentil dhal'); page.fill('#recipeServings', '2')
    for n, k, p, fa, c, fi, po in ING:
        page.evaluate("recipeAddManual()")
        page.fill('#recipeIngName', n); page.fill('#recipeIngKcal', str(k)); page.fill('#recipeIngProt', str(p))
        page.fill('#recipeIngFat', str(fa)); page.fill('#recipeIngCarb', str(c)); page.fill('#recipeIngFibre', str(fi)); page.fill('#recipeIngPolyols', str(po))
        page.evaluate("addRecipeIngredient()")
    for s in STEPS:
        page.fill('#recipeStepInput', s); page.press('#recipeStepInput', 'Enter')
    tot = page.evaluate("(()=>{try{updateRecipeTotals()}catch(e){};return document.getElementById('recipeTotals')?document.getElementById('recipeTotals').innerText:''})()")
    page.evaluate("saveRecipe()"); page.wait_for_timeout(1500)
    rec = page.evaluate("loadRecipes()")
    if len(rec) != 1: f.add('BUG', f'expected 1 saved recipe, found {len(rec)}')
    else:
        r = rec[0]
        if r['name'] != 'Lentil Dhal': f.add('BUG', f'recipe name not normalised: {r["name"]!r}')
        if round(r['total']['kcal']) != 360: f.add('BUG', f'recipe total kcal {r["total"]["kcal"]} != 360')
        if len(r.get('steps', [])) != 2: f.add('BUG', f'steps not kept: {r.get("steps")}')
    # server copy
    import urllib.request
    csv_text = urllib.request.urlopen('http://localhost:5757/recipes').read().decode()
    if 'Lentil Dhal' not in csv_text: f.add('BUG', 'recipe never reached the server CSV')
    # wipe everything in the browser, reload: must come back from the server copy
    page.evaluate("['mh_recipes','mh_recipes_backup','mh_recipes_b2'].forEach(k=>localStorage.removeItem(k))")
    page.reload(); page.wait_for_timeout(3500)
    back = page.evaluate("loadRecipes()")
    if len(back) != 1: f.add('BUG', f'recipe not restored from the server after a wipe ({len(back)} found)')
    else:
        r = back[0]
        st = [s if isinstance(s, str) else (s.get('text') or s.get('step') or '') for s in r.get('steps', [])]
        if len(st) != 2 or '|' not in st[1]: f.add('BUG', f'restored recipe lost/changed its steps: {r.get("steps")}')
        ing = {i['name']: i for i in r['ingredients']}
        if not ing or round(sum(i.get('fibre', 0) for i in r['ingredients'])) != 8: f.add('BUG', 'restored recipe lost ingredient fibre')
        if not any(i.get('polyols') for i in r['ingredients']): f.add('BUG', 'restored recipe lost polyols')
        if round(r['total']['kcal']) != 360: f.add('BUG', f'restored total kcal {r["total"]["kcal"]}')
        # log one of two servings
        page.evaluate("id=>logRecipe(id,1)", r['id']); page.wait_for_timeout(1200)
        page.click("[onclick^=\"switchTab('today'\"]"); page.wait_for_timeout(800)
        kc = page.evaluate("(JSON.parse(localStorage.getItem('maxhealth_v1')||'{}').todayLog||[]).reduce((a,m)=>a+(m.kcal||0),0)")
        if round(kc) != 180: f.add('BUG', f'one of two servings should log 180 kcal, logged {kc}')
    if errs: f.add('JS-exception', str(errs[:2]))
    b.close()
print('findings', len(f)); sys.exit(1 if f else 0)
