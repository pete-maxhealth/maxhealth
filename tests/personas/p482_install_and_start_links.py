"""Persona 482 (v3.10.1400): Add to home screen button (Settings > About and the welcome box) and start links (?start=, ?demo=).
Button: same look as the Check for updates button beside it; Chrome's install prompt is used when offered; otherwise a how-to for iPhone / Android / other;
hidden when already installed (standalone) and in demo mode; translated. Start links: only a brand-new install is pointed at the goal, junk values do nothing,
the address is cleaned, a demo link opens that persona and the real data is untouched. Invented data only."""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
BLOCK = re.compile(r'https://(cdn\.jsdelivr\.net|cdnjs\.cloudflare\.com|fonts\.(googleapis|gstatic)\.com)/.*')
IOS = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
AND = 'Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Mobile Safari/537.36'
def mk(pw, ua=None):
    b = pw.chromium.launch(); kw = dict(viewport={'width': 390, 'height': 844}, service_workers='block')
    if ua: kw['user_agent'] = ua
    ctx = b.new_context(**kw); ctx.route(BLOCK, lambda r: r.abort()); page = ctx.new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:160])); return b, page, errs
with fresh_server() as r, sync_playwright() as pw:
    # --- the button, as a returning user on an iPhone-like browser
    b, page, errs = mk(pw, IOS); ev = page.evaluate
    page.goto('http://localhost:5757/'); page.wait_for_timeout(800)
    ev("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev("document.getElementById('onboardingOverlay')&&(document.getElementById('onboardingOverlay').style.display='none')")
    ev("siteSearchOpenSettings('set-about','manage','settings','')"); page.wait_for_timeout(700)
    look = ev("""(()=>{const a=document.getElementById('mhInstallBtn'),c=document.getElementById('checkUpdateBtn');if(!a||!c)return null;const g=e=>{const s=getComputedStyle(e);return [s.display==='none'?'none':'shown',s.fontSize,s.fontFamily,s.borderTopWidth,s.borderRadius,s.paddingTop,s.color,s.width].join('|')};return {a:g(a),c:g(c),cls:a.className===c.className,hint:getComputedStyle(document.getElementById('mhInstallHint')).display}})()""")
    if not look: f.add('FAIL', 'install button missing')
    else:
        look['a'].startswith('shown') or f.add('FAIL', f'button not shown in a browser tab: {look}')
        look['a'] == look['c'] or f.add('FAIL', f'button does not look like Check for updates: {look}')
        look['cls'] or f.add('FAIL', 'button class differs from Check for updates')
        look['hint'] == 'block' or f.add('FAIL', 'hint not shown')
    ev("mhInstallApp()"); page.wait_for_timeout(300)
    txt = ev("document.body.innerText")
    'Safari' in txt and 'Share button' in txt or f.add('FAIL', 'iPhone how-to not shown')
    ev("document.querySelectorAll('.app-modal-overlay').forEach(o=>o.remove())")
    # install prompt path
    ev("window._pc=0; const e=new Event('beforeinstallprompt'); e.prompt=()=>{window._pc++}; e.userChoice=Promise.resolve({outcome:'accepted'}); window.dispatchEvent(e)")
    ev("mhInstallApp()"); page.wait_for_timeout(200)
    ev("window._pc") == 1 or f.add('FAIL', 'the browser install prompt was not used when offered')
    ev("document.querySelectorAll('.app-modal-overlay').length") == 0 or f.add('FAIL', 'how-to shown although the real prompt was available')
    # standalone and demo hide it
    ev("window.matchMedia = q => ({matches: /standalone/.test(q), addEventListener(){}, removeEventListener(){}}); mhInstallRefresh()")
    ev("getComputedStyle(document.getElementById('mhInstallBtn')).display") == 'none' or f.add('FAIL', 'shown although already installed')
    ev("window.matchMedia = q => ({matches: false, addEventListener(){}, removeEventListener(){}}); mhInstallRefresh()")
    ev("getComputedStyle(document.getElementById('mhInstallBtn')).display") != 'none' or f.add('FAIL', 'not shown again after the standalone flag cleared')
    ev("startDemoMode('doris')"); page.wait_for_timeout(1500)
    ev("mhInstallRefresh(); getComputedStyle(document.getElementById('mhInstallBtn')).display") == 'none' or f.add('FAIL', 'shown in demo mode')
    errs and f.add('FAIL', f'page errors {errs}'); b.close()
    # --- Android wording and Spanish
    b, page, errs = mk(pw, AND); ev = page.evaluate
    page.goto('http://localhost:5757/'); page.wait_for_timeout(800)
    ev("state.onboarded=true; saveState(); localStorage.setItem('mh_lang','es')"); page.reload(); page.wait_for_timeout(2000)
    ev("mhInstallApp()"); page.wait_for_timeout(400)
    t = ev("document.body.innerText")
    'Instalar app' in t and 'Chrome' in t or f.add('FAIL', f'Android how-to not in Spanish: {t[-300:]}')
    'Add to your home screen' in t and f.add('FAIL', 'title left in English')
    errs and f.add('FAIL', f'page errors {errs}'); b.close()
    # --- start links
    b, page, errs = mk(pw); ev = page.evaluate
    page.goto('http://localhost:5757/?start=lose&lang=en'); page.wait_for_timeout(2500)
    g = ev("({goal:_obGoal, start:_obStart, cond:_obCondition, url:location.search})")
    g['goal'] == 'lose' and g['start'] == 'loss' or f.add('FAIL', f'?start=lose did not point the wizard at losing weight: {g}')
    'start=' in g['url'] and f.add('FAIL', f'start param left in the address: {g}')
    b.close()
    for q, want in (('start=muscle', ('recomp', 'gain')), ('start=t2d', ('t2_diabetes', 'lose')), ('start=lowcarb', ('strict_keto', 'lose'))):
        b, page, errs = mk(pw); ev = page.evaluate
        page.goto('http://localhost:5757/?' + q); page.wait_for_timeout(2500)
        g = ev("({goal:_obGoal, cond:_obCondition})")
        (g['cond'], g['goal']) == want or f.add('FAIL', f'{q}: got {g}, wanted {want}')
        b.close()
    b, page, errs = mk(pw); ev = page.evaluate
    page.goto('http://localhost:5757/?start=nonsense'); page.wait_for_timeout(2000)
    g = ev("({goal:_obGoal, cond:_obCondition, chosen:_obGoalChosen})")
    g == {'goal': 'maintain', 'cond': 'general', 'chosen': False} or f.add('FAIL', f'junk start value changed something: {g}')
    b.close()
    # a returning user is never changed
    b, page, errs = mk(pw); ev = page.evaluate
    page.goto('http://localhost:5757/'); page.wait_for_timeout(800)
    ev("state.onboarded=true; localStorage.setItem('mh_condition','t2_diabetes'); saveState()")
    page.goto('http://localhost:5757/?start=muscle'); page.wait_for_timeout(2000)
    ev("localStorage.getItem('mh_condition')") == 't2_diabetes' or f.add('FAIL', 'a start link changed a returning user\'s condition')
    # demo link
    page.goto('http://localhost:5757/?demo=doris'); page.wait_for_timeout(3000)
    ev("_demoMode === true && _demoPersonaId === 'doris'") or f.add('FAIL', '?demo=doris did not open the Doris demo')
    ev("exitDemoMode()"); page.wait_for_timeout(500)
    ev("localStorage.getItem('mh_condition')") == 't2_diabetes' or f.add('FAIL', 'real condition lost after a demo link')
    page.goto('http://localhost:5757/?demo=zzz'); page.wait_for_timeout(2000)
    ev("_demoMode") is False or f.add('FAIL', 'unknown demo id opened a demo')
    errs and f.add('FAIL', f'page errors {errs}'); b.close()
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
