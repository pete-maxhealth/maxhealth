"""Persona 442 (v3.10.1343): food lines and their days-with/without note travel with Compare Metrics exports (copied summary, package, AI send)."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); page = b.new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); ev = page.evaluate
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200)
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay').style.display='none'")
    ev("""(()=>{ const ds=n=>{const d=new Date(); d.setDate(d.getDate()-n); return String(d.getDate()).padStart(2,'0')+'/'+String(d.getMonth()+1).padStart(2,'0')+'/'+String(d.getFullYear()).slice(2)};
      const H=[]; for(let n=1;n<=40;n++){ const items=[{name:'Zzqx Chicken',amount:'150g',kcal:250,protein:40,fat:8,carbs:0}]; if(n%2===1) items.push({name:'Zzqx Whey Protein',amount:'25g',kcal:101,protein:20,fat:1.9,carbs:1});
        H.push({date:ds(n), log:[{description:'meal',items,time:'12:00'}], steps: n%2===1?9000:6000, totals:{kcal:500,protein:60,carbs:3,fat:20}}); }
      state.history=H; saveState(); })()""")
    ev("openMultiMetricOverlay()"); page.wait_for_timeout(600); ev("toggleMMGroup('Foods')"); page.wait_for_timeout(200)
    ev("(()=>{const i=mmFoodIndex(); const c=[...i.foods.values()].find(x=>x.t.includes('Whey')); const b=document.createElement('button'); b.dataset.k=c.k; b.dataset.t=c.t; b.dataset.c='0'; mmFoodAdd(b); if(!_mmSelectedMetrics.includes('steps')) toggleMMMetric('steps')})()"); page.wait_for_timeout(900)
    t = ev("buildCompareMetricsSummaryText()")
    if 'Zzqx Whey Protein' not in t: f.add('BUG', f'1: copied summary has the food line: {t[:300]!r}')
    if 'not a cause' not in t or 'averaged' not in t: f.add('BUG', f'2: summary carries the days with/without note: {t[-300:]!r}')
    if 'NaN' in t or 'undefined' in t: f.add('BUG', f'3: no NaN/undefined in the summary: {t!r}')
    ev("_mmSelectedMetrics=_mmSelectedMetrics.filter(k=>k.startsWith('food')); renderMMChart()"); page.wait_for_timeout(500)
    t2 = ev("buildCompareMetricsSummaryText()")
    if 'averaged' in t2: f.add('BUG', f'4: no stale note when no second line is ticked: {t2[-200:]!r}')
    if errs: f.add('BUG', f'page errors {errs}')
print('findings', len(f)); [print(v) for v in f]; sys.exit(1 if f else 0)
