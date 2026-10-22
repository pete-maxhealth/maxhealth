"""Persona 265: stock between devices and through a backup, in the middle of a shop (v3.10.1158). A phone with counts, a half-ticked list, regulars, a cooked batch and
a use-by date is sent to a tablet and back: every count, the cooked batch and the list must arrive exactly, nothing counted twice, and a backup taken mid-shop restores
the ticks. Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    lv = lambda n: ev("n=>{const i=mhStockLoad().items[mhShopKey(n)]; return i ? i.level : 'missing'}", n)
    ev("""(()=>{ [['Zz Rice','g',640,300],['Zz Milk','ml',1500,500],['Zz Eggs','each',8,4]].forEach(([n,b,l,r])=>{mhStockTrack(n,{base:b,pack:b==='each'?6:1000,shop:'Asda'}); mhStockSetLevel(mhShopKey(n),l); mhStockSetReorder(mhShopKey(n),r);}); })()""")
    ev("localStorage.setItem('mh_recipes', JSON.stringify([{id:'t1',name:'Rice dish',servings:4,ingredients:[{name:'Zz Rice',amount:200,kcal:1,protein:1,fat:1,carbs:1}]}]))")
    ev("()=>mhStockCooked('t1',4)")          # rice 640 -> 440, a cooked batch of 4
    ev("(()=>{const s=mhShopLoad(); mhShopSetAdd(s,'Zz Bread','manual'); mhShopSetAdd(s,'Zz Jam','manual'); s.items.find(i=>i.name==='Zz Bread').checked=true; s.usuals=[{key:mhShopKey('Zz Salt'),name:'Zz Salt'}]; mhShopSave(s);})()")
    ev("mhStockSweep()")
    before = {'stock': ev("JSON.stringify(Object.values(mhStockLoad().items).map(i=>[i.key,i.level,i.reorder,i.pack,i.shop]).sort())"), 'cooked': ev("JSON.stringify(mhStockLoad().cooked)"),
              'list': ev("JSON.stringify(mhShopLoad().items.map(i=>[i.key,i.checked,i.shop]).sort())")}
    if lv('Zz Rice') != 440: f.add('BUG', f'setup: rice {lv("Zz Rice")}')
    # phone -> tablet: the tablet has different counts of its own
    pack = ev("mhStockExport('Pete phone')")
    ev("(()=>{mhStockSetLevel(mhShopKey('Zz Rice'),5); mhStockSetLevel(mhShopKey('Zz Milk'),9); const o=mhStockLoad(); o.cooked={}; mhStockSave(o);})()")
    ev("localStorage.setItem('mh_last_full_backup_date', todayStr())")
    ev("p=>mhStockImportStart(p)", pack); page.wait_for_timeout(300)
    if page.locator('#appModalConfirm').count(): page.click('#appModalConfirm'); page.wait_for_timeout(500)
    else: f.add('BUG', 'importing asks first')
    after = {'stock': ev("JSON.stringify(Object.values(mhStockLoad().items).map(i=>[i.key,i.level,i.reorder,i.pack,i.shop]).sort())"), 'cooked': ev("JSON.stringify(mhStockLoad().cooked)")}
    if after['stock'] != before['stock']: f.add('BUG', f'transfer: every count, reorder, pack and shop arrives exactly: {after["stock"]} vs {before["stock"]}')
    if after['cooked'] != before['cooked']: f.add('BUG', f'transfer: the cooked batch arrives: {after["cooked"]} vs {before["cooked"]}')
    # applying the same file again is a replace, not an add
    ev("p=>mhStockImportApply(p)", pack)
    if lv('Zz Rice') != 440 or lv('Zz Milk') != 1500: f.add('BUG', 'transfer applied twice still gives the file\'s numbers, not double')
    # the list survives the import (it is not part of the stock file)
    if ev("JSON.stringify(mhShopLoad().items.map(i=>[i.key,i.checked,i.shop]).sort())") != before['list'].replace('"zz eggs"', '"zz eggs"') and 'zz bread' not in ev("JSON.stringify(mhShopLoad().items.map(i=>i.key))"): f.add('BUG', 'transfer: the shopping list is still there')
    if ev("mhShopLoad().items.find(i=>i.key===mhShopKey('Zz Bread'))?.checked") is not True: f.add('BUG', 'transfer: a tick made mid-shop is kept')
    # backup mid-shop, change everything, restore
    snap = ev("JSON.stringify([mhStockLoad().items, mhShopLoad().items.map(i=>[i.key,i.checked]), mhShopLoad().usuals.map(u=>u.key)])")
    payload = ev("buildFullBackupPayload()")
    ev("(()=>{const s=mhShopLoad(); s.items=[]; s.usuals=[]; mhShopSave(s); localStorage.removeItem(MH_STOCK_KEY);})()")
    ev("p=>mhApplyBackupObject(p,'mid shop')", payload); page.wait_for_timeout(2500)
    if ev("JSON.stringify(mhStockLoad().items)") != ev("s=>JSON.stringify(JSON.parse(s)[0])", snap): f.add('BUG', 'restore: the stock comes back exactly')
    if ev("mhShopLoad().items.find(i=>i.key===mhShopKey('Zz Bread'))?.checked") is not True: f.add('BUG', 'restore: the tick made mid-shop comes back')
    if ev("mhShopLoad().usuals.map(u=>u.key).join()") != ev("s=>JSON.parse(s)[2].join()", snap): f.add('BUG', 'restore: regulars come back')
    if ev("mhStockLoad().cooked && mhStockLoad().cooked.t1") != 4: f.add('BUG', 'restore: the cooked batch comes back')
    # finishing the shop after the restore still works and counts once
    ev("mhShopComplete()"); page.wait_for_timeout(300)
    if page.locator('#appModalConfirm').count(): page.click('#appModalConfirm'); page.wait_for_timeout(400)
    if 'zz bread' in ev("JSON.stringify(mhShopLoad().items.map(i=>i.key))"): f.add('BUG', 'after a restore, Shopping complete still empties what was ticked')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
