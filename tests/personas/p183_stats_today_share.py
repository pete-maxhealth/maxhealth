"""Persona 183 (v3.10.1081): pinned statistics on Today; shared statistics in AI, weekly summary and clinician view."""
import sys, re, json; sys.path.insert(0, __file__.rsplit('/', 1)[0])
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
    page.evaluate("state.onboarded=true; localStorage.setItem('mh_dashboard_order', JSON.stringify(['weight','daymode','ketosis','macros','mealplan','macroratio','goalcheck','steps','symptoms','treatment','activity','weather','fasting','water','log','guides'])); saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev=page.evaluate
    check('older saved Today order gains My statistics after Weather', ev("(()=>{const o=getDashboardOrder();return o.indexOf('stats')===o.indexOf('weather')+1})()"))
    ev("""(()=>{const d=n=>{const x=new Date();x.setDate(x.getDate()-n);return String(x.getDate()).padStart(2,'0')+'/'+String(x.getMonth()+1).padStart(2,'0')+'/'+String(x.getFullYear()).slice(2)};
      state.history=[1,2,3,4].map(i=>({date:d(i),totals:{kcal:1900+i*50,protein:100,carbs:25,fat:100},log:[{id:i,time:'08:00',description:'Eggs',kcal:300,protein:20,carbs:1,fat:20,items:[{name:'Eggs',kcal:300,protein:20,carbs:1,fat:20}]}],exercises:[]}));saveState();})()""")
    ev("(()=>{const x=state.history[0];['Steak','Salmon','Cheese','Bacon','Pork'].forEach((n,i)=>x.log.push({id:50+i,time:'12:00',description:n,kcal:500,protein:30,carbs:1,fat:30,items:[{name:n,kcal:500,protein:30,carbs:1,fat:30}]}))})()")
    ev("switchTabById('dash'); updateDashboard()"); page.wait_for_timeout(300)
    check('no pinned statistics: the Today card stays out of the way', ev("getComputedStyle(document.getElementById('dashSection-stats')).display")=='none')
    ev("mhStatSeedDefaults()"); ev("mhStatTogglePin(mhStatLoad()[0].id)"); page.wait_for_timeout(200)
    ev("switchTabById('dash'); updateDashboard()"); page.wait_for_timeout(300)
    check('pinning shows the card with the statistic', ev("getComputedStyle(document.getElementById('dashSection-stats')).display")!='none' and 'Top 10 foods' in ev("document.getElementById('dashStatsBody').innerText"))
    check('Today tile shows at most 3 rows for a list', ev("document.getElementById('dashStatsBody').innerText.match(/\\d\\. /g)||[]").__len__()<=3)
    ev("mhStatTogglePin(mhStatLoad()[0].id)"); check('unpinning hides it again', ev("getComputedStyle(document.getElementById('dashSection-stats')).display")=='none')
    # share
    ev("(()=>{const a=mhStatLoad();a[0].share=true;mhStatSave(a);})()")
    ctxt=ev("patientContextBlock(buildPatientContext(state.history))")
    check('shared statistic reaches the AI context', "SAVED STATISTICS" in ctxt and 'Eggs' in ctxt, ctxt[-200:])
    ev("switchTabById('reports')"); page.wait_for_timeout(300)
    ev("generateWeeklySummary()"); page.wait_for_timeout(300)
    wk=ev("window._weeklySummaryText||''")
    check('shared statistic reaches the weekly summary text', 'SAVED STATISTICS' in wk, wk[-150:])
    check('shared statistic reaches the clinician view', ev("generateOncologyView.toString().includes('mhStatShareHtml')"))
    ex=json.loads(ev("JSON.stringify(mhStatExportObj())"))
    check('export strips pin, share and hidden flags', all(not any(k in s for k in ('pinned','share','hidden')) for s in ex['stats']))
    ev("(()=>{const a=mhStatLoad();a[0].hidden=true;mhStatSave(a)})()")
    check('hidden statistics are never shared', 'Top 10 foods' not in (ev("mhStatShareText()")))
    check('no JS errors', not errs, str(errs[:2]))
print('p183:', 'ALL PASS' if not bad else f'{len(bad)} FAIL: {bad}'); sys.exit(1 if bad else 0)
