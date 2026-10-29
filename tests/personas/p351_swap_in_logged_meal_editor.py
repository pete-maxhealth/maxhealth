"""Persona 351 (v3.10.1242): the itemised editors for a logged meal (Today's log and History) get the same 🔄 library swap as the recipe builder,
Cook Mode and suggested combos. The amount and its unit are kept, macros come from the library food, nothing is stored until Save, Cancel leaves
the meal untouched, and the swap survives a reload. No size in Amount: the library's own portion is used (never guessed). Invented foods only."""
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
    # invented library foods (per 100 g): Zed chicken 200 kcal / 30 P / 8 F / 0 C ; Zed turkey 150 kcal / 28 P / 4 F / 0 C
    ev("""(()=>{const lib=loadLibrary();
      lib.push({name:'Zed turkey',portion:'100g',kcal:148,protein:28,fat:4,carbs:0,fibre:0,polyols:0});
      lib.push({name:'Zed chicken',portion:'100g',kcal:192,protein:30,fat:8,carbs:0,fibre:0,polyols:0});
      saveLibrary(lib);})()""")

    def swap_via_picker(btn_sel, pick_name):
        if btn_sel.startswith('JS:'): ev(btn_sel[3:].replace('@DI@', str(DI)))
        else: p.locator(btn_sel).first.click()
        p.wait_for_timeout(500)
        p.locator('#recipeLibSearch').fill(pick_name); p.wait_for_timeout(600)
        p.locator('#recipeLibPickerList [onclick*="_libPickerItemChosen"]:has-text("' + pick_name + '")').first.click(); p.wait_for_timeout(500)

    # ---- Today's log ----
    ev("""state.todayLog=[{id:7001,description:'Zed plate',amount:'1 serving',time:'12:00',kcal:372,protein:35,carbs:20,fat:12,fibre:0,
        items:[{name:'Zed chicken',amount:'150g',kcal:288,protein:45,carbs:0,fat:12,fibre:0},{name:'Zed rice',amount:'50g',kcal:84,protein:1,carbs:20,fat:0,fibre:0}]}]; updateDashboard()""")
    p.wait_for_timeout(300)
    ev("editLogEntry(7001)"); p.wait_for_timeout(400)
    if p.locator('#log-edit-items-7001 button[title*="Swap"]').count() != 2: f.add('BUG', '1: each ingredient row has a 🔄 swap button')
    if p.locator('#log-edit-items-7001 button[title*="Swap"]').count():
        t = ev("document.querySelector('#log-edit-items-7001 button[title*=Swap]').title")
        if t != 'Swap for something similar in your library': f.add('BUG', f'1b: same wording as the combo swap: {t}')
    swap_via_picker('#log-edit-items-7001 button[title*="Swap"]', 'Zed turkey')
    row = ev("(()=>{const i=window._logEditWorkingItems[7001][0];return [i.name,i.amount,i.kcal,i.protein,i.fat,i.carbs]})()")
    if row != ['Zed turkey', '150g', 222, 42, 6, 0]: f.add('BUG', f'2: 150g of Zed turkey should be 222 kcal / 42 P / 6 F: {row}')
    if ev("document.querySelector('#log-edit-items-7001 input').value") != 'Zed turkey': f.add('BUG', '3: the row shows the new name')
    if ev("state.todayLog[0].items[0].name") != 'Zed chicken': f.add('BUG', '4: nothing changes in the log before Save')
    # Cancel leaves the meal untouched
    p.locator('#log-entry-7001 .log-edit-form button.cancel').click(); p.wait_for_timeout(300)
    if ev("state.todayLog[0].items[0].name+state.todayLog[0].kcal") != 'Zed chicken372': f.add('BUG', '5: Cancel keeps the original meal')
    # swap again, then Save: totals follow, amount kept; edit amount afterwards re-scales from the NEW food
    ev("editLogEntry(7001)"); p.wait_for_timeout(400)
    swap_via_picker('#log-edit-items-7001 button[title*="Swap"]', 'Zed turkey')
    p.fill('#log-edit-amt-7001-0', '300g'); p.wait_for_timeout(200)
    k = ev("window._logEditWorkingItems[7001][0].kcal")
    if k != 444: f.add('BUG', f'6: amount edit after a swap scales from the new food (300g = 444 kcal): {k}')
    p.fill('#log-edit-amt-7001-0', '150g'); p.wait_for_timeout(200)
    ev("saveLogEditItems(7001)"); p.wait_for_timeout(500)
    e = ev("state.todayLog[0]")
    if e['items'][0]['name'] != 'Zed turkey' or e['items'][0]['amount'] != '150g' or e['kcal'] != 306: f.add('BUG', f'7: saved swap + derived total (222+84): {e["items"][0]["name"]} {e["items"][0]["amount"]} {e["kcal"]}')
    if '_substitutedFrom' in e['items'][0]: f.add('BUG', '8: the staging tag is not stored in the log')
    # reload keeps it
    ev("updateDashboard()"); p.wait_for_timeout(300)
    if 'Zed turkey' not in ev("document.getElementById('log-entry-7001').innerText") and 'Zed turkey' not in ev("JSON.stringify(state.todayLog)"): f.add('BUG', '9: swap is in the saved log after a redraw')
    # item with no size in Amount: library's own portion, never guessed
    ev("""state.todayLog=[{id:7002,description:'Zed odd',amount:'1 serving',time:'13:00',kcal:100,protein:5,carbs:5,fat:5,fibre:0,
        items:[{name:'Zed chicken',amount:'a handful',kcal:60,protein:5,carbs:0,fat:3,fibre:0},{name:'Zed rice',amount:'50g',kcal:40,protein:0,carbs:5,fat:2,fibre:0}]}]; updateDashboard()""")
    ev("editLogEntry(7002)"); p.wait_for_timeout(400)
    swap_via_picker('#log-edit-items-7002 button[title*="Swap"]', 'Zed turkey')
    row = ev("(()=>{const i=window._logEditWorkingItems[7002][0];return [i.name,i.amount,i.kcal]})()")
    if row != ['Zed turkey', '100g', 148]: f.add('BUG', f'10: no size in Amount uses the library portion (100g, 148 kcal): {row}')
    # ml keeps its unit
    p.locator('#log-entry-7002 .log-edit-form button.cancel').click(); p.wait_for_timeout(300)
    ev("""state.todayLog=[{id:7003,description:'Zed drink',amount:'1 serving',time:'14:00',kcal:100,protein:5,carbs:5,fat:5,fibre:0,
        items:[{name:'Zed chicken',amount:'200ml',kcal:60,protein:5,carbs:0,fat:3,fibre:0},{name:'Zed rice',amount:'50g',kcal:40,protein:0,carbs:5,fat:2,fibre:0}]}]; updateDashboard()""")
    ev("editLogEntry(7003)"); p.wait_for_timeout(400)
    swap_via_picker('#log-edit-items-7003 button[title*="Swap"]', 'Zed turkey')
    if ev("window._logEditWorkingItems[7003][0].amount") != '200ml': f.add('BUG', '11: ml unit kept')
    p.locator('#log-entry-7003 .log-edit-form button.cancel').click(); p.wait_for_timeout(300)

    # ---- History (a past day) ----
    ev("renderHistory()"); p.wait_for_timeout(300)
    DI = ev("(()=>{const dt=(document.querySelector('.hist-day-date')||{}).textContent; return state.history.findIndex(x=>x.date===(dt||'').trim());})()")
    RI = 0  # the day shown first is rendered first
    evd = lambda js: ev(js.replace('@DI@', str(DI)).replace('@IDX@', str(RI)))
    evd("""(()=>{const d=state.history[@DI@]; d.log=[{id:7101,description:'Zed past plate',amount:'1 serving',time:'12:00',kcal:372,protein:35,carbs:20,fat:12,fibre:0,
        items:[{name:'Zed chicken',amount:'150g',kcal:288,protein:45,carbs:0,fat:12,fibre:0},{name:'Zed rice',amount:'50g',kcal:84,protein:1,carbs:20,fat:0,fibre:0}]}]; saveState();})()""")
    ev("renderHistory()"); p.wait_for_timeout(500)
    evd("document.getElementById('histBody@IDX@')&&document.getElementById('histBody@IDX@').classList.add('open')")
    ev("document.getElementById('maintab-log').click()"); p.wait_for_timeout(400); ev("document.getElementById('logtab-hist').click()"); p.wait_for_timeout(600); ev("renderHistory()"); evd("document.getElementById('histBody@IDX@').classList.add('open')"); p.wait_for_timeout(300)
    p.locator('.hist-day').nth(RI).locator('.hist-entry').first.locator('span[onclick*=editHistEntryByDate]').click(); p.wait_for_timeout(600)  # a real tap on the meal name
    if ev("document.querySelectorAll('.hist-edit-form').length") != 1: f.add('BUG', 'H0: tapping a meal name in History opens its editor')
    if p.locator(f'#hist-edit-items-{DI}-0 button[title*="Swap"]').count() != 2: f.add('BUG', '12: History editor rows have the 🔄 swap too')
    else:
        swap_via_picker("JS:swapHistEditItem('@DI@-0',0)", 'Zed turkey')
        row = evd("(()=>{const i=window._histEditWorkingItems['@DI@-0'][0];return [i.name,i.amount,i.kcal]})()")
        if row != ['Zed turkey', '150g', 222]: f.add('BUG', f'13: History swap keeps 150g and recalculates: {row}')
        if evd("state.history[@DI@].log[0].items[0].name") != 'Zed chicken': f.add('BUG', '14: History unchanged before Save')
        evd("saveHistEditItems(@DI@,0)"); p.wait_for_timeout(500)
        e = evd("state.history[@DI@].log[0]")
        if e['items'][0]['name'] != 'Zed turkey' or e['kcal'] != 306: f.add('BUG', f'15: History save keeps the swap and total (306): {e["items"][0]["name"]} {e["kcal"]}')
        if evd("(state.history[@DI@].totals||state.history[@DI@]).kcal") in (None, 0): f.add('BUG', '16: the day total is still present after the swap')
    # neighbours: the recipe-builder swap picker and the combo swap still open the same picker
    ev("_openSubstitutePicker('Zed chicken', ()=>{})"); p.wait_for_timeout(400)
    if ev("document.getElementById('recipeLibSearch').value") != 'Zed chicken': f.add('BUG', '17: the shared swap picker still pre-fills the name')
    if errs: f.add('JS-exception', errs[0])
    b.close()
bad = any(s in ('BUG', 'JS-exception') for s, _ in f)
for s, m in f: print(s, m)
print('BUGS' if bad else 'OK', len(f)); sys.exit(1 if bad else 0)
