"""Persona 212: the worst shopping trip ever, end to end (v3.10.1119). This is also the demo script. Pete runs short of whey, eggs and
mince; the app notices by itself while he logs; he goes to the wrong shop first; forgets cream; cooks a batch; deletes a wrong entry;
restores from a backup. At every step the list, stock and prompts must say the right thing and nothing must be lost or counted twice.
Steps: 1 set up what he tracks  2 logging a shake and eggs makes them low and puts them on the Asda list (mince waits, its shop is not on
this trip)  3 wrong shop: Butchers added, mince appears, Asda things are still safe  4 Butchers complete, review, restock mince  5 Asda
trip, cream forgotten: it stays on the list  6 cook a batch and eat from it with no double counting  7 delete a wrong entry, stock comes back
8 a full backup and restore brings the lot back."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()"); ev("window.confirm=()=>true"); ev("mhShopOpen()")
    K = lambda n: ev("n=>mhShopKey(n)", n)
    lv = lambda n: ev("k=>mhStockLoad().items[k].level", K(n))
    onlist = lambda n: ev("k=>mhShopLoad().items.some(i=>i.key===k)", K(n))
    food = lambda n, a: {'name': n, 'amount': a, 'kcal': 100, 'protein': 10, 'fat': 5, 'carbs': 1}
    log = lambda foods, t='meal': (ev("([x,t])=>logFoods(x,t)", [foods, t]), page.wait_for_timeout(150))
    # 1 set up
    ev("mhStockTrack('Whey protein',{base:'g',pack:750,serving:25,shop:'Asda'})"); ev("mhStockTrack('Eggs',{base:'each',pack:6,shop:'Asda'})")
    ev("mhStockTrack('Double Cream (Asda)',{base:'ml',pack:300,shop:'Asda'})"); ev("mhStockTrack('Beef mince',{base:'g',pack:500,shop:'Butchers'})")
    ev("([w,e,c,m])=>{mhStockSetLevel(w,150);mhStockSetReorder(w,125);mhStockSetLevel(e,3);mhStockSetReorder(e,2);mhStockSetLevel(c,300);mhStockSetReorder(c,100);mhStockSetLevel(m,600);mhStockSetReorder(m,250);}",
       [K('Whey protein'), K('Eggs'), K('Double Cream (Asda)'), K('Beef mince')])
    if any(onlist(n) for n in ('Whey protein', 'Eggs', 'Double Cream (Asda)', 'Beef mince')): f.add('BUG', '1: nothing is low yet, nothing on the list')
    # 2 realise we are short, just by living
    log([food('Whey protein', '1 serving')]); log([food('Eggs', '2')])
    if lv('Whey protein') != 125 or lv('Eggs') != 1: f.add('BUG', f'2: logging should take stock: {lv("Whey protein")} {lv("Eggs")}')
    if not (onlist('Whey protein') and onlist('Eggs')): f.add('BUG', '2: whey and eggs are at their reorder level and must be on the list')
    if onlist('Double Cream (Asda)'): f.add('BUG', '2: cream is fine and must not be on the list')
    row = ev("k=>mhShopLoad().items.find(i=>i.key===k)", K('Eggs'))
    if row['shop'] != 'Asda' or row.get('from') != 'running low': f.add('BUG', f'2: eggs go under Asda tagged running low: {row.get("shop")} {row.get("from")}')
    log([food('Beef mince', '400g')])
    if lv('Beef mince') != 200 or onlist('Beef mince'): f.add('BUG', '2: mince is low but Butchers is not on this trip: it must wait, not be guessed onto Asda')
    # 3 wrong shop first
    ev("window.prompt=()=>'Butchers'"); ev("mhShopAddShop()")
    if not onlist('Beef mince'): f.add('BUG', '3: adding Butchers brings the waiting mince onto the list')
    if ev("k=>mhShopLoad().items.find(i=>i.key===k).shop", K('Beef mince')) != 'Butchers': f.add('BUG', '3: mince is under Butchers')
    ev("mhShopSetShop('Butchers')")
    if ev("mhShopLoad().shop") != 'Butchers' or not onlist('Whey protein'): f.add('BUG', '3: switching to Butchers must not lose the Asda things')
    # 4 Butchers: buy mince, complete, review
    ev("()=>{const s=mhShopLoad();s.items.filter(i=>i.shop==='Butchers').forEach(i=>i.checked=true);mhShopSave(s);}"); ev("mhShopComplete()"); page.wait_for_timeout(200)
    if ev("_shopUi.view") != 'stockbought': f.add('BUG', '4: completing with a tracked item opens the review')
    if page.locator(f'input[data-k="{K("Beef mince")}"]').input_value() != '500 g': f.add('BUG', '4: the usual pack is prefilled')
    page.click('#mhBoughtDone'); page.wait_for_timeout(200)
    if lv('Beef mince') != 700: f.add('BUG', f'4: 200 + 500 = 700: {lv("Beef mince")}')
    if not (onlist('Whey protein') and onlist('Eggs')): f.add('BUG', '4: the Asda things are still safe on the list after the Butchers trip')
    # 5 Asda, forgot the cream (cream is added by hand, not ticked)
    ev("mhShopSetShop('Asda')")
    ev("()=>{const s=mhShopLoad();mhShopSetAdd(s,'Double Cream (Asda)','own','',null);s.items.forEach(i=>{if(i.shop==='Asda'&&i.key!==mhShopKey('Double Cream (Asda)'))i.checked=true;});mhShopSave(s);}")
    ev("mhShopComplete()"); page.wait_for_timeout(200)
    if page.locator(f'input[data-k="{K("Double Cream (Asda)")}"]').count(): f.add('BUG', '5: the forgotten cream was not bought and must not be in the review')
    page.locator(f'input[data-k="{K("Whey protein")}"]').fill('1 pack'); page.click('#mhBoughtDone'); page.wait_for_timeout(200)
    if lv('Whey protein') != 875 or lv('Eggs') != 7: f.add('BUG', f'5: whey 125+750, eggs 1+6: {lv("Whey protein")} {lv("Eggs")}')
    if not onlist('Double Cream (Asda)'): f.add('BUG', '5: the forgotten cream stays on the list for next time')
    if onlist('Whey protein') or onlist('Eggs'): f.add('BUG', '5: bought things come off the list')
    if ev("k=>mhStockLoad().items[k].lowFlag", K('Eggs')): f.add('BUG', '5: restocking clears running low')
    # 6 cook a batch, eat from it
    ev("localStorage.setItem('mh_recipes', JSON.stringify([{id:'r1',name:'Bolognese bake',servings:4,ingredients:[{name:'Beef mince',amount:400,kcal:800,protein:80,fat:50,carbs:0},{name:'Eggs',amount:2,kcal:150,protein:12,fat:10,carbs:1}]}]))")
    ev("mhStockCooked('r1',4)")
    if lv('Beef mince') != 300: f.add('BUG', f'6: cooking the batch takes 400 g of mince: {lv("Beef mince")}')
    ev("logRecipe('r1',2)"); page.wait_for_timeout(200)
    if lv('Beef mince') != 300: f.add('BUG', '6: eating from the cooked batch takes nothing more')
    # 7 delete a wrong entry
    log([food('Whey protein', '2 portions')]); eid = ev("state.todayLog[state.todayLog.length-1].id")
    if lv('Whey protein') != 825: f.add('BUG', f'7: 2 portions = 50 g: {lv("Whey protein")}')
    ev("id=>_doDeleteLogEntry(id)", eid)
    if lv('Whey protein') != 875: f.add('BUG', '7: deleting the wrong entry puts the whey back')
    # 8 backup and restore keeps it all
    snap = ev("JSON.stringify(mhStockLoad().items)"); payload = ev("buildFullBackupPayload()")
    ev("localStorage.removeItem('mh_shopping_stock_v1')"); ev("p=>mhApplyBackupObject(p,'journey backup')", payload); page.wait_for_timeout(2500)
    if ev("JSON.stringify(mhStockLoad().items)") != snap: f.add('BUG', '8: a restore brings the stock back exactly')
    if not onlist('Double Cream (Asda)'): f.add('BUG', '8: the list survives the restore')
    if errs: f.add('BUG', f'page errors {errs[:3]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
