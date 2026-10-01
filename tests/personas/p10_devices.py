"""Persona 10: device setup survives. Custom devices, retired list, file patterns, precedence and
user-written extractors live server-side + in the backup; a wiped browser gets them back."""
import sys, urllib.request, glob; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
U = 'http://localhost:5757'
def post(path, body):
    r = urllib.request.Request(U + path, json.dumps(body).encode(), {'Content-Type': 'application/json'})
    return json.loads(urllib.request.urlopen(r, timeout=10).read())
def get(path): return json.loads(urllib.request.urlopen(U + path, timeout=10).read())
OURA = '''
def run(inbox, password=None, dry_run=False):
    import os, json
    out = []
    for fn in os.listdir(inbox):
        if 'oura' in fn and fn.endswith('.json'):
            out += json.load(open(os.path.join(inbox, fn)))
    return out
'''
ds = days(5)

# A. server round trip + sanitising
with fresh_server() as root:
    if get('/devices').get('exists'): f.add('BUG', 'fresh install claims devices.json exists')
    r = post('/save-devices', {'custom': ['Oura', 'Oura', '  ', 5, 'x' * 99], 'retired': ['Garmin'],
                               'patterns': [{'device': 'Oura', 'contains': 'OURA', 'ext': 'zip'}, 'junk', {'device': '', 'contains': 'x'}]})
    d = get('/devices')
    if d['custom'] != ['Oura'] or d['retired'] != ['Garmin']: f.add('BUG', f'devices not stored/sanitised: {d}')
    if d['patterns'] != [{'device': 'Oura', 'contains': 'oura', 'ext': '.zip'}]: f.add('BUG', f'patterns not normalised: {d["patterns"]}')

# B. browser wipe: devices, patterns and precedence come back; migration of an old browser-only setup
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch()
    def newpage():
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
        ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
        pg = ctx.new_page(); return pg
    import re
    # old-style user: devices only in this browser's localStorage, nothing on the server yet
    pg = newpage(); pg.goto(U + '/'); pg.wait_for_timeout(1200)
    pg.evaluate("""localStorage.setItem('mh_custom_devices', JSON.stringify(['Oura']));
                   localStorage.setItem('mh_retired_devices', JSON.stringify(['Garmin']));
                   localStorage.setItem('mh_device_patterns', JSON.stringify([{device:'Oura',contains:'oura',ext:'.zip'}]));""")
    pg.evaluate("initSettings()"); pg.wait_for_timeout(1000)
    d = get('/devices')
    if not d.get('exists') or d['custom'] != ['Oura'] or d['retired'] != ['Garmin'] or not d['patterns']:
        f.add('BUG', f'existing browser-only devices were not migrated to the server: {d}')
    # user adds another device and a pattern through the app's own functions
    pg.evaluate("registerDevice('Fitbit')"); pg.wait_for_timeout(500)
    if 'Fitbit' not in get('/devices')['custom']: f.add('BUG', 'adding a device did not reach the server')
    pg.evaluate("movePrecedenceDevice('steps','Withings','up')"); pg.wait_for_timeout(600)   # saves precedence
    saved = get('/devices').get('source_precedence', {}).get('steps')
    # now the browser is wiped: brand new context = empty localStorage
    pg2 = newpage(); pg2.goto(U + '/'); pg2.wait_for_timeout(1200)
    pg2.evaluate("localStorage.removeItem('mh_custom_devices'); localStorage.removeItem('mh_retired_devices'); localStorage.removeItem('mh_device_patterns'); localStorage.removeItem('mh_device_precedence');")
    pg2.evaluate("initSettings()"); pg2.wait_for_timeout(1200)
    got = pg2.evaluate("({c: getAllDevices(), r: getRetiredDevices(), p: getDevicePatterns(), o: getMetricOrder('steps', getStoredPrecedence())})")
    if 'Oura' not in got['c'] or 'Fitbit' not in got['c']: f.add('BUG', f'custom devices lost after a browser wipe: {got["c"]}')
    if 'Garmin' in got['c'] or got['r'] != ['Garmin']: f.add('BUG', f'retired list lost after a browser wipe: {got["r"]}')
    if not got['p']: f.add('BUG', 'file patterns lost after a browser wipe')
    if saved and got['o'][:len(saved)] != [x for x in got['o'] if x]:
        pass
    if saved:
        inv = {'withings': 'Withings', 'ringconn': 'RingConn', 'amazfit': 'Zepp/Amazfit', 'garmin': 'Garmin', 'health_connect': 'Health Connect'}
        want = [inv[k] for k in saved if k in inv and inv[k] in got['o']]
        if got['o'][:len(want)] != want: f.add('BUG', f'precedence order not restored after wipe: server {saved} vs shown {got["o"]}')
    html = pg2.evaluate("document.getElementById('precedenceEditor').innerHTML")
    if 'oura' not in html.lower(): f.add('BUG', 'pattern chip / device not shown in the editor after wipe')
    # and the pattern UI path itself (real prompt) must not throw
    pg2.evaluate("editDevicePattern('Oura')"); pg2.wait_for_timeout(300)
    b.close()

