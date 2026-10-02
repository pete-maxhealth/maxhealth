"""Persona 28: the connection is dead-but-not-off (roaming / no signal): external requests HANG, never fail.
The app must load fast, stay usable, show the offline banner, and PDF/zip must work from the bundled libraries."""
import sys, re, json, time; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
def S(page): return page.evaluate("JSON.parse(localStorage.getItem('maxhealth_v1')||'{}')")
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []; hung = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: hung.append(r.request.url))   # never answered
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:160])); page.on('dialog', lambda d: d.accept())
    t = time.time(); page.goto('http://localhost:5757/', wait_until='domcontentloaded', timeout=15000)
    load = time.time() - t
    if load > 4: f.add('BUG', f'page took {load:.1f}s to load with a dead connection')
    page.wait_for_timeout(1000)
    blocking = [u for u in hung if not u.startswith('https://fonts.')]
    if blocking: f.add('BUG', f'page still asks the internet for: {blocking[:4]}')
    # onboarding and normal use with the connection dead
    page.evaluate("onboardNext(2)"); page.fill('#onboardName', 'Ola'); page.evaluate("onboardNext(3)")
    page.evaluate("obSetSex('male')"); page.fill('#onboardAge', '58'); page.fill('#onboardHeight', '176')
    page.fill('#onboardWeight', '82'); page.fill('#onboardTarget', '78')
    page.evaluate("onboardNext(4)"); page.evaluate("obSetActivity('light')"); page.evaluate("obSetGoal('lose')")
    page.evaluate("onboardNext(5)"); page.evaluate("obSetCondition('general')")
    page.evaluate("onboardNext(6)"); page.evaluate("onboardFinish()"); page.wait_for_timeout(1500)
    for tab in ('today', 'log', 'trends', 'insights', 'settings'):
        try:
            page.click(f"[onclick^=\"switchTab('{tab}'\"]", timeout=3000); page.wait_for_timeout(300)
        except Exception: pass
    page.click("[onclick^=\"switchTab('log'\"]"); page.wait_for_timeout(300)
    page.evaluate("processMessage('two boiled eggs')"); page.wait_for_timeout(1200)
    page.evaluate("confirmMealLog()"); page.wait_for_timeout(600)
    page.evaluate("[...document.querySelectorAll('button')].find(b=>/log it as-is/i.test(b.innerText))?.click()"); page.wait_for_timeout(800)
    if len(S(page).get('todayLog') or []) != 1: f.add('BUG', 'could not log a common food with the connection dead')
    # a meal the local database cannot read: AI call hangs -> must not freeze, must offer save-for-later
    page.evaluate("localStorage.setItem('mh_provider','claude');localStorage.setItem('mh_apikey','sk-ant-test-123')")
    page.evaluate("processMessage('homemade lentil and chorizo stew with kale')"); page.wait_for_timeout(1500)
    page.wait_for_function("document.getElementById('mhNetBar').className==='off' || /save it for when/i.test(document.getElementById('chatScroll').innerText)", timeout=15000)
    # offline banner appears once the app notices
    page.evaluate("fetch('https://example.com/x',{signal:AbortSignal.timeout(500)}).catch(()=>{})"); page.wait_for_timeout(7000)
    if page.evaluate("document.getElementById('mhNetBar').className") != 'off': f.add('BUG', 'no offline banner with a hung connection')
    # PDF made from the bundled libraries (no internet)
    ok = page.evaluate("typeof window.jspdf!=='undefined' && typeof window.jspdf.jsPDF==='function' && typeof new window.jspdf.jsPDF().autoTable==='function'")
    if not ok: f.add('BUG', 'jsPDF / autotable not available offline')
    size = page.evaluate("""async()=>{const b=buildProfileReportPDF({name:'Ola',orgColor:'#1a8f6a'},{},'Progress 1-7 Oct',[['Date','Weight','Steps'],['01/10/26','82','5000'],['02/10/26','81.8','6100']],false);return b?b.size:0}""")
    if size < 3000: f.add('BUG', f'PDF not produced offline (size {size})')
    if not page.evaluate("typeof JSZip==='function'"): f.add('BUG', 'JSZip not available offline')
    if errs: f.add('JS-exception', str(errs[:3]))
    b.close()
print('findings', len(f)); sys.exit(1 if f else 0)
