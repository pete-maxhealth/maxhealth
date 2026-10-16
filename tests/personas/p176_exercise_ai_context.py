"""Persona 176 (v3.10.1076): the AI/report context carries a plain-text exercise summary, with the right numbers and the caution."""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
bad = []
def check(n, ok, info=''):
    print(('PASS ' if ok else 'FAIL ') + n + (f'  {info}' if info and not ok else ''))
    if not ok: bad.append(n)
with fresh_server() as root, sync_playwright() as pw:
    br = pw.chromium.launch(); ctx = br.new_context(viewport={'width': 430, 'height': 900}, service_workers='block'); page = ctx.new_page()
    errs = []; page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); page.evaluate("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev = page.evaluate; ev("startDemoMode('alex')"); page.wait_for_timeout(2300)
    c = ev("mhExerciseContext(state.history.slice(0,30))")
    check('summary produced for an active persona', c and 'active day' in c and 'Mix:' in c, str(c)[:120])
    st = ev("(()=>{const d=state.history.slice(0,30); const s=mhExerciseRangeStats(d); return {a:s.activeDays,m:Math.round(s.minutes)}})()")
    check('summary numbers match the stats', f"{st['a']} active day(s) of 30" in c, c[:80] + str(st))
    check('recent days listed with names and effort', 'Recent days:' in c and '(Moderate)' in c or '(Hard)' in c or '(Easy)' in c)
    block = ev("patientContextBlock(buildPatientContext(state.history.slice(0,30)))")
    check('context block includes LOGGED EXERCISE and the association caution', 'LOGGED EXERCISE' in block and 'never proof of cause' in block)
    check('too little exercise -> no block', ev("mhExerciseContext([{date:'01/10/26',exercises:[]}])") is None)
    block2 = ev("(()=>{const h=state.history.slice(0,30).map(d=>({...d,exercises:[]})); state.strengthLog=[]; return patientContextBlock(buildPatientContext(h))})()")
    check('no exercise -> block omits the line', 'LOGGED EXERCISE' not in block2)
    check('no JS errors', not errs, str(errs[:2]))
print('p176:', 'ALL PASS' if not bad else f'{len(bad)} FAIL: {bad}'); sys.exit(1 if bad else 0)
