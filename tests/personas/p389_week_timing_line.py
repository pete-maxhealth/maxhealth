"""Persona 389: the weekly summary says when you ate (v3.10.1280).
Covers: a plain timing line on screen and in the copied text when 3+ days have timed meals, correct figures for known days, nothing when fewer than 3 days, approximate-time meals ignored, no food names. Invented data."""
import sys, json; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    page = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block').new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    # previous week, Sunday to Saturday, so the data is the same whatever day the test runs
    js = """(n)=>{const now=new Date(); const s=new Date(now); s.setDate(now.getDate()-now.getDay()-7); s.setHours(0,0,0,0);
      const ds=i=>{const x=new Date(s); x.setDate(s.getDate()+i); return String(x.getDate()).padStart(2,'0')+'/'+String(x.getMonth()+1).padStart(2,'0')+'/'+String(x.getFullYear()).slice(2)};
      const mk=(i)=>({date:ds(i),mode:'standard',notes:'standard',totals:{kcal:1600,protein:100,carbs:20,fat:60},log:[
        {id:i*10+1,time:'08:00',description:'Zzqx a',kcal:400,protein:30,carbs:2,fat:5},{id:i*10+2,time:'13:00',description:'Zzqx b',kcal:400,protein:30,carbs:3,fat:5},
        {id:i*10+3,time:'19:00',description:'Zzqx c',kcal:400,protein:40,carbs:6,fat:5},{id:i*10+4,time:'15:00',description:'Zzqx approx',kcal:400,protein:99,carbs:99,fat:5,timeApprox:true}]});
      state.history=[]; for(let i=0;i<n;i++) state.history.push(mk(i)); saveState();}"""
    sel = "(()=>{let e=document.getElementById('weekExportSelector'); if(!e){e=document.createElement('select');e.id='weekExportSelector';document.body.appendChild(e)} e.innerHTML='<option value=1>1</option>'; e.value='1'})()"
    ev("(" + js + ")(4)"); ev(sel); ev("generateWeeklySummary()"); page.wait_for_timeout(500)
    line = ev("document.getElementById('weekTimingLine')?.innerText||''")
    if '4 days with times' not in line or 'first meal about 08:00' not in line or 'last about 19:00' not in line or '3 eating occasions' not in line or 'protein before noon 30g' not in line or 'carbs after 5pm 6g' not in line: f.add('BUG', '1: line has the right figures: ' + line)
    if 'Zzqx' in line: f.add('BUG', '2: no food names in it')
    if 'Meal timing (4 days' not in ev("window._weeklySummaryText"): f.add('BUG', '3: in the copied text too')
    ev("(" + js + ")(2)"); ev("generateWeeklySummary()"); page.wait_for_timeout(400)
    if ev("!!document.getElementById('weekTimingLine')") or 'Meal timing' in ev("window._weeklySummaryText"): f.add('BUG', '4: nothing with fewer than 3 days')
    ev("(" + js + ")(4)"); ev("generateWeeklySummary()"); page.wait_for_timeout(400); ev("switchTab('insights'); switchSubTab('insights','reports')"); page.wait_for_timeout(500); ev("document.querySelectorAll('.toast').forEach(t=>t.style.display='none'); document.getElementById('weekTimingLine').scrollIntoView({block:'center'})"); page.wait_for_timeout(300); page.screenshot(path='/tmp/p389.png')
    if errs: f.add('BUG', f'page errors {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
