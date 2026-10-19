"""Persona 208: logging takes stock off (v3.10.1119). Pete Spence logs whey, cream and eggs through every doorway. Covers: a source-level
doorway enumeration (every place a log entry is created either takes stock or is the manual form, which has no amount); today via
logFoods in g, servings and counts; kg and l converting to the base; an amount that cannot be read leaving stock alone (never guessed);
a name that is not tracked being ignored; paste-a-meal; a past day (and a past day older than the last stock-take being ignored);
delete, clear-today and history-delete putting stock back exactly; editing an entry re-applying; and a planned meal never taking stock."""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
src = open(__file__.rsplit('/tests/', 1)[0] + '/maxhealth.html').read().split('\n')
for i, l in enumerate(src):
    if re.search(r'(todayLog|targetDay\.log)\.push\(entry\)', l):
        near = '\n'.join(src[i:i + 4])
        if 'mhStockOnLog' not in near and "source: 'manual'" not in '\n'.join(src[max(0, i - 3):i + 1]):
            f.add('BUG', f'line {i+1}: a log entry is created here without taking stock: {l.strip()}')
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("mhShopOpen()"); page.wait_for_timeout(300)
    ev("mhStockTrack('Whey protein',{base:'g',pack:750,serving:25,shop:'Asda'})"); ev("mhStockTrack('Double Cream (Asda)',{base:'ml',pack:300,shop:'Asda'})")
    ev("mhStockTrack('Eggs',{base:'each',pack:6,shop:'Asda'})")
    wk, ck, ek = [ev("n=>mhShopKey(n)", n) for n in ('Whey protein', 'Double Cream (Asda)', 'Eggs')]
    def reset():
        ev("([a,b,c])=>{mhStockSetLevel(a,750);mhStockSetLevel(b,300);mhStockSetLevel(c,6);state.todayLog=[];saveState();}", [wk, ck, ek])
    lv = lambda k: ev("k=>mhStockLoad().items[k].level", k)
    def food(n, a): return {'name': n, 'amount': a, 'kcal': 100, 'protein': 10, 'fat': 5, 'carbs': 1}
    def log(foods, text='test'): ev("([x,t])=>logFoods(x,t)", [foods, text]); page.wait_for_timeout(150)

    reset(); log([food('Whey protein', '25g')])
    if lv(wk) != 725: f.add('BUG', f'25g logged should leave 725: {lv(wk)}')
    log([food('Whey protein', '2 servings')])
    if lv(wk) != 675: f.add('BUG', '2 servings should take 50 g: %s' % lv(wk))
    log([food('Whey protein', '0.1 kg'), food('Double Cream (Asda)', '0.05 l'), food('Eggs', '2')])
    if (lv(wk), lv(ck), lv(ek)) != (575, 250, 4): f.add('BUG', f'kg/l/count conversions: {(lv(wk), lv(ck), lv(ek))}')
    # unreadable and untracked
    before = lv(wk); log([food('Whey protein', 'a scoop'), food('Chicken', '100g')])
    if lv(wk) != before: f.add('BUG', 'an amount that cannot be read must leave stock alone (never guess)')
    if 'could not read' not in ev("document.body.innerText"): f.add('BUG', 'an unreadable amount should be said out loud')
    log([food('Eggs', '2 portions')])
    if lv(ek) != 4: f.add('BUG', 'portions on an item with no serving size must not guess')
    # delete one, clear all
    reset(); log([food('Whey protein', '100g')]); eid = ev("state.todayLog[0].id")
    ev("id=>_doDeleteLogEntry(id)", eid)
    if lv(wk) != 750: f.add('BUG', f'deleting the entry must put it back: {lv(wk)}')
    log([food('Whey protein', '100g')]); log([food('Eggs', '3')]); ev("_doClearLog()")
    if (lv(wk), lv(ek)) != (750, 6): f.add('BUG', f'clearing today must put everything back: {(lv(wk), lv(ek))}')
    # edit re-applies
    reset(); log([food('Whey protein', '100g')]); eid = ev("state.todayLog[0].id")
    ev("id=>{const e=state.todayLog.find(x=>x.id===id);e.items[0].amount='50g';mhStockResync(e,todayStr());}", eid)
    if lv(wk) != 700: f.add('BUG', f'editing 100g to 50g should leave 700: {lv(wk)}')
    ev("id=>{const e=state.todayLog.find(x=>x.id===id);mhStockResync(e,todayStr());mhStockResync(e,todayStr());}", eid)
    if lv(wk) != 700: f.add('BUG', 're-applying must be idempotent')
    # paste a meal
    reset(); ev("""()=>{openPasteMealModal();document.getElementById('pasteMealDesc').value='Whey protein';document.getElementById('pasteMealAmount').value='75g';
      document.getElementById('pasteMealKcal').value='300';confirmPasteMeal();}""")
    if lv(wk) != 675: f.add('BUG', f'paste-a-meal must take stock: {lv(wk)}')
    # past day: add a day to history, log to it
    reset(); ev("""()=>{const d=new Date();d.setDate(d.getDate()-1);const ds=d.toLocaleDateString('en-CA');
      if(!state.history.find(h=>h.date===ds))state.history.unshift({date:ds,log:[],totals:{kcal:0,protein:0,fat:0,carbs:0}});window._pastDs=ds;saveState();}""")
    ds = ev("window._pastDs"); ev("k=>{const o=mhStockLoad();o.items[k].since=Date.now()-3*86400000;mhStockSave(o);}", wk)
    ev("d=>{window._logTargetDate=d}", ds); log([food('Whey protein', '50g')]); ev("window._logTargetDate=null")
    if lv(wk) != 700: f.add('BUG', f'a yesterday entry newer than the last stock-take must take stock: {lv(wk)}')
    di = ev("d=>state.history.findIndex(h=>h.date===d)", ds); ev("([i])=>{deleteHistEntry(i,0)}", [di]); page.wait_for_timeout(200)
    page.evaluate("document.getElementById('appModalConfirm')?.click()"); page.wait_for_timeout(200)
    if lv(wk) != 750: f.add('BUG', f'deleting a history entry must put it back: {lv(wk)}')
    # a day before the stock-take is already counted
    ev("k=>{const o=mhStockLoad();o.items[k].since=Date.now()+86400000;mhStockSave(o);}", wk)
    ev("d=>{window._logTargetDate=d}", ds); log([food('Whey protein', '50g')]); ev("window._logTargetDate=null")
    if lv(wk) != 750: f.add('BUG', 'food eaten before the last stock-take is already in the count and must not come off again')
    # planned meals never deduct
    reset(); ev("()=>{window._planPending={time:'18:00',date:(()=>{const d=new Date();d.setDate(d.getDate()+1);return d.toLocaleDateString('en-CA')})(),t:Date.now()}}"); log([food('Whey protein', '100g')])
    if lv(wk) != 750: f.add('BUG', f'a planned meal must never take stock: {lv(wk)}')
    if errs: f.add('BUG', f'page errors {errs[:3]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
