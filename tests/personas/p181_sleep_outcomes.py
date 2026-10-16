"""Persona 181 (v3.10.1080): sleep as a full citizen and the what-moves-what engine."""
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
      const d=(n)=>{const x=new Date();x.setDate(x.getDate()-n);return String(x.getDate()).padStart(2,'0')+'/'+String(x.getMonth()+1).padStart(2,'0')+'/'+String(x.getFullYear()).slice(2);};
      let seed=7;const rnd=()=>{seed=(seed*9301+49297)%233280;return seed/233280;};
      const H=[];
      for(let i=60;i>=1;i--){
        const hard=(i%2===0);
        const prevHard=((i+1)%2===0);                       // day before this one (older) was an exercise day
        const slp= prevHard ? 450+rnd()*20 : 335+rnd()*15; // a night after exercise is longer
        const short = slp<360;
        H.push({date:d(i),totals:{kcal:short?2300+rnd()*40:1900+rnd()*40,protein:100,carbs:short?45:25,fat:100},steps:6000+rnd()*500,
          sleep_duration:slp,sleep_deep:short?50:80,sleep_rem:90,sleep_light:200,sleep_wake:20,sleep_efficiency:short?84:92,sleep_hr_avg:short?60:55,
          log:[{id:i,time:'19:00',description:'Dinner',kcal:700,protein:40,carbs:5,fat:50,items:[{name:'Dinner',kcal:700,protein:40,carbs:5,fat:50}]}],
          exercises:hard?[{type:'badminton',name:'🏸 Badminton',duration:'45',effort:'Hard',kcal:450}]:[]});
      }
      state.history=H.reverse();saveState();})()""")
    S = ev("(()=>{const x=mhSleepDay(state.history[0]);return {m:x.min>0,st:x.hasStages,deep:x.deep}})()")
    check('mhSleepDay reads minutes and stages', S['m'] and S['st'] and S['deep'] > 0)
    check('mhSleepDay is null when no sleep', ev("mhSleepDay({date:'01/01/26'})===null"))
    st = ev("(()=>{const s=mhSleepRangeStats(state.history);return {n:s.n,mean:Math.round(s.mean),pct7:s.pct7,deepPct:s.deepPct,nStaged:s.nStaged}})()")
    check('range stats count nights and stages', st['n'] == 60 and st['nStaged'] == 60 and 380 < st['mean'] < 450 and st['deepPct'] > 10, str(st))
    of = ev("mhOutcomeFindings(state.history,{limit:12}).map(o=>({e:o.exposure,o:o.okey,k:o.kind,g:o.good,d:Math.round(o.diff)}))")
    check('finds exercise -> next-night sleep', any(f['o'] == 'sleep' and 'badminton' in f['e'] and f['d'] > 40 and f['g'] == 1 for f in of), str(of))
    check('finds short night -> more calories next-day', any(f['k'] == 'reverse' and f['o'] == 'kcal' and f['d'] > 150 for f in of), str(of))
    ev("(()=>{seed=1;const x=state.history.slice();state.history=x.slice(0,10);})()")
    check('too little data gives nothing rather than guesses', ev("mhOutcomeFindings(state.history).length")==0)
    ev("location.reload()"); page.wait_for_timeout(1500)
    ev("(()=>{const d=(n)=>{const x=new Date();x.setDate(x.getDate()-n);return String(x.getDate()).padStart(2,'0')+'/'+String(x.getMonth()+1).padStart(2,'0')+'/'+String(x.getFullYear()).slice(2);};let seed=3;const rnd=()=>{seed=(seed*9301+49297)%233280;return seed/233280;};const H=[];for(let i=1;i<=40;i++){const ex=i%2===0;H.push({date:d(i),totals:{kcal:2000,protein:100,carbs:30,fat:100},steps:7000,sleep_duration:400+(((i+1)%2===0)?50:0)+rnd()*20,sleep_deep:70,sleep_rem:90,sleep_light:200,sleep_efficiency:90,log:[],exercises:ex?[{type:'walking',name:'Walking',duration:'40',effort:'Easy',kcal:150}]:[]});}state.history=H;saveState();})()")
    ev("switchTabById('hist')"); page.wait_for_timeout(300); ev("renderHistory()")
    html = ev("document.getElementById('histEntries').innerHTML")
    check('History day shows a sleep panel with stages', 'SLEEP' in html and '#7048e8' in html)
    ev("switchTabById('reports')"); page.wait_for_timeout(600); ev("renderReports()")
    check('Reports show the Sleep section', ev("document.getElementById('sleep-report-section').style.display")=='block' and 'AVERAGE NIGHT' in ev("document.getElementById('sleep-report-content').innerText"))
    check('Reports show what-moves-what with the Early Stage label', ev("document.getElementById('outcomes-report-section').style.display")=='block' and 'Early Stage' in ev("document.getElementById('outcomes-report-section').innerText"))
    ctxt = ev("(()=>{const c=buildPatientContext(state.history);return patientContextBlock(c)})()")
    check('AI context carries sleep detail and associations', 'SLEEP DETAIL' in ctxt and 'OWN-DATA ASSOCIATIONS' in ctxt, ctxt[:80])
    pay = ev("JSON.stringify(typeof buildCarerPayload==='function'?buildCarerPayload():null)")
    check('carer payload carries nightly sleep minutes (if builder exposed)', pay in ('null',) or '"sl":' in pay)
    onc = ev("(()=>{try{return generateOncologyView.toString().includes('sleepSection')}catch(e){return false}})()")
    check('clinician view includes sleep', onc)
    check('no JS errors', not errs, str(errs[:2]))
print('p181:', 'ALL PASS' if not bad else f'{len(bad)} FAIL: {bad}'); sys.exit(1 if bad else 0)
