# p368: a typed step total (23.5k) must stay in the box. It is also saved to the server as today's steps; the next sync reads it back and must not retire it.
# A real watch/phone figure that is the same or more still retires it, and a lower one never does.
import sys; sys.path.insert(0, 'tests/personas')
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
def chk(c, m):
    if not c: f.add('BUG', m)
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); ev = page.evaluate
    page.on('pageerror', lambda e: f.add('JS-exception', str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200)
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay').style.display='none'"); page.reload(); page.wait_for_timeout(1500)
    ev("switchTabById('move')"); page.wait_for_timeout(400)
    box = lambda: ev("document.getElementById('dailyStepsInput').value")
    ev("(() => { const e = document.getElementById('dailyStepsInput'); e.focus(); e.value = '23.5k'; e.blur(); })()"); page.wait_for_timeout(1500)
    chk(box() == '23500', f'box after typing 23.5k: {box()!r}')
    chk(ev("localStorage.getItem('mh_steps_pushed')") is not None or not ev("_serverOnline"), 'the saved-to-server marker was not set although the server took the figure')
    # the echo: the sync reads back exactly what was typed
    ev("mhStepsRetireTyped(23500)"); page.wait_for_timeout(200)
    if ev("_serverOnline"):
        chk(ev("localStorage.getItem('mh_steps_today')") == '23500', 'typed total retired by its own echo from the server')
    # the real import path, end to end
    ev("try { autoImportCombinedIfStale(); } catch (e) {}"); page.wait_for_timeout(8000)
    ev("updateDashboard()"); page.wait_for_timeout(300)
    chk(box() == '23500', f'box blank/changed after the sync round trip: {box()!r}')
    # lower device figure: never retires. Higher or equal-from-a-device: retires (marker belongs to the typed figure only).
    ev("localStorage.setItem('mh_steps_today','23500'); localStorage.setItem('mh_steps_pushed', localISODate() + ':23500')")
    chk(ev("mhStepsRetireTyped(9000)") is False and ev("localStorage.getItem('mh_steps_today')") == '23500', 'a lower watch figure retired the typed total')
    chk(ev("mhStepsRetireTyped(24100)") is True and ev("localStorage.getItem('mh_steps_today')") is None, 'a higher watch figure no longer retires the typed total')
    # a new typed figure moves the marker with it; yesterday's marker never protects today's value
    ev("localStorage.setItem('mh_steps_today','23500'); localStorage.setItem('mh_steps_pushed', '2020-01-01:23500')")
    chk(ev("mhStepsRetireTyped(23500)") is True, 'an old marker from another day protected today')
    page.screenshot(path='/tmp/claude-0/shots/steps_typed.png')
bugs = [x for x in f if x[0] in ('BUG', 'JS-exception')]
print('findings:', len(f), 'bugs:', len(bugs)); [print(x) for x in bugs]; sys.exit(1 if bugs else 0)
