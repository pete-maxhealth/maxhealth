"""Persona 152 (v3.10.1047): the demo food library and recipes are generic (no brands, nothing personal), every recipe
ingredient has full macros and logs without NaN, a typed meal is matched to the demo library, and Alex is not low-carb."""
import sys; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    ev = page.evaluate
    ev("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev("startDemoMode('alex')"); page.wait_for_timeout(2500)
    lib = ev("generateDemoLibrary()"); rec = ev("generateDemoRecipes()")
    if len(lib) < 40: f.add('BUG', f'demo library too small: {len(lib)}')
    if len(rec) < 8: f.add('BUG', f'demo recipes too few: {len(rec)}')
    import re
    brands = re.compile(r'asda|tesco|heylo|lurpak|lidl|costco|coors|carling|bud light|tennent|sol\b|verdejo|marmite|farmfoods|centra|oakhahen|elmlea|strathroy|green & blacks|optimum|warrior', re.I)
    for x in lib: 
        if brands.search(x['name']): f.add('BUG', f"brand/personal item in demo library: {x['name']}")
        for k in ('kcal', 'protein', 'carbs', 'fat'):
            if not isinstance(x.get(k), (int, float)): f.add('BUG', f"library {x['name']} missing {k}")
    libnames = {x['name'] for x in lib}
    for r in rec:
        if brands.search(r['name']): f.add('BUG', f"brand in recipe {r['name']}")
        for i in r['ingredients']:
            if i['name'] not in libnames: f.add('BUG', f"{r['name']}: ingredient {i['name']} not in demo library")
            for k in ('kcal', 'protein', 'carbs', 'fat'):
                if not isinstance(i.get(k), (int, float)): f.add('BUG', f"{r['name']}/{i['name']} missing {k}")
        s = r['servings']; t = r['total']
        if not (200 <= t['kcal'] / s <= 1100): f.add('BUG', f"{r['name']}: odd kcal per serving {t['kcal']/s:.0f}")
    # log every recipe's 1 serving through the real UI and look for NaN
    ev("switchTab('log', document.getElementById('maintab-log'))"); page.wait_for_timeout(600)
    ev("switchSubTab('log','library',document.getElementById('logtab-library'))"); page.wait_for_timeout(1500)
    n = ev("[...document.querySelectorAll('button')].filter(e=>/Log 1 serving/i.test(e.textContent)&&e.offsetParent).length")
    if n < 8: f.add('BUG', f'only {n} visible Log 1 serving buttons')
    ev("switchSubTab('log','log',document.getElementById('logtab-log'))"); page.wait_for_timeout(400)
    txt0 = ev("document.getElementById('chatScroll').innerText")
    for i in range(8):
        ev("switchSubTab('log','library',document.getElementById('logtab-library'))"); page.wait_for_timeout(900)
        ev("(i)=>[...document.querySelectorAll('button')].filter(e=>/Log 1 serving/i.test(e.textContent)&&e.offsetParent)[i].click()", i); page.wait_for_timeout(1200)
        txt = ev("document.getElementById('chatScroll').innerText")
        if 'NaN' in txt or 'undefined' in txt: f.add('BUG', f'NaN/undefined after logging recipe #{i}'); break
    # typed meal
    ev("switchSubTab('log','log',document.getElementById('logtab-log'))"); page.wait_for_timeout(500)
    ev("(t)=>{const i=document.getElementById('chatInput'); i.value=t; i.dispatchEvent(new Event('input',{bubbles:true})); sendChat()}", '2 eggs and 2 slices of toast with butter'); page.wait_for_timeout(5000)
    txt = ev("document.getElementById('chatScroll').innerText")
    for w in ('Egg, boiled', 'Wholemeal bread', 'Butter'):
        if w not in txt: f.add('BUG', f'typed meal did not match {w}')
    if 'Sample grilled chicken' in txt: f.add('BUG', 'typed meal still got the canned chicken answer')
    if 'NaN' in txt: f.add('BUG', 'NaN in typed meal preview')
    a = ev("[localStorage.getItem('mh_target_carbs'), localStorage.getItem('mh_target_kcal')]")
    if a[0] != '320': f.add('BUG', f'Alex carb target {a[0]} not 320')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
