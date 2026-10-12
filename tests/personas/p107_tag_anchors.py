"""Persona 107: day tags as before/during/after anchors (alongside treatments): tag + category anchors, >=3 days rule, picker lists them, defaults stay treatments only, no page errors."""
import sys; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("localStorage.setItem('mh_onboarded','1')"); page.reload(); page.wait_for_timeout(1500)
    ev = page.evaluate
    if ev("mhAnchorDefs().some(d=>d.isTag)"): f.add('BUG', 'tag anchors with no tags')
    ev("""(()=>{ const dmy=n=>{const d=new Date(Date.now()-n*864e5);return String(d.getDate()).padStart(2,'0')+'/'+String(d.getMonth()+1).padStart(2,'0')+'/'+String(d.getFullYear()).slice(2);};
      const h=[]; for(let i=1;i<=14;i++){ const tagged=[2,5,8,11].includes(i); h.push({date:dmy(i),log:[],totals:{kcal:1000,protein:50,carbs:20,fat:50},mode:'standard',notes:tagged?'Treatment: Acupuncture, 30min walk':(i===3?'Exercise: Swim':'standard'),weight:90+i*0.1}); }
      state.history=h; })()""")
    names = ev("mhAnchorDefs().map(d=>d.id)")
    for need in ['tag:treatment: acupuncture', 'tag:exercise: swim', 'tagcat:treatment', 'tagcat:exercise']:
        if need not in names: f.add('BUG', f'missing anchor {need}: {names}')
    if ev("mhAnchorSessions('tag:treatment: acupuncture').length") != 4: f.add('BUG', 'tag days not 4')
    if ev("mhAnchorSessions('tagcat:treatment').length") != 4: f.add('BUG', 'category days not 4')
    if any('min' in n for n in names): f.add('BUG', 'activity summary became a tag')
    st = ev("computeTreatmentSessionStats('tag:treatment: acupuncture','weight',1,'0')")
    if st['insufficientData'] or not st['during'] or not st['before'] or not st['after']: f.add('BUG', f'stats {st}')
    st2 = ev("computeTreatmentSessionStats('tag:exercise: swim','weight',1,'0')")
    if not st2['insufficientData']: f.add('BUG', 'single day should be insufficient')
    ev("renderTreatmentSessionsPicker()")
    sec = ev("document.getElementById('treatment-sessions-content').innerText")
    if 'Acupuncture' not in sec: f.add('BUG', 'picker does not list tag')
    if ev("_treatmentSessionsSelected.some(i=>i.indexOf('tag')===0)"): f.add('BUG', 'tags selected by default')
    ev("toggleTreatmentSessionPill('tag:treatment: acupuncture'); toggleTreatmentMetricPill('weight')")
    if 'Acupuncture' not in ev("document.getElementById('treatmentSessionsResult').innerText"): f.add('BUG', 'result missing tag block')
    pills = ev("getAllOverlayableMetrics().filter(m=>m.isTag).map(m=>m.key)")
    if 'tag_treatment: acupuncture' not in pills: f.add('BUG', f'no tag pill {pills}')
    if 'tag_exercise: swim' in pills: f.add('BUG', 'single-day tag became a pill')
    ev("_mmSelectedMetrics=['weight','tag_treatment: acupuncture']; openMultiMetricOverlay()"); page.wait_for_timeout(600)
    if 'Acupuncture' not in ev("document.getElementById('multiMetricOverlay').innerText"): f.add('BUG', 'pill not in overlay')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
