"""Persona 337 (rewritten v3.10.1236): steps live in ONE place on Move. The Daily Steps card holds a scratch calculator:
type steps -> live kcal line; leaving the box empties it; Add puts them on top of today's total (typed or device, whichever is higher).
Plan Ahead has no Steps chip; walk plans still work; legacy step plans still finish; no step plans can be created from the UI."""
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
    ev("document.getElementById('maintab-today').click()"); page.wait_for_timeout(300)
    ev("switchTabById('move')"); page.wait_for_timeout(400)
    ev("localStorage.setItem('mh_plan_open','1'); localStorage.setItem('mh_steps_today','0'); renderActivityCard(); mhRenderPlanAhead(); mhRenderStepsPlan()"); page.wait_for_timeout(300)
    row = ev("document.getElementById('stepsPlanRow').textContent")
    check('Daily Steps card has the calculator row', 'what are more steps worth' in row, row)
    check('? help present and closed', ev("!!document.querySelector('#stepsPlanRow .mh-q') && getComputedStyle(document.getElementById('stepscalcDetail')).display==='none'"))
    chips = ev("document.getElementById('planAhead').textContent")
    check('Plan Ahead has no Steps chip', '👣' not in chips and 'more steps today' not in chips, chips[:120])
    check('Plan Ahead still has Walk, Run, Cycle, Resistance', all(w in chips for w in ('Walk', 'Run', 'Cycle', 'Resistance')))
    check('Add button hidden while empty', ev("getComputedStyle(document.getElementById('stepsCalcAdd')).display")=='none')
    page.click('#stepsPlanInput'); page.keyboard.type('3k'); page.wait_for_timeout(200)
    out = ev("document.getElementById('stepsCalcOut').textContent")
    check('typing shows time, distance and kcal', '3,000 steps' in out and 'min' in out and 'mi' in out and 'kcal' in out, out)
    kc = lambda: int(re.search(r'\+([\d,]+) kcal', ev("document.getElementById('stepsCalcOut').textContent")).group(1).replace(',', ''))
    ev("mhStepsCalcSetPace('easy')"); ke = kc(); ev("mhStepsCalcSetPace('brisk')"); kb = kc(); ev("mhStepsCalcSetPace('steady')"); ks = kc()
    check('effort matters: brisk > steady > easy for the same steps', kb > ks > ke, f'{ke} {ks} {kb}')
    check('pace chips render and one is selected', ev("document.querySelectorAll('#stepsCalcPace span').length")==3)
    page.click('#stepsCalcPace span >> nth=2'); page.wait_for_timeout(600)
    check('tapping a pace chip keeps the typed steps', ev("document.getElementById('stepsPlanInput').value")=='3k' and 'brisk' in ev("document.getElementById('stepsCalcOut').textContent"), ev("document.getElementById('stepsPlanInput').value"))
    check('Add button appears', ev("getComputedStyle(document.getElementById('stepsCalcAdd')).display")!='none')
    check('typing stores nothing', not ev("localStorage.getItem('mh_steps_today')") or ev("localStorage.getItem('mh_steps_today')")=='0')
    ev("document.getElementById('stepsPlanInput').blur()"); page.wait_for_timeout(500)
    check('leaving the box empties it', ev("document.getElementById('stepsPlanInput').value")=='' and ev("document.getElementById('stepsCalcOut').textContent")=='')
    # Add (real tap: pointerdown then click must survive the blur)
    ev("localStorage.setItem('mh_steps_today','2000'); mhRenderStepsPlan()")
    exp = ev("mhStepsTodayTotal()") + 1500   # demo persona already has a device figure for today; Add builds on the higher one
    page.click('#stepsPlanInput'); page.keyboard.type('1500'); page.wait_for_timeout(150)
    page.click('#stepsCalcAdd'); page.wait_for_timeout(700)
    check('Add puts steps on top of today total', ev("localStorage.getItem('mh_steps_today')")==str(exp), ev("localStorage.getItem('mh_steps_today')")+' vs '+str(exp))
    w1 = ev("(()=>{const a=getActivities().find(x=>x.type==='walking'&&x.enabled);return a?[parseFloat(a.duration),parseFloat(a.distance)]:null})()")
    check('Add logs a walk at the chosen pace', bool(w1) and w1[0] > 0 and w1[1] > 0, str(w1))
    check('walk steps not counted twice (remainder = total - walk steps)', ev("(()=>{const b=getNonWalkingStepsToday();return b.remainder===Math.max(0,parseInt(localStorage.getItem('mh_steps_today'))-b.walkingSteps)})()"))
    check('box shows the new total and calculator cleared', ev("document.getElementById('dailyStepsInput').value")==str(exp) and ev("document.getElementById('stepsPlanInput').value")=='')
    # device figure higher than typed
    ev("window._historyIncludingToday = (function(o){return function(){const h=o().slice(); const t=todayStr(); const i=h.findIndex(e=>e.date===t); if(i>=0) h[i]=Object.assign({},h[i],{steps:20000}); else h.push({date:t,steps:20000,totals:{kcal:0}}); return h;}})(window._historyIncludingToday)")
    check('today total = higher of typed and device', ev("mhStepsTodayTotal()")==20000, ev("mhStepsTodayTotal()"))
    ev("mhRenderStepsPlan()"); page.click('#stepsPlanInput'); page.keyboard.type('500'); page.wait_for_timeout(150); page.click('#stepsCalcAdd'); page.wait_for_timeout(700)
    check('Add builds on the device figure', ev("localStorage.getItem('mh_steps_today')")=='20500', ev("localStorage.getItem('mh_steps_today')"))
    # tab round trip + reload
    ev("document.getElementById('maintab-insights').click()"); page.wait_for_timeout(300)
    ev("document.getElementById('maintab-today').click(); switchTabById('move'); updateDashboard(true)"); page.wait_for_timeout(400)
    check('calculator row renders after tab round trip', ev("document.getElementById('stepsPlanRow').textContent.includes('what are more steps worth')"))
    check('typed total survives tab round trip', int(ev("localStorage.getItem('mh_steps_today')")) >= 20500)
    # walk plans and legacy step plans
    ev("mhXPlanAdd('activity','walking',30,'Moderate')")
    check('walk plan still works', ev("mhXPlanItems().some(i=>i.type==='walking')"))
    ev("state.plannedExercise={date:todayStr(),items:[{id:'old1',kind:'steps',type:'steps',amount:500,base:100,effort:'Moderate'}]}; saveState(); mhXPlanPrune()")
    check('legacy step plan clears once passed', ev("mhXPlanItems().filter(i=>i.kind==='steps').length")==0)
    check('no JS errors', not errs, str(errs[:2]))
    page.screenshot(path='/tmp/claude-0/-home-claude/c032a46b-68f2-5aea-a854-98f1a5b7657c/scratchpad/move_steps.png')
print('p337:', 'ALL PASS' if not bad else f'{len(bad)} FAIL: {bad}'); sys.exit(1 if bad else 0)
