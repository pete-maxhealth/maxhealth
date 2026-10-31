#!/usr/bin/env python3
"""Split this repo into the PUBLIC free web app and the PRIVATE Premium payload.

Dry run (default) prints what goes where and checks nothing is left unclassified:
    python3 tools/split_premium.py
Build both trees and the Premium zip:
    python3 tools/split_premium.py --out /tmp/split

Nothing in the repo is modified or deleted. The output is what you would publish: the free tree to the public
repo / GitHub Pages, the zip to the licence server (premium_payload.zip). Premium and host-only files must never
be published to the public repo.
"""
import argparse, fnmatch, os, shutil, subprocess, sys, zipfile
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# First match wins. FREE = public web app. PREMIUM = delivered with a licence. HOST = lives on the GoDaddy host
# only. PRIVATE = development material kept in the private repo only (tests, scripts, notes).
RULES = [
    ('PREMIUM', ['server.py', 'update_health.py', 'extractors/*', 'amazfit.py', 'garmin*.py', 'fix_amazfit_steps.py',
                 'clear_day_sleep.py', 'pattern_detector.py', 'selfcheck.py', 'find_orphans.py', 'setup.sh', 'mh_autoupdate.sh',
                 'apk/*', 'premium/*']),
    ('HOST',    ['premium-site/*']),
    ('PRIVATE', ['tests/*', 'tools/*', 'server.py.bak', 'generate_test_data.py', 'test_garmin_*', 'bump_and_deploy.sh',
                 'deploy_docs.sh', 'BACKLOG.md', 'CLAUDE.md', 'TECHNICAL.md', 'main', '.github/*', '.gitignore',
                 'CHANGELOG.md', 'changelog.html', 'docs/changelog.html',
                 'LICENCE_WORKER_SETUP.md', 'licence-worker.js', 'wrangler.licence.toml']),
    ('FREE',    ['maxhealth.html', 'index.html', 'carer.html', 'changelog.html', 'gbm_patient_guide.html', 'sw.js', 'manifest.json',
                 'icons/*', 'lib/*', 'lang/*', 'starter_packs/*', 'docs/*', 'worker.js', 'LICENSE', 'README.md']),
]

# Files published under a different content in the free tree.
SUBSTITUTE = {'README.md': 'premium/public_README.md'}

def classify(path):
    for bucket, pats in RULES:
        if any(fnmatch.fnmatch(path, p) for p in pats): return bucket
    return None

def tracked():
    out = subprocess.run(['git', 'ls-files'], cwd=REPO, capture_output=True, text=True, check=True).stdout.split('\n')
    return [p for p in out if p]

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out'); a = ap.parse_args()
    buckets = {'FREE': [], 'PREMIUM': [], 'HOST': [], 'PRIVATE': []}; unknown = []
    for p in tracked():
        b = classify(p)
        (buckets[b] if b else unknown).append(p)
    for b, files in buckets.items(): print(f'{b:8} {len(files):4} files')
    if unknown:
        print('UNCLASSIFIED (add a rule before publishing):'); [print('  ', u) for u in unknown]; return 1
    if a.out:
        for b in ('FREE', 'PREMIUM', 'HOST', 'PRIVATE'):
            for p in buckets[b]:
                dst = os.path.join(a.out, b.lower(), p); os.makedirs(os.path.dirname(dst), exist_ok=True)
                src = SUBSTITUTE.get(p) if b == 'FREE' else None
                shutil.copy2(os.path.join(REPO, src or p), dst)
        zp = os.path.join(a.out, 'premium_payload.zip')
        with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED) as z:
            for p in buckets['PREMIUM']:
                if not p.startswith('premium/'): z.write(os.path.join(REPO, p), p)
        print('wrote', a.out, '(free/, premium/, host/, private/, premium_payload.zip)')
    return 0

if __name__ == '__main__':
    sys.exit(main())
