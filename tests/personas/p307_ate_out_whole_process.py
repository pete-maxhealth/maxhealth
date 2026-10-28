"""Persona 307: the ate-out mark, end to end: it survives a reload, editing the meal in History leaves stock alone, the day's calories and totals still count it, the calendar opens the same day with the same button, Today and History use the same plate (v3.10.1209). Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from datetime import date, timedelta
_d = date.today() - timedelta(days=2)   # relative, so the History period never moves past it
D, ISO = _d.strftime('%d/%m/%y'), _d.isoformat()
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()"); ev("window._mhLibQuiet=true")
    ev("mhStockTrack('Zzqx Cream',{base:'g',shop:'Asda'}); mhStockSetLevel(mhShopKey('Zzqx Cream'),500); (()=>{const o=mhStockLoad(); o.items[mhShopKey('Zzqx Cream')].since=Date.parse('2026-10-01'); mhStockSave(o)})()")
    ev("(()=>{ const e={id:555001, name:'Zzqx Cream', description:'Zzqx Cream (250g)', time:'18:48', kcal:300, protein:2, carbs:3, fat:30, items:[{name:'Zzqx Cream', amount:'250g', kcal:300, protein:2, carbs:3, fat:30}]}; state.history.unshift({date:'" + D + "', log:[e], totals:{kcal:300,protein:2,carbs:3,fat:30}}); saveState(); mhStockOnLog(e,'" + ISO + "'); })()")
    lv = lambda: ev("mhStockLoad().items[mhShopKey('Zzqx Cream')].level")
    took = lv()
    if took >= 500: f.add('BUG', f'setup: the meal took stock off ({took})')
    ev("mhStockAteOutHist('" + D + "',555001)"); page.wait_for_timeout(200)
    if lv() != 500: f.add('BUG', 'ate out puts stock back')
    # reload: flag and stock survive
    page.reload(); page.wait_for_timeout(1800); ev = page.evaluate
    if not ev("(state.history.find(d=>d.date==='" + D + "')||{log:[{}]}).log[0].noStock"): f.add('BUG', 'the ate-out mark survives a reload')
    if lv() != 500: f.add('BUG', f'stock survives the reload: {lv()}')
    # editing the meal keeps stock alone (the History edit path resyncs)
    ev("(()=>{const d=state.history.find(x=>x.date==='" + D + "'); mhStockResync(d.log[0],'" + D + "')})()")
    if lv() != 500: f.add('BUG', f'editing an ate-out meal leaves stock alone: {lv()}')
    # calories and totals still count the meal
    if ev("state.history.find(d=>d.date==='" + D + "').totals.kcal") != 300: f.add('BUG', 'the day still counts the meal calories')
    # calendar opens the same day, with the button
    ev("switchTabById('hist')"); page.wait_for_timeout(400); ev("renderHistory()"); ev("toggleHistDay(0)"); page.wait_for_timeout(300)
    if not page.locator('[data-hist-ateout="555001"]').count(): f.add('BUG', 'History shows the button after a reload')
    if ev("getComputedStyle(document.querySelector('[data-hist-ateout=\"555001\"]')).opacity") != '1': f.add('BUG', 'a marked meal shows the button at full strength')
    ev("_historyCalendarSelectDate('" + D + "', true, false)"); page.wait_for_timeout(700)
    if not page.locator('#hist-day-' + D.replace('/', '-')).count(): f.add('BUG', 'the calendar takes you to the same History day')
    # tap again takes stock off; and after the stock-take rule, no double count
    ev("mhStockAteOutHist('" + D + "',555001)"); page.wait_for_timeout(200)
    if lv() >= 500: f.add('BUG', 'unmarking takes the stock off again')
    ev("mhStockAteOutHist('" + D + "',555001)"); page.wait_for_timeout(200)
    if lv() != 500: f.add('BUG', 'marking again puts it back (no double count)')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
