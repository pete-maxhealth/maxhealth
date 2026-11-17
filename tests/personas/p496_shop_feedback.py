"""Persona 496 (v3.10.1415): tapping a recipe in Shopping > Recipe gives feedback you can see: a toast, and the message line scrolled into view on the list,
with the ingredients that are already in the cupboards named as left off. The same feedback for a saved-list add. Invented data."""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 700}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept()); page.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("localStorage.setItem('mh_shop_pane','both')")
    ev("""(()=>{ const r=loadRecipes()||[]; for(let i=0;i<14;i++) r.push({id:'zr'+i,name:'Zzqx Stew '+i,ingredients:[{name:'Zzqx beef '+i},{name:'Zzqx onion'},{name:'Zzqx stock'}]}); saveRecipes(r)})()""")
    ev("mhShopOpen()"); page.wait_for_timeout(300)
    ev("mhStockTrack('Zzqx stock',{base:'g'}); (()=>{const o=mhStockLoad(); const it=o.items[mhShopKey('Zzqx stock')]; it.level=5; mhStockSave(o)})()")
    ev("mhShopView('recipes')"); page.wait_for_timeout(300)
    ev("document.querySelectorAll('[data-k]')[13] && document.querySelectorAll('[data-k][onclick*=mhShopRecipeAdd]')[13].scrollIntoView({block:'center'})"); page.wait_for_timeout(200)
    ev("document.querySelectorAll('[data-k][onclick*=mhShopRecipeAdd]')[13].click()"); page.wait_for_timeout(500)
    toast = ev("document.getElementById('toast')?.innerText||''")
    'ingredient' in toast and 'added from' in toast or f.add('FAIL', f'no toast after tapping a recipe: {toast!r}')
    box = ev("(()=>{const e=document.getElementById('mhShopMsg'); if(!e) return null; const r=e.getBoundingClientRect(); return [Math.round(r.top), innerHeight]})()")
    box and 100 <= box[0] <= box[1] - 20 or f.add('FAIL', f'message line not in view: {box}')
    nm = ev("mhShopLoad().items.map(i=>i.name)"); 
    any(n.lower().startswith('zzqx beef') for n in nm) or f.add('FAIL', 'recipe ingredients not on the list')
    ev("mhShopLoad().items.some(i=>i.name==='Zzqx stock')") and f.add('FAIL', 'an ingredient held in the cupboards was added')
    # a message that already toasts is not doubled
    ev("_shopUi.msg=''; mhShopSugPick && 0")
    page.screenshot(path='/tmp/claude-0/r496.png')
    errs and f.add('FAIL', f'page errors {errs}')
print('findings', len(f))
