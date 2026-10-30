"""Persona 358 (v3.10.1247): the whole journey, offline throughout, invented person. Device A is a brand-new install: the first-run wizard appears, is filled in and finishes, and does not
come back after a reload. A week of use: library, a recipe, meals logged today, water, a past day corrected from History, a shopping list with a ticked item and counted stock. A backup file
is taken. Device B is a second brand-new install: the backup is restored through the app's own file box and the confirmation, and everything matches. Then the app is switched off piece by
piece (every Today card hidden, cupboards turned off) and must still work, keep everything, and come back exactly when switched on again."""
import sys, re, json, os, tempfile; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
bk = os.path.join(tempfile.gettempdir(), 'p358_backup.json')
DIGEST = """(()=>{const L=JSON.parse(localStorage.getItem('mh_shopping_v1')||'{}');
  return JSON.stringify({name:localStorage.getItem('mh_name'),age:localStorage.getItem('mh_age'),height:localStorage.getItem('mh_height_cm'),sex:localStorage.getItem('mh_sex'),
   weight:state.weight,onboarded:!!state.onboarded,
   hist:state.history.slice().sort((a,b)=>String(a.date.split('/').reverse().join('')).localeCompare(b.date.split('/').reverse().join(''))).map(d=>[d.date,(d.totals||{}).kcal,(d.log||[]).length,(d.log||[]).map(e=>e.description+'@'+e.time+(e.timeApprox?'~':'')).join('|')]),
   today:(state.todayLog||[]).map(e=>e.description+'@'+e.kcal), lib:loadLibrary().map(x=>x.name).sort(), rec:loadRecipes().map(x=>x.name).sort(),
   shop:(L.items||[]).map(i=>[i.name,!!i.checked]), water:state.waterToday||state.water||null})})()"""

def new_page(pw, offline=True):
    b = pw.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 900}, service_workers='block', timezone_id='UTC', accept_downloads=True)
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort()); errs = []
    p = ctx.new_page(); p.on('pageerror', lambda e: errs.append(str(e)[:200])); p.on('dialog', lambda d: d.accept())
    return b, p, errs

