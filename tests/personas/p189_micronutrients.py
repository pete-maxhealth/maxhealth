"""Persona 189 (v3.10.1086): micronutrients (fibre, iron, potassium, magnesium, vitamin D, omega-3) in Statistics; unknown never reads as zero."""
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
    ev("""(()=>{const d=n=>{const x=new Date();x.setDate(x.getDate()-n);return String(x.getDate()).padStart(2,'0')+'/'+String(x.getMonth()+1).padStart(2,'0')+'/'+String(x.getFullYear()).slice(2)};
      state.history=[1,2,3].map(i=>({date:d(i),totals:{kcal:900,protein:60,carbs:10,fat:50},log:[
        {id:i,time:'08:00',description:'Salmon',kcal:400,protein:30,carbs:0,fat:25,items:[{name:'Salmon',kcal:400,protein:30,carbs:0,fat:25,vitd:10.5,omega3:2.1,iron:0.8}]},
        {id:10+i,time:'12:00',description:'Rice',kcal:500,protein:30,carbs:10,fat:25,items:[{name:'Rice',kcal:500,protein:30,carbs:10,fat:25}]}],exercises:[]}));saveState();})()""")
    r=ev("mhStatRun({subject:'foods',measure:'vitd',agg:'sum',order:'high',top:10,period:30,output:'list'}).rows.map(x=>[x.label,x.value])")
    check('vitamin D by food ranks salmon with the summed figure', r[0][0]=='Salmon' and abs(r[0][1]-31.5)<0.01, str(r))
    dd=ev("mhStatRun({subject:'days',measure:'omega3',agg:'sum',order:'time',top:14,period:30,output:'bars'}).rows.map(x=>x.value)")
    check('omega-3 by day has 3 days at 2.1', dd==[2.1,2.1,2.1], str(dd))
    check('a day with no figure is absent, not zero', ev("mhDayMicro({log:[{description:'Rice',kcal:1,items:[{name:'Rice',kcal:1}]}]},'iron')")==None)
    check('library offers the new statistics', ev("MH_ST_LIBRARY.some(x=>/Vitamin D/.test(x[0]))"))
    ev("mhStatsOpen()"); check('Statistics tab still renders', ev("document.getElementById('statsList').innerText.length")>20)
    check('no JS errors', not errs, str(errs[:2]))
print('p189: ALL PASS' if not bad else 'p189 FAILED: '+', '.join(bad))
