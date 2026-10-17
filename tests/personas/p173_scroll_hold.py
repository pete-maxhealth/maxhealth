"""Persona 173 (v3.10.1073): logging activity minutes must not make the page jump; the planned-meal module and the exercise
planner must not share function names (v1071 collision)."""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
bad = []
def check(n, ok, info=''):
    print(('PASS ' if ok else 'FAIL ') + n + (f'  {info}' if info and not ok else ''))
    if not ok: bad.append(n)
src = open(__file__.rsplit('/tests/', 1)[0] + '/maxhealth.html').read()
dups = [n for n in set(re.findall(r'^function (mh[A-Za-z0-9_]+)\(', src, re.M)) if len(re.findall(r'^function ' + n + r'\(', src, re.M)) > 1]
check('no duplicate mh* function declarations', not dups, str(dups))
POS = "(()=>{const c=document.getElementById('activityCard');return Math.round(c.getBoundingClientRect().top)})()"
with fresh_server() as root, sync_playwright() as pw:
    br = pw.chromium.launch(); ctx = br.new_context(viewport={'width': 430, 'height': 700}, service_workers='block'); page = ctx.new_page()
    errs = []; page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); page.evaluate("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev = page.evaluate; ev("startDemoMode('alex')"); page.wait_for_timeout(2200)
    ev("document.getElementById('maintab-today').click()"); page.wait_for_timeout(300)
    ev("switchSubTab('today','move')"); page.wait_for_timeout(300)   # v3.10.1097: the activity card lives on the Move tab
    ev("mhOpenResistance(); (()=>{const a=getActivities(); a.forEach(x=>{if(x.type==='resistance'){x.enabled=true}}); saveActivities(a); renderActivityCard();})()"); page.wait_for_timeout(400)
    ev("document.querySelector('#resistanceSimple .activity-row').scrollIntoView({block:'center'})"); page.wait_for_timeout(300)
    ev("typeof mhCheckOnline==='function' && mhCheckOnline()"); page.wait_for_timeout(2500)   # let the offline bar settle first (the test blocks the network); it is fixed-position chrome, not the card jumping
    ev("document.querySelector('#resistanceSimple .activity-row').scrollIntoView({block:'center'})"); page.wait_for_timeout(300)
    t0 = ev(POS)
    page.locator('#resistanceSimple .activity-dur').click(); page.keyboard.type('45'); page.wait_for_timeout(500)
    check('typing minutes does not move the card on screen', abs(ev(POS) - t0) <= 2, f'{t0}->{ev(POS)}')
    page.mouse.click(10, 10); page.wait_for_timeout(1500)
    check('leaving the field does not move the card on screen', abs(ev(POS) - t0) <= 2, f'{t0}->{ev(POS)}')
    page.locator('#resistanceSimple select').select_option('Hard'); page.wait_for_timeout(800)
    check('changing effort does not move the card', abs(ev(POS) - t0) <= 2, f'{t0}->{ev(POS)}')
    ev("mhPickExercise('badminton')"); page.wait_for_timeout(300)
    ev("(()=>{const i=getActivities().findIndex(a=>a.type==='badminton'); updateActivity(i,'duration','60',true)})()")
    txt = ev("document.querySelector('#activityRows .activity-row:last-child .activity-kcal').textContent")
    check('live kcal lands on the badminton row', 'kcal' in txt, txt)
    check('resistance row not overwritten by badminton update', ev("document.querySelector('#resistanceSimple .activity-kcal').textContent") != txt)
    check('meal planner functions intact', ev("typeof mhPlanLoad==='function' && mhPlanAdd.length===3 && String(mhPlanSave).includes('mh_planned_v1')"))
    check('exercise planner is separate', ev("String(mhXPlanSave).includes('plannedExercise')"))
    check('no JS errors', not errs, str(errs[:2]))
print('p173:', 'ALL PASS' if not bad else f'{len(bad)} FAIL: {bad}'); sys.exit(1 if bad else 0)
