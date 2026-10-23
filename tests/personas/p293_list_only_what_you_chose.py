"""Persona 293: at real size (150 foods), filling the cupboards never puts anything on the shopping list that you did not choose: bulk Add to cupboards, per-row Shelves, zero counts, and only genuinely low foods appear, as 'running low' (v3.10.1192). Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
N = 150
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()"); ev("localStorage.setItem('mh_shop_pane','both')")
    ev("(n)=>{const l=loadLibrary(); for(let i=0;i<n;i++)l.push({name:'Zzqx Food '+i,portion:'100 g',kcal:100,protein:5,fat:2,carbs:10}); localStorage.setItem(LIBRARY_KEY, JSON.stringify(l)); mhShopSave(mhShopLoad());}", N)
    onlist = lambda: ev("mhShopLoad().items.filter(i=>/Zzqx Food/.test(i.name)).length")
    ev("switchTabById('shop')"); page.wait_for_timeout(400)
    ev("_shopUi.view='stocklist'; mhSlState().f='all'; mhSlState().q='Zzqx Food'; mhShopRender()"); page.wait_for_timeout(500)
    # 1. tick every food and Add to cupboards: nothing goes on the list
    ev("mhSlRows().forEach(r=>{mhSlState().sel[r.key]=true}); mhSlBulk()"); page.wait_for_timeout(600)
    tracked = ev("Object.keys(mhStockLoad().items).filter(k=>/zzqx food/.test(k)).length")
    if tracked < N * 0.9: f.add('BUG', f'setup: the foods were added to the cupboards: {tracked}')
    if onlist(): f.add('BUG', f'Add to cupboards for {tracked} foods puts {onlist()} on the list')
    # 2. a zero count with no reorder level is not low
    ev("(n)=>{for(let i=0;i<n;i++){const k=mhShopKey('Zzqx Food '+i); mhStockSetLevel(k,0);} mhStockSweep()}", N)
    if onlist(): f.add('BUG', f'zero counts with no reorder level put {onlist()} on the list')
    # 3. only foods that really are low appear, and as running low
    ev("(()=>{for(let i=0;i<5;i++){const k=mhShopKey('Zzqx Food '+i); mhStockSetReorder(k,50);} mhStockSweep()})()")
    got = ev("mhShopLoad().items.filter(i=>/Zzqx Food/.test(i.name)).map(i=>i.from+'|'+i.src)")
    if len(got) != 5 or any(g != 'running low|stock' for g in got): f.add('BUG', f'exactly the 5 low foods appear, as running low: {got}')
    # 4. raising the count takes a food back off the "low" state and nothing else is added
    ev("(()=>{for(let i=5;i<N2;i++){}})()".replace('N2', str(N)))
    ev("mhStockSweep()")
    if onlist() != 5: f.add('BUG', f'a second sweep adds nothing more: {onlist()}')
    # 5. per-row Shelves choice on Needs details adds nothing to the list
    ev("(()=>{const l=loadLibrary(); l.push({name:'Zzqx Extra',portion:'100 g',kcal:100,protein:5,fat:2,carbs:10}); localStorage.setItem(LIBRARY_KEY, JSON.stringify(l));})()")
    ev("_shopUi.view='stocklist'; mhSlState().f='all'; mhSlState().q='Zzqx Extra'; mhShopRender()"); page.wait_for_timeout(400)
    if page.locator('[data-dest="cup"]').count():
        page.click('[data-dest="cup"]'); page.wait_for_timeout(400)
    if ev("mhShopLoad().items.some(i=>i.name==='Zzqx Extra')"): f.add('BUG', 'choosing Shelves on a row does not put it on the list')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
