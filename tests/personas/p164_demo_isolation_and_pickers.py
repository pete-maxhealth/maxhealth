"""Persona 164 (v3.10.1062): Pete's field-test list.
 - non-keto personas never see ketogenic wording in the Today carb-zones panel; keto personas still do
 - Default layout / a page reload inside a demo keeps the demo running and never changes the real account's layout
 - exit puts every real setting back
 - Full Summary and GBM summary grey out offline like the other AI buttons
 - routine editor and Log a workout offer tap-to-add exercises"""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
bad = []
def check(name, ok, info=''):
    print(('PASS ' if ok else 'FAIL ') + name + (f'  {info}' if info and not ok else '')); 
    if not ok: bad.append(name)
with fresh_server() as root, sync_playwright() as pw:
    br = pw.chromium.launch(); ctx = br.new_context(viewport={'width': 430, 'height': 900}, service_workers='block'); page = ctx.new_page()
    errs = []; page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.dismiss())
    page.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); page.evaluate("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev = page.evaluate
    ev("localStorage.setItem('mh_condition','gbm'); localStorage.setItem('mh_tdee','3400'); localStorage.setItem('mh_collapse_dc_foo','closed'); localStorage.setItem('mh_lifestyle','mediterranean')")
    REAL = "({foo:localStorage.getItem('mh_collapse_dc_foo'),cond:localStorage.getItem('mh_condition'),tdee:localStorage.getItem('mh_tdee'),life:localStorage.getItem('mh_lifestyle')})"
    real0 = ev(REAL)
    def tip_text():
        return ev("(()=>{const t=document.getElementById('ketosisTooltip'); if(!t) return 'NOTIP'; t.style.display='block'; const v=[...t.querySelectorAll('*')].filter(e=>e.children.length===0&&e.offsetParent!==null).map(e=>e.textContent).join(' | '); t.style.display='none'; return v})()")
    for pid in ['doris', 'alex', 'john', 'karen']:
        ev(f"startDemoMode('{pid}')"); page.wait_for_timeout(1800); ev("document.getElementById('maintab-today').click()"); page.wait_for_timeout(500)
        t = tip_text(); check(f'{pid}: carb-zones panel has no keto wording', not re.search(r'keto|ketosis|GKI|\bStrict\b', t, re.I), t[:200])
        check(f'{pid}: panel still shows their carb target', 'Your carb target' in t, t[:160])
    for pid in ['maria', 'sam']:
        ev(f"startDemoMode('{pid}')"); page.wait_for_timeout(1800); ev("document.getElementById('maintab-today').click()"); page.wait_for_timeout(500)
        t = tip_text(); check(f'{pid}: keto persona still sees ketogenic zones', re.search(r'Ketogenic', t) is not None, t[:200])
    # Default layout inside a demo
    ev("startDemoMode('alex')"); page.wait_for_timeout(1800)
    ev("mhDoResetLayout(mhLayoutKeys(null))"); page.wait_for_timeout(4500)
    check('Default keeps the demo running', ev("_demoMode") is True and ev("_demoPersonaId") == 'alex')
    ev("localStorage.setItem('mh_lifestyle','higher_protein')")
    # a plain reload (pull-to-refresh, tab reclaimed) also resumes
    page.reload(); page.wait_for_timeout(5000)
    check('page reload resumes the demo', ev("_demoMode") is True and ev("_demoPersonaId") == 'alex')
    ev("exitDemoMode()"); page.wait_for_timeout(600)
    real1 = ev(REAL)
    check('exit restores the real layout, condition, TDEE and eating style', real1 == real0, f'{real0} -> {real1}')
    check('no demo markers left', ev("[localStorage.getItem('mh_demo_active'), sessionStorage.getItem('mh_demo_resume'), sessionStorage.getItem('mh_demo_fullsnap')]") == [None, None, None])
    # abandoned demo (tab closed): next load restores the real layout
    ev("startDemoMode('doris')"); page.wait_for_timeout(1500); ev("localStorage.removeItem('mh_collapse_dc_foo'); localStorage.setItem('mh_lifestyle','balanced')")
    ev("sessionStorage.removeItem('mh_demo_resume')"); page.reload(); page.wait_for_timeout(2500)
    check('abandoned demo: real layout and eating style come back on next load', ev(REAL) == real0, str(ev(REAL)))
    # offline greying
    ev("startDemoMode('alex')"); page.wait_for_timeout(1800)
    ctx.set_offline(True); ev("window.dispatchEvent(new Event('offline'))"); page.wait_for_timeout(1200)
    ev("document.getElementById('maintab-insights').click()"); page.wait_for_timeout(500); ev("document.getElementById('insightstab-reports').click()"); page.wait_for_timeout(700)
    op = ev("(()=>{const o={}; ['rptFullSummaryBtn','rptAskBtn'].forEach(i=>{const e=document.getElementById(i); o[i]=e?getComputedStyle(e).opacity:'none'}); return o})()")
    check('Full Summary and Ask AI both greyed offline', op.get('rptFullSummaryBtn') == '0.55' and op.get('rptAskBtn') == '0.55', str(op))
    ev("runFullSummary()"); page.wait_for_timeout(800)
    tt = ev("[...document.querySelectorAll('.toast,#toast,[id*=oast]')].map(e=>e.innerText).join(' ')")
    check('tapping Full Summary explains it needs internet', re.search(r'needs internet', tt) is not None, tt[:120])
    ctx.set_offline(False); ev("window.dispatchEvent(new Event('online'))")
    # strength pickers
    ev("document.getElementById('maintab-today').click()"); page.wait_for_timeout(600)
    ev("showRoutineList()"); page.wait_for_timeout(400); ev("showCreateRoutineForm()"); page.wait_for_timeout(400)
    chips = ev("document.querySelectorAll('#routineQuickChips span').length"); check('routine editor shows tap-to-add exercises', chips >= 8, str(chips))
    ev("document.querySelector('#routineQuickChips span').click()"); page.wait_for_timeout(300)
    names = ev("[...document.querySelectorAll('#routineExerciseRows input[placeholder=\\'Exercise name\\']')].map(i=>i.value)")
    check('tapping one fills the blank first row (no extra empty row)', len(names) == 1 and names[0] != '', str(names))
    ev("document.querySelectorAll('#routineQuickChips span')[1].click()"); page.wait_for_timeout(300)
    check('second tap adds a second exercise', ev("document.querySelectorAll('#routineExerciseRows input[placeholder=\\'Exercise name\\']').length") == 2)
    ev("document.getElementById('newRoutineName').value='Quick'; saveNewRoutine()"); page.wait_for_timeout(500)
    q = ev("loadRoutines().find(r=>r.name==='Quick')"); check('routine saves with those exercises', q and len(q['exercises']) == 2, str(q))
    ev("applyRoutine(loadRoutines().find(r=>r.name==='Quick').id)"); page.wait_for_timeout(500)
    check('applying it lists both exercises', ev("document.querySelectorAll('#routineApplyRows input[type=number]').length") >= 2)
    ev("showStrengthAddForm()"); page.wait_for_timeout(500)
    sc = ev("document.querySelectorAll('#strengthQuickChips span').length"); check('Log a workout shows tap-to-start exercises', sc >= 8, str(sc))
    ev("document.querySelector('#strengthQuickChips span').click()"); page.wait_for_timeout(300)
    check('tapping one fills the name', ev("document.getElementById('strengthExerciseName').value") != '')
    check('no JS errors', not errs, str(errs[:2]))
print('p164:', 'ALL PASS' if not bad else f'{len(bad)} FAIL: {bad}'); sys.exit(1 if bad else 0)
