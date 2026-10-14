"""Persona 153: Trends 'Edit this day by hand' opens that day's totals editor (Log > History > Edit day totals) when the day has food; a day with no food falls back to Manual Entry, which is shown again even if the person had hidden that card."""
import sys; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
def ddmmyy(back): 
    return f"(()=>{{const d=new Date(); d.setDate(d.getDate()-{back}); return String(d.getDate()).padStart(2,'0')+'/'+String(d.getMonth()+1).padStart(2,'0')+'/'+String(d.getFullYear()).slice(2)}})()"
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev = page.evaluate
    d3 = ev(ddmmyy(3))
    ev("state.history.push({date:%r, totals:{kcal:2100,protein:120,fat:90,carbs:35,fibre:10,polyols:0,sugar:5,sodium:0}, water_ml:1500, entries:[], items:[], exercises:[]}); saveState()" % d3)
    # case 1: day with food -> day totals editor
    ev("switchTab('insights'); setTrendsFilter('today',document.getElementById('trendsBtnToday')); _trendsDayOffset=-3; renderTrends()"); page.wait_for_timeout(800)
    ev("mhEditTrendsDay()"); page.wait_for_timeout(1500)
    r = ev("(()=>{const f=document.querySelector('.hist-day-totals-edit'); const t=f?f.getBoundingClientRect().top:-1; return {logActive:document.getElementById('logtab-hist').classList.contains('active'), form:!!f, vis:!!(f&&f.offsetParent), inView:t>=0&&t<800}})()")
    if not (r['logActive'] and r['form'] and r['vis'] and r['inView']): f.add('BUG', f'day with food did not open the day totals editor {r}')
    # case 2: day without food, Manual Entry hidden -> shown again with that date
    ev("switchTab('settings'); switchSubTab('settings','import')"); page.wait_for_timeout(400)
    if 'imp-manual' not in ev("getGenericHidden('import')"): ev("toggleGenericSectionHidden('import','imp-manual')")
    ev("switchTab('insights'); _trendsDayOffset=-5; renderTrends(); mhEditTrendsDay()"); page.wait_for_timeout(1800)
    r = ev("(()=>{const e=document.getElementById('manualEntryDate'); const w=document.getElementById('imp-manual-wrap'); const t=w.getBoundingClientRect().top; const d=new Date(); d.setDate(d.getDate()-5); const iso=d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0'); return {ok:e&&e.value===iso, vis:!!w.offsetParent, inView:t>=0&&t<760, hidden:getGenericHidden('import').includes('imp-manual')}})()")
    if not (r['vis'] and r['inView'] and r['ok']) or r['hidden']: f.add('BUG', f'food-less day did not show Manual Entry for that date {r}')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
