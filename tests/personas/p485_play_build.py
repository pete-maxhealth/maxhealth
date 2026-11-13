"""Persona 485 (v3.10.1403): the Google Play build (opened with ?src=play) hides the Premium card, the Ko-fi card, the demo Premium cards and the Premium
search entry, remembers itself, and changes nothing else; the normal build still shows them. Invented data only."""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
BLOCK = re.compile(r'https://(cdn\.jsdelivr\.net|cdnjs\.cloudflare\.com|fonts\.(googleapis|gstatic)\.com)/.*')
SHOWN = "(()=>{const v=id=>{const e=document.getElementById(id);return !!e&&getComputedStyle(e).display!=='none'};return {title:v('title-set-premium'),wrap:v('set-premium-wrap'),donate:v('mhDonateCard')}})()"
def mk(pw):
    b = pw.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block'); ctx.route(BLOCK, lambda r: r.abort()); p = ctx.new_page(); errs = []
    p.on('pageerror', lambda e: errs.append(str(e)[:160])); return b, p, errs
with fresh_server() as r, sync_playwright() as pw:
    # normal build: everything is there
    b, page, errs = mk(pw); ev = page.evaluate
    page.goto('http://localhost:5757/'); page.wait_for_timeout(800); ev("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(2500)
    ev("document.getElementById('onboardingOverlay')&&(document.getElementById('onboardingOverlay').style.display='none')")
    ev("switchTabById('settings')"); page.wait_for_timeout(500)
    s = ev(SHOWN); s['title'] and s['wrap'] or f.add('FAIL', f'normal build lost the Premium section: {s}')
    ev("mhIsPlayBuild()") is False or f.add('FAIL', 'normal build says it is the Play build')
    ev("filterSiteSearch('premium'); document.getElementById('siteSearchResults')?.innerText || document.body.innerText").count('Premium (local version)') >= 1 or f.add('FAIL', 'normal search lost the Premium entry')
    ev("startDemoMode('doris')"); page.wait_for_timeout(2500)  # control: the same checks must find the demo Premium cards when it is not the Play build
    d = ev("(()=>{const v=id=>{const e=document.getElementById(id);return !!e&&getComputedStyle(e).display!=='none'};return [v('demoPremiumLink'),v('demoPremiumCard')]})()")
    all(d) or f.add('FAIL', f'control: the normal demo should show Premium link and card: {d}')
    errs and f.add('FAIL', f'page errors {errs}'); b.close()
    # Play build
    b, page, errs = mk(pw); ev = page.evaluate
    page.goto('http://localhost:5757/?src=play'); page.wait_for_timeout(800); ev("state.onboarded=true; saveState()"); page.goto('http://localhost:5757/'); page.wait_for_timeout(2500)
    ev("localStorage.getItem('mh_play')") == '1' or f.add('FAIL', 'the Play flag was not remembered')
    ev("document.getElementById('onboardingOverlay')&&(document.getElementById('onboardingOverlay').style.display='none')")
    ev("switchTabById('settings')"); page.wait_for_timeout(500)
    s = ev(SHOWN); any(s.values()) and f.add('FAIL', f'Play build still shows Premium or Ko-fi: {s}')
    ev("mhIsPlayBuild()") or f.add('FAIL', 'Play build not detected')
    ev("filterSiteSearch('premium'); document.getElementById('siteSearchResults')?.innerText || document.body.innerText").count('Premium (local version)') == 0 or f.add('FAIL', 'search still offers Premium')
    ev("filterSiteSearch('upgrade')"); 'Premium (local version)' in ev("document.body.innerText") and f.add('FAIL', 'a keyword search still reaches Premium')
    ev("startDemoMode('doris')"); page.wait_for_timeout(2500)
    d = ev("(()=>{const v=id=>{const e=document.getElementById(id);return !!e&&getComputedStyle(e).display!=='none'};return {link:v('demoPremiumLink'),card:v('demoPremiumCard'),trends:v('demoPremiumTrends')}})()")
    any(d.values()) and f.add('FAIL', f'demo Premium cards shown in the Play build: {d}')
    ev("switchTabById('trends')"); page.wait_for_timeout(800)
    ev("document.body.innerText").count('Register interest') and f.add('FAIL', 'a Register interest link is visible in the Play build')
    errs and f.add('FAIL', f'page errors {errs}'); b.close()
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
