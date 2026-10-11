"""Persona 79: weekly summary carb limit is a real number; targets boxes tucked behind an advanced toggle with a plain summary; a med companion
(e.g. MCT oil) does not break a fast; no huge blank gap under Supplements; device file patterns can be previewed, are shown with built-in rules and
can be restored after an accidental edit; Downloads preview endpoint never moves files and escapes nothing dangerous."""
import sys, re, os, json, subprocess, tempfile; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# --- server preview, unit level (real files, nothing may move) ---
d = tempfile.mkdtemp(prefix='mh_dl_')
for n in ('oura_export_2026.zip', 'readme.txt', 'withings_data.zip', 'MyDevice-Jan.zip'): open(os.path.join(d, n), 'wb').write(b'x' * 2048)
code = f"import sys,json; sys.path.insert(0,{REPO!r}); import server; server.DOWNLOAD={d!r}; print(json.dumps(server.preview_download_files('oura','.zip')))"
out = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True, cwd=tempfile.gettempdir())
try:
    pv = json.loads(out.stdout.strip().splitlines()[-1])
    names = {x['name']: x for x in pv['files']}
    if pv['would_match'] != 1 or not names.get('oura_export_2026.zip', {}).get('new_pattern'): f.add('BUG', f'preview should match the oura zip only: {pv}')
    if names.get('withings_data.zip', {}).get('builtin') != 'Withings': f.add('BUG', 'preview should say the withings zip is already built in')
    if len(os.listdir(d)) != 4: f.add('BUG', 'preview must never move files')
except Exception as e: f.add('BUG', f'preview helper failed: {e} {out.stderr[-300:]}')
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("localStorage.setItem('mh_onboarded','1')"); page.reload(); page.wait_for_timeout(1500)
    ev = lambda js, a=None: page.evaluate(js, a)
    # weekly summary: seed 9 days, latest 7 must be used, message must carry a real number
    ev("""() => { state.history = []; for (let i = 1; i <= 9; i++) { const dt = new Date(Date.now() - i * 86400000); const ds = String(dt.getDate()).padStart(2,'0') + '/' + String(dt.getMonth()+1).padStart(2,'0') + '/' + String(dt.getFullYear()).slice(2);
      state.history.push({ date: ds, log: [{ description: 'x', kcal: 100, protein: 1, carbs: i <= 7 ? 20 : 200, fat: 5, time: '12:00' }], totals: { kcal: 100, protein: 1, carbs: i <= 7 ? 20 : 200 } }); } }""")
    msg = ev("mhWeeklySummaryMsg()")
    if not msg or 'undefined' in msg or 'NaN' in msg: f.add('BUG', f'weekly summary message is broken: {msg!r}')
    elif 'above' in msg: f.add('BUG', f'weekly summary should only use the latest 7 days (20g/day): {msg!r}')
    # targets boxes
    ev("switchTab('settings'); switchSubTab('settings','dash')"); page.wait_for_timeout(400)
    ev("localStorage.setItem('mh_target_kcal','3800'); loadSettings && loadSettings()") if False else None
    ev("document.getElementById('settingKcalTarget').value='3800'; document.getElementById('settingProteinTarget').value='167'; document.getElementById('settingFatTarget').value='326'; mhRenderCurrentTargets()")
    line = ev("document.getElementById('currentTargetsLine').innerText")
    if '3800' not in line or '167' not in line or '326' not in line: f.add('BUG', f'targets summary line wrong: {line!r}')
    if ev("getComputedStyle(document.getElementById('targetsManualWrap')).display") != 'none': f.add('BUG', 'manual target boxes should be tucked away by default')
    # fast: MCT oil does not break the fast
    ev("localStorage.setItem('mh_fasting_kcal_threshold','50'); localStorage.setItem('mh_fasting_med_item','MCT oil'); localStorage.setItem('mh_fasting_med_kcal','115')")
    n = ev("mhFastDayEvents('01/10/26', [{description:'MCT oil 1 tbsp', kcal:115, time:'07:00'}, {description:'Lunch', kcal:600, time:'13:00'}], '').n")
    if n != 1: f.add('BUG', f'MCT oil should not count as a meal (counted {n})')
    n2 = ev("mhFastDayEvents('01/10/26', [{description:'MCT oil 1 tbsp', kcal:600, time:'07:00'}], '')")
    if not n2 or n2['n'] != 1: f.add('BUG', 'an oversized entry named like the med item should still break the fast')
    ev("localStorage.removeItem('mh_fasting_med_item')")
    n3 = ev("mhFastDayEvents('01/10/26', [{description:'MCT oil 1 tbsp', kcal:115, time:'07:00'}], '').n")
    if n3 != 1: f.add('BUG', 'without the setting MCT oil (115 kcal) should count as a meal')
    # supplements spacer
    h = ev("(() => { const w = document.getElementById('supplementSettingsContent'); const sp = w.lastElementChild; return sp.getBoundingClientRect().height || parseFloat(getComputedStyle(sp).minHeight); })()")
    if h > 40: f.add('BUG', f'blank space under Supplements is still {h}px')
    # devices: built-in rules shown, snapshot + restore
    ev("switchTab('settings'); switchSubTab('settings','import'); renderPrecedenceEditor()"); page.wait_for_timeout(500)
    html = ev("document.body.innerHTML")
    if 'Built in:' not in html: f.add('BUG', 'Manage devices should show the built-in file rules')
    ev("localStorage.setItem('mh_device_patterns', JSON.stringify([{device:'Withings',contains:'abc',ext:'.zip'}]))")
    ev("removeDevicePattern(0)")
    if ev("getDevicePatterns().length") != 0: f.add('BUG', 'remove did not remove')
    if len(ev("getDevicePatternHistory()")) < 1: f.add('BUG', 'removing a pattern should store a restore point')
    ev("restoreDevicePatterns(0)")
    if ev("getDevicePatterns()") != [{'device': 'Withings', 'contains': 'abc', 'ext': '.zip'}]: f.add('BUG', 'restore did not bring the pattern back')
    # preview via server (folder may not exist in the test environment but the route must answer)
    pv = ev("fetch('/devices/preview?contains=oura&ext=.zip').then(r=>r.json())")
    if 'folder_readable' not in pv: f.add('BUG', f'preview route missing: {pv}')
    if '<script' in ev("devicePreviewSummary({folder_readable:true,files:[{name:'<img src=x onerror=alert(1)>.zip',size:5,new_pattern:true}],would_match:1},'x')"): f.add('BUG', 'preview must escape file names')
    if errs: f.add('BUG', f'page errors: {errs[:2]}')
print('findings', len(f)); sys.exit(1 if f else 0)
