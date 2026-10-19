"""Persona 169 (v3.10.1068): Resistance section. Collapsed under Activities with a one-line totals header; Train and routine templates
are separate screens; effort fills itself in; changed sessions ask Just today / Update / Save as new; Clone asks for a name."""
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
    ev("startDemoMode('alex')"); page.wait_for_timeout(2500)
    ev("document.getElementById('maintab-today').click()"); page.wait_for_timeout(500)
    check('Resistance section is collapsed by default', ev("getComputedStyle(document.getElementById('strengthRowsWrap')).display") == 'none')
    check('header says RESISTANCE', 'RESISTANCE' in ev("[...document.querySelectorAll('#activityCard div')].map(e=>e.textContent).join('|')"))
    check('Resistance is not in the Activities list', ev("[...document.querySelectorAll('#activityRows .activity-name')].every(e=>!/Resistance/.test(e.textContent))"))
    check('Resistance minutes/effort row is inside the Resistance section', ev("!!document.querySelector('#resistanceSimple .activity-name')"))
    check('header line exists', ev("document.getElementById('resTotalsLine').textContent.length>5"))
    # Train
    ev("showTrainChooser()"); page.wait_for_timeout(500)
    check('opening Train expands the section', ev("getComputedStyle(document.getElementById('strengthRowsWrap')).display") != 'none')
    check('chooser shows TRAINING TODAY banner', 'TRAINING TODAY' in ev("document.getElementById('routineListContainer').textContent"))
    check('chooser lists routines and Free workout', ev("document.getElementById('routineListContainer').textContent.includes('Free workout')") and ev("loadRoutines().length>0"))
    rid = ev("loadRoutines()[0].id"); rname = ev("loadRoutines()[0].name")
    ev(f"applyRoutine('{rid}')"); page.wait_for_timeout(500)
    check('applying shows TRAINING TODAY with the routine name', rname in ev("document.getElementById('routineListContainer').textContent") and 'TRAINING TODAY' in ev("document.getElementById('routineListContainer').textContent"))
    check('no EDITING TEMPLATE banner on the Train screen', 'EDITING TEMPLATE' not in ev("document.getElementById('routineListContainer').textContent"))
    ev("window._routineApplyDrafts.forEach(d=>{d.sets.forEach(x=>{if(x.weight_kg!=='') x.weight_kg=String(parseFloat(x.weight_kg)+2.5)}); if(!d.sets.some(x=>x.weight_kg!=='')) d.sets[0].weight_kg='20'}); renderRoutineApplyRows()"); page.wait_for_timeout(300)
    tl = ev("document.getElementById('routineLiveTotals').textContent")
    check('live totals line shows sets and kg', 'sets' in tl and 'kg lifted' in tl, tl)
    check('effort filled in with a reason', 'filled in' in ev("document.getElementById('routineEffortNote').textContent"), ev("document.getElementById('routineEffortNote').textContent"))
    n0 = ev("state.strengthLog.length")
    ev("saveRoutineSession()"); page.wait_for_timeout(600)
    check('unchanged session logs without the three-way question', ev("!document.querySelector('.app-modal-overlay')") and ev("state.strengthLog.length") > n0)
    check('logged entries remember the routine', ev(f"state.strengthLog.filter(e=>e.routineId==='{rid}').length") > 0)
    check('header now shows sets and kg', 'kg lifted' in ev("document.getElementById('resTotalsLine').textContent"), ev("document.getElementById('resTotalsLine').textContent"))
    # changed session -> three-way
    ev(f"applyRoutine('{rid}')"); page.wait_for_timeout(300)
    ev("window._routineApplyDrafts.pop(); renderRoutineApplyRows()"); page.wait_for_timeout(300)
    ev("saveRoutineSession()"); page.wait_for_timeout(500)
    check('changed session asks Just today / Update / Save as new', ev("[...document.querySelectorAll('.app-modal-overlay button')].map(b=>b.textContent).join('|')") == 'Just for today|Update the routine|Save as a new routine')
    ex_before = ev(f"loadRoutines().find(r=>r.id==='{rid}').exercises.length")
    ev("document.querySelector('.app-modal-overlay [data-pick=\"1\"]').click()"); page.wait_for_timeout(400)
    check('Update the routine changes the template', ev(f"loadRoutines().find(r=>r.id==='{rid}').exercises.length") == ex_before - 1)
    # clone
    nr = ev("loadRoutines().length")
    ev("showRoutineList()"); page.wait_for_timeout(400)
    check('manager shows EDITING TEMPLATE banner', 'EDITING TEMPLATE' in ev("document.getElementById('routineListContainer').textContent"))
    check('manager has Clone, no Apply', 'Clone' in ev("document.getElementById('routineListContainer').textContent") and 'Apply' not in ev("document.getElementById('routineListContainer').textContent"))
    ev(f"duplicateRoutine('{rid}')"); page.wait_for_timeout(300)
    check('Clone asks for a name', ev("!!document.getElementById('appPromptInput')"))
    ev("document.getElementById('appPromptInput').value='Full Body B'; document.getElementById('appModalConfirm').click()"); page.wait_for_timeout(500)
    check('clone created with the chosen name', ev("loadRoutines().some(r=>r.name==='Full Body B')") and ev("loadRoutines().length") == nr + 1)
    check('clone opens in the template editor', 'EDITING TEMPLATE' in ev("document.getElementById('routineListContainer').textContent") and ev("document.getElementById('newRoutineName').value") == 'Full Body B')
    # free workout
    ev("showTrainChooser(); applyRoutine('__free__')"); page.wait_for_timeout(300)
    ev("addRoutineApplyExerciseByName('Plank')"); page.wait_for_timeout(200)
    ev("window._routineApplyDrafts[0].sets=[{reps:'45',weight_kg:'',note:''}]; renderRoutineApplyRows()")
    ev("saveRoutineSession()"); page.wait_for_timeout(500)
    check('free workout offers to save as a routine', 'Save this workout as a routine' in ev("document.querySelector('.app-modal-overlay')?.textContent||''"))
    # Pete Spence (screenshot): a strength session logged its sets fine but never showed as calories
    # burned or moved any target. Root cause: the Resistance activity row is removable from the
    # Activities card like any other, and both crediting paths did `if (resIdx > -1) {...}` with no
    # else - if that row was ever deleted, every future strength session silently credited nothing,
    # forever, with zero error. v3.10.1111 re-creates the row on the fly instead of dropping the credit.
    ev("saveActivities(getActivities().filter(a=>a.type!=='resistance'))")
    check('Resistance row genuinely removed first', not ev("getActivities().some(a=>a.type==='resistance')"))
    ev("showStrengthAddForm()")
    ev("document.getElementById('strengthExerciseName').value='Deadlift'")
    ev("_strengthDraftSets=[{reps:'5',weight_kg:'100',note:''}]")
    ev("saveStrengthWorkout()"); page.wait_for_timeout(300)
    res1 = ev("getActivities().find(a=>a.type==='resistance')")
    check('manual log recreates a missing Resistance row and credits it', bool(res1) and res1.get('enabled') and ev("calcActivityKcal(getActivities().find(a=>a.type==='resistance'))") > 0, res1)
    ev("saveActivities(getActivities().filter(a=>a.type!=='resistance'))")
    ev("showTrainChooser(); applyRoutine('__free__')"); page.wait_for_timeout(300)
    ev("addRoutineApplyExerciseByName('Row')"); page.wait_for_timeout(200)
    ev("window._routineApplyDrafts[0].sets=[{reps:'10',weight_kg:'40',note:''}]; renderRoutineApplyRows()")
    ev("saveRoutineSession()"); page.wait_for_timeout(400)
    ev("document.querySelector('.app-modal-overlay')?.querySelector('[data-pick=\"0\"],button')?.click()"); page.wait_for_timeout(300)  # dismiss "save as routine?" if it appears
    res2 = ev("getActivities().find(a=>a.type==='resistance')")
    check('routine session recreates a missing Resistance row and credits it', bool(res2) and res2.get('enabled') and ev("calcActivityKcal(getActivities().find(a=>a.type==='resistance'))") > 0, res2)
    check('no JS errors', not errs, str(errs[:2]))
print('p169:', 'ALL PASS' if not bad else f'{len(bad)} FAIL: {bad}'); sys.exit(1 if bad else 0)
