"""Persona 121: Settings > Advanced has a Pipeline & Health Connect Log: lists each log file with path and age, flags a stale one, filters by text, and shows Select all / Copy."""
import sys, os, time; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    logs = os.path.join(root, 'logs'); os.makedirs(logs, exist_ok=True)
    pl = os.path.join(logs, 'pipeline.log')
    open(pl, 'w').write('2026-07-01 10:00:00 | health_connect | extract  | ok     | 12 rows\n2026-07-01 10:00:01 | pipeline   | merge    | ok     | steps merged\n')
    old = time.time() - 100 * 86400; os.utime(pl, (old, old))
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev = page.evaluate
    ev("switchTab('settings'); switchSubTab('settings','manage')"); page.wait_for_timeout(600)
    if not ev("!!document.getElementById('pipelineLogOutput')"): f.add('BUG', 'no log card in Advanced tools')
    ev("mhRenderPipelineLog('')"); page.wait_for_timeout(1500)
    t = ev("document.getElementById('pipelineLogOutput').textContent")
    if 'STALE' not in t or 'pipeline.log' not in t or '12 rows' not in t: f.add('BUG', 'stale log not shown properly: ' + t[:300])
    ev("mhRenderPipelineLog('steps')"); page.wait_for_timeout(1500)
    t = ev("document.getElementById('pipelineLogOutput').textContent")
    if 'steps merged' not in t or '12 rows' in t: f.add('BUG', 'filter did not narrow lines: ' + t[:300])
    ev("document.getElementById('advanced-tools-wrap').style.display='block'; document.querySelectorAll('.mh-grp-hide').forEach(e=>e.classList.remove('mh-grp-hide'))"); page.wait_for_timeout(1200)
    dbg = ev("(()=>{const e=document.getElementById('pipelineLogOutput'); return [!!e.offsetParent, e.textContent.length, e.nextElementSibling&&e.nextElementSibling.className, MH_OUT_SEL.includes('pipelineLogOutput')]})()")
    if not ev("!!document.querySelector('#pipelineLogOutput + .mh-outtools')"): f.add('BUG', f'no Select all / Copy under the log {dbg}')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
