"""Persona 187 (v3.10.1084): Trends chart colour override per card; hostile values refused; reset."""
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
    page.evaluate("state.onboarded=true; saveState()"); page.evaluate("startDemoMode('alex')") if False else None
    ev=page.evaluate
    ev("""(()=>{const d=n=>{const x=new Date();x.setDate(x.getDate()-n);return String(x.getDate()).padStart(2,'0')+'/'+String(x.getMonth()+1).padStart(2,'0')+'/'+String(x.getFullYear()).slice(2)};
      state.history=[...Array(14).keys()].map(i=>({date:d(i),weight:80-i*0.1,totals:{kcal:1900,protein:100,carbs:25,fat:100},log:[],exercises:[]}));saveState();})()""")
    page.reload(); page.wait_for_timeout(1500)
    ev("switchTabById('trends')"); ev("trendsWindow='30'; renderTrends()"); page.wait_for_timeout(1000)
    check('chart colour swatch is on Trends cards', ev("document.querySelectorAll('.mh-chart-colour').length")>0)
    cid=ev("document.getElementById('chartWeight')?'chartWeight':null")
    check('weight chart exists', cid=='chartWeight')
    ev("mhChartSetColour('chartWeight','#ff0000'); renderTrends()"); page.wait_for_timeout(600)
    col=ev("chartInstances['chartWeight'].data.datasets[0].borderColor")
    check('override applied to the main series', col=='#ff0000', str(col))
    check('reference lines untouched', ev("chartInstances['chartWeight'].data.datasets[1].borderColor")!='#ff0000')
    ev("mhChartSetColour('chartWeight','red;x')"); check('hostile colour refused and cleared', 'chartWeight' not in ev("mhChartColours()"))
    check('no JS errors', not errs, str(errs[:2]))
print('p187: ALL PASS' if not bad else 'p187 FAILED: '+', '.join(bad))
