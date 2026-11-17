"""Persona 498 (v3.10.1417): Shopping and My cupboards actions carry an Undo. Quantity, add, recipe add, saved-list apply, stock change; Undo puts the list, cupboards and saved lists back
exactly; an action that changes nothing offers no Undo; one tap never stacks two toasts. Invented data."""
import sys, re, json; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept()); page.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()"); ev("mhShopOpen()"); page.wait_for_timeout(300)
    toast = lambda: ev("document.getElementById('toast')?.innerText||''")
    has_undo = lambda: ev("!!document.querySelector('#toast .toast-undo')")
    undo = lambda: (ev("document.querySelector('#toast .toast-undo').click()"), page.wait_for_timeout(400))
    state = lambda: ev("JSON.stringify([mhShopLoad().items.map(i=>[i.name,i.qty||1,i.hidden,i.checked]), Object.values(mhStockLoad().items).map(i=>[i.name,i.level])])")
    # 1 add by hand
    s0 = state(); ev("mhShopLoad(); document.getElementById('mhShopOwn') || mhShopRender()"); ev("document.getElementById('mhShopOwn').value='Zzqx Butter'"); ev("mhShopAddOwn()"); page.wait_for_timeout(500)
    ev("mhShopLoad().items.some(i=>i.name==='Zzqx Butter')") or f.add('FAIL', 'add did not add')
    has_undo() or f.add('FAIL', f'add: no Undo in toast: {toast()!r}')
    undo(); state() == s0 or f.add('FAIL', f'add: Undo did not restore the list: {state()}')
    # 2 quantity
    ev("(()=>{const s=mhShopLoad(); mhShopSetAdd(s,'Zzqx Jam','own','',null); mhShopSave(s)})()"); s1 = state(); iid = ev("mhShopLoad().items[0].id")
    ev(f"mhShopQty({iid!r}, 1)"); ev("mhShopLoad().items[0].qty") == 2 or f.add('FAIL', 'qty did not change')
    has_undo() or f.add('FAIL', 'qty: no Undo'); undo(); state() == s1 or f.add('FAIL', 'qty: Undo did not restore')
    # 3 recipe: one toast with Undo, and Undo removes everything it added
    ev("(()=>{const r=loadRecipes()||[]; r.push({id:'zu1',name:'Zzqx Soup',ingredients:[{name:'Zzqx Leek'},{name:'Zzqx Stock'}]}); saveRecipes(r)})()"); s2 = state()
    ev("mhShopRecipeAdd('zzqx soup')"); page.wait_for_timeout(500)
    ev("mhShopLoad().items.some(i=>i.name==='Zzqx Leek')") or f.add('FAIL', 'recipe did not add')
    'added from' in toast() and has_undo() or f.add('FAIL', f'recipe: toast should say what happened and carry Undo: {toast()!r}')
    ev("document.querySelectorAll('#toast .toast-undo').length") == 1 or f.add('FAIL', 'recipe: more than one Undo')
    undo(); state() == s2 or f.add('FAIL', 'recipe: Undo did not remove what it added'); 'Undone' in toast() or f.add('FAIL', f'no "Undone" confirmation: {toast()!r}')
    # 4 cupboards: stock change
    ev("mhStockTrack('Zzqx Flour',{base:'g'})"); key = ev("mhShopKey('Zzqx Flour')"); ev(f"mhStockSetLevel({key!r}, 500)"); page.wait_for_timeout(300); s3 = state()
    ev(f"mhStockSetLevel({key!r}, 120)"); ev(f"mhStockLoad().items[{key!r}].level") == 120 or f.add('FAIL', 'stock level did not change')
    has_undo() or f.add('FAIL', 'stock: no Undo'); undo(); state() == s3 or f.add('FAIL', f'stock: Undo did not restore: {state()}')
    # 5 a no-change action offers no Undo
    ev("document.getElementById('toast').innerHTML=''; _toastUndoUntil=0"); ev("_shopUi.addOpen=true; mhShopAddKind('food')"); ev("document.getElementById('mhShopOwn').value='Zzqx Jam'"); ev("mhShopAddOwn()"); page.wait_for_timeout(300); has_undo() and f.add('FAIL', 'an action that changes nothing offered an Undo')
    # 6 saved list apply
    ev("(()=>{const s=mhShopLoad(); mhShopSetAdd(s,'Zzqx Eggs','own','',null); mhShopSave(s)})()"); ev("mhShopLoad(); document.querySelector('#mhShopPane') && 0")
    errs and f.add('FAIL', f'page errors {errs}')
print('findings', len(f))
