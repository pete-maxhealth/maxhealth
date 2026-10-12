"""Persona 104: Settings > Setup > "Change my focus". Lists Everything plus the starter packs; the preview names the cards that tuck away; Switch replaces the layout with the pack's
(old arrangement gone), adds its symptoms without removing the person's own, never touches logged data; 'Show me everything' returns to the standard layout; the muscle growth pack is valid."""
import sys, re, json; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings(); R = '/home/claude/maxhealth/starter_packs/'
with fresh_server() as root, sync_playwright() as pw:
    ctx = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block'); errs = []
    def route(r):
        u = r.request.url
        if 'raw.githubusercontent.com' in u: r.fulfill(body=open(R + u.rsplit('/', 1)[1]).read(), content_type='application/json')
        elif u.startswith('http://localhost'): r.continue_()
        else: r.abort()
    ctx.route('**/*', route); page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("""localStorage.setItem('mh_onboarded','1'); localStorage.setItem('mh_dashboard_hidden','["weight"]'); localStorage.setItem('mh_collapse_dc_water','closed');
      saveSymptomDefs([{id:'mine1',name:'My own symptom',active:true}]); localStorage.setItem('mh_marker_log','keep')"""); page.reload(); page.wait_for_timeout(1800)
    page.evaluate("document.querySelectorAll('[id*=nboard]').forEach(e=>{ if(e.style) e.style.display='none'; })")
    ev = page.evaluate
    ev("switchTab('settings'); switchSubTab('settings','manage'); mhFocusOpen()"); page.wait_for_timeout(1200)
    body = ev("document.getElementById('mhFocusBody').innerText")
    for want in ('Show me everything', 'Muscle growth tracking', 'Strict keto tracking', 'Brain tumour tracking'):
        if want not in body: f.add('BUG', f'focus list missing {want}')
    ev("[...document.querySelectorAll('#mhFocusBody .copy-btn')].find(b=>b.closest('div').textContent.includes('Muscle growth')).click()"); page.wait_for_timeout(800)
    prev = ev("document.getElementById('mhFocusModal').innerText")
    if 'Ketosis' not in prev or 'Fasting' not in prev or 'Nothing you have logged is touched' not in prev: f.add('BUG', f'preview wrong: {prev[:300]}')
    with page.expect_navigation(): ev("document.getElementById('mhFocusGo').click()")
    page.wait_for_timeout(1800)
    r = ev("({hidden: localStorage.getItem('mh_dashboard_hidden'), water: localStorage.getItem('mh_collapse_dc_water'), wx: localStorage.getItem('mh_collapse_dc_wx'), syms: loadSymptomDefs().map(s=>s.name), marker: localStorage.getItem('mh_marker_log'), base: Object.keys(mhLayoutBase()).length})")
    if r['hidden'] != '["ketosis", "fasting"]': f.add('BUG', f'layout not swapped {r}')
    if r['water'] is not None: f.add('BUG', 'old arrangement survived the switch')
    if r['wx'] != 'closed' or r['base'] < 3: f.add('BUG', f'pack layout missing {r}')
    if 'My own symptom' not in r['syms'] or 'Muscle soreness' not in r['syms']: f.add('BUG', f'symptoms wrong {r["syms"]}')
    if r['marker'] != 'keep': f.add('BUG', 'logged data touched')
    # everything
    ev("mhFocusPreview({everything:true,title:'Show me everything'})")
    with page.expect_navigation(): ev("document.getElementById('mhFocusGo').click()")
    page.wait_for_timeout(1800)
    r = ev("({hidden: localStorage.getItem('mh_dashboard_hidden'), wx: localStorage.getItem('mh_collapse_dc_wx'), base: localStorage.getItem('mh_layout_base'), syms: loadSymptomDefs().map(s=>s.name)})")
    if r['hidden'] or r['wx'] or r['base']: f.add('BUG', f'everything did not reset {r}')
    if 'My own symptom' not in r['syms']: f.add('BUG', 'everything removed lists')
    # muscle pack validity
    d = json.load(open(R + 'muscle_growth_tracking.json'))
    if len(d['sets']['symptoms']['data']) != 7 or json.loads(d['sets']['layout']['data']['mh_dashboard_hidden']) != ['ketosis', 'fasting']: f.add('BUG', 'muscle pack content')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
