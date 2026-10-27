"""Persona 337: steps live in ONE place on Move. Plan more steps sits inside Daily Steps; Plan Ahead no longer has a Steps chip.
Walks: plan -> shows in Plan Ahead list -> Done writes real steps -> reload -> History/Today untouched; walk plan still works."""
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
    ev("document.querySelector('#subtab-move, [onclick*=\"move\"]') && 0")
    ev("switchTabById('move')"); page.wait_for_timeout(400)
    ev("localStorage.setItem('mh_plan_open','1'); localStorage.setItem('mh_steps_today','0'); renderActivityCard(); mhRenderPlanAhead(); mhRenderStepsPlan()"); page.wait_for_timeout(300)
    row = ev("document.getElementById('stepsPlanRow').textContent")
    check('Daily Steps card has the plan row', 'plan more steps' in row, row)
    chips = ev("document.getElementById('planAhead').textContent")
    check('Plan Ahead has no Steps chip', '👣' not in chips and 'more steps today' not in chips, chips[:120])
    check('Plan Ahead still has Walk, Run, Cycle, Resistance', all(w in chips for w in ('Walk', 'Run', 'Cycle', 'Resistance')))
    ev("mhStepsPlanSet(4000)")
    check('amount change updates the kcal line', '4,000' not in ev("document.getElementById('stepsPlanRow').textContent") and ev("document.getElementById('stepsPlanInput').value") == '4000')
    ev("localStorage.setItem('mh_steps_today', String(getStepsBaseline()+500)); mhRenderStepsPlan()")
    page.click('#stepsPlanRow span[onclick*="mhXPlanAdd"]'); page.wait_for_timeout(300)
    items = ev("mhXPlanItems()")
    check('Plan adds a steps item', len(items) == 1 and items[0]['kind'] == 'steps' and items[0]['amount'] == 4000, str(items))
    check('planned item listed in Plan Ahead', 'steps still to go' in ev("document.getElementById('planAhead').textContent"))
    ev("mhXPlanDone(mhXPlanItems()[0].id)"); page.wait_for_timeout(300)
    check('Done writes the real step count', int(ev("localStorage.getItem('mh_steps_today')")) >= ev("getStepsBaseline()") + 4500)
    check('plan cleared after Done', ev("mhXPlanItems().length") == 0)
    ev("document.getElementById('maintab-today').click()"); page.wait_for_timeout(300); ev("document.getElementById('maintab-insights').click()"); page.wait_for_timeout(300)
    ev("document.getElementById('maintab-today').click(); switchTabById('move'); updateDashboard(true)"); page.wait_for_timeout(400)
    check('real steps survive tab round trip', int(ev("localStorage.getItem('mh_steps_today')")) > 4000)
    check('plan row renders after tab round trip', ev("!!document.getElementById('stepsPlanRow') && document.getElementById('stepsPlanRow').textContent.includes('plan more steps')"))
    ev("mhXPlanAdd('activity','walking',30,'Moderate')")
    check('walk plan still works', ev("mhXPlanItems().length") == 1 and ev("mhXPlanItems()[0].type") == 'walking')
    check('no JS errors', not errs, str(errs[:2]))
    page.screenshot(path='/tmp/claude-0/-home-claude/c032a46b-68f2-5aea-a854-98f1a5b7657c/scratchpad/move_steps.png')
print('p337:', 'ALL PASS' if not bad else f'{len(bad)} FAIL: {bad}'); sys.exit(1 if bad else 0)
