"""Persona 350 (v3.10.1238): Move = Steps & cardio (steps, calculator, walk and other cardio, Add exercise) / Resistance (sessions, routines).
Cardio rows live in the Steps card; the Resistance card holds only resistance; labels and hide/restore follow; no duplicate walk."""
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
    ev("switchTabById('move')"); page.wait_for_timeout(500)
    titles = ev("[...document.querySelectorAll('#moveScroll > .activity-card > .activity-card-title')].map(e=>e.firstElementChild.textContent.trim())")
    check('card order and titles', titles[:4] == ['STEPS & CARDIO', 'RESISTANCE', 'PLAN AHEAD', 'CURRENT REGIME'], str(titles))
    check('Add exercise button lives in the Steps & cardio card', ev("!!document.querySelector('#dailyStepsCard button[onclick=\"addCustomActivity()\"]')"))
    check('Resistance card has no Add exercise / cardio list', ev("!document.querySelector('#activityCard button[onclick=\"addCustomActivity()\"]') && !document.querySelector('#activityCard #activityRows')"))
    check('walk row inside Steps & cardio', ev("document.getElementById('dailyStepsCard').contains(document.getElementById('stepsWalkRow'))"))
    # add cycling through the picker
    ev("addCustomActivity()"); page.wait_for_timeout(500)
    check('picker opens from the Steps card', ev("!!document.getElementById('mhPickOv')"))
    ev("mhPickExercise('cycling')"); page.wait_for_timeout(600)
    check('new cardio row appears in the Steps & cardio card', ev("[...document.querySelectorAll('#dailyStepsCard #activityRows .activity-name')].some(e=>/Cycling/.test(e.textContent))"))
    check('cycling is not in the Resistance card', ev("![...document.querySelectorAll('#activityCard .activity-name')].some(e=>/Cycling/.test(e.textContent))"))
    check('resistance row is in the Resistance card only', ev("!!document.querySelector('#activityCard #resistanceSimple .activity-row') && !document.querySelector('#dailyStepsCard #resistanceSimple')"))
    check('exercise kcal total shows in the Steps & cardio title', ev("!!document.querySelector('#dailyStepsCard .activity-card-title #activityTotalKcal')"))
    # plan is its own card, apart from resistance
    check('Plan ahead lives in its own card, not in Resistance', ev("!!document.querySelector('#planCard #planAhead') && !document.querySelector('#activityCard #planAhead')"))
    check('Plan card has its own order/hide controls', ev("document.querySelectorAll('#planCard .activity-card-title .mh-cl > span').length")>=3 and ev("document.querySelectorAll('#regimeCard .activity-card-title .mh-cl > span').length")>=3)
    check('Current regime starts folded', ev("getComputedStyle(document.getElementById('dash-regime-wrap')).display")=='none')
    ev("toggleSection('dash-regime','dash-regime-wrap','dash-regime-icon')"); page.wait_for_timeout(200)
    reg = ev("document.getElementById('regimeBody').innerText")
    check('regime lists usual cardio and routines with Plan buttons', 'Walking' in reg and 'Plan 30 min' in reg and 'RESISTANCE ROUTINES' in reg, reg[:200])
    page.evaluate("document.querySelector('#regimeBody span[onclick*=mhXPlanAdd]').click()"); page.wait_for_timeout(400)
    check('planning from the regime feeds Plan ahead', ev("mhXPlanItems().length")==1 and 'If you do your plan' in ev("document.getElementById('planAhead').innerText"))
    ev("switchTabById('today'); updateDashboard()"); page.wait_for_timeout(400)
    check('planned exercise feeds the In/Out strip', 'plan' in ev("document.getElementById('inOutStrip').innerText").lower())
    ev("switchTabById('move')"); page.wait_for_timeout(300)
    ev("mhXPlanDone(mhXPlanItems()[0].id)"); page.wait_for_timeout(400)
    check('Done turns the plan into a real entry', ev("mhXPlanItems().length")==0 and ev("getActivities().some(a=>a.type==='walking'&&parseFloat(a.duration)>0)"))
    # saved order gets the new cards right after Resistance (migration)
    ev("localStorage.removeItem('mh_move_mig3'); localStorage.setItem('mh_move_order', JSON.stringify(['journey','steps','activity','exercise','bodycomp'])); mhMoveMigrate()")
    check('saved order gains Plan and Regime after Resistance', ev("JSON.parse(localStorage.getItem('mh_move_order')).join()")=='journey,steps,activity,plan,regime,exercise,bodycomp', ev("localStorage.getItem('mh_move_order')"))
    ev("localStorage.removeItem('mh_move_order')")
    # hide / restore labels
    ev("toggleMoveSectionHidden('activity'); toggleMoveSectionHidden('steps')"); page.wait_for_timeout(300)
    strip = ev("document.getElementById('moveRestoreStrip').innerText")
    check('restore strip uses new names', 'Steps & cardio' in strip and 'Resistance' in strip, strip)
    ev("toggleMoveSectionHidden('plan'); toggleMoveSectionHidden('regime')"); page.wait_for_timeout(200)
    check('plan and regime appear in the restore strip', all(w in ev("document.getElementById('moveRestoreStrip').innerText") for w in ('Plan ahead','Current regime')))
    ev("toggleMoveSectionHidden('plan'); toggleMoveSectionHidden('regime')")
    ev("toggleMoveSectionHidden('activity'); toggleMoveSectionHidden('steps')"); page.wait_for_timeout(300)
    check('both cards back', ev("getComputedStyle(document.getElementById('dailyStepsCard')).display")!='none' and ev("getComputedStyle(document.getElementById('activityCard')).display")!='none')
    # In/Out strip goes to the cardio card
    ev("switchTabById('today'); updateDashboard()"); page.wait_for_timeout(400)
    check('Out box jumps to Steps & cardio', ev("(document.getElementById('inOutStrip')||{innerHTML:''}).innerHTML.includes(\"mhGoMove('dailyStepsCard')\")"))
    check('no JS errors', not errs, str(errs[:2]))
    page.screenshot(path='/tmp/claude-0/-home-claude/c032a46b-68f2-5aea-a854-98f1a5b7657c/scratchpad/p350.png')
print('p350:', 'ALL PASS' if not bad else f'{len(bad)} FAIL: {bad}'); sys.exit(1 if bad else 0)
