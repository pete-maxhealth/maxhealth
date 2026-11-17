"""Persona 490 (v3.10.1408): Settings > licence: the Devices button and list, freeing a slot, moving a full key to this phone, the move limit, and the label sent.
The licence server is faked in the page (route), so nothing real is contacted. Invented key and data only."""
import sys, re, json; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
KEY = 'ABCD-EFGH-JKLM-NPQR'
def make_server(state):
    def h(route, request):
        o = request.post_data_json or {}; a = o.get('action'); state['calls'].append(o)
        def j(code, body): route.fulfill(status=code, content_type='application/json', headers={'Access-Control-Allow-Origin': '*'}, body=json.dumps(body))
        if request.method == 'OPTIONS': return route.fulfill(status=204, headers={'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': '*', 'Access-Control-Allow-Methods': '*'})
        if o.get('key') != KEY and a in ('activate', 'devices', 'release'): return j(403, {'ok': False, 'error': 'That key was not recognised.'})
        devs = state['devs']
        if a == 'activate':
            if o['device'] not in [d['dev'] for d in devs]:
                if len(devs) >= 2: return j(409, {'ok': False, 'code': 'devices_full', 'max': 2, 'error': 'This key is already in use on 2 devices.'})
                devs.append({'dev': o['device'], 'label': o.get('label', ''), 'last': '2026-11-17T10:00:00Z'})
            return j(200, {'ok': True, 'tier': 'premium', 'days': 30, 'token': 'eyJpZCI6InQiLCJ0aWVyIjoicHJlbWl1bSIsImV4cCI6MTk5OTk5OTk5OX0.sig'})
        view = lambda: [{'id': d['dev'][:6], 'label': d['label'], 'last': d['last'], 'here': d['dev'] == o.get('device')} for d in devs]
        if a == 'devices': return j(200, {'ok': True, 'devices': view(), 'max': 2, 'moves_left': 3 - state['moves']})
        if a == 'release':
            if state['moves'] >= 3: return j(403, {'ok': False, 'code': 'moves_used', 'error': 'This key has already been moved 3 times in the last 30 days. Please contact support.'})
            t = [d for d in devs if d['dev'][:6] == o.get('target')]
            if not t: return j(404, {'ok': False, 'error': 'That device is not on this key.'})
            devs.remove(t[0]); state['moves'] += 1; return j(200, {'ok': True, 'devices': view(), 'max': 2, 'moves_left': 3 - state['moves']})
        return j(400, {'ok': False})
    return h
with fresh_server() as r, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []; state = {'calls': [], 'moves': 0, 'devs': [{'dev': 'phoneA-aaaaaaaaaaaa', 'label': "Pete's phone", 'last': '2026-11-16T09:00:00Z'}, {'dev': 'phoneB-bbbbbbbbbbbb', 'label': 'Jill phone', 'last': '2026-11-15T09:00:00Z'}]}
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block'); page = ctx.new_page()
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); ctx.route(re.compile(r'https://maxedhealth-licence\..*'), make_server(state))
    page.route(re.compile(r'^https?://(?!localhost|maxedhealth-licence)'), lambda r: r.abort())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev("siteSearchOpenSettings && switchTab('settings'); switchSubTab('settings','manage')"); page.wait_for_timeout(500)
    vis = lambda i: ev(f"getComputedStyle(document.getElementById('{i}')).display")
    vis('licenceDevicesBtn') == 'none' or f.add('FAIL', 'Devices button shown with no key')
    # 1. this phone is not on the key and it is full -> list appears with Replace buttons
    ev(f"document.getElementById('licenceKeyInput').value='{KEY}'"); ev("mhLicenceActivate()"); page.wait_for_timeout(800)
    vis('licenceDevices') == 'block' or f.add('FAIL', 'device list not shown when the key is full')
    t = ev("document.getElementById('licenceDevices').innerText")
    "Pete's phone" in t and 'Jill phone' in t and '2 of 2' in t or f.add('FAIL', f'list text: {t[:160]}')
    ev("document.querySelectorAll('#licenceDevices .copy-btn').length") == 2 or f.add('FAIL', 'expected a Replace button per device')
    # a '?' for the long text, closed by default
    ev("document.querySelector('#licenceDevices [id^=help-]')!==null") or f.add('FAIL', 'no ? help on the device list')
    # 2. move Jill's slot to this phone
    page.evaluate("[...document.querySelectorAll('#licenceDevices .copy-btn')].find(b=>b.closest('.settings-row').innerText.includes('Jill')).click()"); page.wait_for_timeout(1200)
    ev("!!localStorage.getItem('mh_licence')") or f.add('FAIL', 'licence not stored after the move')
    ev("localStorage.getItem('mh_licence_key')") == KEY or f.add('FAIL', 'key not stored after the move')
    'Licence moved to this phone' in ev("document.getElementById('licenceMsg').innerText") or f.add('FAIL', 'no confirmation after the move')
    vis('licenceDevicesBtn') != 'none' or f.add('FAIL', 'Devices button not shown once the key is stored')
    lab = [c.get('label') for c in state['calls'] if c.get('action') == 'activate' and c.get('label')]
    lab and 'browser' in lab[-1] or f.add('FAIL', f'device label not sent: {lab}')
    ev("state_names=null"); t = ev("document.getElementById('licenceDevices').innerText"); 'this phone' in t and 'Jill phone' not in t or f.add('FAIL', f'list after the move: {t[:200]}')
    # 3. free another slot from a licensed phone, then the limit
    state['devs'].append({'dev': 'phoneC-cccccccccccc', 'label': 'Old tablet', 'last': '2026-10-01T09:00:00Z'}) if len(state['devs']) < 2 else None
    ev("mhLicenceDevices()"); page.wait_for_timeout(500)   # toggles closed
    ev("mhLicenceDevices()"); page.wait_for_timeout(800)
    btn = ev("[...document.querySelectorAll('#licenceDevices .copy-btn')].map(b=>b.innerText)")
    btn and all(x == 'Free this slot' for x in btn) or f.add('FAIL', f'buttons on a licensed phone: {btn}')
    state['moves'] = 3; page.evaluate("document.querySelector('#licenceDevices .copy-btn').click()"); page.wait_for_timeout(800)
    'moved 3 times' in ev("document.getElementById('licenceMsg').innerText") or f.add('FAIL', 'move limit message not shown')
    # 4. wrong key
    ev("localStorage.removeItem('mh_licence'); localStorage.removeItem('mh_licence_key'); mhLicenceRender(); document.getElementById('licenceKeyInput').value='NOPE-NOPE-NOPE-NOPE'; mhLicenceActivate()"); page.wait_for_timeout(700)
    'not recognised' in ev("document.getElementById('licenceMsg').innerText") or f.add('FAIL', 'wrong key message')
    # Spanish button label
    ev("localStorage.setItem('mh_lang','es')"); page.reload(); page.wait_for_timeout(2000)
    ev("localStorage.setItem('mh_licence','x.y'); localStorage.setItem('mh_licence_key','K'); mhLicenceRender()")
    ev("document.getElementById('licenceDevicesBtn').innerText") == 'Dispositivos' or f.add('FAIL', 'Devices button not translated')
    errs and f.add('FAIL', f'page errors {errs}'); b.close()
print('findings', len(f))
