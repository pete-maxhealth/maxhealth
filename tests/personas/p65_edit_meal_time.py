"""Persona 65: changing a portion never moves the time a meal was eaten; the Meal time field in the edit forms corrects it on
purpose, and choosing a time clears the 'approximate' flag so the meal counts for fasting. Covers the single-item and the
multi-ingredient edit forms and Cancel."""
import sys, re; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("localStorage.setItem('mh_onboarded','1')")
    page.evaluate("""state.todayLog = [
      {id:1, time:'08:15', description:'eggs', amount:'100g', kcal:150, protein:12, fat:10, carbs:1},
      {id:2, time:'13:00', timeApprox:true, description:'cheese', amount:'50g', kcal:200, protein:12, fat:16, carbs:1},
      {id:3, time:'19:00', description:'stew', kcal:400, protein:30, fat:20, carbs:6, items:[
         {name:'beef',amount:'100g',kcal:250,protein:25,fat:15,carbs:0},{name:'veg',amount:'100g',kcal:150,protein:5,fat:5,carbs:6}]}];
      saveState(); updateDashboard(); switchTab('today')""")
    page.wait_for_timeout(500)
    g = lambda i: page.evaluate(f"(()=>{{const e=state.todayLog.find(x=>x.id=={i});return [e.time,!!e.timeApprox,e.kcal]}})()")
    # portion change keeps the time
    page.evaluate("editLogEntry(1)"); page.wait_for_timeout(200)
    if page.evaluate("document.getElementById('edit-time-1').value") != '08:15': f.add('BUG', 'time field not prefilled')
    page.fill('#edit-pct-1', '50'); page.evaluate("saveLogEdit(1)")
    if g(1)[0] != '08:15' or g(1)[2] == 150: f.add('BUG', f'portion edit moved the time or did nothing: {g(1)}')
    # approximate entry: blank until set, then counts
    page.evaluate("editLogEntry(2)"); page.wait_for_timeout(200)
    if page.evaluate("document.getElementById('edit-time-2').value") != '': f.add('BUG', 'approximate time should show blank')
    page.evaluate("saveLogEdit(2)")
    if not g(2)[1]: f.add('BUG', 'saving without choosing a time must leave it approximate')
    page.evaluate("editLogEntry(2)"); page.wait_for_timeout(200)
    page.fill('#edit-time-2', '12:40'); page.evaluate("saveLogEdit(2)")
    if g(2)[:2] != ['12:40', False]: f.add('BUG', f'chosen time not applied / flag not cleared: {g(2)}')
    # multi-item form
    page.evaluate("editLogEntry(3)"); page.wait_for_timeout(200)
    page.fill('#edit-time-3', '18:30'); page.evaluate("saveLogEditItems(3)")
    if g(3)[0] != '18:30': f.add('BUG', 'multi-item edit did not apply the time')
    # cancel is a no-op
    page.evaluate("editLogEntry(1)"); page.wait_for_timeout(200)
    page.fill('#edit-time-1', '23:59'); page.evaluate("cancelLogEdit(1)")
    if g(1)[0] != '08:15': f.add('BUG', 'cancel changed the time')
    if errs: f.add('BUG', f'page errors: {errs[:2]}')
print('findings', len(f)); sys.exit(1 if f else 0)
