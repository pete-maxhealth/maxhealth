"""Persona 158 (v3.10.1055): the shared starter food + recipe pool. Real-account apply adds foods and recipes once (idempotent), never touches
existing entries, keto leaves out high-carb foods and non-keto recipes, remove takes out only the starter items, every pool recipe ingredient
exists with full macros, no brand words, and every starter pack file is flagged foodPool."""
import sys, json, glob, os, re; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
packs = [p for p in glob.glob(root_dir + '/starter_packs/*.json') if not p.endswith(('index.json', 'food_pool.json'))]
if len(packs) != 27: f.add('BUG', f'expected 27 pack files, found {len(packs)}')
for p in packs:
    if not json.load(open(p)).get('foodPool'): f.add('BUG', f'{os.path.basename(p)} not flagged foodPool')
brands = re.compile(r'asda|tesco|heylo|lurpak|lidl|costco|coors|carling|bud light|tennent|marmite|farmfoods|centra|elmlea|optimum|warrior|quorn|müller|muller|alpro|innocent', re.I)
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    pool = ev("MH_FOOD_POOL")
    if len(pool['foods']) < 140 or len(pool['recipes']) < 50: f.add('BUG', f"pool too small: {len(pool['foods'])} foods, {len(pool['recipes'])} recipes")
    names = {x['n'] for x in pool['foods']}
    for x in pool['foods']:
        if brands.search(x['n']): f.add('BUG', f"brand word in food {x['n']}")
        if not all(isinstance(x[k], (int, float)) for k in 'gkpcf'): f.add('BUG', f"food {x['n']} missing macros")
    for r in pool['recipes']:
        if brands.search(r['n']): f.add('BUG', f"brand word in recipe {r['n']}")
        for n, g in r['i']:
            if n not in names: f.add('BUG', f"{r['n']}: ingredient {n} not in pool")
    lib0 = ev("mhPackLoadCurrent('library').length")
    ev("saveLibrary(mhPackLoadCurrent('library').concat([{name:'My own food',kcal:100,protein:5,carbs:5,fat:5,portion:'100g'}]))")
    a = ev("mhPoolApply('')"); b = ev("mhPoolApply('')")
    if a['foods'] < 140 or a['recipes'] < 40: f.add('BUG', f'first apply added too little: {a}')
    if b['foods'] or b['recipes']: f.add('BUG', f'second apply not idempotent: {b}')
    if not ev("mhPackLoadCurrent('library').some(x=>x.name.toLowerCase()==='my own food')"): f.add('BUG', 'existing entry lost')
    r = ev("mhPoolRemove()")
    if r['foods'] != a['foods']: f.add('BUG', f'remove took out {r["foods"]}, expected {a["foods"]}')
    if not ev("mhPackLoadCurrent('library').some(x=>x.name.toLowerCase()==='my own food')"): f.add('BUG', 'remove deleted a non-starter entry')
    k = ev("mhPoolApply('keto')")
    if ev("mhPackLoadCurrent('library').some(x=>/bread|oats|banana|^(white |brown )?rice(,|$)/i.test(x.name)&&x.source==='starter')"): f.add('BUG', 'keto pool contains high-carb staples')
    if ev("mhPackLoadCurrent('recipes').some(x=>/porridge|banana oat|burrito/i.test(x.name))"): f.add('BUG', 'keto pool contains non-keto recipes')
    if k['recipes'] < 20: f.add('BUG', f'keto recipes too few: {k}')
    ev("mhPoolRemove()")
    # pack preview offers the pool and applies it
    ev("mhPackPreview({mhpack:1,foodPool:true,title:'Test',sets:{symptoms:{label:'Symptom list',count:1,data:[{id:'s1',name:'Test symptom',active:true}]}}})"); page.wait_for_timeout(400)
    if not ev("!!document.getElementById('mhPackFoodPool')"): f.add('BUG', 'pack preview has no starter foods tick for a foodPool pack')
    ev("document.getElementById('mhPackFoodPool').checked=true; document.getElementById('mhPackGo').click()"); page.wait_for_timeout(600)
    if ev("mhPackLoadCurrent('library').filter(x=>x.source==='starter').length") < 100: f.add('BUG', 'pack preview tick did not add the pool')
    ev("document.getElementById('mhPackModal')?.remove()")
    ev("mhPoolRender()")
    if 'Remove starter' not in ev("(document.getElementById('mhPoolRow')||{innerText:''}).innerText||''") and ev("!!document.getElementById('mhPoolRow')"): f.add('BUG', 'settings row does not offer Remove when starter foods are present')
    ev("mhPoolRemove()")
    ev("mhPackPreview({mhpack:1,title:'Plain',sets:{symptoms:{label:'Symptom list',count:1,data:[{id:'s2',name:'Another',active:true}]}}})"); page.wait_for_timeout(300)
    if ev("!!document.getElementById('mhPackFoodPool')"): f.add('BUG', 'a pack without foodPool shows the tick')
    ev("document.getElementById('mhPackModal')?.remove()")
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
