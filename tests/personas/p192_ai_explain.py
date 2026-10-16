"""Persona 192 (v3.10.1089): legend on What seems to move what; thin findings (under 10 days a side) are not shown; ✨ explain buttons call the AI once and cache."""
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
      state.history=[...Array(60).keys()].map(i=>{const late=i%2===0; return {date:d(i+1),bedtime:late?'00:'+String(10+(i%4)*5).padStart(2,'0'):'22:'+String(20+(i%4)*5),sleep_duration:late?340+(i%3)*4:455+(i%3)*4,sleep_deep:late?50:80,totals:{kcal:1900,protein:100,carbs:25,fat:100},log:[{id:i,time:'08:00',description:'Eggs',kcal:300,protein:20,carbs:1,fat:20,items:[{name:'Eggs',kcal:300,protein:20,carbs:1,fat:20}]}],exercises:[]}});saveState();})()""")
    ev("window._aiCalls=0; window._aiPrompt=''; callHealthAI=async(p,o)=>{if(String(p||'').includes('does not know what is good')){window._aiCalls++; window._aiPrompt=p;} return {ok:true,text:'Plain words about your nights.'}}")
    ev("switchTabById('reports'); renderOutcomesReport()"); page.wait_for_timeout(300)
    t=ev("document.getElementById('outcomes-report-content').innerText")
    check('legend explains the markers', 'looks helpful' in t and 'looks unhelpful' in t, t[:200])
    check('explain button present', 'what does this mean for me' in t.lower())
    ev("mhExplainOutcomes()"); page.wait_for_timeout(400)
    check('AI explanation shown', 'Plain words' in ev("document.getElementById('outcomesExplain').innerText"))
    check('prompt carries the findings', 'bed later' in ev("window._aiPrompt") or 'later than usual' in ev("window._aiPrompt"), ev("window._aiPrompt")[-300:])
    ev("mhExplainOutcomes()"); page.wait_for_timeout(300)
    check('second tap is served from cache (one AI call)', ev("window._aiCalls")==1, str(ev("window._aiCalls")))
    # thin evidence
    ev("""(()=>{state.history.forEach((x,i)=>{x.steps=5000+(i%7)*100}); state.history.slice(0,9).forEach(x=>{x.steps=15000}); state.history.forEach((x,i)=>{ if(i<9) x.hrv=20; else x.hrv=40+(i%3)})})()""")
    f=ev("mhOutcomeFindings(state.history,{limit:30}).map(o=>o.nA+'/'+o.nB)")
    check('no finding rests on fewer than 10 days a side', all(int(a)>=10 and int(b)>=10 for a,b in (x.split('/') for x in f)), str(f))
    ev("switchTabById('stats'); mhStatsOpen()"); page.wait_for_timeout(300)
    id0=ev("mhStatLoad()[0].id")
    check('statistics card has ✨ Explain', ev("document.getElementById('stcard-%s').innerText.includes('Explain')"%id0))
    ev("mhStatExplain('%s')"%id0); page.wait_for_timeout(500)
    check('statistic explanation shown', 'Plain words' in ev("document.getElementById('stExplain-%s').innerText"%id0))
    check('no JS errors', not errs, str(errs[:2]))
print('p192: ALL PASS' if not bad else 'p192 FAILED: '+', '.join(bad))
