"""Persona 374: the Check for updates button finds a newer app page without a refresh first (v3.10.1259).
Pete (4 Nov): "Check for updates button doesn't work as you need to refresh the screen first. If you do that, it updates with the refresh, not the button."
sw.js does not change between releases, so the old check never saw a new page. Now the button (and coming back to the app) reads the served page's own version.
Covers: up to date says so; newer served page shows the Reload banner; the banner reloads onto the new version; the button never stays stuck on Checking; coming back to the
app shows the banner on its own; no page errors. Invented data."""
import sys, os, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}).new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(2500); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    cur = ev("APP_VERSION")
    if not ev("!!_swRegistration"): f.add('BUG', '0: the service worker registered, so the button has something to ask')
    toasts = "[...document.querySelectorAll('.toast')].map(t=>t.innerText).join(' | ')"
    # 1. nothing newer: the button says so and goes back to its normal label
    ev("document.getElementById('checkUpdateBtn').click()"); page.wait_for_timeout(2500)
    if ev("!!document.getElementById('swUpdateBanner')"): f.add('BUG', '1: no banner when the served page is the same version')
    if ev("document.getElementById('checkUpdateBtn').textContent.includes('Checking')"): f.add('BUG', '2: the button is stuck on Checking')
    # 2. the server now hands out a newer page: the button must find it, no refresh first
    app = os.path.join(root, 'app', 'maxhealth.html'); h = open(app, encoding='utf-8').read()
    open(app, 'w', encoding='utf-8').write(h.replace("const APP_VERSION = '" + cur + "'", "const APP_VERSION = 'v3.10.9999'", 1))
    ev("document.querySelectorAll('.toast').forEach(t=>t.remove())")
    ev("document.getElementById('checkUpdateBtn').click()"); page.wait_for_timeout(2500)
    if not ev("!!document.getElementById('swUpdateBanner')"): f.add('BUG', '3: a newer served page shows the Reload banner from the button')
    if 'latest version' in ev(toasts): f.add('BUG', '4: it does not also say you are on the latest version')
    if ev("document.getElementById('checkUpdateBtn').disabled"): f.add('BUG', '5: the button is usable again')
    # 3. the banner reloads onto the new version
    if ev("!!document.getElementById('swUpdateBanner')"):
        page.click('#swUpdateBanner'); page.wait_for_timeout(2500)
        now = ev("APP_VERSION")
        if now != 'v3.10.9999': f.add('BUG', f'6: tapping Reload now lands on the new version (got {now})')
    # 4. coming back to the app shows it on its own (served page newer again)
    open(app, 'w', encoding='utf-8').write(h.replace("const APP_VERSION = '" + cur + "'", "const APP_VERSION = 'v3.11.1'", 1))
    ev("document.getElementById('swUpdateBanner')?.remove(); _servedCheckAt = 0; Object.defineProperty(document,'visibilityState',{get:()=>'visible',configurable:true}); document.dispatchEvent(new Event('visibilitychange'))"); page.wait_for_timeout(2500)
    if not ev("!!document.getElementById('swUpdateBanner')"): f.add('BUG', '7: returning to the app shows the banner without pressing anything')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
