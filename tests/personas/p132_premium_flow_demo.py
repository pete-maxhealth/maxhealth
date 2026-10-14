"""Persona 132: the demo advertises Premium as COMING SOON (Today card, Trends sample and banner link, v3.10.1046), and the example flow and preview still open when called, and a clearly labelled example of the synced-data flow (Health Connect snapshots, ring and watch, ranking decision, self-check); the card is gone after exiting the demo."""
import sys; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev = page.evaluate
    if ev("!!document.getElementById('demoPremiumCard')"): f.add('BUG', 'Premium card present outside demo')
    ev("startDemoMode(DEMO_PERSONAS[0].id)"); page.wait_for_timeout(2500)
    if not ev("!!document.getElementById('demoPremiumCard')"): f.add('BUG', 'Premium card missing in the demo')
    elif 'Coming soon' not in ev("document.getElementById('demoPremiumCard').textContent"): f.add('BUG', 'Premium card does not say Coming soon')
    if not ev("!!document.getElementById('demoPremiumTrends')"): f.add('BUG', 'Premium sample chart missing on Trends in the demo')
    if ev("getComputedStyle(document.getElementById('demoPremiumLink')).display") == 'none': f.add('BUG', 'Premium link hidden in the demo banner')
    elif 'coming soon' not in ev("document.getElementById('demoPremiumLink').textContent").lower(): f.add('BUG', 'banner link does not say coming soon')
    ev("mhPremiumFlow()"); page.wait_for_timeout(300)
    t = ev("(document.getElementById('mhPremiumFlow')||{}).textContent||''")
    for need in ('EXAMPLE ONLY', 'Health Connect', 'RingConn', 'Zepp', 'Device ranking', 'self-check'):
        if need not in t: f.add('BUG', f'flow missing "{need}"')
    ev("document.getElementById('mhPremiumFlow').remove(); mhPremiumPreview()"); page.wait_for_timeout(200)
    if 'See a day of synced data' not in ev("document.getElementById('mhPremiumPrev').textContent"): f.add('BUG', 'preview lacks the flow button')
    if 'iPhone' not in ev("document.getElementById('mhPremiumPrev').textContent"): f.add('BUG', 'preview lacks the iPhone / backup note')
    pv = ev("document.getElementById('mhPremiumPrev').textContent")
    for need in ('coming soon', 'External data imports', 'Support', 'Register interest'):
        if need.lower() not in pv.lower(): f.add('BUG', f'preview missing "{need}"')
    ev("document.querySelector('#mhPremiumPrev button').click()"); page.wait_for_timeout(300)
    if not ev("!!document.getElementById('mhPremiumFlow')") or ev("!!document.getElementById('mhPremiumPrev')"): f.add('BUG', 'preview button did not swap to the flow')
    ev("document.getElementById('mhPremiumFlow').remove(); exitDemoMode()"); page.wait_for_timeout(1800)
    if ev("!!document.getElementById('demoPremiumTrends')"): f.add('BUG', 'Trends sample left behind after exiting the demo')
    if ev("!!document.getElementById('demoPremiumCard')"): f.add('BUG', 'Premium card left behind after exiting the demo')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
