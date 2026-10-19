"""Persona 215: fasting handles planned meals (v3.10.1122). Pete: entering a planned meal made the fasting timer disappear and left only a
line. Fixed clock 14:00. Covers: the timer keeps running after a meal is planned; the card says what the fast would be if he eats as
planned (short of goal / goal reached / tomorrow), ignores plans under the fasting threshold, and clears when the plan goes; ticking "Ate it"
BEFORE the planned time logs it at the real time and the timer restarts from it instead of vanishing; a plan already due keeps its planned
time; a meal stamped later than now cannot blank the timer; with nothing eaten yet the plan line says it starts the next fast."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    ctx = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block', timezone_id='Europe/London')
    page = ctx.new_page(); errs = []
    page.clock.install(time='2026-10-19T14:00:00+01:00')
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.goto('http://localhost:5757/'); page.wait_for_timeout(1500); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    val = lambda: ev("document.getElementById('fastNowVal').textContent"); sub = lambda: ev("document.getElementById('fastNowSub').textContent"); line = lambda: ev("(()=>{const e=document.getElementById('fastPlanLine');return e.style.display==='none'?'':e.textContent})()")
    plan = lambda t, kcal=600, day=0, text='Steak': ev("([t,k,d,x])=>{const dt=new Date(Date.now()+d*86400000);mhPlanAdd([{name:x,amount:'200g',kcal:k,protein:50,fat:40,carbs:0}],x,{time:t,date:localISODate(dt)});}", [t, kcal, day, text])
    ev("localStorage.setItem('mh_fast_goal_h','12')") if False else None
    # nothing eaten yet
    plan('18:00'); page.wait_for_timeout(100)
    if 'starts your next fast' not in line(): f.add('BUG', f'nothing eaten yet: the plan line should say it starts the next fast: {line()!r}')
    ev("mhPlanSave([])")
    # lunch at 11:00 (3h ago)
    ev("()=>{state.todayLog=[{id:1,time:'11:00',description:'Lunch',kcal:500,protein:30,fat:30,carbs:5,items:[]}];saveState();updateDashboard();mhRenderFastingCard();}")
    if val() != '3h' or 'since your last meal at 11:00' not in sub(): f.add('BUG', f'precondition: timer from 11:00: {val()!r} {sub()!r}')
    plan('18:00'); page.wait_for_timeout(100)
    if val() != '3h': f.add('BUG', f'planning a meal must not blank the timer: {val()!r}')
    if '18:00' not in line() or '7h' not in line() or 'short of' not in line(): f.add('BUG', f'plan line: 18:00 is 7h after 11:00 and short of 12h: {line()!r}')
    ev("mhPlanSave([])"); ev("mhPlanRender()"); plan('23:30'); page.wait_for_timeout(100)
    if 'goal 12h reached' not in line() and 'reached' not in line(): f.add('BUG', f'12.5h after the last meal clears the goal: {line()!r}')
    ev("mhPlanSave([])"); ev("mhPlanRender()"); plan('08:00', 600, 1); page.wait_for_timeout(100)
    if 'tomorrow' not in line() or '21h' not in line(): f.add('BUG', f'tomorrow\'s plan: {line()!r}')
    ev("mhPlanSave([])"); ev("mhPlanRender()"); plan('18:00', 10, 0, 'Black coffee'); page.wait_for_timeout(100)
    if line(): f.add('BUG', f'a plan under the fasting threshold says nothing: {line()!r}')
    ev("mhPlanSave([])"); ev("mhPlanRender()")
    if line(): f.add('BUG', 'the line goes when the plan goes')
    # ticking Ate it early: eaten NOW
    plan('18:00'); pid = ev("mhPlanLoad()[0].id"); ev("id=>mhPlanEat(id)", pid); page.wait_for_timeout(150)
    times = ev("state.todayLog.map(e=>e.time)")
    if '18:00' in times: f.add('BUG', f'ticked at 14:00 it was eaten at 14:00, not the planned 18:00: {times}')
    if val() == '—' or 'since your last meal at 14:00' not in sub(): f.add('BUG', f'the timer restarts from the real meal, it must not vanish: {val()!r} {sub()!r}')
    # a plan that is already due keeps its planned time
    ev("()=>{state.todayLog=[{id:1,time:'08:00',description:'Breakfast',kcal:500,protein:30,fat:30,carbs:5,items:[]}];saveState();}"); ev("mhPlanSave([])")
    plan('13:00', 500, 0, 'Late lunch'); pid = ev("mhPlanLoad()[0].id"); ev("id=>mhPlanEat(id)", pid); page.wait_for_timeout(150)
    if '13:00' not in ev("state.todayLog.map(e=>e.time)"): f.add('BUG', 'a plan already due keeps its planned time when ticked')
    # a meal stamped in the future cannot blank the timer
    ev("()=>{state.todayLog=[{id:1,time:'11:00',description:'Lunch',kcal:500,protein:30,fat:30,carbs:5,items:[]},{id:2,time:'22:00',description:'Typo',kcal:500,protein:30,fat:30,carbs:5,items:[]}];saveState();updateDashboard();mhRenderFastingCard();}")
    if val() != '3h': f.add('BUG', f'a meal stamped 22:00 at 14:00 has not happened: the timer stays on 11:00: {val()!r}')
    if errs: f.add('BUG', f'page errors {errs[:3]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
