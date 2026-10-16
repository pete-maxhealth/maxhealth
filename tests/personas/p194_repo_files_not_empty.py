"""Persona 194: the files the public repo is judged by are never empty. README.md has been blanked twice by a disk-full commit (v1043 and v1048); this fails loudly if it happens again."""
import os, sys, json
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
MIN = {'README.md': 5000, 'CHANGELOG.md': 5000, 'TECHNICAL.md': 5000, 'BACKLOG.md': 500, 'maxhealth.html': 500000, 'server.py': 5000, 'worker.js': 2000,
       'docs/story.html': 5000, 'docs/user-guide.html': 5000, 'docs/changelog.html': 5000, 'docs/why-free.html': 1000, 'docs/legal.html': 1000, 'gbm_patient_guide.html': 50000}
bad = []
for f, n in MIN.items():
    p = os.path.join(ROOT, f)
    if not os.path.exists(p): bad.append(f'{f} missing'); continue
    if os.path.getsize(p) < n: bad.append(f'{f} only {os.path.getsize(p)} bytes')
for fn in sorted(os.listdir(os.path.join(ROOT, 'lang'))):
    p = os.path.join(ROOT, 'lang', fn)
    try:
        if len(json.load(open(p, encoding='utf-8'))) < 500: bad.append(f'lang/{fn} too small')
    except Exception as e: bad.append(f'lang/{fn} unreadable {e}')
print('findings', len(bad)); [print('  [BUG]', b) for b in bad]; sys.exit(1 if bad else 0)
