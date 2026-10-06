"""Persona 35: HRV shows whole ms (not 27.29901960784314); launcher floats are rounded on import; the weather setup inputs are a sensible size."""
import sys, re, json, os, tempfile; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
# server side: the extractor keeps 1 decimal on averages
sys.path.insert(0, os.path.join(REPO, 'extractors'))
import health_connect as hc
d = tempfile.mkdtemp(); json.dump([{'date': '05/10/26', 'hrv': 27.29901960784314, 'hrv_min': 24.1234567, 'steps': 11640, 'hr_avg': 61.456789}], open(os.path.join(d, 'health_connect_export.json'), 'w'))
r = hc.run(d)[0]
if r['hrv'] != 27.3 or r['hrv_min'] != 24.1 or r['hr_avg'] != 61.5: f.add('BUG', f'extractor did not round: {r}')
if r['steps'] != 11640: f.add('BUG', 'steps changed')
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:160]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("startDemoMode(DEMO_PERSONAS[0].id)"); page.wait_for_timeout(1500)
    page.evaluate("(()=>{const h=getReportHistory?state.history:state.history; state.history.forEach(e=>{e.hrv=27.29901960784314; e.hrv_min=24.123456789;});})()")
    page.evaluate("switchTab('insights')"); page.wait_for_timeout(1500)
    page.evaluate("trendsWindow = 30; renderTrends()"); page.wait_for_timeout(800)
    txt = page.evaluate("[document.getElementById('mcHRVVal')?.textContent, document.getElementById('mcHRVStatus')?.textContent, document.getElementById('statHRVMin')?.textContent, document.getElementById('statHRVMax')?.textContent].join(' | ')")
    if re.search(r'\d+\.\d{3,}', txt): f.add('BUG', 'HRV still shows long decimals: ' + txt)
    if '27' not in txt: f.add('check', 'HRV card did not show 27: ' + txt)
    # weather setup inputs are normal sized
    page.evaluate("switchTab('today')"); page.wait_for_timeout(400); page.evaluate("mhWxOpenSetup()"); page.wait_for_timeout(300)
    box = page.evaluate("(()=>{const i=document.getElementById('mhWxCity').getBoundingClientRect();const b=[...document.querySelectorAll('#mhWxCard button')].find(x=>/search/i.test(x.innerText)).getBoundingClientRect();return [i.width,i.height,b.width,b.height]})()")
    if box[0] < 150 or box[1] > 50: f.add('BUG', f'city input mis-sized {box}')
    if box[2] > 130: f.add('BUG', f'Search button too wide {box}')
    if errs: f.add('JS-exception', str(errs[:3]))
    b.close()
print('findings', len(f)); sys.exit(1 if f else 0)
