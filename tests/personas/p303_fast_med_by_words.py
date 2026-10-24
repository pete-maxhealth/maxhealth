"""Persona 303: the fasting 'taken with meds' item is matched by its words, so 'mct oil' covers 'MCT C8 Oil (15g)' and the fast is not restarted by it (v3.10.1204). Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("localStorage.setItem('mh_fasting_med_item','mct oil'); localStorage.setItem('mh_fasting_med_kcal','126')")
    chk = lambda d, k: ev("mhFastIsMedItem({description:%r,kcal:%s})" % (d, k))
    if not chk('MCT C8 Oil (15g)', 126): f.add('BUG', 'MCT C8 Oil counts as the meds item')
    if not chk('MCT oil', 126): f.add('BUG', 'the plain name still matches')
    if not chk('Oil, MCT', 100): f.add('BUG', 'words in any order match')
    if chk('Olive oil', 100): f.add('BUG', 'a different oil does not match')
    if chk('MCT C8 Oil (30g)', 300): f.add('BUG', 'a much bigger amount than usual still counts as a meal')
    if chk('Cheese', 126): f.add('BUG', 'unrelated food does not match')
    # the live timer is not restarted by it
    ev("(()=>{const d=new Date(), t=String(d.getHours()).padStart(2,'0')+':'+String(Math.max(0,d.getMinutes()-20)).padStart(2,'0'); const day=todayStr(); window.__ev=mhFastDayEvents(day,[{description:'MCT C8 Oil (15g)',kcal:126,time:t}],'')})()")
    if ev("window.__ev") is not None: f.add('BUG', 'a day with only the MCT oil entry has no meal, so it cannot restart the fast')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
