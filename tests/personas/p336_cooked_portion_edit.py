"""Persona 336 (Pete, 27 Oct 2026): a recipe cooked for 4, only a half portion eaten, then the portion changed (percentage or amount) or deleted.
The ingredients came off stock once, when the batch was cooked. Editing the entry must move the leftover portions, never take the ingredients a
second time. Checks: half portion (stock 200 g, 3.5 left over); edited to a full portion (stock unchanged, 3 left); back to half (3.5); edited to
more than are left over (the extra share comes off stock); a past-day edit; deleting gives the portions back; stock counting off leaves it alone."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()"); ev("mhShopOpen()")
    ev("""localStorage.setItem('mh_recipes', JSON.stringify([{id:'r1',name:'Bolognese bake',servings:4,ingredients:[{name:'Beef mince',amount:800,kcal:1600,protein:160,fat:100,carbs:0}]}]))""")
    ev("mhStockTrack('Beef mince',{base:'g',pack:1000,shop:'Asda'})")
    mk = ev("n=>mhShopKey(n)", 'Beef mince')
    lv = lambda: ev("k=>mhStockLoad().items[k].level", mk)
    cooked = lambda: ev("mhStockLoad().cooked && mhStockLoad().cooked.r1 || 0")
    ev("k=>mhStockSetLevel(k,1000)", mk)
    ev("()=>logRecipe('r1',0.5)"); page.wait_for_timeout(700)
    page.fill('#appPromptInput', '4'); page.click('#appModalConfirm'); page.wait_for_timeout(600)
    if lv() != 200 or cooked() != 3.5: f.add('BUG', f'cook 4, eat half: stock 200 g, 3.5 left: {lv()} {cooked()}')
    scale = lambda x: ev("x=>{const e=state.todayLog[state.todayLog.length-1]; e.items.forEach(i=>{ i.amount=(parseFloat(i.amount)*x)+'g'; i.kcal=Math.round(i.kcal*x); }); e.kcal=Math.round(e.kcal*x); mhStockResync(e, todayStr());}", x)
    scale(2)
    if lv() != 200 or cooked() != 3: f.add('BUG', f'half edited to a full portion: stock stays 200 g, 3 left: {lv()} {cooked()}')
    scale(0.5)
    if lv() != 200 or cooked() != 3.5: f.add('BUG', f'back to half: stock 200 g, 3.5 left: {lv()} {cooked()}')
    scale(8)   # all 4 cooked portions eaten: the whole batch, nothing more off stock
    if lv() != 200 or cooked() != 0: f.add('BUG', f'edited to 4 portions with 4 cooked: stock 200 g, none left: {lv()} {cooked()}')
    scale(1.25)   # 5 portions eaten: 4 from the batch, the 5th (200 g) from stock
    if lv() != 0 or cooked() != 0: f.add('BUG', f'edited to 5 portions with 4 cooked: stock 0 g, none left: {lv()} {cooked()}')
    scale(0.1)
    if lv() != 200 or cooked() != 3.5: f.add('BUG', f'back to half again: stock 200 g, 3.5 left: {lv()} {cooked()}')
    ev("()=>_doDeleteLogEntry(state.todayLog[state.todayLog.length-1].id)")
    if lv() != 200 or cooked() != 4: f.add('BUG', f'delete: portions back, stock 200 g: {lv()} {cooked()}')
    if errs: f.add('BUG', f'page errors {errs[:3]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
