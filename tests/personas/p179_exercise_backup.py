"""Persona 179 (v3.10.1076): a full backup carries every piece of exercise data and a restore brings it back."""
import sys, re, json; sys.path.insert(0, __file__.rsplit('/', 1)[0])
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
    ev("""(()=>{
      state.history=[{date:'01/10/26',log:[],totals:{kcal:2000,protein:100,carbs:30,fat:100},exercises:[{type:'badminton',name:'🏸 Badminton',duration:'60',effort:'Hard',kcal:630}]}];
      state.strengthLog=[{id:'s1',date:'01/10/26',exercise:'Bicep Curl',sets:[{reps:12,weight_kg:20,note:'seated'}],routineId:'rt1'}];
      state.plannedExercise={date:todayStr(),items:[{id:'p1',kind:'activity',type:'kayak',amount:60,effort:'Moderate'}]};
      saveRoutines([{id:'rt1',name:'Full Body',exercises:[{name:'Bicep Curl',sets:[{reps:20,weight_kg:40,note:'seated'}]}]}]);
      mhAddCatalogActivity('badminton', true); mhRememberEffort('badminton','Hard');
      localStorage.setItem('mh_calibration_log', JSON.stringify([{date:'01/10/26',metKcal:300,wearKcal:240,ratio:0.8,cat:'racket'}]));
      localStorage.setItem('mh_activity_level','active'); localStorage.setItem('mh_steps_baseline','9000');
      saveState();})()""")
    raw = ev("JSON.stringify(buildFullBackupPayload())")
    b = json.loads(raw)
    check('backup has dated exercise history', b['state']['history'][0]['exercises'][0]['type'] == 'badminton')
    check('backup has resistance sets with notes', b['state']['strengthLog'][0]['sets'][0]['note'] == 'seated')
    check('backup has the planned exercise', b['state']['plannedExercise']['items'][0]['type'] == 'kayak')
    check('backup has routines with template sets', b['routines'][0]['exercises'][0]['sets'][0]['weight_kg'] == 40)
    st = b['settings']
    check('backup settings carry the activity list, calibration, remembered effort, level and baseline',
          'mh_activities' in st and 'badminton' in st['mh_activities'] and 'mh_calibration_log' in st and 'mh_last_effort' in st and st.get('mh_activity_level') == 'active' and st.get('mh_steps_baseline') == '9000', str(sorted(k for k in st if 'act' in k or 'cal' in k or 'effort' in k)))
    # wipe then restore
    ev("""(()=>{state.history=[];state.strengthLog=[];state.plannedExercise=null;saveRoutines([]);localStorage.removeItem('mh_activities');localStorage.removeItem('mh_calibration_log');localStorage.removeItem('mh_last_effort');})()""")
    ev(f"mhApplyBackupObject({raw}, 'test')")
    r = ev("({h:state.history[0]&&state.history[0].exercises[0].type, s:state.strengthLog[0]&&state.strengthLog[0].sets[0].note, p:state.plannedExercise&&state.plannedExercise.items[0].type, rt:loadRoutines()[0]&&loadRoutines()[0].exercises[0].sets[0].weight_kg, act:getActivities().some(a=>a.type==='badminton'), cal:JSON.parse(localStorage.getItem('mh_calibration_log')||'[]').length, eff:mhLastEffort('badminton')})")
    check('restore brings back history exercises, sets, plan, routine sets', r['h'] == 'badminton' and r['s'] == 'seated' and r['p'] == 'kayak' and r['rt'] == 40, str(r))
    check('restore brings back the activity list, calibration and remembered effort', r['act'] and r['cal'] == 1 and r['eff'] == 'Hard', str(r))
    check('no JS errors', not errs, str(errs[:2]))
print('p179:', 'ALL PASS' if not bad else f'{len(bad)} FAIL: {bad}'); sys.exit(1 if bad else 0)
