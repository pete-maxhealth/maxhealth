"""Persona 190 (v3.10.1086): exported PDF is a real PDF; every language file loads offline and translates; reminder test chain with a stubbed Notification; device import tolerates hostile rows."""
import sys, re, json, glob, os; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
bad=[]
def check(n, ok, info=''):
    print(('PASS ' if ok else 'FAIL ')+n+(f'  {info}' if info and not ok else ''))
    if not ok: bad.append(n)
REPO=os.path.abspath(os.path.join(__file__,'..','..','..'))
with fresh_server() as root, sync_playwright() as pw:
    br=pw.chromium.launch(); ctx=br.new_context(viewport={'width':430,'height':900},service_workers='block'); page=ctx.new_page()
    errs=[]; page.on('pageerror',lambda e:errs.append(str(e)[:200])); page.on('dialog',lambda d:d.accept())
    page.route(re.compile(r'^https?://(?!localhost)'),lambda r:r.abort())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    ev=page.evaluate
    ev("state.onboarded=true; saveState()")
    # ---- PDF
    r=ev("""(async()=>{ const prof={name:'Test profile',orgName:'Test Org',orgColor:'#2deb8f'}; const rows=[['Date','Calories','Protein'],['16/10/26','1900','120'],['15/10/26','2000','110']];
      const b=buildProfileReportPDF(prof,null,'Header line',rows,false); if(!b) return null; const t=await b.text(); return [b.size, t.slice(0,5), b.type]; })()""")
    check('PDF report builds from the bundled jsPDF', r is not None and r[1]=='%PDF-' and r[0]>1500, str(r))
    r=ev("""(async()=>{ const rows=[['a','b']].concat(Array.from({length:300},(_,i)=>['x'+i,'y'.repeat(60)])); const b=buildProfileReportPDF({name:'Big',orgName:'<b>Org</b>',orgColor:'zzz'},null,'H',rows,true); return b? b.size:null; })()""")
    check('PDF copes with 300 rows, markup in the name and a bad colour', r and r>3000, str(r))
    # ---- languages
    for f in sorted(glob.glob(REPO+'/lang/*.json')):
        code=os.path.basename(f)[:-5]; d=json.load(open(f))
        check(f'lang {code}: valid JSON with entries', isinstance(d,dict) and len(d)>100, str(len(d)))
        ph=[k for k,v in d.items() if isinstance(v,str) and sorted(re.findall(r'\{[^}]*\}',k))!=sorted(re.findall(r'\{[^}]*\}',v))]
        check(f'lang {code}: placeholders preserved', not ph, str(ph[:3]))
    ok=ev("(async()=>{ await mhLangLoad('es'); return Object.keys(MH_L.dict||{}).length })()")
    check('Spanish loads from the app copy (no GitHub needed)', ok and ok>100, str(ok))
    # ---- reminders (stub Notification so the chain can run headless)
    r=ev("""(()=>{ const made=[]; window.Notification=function(t,o){made.push(t)}; Notification.permission='granted'; Notification.requestPermission=async()=>'granted';
      let el=document.getElementById('suppReminderTestResult'); if(!el){el=document.createElement('div'); el.id='suppReminderTestResult'; document.body.appendChild(el);}
      try{ testSupplementReminder(); }catch(e){ return 'ERR '+e.message } return new Promise(r=>setTimeout(()=>r(el.textContent.slice(0,300)),1500)); })()""")
    check('reminder self-test runs to the end without error', isinstance(r,str) and not r.startswith('ERR') and len(r)>20, str(r))
    # ---- device import
    ev("state.history=[]; saveState()")
    csv="date,steps,sleep_duration,sleep_deep,sleep_rem,hr_avg,hrv,weight\n2026-10-10,8000,450,80,95,60,48,80.2\n2026-10-11,abc,-5,,,,,\n,,,,,,,\n2026-10-12,99999999,9999,99999,0,300,-4,5000\n2026-10-13,6000,420,70,90,58,52,80.0\n"
    ev("(t)=>{ processCombinedText(t,true) }",csv); 
    h=ev("state.history.map(d=>[d.date,d.steps,d.sleep_duration,d.weight])")
    check('good rows imported', any(x[1]==8000 and x[2]==450 for x in h) and any(x[1]==6000 for x in h), str(h))
    check('blank-date row skipped, no crash', len(h)>=2 and all(x[0] for x in h), str(h))
    bad_row=ev("state.history.find(d=>d.date==='12/10/26')")
    check('impossible values are blanked, row kept', bad_row is not None and bad_row['steps'] is None and bad_row['weight'] is None and bad_row['hr_avg'] is None and bad_row['sleep_duration'] is None, str(bad_row)[:300])
    good=ev("state.history.find(d=>d.date==='10/10/26')")
    check('plausible values untouched', good['steps']==8000 and good['weight']==80.2 and good['hrv']==48, str(good)[:200])
    check('no JS errors', not errs, str(errs[:2]))
print('p190: ALL PASS' if not bad else 'p190 FAILED: '+', '.join(bad))
