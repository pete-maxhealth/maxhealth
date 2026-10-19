"""Persona 200: A strength routine session survives a screen timeout. Wake lock requested while a routine is open
and released on finish/cancel; in-progress sets are persisted to localStorage as they're typed and offered back as
a resume on reopening the same routine within 12 hours; cancelling or finishing clears the draft so it's never
wrongly offered again; a draft for a DIFFERENT routine, or an old one, is treated as stale and discarded."""
import sys, json; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500); ev = page.evaluate
    ev("state.onboarded=true; saveState()")
    ev("""()=>{saveRoutines([{id:'r1',name:'Full Body',exercises:[{name:'Squat'},{name:'Bench'}]}]);}""")

    # Headless Chromium denies the Wake Lock permission outright (no UI to grant it), the same way it would for Cook
    # Mode's existing, unrelated wake lock - caught and logged, never thrown, same as here - so _routineWakeLock
    # itself can't be asserted true in this harness. What IS checkable: the release path never errors when called
    # with nothing held (covered by the Finish/Cancel checks below), and the request function exists and runs clean.
    ev("applyRoutine('r1')")
    page.wait_for_timeout(200)  # wake lock request is async

    # type into the first exercise's first set - this must persist live, not just on Finish
    ev("document.querySelector('#routineApplyRows input[placeholder=reps]').value='8'; document.querySelector('#routineApplyRows input[placeholder=reps]').dispatchEvent(new Event('input'))")
    draft = ev("JSON.parse(localStorage.getItem('mh_routine_draft')||'null')")
    if not draft or draft.get('routineId') != 'r1': f.add('BUG', f'draft not persisted while typing: {draft}')
    elif draft['drafts'][0]['sets'][0]['reps'] != '8': f.add('BUG', f'persisted draft has wrong value: {draft}')

    # simulate the screen-timeout / reclaimed-tab scenario: reload with the draft still on disk
    page.reload(); page.wait_for_timeout(1500)
    ev("state.onboarded=true; saveState()")
    ev("applyRoutine('r1')")
    page.wait_for_timeout(300)
    if 'unfinished' not in (ev("document.body.innerText") or ''): f.add('BUG', 'no resume offer shown for a fresh same-routine draft after reload')
    ev("document.getElementById('appModalConfirm')?.click()")
    page.wait_for_timeout(200)
    got = ev("document.querySelector('#routineApplyRows input[placeholder=reps]')?.value")
    if got != '8': f.add('BUG', f'resumed session lost the typed value: {got!r}')

    # finishing clears the draft so it's never wrongly re-offered
    ev("document.querySelectorAll('#routineApplyRows input[placeholder=reps]').forEach(i=>{i.value='8';i.dispatchEvent(new Event('input'))})")
    ev("saveRoutineSession()")
    page.wait_for_timeout(200)
    if ev("localStorage.getItem('mh_routine_draft')") not in (None, 'null'): f.add('BUG', 'draft not cleared after Finish & log')
    if ev("!!_routineWakeLock"): f.add('BUG', 'wake lock not released after finishing')

    # a draft left over for a DIFFERENT routine must never be offered as a resume
    ev("""()=>{saveRoutines([{id:'r1',name:'Full Body',exercises:[{name:'Squat'}]},{id:'r2',name:'Leg Day',exercises:[{name:'Lunge'}]}]);
      localStorage.setItem('mh_routine_draft', JSON.stringify({routineId:'r1', drafts:[{name:'Squat',sets:[{reps:'5',weight_kg:'',note:''}]}], savedAt: Date.now()}));}""")
    ev("applyRoutine('r2')")
    page.wait_for_timeout(300)
    if 'unfinished' in (ev("document.body.innerText") or ''): f.add('BUG', "a different routine's leftover draft was offered as a resume")
    ev("cancelRoutineApply()")

    # cancelling also clears any draft, so it's not wrongly offered next time
    ev("applyRoutine('r1')")
    ev("document.querySelector('#routineApplyRows input[placeholder=reps]').value='3'; document.querySelector('#routineApplyRows input[placeholder=reps]').dispatchEvent(new Event('input'))")
    ev("cancelRoutineApply()")
    if ev("localStorage.getItem('mh_routine_draft')") not in (None, 'null'): f.add('BUG', 'draft not cleared after Cancel')
    if ev("!!_routineWakeLock"): f.add('BUG', 'wake lock not released after Cancel')

    # a stale (>12h old) same-routine draft must not be offered either
    ev("""()=>{localStorage.setItem('mh_routine_draft', JSON.stringify({routineId:'r1', drafts:[{name:'Squat',sets:[{reps:'9',weight_kg:'',note:''}]}], savedAt: Date.now()-13*60*60*1000}));}""")
    ev("applyRoutine('r1')")
    page.wait_for_timeout(300)
    if 'unfinished' in (ev("document.body.innerText") or ''): f.add('BUG', 'a stale (>12h) draft was offered as a resume')

    if errs: f.add('BUG', f'page errors {errs[:3]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
