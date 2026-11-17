"""Persona 497 (v3.10.1416): the same food under two names is one food on the shopping list ("Asda Frozen Cauliflower" / "Cauliflower Frozen (Asda)").
Adding the second name does not make a second line; a recipe leaves off an ingredient you hold under the other name; different foods and different shops stay separate. Invented data."""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept()); page.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()"); ev("mhShopOpen()"); page.wait_for_timeout(300)
    add = lambda n, src='recipe': ev(f"(()=>{{const s=mhShopLoad(); const r=mhShopSetAdd(s,{n!r},{src!r},'',null); mhShopSave(s); return r}})()")
    names = lambda: ev("mhShopLoad().items.map(i=>i.name)")
    add('Zzqx Frozen Cauliflower') is True or f.add('FAIL', 'first add refused')
    add('Cauliflower Zzqx Frozen (Asda)') is False or f.add('FAIL', 'second name made a second line')
    add('Zzqx Frozen Cauliflowers') is False or f.add('FAIL', 'plural made a second line')
    add('Zzqx Frozen Cauliflower Rice') is True or f.add('FAIL', 'a different food was joined')
    len(names()) == 2 or f.add('FAIL', f'list should hold 2 lines: {names()}')
    add('Zzqx Frozen Cauliflower', 'own') is False or f.add('FAIL', 'the exact same name should still be one line')
    add('Cauliflower Zzqx Frozen (Asda)', 'own') is True or f.add('FAIL', 'something typed or picked by hand must always be added')
    ev("(()=>{const s=mhShopLoad(); s.items=s.items.filter(i=>i.name!=='Cauliflower Zzqx Frozen (Asda)'); mhShopSave(s)})()")
    # different shops in the names stay separate
    ev("(()=>{const s=mhShopLoad(); s.shops=['Asda','Tesco']; mhShopSave(s)})()")
    add('Asda Zzqx Beans', 'recipe') is True and add('Tesco Zzqx Beans', 'recipe') is True or f.add('FAIL', 'names for two different shops were joined')
    # recipe: a held food under the other name is left off
    ev("(()=>{const r=loadRecipes()||[]; r.push({id:'zr1',name:'Zzqx Pie',ingredients:[{name:'Zzqx Mince Frozen (Asda)'},{name:'Zzqx Leeks'}]}); saveRecipes(r)})()")
    ev("mhStockTrack('Asda Zzqx Frozen Mince',{base:'g'}); (()=>{const o=mhStockLoad(); const it=Object.values(o.items).find(x=>x.name==='Asda Zzqx Frozen Mince'); it.level=900; mhStockSave(o)})()")
    ev("mhShopRecipeAdd('zzqx pie')"); page.wait_for_timeout(400)
    n = names(); any('Leeks' in x for x in n) or f.add('FAIL', f'recipe did not add the missing ingredient: {n}')
    any('Mince' in x for x in n) and f.add('FAIL', f'held food added under its other name: {n}')
    errs and f.add('FAIL', f'page errors {errs}')
print('findings', len(f))
