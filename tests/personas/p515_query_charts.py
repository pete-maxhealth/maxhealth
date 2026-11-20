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
    'Days I topped 8,000 steps' in txt or f.add('FAIL', 'demo statistic missing from the Statistics screen')
    m = re.search(r'(\d+) of (\d+) days matched', txt)
    exp = pg.evaluate("(()=>{const c=new Date();c.setDate(c.getDate()-90);c.setHours(0,0,0,0);const a=state.history.filter(d=>{const x=parseDateStr(d.date);return x&&x>=c});return [a.filter(d=>d.steps>8000).length,a.length]})()")
    if not m: f.add('FAIL', 'no "N of M days matched" line on the card')
    elif [int(m.group(1)), int(m.group(2))] != exp: f.add('FAIL', f'matched {m.group(1)} of {m.group(2)}, expected {exp}')
    # 2. Chart button on the saved query opens the builder already set up
    pg.evaluate("switchTab('insights'); switchSubTab('insights','reports'); renderSavedQueries()"); pg.wait_for_timeout(500)
    pg.get_by_role('button', name='Chart').first.click(); pg.wait_for_timeout(900)
    b = pg.inner_text('#statsBuilder')
    ('Active days' in b and 'ONLY DAYS WHEN' in b) or f.add('FAIL', 'Chart button did not open a builder with the saved query chosen')
    pg.evaluate("mhStatSaveDraft()"); pg.wait_for_timeout(600)
    n = pg.evaluate("mhStatLoad().filter(x=>x.filter&&x.filter.metric==='steps').length")
    n == 2 or f.add('FAIL', f'expected 2 filtered statistics after saving, got {n}')
    # 3. choosing Every day removes the filter; the matched line goes
    sid = pg.evaluate("mhStatLoad().find(x=>x.name==='Active days').id")
    pg.evaluate(f"mhStatEdit('{sid}')"); pg.wait_for_timeout(400); pg.evaluate("mhStatSet('filter','')"); pg.evaluate("mhStatSaveDraft()"); pg.wait_for_timeout(500)
    pg.evaluate(f"!!mhStatLoad().find(x=>x.id==='{sid}').filter") and f.add('FAIL', 'filter still stored after choosing Every day')
    # 4. the copy survives deleting the saved query; backup carries it
    pg.evaluate("localStorage.setItem('mh_saved_queries','[]')")
    r = pg.evaluate("(()=>{const d=mhStatLoad().find(x=>x.id==='st_demo_active');const res=mhStatRun(d);return {filt:!!res.filt,matched:res.filt&&res.filt.matched,backup:JSON.stringify(buildFullBackupPayload()).includes('Active days')}})()")
    r['filt'] or f.add('FAIL', 'statistic stopped filtering after the saved query was deleted')
    r['backup'] or f.add('FAIL', 'statistic filter missing from the full backup')
    # 5. tag queries keep their tag (saved empty before)
    t = pg.evaluate("""(()=>{document.getElementById('rptQueryName').value='Tagged x';document.getElementById('rptQueryMetric').value='tag';document.getElementById('rptQueryTagVal').value='  Holiday ';saveReportQuery();const q=JSON.parse(localStorage.getItem('mh_saved_queries')||'[]').pop();return q&&q.val1})()""")
    t == 'Holiday' or f.add('FAIL', f'tag query saved with value {t!r}')
    # 6. text/export carries the filter; non-day statistics drop it
    tx = pg.evaluate("mhStatText(mhStatLoad().find(x=>x.id==='st_demo_active'))")
    'only days when Steps above 8000' in tx or f.add('FAIL', 'text export missing the filter')
    pg.evaluate("mhStatNormalise({subject:'foods',measure:'kcal',filter:{metric:'steps',op:'gt',val1:'1'}}).filter") and f.add('FAIL', 'foods statistic kept a day filter')
    for e in errs: f.add('JS-exception', e)
print('findings', len(f))
