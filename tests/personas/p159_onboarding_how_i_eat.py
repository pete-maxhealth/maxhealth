"""Persona 159 (v3.10.1055): onboarding step 5c. A general profile picks Mediterranean + starter foods; a keto profile gets no lifestyle choice but the
keto starter set; Skip adds nothing. Works with no internet (the pool is embedded)."""
import sys; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
def run(pw, cond, ls, pool, label):
    b = pw.chromium.launch(); page = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1800)
    def call(js): return page.evaluate(js)
    call('onboardNext(2)'); page.fill('#onboardName', 'Jill'); call('onboardNext(3)'); call("obSetSex('female')"); page.fill('#onboardAge', '52')
    page.fill('#onboardHeight', '165'); page.fill('#onboardWeight', '70'); page.fill('#onboardTarget', '65'); call('onboardNext(4)')
    call("obSetActivity('light')"); call("obSetGoal('lose')"); call('onboardNext(5)'); call(f"obSetCondition('{cond}')"); call("obSetStart('everything')")
    call("onboardNext('5b')"); call("onboardNext('5c')"); page.wait_for_timeout(300)
    shown = call("document.getElementById('step5c').style.display")
    if shown != 'block': f.add('BUG', f'{label}: step 5c not shown')
    opts = call("document.querySelectorAll('#ob5cLifestyle .provider-btn').length")
    if cond == 'strict_keto' and opts: f.add('BUG', f'{label}: keto profile offered {opts} lifestyle choices')
    if cond == 'general' and opts != 5: f.add('BUG', f'{label}: expected 5 lifestyle choices, got {opts}')
    if ls: call(f"_obLifestyle='{ls}'; obRender5c()")
    call(f"document.getElementById('ob5cPool').checked={'true' if pool else 'false'}")
    call('onboardNext(6)'); call('onboardFinish()'); page.wait_for_timeout(1500)
    st = call("({ls:localStorage.getItem('mh_lifestyle'), n:mhPackLoadCurrent('library').filter(x=>x.source==='starter').length, r:mhPackLoadCurrent('recipes').filter(x=>x.source==='starter').length, oats:mhPackLoadCurrent('library').some(x=>/porridge oats/i.test(x.name)), cond:localStorage.getItem('mh_condition')})")
    if errs: f.add('BUG', f'{label}: page errors {errs[:2]}')
    b.close(); return st
with sync_playwright() as pw:
    with fresh_server() as root: a = run(pw, 'general', 'mediterranean', True, 'general+med')
    if a['ls'] != 'mediterranean': f.add('BUG', f'lifestyle not stored: {a}')
    if a['n'] < 140 or a['r'] < 30: f.add('BUG', f'starter foods not added: {a}')
    with fresh_server() as root: k = run(pw, 'strict_keto', 'mediterranean', True, 'keto')
    if k['ls']: f.add('BUG', f'keto profile stored a lifestyle: {k}')
    if k['n'] < 70 or k['oats']: f.add('BUG', f'keto starter set wrong: {k}')
    with fresh_server() as root: s = run(pw, 'general', '', False, 'skip')
    if s['ls'] or s['n'] or s['r']: f.add('BUG', f'skip added something: {s}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
