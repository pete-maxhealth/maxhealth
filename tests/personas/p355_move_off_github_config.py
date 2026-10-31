"""Persona 355 (v3.10.1246): everything the app fetches from or links to on GitHub comes from the one MH_HOME block. Part A: unchanged defaults still hit the same GitHub URLs.
Part B: the block is pointed at a different host (invented: files.example.test) and starter packs, a language file and the version check all go there, nothing goes to GitHub,
the story links follow `site`, and with no bug-report page configured the bug report copies instead of opening a window."""
import sys, re, os, json; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
R = '/home/claude/maxhealth/'
f = Findings()

def run(label, edit, block_local=False):
    seen = []
    with fresh_server() as root, sync_playwright() as pw:
        if edit:
            ap = os.path.join(root, 'app', 'maxhealth.html'); s = open(ap).read()
            for a, b in edit: assert a in s, a; s = s.replace(a, b)
            open(ap, 'w').write(s)
        b = pw.chromium.launch(); errs = []
        ctx = b.new_context(viewport={'width': 390, 'height': 900}, service_workers='block')
        def route(r):
            u = r.request.url; seen.append(u)
            m = re.search(r'/(starter_packs|lang)/([^/?]+)$', u)
            if m and not u.startswith('http://localhost'): r.fulfill(body=open(R + m.group(1) + '/' + m.group(2)).read(), content_type='application/json')
            elif u.endswith('/README.md') and not u.startswith('http://localhost'): r.fulfill(body='**Version:** v9.9.9', content_type='text/plain')
            elif block_local and re.search(r'^http://localhost:\d+/(starter_packs|lang)/', u): r.fulfill(status=404, body='{}', content_type='application/json')   # the app's own copy is missing
            elif u.startswith('http://localhost'): r.continue_()
            else: r.abort()
        ctx.route('**/*', route)
        p = ctx.new_page(); p.on('pageerror', lambda e: errs.append(str(e)[:200])); ev = p.evaluate
        p.goto('http://localhost:5757/'); p.wait_for_timeout(1500); ev("startDemoMode('doris')"); p.wait_for_timeout(2500)
        ev("mhBehindCheck(true)"); p.wait_for_timeout(600)
        ev("mhStarterPacks(); 0")
        p.wait_for_timeout(1200)
        ev("document.getElementById('mhPackModal')&&document.getElementById('mhPackModal').remove(); 0")
        ev("mhLangLoad('es')"); p.wait_for_timeout(800)
        site = ev("[...document.querySelectorAll('[data-mh-site]')].map(a=>a.href)")
        copied = ev("(async()=>{let opened=0; window.open=()=>{opened++}; window.mhBuildBugReportText=async()=>'info'; try{Object.defineProperty(navigator,'clipboard',{value:{writeText:async()=>{window.__copied=1}},configurable:true})}catch(e){} await mhReportBug(); return [opened, window.__copied||0]})()")
        if errs: f.add('JS-exception', f'{label}: {errs[0]}')
        b.close()
    return seen, site, copied

# Part A: defaults
seen, site, copied = run('defaults', None)
gh = [u for u in seen if 'raw.githubusercontent.com/pete-maxhealth/maxhealth/main/' in u]
if not any(u.endswith('/README.md') for u in gh): f.add('BUG', 'A1: the version check should still read README.md from GitHub by default')
if any('/lang/' in u or '/starter_packs/' in u for u in gh): f.add('BUG', 'A2: v3.10.1251: language files and starter packs come from the app\'s own address first, not GitHub')
if not any(re.search(r'localhost:\d+/lang/es\.json', u) for u in seen): f.add('BUG', 'A3: language files are read from the app\'s own copy')
if not any(re.search(r'localhost:\d+/starter_packs/index\.json', u) for u in seen): f.add('BUG', 'A4: starter packs are read from the app\'s own copy')
if not site or not all(h.startswith('https://pete-maxhealth.github.io/maxhealth/docs/story.html') for h in site): f.add('BUG', f'A4: story links unchanged by default: {site}')
if copied[0] != 1: f.add('BUG', f'A5: the bug report still opens a window by default: {copied}')

# Part B: another host, no issue tracker
edit = [("raw: 'https://raw.githubusercontent.com/pete-maxhealth/maxhealth/main/'", "raw: 'https://files.example.test/mh/'"),
        ("site: 'https://pete-maxhealth.github.io/maxhealth/'", "site: 'https://www.example.test/mh/'"),
        ("issues: 'https://github.com/pete-maxhealth/maxhealth/issues/new'", "issues: ''")]
seen, site, copied = run('moved', edit)
mine = [u for u in seen if 'files.example.test/mh/' in u]
if not any(u.endswith('/README.md') for u in mine): f.add('BUG', 'B1: version check follows MH_HOME.raw')
# Part C: the app's own copy is missing (404): the published copy at MH_HOME.raw is the fallback
seenC, _, _ = run('moved-fallback', edit, block_local=True)
mineC = [u for u in seenC if 'files.example.test/mh/' in u]
if not any('/lang/es.json' in u for u in mineC): f.add('BUG', 'C1: language files fall back to MH_HOME.raw')
if not any('/starter_packs/index.json' in u for u in mineC): f.add('BUG', 'C2: starter packs fall back to MH_HOME.raw')
if [u for u in seenC if 'github' in u]: f.add('BUG', 'C3: nothing should go to GitHub in the moved setup')
gone = [u for u in seen if 'github' in u]
if gone: f.add('BUG', f'B4: nothing should still go to GitHub: {gone[:3]}')
if not site or not all(h == 'https://www.example.test/mh/docs/story.html' for h in site): f.add('BUG', f'B5: story links follow MH_HOME.site: {site}')
if copied != [0, 1]: f.add('BUG', f'B6: with no bug-report page, copy instead of opening a window: {copied}')

bad = any(s in ('BUG', 'JS-exception') for s, _ in f)
for s, m in f: print(s, m)
print('BUGS' if bad else 'OK', len(f)); sys.exit(1 if bad else 0)
