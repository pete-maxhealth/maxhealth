"""Persona 87: typing a figure in the Today 'Daily Steps' box saves it as today's manual steps, so it beats a device figure in combined.csv."""
import sys, os, json, time; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
from datetime import date
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    iso = date.today().isoformat()
    os.makedirs(os.path.join(root, 'data', 'tables'), exist_ok=True)
    # a device figure already on today's row
    open(os.path.join(root, 'data', 'tables', 'combined.csv'), 'w').write('date,steps,source\n%s,4277,amazfit\n' % iso)
    json.dump({iso: {'steps': 'amazfit'}}, open(os.path.join(root, 'data', 'field_sources.json'), 'w'))
    errs = []
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 844}, service_workers='block').new_page()
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("localStorage.setItem('mh_onboarded','1')"); page.reload(); page.wait_for_timeout(2500)
    page.evaluate("saveDailySteps('6k')"); page.wait_for_timeout(1500)
    mf = os.path.join(root, 'data', 'inbox', 'manual_entry.json'); arch = os.path.join(root, 'data', 'inbox', 'old')
    ok = False
    for _ in range(20):
        c = read_combined(root)
        if (c.get(iso) or {}).get('steps') in ('6000', '6000.0'): ok = True; break
        time.sleep(1)
    if not ok: f.add('BUG', f"typed total did not reach combined.csv: {(read_combined(root).get(iso) or {}).get('steps')}")
    fs = json.load(open(os.path.join(root, 'data', 'field_sources.json')))
    if fs.get(iso, {}).get('steps') != 'manual': f.add('BUG', f"steps not attributed to manual: {fs.get(iso)}")
    if errs: f.add('BUG', f'page errors: {errs[:2]}')
print('findings', len(f)); sys.exit(1 if f else 0)
