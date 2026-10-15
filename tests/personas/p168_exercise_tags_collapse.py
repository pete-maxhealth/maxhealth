"""Persona 168 (v3.10.1067): 'Exercise: 45min Walking' and 'Exercise: 60min Walking' are ONE tag in the tag lists / before-during-after chips
(they used to be one chip per distinct duration, hundreds on a long history)."""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
bad = []
def check(n, ok, info=''):
    print(('PASS ' if ok else 'FAIL ') + n + (f'  {info}' if info and not ok else ''))
    if not ok: bad.append(n)
with fresh_server() as root, sync_playwright() as pw:
    br = pw.chromium.launch(); ctx = br.new_context(viewport={'width': 430, 'height': 900}, service_workers='block'); page = ctx.new_page()
    errs = []; page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.dismiss())
    page.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); page.evaluate("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev = page.evaluate
    ev("startDemoMode('alex')"); page.wait_for_timeout(2000)
    ev("state.history.slice(0,20).forEach((h,i)=>{h.notes=(i%2?'Exercise: '+(30+i*5)+'min Walking':'Exercise: '+(40+i*7)+'min Resistance')+', Travel'})")
    keys = ev("Object.keys(mhTagDays())")
    ex = [k for k in keys if k.startswith('exercise:')]
    check('20 days with different durations give 2 exercise tags', sorted(ex) == ['exercise: resistance', 'exercise: walking'], str(ex))
    defs = ev("mhAnchorDefs ? 1 : 0") if ev("typeof mhAnchorDefs") != 'undefined' else 1
    ev("document.getElementById('maintab-insights').click()"); page.wait_for_timeout(500); ev("document.getElementById('insightstab-reports').click()"); page.wait_for_timeout(800)
    n = ev("[...document.querySelectorAll('body *')].filter(e=>e.children.length===0&&/^🏷\\s*Exercise:\\s*\\d/.test(e.textContent)).length")
    check('no per-duration exercise chips on Reports', n == 0, str(n))
    ev("mhTagRename('Exercise: Walking','Dog walk')"); 
    check('renaming the combined tag renames every day', ev("state.history.filter(h=>/Dog walk/.test(h.notes||'')).length") == 10 and ev("state.history.some(h=>/\\d+min Walking/.test(h.notes||''))") is False)
    check('no JS errors', not errs, str(errs[:2]))
print('p168:', 'ALL PASS' if not bad else f'{len(bad)} FAIL: {bad}'); sys.exit(1 if bad else 0)
