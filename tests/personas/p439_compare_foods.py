"""Persona 439: Foods in Compare Metrics (v3.10.1337). Pick any logged food or category, see grams a day (or times had), days with it against days without it, remove, reload.
Pete (9 Nov 2026): "include food as metrics ... as generic as possible, whilst remaining useful". Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
SHOT = '/tmp/claude-0/-home-claude/c032a46b-68f2-5aea-a854-98f1a5b7657c/scratchpad/p439_%s.png'
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); page = b.new_context(viewport={'width': 390, 'height': 900}, service_workers='block', device_scale_factor=2).new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); ev = page.evaluate
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200)
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay').style.display='none'")
    # 40 logged days (1..40 days ago); whey (25g) on odd days with high steps; cheese by count on every 3rd day; day 5 has no meals at all; day 6 meals but no whey
    ev("""(()=>{ const ds=n=>{const d=new Date(); d.setDate(d.getDate()-n); return String(d.getDate()).padStart(2,'0')+'/'+String(d.getMonth()+1).padStart(2,'0')+'/'+String(d.getFullYear()).slice(2)};
      const H=[]; for(let n=1;n<=40;n++){ const items=[{name:'Zzqx Chicken',amount:'150g',kcal:250,protein:40,fat:8,carbs:0}]; if(n%2===1) items.push({name:'Zzqx Whey Protein',amount:'25g',kcal:101,protein:20,fat:1.9,carbs:1});
        if(n%3===0) items.push({name:'Zzqx Cheddar Cheese',amount:'2 slices',kcal:200,protein:12,fat:16,carbs:1});
        H.push({date:ds(n), log: n===5?[]:[{description:'meal',items,time:'12:00'}], steps: n%2===1?9000:6000, totals:{kcal:500,protein:60,carbs:3,fat:20}}); }
      state.history=H; saveState(); window._ds=ds; })()""")
    ev("openMultiMetricOverlay()"); page.wait_for_timeout(700)
    # 1 group present although nothing picked yet
    if 'Foods' not in ev("document.getElementById('mmMetricPicker').innerText"): f.add('BUG', '1: the Foods group is not shown before any food is picked')
    ev("toggleMMGroup('Foods')"); page.wait_for_timeout(200)
    chips = ev("[...document.querySelectorAll('#mmFoodChips button')].map(b=>b.innerText.replace(/\\s+/g,' ').trim())")
    if not any('Zzqx Whey Protein' in c for c in chips) or not any('Zzqx Chicken' in c for c in chips): f.add('BUG', f'2: quick picks show the logged foods: {chips}')
    if not any(c.startswith('🗂') for c in chips): f.add('BUG', f'2b: quick picks include categories: {chips}')
    # search narrows
    page.fill('#mmFoodSearch', 'whey'); page.wait_for_timeout(200)
    chips = ev("[...document.querySelectorAll('#mmFoodChips button')].map(b=>b.dataset.t)")
    if chips != ['Zzqx Whey Protein']: f.add('BUG', f'3: searching "whey" gives just the whey: {chips}')
    # 4 add the whey: becomes a ticked pill, a chart line, saved
    page.locator('#mmFoodChips button').first.click(); page.wait_for_timeout(500)
    sel = ev("_mmSelectedMetrics.filter(k=>k.startsWith('food'))")
    if len(sel) != 1: f.add('BUG', f'4a: whey added and ticked: {sel}')
    S = ev("(()=>{const m=getAllOverlayableMetrics().find(x=>x.isFood && x.foodKey); if(!m) return null; _mmPeriod=0; const s=mmFoodSeries(m); return {unit:s.unit, n:s.points.length, withIt:s.points.filter(p=>p.val>0).length, zero:s.points.filter(p=>p.val===0).length, vals:[...new Set(s.points.map(p=>p.val))].sort((a,b)=>a-b), has5:s.points.some(p=>p.date===window._ds(5))}})()")
    if not S or S['unit'] != 'g' or S['vals'] != [0, 25]: f.add('BUG', f'4b: whey in grams, 25 on days had and 0 on other logged days: {S}')
    elif S['has5'] or S['n'] != 39: f.add('BUG', f'4c: the day with no meals is a gap, not a zero ({S})')
    dl = ev("(_mmChart ? _mmChart.data.datasets.map(d=>d.label+':'+d.data.length) : null)")
    if not dl or not any(x.startswith('Zzqx Whey Protein') for x in dl): f.add('BUG', f'4d: one line drawn for the whey: {dl}')
    # 5 count-only food shows times; category works
    ev("mmFoodAdd(Object.assign(document.createElement('b'),{}))") if False else None
    ev("""(()=>{ const i=mmFoodIndex(); const c=i.foods.get(_libNormaliseName('Zzqx Cheddar Cheese')); const b=document.createElement('button'); b.dataset.k=c.k; b.dataset.t=c.t; b.dataset.c='0'; mmFoodAdd(b); })()"""); page.wait_for_timeout(400)
    C = ev("(()=>{const m=getAllOverlayableMetrics().find(x=>x.isFood && x.foodKey && x.title.includes('Cheddar')); _mmPeriod=0; const s=mmFoodSeries(m); return {unit:s.unit, vals:[...new Set(s.points.map(p=>p.val))].sort((a,b)=>a-b)}})()")
    if C['unit'] != '×' or C['vals'] != [0, 1]: f.add('BUG', f'5a: a food logged by count shows times had: {C}')
    cat = ev("(()=>{const i=mmFoodIndex(); const cs=[...i.cats.values()].filter(c=>c.days.size>=10).map(c=>c.k); return cs})()")
    if not cat: f.add('BUG', '5b: there is at least one category from these foods')
    else:
        ev(f"(()=>{{ const b=document.createElement('button'); b.dataset.k={cat[0]!r}; b.dataset.t='Cat'; b.dataset.c='1'; mmFoodAdd(b); }})()"); page.wait_for_timeout(300)
        if not ev("getAllOverlayableMetrics().some(x=>x.foodCat)"): f.add('BUG', '5c: a category can be added')
    # 6 with / without: tick steps too
    ev("(()=>{ if(!_mmSelectedMetrics.includes('steps')) toggleMMMetric('steps'); })()"); page.wait_for_timeout(700)
    cmp = ev("document.getElementById('mmFoodCompare')?.innerText || ''")
    if 'averaged 9000' not in cmp or '6000' not in cmp or 'not a cause' not in cmp: f.add('BUG', f'6: days with / without comparison for steps: {cmp[:300]!r}')
    # 7 date range is respected
    ev("setMMPeriod(7, document.querySelector('#mmPeriodBtns .drill-period'))"); page.wait_for_timeout(500)
    R = ev("(()=>{const m=getAllOverlayableMetrics().find(x=>x.foodKey && x.title.includes('Whey')); const s=mmFoodSeries(m); return s.points.length})()")
    if R > 7 or R < 5: f.add('BUG', f'7: 7-day range gives about a week of points: {R}')
    ev("setMMPeriod(0, document.querySelectorAll('#mmPeriodBtns .drill-period')[3])")
    page.screenshot(path=SHOT % 'picker_dark')
    ev("document.documentElement.setAttribute('data-theme','light')"); page.wait_for_timeout(300); page.screenshot(path=SHOT % 'picker_light'); ev("document.documentElement.removeAttribute('data-theme')")
    # 8 reload keeps picks; remove works
    before = ev("mmFoodPicks().length")
    page.reload(); page.wait_for_timeout(1500); ev("document.getElementById('onboardingOverlay')&&(document.getElementById('onboardingOverlay').style.display='none')")
    if ev("mmFoodPicks().length") != before: f.add('BUG', '8a: picked foods survive a reload')
    ev("openMultiMetricOverlay()"); page.wait_for_timeout(600)
    key = ev("getAllOverlayableMetrics().find(x=>x.isFood && x.foodKey).key")
    ev(f"mmFoodRemove({key!r})"); page.wait_for_timeout(300)
    if ev(f"_mmSelectedMetrics.includes({key!r}) || mmFoodPicks().some(x=>('food_'+x.k)==={key!r})"): f.add('BUG', '8b: removing a food takes it out of the picks and the chart')
    if not ev("_mmSelectedMetrics.includes('steps')"): f.add('BUG', '8c: removing a food leaves the other ticked lines alone')
    # 9 neighbours
    grp = ev("document.getElementById('mmMetricPicker').innerText")
    for g in ['Body Composition', 'Exercise', 'Nutrition', 'Vitals']:
        if g.lower() not in grp.lower(): f.add('BUG', f'9: neighbouring group still there: {g}')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f]; sys.exit(1 if f else 0)
