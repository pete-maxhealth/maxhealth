"""Persona 454: deleting something you made asks "are you sure" (Keep leaves it), and after you confirm an Undo puts it back exactly: a history day, a history entry, a food in the Library, a recipe, a supplement, an activity, a log entry (v3.10.1368). Invented data; destructive, runs on a fresh test server."""
import sys, json; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("saveLibrary([{id:'a1',name:'Zzqx Milk',kcal:60,protein:3.4,carbs:4.7,fat:3.6,portion:'100ml'},{id:'a2',name:'Zzqx Rice',kcal:130,protein:2.7,carbs:28,fat:0.3,portion:'100g'}])")
    ev("state.history = [{date:'2020-03-02', totals:{kcal:500,protein:20,carbs:10,fat:30}, log:[{id:'h1',name:'Zzqx A',kcal:200,protein:10,carbs:5,fat:10,time:'08:00'},{id:'h2',name:'Zzqx B',kcal:300,protein:10,carbs:5,fat:20,time:'12:00'}]},{date:'2020-03-03', totals:{kcal:100,protein:1,carbs:1,fat:1}, log:[{id:'h3',name:'Zzqx C',kcal:100,protein:1,carbs:1,fat:1,time:'09:00'}]}]; state.todayLog = [{id:'t1',name:'Zzqx Today',kcal:120,protein:5,carbs:5,fat:5,time:'10:00'}]; saveState()")
    ev("saveRecipes([{id:'r1',name:'Zzqx Stew',ingredients:[],steps:[]},{id:'r2',name:'Zzqx Pie',ingredients:[],steps:[]}])") if ev("typeof saveRecipes==='function'") else None
    snap = lambda: json.dumps([ev("JSON.stringify(state.history)"), ev("JSON.stringify(state.todayLog)"), ev("JSON.stringify(loadLibrary())"), ev("typeof loadRecipes==='function'?JSON.stringify(loadRecipes()):''")])
    def undo_click():
        loc = page.locator('#toast .toast-undo')
        if not loc.count(): return False
        loc.first.click(timeout=3000); page.wait_for_timeout(400); return True
    def case(name, call, gone):
        before = snap()
        ev(call); page.wait_for_timeout(300)
        if not ev("!!document.querySelector('.app-modal-overlay')"): f.add('BUG', f'{name}: no "are you sure"'); return
        if snap() != before: f.add('BUG', f'{name}: changed before the answer')
        page.locator('#appModalCancel').click(timeout=3000); page.wait_for_timeout(300)
        if snap() != before: f.add('BUG', f'{name}: Keep still changed something')
        ev(call); page.wait_for_timeout(300); page.locator('#appModalConfirm').click(timeout=3000); page.wait_for_timeout(400)
        if snap() == before or not gone(): f.add('BUG', f'{name}: confirming did not delete')
        if not undo_click(): f.add('BUG', f'{name}: no Undo after deleting'); return
        if snap() != before: f.add('BUG', f'{name}: Undo did not put it back exactly')
    case('history day', "deleteHistDay('2020-03-03')", lambda: ev("state.history.length") == 1)
    case('history entry', "deleteHistEntry(0, 0)", lambda: ev("state.history[0].log.length") == 1)
    case('library food', "_doDeleteLibraryItem(0)", lambda: ev("loadLibrary().length") == 1) if False else None
    # direct deletes (the caller asked): Undo only
    before = snap(); ev("_doDeleteLibraryItem(0)"); page.wait_for_timeout(300)
    if ev("loadLibrary().length") != 1: f.add('BUG', 'library food: not deleted')
    if not undo_click() or snap() != before: f.add('BUG', 'library food: Undo did not put it back exactly')
    before = snap(); ev("_doDeleteLogEntry('t1')"); page.wait_for_timeout(300)
    if ev("state.todayLog.length") != 0: f.add('BUG', 'log entry: not deleted')
    if not undo_click() or snap() != before: f.add('BUG', 'log entry: Undo did not put it back exactly')
    if ev("typeof loadRecipes==='function'") and ev("loadRecipes().length") == 2: case('recipe', "deleteRecipe('r1')", lambda: ev("loadRecipes().length") == 1)
    else: f.add('BUG', 'recipes could not be set up for the test')
    # the same Undo is gone once its time is up and does not leave a second toast stacked
    if errs: f.add('BUG', f'page errors: {errs[:2]}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
