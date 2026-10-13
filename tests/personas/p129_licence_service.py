"""Persona 129: the PHP licence service issues, activates (device-bound), trials, revokes and serves downloads correctly, and its tokens are accepted by the Cloudflare Worker."""
import sys, os, json, subprocess, tempfile, time, urllib.request, urllib.error
root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
bad = []
def add(m): bad.append(m); print('  [BUG]', m)
d = tempfile.mkdtemp(prefix='mh_lic_')
open(d + '/config.php', 'w').write("<?php return ['signing_secret' => 'worker-secret-123', 'admin_secret' => 'admin-secret-456'];")
open(d + '/premium_payload.zip', 'wb').write(b'PK\x03\x04fake')
env = dict(os.environ, MH_LICENCE_DIR=d)
srv = subprocess.Popen(['php', '-S', '127.0.0.1:8099', os.path.join(root, 'premium-site/licence.php')], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.2)
def post(obj):
    req = urllib.request.Request('http://127.0.0.1:8099/', data=json.dumps(obj).encode(), headers={'Content-Type': 'application/json'})
    try:
        r = urllib.request.urlopen(req, timeout=10); return r.status, r.read(), r.headers
    except urllib.error.HTTPError as e: return e.code, e.read(), e.headers
def js(t): return json.loads(t[1])
try:
    dev1, dev2, dev3 = 'devA_abcdefghijklmnop', 'devB_abcdefghijklmnop', 'devC_abcdefghijklmnop'
    if post({'action': 'issue', 'admin': 'wrong', 'tier': 'premium'})[0] != 403: add('issue without admin secret was not refused')
    r = post({'action': 'issue', 'admin': 'admin-secret-456', 'tier': 'premium', 'note': 'test'}); key = js(r).get('key', '')
    if r[0] != 200 or len(key) != 19: add(f'issue failed {r[0]} {r[1][:100]}')
    r = post({'action': 'activate', 'key': key, 'device': dev1}); a = js(r)
    if r[0] != 200 or not a.get('token'): add(f'activate failed {r[1][:120]}')
    tok = a.get('token', '')
    r = post({'action': 'activate', 'key': key.lower(), 'device': dev1})
    if r[0] != 200: add('re-activate on the same device (lowercase key) should work')
    if post({'action': 'activate', 'key': key, 'device': dev2})[0] != 200: add('second device should be allowed')
    r = post({'action': 'activate', 'key': key, 'device': dev3})
    if r[0] != 409: add(f'third device should be refused, got {r[0]}')
    if post({'action': 'activate', 'key': 'AAAA-BBBB-CCCC-DDDD', 'device': dev1})[0] != 403: add('unknown key not refused')
    if post({'action': 'activate', 'key': key, 'device': 'x'})[0] != 400: add('bad device id not refused')
    # download
    if post({'action': 'download', 'token': 'junk.sig'})[0] != 403: add('download with junk token not refused')
    r = post({'action': 'download', 'token': tok})
    if r[0] != 200 or not r[1].startswith(b'PK'): add(f'download with valid token failed {r[0]}')
    # worker accepts the PHP token, rejects it under a different secret
    t1 = subprocess.run(['node', os.path.join(root, 'tests/worker/verify_token.mjs'), tok, 'worker-secret-123'], capture_output=True, text=True).stdout.strip()
    t2 = subprocess.run(['node', os.path.join(root, 'tests/worker/verify_token.mjs'), tok, 'other-secret'], capture_output=True, text=True).stdout.strip()
    if t1 != 'premium': add(f'Worker did not accept the PHP token: {t1}')
    if t2 == 'premium': add('Worker accepted a token under the wrong secret')
    # revoke blocks new activations
    if post({'action': 'revoke', 'admin': 'admin-secret-456', 'key': key})[0] != 200: add('revoke failed')
    if post({'action': 'activate', 'key': key, 'device': dev1})[0] != 403: add('revoked key still activates')
    # trial
    r = post({'action': 'trial', 'device': dev3}); t = js(r)
    if r[0] != 200 or t.get('tier') != 'trial': add(f'trial failed {r[1][:100]}')
    r = post({'action': 'trial', 'device': dev3})
    if r[0] != 200: add('repeat trial request on the same device should return the same running trial')
    # founder key supports 5 devices
    fk = js(post({'action': 'issue', 'admin': 'admin-secret-456', 'tier': 'founder'}))['key']
    okc = sum(post({'action': 'activate', 'key': fk, 'device': f'dev{i}_abcdefghijklmnopq'})[0] == 200 for i in range(6))
    if okc != 5: add(f'founder key bound {okc} devices, expected 5')
    # throttle: many wrong guesses
    codes = [post({'action': 'activate', 'key': f'ZZZZ-ZZZZ-ZZZZ-{i:04d}', 'device': dev1})[0] for i in range(10)]
    if 429 not in codes: add(f'no throttle on wrong guesses {codes}')
    st = open(d + '/state.json').read()
    if key in st or fk in st: add('plain keys are stored in the state file (should be hashed)')
finally:
    srv.terminate()
print('findings', len(bad)); sys.exit(1 if bad else 0)
