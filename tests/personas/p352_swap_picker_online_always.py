"""Persona 352 (v3.10.1243): the swap picker keeps "Search online" and "✨ Try AI" on screen all the time (not only when a search finds nothing),
wherever the swap can take an online result back: logged-meal editors (Today and History), recipe builder. Cook Mode, which cannot, shows neither.
A picked AI result lands in the staged row keeping its amount; Cancel leaves the meal alone. Invented foods and a stubbed AI only."""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 900}, service_workers='block')
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    p = ctx.new_page(); p.on('pageerror', lambda e: errs.append(str(e)[:200])); ev = p.evaluate
    p.goto('http://localhost:5757/'); p.wait_for_timeout(1500); ev("startDemoMode('doris')"); p.wait_for_timeout(2500)
    ev("switchTab('today')"); p.wait_for_timeout(500)
    ev("""(()=>{const lib=loadLibrary(); lib.push({name:'Zed turkey',portion:'100g',kcal:148,protein:28,fat:4,carbs:0,fibre:0,polyols:0}); saveLibrary(lib);})()""")
    ev("window.mhCheckOnline = async () => true; 0")
    ev("window.callHealthAI = async () => ({ok:true, text:'{\"name\":\"Zed AI mince\",\"kcal\":200,\"protein\":20,\"fat\":12,\"carbs\":0}'})")
    ev("""state.todayLog=[{id:8001,description:'Zed plate',amount:'1 serving',time:'12:00',kcal:372,protein:35,carbs:20,fat:12,fibre:0,
        items:[{name:'Zed chicken',amount:'150g',kcal:288,protein:45,carbs:0,fat:12,fibre:0},{name:'Zed rice',amount:'50g',kcal:84,protein:1,carbs:20,fat:0,fibre:0}]}]; updateDashboard()""")
    p.wait_for_timeout(300); ev("editLogEntry(8001)"); p.wait_for_timeout(400)
    row = lambda: p.locator('#recipeLibPickerList [data-lib-online-row]')
    # 1: opens with the row visible even though 'Zed chicken' has no library match for its own name, and after typing something that DOES match
    p.locator('#log-edit-items-8001 button[title*="Swap"]').first.click(); p.wait_for_timeout(500)
    if row().count() != 1 or 'Try AI' not in row().inner_text() or 'Search online' not in row().inner_text(): f.add('BUG', '1: row with Search online + ✨ Try AI shows when the picker opens')
    p.locator('#recipeLibSearch').fill('Zed turkey'); p.wait_for_timeout(500)
    if row().count() != 1: f.add('BUG', '2: row still shows when the search has results')
    p.locator('#recipeLibSearch').fill('zzzqqq'); p.wait_for_timeout(500)
    if row().count() != 1: f.add('BUG', '3: row shows once (not doubled) when nothing matches')
    # 2: Try AI -> estimate -> use -> amount screen -> row swapped, amount kept
    p.locator('#recipeLibSearch').fill('mince'); p.wait_for_timeout(400)
    row().locator('text=Try AI').click(); p.wait_for_timeout(1200)
    if 'Zed AI mince' not in ev("document.getElementById('foodResults').innerText"): f.add('BUG', '4: Try AI shows the AI estimate in the search screen: ' + ev("document.getElementById('foodResults').innerText")[:120])
    else:
        p.locator('#foodResults button:has-text("Use these values")').click(); p.wait_for_timeout(600)
        p.locator('#foodAmountGrams').fill('150'); p.wait_for_timeout(300)
        p.locator('[onclick*="logFoodFromDatabase"]:visible').click(); p.wait_for_timeout(900)
        it = ev("window._logEditWorkingItems[8001][0]")
        if it['name'] != 'Zed AI mince (AI estimate)' and 'Zed AI mince' not in it['name']: f.add('BUG', f'5: AI result lands in the staged row: {it["name"]}')
        if it['amount'] != '150g' or it['kcal'] != 300: f.add('BUG', f'6: amount 150g kept, 200 kcal/100g = 300: {it["amount"]} {it["kcal"]}')
        if ev("state.todayLog[0].items[0].name") != 'Zed chicken': f.add('BUG', '7: nothing stored in the log before Save')
        if ev("document.getElementById('foodSearchView').offsetParent!==null && document.getElementById('foodSearchView').style.display!=='none' && document.getElementById('foodSearch') && document.getElementById('foodSearch').classList.contains('open')"): f.add('BUG', '8: search screen closed after the pick')
    p.locator('#log-entry-8001 .log-edit-form button.cancel').click(); p.wait_for_timeout(300)
    if ev("state.todayLog[0].items[0].name") != 'Zed chicken': f.add('BUG', '9: Cancel keeps the original meal')
    # 3: Search online opens the food search with the typed term, and backing out leaves things alone (no stale target)
    ev("editLogEntry(8001)"); p.wait_for_timeout(400)
    p.locator('#log-edit-items-8001 button[title*="Swap"]').first.click(); p.wait_for_timeout(400)
    p.locator('#recipeLibSearch').fill('lamb'); p.wait_for_timeout(300)
    row().locator('text=Search online').click(); p.wait_for_timeout(700)
    if ev("document.getElementById('foodSearchInput').value") != 'lamb': f.add('BUG', '10: Search online carries the typed word into the food search')
    if not ev("!!_editSearchTarget"): f.add('BUG', '11: the swap target is set while searching')
    ev("closeFoodSearch()"); p.wait_for_timeout(300)
    if ev("!!_editSearchTarget"): f.add('BUG', '12: backing out clears the swap target')
    p.locator('#log-entry-8001 .log-edit-form button.cancel').click(); p.wait_for_timeout(300)
    # 4: History editor has it too
    ev("""(()=>{const d=state.history[0]; d.log=[{id:8101,description:'Zed past plate',amount:'1 serving',time:'12:00',kcal:372,protein:35,carbs:20,fat:12,fibre:0,
        items:[{name:'Zed chicken',amount:'150g',kcal:288,protein:45,carbs:0,fat:12,fibre:0},{name:'Zed rice',amount:'50g',kcal:84,protein:1,carbs:20,fat:0,fibre:0}]}]; saveState();})()""")
    ev("renderHistory()"); p.wait_for_timeout(500); ev("document.getElementById('histBody0')&&document.getElementById('histBody0').classList.add('open')")
    ev("editHistEntry(0,0)"); p.wait_for_timeout(500); ev("swapHistEditItem('0-0',0)"); p.wait_for_timeout(500)
    if row().count() != 1: f.add('BUG', '13: History swap picker has the row')
    else:
        p.locator('#recipeLibSearch').fill('mince'); p.wait_for_timeout(300)
        row().locator('text=Try AI').click(); p.wait_for_timeout(1200)
        p.locator('#foodResults button:has-text("Use these values")').click(); p.wait_for_timeout(600)
        p.locator('#foodAmountGrams').fill('150'); p.wait_for_timeout(300)
        p.locator('[onclick*="logFoodFromDatabase"]:visible').click(); p.wait_for_timeout(900)
        it = ev("window._histEditWorkingItems['0-0'][0]")
        if 'Zed AI mince' not in it['name'] or it['kcal'] != 300: f.add('BUG', f'14: History AI swap: {it["name"]} {it["kcal"]}')
        if ev("state.history[0].log[0].items[0].name") != 'Zed chicken': f.add('BUG', '15: History unchanged before Save')
        ev("saveHistEditItems(0,0)"); p.wait_for_timeout(400)
        if 'Zed AI mince' not in ev("state.history[0].log[0].items[0].name") or ev("state.history[0].log[0].kcal") != 384: f.add('BUG', f'16: History save keeps the AI swap and total (300+84): {ev("state.history[0].log[0].kcal")}')
    # 5: Cook Mode swap (no online route) shows no row; library swap still works there
    ev("_openSubstitutePicker('Zed chicken', ()=>{})"); p.wait_for_timeout(400)
    if row().count() != 0: f.add('BUG', '17: a swap picker with no online route (Cook Mode) shows no online row')
    if errs: f.add('JS-exception', errs[0])
    b.close()
bad = any(s in ('BUG', 'JS-exception') for s, _ in f)
for s, m in f: print(s, m)
print('BUGS' if bad else 'OK', len(f)); sys.exit(1 if bad else 0)
