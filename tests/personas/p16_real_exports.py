"""Persona 16: REAL exports (Withings, RingConn, Zepp) replayed through a fresh install.
Private data: the files live OUTSIDE the repo (MH_FIXTURES, default /root/maxhealth_fixtures) and are never
committed. If they are absent (e.g. the nightly cloud run) the test is skipped and passes.
Reference: combined_*.csv from the same period (the real phone result) - values must agree."""
import sys, glob, shutil; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
FX = os.environ.get('MH_FIXTURES', '/root/maxhealth_fixtures')
zips = glob.glob(os.path.join(FX, '*.zip')); refs = glob.glob(os.path.join(FX, 'combined_*.csv'))
if len(zips) < 2:
    print('SKIP: no private fixtures at', FX); sys.exit(0)
f = Findings(); chk = lambda ok, msg: None if ok else f.add('BUG', msg)
with fresh_server() as root:
    dl = os.path.join(root, 'Download'); os.makedirs(dl)
    for z in zips: shutil.copy(z, dl)
    r = subprocess.run([sys.executable, '-c', f"import server; server.DOWNLOAD={dl!r}; print(server.move_exports_to_inbox())"],
                       cwd=os.path.join(root, 'app'), capture_output=True, text=True, timeout=120)
    moved = os.listdir(os.path.join(root, 'data', 'inbox'))
    chk(len(moved) == len(zips), f'sweep moved {len(moved)} of {len(zips)} real export zips: {moved}')
    rc, out = run_pipeline(root)
    chk(rc == 0 and 'Traceback' not in out, 'pipeline crashed on real exports: ' + out[-300:])
    c = read_combined(root)
    print('rows', len(c))
    chk(len(c) > 300, f'only {len(c)} days from real exports')
    for d, row in c.items():
        for fld, lo, hi in (('weight', 30, 300), ('steps', 0, 100000), ('sleep_duration', 0, 1440), ('hr_avg', 20, 250), ('hrv', 0, 300), ('spo2', 50, 100)):
            v = row.get(fld, '')
            if v not in ('', None) and not lo <= float(v) <= hi: f.add('BUG', f'{d}: {fld}={v} out of range')
    if refs:
        ref = {x['date']: x for x in csv.DictReader(open(refs[0], encoding='utf-8'))}
        for fld in ('weight', 'hrv', 'spo2', 'fat_pct'):
            both = same = 0
            for d in set(c) & set(ref):
                x, y = c[d].get(fld), ref[d].get(fld)
                if x and y:
                    both += 1; same += abs(float(x) - float(y)) <= max(0.6, abs(float(y)) * 0.02)
            print(f'  {fld}: {same}/{both} agree with the real phone result')
            chk(both == 0 or same / both >= 0.97, f'{fld}: only {same}/{both} agree with the real combined.csv')
print('findings', len(f)); sys.exit(1 if f else 0)
