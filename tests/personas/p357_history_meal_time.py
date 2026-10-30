"""Persona 357 (v3.10.1247): a meal's time can be corrected from History, like Today's log. Both History editors (single meal, ingredient list) carry the same
Meal time row as Today's; choosing a time clears 'approximate' so the meal counts for that day's fast and the figures change; leaving it blank keeps it approximate;
Cancel is a no-op and forgets a typed time; a typed time survives the ingredient list redrawing; Today's own editors still work; the Paste-a-meal box takes an optional
time for a past day. Invented foods and days."""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 900}, service_workers='block', timezone_id='UTC')
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    p = ctx.new_page(); p.on('pageerror', lambda e: errs.append(str(e)[:200])); ev = p.evaluate
    p.goto('http://localhost:5757/'); p.wait_for_timeout(1500); ev("startDemoMode('doris')"); p.wait_for_timeout(2500)
    ev("""(()=>{
      const dmy=n=>{const d=new Date(); d.setDate(d.getDate()-n); return String(d.getDate()).padStart(2,'0')+'/'+String(d.getMonth()+1).padStart(2,'0')+'/'+String(d.getFullYear()).slice(2)};
      window.__dmy=dmy;
      const M=(id,t,desc,k,ap,items)=>({id:id,time:t,...(ap?{timeApprox:true}:{}),description:desc,amount:'1 serving',kcal:k,protein:10,fat:5,carbs:5,fibre:0,...(items?{items}:{})});
      const day=(n,log)=>({date:dmy(n),mode:'standard',notes:'',log:log,totals:{kcal:log.reduce((a,e)=>a+e.kcal,0),protein:0,fat:0,carbs:0}});
      const keep=state.history.filter(h=>![5,4,3,2].map(dmy).includes(h.date));
      state.history=[day(5,[M(9001,'08:00','Zed oats',300),M(9002,'19:30','Zed stew',500)]),
        day(4,[M(9003,'12:00','Zed cheese',200,true),M(9004,'18:00','Zed fish',400)]),
        day(3,[M(9005,'11:00','Zed pot',350,true,[{name:'Zed beef',amount:'100g',kcal:250,protein:25,fat:15,carbs:0},{name:'Zed veg',amount:'100g',kcal:100,protein:5,fat:5,carbs:6}]),M(9006,'20:00','Zed toast',300)]),
        ...keep.filter(h=>![2].map(dmy).includes(h.date))].sort((a,b)=>0);
      state.todayLog=[]; saveState();})()""")
    fast = lambda n: ev("(()=>{const m=mhFastingMap(); const v=m.get(__dmy(%d)); return v? v.fastH : null})()" % n)
    near = lambda a, b: a is not None and abs(a - b) < 0.02
    # before: day-4's 12:00 cheese is approximate and ignored, so the first counted meal is 18:00 -> fast = (24-19.5)+18
    if not near(fast(4), 22.5): f.add('BUG', f'1: before editing, the fast of day 4 ignores the approximate meal: {fast(4)}')
    ev("document.getElementById('maintab-log').click()"); p.wait_for_timeout(450); ev("document.getElementById('logtab-hist').click()"); p.wait_for_timeout(700)

    def open_day(n):
        ev("renderHistory()"); p.wait_for_timeout(300)
        i = ev("[...document.querySelectorAll('.hist-day')].findIndex(d=>d.querySelector('.hist-day-date').textContent.trim()==__dmy(%d))" % n)
        if i < 0: f.add('BUG', f'day {n} not shown in History'); return None
        ev("document.querySelectorAll('.hist-day')[%d].querySelector('.hist-day-body').classList.add('open')" % i); return i
    def tap(i, name):
        j = ev("[...document.querySelectorAll('.hist-day')[%d].querySelectorAll('.hist-entry')].findIndex(e=>e.textContent.includes(%r))" % (i, name))
        p.locator('.hist-day').nth(i).locator('.hist-entry').nth(j).locator('span[onclick*=editHistEntryByDate]').click(); p.wait_for_timeout(350)
        return ev("document.querySelectorAll('.hist-day')[%d].querySelectorAll('.hist-entry')[%d].id" % (i, j))
    tm = lambda eid: eid.replace('hist-entry-', 'edit-time-h')

    # --- single-meal editor ---
    i = open_day(4); eid = tap(i, 'Zed cheese'); t = tm(eid)
    if ev("!!document.getElementById(%r)" % t) is False: f.add('BUG', '2: History single-meal editor has the Meal time row')
    else:
        if ev("document.getElementById(%r).value" % t) != '': f.add('BUG', '3: an approximate meal shows a blank time')
        if 'ignored when working out fasts' not in ev("document.getElementById(%r).parentElement.innerText" % t): f.add('BUG', '3b: same note as Today for an approximate meal')
        # Save without choosing: still approximate
        ev("saveHistEntry(%s,%s)" % tuple(eid.replace('hist-entry-', '').split('-'))); p.wait_for_timeout(300)
        if not ev("state.history.find(h=>h.date===__dmy(4)).log[0].timeApprox"): f.add('BUG', '4: saving without a time leaves it approximate')
        # choose a time
        i = open_day(4); eid = tap(i, 'Zed cheese'); t = tm(eid)
        p.fill('#' + t, '09:00'); ev("saveHistEntry(%s,%s)" % tuple(eid.replace('hist-entry-', '').split('-'))); p.wait_for_timeout(400)
        e = ev("state.history.find(h=>h.date===__dmy(4)).log[0]")
        if e['time'] != '09:00' or e.get('timeApprox'): f.add('BUG', f'5: chosen time applied and flag cleared: {e["time"]} {e.get("timeApprox")}')
        if not near(fast(4), 13.5): f.add('BUG', f'6: the fast of day 4 now counts the 09:00 meal ((24-19.5)+9 = 13.5): {fast(4)}')
        # the day shown in History / Today's fasting card read the same
        ev("switchTab('today')"); p.wait_for_timeout(500)
        if not near(fast(4), 13.5): f.add('BUG', '7: still 13.5 after going to Today')
        ev("document.getElementById('maintab-log').click()"); p.wait_for_timeout(300); ev("document.getElementById('logtab-hist').click()"); p.wait_for_timeout(500)
    # Cancel is a no-op and forgets a typed time
    i = open_day(4); eid = tap(i, 'Zed fish'); t = tm(eid); key = eid.replace('hist-entry-', '')
    p.fill('#' + t, '23:30'); ev("cancelHistEdit(%r)" % key); p.wait_for_timeout(200)
    if ev("state.history.find(h=>h.date===__dmy(4)).log.find(x=>x.description==='Zed fish').time") != '18:00': f.add('BUG', '8: Cancel must not change the time')
    i = open_day(4); eid = tap(i, 'Zed fish'); t = tm(eid)
    if ev("document.getElementById(%r).value" % t) != '18:00': f.add('BUG', '9: a cancelled time must not come back when the editor is reopened')
    ev("cancelHistEdit(%r)" % eid.replace('hist-entry-', ''))

    # --- ingredient-list editor ---
    i = open_day(3); eid = tap(i, 'Zed pot'); t = tm(eid); key = eid.replace('hist-entry-', '')
    if not ev("!!document.getElementById(%r)" % t): f.add('BUG', '10: History ingredient editor has the Meal time row')
    else:
        p.fill('#' + t, '10:15')
        ev("renderHistEditItemsForm(%s,%s,state.history[%s].log[%s])" % (*key.split('-'), key.split('-')[0], key.split('-')[1])); p.wait_for_timeout(300)
        if ev("document.getElementById(%r).value" % t) != '10:15': f.add('BUG', '11: a typed time survives the ingredient list redrawing')
        ev("saveHistEditItems(%s,%s)" % tuple(key.split('-'))); p.wait_for_timeout(400)
        e = ev("state.history.find(h=>h.date===__dmy(3)).log.find(x=>x.description==='Zed pot')")
        if e['time'] != '10:15' or e.get('timeApprox'): f.add('BUG', f'12: ingredient editor applies the time: {e["time"]} {e.get("timeApprox")}')
        if e['kcal'] != 350 or len(e['items']) != 2: f.add('BUG', '13: the ingredients and totals are untouched by a time change')
    # uniformity: same row markup as Today's
    ev("state.todayLog=[{id:9100,time:'12:00',description:'Zed lunch',amount:'1 serving',kcal:100,protein:5,fat:5,carbs:5}]; saveState(); updateDashboard(); editLogEntry(9100)"); p.wait_for_timeout(300)
    today_row = ev("(()=>{const r=document.getElementById('edit-time-9100'); return r? r.parentElement.querySelector('span').textContent+'|'+r.className+'|'+r.getAttribute('style') : ''})()")
    i = open_day(4); eid = tap(i, 'Zed fish'); t = tm(eid)
    hist_row = ev("(()=>{const r=document.getElementById(%r); return r? r.parentElement.querySelector('span').textContent+'|'+r.className+'|'+r.getAttribute('style') : ''})()" % t)
    if not today_row or today_row != hist_row: f.add('BUG', f'14: the Meal time row looks and reads the same in Today and History: {today_row!r} vs {hist_row!r}')
    ev("cancelHistEdit(%r)" % eid.replace('hist-entry-', ''))
    # Today's own editor still saves its time (neighbour)
    ev("switchTab('today')"); p.wait_for_timeout(500); ev("document.getElementById('log-entry-9100') && !document.querySelector('#log-entry-9100 .log-edit-form') && editLogEntry(9100)"); p.wait_for_timeout(300)
    p.fill('#edit-time-9100', '12:45'); ev("saveLogEdit(9100)"); p.wait_for_timeout(300)
    if ev("state.todayLog[0].time") != '12:45': f.add('BUG', "15: Today's editor still applies the time")

    # --- Paste a meal onto a past day ---
    def paste(d, time):
        ev("openPasteMealModal()"); p.wait_for_timeout(200)
        ev("document.getElementById('pasteMealDesc').value='Zed paste'; document.getElementById('pasteMealKcal').value='100'; document.getElementById('pasteMealDate').value=%r; document.getElementById('pasteMealTime').value=%r" % (d, time))
        ev("confirmPasteMeal()"); p.wait_for_timeout(300)
    d5 = ev("__dmy(5)")
    paste(d5, '16:20')
    e = ev("state.history.find(h=>h.date===__dmy(5)).log.find(x=>x.description==='Zed paste')")
    if not e or e['time'] != '16:20' or e.get('timeApprox'): f.add('BUG', f'16: pasting onto a past day with a time keeps the time: {e}')
    ev("state.history.find(h=>h.date===__dmy(5)).log=state.history.find(h=>h.date===__dmy(5)).log.filter(x=>x.description!=='Zed paste')")
    paste(d5, '')
    e = ev("state.history.find(h=>h.date===__dmy(5)).log.find(x=>x.description==='Zed paste')")
    if not e or not e.get('timeApprox'): f.add('BUG', f'17: pasting onto a past day with no time stays approximate (as before): {e}')
    if ev("document.getElementById('pasteMealTime').value") != '': f.add('BUG', '18: the time box is empty each time the box opens') if False else None
    ev("openPasteMealModal()"); p.wait_for_timeout(200)
    if ev("document.getElementById('pasteMealTime').value") != '': f.add('BUG', '18: the time box starts empty each time the box opens')
    if errs: f.add('JS-exception', errs[0])
    b.close()
bad = any(s in ('BUG', 'JS-exception') for s, _ in f)
for s, m in f: print(s, m)
print('BUGS' if bad else 'OK', len(f)); sys.exit(1 if bad else 0)
