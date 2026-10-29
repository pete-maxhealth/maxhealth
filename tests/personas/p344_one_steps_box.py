"""Persona 344 (v3.10.1231): Move tab has ONE steps box. Walking is logged inside Daily Steps (not in Today's activity); it still counts (estimated steps, calories, effort); hiding Daily Steps puts Walking back in the list so a walk can still be logged; reload keeps both. Invented data."""
import sys, re; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 450, 'height': 1000}, service_workers='block')
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:200])); ev = page.evaluate
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev("switchTabById('today'); switchSubTab('today','move')"); page.wait_for_timeout(700)
    # v3.10.1239: Steps is its own box (one typed total); walking is an ordinary row in Exercise today
    if ev("document.querySelectorAll('#dailyStepsInput').length") != 1: f.add('BUG', 'exactly one steps box expected')
    if not ev("!![...document.querySelectorAll('#activityCard #activityRows .activity-name')].find(e => /Walking/.test(e.textContent))"): f.add('BUG', 'Walking should be a row in Exercise today')
    if ev("document.querySelectorAll('#activityRows .activity-row:first-child input[type=number].activity-dur').length") < 2: f.add('BUG', 'walk minutes + distance inputs missing')
    # log a walk there: it counts
    ev("(()=>{const i=getActivities().findIndex(a=>a.type==='walking'); toggleActivity(i,true); updateActivity(i,'duration','40',false); updateActivity(i,'distance','3',false);})()"); page.wait_for_timeout(400)
    acts = ev("getActivities().filter(a=>a.type==='walking').map(a=>({e:a.enabled,d:a.duration,k:a.distance}))")
    if not acts or not acts[0]['e'] or str(acts[0]['d']) != '40': f.add('BUG', f'walk not saved: {acts}')
    if not ev("(document.querySelector('#activityRows .activity-kcal')||{}).textContent"): f.add('BUG', 'walk shows no calories')
    if ev("getEstimatedStepsToday()") < 3000: f.add('BUG', 'estimated steps from the walk missing')
    # typing a day total still works next to it
    page.fill('#dailyStepsInput', '9000'); page.keyboard.press('Tab'); page.wait_for_timeout(300)
    if ev("parseInt(localStorage.getItem('mh_steps_today'))") != 9000: f.add('BUG', 'typed daily steps not saved')
    # v3.10.1238: steps, walking and the other cardio rows are ONE card (Steps & cardio). Hiding it hides them together; nothing is duplicated elsewhere.
    ev("(()=>{const h=getMoveHidden(); h.push('steps'); saveMoveHidden(h); applyMoveOrder();})()"); page.wait_for_timeout(400)
    if not ev("document.getElementById('activityCard').contains(document.querySelector('#activityRows .activity-row'))"): f.add('BUG', 'walk row must stay in Exercise today when Steps is hidden')
    ev("(()=>{const h=getMoveHidden().filter(k=>k!=='steps'); saveMoveHidden(h); applyMoveOrder();})()"); page.wait_for_timeout(400)
    # reload
    page.reload(); page.wait_for_timeout(1500); ev("switchTabById('today'); switchSubTab('today','move')"); page.wait_for_timeout(700)
    w = ev("(document.querySelector('#activityRows .activity-dur')||{}).value")
    if str(w) != '40': f.add('BUG', f'walk minutes lost after reload: {w!r}')
    page.screenshot(path='/tmp/claude-0/shots/onebox.png')
    if errs: f.add('JS-exception', errs[0])
    b.close()
bad = any(s in ('BUG', 'JS-exception') for s, _ in f); print('BUGS' if bad else 'OK', len(f)); sys.exit(1 if bad else 0)
