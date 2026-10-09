"""Persona 61: the Premium (local version) card. A cloud visitor sees the pitch and a Register interest link that only opens a
page (no request is made to it by the app, nothing from the app is sent); a local user sees a thank-you instead. The card
obeys show/hide, and the register-interest page and handler exist with the consent box and privacy note."""
import sys, re, os; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
HTML = open(os.path.join(REPO, 'maxhealth.html'), encoding='utf-8').read()
def mk(ctx, host, seen):
    def h(r):
        u = r.request.url; seen.append(u)
        if u.rstrip('/') in (f'https://{host}', f'http://{host}'): return r.fulfill(status=200, content_type='text/html', body=HTML)
        return r.abort()
    ctx.route(re.compile(r'.*'), h)
def card(page):
    page.evaluate("switchTab('settings'); switchSubTab('settings','manage')"); page.wait_for_timeout(900)
    page.evaluate("mhShowPremiumCard()")
    return page.evaluate("""() => ({ cloud: getComputedStyle(document.getElementById('mhPremiumCloud')).display !== 'none',
        local: getComputedStyle(document.getElementById('mhPremiumLocal')).display !== 'none',
        href: document.getElementById('mhPremiumLink').href, rel: document.getElementById('mhPremiumLink').rel,
        target: document.getElementById('mhPremiumLink').target })""")
with sync_playwright() as pw:
    b = pw.chromium.launch()
    for host, scheme, want_cloud in (('cloud.example', 'https', True), ('localhost', 'http', False)):
        seen = []; errs = []
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block'); mk(ctx, host, seen)
        page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:200]))
        page.goto(f'{scheme}://{host}/'); page.wait_for_timeout(1500)
        page.evaluate("localStorage.setItem('mh_onboarded','1')")
        c = card(page)
        if c['cloud'] != want_cloud or c['local'] == want_cloud: f.add('BUG', f'{host}: wrong Premium variant {c}')
        if want_cloud:
            if not c['href'].startswith('https://pspence.co.uk/'): f.add('BUG', f'Register interest link wrong: {c["href"]}')
            if 'noopener' not in c['rel'] or c['target'] != '_blank': f.add('BUG', 'link must open in a new tab with noopener')
            if any('pspence.co.uk' in u for u in seen): f.add('BUG', 'the app itself contacted the Premium page')
            # show/hide
            page.evaluate("toggleSection('set-premium','set-premium-wrap','set-premium-icon')")
            if page.evaluate("getComputedStyle(document.getElementById('set-premium-wrap')).display") != 'none': f.add('BUG', 'Premium card cannot be hidden')
            page.evaluate("toggleSection('set-premium','set-premium-wrap','set-premium-icon')")
            if page.evaluate("typeof siteSearchOpenSettings") != 'function': f.add('BUG', 'site search missing')
            if 'set-premium' not in page.evaluate("JSON.stringify(GENERIC_DEFAULT_ORDER.manage)"): f.add('BUG', 'Premium not in reorder list')
        if errs: f.add('BUG', f'{host}: page errors {errs[:2]}')
        ctx.close()
    b.close()
site = os.path.join(REPO, 'premium-site')
page_html = open(os.path.join(site, 'index.html'), encoding='utf-8').read()
php = open(os.path.join(site, 'register.php'), encoding='utf-8').read()
for k, msg in (('name="consent"', 'consent box missing'), ('What happens to your details', 'privacy note missing'), ('required', 'consent not required'),
               ('action="register.php"', 'form action wrong')):
    if k not in page_html: f.add('BUG', msg)
for k, msg in (("empty($_POST['consent'])", 'handler must require consent'), ('FILTER_VALIDATE_EMAIL', 'handler must validate email'),
               ('chmod($CSV, 0600)', 'sign-ups file must be private'), ("dirname($_SERVER['DOCUMENT_ROOT'])", 'data must sit outside the web root')):
    if k not in php: f.add('BUG', msg)
print('findings', len(f)); sys.exit(1 if f else 0)
