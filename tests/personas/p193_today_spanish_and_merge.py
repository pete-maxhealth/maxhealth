"""Persona 193: Today screen in Spanish demo (Raj) leaves none of the known English strings behind, and every inbound set merges with the same de-duplicate rule (starter foods, packs, exports)."""
import sys, json, os, re; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
STILL_ENGLISH = ['KETOSIS ZONE', 'no carbs yet', 'Weight stable', 'kcal eaten', 'ROOM LEFT', 'PLAN AHEAD', 'Add exercise', 'Nothing logged yet', 'Eating window',
                 'check with your', 'Demo mode', 'Coming soon', 'Seizure activity', 'Sleep disruption', 'Alertness', 'moderately active', 'Vitamin D3', 'Melatonin']
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    def serve(route):
        p = os.path.join(ROOT, 'lang', route.request.url.split('/lang/')[1].split('?')[0])
        route.fulfill(status=200, content_type='application/json', body=open(p, 'rb').read()) if os.path.exists(p) else route.fulfill(status=404, body='')
    page.route('**/raw.githubusercontent.com/**/lang/*.json', serve)
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    ev = page.evaluate
    ev("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    # ---- merge rule first (English, real account) ----
    ev("""saveLibrary([{id:'x1',name:'Cheddar Cheese (Tesco)',kcal:400,protein:25,carbs:0,fat:33,portion:'100g',per100g:true,locked:true,source:'me'}]); saveRecipes([])""")
    ev("MH_FOOD_POOL.foods.push({n:'  cheddar  cheese (tesco) ',g:100,k:1,p:1,c:1,f:1})")
    r1 = ev("mhPoolApply('keto')"); r2 = ev("mhPoolApply('keto')")
    if r2['foods'] != 0 or r2['recipes'] != 0: f.add('BUG', f'second starter add duplicated things {r2}')
    lib = ev("loadLibrary()")
    ch = [x for x in lib if x['name'].lower().replace(' ', '').startswith('cheddarcheese(tesco)')]
    if len(ch) != 1 or ch[0]['kcal'] != 400 or not ch[0]['locked']: f.add('BUG', f'own cheddar entry duplicated or overwritten {ch}')
    # export: duplicates never leave
    ev("saveLibrary(loadLibrary().concat([{id:'dupe1',name:'cheddar cheese (tesco)',kcal:1,protein:1,carbs:1,fat:1,portion:'100g',per100g:true}]))")
    n = ev("mhPackBuild(['library']).sets.library.data.filter(x=>x.name.toLowerCase().indexOf('cheddar cheese (tesco)')>=0).length")
    if n != 1: f.add('BUG', f'pack export carries duplicates ({n})')
    ev("mhPackApply(mhPackBuild(['library']), ['library'], 'merge')")
    before = ev("loadLibrary().length"); ev("mhPackApply(mhPackBuild(['library']), ['library'], 'merge')")
    if ev("loadLibrary().length") != before: f.add('BUG', 'importing your own pack again changed the library size')
    # ---- Spanish Today ----
    ev("startDemoMode('raj')"); page.wait_for_timeout(1200)
    ev("mhLangSet('es')"); page.wait_for_timeout(4000)
    for sub in ['dash', 'supplements']:
        ev(f"switchSubTab('today','{sub}',document.getElementById('todaytab-{sub}'))"); page.wait_for_timeout(700)
        txt = ev("document.body.innerText")
        for s in STILL_ENGLISH:
            if re.search(r'(?<![A-Za-zÀ-ÿ])' + re.escape(s) + r'(?![A-Za-zÀ-ÿ])', txt, re.I): f.add('BUG', f'Spanish Today ({sub}) still shows English: {s!r}')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
