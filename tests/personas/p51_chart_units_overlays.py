"""Persona 51: charts follow the chosen weight unit (series stay kg), Compare Metrics gains fat / logged exercise / active calories, Journey has overlay chips whose choice persists."""
import sys, re; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    ctx.route(re.compile(r'https://(cdn\.jsdelivr\.net|cdnjs\.cloudflare\.com|fonts\.(googleapis|gstatic)\.com)/.*'), lambda r: r.abort())
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:160]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200)
    page.evaluate("localStorage.setItem('mh_weight_unit','lbs')")
    cv = page.evaluate("[mhChartCv('weight',90.7), mhChartCv('bone_mass',3.0), mhChartCv('hr',60), mhChartUnit('weight','kg'), mhChartUnit('hr','bpm'), mhChartCv('weight',null)]")
    if abs(cv[0]-200) > 0.2 or abs(cv[1]-6.6) > 0.1 or cv[2] != 60 or cv[3] != 'lb' or cv[4] != 'bpm' or cv[5] is not None:
        f.add('BUG', f'chart converters wrong in lbs: {cv}')
    page.evaluate("localStorage.setItem('mh_weight_unit','st')")
    if page.evaluate("mhChartUnit('weight','kg')") != 'lb': f.add('BUG', 'st charts should use lb axis')
    page.evaluate("localStorage.setItem('mh_weight_unit','kg')")
    if page.evaluate("mhChartCv('weight',90.7)") != 90.7 or page.evaluate("mhChartUnit('weight','kg')") != 'kg': f.add('BUG', 'kg charts changed')
    # data: exercise + active cal flow through getDrillData
    page.evaluate("""state.history = [
      {date:'01/10/26', weight:90, totals:{kcal:2000,protein:150,carbs:30,fat:150}, exercises:[{kcal:200},{kcal:150}], calories_active:640, water_ml:2000, steps:8000},
      {date:'02/10/26', weight:89.5, totals:{kcal:2100,protein:140,carbs:40,fat:140}, exercises:[], calories_active:500, water_ml:1500, steps:6000},
      {date:'03/10/26', weight:89.2, totals:{kcal:1900,protein:160,carbs:20,fat:120}, exercises:[{kcal:300}], water_ml:2500, steps:9000}];""")
    ex = page.evaluate("getDrillData('exercise_kcal',0).map(d=>d.val)")
    if ex != [350, 300]: f.add('BUG', f'exercise_kcal series wrong: {ex}')
    ac = page.evaluate("getDrillData('active_cal',0).map(d=>d.val)")
    if ac != [640, 500]: f.add('BUG', f'active_cal series wrong: {ac}')
    grp = page.evaluate("MM_METRIC_GROUPS.map(g=>[g.label, getAllOverlayableMetrics().filter(g.match).map(m=>m.key)])")
    d = dict((a, b2) for a, b2 in grp)
    if 'fat' not in d['Nutrition']: f.add('BUG', f"fat missing from Compare Metrics: {d['Nutrition']}")
    if 'exercise_kcal' not in d['Exercise'] or 'active_cal' not in d['Exercise']: f.add('BUG', f"exercise metrics missing: {d['Exercise']}")
    allkeys = [k for _, ks in grp for k in ks if not k.startswith(('symptom_', 'treatment_'))]
    base = page.evaluate("Object.keys(DRILL_CONFIG).filter(k=>!DRILL_CONFIG[k].isLabMarker)")
    miss = [k for k in base if k not in allkeys]
    if miss: f.add('BUG', f'metrics in no Compare group (invisible): {miss}')
    # journey chips
    page.evaluate("switchTabById('trends')"); page.wait_for_timeout(800)
    page.evaluate("renderJourneyCard()")
    n = page.evaluate("document.querySelectorAll('#journeyOverlayBar [data-jov]').length")
    if n != 7: f.add('BUG', f'expected 7 journey chips, got {n}')
    page.evaluate("mhJourneyToggleOverlay('exercise'); mhJourneyToggleOverlay('water')")
    if sorted(page.evaluate("mhJourneyOverlayKeys()")) != ['exercise', 'water']: f.add('BUG', 'overlay choice not saved')
    page.reload(); page.wait_for_timeout(1500)
    if sorted(page.evaluate("mhJourneyOverlayKeys()")) != ['exercise', 'water']: f.add('BUG', 'overlay choice lost on reload')
    page.evaluate("mhJourneyToggleOverlay('water')")
    if page.evaluate("mhJourneyOverlayKeys()") != ['exercise']: f.add('BUG', 'overlay untoggle failed')
    vals = page.evaluate("mhJourneyOverlayDefs().find(o=>o.key==='exercise').get({exercises:[{kcal:200},{kcal:150}]})")
    if vals != 350: f.add('BUG', f'journey exercise getter: {vals}')
    # day panel shows real overlay values
    page.evaluate("showJourneyDayPanel(0, [{date:'01/10/26', weight:90, exercises:[{kcal:200},{kcal:150}]}], ['#2deb8f'])")
    pt = page.evaluate("document.getElementById('journeyDayPanel').textContent")
    if '350' not in pt: f.add('BUG', f'journey day panel missing exercise value: {pt!r}')
    if errs: f.add('BUG', f'page errors: {errs[:3]}')
    b.close()
print("findings", len(f)); sys.exit(1 if f else 0)
