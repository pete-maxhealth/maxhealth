"""Persona 321 (v3.10.1216): "2 x double cream" - a count on each list row. Typed "2 x name" works, the stepper changes it and shows it, two planned meals needing the same ingredient count it twice (and refreshing again does not add more), a saved list and its reuse keep the count, a list import carries it, and finishing a shop offers 2 packs as the bought amount."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay').style.display='none'")
    ev("switchTabById('shop'); mhShopOpen()"); page.wait_for_timeout(400)
    q = lambda n: ev("n=>{const i=mhShopLoad().items.find(x=>x.key===mhShopKey(n)); return i ? (i.qty||1) : 'missing'}", n)
    # typed
    ev("(()=>{ document.getElementById('mhShopOwn') ? 0 : mhShopAddOpen && mhShopAddOpen(); })()")
    ev("(()=>{ let e=document.getElementById('mhShopOwn'); if(!e){ const i=document.createElement('input'); i.id='mhShopOwn'; document.body.appendChild(i); e=i;} e.value='2 x Zz Double cream'; mhShopAddOwn(); })()"); page.wait_for_timeout(300)
    if q('Zz Double cream') != 2: f.add('BUG', f'typing "2 x name" gives 2: {q("Zz Double cream")}')
    if '2 × Zz Double cream' not in ev("document.body.innerText.replace(/\\s+/g,' ')") and '2 ×' not in ev("document.body.innerText"): f.add('BUG', 'the row shows 2 ×')
    # stepper in edit mode
    ev("_shopUi.edit = true; mhShopRender()"); page.wait_for_timeout(300)
    page.click('[data-item="Zz Double cream"] [title="One more"]'); page.wait_for_timeout(200)
    if q('Zz Double cream') != 3: f.add('BUG', f'+ makes it 3: {q("Zz Double cream")}')
    page.click('[data-item="Zz Double cream"] [title="One fewer"]'); page.click('[data-item="Zz Double cream"] [title="One fewer"]'); page.click('[data-item="Zz Double cream"] [title="One fewer"]'); page.wait_for_timeout(200)
    if q('Zz Double cream') != 1: f.add('BUG', 'it never goes below 1')
    if ev("!!document.querySelector('[data-item=\"Zz Double cream\"] [data-qty]')"): f.add('BUG', 'a count of 1 shows nothing extra')
    ev("_shopUi.edit = false")
    # two planned meals
    ev("""(()=>{ localStorage.setItem('mh_recipes', JSON.stringify([{id:'a',name:'Zz Soup',servings:2,ingredients:[{name:'Zz Leek',amount:100,kcal:1,protein:1,fat:1,carbs:1}]},{id:'b',name:'Zz Pie',servings:2,ingredients:[{name:'Zz Leek',amount:200,kcal:1,protein:1,fat:1,carbs:1}]}]));
      const d=new Date(); d.setDate(d.getDate()+1); const iso=d.toISOString().slice(0,10);
      localStorage.setItem('mh_planned_v1', JSON.stringify([{id:'p1',date:iso,time:'12:00',text:'Zz Soup',foods:[{name:'Zz Soup'}]},{id:'p2',date:iso,time:'19:00',text:'Zz Pie',foods:[{name:'Zz Pie'}]}])); })()""")
    ev("mhShopRefresh(true)"); ev("mhShopRefresh(true)"); ev("mhShopRefresh(true)")
    if q('Zz Leek') != 2: f.add('BUG', f'two planned meals needing leek count 2, and refreshing again changes nothing: {q("Zz Leek")}')
    # save + reuse
    ev("mhShopListSaveNamed('all','Zz weekly')")
    nl = ev("JSON.stringify((mhShopListsLoad().lists||[]).map(l=>l.items.map(i=>[i.name,i.qty])))")
    if '"Zz Leek",2' not in nl and '["Zz Leek",2]' not in nl: f.add('BUG', f'a saved list keeps the count: {nl}')
    # finishing a shop: a tracked food bought as 2 on the list is offered as 2 packs
    ev("(()=>{ localStorage.setItem('mh_stock_on','1'); })()")
    ev("mhStockOn = ()=>true; mhStockTrack('Zz Cream',{base:'ml',pack:300,shop:'Asda'}); mhStockSetLevel(mhShopKey('Zz Cream'),100)")
    ev("(()=>{const s=mhShopLoad(); mhShopSetAdd(s,'Zz Cream','own','',null,{qty:2}); const i=s.items.find(x=>x.key===mhShopKey('Zz Cream')); i.checked=true; mhShopSave(s); mhShopCompleteGo(false,false);})()"); page.wait_for_timeout(300)
    d = ev("mhBoughtDefault(mhStockLoad().items[mhShopKey('Zz Cream')])")
    if d != '600 ml': f.add('BUG', f'2 x a 300 ml pack is offered as 600 ml when finishing the shop: {d}')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
