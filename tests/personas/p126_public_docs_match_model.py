"""Persona 126: the public pages describe Free web app vs Premium and no longer hand out the DIY route (setup script, Termux steps, pipeline commands, launcher download), and still point to the register-interest page."""
import sys, re, os; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import REPO, Findings
f = Findings()
BAD = [r'termux', r'setup\.sh', r'raw\.githubusercontent', r'update_health', r'releases/latest', r'F-Droid', r'mhstart', r'open source', r'free, forever', r'no premium tier']
for rel in ('docs/user-guide.html', 'docs/story.html', 'docs/why-free.html', 'index.html'):
    t = open(os.path.join(REPO, rel), encoding='utf-8').read()
    for b in BAD:
        m = re.search(b, t, re.I)
        if m: f.add('BUG', f'{rel}: still contains "{m.group(0)}"')
    if 'pspence.co.uk/maxedhealth' not in t and rel != 'docs/why-free.html': f.add('BUG', f'{rel}: no link to the Premium register page')
g = open(os.path.join(REPO, 'docs/user-guide.html'), encoding='utf-8').read()
if 'Free web app' not in g or 'Premium' not in g: f.add('BUG', 'user guide lacks the Free vs Premium section')
if not os.path.exists(os.path.join(REPO, 'premium/user-guide-full.html')): f.add('BUG', 'full DIY guide not staged under premium/')
print('findings', len(f)); sys.exit(1 if f else 0)
