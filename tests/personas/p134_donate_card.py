"""Persona 134: the Ko-fi "Help keep it free" card is hidden while MH_DONATE_URL is empty; with a URL set it shows in Settings, links to it, and never appears in demo mode."""
import sys; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    ctx = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block'); page = ctx.new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    if 'ko-fi.com/maxedhealth' not in page.evaluate("document.getElementById('mhDonateCard').innerHTML"): f.add('BUG', 'Ko-fi card not wired to the real page')
    def patch(route):
        r = route.fetch(); b = r.text().replace("const MH_DONATE_URL = 'https://ko-fi.com/maxedhealth';", "const MH_DONATE_URL = 'https://ko-fi.com/example';")
        route.fulfill(response=r, body=b)
    page.route('**/maxhealth.html*', patch); page.route('http://localhost:5757/', patch)
    page.goto('http://localhost:5757/'); page.wait_for_timeout(2500)
    ev = page.evaluate
    if ev("document.getElementById('mhDonateCard').style.display") == 'none' or 'ko-fi.com/example' not in ev("document.getElementById('mhDonateCard').innerHTML"): f.add('BUG', 'donate card not shown / no link when URL set')
    ev("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev("startDemoMode(DEMO_PERSONAS[0].id)"); page.wait_for_timeout(2500); ev("mhDonateRender()")
    if ev("document.getElementById('mhDonateCard').style.display") != 'none': f.add('BUG', 'donate card shown in demo')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
