"""Persona 174 (v3.10.1074): per-category watch calibration (shrunk toward the overall factor), remembered effort per activity."""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
bad = []
def check(n, ok, info=''):
    print(('PASS ' if ok else 'FAIL ') + n + (f'  {info}' if info and not ok else ''))
    if not ok: bad.append(n)
with fresh_server() as root, sync_playwright() as pw:
    br = pw.chromium.launch(); ctx = br.new_context(viewport={'width': 430, 'height': 900}, service_workers='block'); page = ctx.new_page()
    errs = []; page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); page.evaluate("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev = page.evaluate
    ev("localStorage.removeItem('mh_calibration_log')")
    check('categories: badminton racket, walking walk, custom other', ev("[mhActCat({type:'badminton'}),mhActCat({type:'walking'}),mhActCat({type:'exercise'})].join()") == 'racket,walk,other')
    check('no data -> no category calibration', ev("getCategoryCalibration('racket')") is None)
    # 10 walking days at ratio 1.0 and 3 racket days at 0.7: not enough racket days yet
    ev("""(()=>{const log=[];for(let i=1;i<=10;i++)log.push({date:'0'+i+'/09/26',metKcal:300,wearKcal:300,ratio:1,cat:'walk'});for(let i=11;i<=13;i++)log.push({date:i+'/09/26',metKcal:300,wearKcal:210,ratio:0.7,cat:'racket'});localStorage.setItem('mh_calibration_log',JSON.stringify(log))})()""")
    check('3 racket days not enough', ev("getCategoryCalibration('racket')") is None)
    ev("""(()=>{const log=JSON.parse(localStorage.getItem('mh_calibration_log'));for(let i=14;i<=17;i++)log.push({date:i+'/09/26',metKcal:300,wearKcal:210,ratio:0.7,cat:'racket'});localStorage.setItem('mh_calibration_log',JSON.stringify(log))})()""")
    c = ev("getCategoryCalibration('racket')")
    g = ev("getCalibrationFactor().factor")
    exp = (7 * 0.7 + 5 * g) / 12
    check('7 racket days -> shrunk factor between 0.7 and overall', c and abs(c['factor'] - exp) < 0.001 and 0.7 < c['factor'] < g, f'{c} exp {exp} g {g}')
    ev("(()=>{const a=getActivities(); a.push({id:'t1',name:'b',type:'badminton',needsDistance:false,duration:'60',effort:'Moderate',enabled:true}); a.push({id:'t2',name:'w',type:'walking',needsDistance:false,duration:'60',effort:'Moderate',enabled:true}); saveActivities(a)})()")
    w = ev("state.weight||90")
    kb = ev("calcActivityKcal(getActivities().find(a=>a.type==='badminton'))")
    kw = ev("calcActivityKcal(getActivities().find(a=>a.id==='t2'))")
    check('badminton uses racket factor', abs(kb - round(5.5 * w * c['factor'])) <= 1, f'{kb} vs {5.5*w*c["factor"]}')
    gf = ev("getCalibrationFactor().factor")
    wf = (10 * 1.0 + 5 * gf) / 15
    check('walking uses its own 10-day factor, shrunk toward overall', abs(kw - round(3.5 * w * wf)) <= 1, f'{kw} vs {3.5*w*wf}')
    ev("(()=>{const a=getActivities(); a.push({id:'t3',name:'k',type:'kettlebell',needsDistance:false,duration:'60',effort:'Moderate',enabled:true}); saveActivities(a)})()")
    kk = ev("calcActivityKcal(getActivities().find(a=>a.id==='t3'))")
    check('category with no days uses the overall factor', abs(kk - round(8.0 * w * gf)) <= 1, f'{kk} vs {8.0*w*gf}')
    # clamp
    ev("""(()=>{const log=[];for(let i=1;i<=12;i++)log.push({date:'0'+i+'/09/26',metKcal:300,wearKcal:30,ratio:0.1,cat:'water'});localStorage.setItem('mh_calibration_log',JSON.stringify(log))})()""")
    check('extreme ratios are clamped to 0.6', ev("getCategoryCalibration('water').factor") >= 0.6)
    # remembered effort
    ev("mhRememberEffort('kayak','Hard')")
    ev("mhAddCatalogActivity('kayak', true)")
    check('re-added activity starts at last-used effort', ev("getActivities().find(a=>a.type==='kayak').effort") == 'Hard')
    check('no JS errors', not errs, str(errs[:2]))
print('p174:', 'ALL PASS' if not bad else f'{len(bad)} FAIL: {bad}'); sys.exit(1 if bad else 0)
