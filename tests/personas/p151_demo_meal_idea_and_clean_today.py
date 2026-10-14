"""Persona 151: in a demo, Next meal idea returns real combos built from the demo library (not a JSON error), and Today shows no new-user welcome card or backup nag, including after a language-change resume."""
import sys; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    ev = page.evaluate
    ev("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev("startDemoMode('barry')"); page.wait_for_timeout(2500)
    ev("switchTab('log', document.getElementById('maintab-log'))"); page.wait_for_timeout(600)
    ev("startNextMealFlow()"); page.wait_for_timeout(800)
    for w in ('Protein', 'Vegetable'):
        ev("(w)=>{const e=[...document.querySelectorAll('.mealPillEl')].find(x=>x.textContent.includes(w)); e.click()}", w); page.wait_for_timeout(200)
    ev("document.querySelector('.mealPillSendBtn').click()"); page.wait_for_timeout(5000)
    txt = ev("document.getElementById('chatScroll').innerText")
    if 'not valid JSON' in txt or "Couldn't reach the AI" in txt: f.add('BUG', 'meal idea failed in the demo')
    if ev("document.querySelectorAll('[data-meal-suggestion-result] button, .chat-bubble button').length") < 1 or 'Log this meal' not in txt: f.add('BUG', 'no loggable suggestion shown')
    ev("switchTab('dash', document.getElementById('maintab-dash'))"); page.wait_for_timeout(500)
    for i in ('newUserBanner', 'backupReminderBanner'):
        if ev("(i)=>{const e=document.getElementById(i); return !!e && getComputedStyle(e).display!=='none' && !!e.offsetParent}", i): f.add('BUG', f'{i} visible in the demo')
    ev("mhLangSet('es')"); page.wait_for_timeout(4500)
    for i in ('newUserBanner', 'backupReminderBanner'):
        if ev("(i)=>{const e=document.getElementById(i); return !!e && getComputedStyle(e).display!=='none' && !!e.offsetParent}", i): f.add('BUG', f'{i} visible after a language-change resume')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
