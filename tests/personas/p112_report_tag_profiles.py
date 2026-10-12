"""Persona 112: report profiles can be about a tag or a tag category (not just a treatment), with condition chips in the wizard, a saved profile lists it, and the report generates without errors."""
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
    ev("""(()=>{ const dmy=n=>{const d=new Date(Date.now()-n*864e5);return String(d.getDate()).padStart(2,'0')+'/'+String(d.getMonth()+1).padStart(2,'0')+'/'+String(d.getFullYear()).slice(2);};
      const h=[]; for(let i=1;i<=14;i++){ h.push({date:dmy(i),log:[],totals:{kcal:1000,protein:50,carbs:20,fat:50},mode:'standard',notes:[2,5,8,11].includes(i)?"Exercise: Swim, Nan's massage":'standard',weight:90+i*0.1}); }
      state.history=h; })()""")
    ids = ev("mhAnchorDefs().map(d=>d.id)")
    if "tag:exercise: swim" not in ids or 'tagcat:exercise' not in ids: f.add('BUG', f'anchors {ids}')
    odd = [i for i in ids if "'" in i]
    ev("openReportProfileWizard && openReportProfileWizard(null)") if ev("typeof openReportProfileWizard") == 'function' else None
    if not ev("!!document.getElementById('reportWizardModal')"): f.add('BUG', 'wizard did not open')
    else:
        ev("window._reportWizardDraft.name='Clinic'; reportWizardGoto(2)")
        txt = ev("document.getElementById('reportWizardScroll').innerText")
        if 'Swim' not in txt: f.add('BUG', 'tag not offered in wizard')
        for sel in ["[data-aid=\"tagcat:exercise\"]"]:
            page.click(sel); page.wait_for_timeout(200)
        if ev("window._reportWizardDraft.treatmentId") != 'tagcat:exercise': f.add('BUG', 'tag category not chosen')
        if odd:
            ev(f"window._reportWizardDraft.treatmentId={odd[0]!r}; renderReportWizardStep()")
    ev("window._reportWizardDraft.treatmentId='tag:exercise: swim'; window._reportWizardDraft.metrics=['weight']; saveReportProfiles([window._reportWizardDraft]); closeReportProfileWizard(); renderReportProfileList()")
    if 'Swim' not in ev("document.getElementById('reportProfileListInner').innerText"): f.add('BUG', 'saved profile does not show tag name')
    ev("navigator.canShare=()=>false; window.__links=[]; const o=document.createElement.bind(document); URL.createObjectURL=()=>'blob:x'; window.open=()=>null")
    ev("generateProfileReport(loadReportProfiles()[0].id)"); page.wait_for_timeout(1200)
    if 'no longer exists' in ev("(document.getElementById('toast')||{innerText:''}).innerText"): f.add('BUG', 'report says anchor missing')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
