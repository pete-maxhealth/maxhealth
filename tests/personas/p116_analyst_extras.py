"""Persona 116: the Ask-the-analyst prompt also carries symptom scores, tags and treatment days (so condition questions can be answered); empty when none; no page errors."""
import sys; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev = page.evaluate
    if ev("mhAnalystExtras([])") != '': f.add('BUG', 'extras not empty with no data')
    ev("saveSymptomDefs([{id:'s1',name:'Headache',active:true}]); saveTreatmentDefs([{id:'t1',name:'Acupuncture',active:true}])")
    out = ev("""(()=>{ const d=n=>{const x=new Date(Date.now()-n*864e5);const p=v=>String(v).padStart(2,'0');return p(x.getDate())+'/'+p(x.getMonth()+1)+'/'+String(x.getFullYear()).slice(2);};
      state.history=[{date:d(1),log:[],totals:{kcal:900},notes:'Exercise: Swim, 30min walk',symptoms:{s1:2}},{date:d(2),log:[],totals:{kcal:900},notes:'standard'}];
      saveTreatmentLog([{id:'x1',treatmentId:'t1',date:d(1)}]);
      return mhAnalystExtras(state.history); })()""")
    for need in ['Headache=2', 'Exercise: Swim', 'Acupuncture']:
        if need not in out: f.add('BUG', f'missing {need}: {out!r}')
    if '30min' in out: f.add('BUG', 'activity summary leaked as a tag')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
