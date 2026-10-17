"""Persona 197: Shopping list. Top-N refresh from most used and most recent, meal-plan feed, picker from known ingredients, recipe ingredient include/exclude, 'always have' staples, tick/untick, select all/none, hide/show, reorder, category filter, by-aisle sort, Shop complete empties only the basket, persistence across reload, Today card show/hide/reorder and migration."""
import sys, json; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500); ev = page.evaluate
    old = ev("DEFAULT_DASHBOARD_ORDER.filter(k=>k!=='shopping').reverse()")
    ev("o=>localStorage.setItem('mh_dashboard_order', JSON.stringify(o))", old)
    ev("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    if 'shopping' not in ev("getDashboardOrder()"): f.add('BUG', 'shopping card not migrated into saved order')
    ev("localStorage.removeItem('mh_dashboard_order')")
    # library: ingredients with different use, one meal with three ingredients
    ev("""saveLibrary([
      {id:'a',name:'Chicken thighs',kcal:200,protein:30,carbs:0,fat:8,useCount:9,isMeal:false},
      {id:'b',name:'Broccoli',kcal:30,protein:3,carbs:4,fat:0,useCount:7,isMeal:false},
      {id:'c',name:'Eggs',kcal:150,protein:12,carbs:1,fat:10,useCount:5,isMeal:false},
      {id:'d',name:'Cheddar',kcal:400,protein:25,carbs:1,fat:33,useCount:3,isMeal:false},
      {id:'e',name:'Blueberries',kcal:50,protein:1,carbs:12,fat:0,useCount:1,isMeal:false},
      {id:'f',name:'Rare spice',kcal:5,protein:0,carbs:1,fat:0,useCount:0,isMeal:false},
      {id:'m',name:'Cheesy omelette',kcal:500,protein:35,carbs:3,fat:40,portion:'1 serving',isMeal:true,items:[{name:'Eggs',kcal:150},{name:'Cheddar',kcal:400},{name:'Olive oil',kcal:120}]}])""")
    ev("state.todayLog=[]; state.history=[]; updateDashboard()")
    if ev("document.getElementById('shopCount').textContent") != 'Empty': f.add('BUG', 'card not empty at start')
    ev("mhShopSetTopN(2)"); ev("mhShopRefresh()")
    names = ev("mhShopLoad().items.map(i=>i.name)")
    if len(names) != 2 or names[0] != 'Chicken Thighs': f.add('BUG', f'top-2 by use wrong: {names}')
    ev("mhShopRefresh()")
    if len(ev("mhShopLoad().items")) != 4: f.add('BUG', 'a second refresh should add the next 2 (refresh only adds)')
    ev("mhShopSetTopN(10)"); ev("mhShopRefresh()")
    if len(ev("mhShopLoad().items")) != len(set(ev("mhShopLoad().items.map(i=>i.key)"))): f.add('BUG', 'duplicate on list')
    if 'Rare Spice' in ev("mhShopLoad().items.map(i=>i.name)"): f.add('BUG', 'never-used item should not be suggested')
    # recent eating beats old use count
    ev("""(()=>{const d=new Date();d.setDate(d.getDate()-1);const iso=d.toISOString().slice(0,10);
      state.history=[{date:iso.slice(8,10)+'/'+iso.slice(5,7)+'/'+iso.slice(2,4),log:[{id:1,time:'12:00',name:'Blueberries',kcal:50},{id:2,time:'13:00',name:'Blueberries',kcal:50},{id:3,time:'14:00',name:'Blueberries',kcal:50}],totals:{kcal:150}}];
      localStorage.removeItem('mh_shopping_v1');})()""")
    ev("mhShopSetTopN(1)"); ev("mhShopRefresh()")
    if ev("mhShopLoad().items.map(i=>i.name)") != ['Blueberries']: f.add('BUG', 'most recent/most eaten should rank first')
    # open the modal and drive it
    ev("localStorage.removeItem('mh_shopping_v1'); mhShopSetTopN(10); mhShopRefresh(); mhShopOpen()")
    if not ev("!!document.getElementById('mhShopModal')"): f.add('BUG', 'modal did not open')
    # tick, select all/none
    id0 = ev("mhShopLoad().items[0].id"); ev("i=>mhShopToggle(i)", id0)
    if not ev("mhShopLoad().items[0].checked"): f.add('BUG', 'tick failed')
    ev("mhShopAll(true)")
    if not ev("mhShopLoad().items.every(i=>i.checked)"): f.add('BUG', 'select all failed')
    ev("mhShopAll(false)")
    if ev("mhShopLoad().items.some(i=>i.checked)"): f.add('BUG', 'select none failed')
    # hide and show hidden; refresh must not bring a hidden item back as a duplicate or unhide it
    n0 = ev("mhShopLoad().items.length"); ev("i=>mhShopHide(i)", id0)
    if ev("document.querySelectorAll('[data-item]').length") != n0 - 1: f.add('BUG', 'hide did not remove row from view')
    ev("mhShopRefresh()")
    if ev("mhShopLoad().items.length") != n0 or not ev("mhShopLoad().items[0].hidden"): f.add('BUG', 'refresh changed a hidden item')
    ev("mhShopShowHidden()")
    if ev("document.querySelectorAll('[data-item]').length") != n0: f.add('BUG', 'show hidden failed')
    ev("mhShopShowHidden(); mhShopHide(mhShopLoad().items[0].id)")
    # reorder
    first, second = ev("mhShopLoad().items.map(i=>i.id)")[:2]
    ev("i=>mhShopMove(i,'down')", first)
    if ev("mhShopLoad().items.map(i=>i.id)")[:2] != [second, first]: f.add('BUG', 'reorder down failed')
    # category filter: meat only
    ev("mhShopSetCat('meat')")
    shown = ev("[...document.querySelectorAll('[data-item]')].map(e=>e.dataset.item)")
    if shown != ['Chicken Thighs']: f.add('BUG', f'meat filter wrong: {shown}')
    ev("mhShopSetCat('meat')")
    ev("mhShopSortAisle()")
    cats = ev("mhShopLoad().items.map(i=>i.cat)")
    if cats.index('meat') != 0: f.add('BUG', f'aisle sort: meat not first {cats}')
    # picker: add something outside the top group, including a meal ingredient not in the library as an item
    ev("mhShopView('picker')")
    txt = ev("document.getElementById('mhShopModal').innerText")
    if 'Olive oil' not in txt or 'Rare Spice' not in txt: f.add('BUG', 'picker should list every known ingredient including meal ingredients')
    ev("mhShopPick('rare spice')"); ev("mhShopPick('olive oil')")
    names = ev("mhShopLoad().items.map(i=>i.name)")
    if 'Rare Spice' not in names or 'Olive oil' not in names: f.add('BUG', f'picker add failed {names}')
    # own item
    ev("mhShopView('list'); document.getElementById('mhShopOwn').value='Washing up liquid'; mhShopAddOwn()")
    if 'Washing up liquid' not in ev("mhShopLoad().items.map(i=>i.name)"): f.add('BUG', 'own item not added')
    # recipe include/exclude
    ev("localStorage.setItem('mh_shopping_v1','{}')")
    ev("mhShopView('recipe','cheesy omelette')")
    ev("mhShopRecipeToggle('cheesy omelette','olive oil')")
    ev("mhShopRecipeAdd('cheesy omelette')")
    names = sorted(ev("mhShopLoad().items.map(i=>i.name)"))
    if names != ['Cheddar', 'Eggs']: f.add('BUG', f'recipe exclusion wrong: {names}')
    ev("mhShopRecipeToggle('cheesy omelette','olive oil')")
    ev("mhShopRecipeAdd('cheesy omelette')")
    if 'Olive oil' not in ev("mhShopLoad().items.map(i=>i.name)"): f.add('BUG', 'including an ingredient again failed')
    # always have: removed from list and never suggested again
    eid = ev("mhShopLoad().items.find(i=>i.name==='Eggs').id"); ev("i=>mhShopHave(i)", eid)
    ev("mhShopRefresh()")
    if 'Eggs' in ev("mhShopLoad().items.map(i=>i.name)"): f.add('BUG', 'staple came back after refresh')
    # meal plan feed: planned meal brings included ingredients only
    ev("localStorage.setItem('mh_shopping_v1','{}')")
    ev("mhShopRecipeToggle('cheesy omelette','cheddar')")
    ev("localStorage.setItem('mh_planned_v1', JSON.stringify([{id:'p1',date:'2099-01-01',time:'12:00',text:'omelette',foods:[{name:'Cheesy omelette',kcal:500}]}]))")
    ev("mhShopSetTopN(1); mhShopRefresh()")
    src = ev("mhShopLoad().items.filter(i=>i.src==='plan').map(i=>i.name)")
    if sorted(src) != ['Eggs', 'Olive oil']: f.add('BUG', f'plan feed should honour the recipe exclusion (cheddar left out): {src}')
    ev("s=>{const x=mhShopLoad();x.pantry=['eggs'];x.items=[];localStorage.setItem('mh_shopping_v1',JSON.stringify(x))}", 0); ev('mhShopRefresh()')
    if 'Eggs' in ev("mhShopLoad().items.map(i=>i.name)"): f.add('BUG', 'plan feed should skip staples you always have')
    # shop complete: only ticked come off
    ev("localStorage.removeItem('mh_planned_v1'); localStorage.setItem('mh_shopping_v1','{}')")
    ev("mhShopSetTopN(10); mhShopRefresh()")
    all_n = ev("mhShopLoad().items.length"); ids = ev("mhShopLoad().items.map(i=>i.id)")
    ev("i=>mhShopToggle(i)", ids[0]); ev("i=>mhShopToggle(i)", ids[1])
    page.reload(); page.wait_for_timeout(1500)
    if len(ev("mhShopLoad().items")) != all_n or ev("mhShopLoad().items.filter(i=>i.checked).length") != 2: f.add('BUG', 'list or ticks lost across reload')
    if '2 of' not in ev("document.getElementById('shopCount').textContent"): f.add('BUG', 'card count wrong')
    ev("mhShopComplete()")
    if len(ev("mhShopLoad().items")) != all_n - 2: f.add('BUG', 'shop complete should remove only the ticked items')
    # name filter (v1096)
    ev("(()=>{const s=mhShopLoad(); s.items=[{id:'a1',key:'a1',name:'Double Cream (Asda)',cat:'Dairy',checked:false},{id:'a2',key:'a2',name:'Double Cream (Tesco)',cat:'Dairy',checked:false},{id:'a3',key:'a3',name:'Butter (Asda)',cat:'Dairy',checked:false},{id:'a4',key:'a4',name:'Eggs',cat:'Dairy',checked:false},{id:'a5',key:'a5',name:'Spinach',cat:'Veg',checked:false}]; mhShopSave(s); mhShopOpen();})()")
    ev("mhShopLQ('asda')")
    if ev("mhShopVisible(mhShopLoad()).length") != 2: f.add('BUG', 'name filter should show the 2 Asda items')
    if ev("document.activeElement && document.activeElement.id") != 'mhShopLQ': f.add('BUG', 'filter box lost focus while typing')
    ev("mhShopLQ('cream')")
    if ev("mhShopVisible(mhShopLoad()).length") != 2: f.add('BUG', 'filter by word failed')
    ev("mhShopLQ('')")
    if ev("mhShopVisible(mhShopLoad()).length") != 5: f.add('BUG', 'clearing the filter should show all')
    # card controls
    ev("toggleDashboardSectionHidden('shopping')")
    if ev("getComputedStyle(document.getElementById('dashSection-shopping')).display") != 'none': f.add('BUG', 'hide did not hide the card')
    ev("toggleDashboardSectionHidden('shopping')")
    before = ev("getDashboardOrder().indexOf('shopping')"); ev("moveDashboardSection('shopping','down')")
    if ev("getDashboardOrder().indexOf('shopping')") != before + 1: f.add('BUG', 'card reorder failed')
    # per-card fold and details (also Fibre, Water, Fasting): visible '▾ hide', body folds, details closed by default and open on the i
    for k in ['fibre', 'water', 'fasting', 'shopping']:
        if '▾ hide' not in ev("k=>document.getElementById(k+'BodyIcon').textContent", k): f.add('BUG', f'{k}: no visible hide control')
        ev("k=>mhCardBody(k)", k)
        if ev("k=>getComputedStyle(document.getElementById(k+'Body')).display", k) != 'none' or '▸ show' not in ev("k=>document.getElementById(k+'BodyIcon').textContent", k): f.add('BUG', f'{k}: fold failed')
        ev("k=>mhCardBody(k)", k)
        if ev("k=>getComputedStyle(document.getElementById(k+'Body')).display", k) == 'none': f.add('BUG', f'{k}: unfold failed')
    for k in ['fibre', 'fasting', 'shopping']:
        if ev("k=>getComputedStyle(document.getElementById(k+'Detail')).display", k) != 'none': f.add('BUG', f'{k}: details should start closed')
        ev("k=>mhCardInfo(k)", k)
        if ev("k=>getComputedStyle(document.getElementById(k+'Detail')).display", k) == 'none': f.add('BUG', f'{k}: details did not open')
        ev("k=>mhCardInfo(k)", k)
    page.reload(); page.wait_for_timeout(1200); ev("mhCardBody('water')"); page.reload(); page.wait_for_timeout(1200)
    if ev("getComputedStyle(document.getElementById('waterBody')).display") != 'none': f.add('BUG', 'fold not remembered across reload')
    ev("mhCardBody('water')")
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
