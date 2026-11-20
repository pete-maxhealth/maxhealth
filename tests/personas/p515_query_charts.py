"""Persona 515 (v3.10.1440): saved-query charts on Statistics. A day-based statistic can be limited to the days a Reports saved query matches; Chart button on the saved query; copy survives deleting the query; tag queries keep their tag; demo shows one working."""
import sys, re, json; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    br = pw.chromium.launch(); ctx = br.new_context(viewport={'width': 390, 'height': 900}, service_workers='block'); pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    pg.goto('http://localhost:5757/?demo=alex'); pg.wait_for_timeout(3500)
    pg.evaluate("var o=document.getElementById('onboardingOverlay'); if(o) o.style.display='none'")
    # 1. the demo carries a working one
    pg.evaluate("switchTab('insights'); switchSubTab('insights','stats'); mhStatsOpen()"); pg.wait_for_timeout(800)
    txt = pg.inner_text('#statsList')
    'Sleep on days over' in txt or f.add('FAIL', 'demo statistic missing from the Statistics screen')
    m = re.search(r'(\d+) of (\d+) days matched', txt)
    exp = pg.evaluate("(()=>{const TH=parseFloat(mhStatLoad().find(x=>x.id==='st_demo_active').filter.val1);const c=new Date();c.setDate(c.getDate()-90);c.setHours(0,0,0,0);const a=state.history.filter(d=>{const x=parseDateStr(d.date);return x&&x>=c});return [a.filter(d=>(d.totals&&d.totals.kcal>TH)).length,a.length]})()")
    if not m: f.add('FAIL', 'no "N of M days matched" line on the card')
    elif [int(m.group(1)), int(m.group(2))] != exp: f.add('FAIL', f'matched {m.group(1)} of {m.group(2)}, expected {exp}')
    # 2. Chart button on the saved query opens the builder already set up
    pg.evaluate("switchTab('insights'); switchSubTab('insights','reports'); renderSavedQueries()"); pg.wait_for_timeout(500)
    pg.get_by_role('button', name='Chart').first.click(); pg.wait_for_timeout(900)
    b = pg.inner_text('#statsBuilder')
    ('Higher-calorie days' in b and 'ONLY DAYS WHEN' in b) or f.add('FAIL', 'Chart button did not open a builder with the saved query chosen')
    pg.evaluate("mhStatSaveDraft()"); pg.wait_for_timeout(600)
    n = pg.evaluate("mhStatLoad().filter(x=>x.filter&&x.filter.metric==='kcal').length")
    n == 2 or f.add('FAIL', f'expected 2 filtered statistics after saving, got {n}')
    # 3. choosing Every day removes the filter; the matched line goes
    sid = pg.evaluate("mhStatLoad().find(x=>x.name==='Higher-calorie days').id")
    pg.evaluate(f"mhStatEdit('{sid}')"); pg.wait_for_timeout(400); pg.evaluate("mhStatSet('filter','')"); pg.evaluate("mhStatSaveDraft()"); pg.wait_for_timeout(500)
    pg.evaluate(f"!!mhStatLoad().find(x=>x.id==='{sid}').filter") and f.add('FAIL', 'filter still stored after choosing Every day')
    # 4. the copy survives deleting the saved query; backup carries it
    pg.evaluate("localStorage.setItem('mh_saved_queries','[]')")
    r = pg.evaluate("(()=>{const d=mhStatLoad().find(x=>x.id==='st_demo_active');const res=mhStatRun(d);return {filt:!!res.filt,matched:res.filt&&res.filt.matched,backup:JSON.stringify(buildFullBackupPayload()).includes('Higher-calorie days')}})()")
    r['filt'] or f.add('FAIL', 'statistic stopped filtering after the saved query was deleted')
    r['backup'] or f.add('FAIL', 'statistic filter missing from the full backup')
    # 5. tag queries keep their tag (saved empty before)
    t = pg.evaluate("""(()=>{document.getElementById('rptQueryName').value='Tagged x';document.getElementById('rptQueryMetric').value='tag';document.getElementById('rptQueryTagVal').value='  Holiday ';saveReportQuery();const q=JSON.parse(localStorage.getItem('mh_saved_queries')||'[]').pop();return q&&q.val1})()""")
    t == 'Holiday' or f.add('FAIL', f'tag query saved with value {t!r}')
    # 6. text/export carries the filter; non-day statistics drop it
    tx = pg.evaluate("mhStatText(mhStatLoad().find(x=>x.id==='st_demo_active'))")
    'only days when Calories above' in tx or f.add('FAIL', 'text export missing the filter')
    pg.evaluate("mhStatNormalise({subject:'foods',measure:'kcal',filter:{metric:'steps',op:'gt',val1:'1'}}).filter") and f.add('FAIL', 'foods statistic kept a day filter')
    # 7. matching vs other days: sleep on the active days, checked against an independent average
    c = pg.evaluate("""(()=>{const d=mhStatLoad().find(x=>x.id==='st_demo_active');const TH=parseFloat(mhStatLoad().find(x=>x.id==='st_demo_active').filter.val1);const def=Object.assign({},d,{measure:'sleep',filter:{name:'a',metric:'kcal',op:'gt',val1:String(TH),val2:''}});const r=mhStatRun(def);
      const cut=new Date();cut.setDate(cut.getDate()-90);cut.setHours(0,0,0,0);const a=state.history.filter(x=>{const t=parseDateStr(x.date);return t&&t>=cut});
      const av=l=>{const v=l.filter(x=>x.sleep_duration>0).map(x=>x.sleep_duration/60);return v.length?v.reduce((p,q)=>p+q,0)/v.length:null};
      return {got:r.filt.inAvg,exp:av(a.filter(x=>(x.totals&&x.totals.kcal>TH))),gotO:r.filt.outAvg,expO:av(a.filter(x=>!((x.totals&&x.totals.kcal>TH)))),html:mhStatRender(r).includes('on the other days'),same:mhStatRun(Object.assign({},d,{measure:'kcal'})).filt.inAvg==null}})()""")
    (c['got'] is not None and abs(c['got'] - c['exp']) < 0.01 and abs(c['gotO'] - c['expO']) < 0.01) or f.add('FAIL', f'matching/other averages wrong: {c}')
    c['html'] or f.add('FAIL', 'comparison line missing from the card')
    c['same'] or f.add('FAIL', 'comparison shown when measuring the query\'s own column')
    # 8. every demo persona gets a card with days on both sides of its own middle step count
    for per in ['maria', 'sam', 'doris', 'john', 'raj']:
        pg.goto('http://localhost:5757/?demo=' + per); pg.wait_for_timeout(3000)
        r = pg.evaluate("(()=>{const d=mhStatLoad().find(x=>x.id==='st_demo_active');if(!d)return null;const r=mhStatRun(d);return {m:r.filt.matched,o:r.filt.of,cmp:r.filt.inAvg!=null,rows:r.rows.length}})()")
        if not r: f.add('FAIL', per + ': demo statistic missing')
        elif r['m'] < 3 or r['o'] - r['m'] < 3 or not r['cmp'] or not r['rows']: f.add('FAIL', f'{per}: demo statistic has too little to show: {r}')
    for e in errs: f.add('JS-exception', e)
print('findings', len(f))
