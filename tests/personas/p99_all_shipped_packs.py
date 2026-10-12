"""Persona 99: every shipped starter pack is valid and safe: listed in index.json, version not newer than the app, unique ids, layout keys all real
(dashboard cards, Today fold keys, Trends cards), applies cleanly in the app (symptoms added, layout set, nothing else touched),
and the embedded first-run packs still equal their JSON files."""
import sys, re, json, glob, os; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
R = '/home/claude/maxhealth/'
html = open(R + 'maxhealth.html').read(); ver = re.search(r"const APP_VERSION = '(v[0-9.]+)'", html).group(1)
idx = json.load(open(R + 'starter_packs/index.json'))['packs']
files = sorted(os.path.basename(p) for p in glob.glob(R + 'starter_packs/*.json') if not p.endswith('index.json'))
if sorted(p['file'] for p in idx) != files: f.add('BUG', f'index.json and files differ: {sorted(p["file"] for p in idx)} vs {files}')
for p in idx:
    if not p.get('title') or len(p.get('description', '')) < 30 or 'nothing here is advice' not in p['description'].lower() and 'wellbeing' not in p['title'].lower(): f.add('BUG', f'index entry weak {p["file"]}')
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page = ctx.new_page(); errs = []; page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); page.evaluate("localStorage.setItem('mh_onboarded','1')")
    valid = page.evaluate("({dc: MH_DASH_CARDS.map(c=>c[0]), dash: DEFAULT_DASHBOARD_ORDER.slice()})")
    for fn in files:
        d = json.load(open(R + 'starter_packs/' + fn)); tag = fn
        if d.get('mhpack') != 1: f.add('BUG', f'{tag}: mhpack != 1')
        vt = lambda v: tuple(int(x) for x in re.findall(r'\d+', v or '0'))
        if not d.get('version') or vt(d['version']) > vt(ver): f.add('BUG', f'{tag}: version {d.get("version")} missing or newer than app {ver}')
        sets = d.get('sets', {}); syms = sets.get('symptoms', {}).get('data', [])
        if not (5 <= len(syms) <= 12): f.add('BUG', f'{tag}: {len(syms)} symptoms')
        ids = [s['id'] for s in syms]
        if len(set(ids)) != len(ids) or len({s['name'] for s in syms}) != len(syms): f.add('BUG', f'{tag}: duplicate symptom ids or names')
        if sets.get('symptoms', {}).get('count') != len(syms): f.add('BUG', f'{tag}: symptom count mismatch')
        lay = sets.get('layout', {}).get('data')
        if not lay: f.add('BUG', f'{tag}: no layout'); continue
        for k, v in lay.items():
            if not re.match(r'^(mh_collapse_dc_|mh_dashboard_hidden$|mh_trend_cards_hidden$)', k): f.add('BUG', f'{tag}: unexpected layout key {k}'); continue
            if k.startswith('mh_collapse_dc_') and (k[len('mh_collapse_dc_'):] not in valid['dc'] or v != 'closed'): f.add('BUG', f'{tag}: bad fold {k}={v}')
            if k == 'mh_dashboard_hidden':
                for x in json.loads(v):
                    if x not in valid['dash']: f.add('BUG', f'{tag}: hides unknown Today card {x}')
            if k == 'mh_trend_cards_hidden':
                for x in json.loads(v):
                    if f'id="{x}"' not in html: f.add('BUG', f'{tag}: hides unknown Trends card {x}')
        # applies cleanly
        r = page.evaluate("""(pack) => { localStorage.clear(); localStorage.setItem('mh_onboarded','1'); const before = Object.keys(localStorage).sort();
          const out = mhPackApply(pack, Object.keys(pack.sets), 'merge'); const after = Object.keys(localStorage).filter(k => !before.includes(k));
          return { out: String(out), added: after, hidden: localStorage.getItem('mh_dashboard_hidden'), base: Object.keys(mhLayoutBase()).length }; }""", d)
        if r['base'] != len(lay): f.add('BUG', f'{tag}: pack layout base {r["base"]} != {len(lay)}')
        for k in r['added']:
            if not re.match(r'^(mh_collapse_dc_|mh_dashboard_hidden$|mh_trend_cards_hidden$|mh_layout_base|mh_symptom|mh_treatment_defs|maxhealth|mh_nudge|mh_pack)', k) and 'symp' not in k.lower(): f.add('BUG', f'{tag}: pack wrote unexpected key {k}')
        if lay.get('mh_dashboard_hidden') and r['hidden'] != lay['mh_dashboard_hidden']: f.add('BUG', f'{tag}: hidden list not applied ({r["hidden"]})')
    # embedded first-run packs equal the JSON files
    emb = page.evaluate("MH_FIRST_RUN_PACKS")
    for key, fn in (('brain', 'brain_tumour_tracking.json'), ('simple', 'general_wellbeing.json')):
        if emb[key]['sets'] != json.load(open(R + 'starter_packs/' + fn))['sets']: f.add('BUG', f'embedded {key} differs from {fn}')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
    b.close()
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