# C. user extractor + user pattern, end to end (sweep -> pipeline -> combined.csv); backup + restore
with fresh_server() as root:
    os.makedirs(os.path.join(root, 'data', 'extractors'))
    open(os.path.join(root, 'data', 'extractors', 'oura.py'), 'w').write(OURA)
    post('/save-devices', {'custom': ['Oura'], 'patterns': [{'device': 'Oura', 'contains': 'oura', 'ext': '.json'}]})
    dl = os.path.join(root, 'Download'); os.makedirs(dl)
    json.dump([{'date': d, 'steps': 9000 + i, 'hr_avg': 61} for i, d in enumerate(ds)], open(os.path.join(dl, 'my_oura_2026.json'), 'w'))
    json.dump({'unrelated': 1}, open(os.path.join(dl, 'shopping_list.json'), 'w'))
    r = subprocess.run([sys.executable, '-c', f"import server; server.DOWNLOAD={dl!r}; print(server.move_exports_to_inbox())"],
                       cwd=os.path.join(root, 'app'), capture_output=True, text=True, timeout=60)
    inbox = os.listdir(os.path.join(root, 'data', 'inbox'))
    if 'my_oura_2026.json' not in inbox: f.add('BUG', f'user pattern did not pick the file up: {r.stdout[-150:]} {r.stderr[-150:]}')
    if 'shopping_list.json' in inbox: f.add('BUG', 'pattern grabbed an unrelated file')
    rc, out = run_pipeline(root); c = read_combined(root)
    if len(c) != 5 or any(not c[d].get('steps') for d in c): f.add('BUG', f'user extractor data missing from combined.csv ({len(c)} rows): {out[-300:]}')
    if c and 'oura' not in list(c.values())[0].get('source', ''): f.add('BUG', 'source column does not credit the custom device')
    ue = get('/devices')['user_extractors']
    if ue != [{'key': 'oura', 'overrides_builtin': False}]: f.add('BUG', f'/devices user_extractors wrong: {ue}')
    # a user extractor overriding a built-in is flagged
    open(os.path.join(root, 'data', 'extractors', 'ringconn.py'), 'w').write('def run(i, password=None, dry_run=False): return []\n')
    if not any(x['overrides_builtin'] for x in get('/devices')['user_extractors']): f.add('BUG', 'built-in override not flagged')
    run_pipeline(root)
    log = open(os.path.join(root, 'logs', 'pipeline.log')).read() if os.path.exists(os.path.join(root, 'logs', 'pipeline.log')) else ''
    if 'YOUR extractor' not in log: f.add('BUG', 'override of a built-in extractor not logged on the pipeline run')
    os.remove(os.path.join(root, 'data', 'extractors', 'ringconn.py'))
    # backup contains everything
    json.dump([{'date': ds[0], 'steps': 1}], open(os.path.join(root, 'data', 'inbox', 'oura_more.json'), 'w'))
    post('/save-precedence', {'source_precedence': {'steps': ['withings', 'ringconn']}})
    run_pipeline(root)
    bk = os.listdir(os.path.join(root, 'data', 'backup'))
    for pre in ('pipeline_prefs_', 'devices_', 'extractors_'):
        if not any(x.startswith(pre) for x in bk): f.add('BUG', f'{pre}* missing from the backup: {sorted(bk)[:12]}')
    # restore after a "lost phone": delete live copies then restore from backup
    for pth in ('data/devices.json', 'data/pipeline_prefs.json', 'data/extractors/oura.py'):
        os.remove(os.path.join(root, pth))
    for pre in ('pipeline_prefs_', 'devices_', 'extractors_'):
        fn = sorted(x for x in os.listdir(os.path.join(root, 'data', 'backup')) if x.startswith(pre))[-1]
        run_pipeline(root, '--restore', os.path.join(root, 'data', 'backup', fn))
    for pth in ('data/devices.json', 'data/pipeline_prefs.json', 'data/extractors/oura.py'):
        if not os.path.exists(os.path.join(root, pth)): f.add('BUG', f'{pth} not restored from backup')
print('findings', len(f)); sys.exit(1 if f else 0)
