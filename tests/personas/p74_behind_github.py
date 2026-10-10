"""Persona 74: a phone that is behind GitHub says so (banner + About note), stays quiet when current or offline, and a dismissal sticks until a newer version appears."""
import sys, re; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
def run(pw, root, readme, status=200, name=''):
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    def route(r):
        if 'raw.githubusercontent.com' in r.request.url:
            if readme is None: return r.abort()
            return r.fulfill(status=status, body=readme, headers={'access-control-allow-origin': '*', 'content-type': 'text/plain'})
        if not r.request.url.startswith('http://localhost'): return r.abort()
        r.continue_()
    ctx.route(re.compile(r'.*'), route)
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200)
    return b, ctx, page, errs
with fresh_server() as root, sync_playwright() as pw:
    # 1. behind: banner appears
    b, ctx, page, errs = run(pw, root, '# X\n**Version:** v3.10.999\n')
    page.evaluate("localStorage.setItem('mh_onboarded','1'); localStorage.removeItem('mh_behind_checked'); mhBehindCheck(true)"); page.wait_for_timeout(600)
    if not page.query_selector('#mhBehindBanner'): f.add('BUG', 'no banner when GitHub is ahead')
    else:
        t = page.inner_text('#mhBehindBanner')
        if 'v3.10.999' not in t or 'mh_autoupdate' not in t: f.add('BUG', f'banner text unhelpful: {t[:120]}')
        page.click('#mhBehindClose'); page.wait_for_timeout(200)
        if page.query_selector('#mhBehindBanner'): f.add('BUG', 'Dismiss did not remove banner')
        page.evaluate("mhBehindRender()")
        if page.query_selector('#mhBehindBanner'): f.add('BUG', 'dismissed version came back')
    # About note still tells the truth after dismissal
    page.evaluate("switchTab('settings'); switchSubTab('settings','about')"); page.wait_for_timeout(400)
    if 'v3.10.999' not in page.evaluate("document.getElementById('mhBehindNote').textContent"): f.add('BUG', 'About note missing while behind')
    # 2. newer release un-dismisses
    page.evaluate("localStorage.setItem('mh_latest_ver','v3.10.1000'); mhBehindRender()"); page.wait_for_timeout(200)
    if not page.query_selector('#mhBehindBanner'): f.add('BUG', 'a newer version should show the banner again after a dismissal')
    if errs: f.add('BUG', f'page errors: {errs[:2]}')
    b.close()
    # 3. current: silent
    b, ctx, page, errs = run(pw, root, '**Version:** v3.10.946\n')
    page.evaluate("localStorage.removeItem('mh_behind_checked'); mhBehindCheck(true)"); page.wait_for_timeout(600)
    if page.query_selector('#mhBehindBanner'): f.add('BUG', 'banner shown although up to date')
    b.close()
    # 4. offline / junk: silent, no errors
    for rd, st in ((None, 200), ('nothing here', 200), ('x', 404)):
        b, ctx, page, errs = run(pw, root, rd, st)
        page.evaluate("localStorage.removeItem('mh_latest_ver'); localStorage.removeItem('mh_behind_checked'); mhBehindCheck(true)"); page.wait_for_timeout(600)
        if page.query_selector('#mhBehindBanner'): f.add('BUG', f'banner shown on failed check ({rd!r},{st})')
        if errs: f.add('BUG', f'errors on failed check: {errs[:2]}')
        b.close()
    # 5. version compare is numeric, not text
    b, ctx, page, errs = run(pw, root, '**Version:** v3.10.946\n')
    if not page.evaluate("mhVerNum('v3.10.1000') > mhVerNum('v3.10.999') && mhVerNum('v3.11.1') > mhVerNum('v3.10.9999')"): f.add('BUG', 'version compare is not numeric')
    b.close()
print('findings', len(f)); sys.exit(1 if f else 0)
