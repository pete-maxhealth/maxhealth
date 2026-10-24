"""Persona 257: non-nutritional regulars (v3.10.1153). Pete: toilet roll is a weekly regular, hairspray monthly. A regular stays on the shopping list, unticked, after
Shopping complete (in the collapsed Non-nutritional block); the others go back on the shelf and leave the list. Food is unchanged. Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("""(()=>{['Zzqx Loo Roll','Zzqx Hairspray'].forEach(n=>{mhStockTrack(n,{base:'each'}); const o=mhStockLoad(); o.items[mhShopKey(n)].nonFood=true; mhStockSave(o);}); mhStockTrack('Zzqx Milk',{base:'ml'});})()""")
    ev("mhShopOpen()"); ev("_shopUi.view='list'; mhStockLowNow(mhShopKey('Zzqx Loo Roll')); _shopUi.edit=true; mhShopRender()"); page.wait_for_timeout(300)
    ev("document.querySelectorAll('.mh-aisle span[onclick^=\"mhShopFold\"]').forEach(e=>e.click())"); page.wait_for_timeout(300)
    page.click('[data-item="Zzqx Loo Roll"] [title^="Regular"]'); page.wait_for_timeout(300)
    s = ev("mhShopLoad()")
    if not any(i['name'] == 'Zzqx Loo Roll' for i in s['items']) or 'Zzqx Loo Roll' not in s['usuals']: f.add('BUG', f'1: marking a regular puts it on the list: {s["items"]} {s["usuals"]}')
    ev("(()=>{const s=mhShopLoad(); mhShopSetAdd(s,'Zzqx Hairspray','own','',null,{nonFood:true}); mhShopSetAdd(s,'Zzqx Milk','own','',null); s.usuals.push('Zzqx Milk'); s.items.forEach(i=>i.checked=true); mhShopSave(s);})()")
    ev("mhShopComplete()"); page.click("#appModalConfirm"); page.wait_for_timeout(400)
    left = ev("mhShopLoad().items.map(i=>[i.name,i.checked])")
    if left != [['Zzqx Loo Roll', False]]: f.add('BUG', f'3: only the regular stays, unticked: {left}')
    if 'Zzqx Hairspray' not in ev("Object.values(mhStockLoad().items).filter(i=>i.nonFood).map(i=>i.name)"): f.add('BUG', '4: the other non-nutritional item is on the shelf')
    if 'Zzqx Loo Roll' not in ev("Object.values(mhStockLoad().items).filter(i=>i.nonFood).map(i=>i.name)"): f.add('BUG', '5: the regular is on the shelf too')
    if 'stay on your list' not in ev("document.getElementById('mhShopMsg')?.innerText||''"): f.add('BUG', '6: it says so')
    # a second shop: still there, unticked
    ev("(()=>{const s=mhShopLoad(); s.items.forEach(i=>i.checked=true); mhShopSave(s);})()"); ev("mhShopComplete()"); page.click("#appModalConfirm"); page.wait_for_timeout(300)
    if ev("mhShopLoad().items.length") != 1: f.add('BUG', '7: a regular stays shop after shop')
    # remove it from the list: it is gone; switch off regular: it leaves after the next shop
    ev("(()=>{const s=mhShopLoad(); s.items=[]; mhShopSave(s);})()")
    if 'Zzqx Loo Roll' not in ev("mhShopLoad().usuals"): f.add('BUG', '7b: removing it from the list leaves it a regular')
    ev("mhNfRegular(mhShopKey('Zzqx Loo Roll'))"); page.wait_for_timeout(200)
    if 'Zzqx Loo Roll' in ev("mhShopLoad().usuals"): f.add('BUG', '8: toggling again switches regular off')
    ev("(()=>{const s=mhShopLoad(); mhShopSetAdd(s,'Zzqx Loo Roll','own','',null,{nonFood:true}); s.items.forEach(i=>i.checked=true); mhShopSave(s);})()"); ev("mhShopComplete()"); page.click("#appModalConfirm"); page.wait_for_timeout(300)
    if ev("mhShopLoad().items.length") != 0: f.add('BUG', '9: not a regular any more: it leaves the list')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
