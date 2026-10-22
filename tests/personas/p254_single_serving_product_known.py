"""Persona 254: a library food saved as "1 serving" with no ingredients inside is a food the shop and cupboard search can find (v3.10.1150). Pete's Heylo Flatbread was in
his library but the search said nothing matched: any "1 serving" entry was treated as a meal and only its (empty) ingredient list was offered. Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("""(()=>{const l=loadLibrary(); l.push({name:'Zzqx Flatbread',portion:'1 serving',kcal:150,protein:5,fat:3,carbs:25},
        {name:'Zzqx Pasta Bake',portion:'1 serving',isMeal:true,kcal:500,protein:20,fat:15,carbs:60,items:[{name:'Zzqx Pasta'},{name:'Zzqx Sauce'}]}); localStorage.setItem(LIBRARY_KEY, JSON.stringify(l));})()""")
    names = ev("mhShopKnown().map(x=>x.name)")
    if 'Zzqx Flatbread' not in names: f.add('BUG', f'1: a "1 serving" food with no ingredients is known: {names[-6:]}')
    if 'Zzqx Pasta Bake' in names: f.add('BUG', '2: a real meal is still not listed as a food itself')
    if not {'Zzqx Pasta', 'Zzqx Sauce'} <= set(names): f.add('BUG', '3: a meal still offers its ingredients')
    ev("localStorage.removeItem(MH_STOCK_KEY); mhStockTrack('Zzqx Seed',{base:'g'})"); ev("switchTabById('shop')"); page.wait_for_timeout(300)
    ev("(()=>{const st=mhSlState(); st.q='flatbread'; st.f='all'; mhShopView('stocklist');})()"); page.wait_for_timeout(300)
    if not page.locator('#mhSlRows').inner_text().count('Zzqx Flatbread'): f.add('BUG', '4: the cupboard search shows it')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
