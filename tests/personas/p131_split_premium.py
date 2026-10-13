"""Persona 131: the repo splits cleanly into a public free tree and a private Premium payload: every tracked file is classified, the free tree holds no server, pipeline, extractor, setup script, launcher APK or DIY guide, the public README replaces the internal one, and the Premium zip holds what a licensed phone needs."""
import sys, os, subprocess, tempfile, zipfile, re
root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
bad = []
def add(m): bad.append(m); print('  [BUG]', m)
out = tempfile.mkdtemp(prefix='mh_split_')
r = subprocess.run([sys.executable, os.path.join(root, 'tools/split_premium.py'), '--out', out], capture_output=True, text=True)
if r.returncode != 0: add('split reported unclassified files: ' + r.stdout[-300:])
free = os.path.join(out, 'free')
allfree = [os.path.relpath(os.path.join(d, f), free) for d, _, fs in os.walk(free) for f in fs]
for need in ('maxhealth.html', 'index.html', 'sw.js', 'manifest.json', 'starter_packs/index.json', 'lang/es.json', 'docs/user-guide.html', 'worker.js'):
    if need not in allfree: add(f'free tree is missing {need}')
for f in allfree:
    if re.search(r'(^server\.py|update_health|^extractors/|setup\.sh|mh_autoupdate|\.apk$|^premium/|^apk/|^tests/|user-guide-full)', f): add(f'premium file leaked into the free tree: {f}')
rd = open(os.path.join(free, 'README.md'), encoding='utf-8').read()
if re.search(r'termux|git clone|server\.py', rd, re.I) or 'Premium' not in rd: add('free README is still the internal one')
z = zipfile.ZipFile(os.path.join(out, 'premium_payload.zip')).namelist()
for need in ('server.py', 'update_health.py', 'extractors/ringconn.py', 'setup.sh'):
    if need not in z: add(f'premium zip is missing {need}')
if any(n.startswith('premium/') or n.startswith('tests/') for n in z): add('premium zip contains private material')
print('findings', len(bad)); sys.exit(1 if bad else 0)
