"""Persona 260: shopping works the same with stock counting on or off (v3.10.1156). Pete: on or off only decides whether amounts are tracked; the list, regulars and saved lists
are for everyone. Shopping complete offers "Empty the basket" or "Keep the whole list for next shop". With stock off every regular stays (nothing else can bring a food back),
and a shop never drops you into the stock review. Saved lists do not depend on stock. Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    SETUP = """(()=>{const s=mhShopLoad(); s.items=[]; s.usuals=['Zzqx Reg Milk','Zzqx Reg Loo Roll'];
      mhShopSetAdd(s,'Zzqx Reg Milk','own','',null); mhShopSetAdd(s,'Zzqx Reg Loo Roll','own','',null,{nonFood:true}); mhShopSetAdd(s,'Zzqx One Off','own','',null); mhShopSetAdd(s,'Zzqx Hairspray','own','',null,{nonFood:true});
      s.items.forEach(i=>i.checked=true); mhShopSave(s);})()"""
    names = lambda: sorted([i['name'], i['checked']] for i in ev("mhShopLoad().items"))
    # ---- stock OFF (never used) ----
    ev("mhShopOpen()"); ev(SETUP); ev("mhShopComplete()"); page.wait_for_timeout(300)
    if not page.locator('#appModalKeep').count() or not page.locator('#appModalConfirm').count(): f.add('BUG', '1: Shopping complete offers both ways to finish')
    page.click('#appModalConfirm'); page.wait_for_timeout(400)
    got = names()
    if got != [['Zzqx Reg Loo Roll', False], ['Zzqx Reg Milk', False]]: f.add('BUG', f'2: stock off: only the regulars (food too) stay, unticked: {got}')
    ev(SETUP); ev("mhShopComplete()"); page.click('#appModalKeep'); page.wait_for_timeout(400)
    got = names()
    if got != [['Zzqx Hairspray', False], ['Zzqx One Off', False], ['Zzqx Reg Loo Roll', False], ['Zzqx Reg Milk', False]]: f.add('BUG', f'3: keep the whole list: everything stays, unticked: {got}')
    if 'ready for next shop' not in page.inner_text('body'): f.add('BUG', '4: it says so')
    # ---- stock switched OFF but items still tracked: no stock review ----
    ev("mhStockTrack('Zzqx Reg Milk',{base:'ml'}); mhStockTrack('Zzqx One Off',{base:'g'}); (()=>{const o=mhStockLoad(); o.enabled=false; mhStockSave(o);})()")
    ev(SETUP); ev("mhShopComplete()"); page.click('#appModalConfirm'); page.wait_for_timeout(400)
    if ev("_shopUi.view") == 'stockbought' or (ev("mhStockLoad().review") or []): f.add('BUG', '5: with stock off a shop never opens the stock review')
    # ---- stock ON: food regular goes (threshold brings it back), non-food regular stays ----
    ev("(()=>{const o=mhStockLoad(); o.enabled=true; mhStockSave(o);})()")
    ev(SETUP); ev("mhShopComplete()"); page.click('#appModalConfirm'); page.wait_for_timeout(400)
    got = names()
    if got != [['Zzqx Reg Loo Roll', False]]: f.add('BUG', f'6: stock on: a non-food regular stays, food goes: {got}')
    ev("_shopUi.view='list'; (()=>{const o=mhStockLoad(); o.review=[]; mhStockSave(o);})()")
    ev(SETUP); ev("mhShopComplete()"); page.click('#appModalKeep'); page.wait_for_timeout(400)
    if len(names()) != 4: f.add('BUG', f'7: stock on, keep the whole list: {names()}')
    if ev("_shopUi.view") != 'stockbought': f.add('BUG', '8: stock on: bought food still goes to the stock review')
    # ---- saved lists with stock off ----
    ev("(()=>{const o=mhStockLoad(); o.enabled=false; mhStockSave(o);})()"); ev("_shopUi.view='list'")
    ev(SETUP); ev("mhShopListSaveAs('shop')"); page.wait_for_timeout(300); page.fill('#appPromptInput', 'Zzqx Weekly'); page.click('#appModalConfirm'); page.wait_for_timeout(300)
    if 'Zzqx Weekly' not in [l['name'] for l in ev("mhShopListsLoad().lists")]: f.add('BUG', '9: a list can be saved with stock off, using the app\'s own name box')
    ev("(()=>{const s=mhShopLoad(); s.items=[]; mhShopSave(s);})()"); ev("mhShopListApply(mhShopListsLoad().lists[0].id,'merge')")
    if len(ev("mhShopLoad().items")) != 4: f.add('BUG', '10: and brought back with stock off')
    ev("mhShopAddShop()"); page.wait_for_timeout(200); page.fill('#appPromptInput', 'Zzqnewshop'); page.click('#appModalConfirm'); page.wait_for_timeout(300)
    if 'Zzqnewshop' not in ev("mhShopLoad().shops"): f.add('BUG', '11: a shop can be added without a browser pop-up')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