with fresh_server() as root, sync_playwright() as pw:
    # ============ DEVICE A: brand-new install ============
    b, p, errs = new_page(pw); ev = p.evaluate
    p.goto('http://localhost:5757/'); p.wait_for_timeout(3000)
    if ev("getComputedStyle(document.getElementById('onboardingOverlay')).display") != 'block': f.add('BUG', 'A1: a brand-new install shows the first-run wizard')
    ev("onboardNext(2)"); p.fill('#onboardName', 'Zed Tester'); ev("onboardNext(3)")
    p.fill('#onboardAge', '52'); p.fill('#onboardHeight', '178'); p.fill('#onboardWeight', '84.5'); ev("obSetSex('male')"); ev("onboardNext(4)"); p.wait_for_timeout(300)
    ev("onboardNext(5)"); ev("onboardNext('5b')"); ev("obSetStart('everything')"); ev("onboardNext(6)"); ev("onboardFinish()"); p.wait_for_timeout(2500)
    if ev("getComputedStyle(document.getElementById('onboardingOverlay')).display") == 'block': f.add('BUG', 'A2: the wizard closes when finished')
    got = ev("[localStorage.getItem('mh_name'),localStorage.getItem('mh_age'),localStorage.getItem('mh_height_cm'),localStorage.getItem('mh_sex'),state.weight]")
    if got != ['Zed Tester', '52', '178', 'male', 84.5]: f.add('BUG', f'A3: wizard answers saved (name, age, height, sex, weight): {got}')
    p.reload(); p.wait_for_timeout(2500)
    if ev("getComputedStyle(document.getElementById('onboardingOverlay')).display") == 'block': f.add('BUG', 'A4: the wizard must not come back after a reload')
    # ---- a week of use
    ev("""(()=>{saveLibrary([{id:'z1',name:'Zed oats',kcal:380,protein:13,carbs:60,fat:7,portion:'50g',useCount:3},{id:'z2',name:'Zed eggs',kcal:143,protein:13,carbs:1,fat:10,portion:'100g',useCount:5},
        {id:'z3',name:'Zed salmon',kcal:208,protein:20,carbs:0,fat:13,portion:'100g',useCount:2}]);
      localStorage.setItem('mh_recipes', JSON.stringify([{id:'zr1',name:'Zed salmon plate',servings:1,ingredients:[{name:'Zed salmon',amount:150,unit:'g',kcal:312,protein:30,fat:19.5,carbs:0}]}]));})()""")
    ev("""(()=>{const dmy=n=>{const d=new Date(); d.setDate(d.getDate()-n); return String(d.getDate()).padStart(2,'0')+'/'+String(d.getMonth()+1).padStart(2,'0')+'/'+String(d.getFullYear()).slice(2)};
      window.__dmy=dmy; const M=(id,t,desc,k,ap)=>({id:id,time:t,...(ap?{timeApprox:true}:{}),description:desc,amount:'1 serving',kcal:k,protein:20,fat:10,carbs:8,fibre:2});
      const day=(n,log)=>({date:dmy(n),mode:'standard',notes:'',log:log,totals:{kcal:log.reduce((a,e)=>a+e.kcal,0),protein:log.length*20,fat:log.length*10,carbs:log.length*8}});
      state.history=[6,5,4,3,2,1].map(n=>day(n,[M(8000+n*10,'08:00','Zed oats',380),M(8001+n*10,'13:00','Zed salmon plate',312),M(8002+n*10,'19:00','Zed eggs',286)]));
      state.history[2].log[1].time='12:00'; state.history[2].log[1].timeApprox=true;   // a meal added later to a past day: no real time (this one is corrected from History below)
      state.history[4].log[2].timeApprox=true;                                          // and one that stays unknown
      state.history.forEach(d=>{d.totals=d.log.reduce((a,e)=>({kcal:a.kcal+e.kcal,protein:a.protein+e.protein,fat:a.fat+e.fat,carbs:a.carbs+e.carbs}),{kcal:0,protein:0,fat:0,carbs:0})});
      state.todayLog=[]; saveState();})()""")
    ev("logFoods([{name:'Zed oats',amount:'50g',kcal:380,protein:13,carbs:60,fat:7,fibre:0}],'Zed oats')"); p.wait_for_timeout(300)
    ev("logFoods([{name:'Zed eggs',amount:'100g',kcal:143,protein:13,carbs:1,fat:10,fibre:0}],'Zed eggs')"); p.wait_for_timeout(300)
    ev("logWater(500); logWater(250)"); p.wait_for_timeout(200)
    if len(ev("state.todayLog")) != 2: f.add('BUG', f'B1: two meals logged today: {len(ev("state.todayLog"))}')
    # a past meal's time corrected from History (the v3.10.1247 route), by a real tap
    ev("document.getElementById('maintab-log').click()"); p.wait_for_timeout(400); ev("document.getElementById('logtab-hist').click()"); p.wait_for_timeout(700)
    i = ev("[...document.querySelectorAll('.hist-day')].findIndex(d=>d.querySelector('.hist-day-date').textContent.trim()==__dmy(4))")
    ev("document.querySelectorAll('.hist-day')[%d].querySelector('.hist-day-body').classList.add('open')" % i)
    j = ev("[...document.querySelectorAll('.hist-day')[%d].querySelectorAll('.hist-entry')].findIndex(e=>e.textContent.includes('Zed salmon plate'))" % i)
    p.locator('.hist-day').nth(i).locator('.hist-entry').nth(j).locator('span[onclick*=editHistEntryByDate]').click(); p.wait_for_timeout(350)
    tid = ev("document.querySelectorAll('.hist-day')[%d].querySelectorAll('.hist-entry')[%d].querySelector('input[type=time]').id" % (i, j))
    p.fill('#' + tid, '12:30'); ev("[...document.querySelectorAll('.hist-day')[%d].querySelectorAll('.hist-entry')[%d].querySelectorAll('button')].find(b=>/^Save/.test(b.textContent.trim())).click()" % (i, j)); p.wait_for_timeout(500)
    if ev("state.history.find(d=>d.date===__dmy(4)).log[1].time") != '12:30': f.add('BUG', 'B2: the corrected past-meal time is kept')
    # shopping: list, tick, stock
    ev("""(()=>{const s=mhShopLoad(); mhShopSetAdd(s,'Zed milk','own','', 'dairy'); mhShopSetAdd(s,'Zed apples','own','', 'fruit'); mhShopSetAdd(s,'Zed bread','own','', 'bread'); mhShopSave(s);
      const t=mhShopLoad(); const it=t.items.find(x=>x.name==='Zed apples'); if(it) it.checked=true; mhShopSave(t);})()""")
    shop = ev("mhShopLoad().items.map(i=>[i.name,!!i.checked])")
    if ['Zed apples', True] not in shop or len(shop) < 3: f.add('BUG', f'B3: shopping list has three items with one ticked: {shop}')
    ev("switchTab('today')"); p.wait_for_timeout(600); ev("updateDashboard(true)")
    before = ev(DIGEST)
    payload = ev("JSON.stringify(buildFullBackupPayload())")
    open(bk, 'w').write(payload)
    if errs: f.add('JS-exception', 'A: ' + errs[0])
    b.close()

    # ============ DEVICE B: second brand-new install, restore through the file box ============
    b, p, errs = new_page(pw); ev = p.evaluate
    p.goto('http://localhost:5757/'); p.wait_for_timeout(3000)
    if ev("getComputedStyle(document.getElementById('onboardingOverlay')).display") != 'block': f.add('BUG', 'C1: device B starts as a brand-new install')
    ev("document.getElementById('onboardingOverlay').style.display='none'")
    ev("switchTab('settings'); switchSubTab('settings','data')"); p.wait_for_timeout(700)
    p.set_input_files('#restoreFileInput', bk); p.wait_for_timeout(800)
    if not ev("!!document.getElementById('restoreConfirmModal')"): f.add('BUG', 'C2: choosing a backup file asks first (Replace all current data?)')
    else:
        with p.expect_navigation(timeout=15000): ev("document.getElementById('mhRestoreYes').click()")
        p.wait_for_timeout(3000)
    if ev("getComputedStyle(document.getElementById('onboardingOverlay')).display") == 'block': f.add('BUG', 'C3: after a restore the wizard must not appear')
    after = ev(DIGEST)
    if after != before:
        a, bb = json.loads(before), json.loads(after)
        for k in a:
            if a[k] != bb.get(k): f.add('BUG', f'C4: after the restore, {k} differs: {str(a[k])[:140]} vs {str(bb.get(k))[:140]}')
    # the approximate meal is still approximate after a round trip, the corrected one is not
    appr = ev("state.history.map(d=>d.log.filter(e=>e.timeApprox).length).reduce((a,b)=>a+b,0)")
    if appr != 1: f.add('BUG', f'C5: exactly one meal is still "time unknown" after the restore: {appr}')
    # the screens draw from the restored data
    ev("switchTab('today')"); p.wait_for_timeout(700)
    if '380' not in ev("document.body.innerText") and 'kcal' not in ev("document.body.innerText"): f.add('BUG', 'C6: Today draws after the restore')
    ev("document.getElementById('maintab-log').click()"); p.wait_for_timeout(400); ev("document.getElementById('logtab-hist').click()"); p.wait_for_timeout(700)
    if ev("document.querySelectorAll('.hist-day').length") < 6: f.add('BUG', 'C7: History shows the restored days')

    # ============ switching it off, piece by piece ============
    ev("switchTab('today')"); p.wait_for_timeout(500)
    keys = ev("DEFAULT_DASHBOARD_ORDER.slice()")
    ev("localStorage.setItem('mh_dashboard_hidden', JSON.stringify(%s)); mhStockSetOn(false)" % json.dumps(keys)); p.reload(); p.wait_for_timeout(2500)
    vis = ev("Object.entries(DASHBOARD_SECTION_IDS).filter(([k,ids])=>ids.some(id=>{const e=document.getElementById(id); return e && e.offsetParent!==null})).map(([k])=>k)")
    if vis: f.add('BUG', f'D1: every Today card hidden, but these still show: {vis}')
    if ev("mhStockOn()"): f.add('BUG', 'D2: cupboards & stock is off')
    ev("logFoods([{name:'Zed eggs',amount:'100g',kcal:143,protein:13,carbs:1,fat:10,fibre:0}],'Zed eggs again')"); p.wait_for_timeout(400)
    if len(ev("state.todayLog")) != 3: f.add('BUG', 'D3: logging still works with every card hidden')
    if ev(DIGEST).count('Zed') < 10: f.add('BUG', 'D4: nothing was lost by hiding things')
    ev("document.getElementById('maintab-log').click()"); p.wait_for_timeout(400); ev("document.getElementById('logtab-hist').click()"); p.wait_for_timeout(600)
    if ev("document.querySelectorAll('.hist-day').length") < 6: f.add('BUG', 'D5: History still shows everything while the cards are hidden')
    # back on
    ev("localStorage.removeItem('mh_dashboard_hidden'); mhStockSetOn(true)"); p.reload(); p.wait_for_timeout(2500)
    shown = ev("Object.entries(DASHBOARD_SECTION_IDS).filter(([k,ids])=>ids.some(id=>{const e=document.getElementById(id); return e && e.offsetParent!==null})).length")
    if shown < 6: f.add('BUG', f'D6: switching back on brings the cards back (shown: {shown})')
    if not ev("mhStockOn()"): f.add('BUG', 'D7: cupboards & stock is on again')
    if [i for i in ev("mhShopLoad().items.map(i=>[i.name,!!i.checked])")] != json.loads(before)['shop']: f.add('BUG', 'D8: the shopping list is exactly as it was')
    if errs: f.add('JS-exception', 'B: ' + errs[0])
    b.close()
bad = any(s in ('BUG', 'JS-exception') for s, _ in f)
for s, m in f: print(s, m)
print('BUGS' if bad else 'OK', len(f)); sys.exit(1 if bad else 0)
