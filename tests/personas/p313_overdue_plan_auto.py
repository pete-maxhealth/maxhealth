"""Persona 313: "Trust my plan" with an overdue plan from an earlier day: if that day is in History the meal is logged there at its planned time and the plan is gone; if the day is NOT in History the plan stays (nothing is lost), says why once, and auto-log leaves it alone (v3.10.1214). Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay').style.display='none'"); ev("switchTabById('dash')"); page.wait_for_timeout(400)
    plan = "mhPlanAdd([{name:'Zzqx Bar',amount:'40g',kcal:162,protein:2,fat:14,carbs:2}],'Zzqx Bar',{time:'19:00',date:localISODate(new Date(Date.now()-86400000))})"
    # 1. yesterday is not in History
    ev(plan); page.wait_for_timeout(300); ev("mhPlanSetAuto(true)"); page.wait_for_timeout(800)
    if ev("mhPlanLoad().length") != 1: f.add('BUG', 'the plan is not lost when its day is not in History')
    toasts = []
    ev("window.__t=0; const _st=window.showToast; window.showToast=function(m){ if (m) { window.__t++; } return _st&&_st.apply(this,arguments); }")
    ev("mhPlanRender(); mhPlanRender(); mhPlanRender()"); page.wait_for_timeout(300)
    if ev("window.__t") != 0: f.add('BUG', 'auto-log leaves the stuck plan alone without repeating the message: ')
    if '+162' not in ev("document.getElementById('calPlanned').textContent"): f.add('BUG', 'the planned line still shows for it')
    ev("mhPlanRemove(mhPlanLoad()[0].id)")
    # 2. yesterday is in History
    y = ev("mhPlanISOtoDMY(localISODate(new Date(Date.now()-86400000)))")
    ev("state.history.unshift({date:%r, log:[], totals:{kcal:0,protein:0,carbs:0,fat:0}}); saveState()" % y)
    ev(plan); page.wait_for_timeout(1500)
    if ev("mhPlanLoad().length") != 0: f.add('BUG', 'with the day in History the overdue plan is logged')
    d = ev("(state.history.find(h=>h.date===%r)||{log:[]}).log.map(e=>e.time+' '+e.kcal)" % y)
    if d != ['19:00 162']: f.add('BUG', f'it lands in that day at 19:00: {d}')
    if ev("state.todayLog.length") != 0: f.add('BUG', 'nothing leaks into today')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
