"""Persona 130: Settings > AI Provider has a licence card: a key activates through the licence service (device id sent), a wrong key shows a clear message, the trial starts, the token is stored and drives the 'Premium licence' state, Remove clears it, and a token near expiry is refreshed quietly."""
import sys, json, time, base64; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
def tok(tier, days):
    p = base64.urlsafe_b64encode(json.dumps({'id': 'x', 'tier': tier, 'exp': int(time.time()) + days * 86400}).encode()).decode().rstrip('=')
    return p + '.sig'
with fresh_server() as root, sync_playwright() as pw:
    ctx = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block')
    page = ctx.new_page(); errs = []; calls = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    def lic(route):
        b = json.loads(route.request.post_data or '{}'); calls.append(b)
        if b.get('action') == 'activate' and b.get('key') == 'GOOD-GOOD-GOOD-GOOD': r = {'ok': True, 'token': tok('premium', 30), 'tier': 'premium'}
        elif b.get('action') == 'activate': r = {'ok': False, 'error': 'That key was not recognised.'}
        elif b.get('action') == 'trial': r = {'ok': True, 'token': tok('trial', 14), 'tier': 'trial'}
        else: r = {'ok': False}
        route.fulfill(status=200, content_type='application/json', body=json.dumps(r))
    ctx.route('https://maxedhealth-licence.bogginsuk.workers.dev/licence', lic)
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev = page.evaluate
    ev("switchTab('settings'); switchSubTab('settings','manage')"); page.wait_for_timeout(500)
    if not ev("!!document.getElementById('licenceCard')"): f.add('BUG', 'no licence card')
    ev("document.getElementById('licenceKeyInput').value='nope'; mhLicenceActivate()"); page.wait_for_timeout(600)
    if 'not recognised' not in ev("document.getElementById('licenceMsg').textContent"): f.add('BUG', 'wrong-key message not shown')
    if ev("localStorage.getItem('mh_licence')"): f.add('BUG', 'token stored for a wrong key')
    ev("document.getElementById('licenceKeyInput').value='good-good-good-good'; mhLicenceActivate()"); page.wait_for_timeout(600)
    if not ev("localStorage.getItem('mh_licence')"): f.add('BUG', 'token not stored after a good key')
    if 'Premium licence' not in ev("document.getElementById('licenceState').textContent"): f.add('BUG', 'state not shown: ' + ev("document.getElementById('licenceState').textContent"))
    if not any(len(c.get('device', '')) >= 16 for c in calls): f.add('BUG', 'device id not sent to the licence service')
    ev("mhLicenceRemove()"); page.wait_for_timeout(200)
    if ev("localStorage.getItem('mh_licence')") or ev("document.getElementById('licenceState').textContent") != 'None': f.add('BUG', 'remove did not clear the licence')
    ev("mhLicenceTrial()"); page.wait_for_timeout(600)
    if 'Trial: 14 days left' not in ev("document.getElementById('licenceState').textContent"): f.add('BUG', 'trial not shown: ' + ev("document.getElementById('licenceState').textContent"))
    # near-expiry token is refreshed
    ev("localStorage.setItem('mh_licence_key','GOOD-GOOD-GOOD-GOOD'); localStorage.setItem('mh_licence','%s')" % tok('premium', 2)); calls.clear()
    ev("mhLicenceAutoRefresh()"); page.wait_for_timeout(600)
    if not any(c.get('action') == 'activate' for c in calls): f.add('BUG', 'token near expiry was not refreshed')
    if any('pspence' in (r or '') for r in [page.evaluate('MH_LICENCE_URL')]): f.add('BUG', 'licence address still points at the old GoDaddy host')
    ev("localStorage.setItem('mh_licence','%s')" % tok('premium', 25)); calls.clear()
    ev("mhLicenceAutoRefresh()"); page.wait_for_timeout(400)
    if calls: f.add('BUG', 'a fresh token was refreshed needlessly')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
