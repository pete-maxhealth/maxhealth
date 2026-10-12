"""Persona 91: a starter pack can carry a screen layout. Preview lists it, import applies only layout keys (junk and non-layout keys refused),
merge never overrides a screen the person arranged, and the Default buttons return to the pack's layout rather than bare standard."""
import sys, re, json; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch()
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page = ctx.new_page(); errs = []; page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200)
    page.evaluate("localStorage.setItem('mh_onboarded','1')")
    r = page.evaluate("""() => {
      localStorage.setItem('mh_collapse_dc_water','open');
      const pack = {mhpack:1, sets:{layout:{label:'Screen layout',count:1,data:{
        mh_dashboard_hidden:'["ketosis"]', mh_collapse_dc_water:'closed', mh_collapse_dc_fasting:'closed',
        maxhealth_v1:'{"evil":1}', mh_api_key:'steal', mh_pills_open:'1', mh_collapse_dc_x:{a:1}}}}};
      const plan = mhPackPlan('layout', pack.sets.layout.data);
      const out = mhPackApply(pack, ['layout'], 'merge');
      const res = { plan: plan.text, out, hidden: localStorage.getItem('mh_dashboard_hidden'), water: localStorage.getItem('mh_collapse_dc_water'),
        fasting: localStorage.getItem('mh_collapse_dc_fasting'), evil: localStorage.getItem('maxhealth_v1'), key: localStorage.getItem('mh_api_key'),
        pills: localStorage.getItem('mh_pills_open'), x: localStorage.getItem('mh_collapse_dc_x'), base: Object.keys(mhLayoutBase()).sort() };
      // person changes things, then Default restores the pack layout
      localStorage.setItem('mh_dashboard_hidden','["weight","water"]'); localStorage.setItem('mh_collapse_dc_fasting','open');
      localStorage.setItem('mh_collapse_dc_extra','open');
      const keys = mhLayoutKeys(null);
      keys.forEach(k => localStorage.removeItem(k)); const base = mhLayoutBase(); keys.forEach(k => { if (k in base) localStorage.setItem(k, base[k]); });
      res.afterHidden = localStorage.getItem('mh_dashboard_hidden'); res.afterFasting = localStorage.getItem('mh_collapse_dc_fasting'); res.afterExtra = localStorage.getItem('mh_collapse_dc_extra');
      res.snap = Object.keys(mhLayoutSnapshot() || {});
      return res;
    }""")
    if r['hidden'] != '["ketosis"]': f.add('BUG', f"layout not applied: {r['hidden']}")
    if r['water'] != 'open': f.add('BUG', 'merge overrode a card the person had already arranged')
    if r['fasting'] != 'closed': f.add('BUG', 'merge did not set a missing layout key')
    if r['evil'] or r['key']: f.add('BUG', 'pack wrote a non-layout key')
    if r['pills'] or r['x']: f.add('BUG', 'pack wrote a refused layout key')
    if r['base'] != ['mh_collapse_dc_fasting','mh_collapse_dc_water','mh_dashboard_hidden']: f.add('BUG', f"base wrong {r['base']}")
    if r['afterHidden'] != '["ketosis"]' or r['afterFasting'] != 'closed': f.add('BUG', 'Default did not return to the pack layout')
    if r['afterExtra'] is not None: f.add('BUG', 'Default left a non-pack layout key')
    if 'mh_pills_open' in r['snap']: f.add('BUG', 'snapshot should not carry the Filter open state')
    # shipped packs parse and carry layout
    for fn in ('general_wellbeing','brain_tumour_tracking'):
        d = json.load(open(f'/home/claude/maxhealth/starter_packs/{fn}.json'))
        if 'layout' not in d['sets']: f.add('BUG', f'{fn} has no layout')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
    b.close()
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
