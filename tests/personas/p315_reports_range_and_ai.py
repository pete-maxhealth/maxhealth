"""Persona 315 (v3.10.1215): Reports date range and Include today redraw every card that follows them at once (Exercise moved to Move in v3.10.1216 and has its own range, see p323); Ask AI keeps its answer area on screen while thinking (no jump to the top); the AI context carries age, sex, height and latest weight; Your Journey has a Fat chip; the Add foods row says what Have now and One serving mean."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("startDemoMode('alex')"); page.wait_for_timeout(2500)
    ev("switchTabById('reports')"); page.wait_for_timeout(800)
    sl = lambda: ev("(document.getElementById('sleep-report-content')||{innerText:''}).innerText.replace(/\\s+/g,' ').slice(0,120)")
    ev("setReportRange(7, document.getElementById('rpt-range-7'))"); page.wait_for_timeout(400); s7 = sl()
    ev("setReportRange(0, document.getElementById('rpt-range-all'))"); page.wait_for_timeout(400); sa = sl()
    if not s7 or s7 == sa: f.add('BUG', f'the Sleep card follows the date range too: "{s7}" vs "{sa}"')
    # Journey fat chip
    if 'fat' not in ev("mhJourneyOverlayDefs().map(o=>o.key)"): f.add('BUG', 'Your Journey has a Fat chip')
    # profile line
    ev("localStorage.setItem('mh_age','56'); localStorage.setItem('mh_sex','male'); localStorage.setItem('mh_height_cm','180')")
    pl = ev("mhProfileLine()")
    if 'Age 56' not in pl or 'Height 180cm' not in pl or 'Sex male' not in pl: f.add('BUG', f'the AI context has the profile: {pl}')
    # Ask AI keeps its area on screen while thinking
    ev("document.getElementById('rpt-ask-output').style.display='none'")
    ev("window.callAI = window.callAI || null")
    ev("window.mhCheckOnline = async function(){ return true; }")
    ev("(function(){ window.fetch = function(){ return new Promise(()=>{}); }; })()")
    ev("document.getElementById('rptAskInput').value='How am I doing?'; void askReportsAI(); 0"); page.wait_for_timeout(400)
    if ev("document.getElementById('rpt-ask-output').style.display") == 'none': f.add('BUG', 'the answer area stays on screen while thinking')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
