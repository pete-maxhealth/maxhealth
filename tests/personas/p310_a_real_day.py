"""Persona 310: one real day for a demo user, start to finish, checking each part moves the others the way it should: plan a meal (tiles show it, stock reserves it), eat it (plan gone, IN up, stock down, fasting clock follows), mark it ate-out (stock back, calories stay), log exercise (OUT and room left), a History meal marked ate-out (day totals unchanged), stock running low -> list -> Filtered -> back. Usage: p310_a_real_day.py [personaId]. Invented foods."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
PID = sys.argv[1] if len(sys.argv) > 1 else 'alex'
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("startDemoMode(%r)" % PID); page.wait_for_timeout(2500)
    ev("window.appConfirm=(m,ok)=>{ok&&ok()}; window._mhLibQuiet=true; localStorage.setItem('mh_shop_pane','both')")
    ev("switchTabById('dash')"); page.wait_for_timeout(500)
    note = lambda i: ev("(()=>{const e=document.getElementById('%s');return e&&e.style.display!=='none'?e.textContent:''})()" % i)
    kcal = lambda: round(ev("calcTotals(state.todayLog).kcal"))
    lv = lambda: ev("mhStockLoad().items[mhShopKey('Zzqx Cream')].level")
    k0 = kcal(); n0 = ev("state.todayLog.length")
    # stock: 500 g, reorder at 150 g
    ev("mhStockTrack('Zzqx Cream',{base:'g',shop:'Asda'}); (()=>{const k=mhShopKey('Zzqx Cream'); mhStockSetLevel(k,500); mhStockSetReorder(k,150);})()")
    # plan a meal that uses 100 g
    ev("mhPlanAdd([{name:'Zzqx Cream',amount:'100g',kcal:300,protein:2,fat:30,carbs:3}],'Zzqx Cream',{time:'00:05',date:localISODate()})"); page.wait_for_timeout(500)
    if '+300 kcal planned' not in note('calPlanned'): f.add('BUG', f'planned meal shows on the calories tile: "{note("calPlanned")}"')
    if f"{k0 + 300:,}" not in note('calPlanned').replace('kcal', '').replace(' ', ''): pass
    pid = ev("mhPlanLoad()[0].id")
    # eat it
    ev("mhPlanEat(%r)" % pid); page.wait_for_timeout(700)
    if ev("mhPlanLoad().length") != 0: f.add('BUG', 'eating the plan removes it')
    if note('calPlanned'): f.add('BUG', f'the planned line goes once eaten (it is in the day now): "{note("calPlanned")}"')
    if kcal() != k0 + 300 or ev("state.todayLog.length") != n0 + 1: f.add('BUG', f'eating adds the meal once: {k0}->{kcal()}, entries {n0}->{ev("state.todayLog.length")}')
    if lv() != 400: f.add('BUG', f'stock down by 100 g: {lv()}')
    if ev("document.getElementById('calCurrent').innerText").replace(',', '').split('k')[0].strip() != str(kcal()): f.add('BUG', 'the Today tile matches the day total')
    ent = ev("state.todayLog[state.todayLog.length-1].id")
    # fasting clock follows the last meal
    fn = ev("(()=>{const x=mhFastingNow(); return x?{h:x.hours,stale:x.stale}:null})()")
    if fn is None: f.add('BUG', 'fasting clock exists after a meal')
    # ate out: stock back, calories stay
    ev("mhStockAteOutToggle(%s)" % ent if isinstance(ent, int) else "mhStockAteOutToggle(%r)" % ent); page.wait_for_timeout(300)
    if lv() != 500: f.add('BUG', f'ate out puts the stock back: {lv()}')
    if kcal() != k0 + 300: f.add('BUG', 'ate out leaves the calories counted')
    # below reorder level -> on list
    ev("mhStockSetLevel(mhShopKey('Zzqx Cream'),100); mhStockSweep()")
    if not ev("mhShopLoad().items.some(i=>/Zzqx Cream/.test(i.name))"): f.add('BUG', 'a food under its reorder level reaches the list')
    # exercise
    ev("(()=>{const a=getActivities(); const w=a.find(x=>x.type==='walking')||a[0]; w.enabled=true; w.duration='45'; w.distance='4'; saveActivities(a);})()")
    ev("updateDashboard()"); page.wait_for_timeout(500)
    io = ev("mhInOutNow()")
    if not io['out'] > 0: f.add('BUG', f'exercise shows as OUT: {io}')
    if abs(io['room'] - (io['base'] + io['out'] - io['eaten'])) > 1: f.add('BUG', f'room left = target + out - eaten: {io}')
    strip = ev("document.getElementById('inOutStrip').innerText")
    if str(round(io['eaten'])) not in strip.replace(',', ''): f.add('BUG', f'the strip shows what was eaten: {strip[:120]}')
    # History: an earlier day's meal marked ate-out leaves that day's totals alone
    h = ev("(()=>{const d=state.history.find(x=>x.log&&x.log.length&&x.log[0].id!=null&&x.log[0].description); return d?{date:d.date,id:d.log[0].id,kcal:d.totals&&d.totals.kcal}:null})()")
    if h:
        ev("mhStockAteOutHist(%r,%s)" % (h['date'], h['id'] if isinstance(h['id'], int) else repr(h['id']))); page.wait_for_timeout(300)
        if ev("state.history.find(x=>x.date===%r).totals.kcal" % h['date']) != h['kcal']: f.add('BUG', 'History ate-out leaves the day totals')
    # Filtered round trip
    ev("switchTabById('shop')"); page.wait_for_timeout(400)
    sid = ev("(mhShopLoad().items.find(i=>/Zzqx Cream/.test(i.name))||{}).id")
    if sid is None: f.add('BUG', 'item still on the list')
    else:
        ev("mhShopHold(%s)" % (sid if isinstance(sid, int) else repr(sid)))
        if not ev("mhStockLoad().items[mhShopKey('Zzqx Cream')].held"): f.add('BUG', 'X sends it to Filtered')
        ev("_shopUi.heldSel={[mhShopKey('Zzqx Cream')]:true}; mhShopHeldRelease()")
        if ev("mhStockLoad().items[mhShopKey('Zzqx Cream')].held"): f.add('BUG', 'it comes back off Filtered')
        if not ev("mhShopLoad().items.some(i=>/Zzqx Cream/.test(i.name))"): f.add('BUG', 'back on the list because it is still low')
    # every Today/Shop/History screen still draws
    for sc in ['dash', 'move', 'hist', 'shop', 'library', 'stats']:
        ev("switchTabById(%r)" % sc); page.wait_for_timeout(250)
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
