"""Persona 292: the list says why items are on it, a whole reason can be taken off (cupboards untouched, basket untouched) and put back (v3.10.1190). Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("""(()=>{const s=mhShopLoad();
      for(let i=0;i<3;i++)mhShopSetAdd(s,'Zzqx Low '+i,'stock','running low',null);
      for(let i=0;i<2;i++)mhShopSetAdd(s,'Zzqx Hand '+i,'stock','added by hand',null);
      mhShopSetAdd(s,'Zzqx Typed','own','',null);
      mhShopSetAdd(s,'Zzqx Ticked','stock','running low',null); s.items[s.items.length-1].checked=true;
      mhShopSave(s); for(let i=0;i<3;i++){const n='Zzqx Low '+i; mhStockTrack(n,{base:'g'}); const k=mhShopKey(n); mhStockSetReorder(k,50); mhStockSetLevel(k,0);} const t=mhShopKey('Zzqx Ticked'); mhStockTrack('Zzqx Ticked',{base:'g'}); mhStockSetReorder(t,50); mhStockSetLevel(t,0);})()""")
    # a food that really is low, sitting in the 'added by hand' group
    ev("mhStockTrack('Zzqx Needs',{base:'g'}); mhStockSetLevel(mhShopKey('Zzqx Needs'),0); mhStockSetReorder(mhShopKey('Zzqx Needs'),100); mhStockSweep()")
    ev("const s=mhShopLoad(); const e=s.items.find(i=>i.key===mhShopKey('Zzqx Needs')); e.from='added by hand'; mhShopSave(s)")
    ev("switchTabById('shop')"); page.wait_for_timeout(500)
    ev("mhShopWhyToggle()"); page.wait_for_timeout(300)
    txt = lambda: ev("document.getElementById('mhShopWhy').innerText")
    t = txt()
    for want in ['Running low in my cupboards (3)', 'Added from Add foods or My cupboards (3)', 'Typed in by hand (1)']:
        if want not in t: f.add('BUG', f'the reasons list shows "{want}": {t!r}')
    page.click('[data-why="Added from Add foods or My cupboards"]'); page.wait_for_timeout(300); page.click('#appModalConfirm'); page.wait_for_timeout(500)
    if ev("mhShopLoad().items.filter(i=>/Zzqx Hand/.test(i.name)).length") != 0: f.add('BUG', 'foods that are not low come off')
    nd = ev("mhShopLoad().items.filter(i=>i.key===mhShopKey('Zzqx Needs')).map(i=>i.from)")
    if nd != ['running low']: f.add('BUG', f'a food that really is low stays on the list as running low: {nd}')
    ev("mhShopWhyUndo()"); page.wait_for_timeout(300); ev("_shopUi.whyOpen=true; mhShopRender()"); page.wait_for_timeout(300)
    page.click('[data-why="Running low in my cupboards"]'); page.wait_for_timeout(300); page.click('#appModalConfirm'); page.wait_for_timeout(500)
    n = ev("mhShopLoad().items.filter(i=>/Zzqx Low/.test(i.name)).length")
    if n != 3: f.add('BUG', f'taking off the running-low group keeps the foods that really are low: {n} left')
    if not ev("mhShopLoad().items.some(i=>i.name==='Zzqx Ticked')"): f.add('BUG', 'a ticked item in the basket stays')
    if ev("mhShopLoad().items.filter(i=>/Zzqx Hand/.test(i.name)).length") != 2: f.add('BUG', 'other reasons are left alone (undone above)')
    if not ev("!!mhStockLoad().items[mhShopKey('Zzqx Low 0')]"): f.add('BUG', 'the cupboards are untouched')
    ev("_shopUi.whyOpen=true; mhShopRender()"); page.wait_for_timeout(300)
    page.click('#mhShopWhy button:has-text("Put back")'); page.wait_for_timeout(400)
    if ev("mhShopLoad().items.filter(i=>/Zzqx Low/.test(i.name)).length") != 3: f.add('BUG', 'Put back restores them')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
