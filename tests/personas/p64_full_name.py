"""Persona 64: the developer is credited by full name (Pete Spence) everywhere a person reads it, and no bare 'Pete' is left
in the app, the landing page or the docs (real export file names such as Activity-Pete-*.csv are the only allowed exceptions)."""
import sys, re, os; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
f = Findings()
bare = re.compile(r'(?<![-\w])Pete(?!\s+Spence)(?![-\w])')
for rel in ('maxhealth.html','index.html','README.md','TECHNICAL.md','docs/user-guide.html','docs/why-free.html','docs/story.html','gbm_patient_guide.html','.github/CODEOWNERS','premium-site/index.html'):
    t = open(os.path.join(REPO, rel), encoding='utf-8').read()
    n = len(bare.findall(t))
    if n: f.add('BUG', f'{rel}: {n} bare "Pete" left')
html = open(os.path.join(REPO, 'maxhealth.html'), encoding='utf-8').read()
if '<div class="settings-value">Pete Spence</div>' not in html: f.add('BUG', 'Settings "Developed by" does not show the full name')
print('findings', len(f)); sys.exit(1 if f else 0)
