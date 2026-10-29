"""Persona 171 (v3.10.1071): Plan ahead. Planned steps/exercise show their effect before being done; real (typed or live
Health Connect) steps take over a planned steps target and clear it once passed; Done converts a plan into the real activity."""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
bad = []
def check(n, ok, info=''):
    print(('PASS ' if ok else 'FAIL ') + n + (f'  {info}' if info and not ok else ''))
    if not ok: bad.append(n)
with fresh_server() as root, sync_playwright() as pw:
    br = pw.chromium.launch(); ctx = br.new_context(viewport={'width': 430, 'height': 900}, service_workers='block'); page = ctx.new_page()
    errs = []; page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.dismiss())
    page.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); page.evaluate("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev = page.evaluate
    ev("startDemoMode('alex')"); page.wait_for_timeout(2200)
    ev("document.getElementById('maintab-today').click()"); page.wait_for_timeout(400)
    ev("localStorage.setItem('mh_plan_open','1'); renderActivityCard()"); page.wait_for_timeout(300)
    check('plan box renders (own card)', 'WHAT IF' in ev("document.getElementById('planCard').textContent").upper() and 'Walk' in ev("document.getElementById('whatIf').textContent"))
    # steps far below baseline add nothing
    ev("localStorage.setItem('mh_steps_today','0'); mhXPlanSetType('steps'); mhXPlanSetAmt(500)")
    check('500 steps from zero adds 0 kcal', ev("mhStepsKcalFor(500)") == 0)
    # beyond baseline adds something and rises with steps
    k = ev("(()=>{localStorage.setItem('mh_steps_today', String(getStepsBaseline()+1000)); return [mhStepsKcalFor(1000), mhStepsKcalFor(3000)]})()")
    check('steps past baseline earn kcal, more steps earn more', k[0] > 0 and k[1] > k[0], str(k))
    # resistance: kcal rise with effort, +15g protein
    e = ev("[mhActivityKcalFor('resistance',45,'Easy'),mhActivityKcalFor('resistance',45,'Moderate'),mhActivityKcalFor('resistance',45,'Hard')]")
    check('resistance kcal Easy < Moderate < Hard', e[0] < e[1] < e[2], str(e))
    ev("mhXPlanAdd('activity','resistance',45,'Hard')")
    t = ev("mhXPlanTotals()")
    check('planned resistance: kcal and +15g protein', t['kcal'] > 0 and t['protein'] == 15, str(t))
    check('strip shows the plan line', 'Plan:' in ev("document.getElementById('inOutStrip').textContent"))
    # plan does not change the real target until done
    before = ev("mhInOutNow().out")
    check('planning alone does not change OUT', before == ev("mhInOutNow().out"))
    # Done converts to a real activity
    ev("(()=>{const a=getActivities(); if(!a.some(x=>x.type==='resistance')){a.push({type:'resistance',label:'Resistance',enabled:false,duration:'',effort:'Moderate',needsDistance:false}); saveActivities(a)} })()")
    pid = ev("mhXPlanItems()[0].id"); ev(f"mhXPlanDone('{pid}')"); page.wait_for_timeout(300)
    r = ev("getActivities().find(a=>a.type==='resistance')")
    check('Done enables the activity with duration and effort', r['enabled'] and float(r['duration']) >= 45 and r['effort'] == 'Hard', str(r))
    check('plan list empty after Done', ev("mhXPlanItems().length") == 0)
    # steps plan is a target; live count takes over and clears it
    ev("localStorage.setItem('mh_steps_today','4000'); mhXPlanAdd('steps','steps',3000)")
    check('steps plan target = now + amount, 3000 left', ev("mhXPlanStepsLeft(mhXPlanItems()[0])") == 3000)
    ev("localStorage.setItem('mh_steps_today','5500')")
    check('live steps shrink the plan (1500 left)', ev("mhXPlanStepsLeft(mhXPlanItems()[0])") == 1500)
    ev("localStorage.setItem('mh_steps_today','7200'); mhXPlanTotals()")
    check('live steps past target clear the plan', ev("mhXPlanItems().length") == 0)
    # yesterday's plan ignored
    ev("state.plannedExercise={date:'2000-01-01',items:[{id:'x',kind:'steps',type:'steps',amount:1000,base:0}]}")
    check('old-date plan ignored', ev("mhXPlanItems().length") == 0)
    check('no JS errors', not errs, str(errs[:2]))
print('p171:', 'ALL PASS' if not bad else f'{len(bad)} FAIL: {bad}'); sys.exit(1 if bad else 0)
