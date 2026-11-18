"""Persona 502 (v3.10.1426): deleting a logged food, a history entry, a whole history day, a library food or a recipe keeps its "Are you sure" and now also offers Undo
in the toast. Undo puts the item back where it was (and a logged food's cupboard stock as it was); reload keeps it; the confirm no longer says "can't be undone". Invented data."""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept()); page.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    toast = lambda: ev("document.getElementById('toast')?.innerText||''")
    has_undo = lambda: ev("!!document.querySelector('#toast .toast-undo')")
    undo = lambda: (ev("document.querySelector('#toast .toast-undo').click()"), page.wait_for_timeout(400))
    confirm_ok = lambda: (ev("document.getElementById('appModalConfirm').click()"), page.wait_for_timeout(400))
    E = lambda i, n: "{id:'%s',name:'%s',description:'%s',kcal:100,protein:5,carbs:10,fat:2,time:'08:00'}" % (i, n, n)
    # 1 logged food, with cupboard stock that delete gives back
    ev("mhStockTrack('Zzqx Oats',{base:'g'})")
    ev("(()=>{state.todayLog=[%s,%s,%s]; saveState(); updateDashboard();})()" % (E('a1', 'Zzqx One'), E('a2', 'Zzqx Two'), E('a3', 'Zzqx Three')))
    names = lambda: ev("state.todayLog.map(e=>e.name).join(',')")
    ev("deleteLogEntry('a2')"); ev("document.getElementById('appModal')") ; confirm_ok()
    names() == 'Zzqx One,Zzqx Three' or f.add('FAIL', f'log delete: {names()}')
    has_undo() or f.add('FAIL', f'log delete: no Undo in toast {toast()!r}')
    undo(); names() == 'Zzqx One,Zzqx Two,Zzqx Three' or f.add('FAIL', f'log Undo did not put it back in place: {names()}')
    page.reload(); page.wait_for_timeout(1500); ev("document.getElementById('onboardingOverlay')?.remove()")
    names() == 'Zzqx One,Zzqx Two,Zzqx Three' or f.add('FAIL', f'log Undo lost on reload: {names()}')
    # 2 history entry and day
    ev("(()=>{state.history=[{date:'2026-11-01',log:[%s,%s],totals:{kcal:200,protein:10,fat:4,carbs:20,fibre:0,polyols:0}},{date:'2026-11-02',log:[%s],totals:{kcal:100,protein:5,fat:2,carbs:10,fibre:0,polyols:0}}]; saveState();})()" % (E('h1', 'Zzqx H1'), E('h2', 'Zzqx H2'), E('h3', 'Zzqx H3')))
    hist = lambda: ev("JSON.stringify(state.history.map(d=>[d.date,d.log.map(e=>e.name),d.totals.kcal]))")
    h0 = hist()
    ev("deleteHistEntry(0,0)"); confirm_ok()
    hist() != h0 or f.add('FAIL', 'history delete did nothing')
    has_undo() or f.add('FAIL', 'history entry: no Undo'); undo(); hist() == h0 or f.add('FAIL', f'history entry Undo: {hist()} != {h0}')
    ev("deleteHistDay('2026-11-01')"); confirm_ok(); ev("state.history.length") == 1 or f.add('FAIL', 'day delete did nothing')
    has_undo() or f.add('FAIL', 'history day: no Undo'); undo(); hist() == h0 or f.add('FAIL', f'history day Undo: {hist()}')
    # 3 library food
    ev("saveLibrary([{name:'Zzqx Aa',kcal:1,protein:1,carbs:1},{name:'Zzqx Bb',kcal:2,protein:2,carbs:2},{name:'Zzqx Cc',kcal:3,protein:3,carbs:3}])")
    lib = lambda: ev("loadLibrary().map(x=>x.name).join(',')")
    l0 = lib(); ev("deleteFromLibrary(1)"); confirm_ok()
    lib() == 'Zzqx Aa,Zzqx Cc' or f.add('FAIL', f'library delete: {lib()}')
    has_undo() or f.add('FAIL', 'library: no Undo'); undo(); lib() == l0 or f.add('FAIL', f'library Undo: {lib()}')
    # 4 recipe
    ev("saveRecipes([{id:'r1',name:'Zzqx Stew',ingredients:[],servings:2},{id:'r2',name:'Zzqx Soup',ingredients:[],servings:2}])")
    rec = lambda: ev("loadRecipes().map(r=>r.name).join(',')")
    ev("deleteRecipe('r1')")
    "can't be undone" not in ev("document.getElementById('appModal')?.innerText||''") or f.add('FAIL', 'the confirm still says it cannot be undone')
    confirm_ok(); rec() == 'Zzqx Soup' or f.add('FAIL', f'recipe delete: {rec()}')
    has_undo() or f.add('FAIL', 'recipe: no Undo'); undo(); rec() == 'Zzqx Stew,Zzqx Soup' or f.add('FAIL', f'recipe Undo: {rec()}')
    # cancelling the confirm deletes nothing and offers no Undo
    ev("deleteRecipe('r2')"); ev("document.getElementById('appModalCancel')?.click()"); page.wait_for_timeout(300)
    rec() == 'Zzqx Stew,Zzqx Soup' or f.add('FAIL', 'cancel deleted the recipe')
    if errs: f.add('FAIL', f'page errors {errs[:3]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
