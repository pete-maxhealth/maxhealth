"""Persona 323 (v3.10.1216): Exercise over time, Body composition and Your Journey live on Move, each with its own date range, show/hide and reorder. Choosing a range redraws that card at once; the cards are gone from Reports and Trends; an empty card says why instead of vanishing; saved Move order keeps its place and the new cards join the end."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("startDemoMode('alex')"); page.wait_for_timeout(2500)
    ev("localStorage.setItem('mh_move_order', JSON.stringify(['activity','steps']))")
    ev("switchTabById('move')"); page.wait_for_timeout(1200)
    order = ev("[...document.querySelectorAll('#moveScroll > .activity-card')].map(e=>e.id)")
    if order[:2] != ['activityCard','dailyStepsCard'] or order[2:] != ['planCard','moveExerciseCard','moveBodycompCard','moveJourneyCard']: f.add('BUG', f'saved order kept, new cards join the end: {order}')
    for k in ['exercise','bodycomp','journey']:
        if not ev(f"!!document.getElementById('moveRange-{k}') && document.querySelectorAll('#moveRange-{k} .trends-filter-btn').length === 5"): f.add('BUG', f'{k} has its 5 range chips incl. Custom')
        for sel in ['▲','▼','👁']:
            if not ev(f"document.getElementById('move{k.capitalize()}Card').innerText.includes('{sel}')"): f.add('BUG', f'{k} has {sel} control')
    if ev("!!document.getElementById('exercise-report-section') && !document.getElementById('moveExerciseCard').contains(document.getElementById('exercise-report-section'))"): f.add('BUG', 'exercise section is inside the Move card')
    # gone from Reports and Trends
    ev("switchTabById('reports')"); page.wait_for_timeout(600)
    ev("switchTabById('insights'); switchSubTab('insights','trends',document.getElementById('insightstab-trends'))"); page.wait_for_timeout(800)
    for id in ['journeyCard','bodyCompCard','exercise-report-section']:
        inv = ev(f"(function(){{const e=document.getElementById('{id}'); return !!e && !e.closest('#view-move');}})()")
        if inv: f.add('BUG', f'{id} is only on Move')
    if 'Your Journey' in ev("document.getElementById('view-trends').innerText"): f.add('BUG', 'Trends no longer has Your Journey')
    # ranges redraw straight away
    ev("switchTabById('move')"); page.wait_for_timeout(800)
    sig = lambda: ev("[document.getElementById('exercise-report-content').innerText.replace(/\\s+/g,' '), (function(){const c=document.getElementById('journeyCanvas'); return c? c.toDataURL().length+':'+c.toDataURL().slice(-80):''})(), document.getElementById('trends-bodycomp-wrap').innerText.replace(/\\s+/g,' ')]")
    ev("mhMoveSetRange('exercise',7); mhMoveSetRange('journey',7); mhMoveSetRange('bodycomp',7)"); page.wait_for_timeout(500); a = sig()
    ev("mhMoveSetRange('exercise',0); mhMoveSetRange('journey',0); mhMoveSetRange('bodycomp',0)"); page.wait_for_timeout(500); b = sig()
    for i, n in enumerate(['exercise text','journey chart','body composition text']):
        if a[i] == b[i]: f.add('BUG', f'{n} changes when its range changes (7 days vs all): {str(a[i])[:80]}')
    print('exercise 7d:', a[0][:90]); print('exercise all:', b[0][:90]); print('body all:', b[2][-200:])
    # chip highlights follow the choice
    if ev("document.querySelector('#moveRange-journey .active').innerText") != 'All': f.add('BUG', 'the chosen range is highlighted')
    ev("mhMoveSetRange('journey',-1)"); page.wait_for_timeout(300)
    if not ev("document.getElementById('moveDates-journey').style.display === 'flex' && !!document.getElementById('moveFrom-journey')"): f.add('BUG', 'Custom shows From/To date boxes')
    sa = sig(); ev("mhMoveSetCustom('journey','from','2099-01-01')"); page.wait_for_timeout(300); sb = sig()
    if sa == sb: f.add('BUG', 'a custom range that excludes all data changes the card')
    ev("mhMoveSetCustom('journey','from','')"); ev("mhMoveSetRange('journey',0)")
    if ev("document.getElementById('moveDates-journey').style.display") != 'none': f.add('BUG', 'date boxes hide again on other ranges')
    ev("mhMoveSetRange('exercise',30)")
    # hide / show
    ev("toggleMoveSectionHidden('journey')"); page.wait_for_timeout(200)
    if ev("document.getElementById('moveJourneyCard').style.display") != 'none': f.add('BUG', '👁 hides the Journey card')
    ev("toggleMoveSectionHidden('journey')")
    # a new exercise logged while on Move shows up in the Exercise card without leaving
    ev("mhMoveSetRange('exercise',7)"); page.wait_for_timeout(300); before = ev("document.getElementById('exercise-report-content').innerText.replace(/\\s+/g,' ')")
    ev("(()=>{ const d = state.history[0]; d.exercises = (d.exercises||[]).concat([{name:'Zz Walk', type:'walking', duration:600, kcal:50, effort:'Hard'}]); saveState(); updateDashboard(); })()"); page.wait_for_timeout(1200)
    after = ev("document.getElementById('exercise-report-content').innerText.replace(/\\s+/g,' ')")
    if before == after: f.add('BUG', 'a change made while on Move redraws the Exercise card without leaving the page')
    # empty card explains itself
    ev("state.history=[]; window.getFullBodyCompositionHistory = () => []; saveState(); mhMoveRenderAll()"); page.wait_for_timeout(300)
    for k in ['Exercise','Bodycomp','Journey']:
        if not ev(f"document.getElementById('move{k}Empty').style.display === 'block'"): f.add('BUG', f'empty {k} card says why')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
