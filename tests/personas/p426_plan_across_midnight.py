"""Persona 426: a plan for 23:50 last night with "Trust my plan" on. Opened the next morning, the app checks the plan before it moves yesterday into History; that used to park the plan for good ("could not find the day") although the day arrived a moment later. Expect: the meal lands in yesterday at 23:50, the plan is gone, nothing leaks into today; a plan already parked that way is picked up once its day exists."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay').style.display='none'"); ev("switchTabById('dash')"); page.wait_for_timeout(400)
    y = ev("mhPlanISOtoDMY(localISODate(new Date(Date.now()-86400000)))")
    def setup():
        ev("localStorage.removeItem('mh_planned_v1'); state.history=[]; state.todayLog=[]")
        # yesterday still open in Today (as it is when the app was last used last night)
        ev("state.lastDate=%r; state.todayLog=[{name:'Zzqx Eggs',amount:'2',kcal:140,protein:12,fat:10,carbs:1,time:'20:00'}]; saveState()" % y)
        ev("mhPlanAdd([{name:'Double cream',amount:'50ml',kcal:200,protein:1,fat:21,carbs:1},{name:'Whey',amount:'30g',kcal:120,protein:24,fat:2,carbs:2}],'double cream and whey',{time:'23:50',date:localISODate(new Date(Date.now()-86400000))})")
        ev("mhPlanSetAuto(true)")
    # 1. first open of the new day
    setup(); ev("updateDashboard()"); page.wait_for_timeout(1500); ev("updateDashboard()"); page.wait_for_timeout(800)
    if ev("mhPlanLoad().length") != 0: f.add('BUG', f"plan still waiting after the new day opened: {ev('JSON.stringify(mhPlanLoad().map(p=>[p.time,p.noAuto]))')}")
    d = ev("(state.history.find(h=>h.date===%r)||{log:[]}).log.map(e=>e.time+' '+e.name)" % y)
    if not any(x.startswith('23:50') for x in d): f.add('BUG', f'the planned meal lands in yesterday at 23:50: {d}')
    if not any('Zzqx' in x for x in d): f.add('BUG', f'yesterday keeps what was already eaten: {d}')
    if ev("state.todayLog.length") != 0: f.add('BUG', 'nothing leaks into today')
    # 2. a plan already parked (noAuto) before the day existed is retried once the day is there
    ev("localStorage.removeItem('mh_planned_v1'); state.history=state.history.filter(h=>h.date!==%r); mhPlanSetAuto(false)" % y)
    ev("mhPlanAdd([{name:'Whey',amount:'30g',kcal:120,protein:24,fat:2,carbs:2}],'whey',{time:'23:50',date:localISODate(new Date(Date.now()-86400000))}); const a=mhPlanLoad(); a[0].noAuto=true; mhPlanSave(a)")
    ev("mhPlanSetAuto(true)"); page.wait_for_timeout(300)
    if ev("mhPlanLoad().length") != 1: f.add('BUG', 'with the day missing the parked plan stays')
    ev("state.history.unshift({date:%r, log:[], totals:{kcal:0,protein:0,carbs:0,fat:0}}); saveState(); mhPlanRender()" % y); page.wait_for_timeout(800)
    if ev("mhPlanLoad().length") != 0: f.add('BUG', 'a parked plan is logged once its day is in History')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
