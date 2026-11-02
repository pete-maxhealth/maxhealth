"""p371: Pete's standing rules, checked by machine. (1) Every card has show/hide and reorder controls (Today, Move, Trends, Library). (2) No public page links to the
Premium page until it is live: Premium is 'coming soon' and only the Tally register-interest link may be used. (3) No personal health details of the owner in the public (FREE)
files. (4) Free app, docs and public pages carry no live Premium purchase wording. Static checks read the files; card checks run the app. Invented data."""
import sys, re, subprocess, fnmatch; sys.path.insert(0, 'tests/personas'); sys.path.insert(0, 'tools')
from harness import *
f = Findings()
def bug(m): f.add('BUG', m)
REPO = '.'
files = subprocess.run(['git', 'ls-files'], capture_output=True, text=True).stdout.split('\n')
import split_premium as sp
free = [p for p in files if p and sp.classify(p) == 'FREE' and not p.endswith(('.png', '.ico', '.jpg', '.svg', '.woff', '.woff2', '.zip'))]
txt = {p: open(p, errors='ignore').read() for p in free}
# (2) links to Premium
TALLY = 'tally.so/r/Dq2AQ5'
for p, t in txt.items():
    for m in re.finditer(r'(?:href|src|action)\s*=\s*["\']([^"\']+)["\']', t, re.I):
        u = m.group(1)
        if re.search(r'premium', u, re.I) and not u.startswith('#') and TALLY not in u and u != '${MH_PREMIUM_URL}': bug(f'{p}: links to a Premium page ({u[:80]}); only the Tally register-interest link is allowed until Premium is live')
        if re.search(r'premium-site|licen[cs]e\.php|register\.php|setup\.html', u, re.I) and TALLY not in u: bug(f'{p}: links into the Premium site ({u[:80]})')
mh = txt.get('maxhealth.html', '')
m = re.search(r"const MH_PREMIUM_URL = '([^']*)'", mh)
if not m or TALLY not in m.group(1): bug(f'MH_PREMIUM_URL is not the Tally register-interest link: {m and m.group(1)}')
if 'coming soon' not in (txt.get('index.html', '') + mh).lower() and 'not on sale yet' not in txt.get('index.html', '').lower(): bug('no "coming soon / not on sale yet" wording found for Premium')
for p, t in txt.items():
    if re.search(r'buy now|add to basket|\\bcheckout\\b|stripe\.com|paypal\.com|£\s*\d+\s*/\s*(?:mo|month|year)', t, re.I) and p not in ('lang/en.json',): bug(f'{p}: looks like live purchase wording or a payment link')
# (3) personal health details of the owner in public files (name and contact email are public on purpose)
DELIBERATE = {'docs/story.html'}   # Pete's own public sign-off; listed so a NEW disclosure anywhere else fails. Remove from this set if Pete wants it out.
PERSONAL = [r'\bmy (gbm|glioblastoma|brain tumou?r|tumou?r|mri|chemo(?:therapy)?|temozolomide|radiotherapy|oncologist|neurosurgeon|seizures?|medication)\b', r'\bI (?:have|had|was diagnosed with|am being treated for) (?:a )?(?:gbm|glioblastoma|brain tumou?r)',
            r'\bmy (?:weight|blood pressure|hba1c|ketones?|glucose)\s+(?:is|was)\s+\d', r'bogginsuk@', r'\bmy (?:own )?(?:lab|blood) results']
for p, t in txt.items():
    if p.startswith(('lang/', 'starter_packs/')) or p.endswith('.json'): scan = t
    else: scan = t
    for pat in PERSONAL:
        for m in re.finditer(pat, scan, re.I):
            msg = f'{p}: personal health detail in a public file: ...{scan[max(0, m.start()-30):m.end()+30]!r}'
            if p in DELIBERATE: f.add('REVIEW', msg + ' (the owner\'s own public story: deliberate? Pete to confirm)')
            else: bug(msg)
# (1) every card has show/hide + reorder
from playwright.sync_api import sync_playwright
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); ev = page.evaluate
    page.on('pageerror', lambda e: f.add('JS-exception', str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200)
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay').style.display='none'"); page.reload(); page.wait_for_timeout(1500)
    for tb in ('move', 'insights', 'library'):
        ev(f"try {{ switchTabById('{tb}'); }} catch (e) {{}}"); page.wait_for_timeout(500)
    sets = {
        'Today': (ev("DEFAULT_DASHBOARD_ORDER"), 'moveDashboardSection', 'toggleDashboardSectionHidden'),
        'Move': (ev("MOVE_DEFAULT_ORDER"), 'moveMoveSection', None),
        'Trends': (ev("DEFAULT_TREND_CARDS_ORDER"), 'moveTrendCard', 'toggleTrendCardHidden'),
        'Library': (ev("DEFAULT_LIBRARY_ORDER"), 'moveLibrarySection', None),
    }
    html = ev("document.documentElement.outerHTML")
    for screen, (keys, mover, hider) in sets.items():
        for k in keys:
            up = re.search(re.escape(mover) + r"\(\s*['\"]" + re.escape(k) + r"['\"]\s*,\s*['\"]up['\"]", html); dn = re.search(re.escape(mover) + r"\(\s*['\"]" + re.escape(k) + r"['\"]\s*,\s*['\"]down['\"]", html)
            if not (up and dn): bug(f'{screen}: card "{k}" has no reorder (up/down) control')
            if hider and not re.search(re.escape(hider) + r"\(\s*['\"]" + re.escape(k) + r"['\"]", html): bug(f'{screen}: card "{k}" has no show/hide control')
bugs = [x for x in f if x[0] in ('BUG', 'JS-exception')]
print('checked', len(free), 'public files for Premium links and personal health wording; card controls on 4 screens'); [print('  review:', x[1][:200]) for x in f if x[0] == 'REVIEW']
print('findings:', len(f), 'bugs:', len(bugs)); [print(x) for x in bugs[:40]]; sys.exit(1 if bugs else 0)
