"""Persona 78: hiding cards then reordering (arrow buttons) must never bring hidden cards back, on every screen that has hide + reorder."""
import sys, re; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("localStorage.setItem('mh_onboarded','1')"); page.reload(); page.wait_for_timeout(1500)
    shown = lambda ids: page.evaluate("(ids)=>ids.filter(i=>{const e=document.getElementById(i);return e&&getComputedStyle(e).display!=='none'})", ids)
    # Generic scopes: hide two, then press the real up/down buttons on others
    for scope, tab, sub in (('manage','settings','manage'),('reports','insights','reports'),('trends','insights',None),('import','settings','import')):
        page.evaluate("([s,t,u])=>{switchTab(t); if(u) switchSubTab(t,u); mhTopicApply&&mhTopicApply(s)}", [scope, tab, sub]); page.wait_for_timeout(400)
        keys = page.evaluate("(s)=>getGenericOrder(s)", scope)
        if len(keys) < 4: continue
        ids = page.evaluate("(s)=>Object.fromEntries(Object.entries(GENERIC_SECTION_IDS[s]).map(([k,v])=>[k,v[0]]))", scope)
        hide = keys[:2]
        for k in hide: page.evaluate("([s,k])=>toggleGenericSectionHidden(s,k)", [scope, k])
        for k in (keys[2], keys[3], keys[2]):
            page.evaluate("([s,k])=>moveGenericSection(s,k,'down')", [scope, k]); page.wait_for_timeout(100)
        vis = page.evaluate("([s,hide])=>hide.filter(k=>genericUnitFor(s,k).some(e=>getComputedStyle(e).display!=='none'))", [scope, hide])
        if vis: f.add('BUG', f'{scope}: hidden cards reappeared after reorder: {vis}')
        # clicking the real arrow button in the DOM
        btn = page.evaluate("([s,k])=>{const t=document.getElementById(GENERIC_SECTION_IDS[s][k][0]);return [...(t?t.querySelectorAll('[onclick*=moveGenericSection]'):[])].length}", [scope, keys[3]])
        print(scope, 'order buttons on a card:', btn)
    # Dashboard
    page.evaluate("switchTab('dashboard')"); page.wait_for_timeout(400)
    page.evaluate("['weight','ketosis'].forEach(k=>toggleDashboardSectionHidden(k)); moveDashboardSection('macros','down'); moveDashboardSection('macros','down'); updateDashboard&&updateDashboard();"); page.wait_for_timeout(400)
    vis = page.evaluate("DASHBOARD_SECTION_IDS.weight.concat(DASHBOARD_SECTION_IDS.ketosis).filter(i=>{const e=document.getElementById(i);return e&&getComputedStyle(e).display!=='none'})")
    if vis: f.add('BUG', f'dashboard: hidden cards back after reorder/update: {vis}')
    # Trends cards
    page.evaluate("switchTab('insights'); renderTrends()"); page.wait_for_timeout(500)
    page.evaluate("['mcWeight','mcHR'].forEach(k=>toggleTrendCardHidden(k)); moveTrendCard('mcSpO2','down'); moveTrendCard('mcSteps','up'); renderTrends();"); page.wait_for_timeout(500)
    vis = page.evaluate("['mcWeight','mcHR'].filter(i=>getComputedStyle(document.getElementById(i)).display!=='none')")
    if vis: f.add('BUG', f'trend cards: hidden back: {vis}')
    # Library
    print('errors', errs[:2])
print('findings', len(f)); sys.exit(1 if f else 0)
