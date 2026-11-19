"""Persona 505 (v3.10.1430): bulk deletes of workouts and routines, and removing a device mapping, now offer the standard toast Undo. Invented data."""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    br = pw.chromium.launch()
    ctx = br.new_context(viewport={'width': 390, 'height': 900}, service_workers='block'); page = ctx.new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(3000); ev = page.evaluate
    ev("state.onboarded=true; saveState(); var o=document.getElementById('onboardingOverlay'); if(o) o.style.display='none'; window.appConfirm=function(m,y){y&&y();}")
    def run(name, seed, call, count):
        ev(seed); n0 = ev(count); ev(call); page.wait_for_timeout(300); n1 = ev(count)
        n1 < n0 or f.add('FAIL', f'{name}: delete did nothing ({n0}->{n1})')
        if not page.locator('#toast .toast-undo').count(): f.add('FAIL', name + ': no Undo on toast'); return
        page.click('#toast .toast-undo'); page.wait_for_timeout(400); n2 = ev(count)
        n2 == n0 or f.add('FAIL', f'{name}: undo did not restore ({n0}->{n1}->{n2})')
    run('workouts', "state.strengthLog=[{id:'s1',date:todayStr(),exercise:'Squat',sets:[]},{id:'s2',date:todayStr(),exercise:'Row',sets:[]}]; saveState(); _strengthSelectMode=true; _strengthSelectedIds=['s1']", "deleteSelectedStrengthSessions()", "(JSON.parse(localStorage.getItem('mh_state')||'{}').strengthLog||state.strengthLog||[]).length")
    run('routines', "saveRoutines([{id:'r1',name:'A',exercises:[]},{id:'r2',name:'B',exercises:[]}]); _routineSelectMode=true; _routineSelectedIds=['r1']", "deleteSelectedRoutines()", "loadRoutines().length")
    run('device mapping', "saveDeviceConfigs([{device_name:'Dev A',mappings:[]},{device_name:'Dev B',mappings:[]}])", "deleteDeviceConfig(0)", "loadDeviceConfigs().length")
    errs and f.add('JS-exception', errs[0])
print('findings', len(f))
