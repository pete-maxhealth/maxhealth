"""Persona 350 (v3.10.1239): Move = Steps / Exercise today / What if.
One place to record exercise (walking, cardio and resistance in the same list, with km/mi and effort); What if never stores a plan; Log it appends or creates."""
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
    check('card order and titles', [t.upper() for t in titles[:3]] == ['STEPS', 'EXERCISE TODAY', 'WHAT IF…'], str(titles))
    check('no regime / plan-ahead cards left', ev("!document.getElementById('regimeCard') && !document.getElementById('planAhead')"))
    check('Add exercise lives only in Exercise today', ev("document.querySelectorAll('button[onclick=\"addCustomActivity()\"]').length")==1 and ev("!!document.querySelector('#activityCard button[onclick=\"addCustomActivity()\"]')"))
    check('walking is an ordinary row in Exercise today', ev("!!document.querySelector('#activityCard #activityRows .activity-row') && /Walking/.test(document.getElementById('activityRows').innerText)"))
    check('resistance row is in Exercise today too', ev("!!document.querySelector('#activityCard #resistanceSimple .activity-row')"))
    check('walking row has km/mi and effort', ev("!!document.querySelector('#activityRows select') && /km/.test(document.getElementById('activityRows').innerText) && /mi/.test(document.getElementById('activityRows').innerText)"))
    check('kcal total shows in Exercise today title', ev("!!document.querySelector('#activityCard .activity-card-title #activityTotalKcal')"))
    check('each card has order/hide controls', ev("[...document.querySelectorAll('#dailyStepsCard,#activityCard,#planCard')].every(c=>c.querySelectorAll('.activity-card-title .mh-cl > span').length>=3)"))
    # add cycling via picker
    ev("addCustomActivity()"); page.wait_for_timeout(500)
    check('picker opens', ev("!!document.getElementById('mhPickOv')"))
    ev("mhPickExercise('cycling')"); page.wait_for_timeout(600)
    check('cycling row appears in Exercise today', ev("[...document.querySelectorAll('#activityCard .activity-name')].some(e=>/Cycling/.test(e.textContent))"))
    # typing minutes then distance must keep every digit and focus (v3.10.1241: no card redraw per keystroke)
    ev("(()=>{const i=getActivities().findIndex(a=>a.type==='walking'); toggleActivity(i,true)})()"); page.wait_for_timeout(300)
    mi = page.locator('#activityRows .activity-row').first.locator('input.activity-dur').first; mi.click(); page.keyboard.type('40', delay=100); page.wait_for_timeout(300)
    check('typing 40 minutes keeps both digits', ev("document.querySelector('#activityRows input.activity-dur').value")=='40')
    di = page.locator('#activityRows .activity-row').first.locator('input.activity-dur').nth(1); di.click(); page.keyboard.type('3.5', delay=100); page.wait_for_timeout(300)
    check('typing a distance keeps focus and value', ev("document.querySelectorAll('#activityRows input.activity-dur')[1].value")=='3.5')
    ev("(()=>{const i=getActivities().findIndex(a=>a.type==='walking'); updateActivity(i,'duration','',false); updateActivity(i,'distance','',false); toggleActivity(i,false)})()"); page.wait_for_timeout(300)
    # What if: nothing stored, Log it appends
    ev("mhWiSet && 0"); 
    before = ev("getActivities().find(a=>a.type==='walking')")
    b0 = float((before or {}).get('duration') or 0)
    page.fill('#wiInput', '40 min'); page.wait_for_timeout(300)
    out = ev("document.getElementById('wiOut').innerText")
    check('What if shows kcal and room left', 'kcal' in out and 'room' in out.lower(), out)
    check('What if stores nothing', ev("mhXPlanItems().length")==0 and float((ev("getActivities().find(a=>a.type==='walking')") or {}).get('duration') or 0)==b0)
    check('What if has effort chips', all(w in ev("document.getElementById('whatIf').innerText") for w in ('Easy','Moderate','Hard')))
    ev("mhWiLog()"); page.wait_for_timeout(500)
    after = float(ev("getActivities().find(a=>a.type==='walking').duration") or 0)
    check('Log it appends 40 min to today\'s walking', abs(after-(b0+40))<0.01, f'{b0}->{after}')
    check('input clears after logging', ev("document.getElementById('wiInput').value")=='')
    ev("switchTabById('today'); updateDashboard()"); page.wait_for_timeout(400)
    check('Out box jumps to Exercise today', ev("(document.getElementById('inOutStrip')||{innerHTML:''}).innerHTML.includes(\"mhGoMove('activityCard')\")"))
    # hide / restore labels
    ev("switchTabById('move')"); page.wait_for_timeout(300)
    ev("toggleMoveSectionHidden('activity'); toggleMoveSectionHidden('steps'); toggleMoveSectionHidden('plan')"); page.wait_for_timeout(300)
    strip = ev("document.getElementById('moveRestoreStrip').innerText")
    check('restore strip uses new names', all(w in strip for w in ('Steps','Exercise today','What if')), strip)
    ev("toggleMoveSectionHidden('activity'); toggleMoveSectionHidden('steps'); toggleMoveSectionHidden('plan')"); page.wait_for_timeout(300)
    check('cards back', all(ev(f"getComputedStyle(document.getElementById('{i}')).display")!='none' for i in ('dailyStepsCard','activityCard','planCard')))
    # migration puts plan after activity
    ev("localStorage.removeItem('mh_move_mig3'); localStorage.setItem('mh_move_order', JSON.stringify(['journey','steps','activity','exercise','bodycomp'])); mhMoveMigrate()")
    check('saved order gains plan after activity', ev("JSON.parse(localStorage.getItem('mh_move_order')).join()").startswith('journey,steps,activity,plan'), ev("localStorage.getItem('mh_move_order')"))
    ev("localStorage.removeItem('mh_move_order')")
    check('no JS errors', not errs, str(errs))
print('FAILED: ' + ', '.join(bad) if bad else 'ALL PASS'); sys.exit(1 if bad else 0)
