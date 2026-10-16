"""Persona 184 (v3.10.1081): speed-based MET for walk/run/ride, and net-of-resting energy for uncalibrated estimates."""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
bad=[]
def check(n, ok, info=''):
    print(('PASS ' if ok else 'FAIL ')+n+(f'  {info}' if info and not ok else ''))
    if not ok: bad.append(n)
with fresh_server() as root, sync_playwright() as pw:
    br=pw.chromium.launch(); ctx=br.new_context(viewport={'width':430,'height':900},service_workers='block'); page=ctx.new_page()
    errs=[]; page.on('pageerror',lambda e:errs.append(str(e)[:200])); page.on('dialog',lambda d:d.dismiss())
    page.route(re.compile(r'^https?://(?!localhost)'),lambda r:r.abort())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); page.evaluate("state.onboarded=true; state.weight=80; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev=page.evaluate
    ev("state.weight=80")
    A=lambda extra: "(()=>{const a=Object.assign({id:'t',name:'Walk',type:'walking',needsDistance:true,enabled:true,duration:'60',distance:'5',distanceUnit:'km',effort:'Moderate'},%s);return a})()"%extra
    m=lambda extra: ev("(a=>mhSpeedMet(a))(%s)"%A(extra))
    r=m("{}")  # 5 km in 1 h = 3.11 mph
    check('walking at about 3.1 mph gets about 3.6 METs', r and 3.5<=r['met']<=3.7 and 3.0<r['mph']<3.2, str(r))
    check('running 10 km in 1 h (6.2 mph) gets about 10.1 METs', 9.9<=m("{type:'running',name:'Run',distance:'10'}")['met']<=10.3, str(m("{type:'running',name:'Run',distance:'10'}")))
    check('cycling 24 km in 1 h (14.9 mph) is about 10 METs', 9.7<=m("{type:'cycling',name:'Ride',distance:'24'}")['met']<=10.3)
    check('an implausible speed is ignored (typo guard)', m("{distance:'60'}") is None)
    check('a hand-chosen effort overrides the speed', m("{_manualEffort:true}") is None)
    check('no distance, no speed MET', m("{distance:''}") is None)
    check('non-pace activities are untouched', ev("mhSpeedMet({needsDistance:false,type:'resistance',duration:'60'})")is None)
    raw=ev("calcActivityKcalRaw(%s)"%A("{}")); 
    check('raw kcal = speed MET x weight x hours', abs(raw-round(m("{}")['met']*80))<=1, str(raw))
    net=ev("calcActivityKcal(%s)"%A("{}"))
    check('uncalibrated estimate is net of resting (MET-1)', net==raw-80, f'{net} vs {raw}')
    ev("localStorage.setItem('mh_ex_energy_basis','gross')")
    check('gross setting restores the full figure', ev("calcActivityKcal(%s)"%A("{}"))==raw)
    ev("localStorage.removeItem('mh_ex_energy_basis')")
    ev("localStorage.setItem('mh_calibration_log', JSON.stringify(Array.from({length:12},(_,i)=>({date:'0'+(i%9+1)+'/01/26',metKcal:300,wearKcal:240,ratio:0.8}))))")
    cal=ev("calcActivityKcal(%s)"%A("{}"))
    check('with calibration, the measured factor applies and net is NOT applied on top', abs(cal-round(raw*0.8))<=1, f'{cal} vs {raw*0.8}')
    check('Formulas section has the exercise energy setting', ev("!!document.getElementById('exBasisSelect')"))
    check('no JS errors', not errs, str(errs[:2]))
print('p184:', 'ALL PASS' if not bad else f'{len(bad)} FAIL: {bad}'); sys.exit(1 if bad else 0)
