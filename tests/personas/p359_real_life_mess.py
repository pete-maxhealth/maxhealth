"""Persona 359 (v3.10.1248): real-life mess. A "Missed day" entry for a day that already has meals adds to them (it used to overwrite the day's totals and tags while leaving the meals, so the day
disagreed with its own list); for a day that is itself a missed-day entry it replaces it and stays consistent; a brand-new missed day still works; the added entry is visible, editable and
deletable, and totals follow. Also: a junk amount does not crash an edit, double Save does not double a meal, a reload in the middle of an edit leaves the day intact, and deleting the last meal of a day
leaves a sensible day. Invented data."""
import sys, re, json; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 900}, service_workers='block', timezone_id='UTC')
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    p = ctx.new_page(); p.on('pageerror', lambda e: errs.append(str(e)[:200])); p.on('dialog', lambda d: d.accept()); ev = p.evaluate
    p.goto('http://localhost:5757/'); p.wait_for_timeout(1500); ev("state.onboarded=true; saveState()"); p.reload(); p.wait_for_timeout(2000)
    ev("""(()=>{const dmy=n=>{const d=new Date(); d.setDate(d.getDate()-n); return String(d.getDate()).padStart(2,'0')+'/'+String(d.getMonth()+1).padStart(2,'0')+'/'+String(d.getFullYear()).slice(2)}; window.__dmy=dmy;
      const M=(id,t,desc,k)=>({id:id,time:t,description:desc,amount:'1 serving',kcal:k,protein:20,fat:10,carbs:8,fibre:1});
      const sum=log=>log.reduce((a,e)=>({kcal:a.kcal+e.kcal,protein:a.protein+e.protein,fat:a.fat+e.fat,carbs:a.carbs+e.carbs}),{kcal:0,protein:0,fat:0,carbs:0});
      const L3=[M(7001,'08:00','Zed oats',380),M(7002,'13:00','Zed salmon plate',312)];
      state.history=[{date:dmy(3),mode:'standard',notes:'Illness',log:L3,totals:sum(L3)},
        {date:dmy(5),mode:'standard',notes:'missed day entry',log:[{id:7003,time:'23:59',description:'missed day entry',kcal:1800,protein:100,carbs:60,fat:0,fibre:0,polyols:0}],totals:{kcal:1800,protein:100,carbs:60,fat:0}}];
      state.todayLog=[]; saveState();})()""")
    ev("window.appConfirm=(m,yes)=>yes(); 0")   # the app's own confirm box answers yes
    day = lambda n: ev("state.history.find(h=>h.date===__dmy(%d))" % n)
    miss = lambda n, k, pr, c, note='': ev("openMissedDayModal(__dmy(%d)); setMissedMode('manual'); document.getElementById('missedKcal').value=%r; document.getElementById('missedProtein').value=%r; document.getElementById('missedCarbs').value=%r; document.getElementById('missedNotes').value=%r; saveMissedDay()" % (n, k, pr, c, note))
    # 1. a day with meals: the numbers are ADDED, tags and meals stay, totals match the list
    d = day(3); before = d['totals']['kcal']; miss(3, '500', '30', '20'); p.wait_for_timeout(300); d = day(3)
    if d['totals']['kcal'] != before + 500: f.add('BUG', f'1: a missed-day entry on a day with meals adds to the total ({before}+500): {d["totals"]}')
    if len(d['log']) != 3 or sum(e['kcal'] for e in d['log']) != d['totals']['kcal']: f.add('BUG', f'2: the day total equals its list: {d["totals"]["kcal"]} vs {sum(e["kcal"] for e in d["log"])}')
    if d.get('notes') != 'Illness': f.add('BUG', f'3: the day keeps its tags: {d.get("notes")}')
    if [e['description'] for e in d['log']][:2] != ['Zed oats', 'Zed salmon plate']: f.add('BUG', '4: the original meals are untouched')
    # visible in History, and can be deleted: totals follow
    ev("document.getElementById('maintab-log').click()"); p.wait_for_timeout(400); ev("document.getElementById('logtab-hist').click()"); p.wait_for_timeout(700)
    i = ev("[...document.querySelectorAll('.hist-day')].findIndex(x=>x.querySelector('.hist-day-date').textContent.trim()==__dmy(3))")
    ev("document.querySelectorAll('.hist-day')[%d].querySelector('.hist-day-body').classList.add('open')" % i)
    txt = ev("document.querySelectorAll('.hist-day')[%d].innerText" % i)
    if 'Missed meals added later' not in txt: f.add('BUG', '5: the added entry is visible in the day list')
    ev("deleteHistEntryByDate(__dmy(3), 2)"); p.wait_for_timeout(400)
    d = day(3)
    if d['totals']['kcal'] != before or len(d['log']) != 2: f.add('BUG', f'6: deleting the added entry puts the day back: {d["totals"]["kcal"]} / {len(d["log"])}')
    # 2. a day that is itself a missed-day entry: replaced, consistent
    miss(5, '2000', '110', '70'); p.wait_for_timeout(300); d = day(5)
    if d['totals']['kcal'] != 2000 or len(d['log']) != 1 or d['log'][0]['kcal'] != 2000: f.add('BUG', f'7: re-entering a missed day replaces it and keeps the list in step: {d["totals"]} {[e["kcal"] for e in d["log"]]}')
    # 3. a brand-new missed day still works
    ev("state.history=state.history.filter(h=>h.date!==__dmy(7)); 0"); miss(7, '1700', '90', '50', 'Zed holiday'); p.wait_for_timeout(300)
    d = day(7)
    if not d or d['totals']['kcal'] != 1700 or len(d['log']) != 1: f.add('BUG', f'8: a new missed day is added: {d}')
    # 4. real-life mess in an edit
    ev("document.getElementById('maintab-log').click()"); p.wait_for_timeout(300); ev("document.getElementById('logtab-hist').click()"); p.wait_for_timeout(500)
    i = ev("[...document.querySelectorAll('.hist-day')].findIndex(x=>x.querySelector('.hist-day-date').textContent.trim()==__dmy(3))")
    ev("document.querySelectorAll('.hist-day')[%d].querySelector('.hist-day-body').classList.add('open')" % i)
    p.locator('.hist-day').nth(i).locator('.hist-entry').first.locator('span[onclick*=editHistEntryByDate]').click(); p.wait_for_timeout(300)
    # reload with the editor open: the day must be exactly as it was (nothing half-saved)
    snap = json.dumps(day(3)); p.reload(); p.wait_for_timeout(2500)
    ev("window.__dmy=n=>{const d=new Date(); d.setDate(d.getDate()-n); return String(d.getDate()).padStart(2,'0')+'/'+String(d.getMonth()+1).padStart(2,'0')+'/'+String(d.getFullYear()).slice(2)}; window.appConfirm=(m,yes)=>yes(); 0")
    if json.dumps(day(3)) != snap: f.add('BUG', '9: a reload in the middle of an edit leaves the day exactly as it was')
    # junk kcal in a single-meal editor: saved as a number or refused, never NaN
    ev("document.getElementById('maintab-log').click()"); p.wait_for_timeout(300); ev("document.getElementById('logtab-hist').click()"); p.wait_for_timeout(500)
    i = ev("[...document.querySelectorAll('.hist-day')].findIndex(x=>x.querySelector('.hist-day-date').textContent.trim()==__dmy(3))")
    ev("document.querySelectorAll('.hist-day')[%d].querySelector('.hist-day-body').classList.add('open')" % i)
    eid = ev("document.querySelectorAll('.hist-day')[%d].querySelectorAll('.hist-entry')[0].id" % i); key = eid.replace('hist-entry-', '')
    p.locator('.hist-day').nth(i).locator('.hist-entry').first.locator('span[onclick*=editHistEntryByDate]').click(); p.wait_for_timeout(300)
    if ev("!!document.getElementById('hedit-kcal-%s')" % key):
        k0 = day(3)['log'][0]['kcal']
        ev("document.getElementById('hedit-kcal-%s').value=''" % key); ev("saveHistEntry(%s,%s)" % tuple(key.split('-'))); p.wait_for_timeout(300)   # a number box cannot hold letters; empty is the junk it can hold
        k = day(3)['log'][0]['kcal']
        if k != k0 or not isinstance(k, (int, float)) or k != k: f.add('BUG', f'10: an empty calorie box is refused, never NaN or zero: {k0} -> {k}')
    # double save of the same edit does not duplicate the meal
    n = len(day(3)['log']); ev("saveHistEntry(%s,%s); saveHistEntry(%s,%s)" % (*key.split('-'), *key.split('-'))); p.wait_for_timeout(300)
    if len(day(3)['log']) != n: f.add('BUG', '11: saving twice does not add a meal')
    # delete every meal of a day: the day stays sensible and History still draws
    ev("(()=>{const d=state.history.find(h=>h.date===__dmy(3)); while(d.log.length) deleteHistEntry(state.history.indexOf(d),0);})()"); p.wait_for_timeout(500)
    d = day(3)
    if d and (d['totals']['kcal'] or 0) != 0: f.add('BUG', f'12: a day with every meal deleted totals zero: {d["totals"]}')
    ev("renderHistory()"); p.wait_for_timeout(300)
    if errs: f.add('JS-exception', errs[0])
    b.close()
bad = any(s in ('BUG', 'JS-exception') for s, _ in f)
for s, m in f: print(s, m)
print('BUGS' if bad else 'OK', len(f)); sys.exit(1 if bad else 0)
