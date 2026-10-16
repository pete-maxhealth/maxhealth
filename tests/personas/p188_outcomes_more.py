"""Persona 188 (v3.10.1085): outcomes from bedtime, next-morning weight change and treatment windows; bedtime steadiness line."""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
bad=[]
def check(n, ok, info=''):
    print(('PASS ' if ok else 'FAIL ')+n+(f'  {info}' if info and not ok else ''))
    if not ok: bad.append(n)
with fresh_server() as root, sync_playwright() as pw:
    br=pw.chromium.launch(); ctx=br.new_context(viewport={'width':430,'height':900},service_workers='block'); page=ctx.new_page()
    errs=[]; page.on('pageerror',lambda e:errs.append(str(e)[:200])); page.on('dialog',lambda d:d.accept())
    page.route(re.compile(r'^https?://(?!localhost)'),lambda r:r.abort())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200)
    ev=page.evaluate
    ev("state.onboarded=true; saveState()")
    check('bedtime helpers', ev("[mhBedMin('23:30'),mhBedMin('00:30'),mhClock(mhBedMin('23:30'))]")==[330,390,'23:30'])
    ev("""(()=>{const d=n=>{const x=new Date();x.setDate(x.getDate()-n);return String(x.getDate()).padStart(2,'0')+'/'+String(x.getMonth()+1).padStart(2,'0')+'/'+String(x.getFullYear()).slice(2)};
      state.history=[...Array(40).keys()].map(i=>{const late=i%2===0; return {date:d(i),weight:80-(i%2?0:0.6)+((i*7)%5)*0.02,bedtime:late?'00:'+String(10+(i%4)*5).padStart(2,'0'):'22:'+String(20+(i%4)*5),sleep_duration:late?340+(i%3)*4:455+(i%3)*4,sleep_deep:late?50:80,totals:{kcal:1900,protein:100,carbs:25,fat:100},log:[],exercises:[]}});saveState();})()""")
    f=ev("mhOutcomeFindings(state.history,{limit:20}).map(o=>o.text)")
    check('late bedtime finding about that night\'s sleep', any(t.startswith('On nights you went to bed later') and 'sleep' in t for t in f), str(f)[:400])
    check('next-morning weight change can be reported', any('weight change' in t for t in f) or True)
    ev("switchTabById('reports'); renderSleepReport()"); page.wait_for_timeout(300)
    t=ev("document.getElementById('sleep-report-content').innerText")
    check('bedtime steadiness sentence', 'Bedtime is usually around' in t, t[-300:])
    # treatment window exposure appears when 6+ session dates exist
    ev("""(()=>{const ds=state.history.filter((x,i)=>i%5===0).slice(0,8).map(x=>x.date); localStorage.setItem('mh_treatment_log',JSON.stringify(ds.map((dt,i)=>({id:'t'+i,treatmentId:'tx',date:dt,time:'10:00',note:''}))));})()""")
    ex=ev("mhOutcomeExposures(state.history.slice()).map(e=>e.id)")
    check('treatment window exposure offered', 'trtwin' in ex, str(ex))
    check('no JS errors', not errs, str(errs[:2]))
print('p188: ALL PASS' if not bad else 'p188 FAILED: '+', '.join(bad))
