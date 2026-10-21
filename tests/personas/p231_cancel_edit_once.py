"""Persona 231: one press of Cancel closes the Edit-entry form in Today's log and it stays closed (v3.10.1126); the shopping screen scroll box
reports its scrolling so the shared up arrow can appear there. Invented data only."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("state.todayLog=[{id:9001,description:'Test omelette',amount:'1 serving',time:'08:00',kcal:300,protein:20,carbs:2,fat:22,fibre:0}]; updateDashboard()")
    page.wait_for_timeout(300)
    page.click('#log-entry-9001 >> text=Test omelette'); page.wait_for_timeout(200)
    n = ev("document.querySelectorAll('#log-entry-9001 .log-edit-form').length")
    if n != 1: f.add('BUG', f'1: tapping the entry opens the form once: {n}')
    h = ev("document.querySelector('#log-entry-9001 .log-edit-form button.cancel').getBoundingClientRect().height")
    if h < 43: f.add('BUG', f'2: Cancel is a finger-sized target: {h}px')
    page.click('#log-entry-9001 .log-edit-form button.cancel'); page.wait_for_timeout(300)
    n = ev("document.querySelectorAll('#log-entry-9001 .log-edit-form').length")
    if n != 0: f.add('BUG', f'3: one Cancel press closes the form and it stays closed: {n} forms')
    page.click('#log-entry-9001 >> text=Test omelette'); page.wait_for_timeout(200)
    if not ev("!!document.querySelector('#log-entry-9001 .mh-edit-close')"): f.add('BUG', '4: a Close button sits at the top of the form')
    page.click('#log-entry-9001 .mh-edit-close'); page.wait_for_timeout(300)
    if ev("document.querySelectorAll('#log-entry-9001 .log-edit-form').length") != 0: f.add('BUG', '5: top Close closes the form once')
    ev("state.todayLog[0].items=[{name:'Egg',amount:'2',kcal:150,protein:12,carbs:1,fat:10},{name:'Cheese',amount:'30g',kcal:150,protein:8,carbs:1,fat:12}]; updateDashboard()"); page.wait_for_timeout(200)
    ev("editLogEntry(9001)"); page.wait_for_timeout(200)
    if not ev("!!document.querySelector('#log-entry-9001 .mh-edit-close')"): f.add('BUG', '6: itemised form also has a top Close')
    else:
        page.click('#log-entry-9001 .mh-edit-close'); page.wait_for_timeout(300)
        if ev("document.querySelectorAll('#log-entry-9001 .log-edit-form, #log-entry-9001 [class*=edit]').length") and ev("!!document.querySelector('#log-entry-9001 .mh-edit-close')"): f.add('BUG', '7: itemised Close closes once')
    if 'onscroll' not in (ev("document.getElementById('shopScroll').outerHTML.slice(0,200)") or ''): f.add('BUG', '3: shopScroll tracks scrolling')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
