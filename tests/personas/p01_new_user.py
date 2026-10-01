"""Persona 1: brand-new user walks the setup wizard in many variants."""
import sys, re, itertools; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
NOISE = ('ERR_TUNNEL', 'status of 404', 'ERR_NAME_NOT_RESOLVED', 'cdn.jsdelivr', 'cdnjs', 'fonts.g')
VARIANTS = [
  dict(name='Alex', sex='male', age='40', hu='cm', h='175', wu='kg', w='80.5', t='75', act='light', goal='lose', cond='general'),
  dict(name='Sam', sex='female', age='33', hu='ft', h='5.6', wu='lbs', w='160', t='145', act='moderate', goal='maintain', cond='general'),
  dict(name='Pat', sex='male', age='56', hu='cm', h='180', wu='st', w='13', t='12', act='sedentary', goal='lose', cond='gbm'),
  dict(name='Dee', sex='female', age='29', hu='cm', h='165', wu='kg', w='60', t='', act='active', goal='gain', cond='t1_diabetes'),
  dict(name='Kim', sex='female', age='71', hu='cm', h='158', wu='kg', w='72', t='65', act='light', goal='lose', cond='epilepsy'),
  dict(name='X', sex='male', age='', hu='cm', h='', wu='kg', w='', t='', act=None, goal=None, cond=None),  # skips everything
]
def run(v, pw):
    f = Findings(); b = pw.chromium.launch()
    page = b.new_context(viewport={'width':390,'height':844}).new_page()
    page.on('console', lambda m: f.add('console-error', m.text[:160]) if m.type=='error' and not any(n in m.text for n in NOISE) else None)
    page.on('pageerror', lambda e: f.add('JS-exception', str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(2000)
    def call(js):
        try: page.evaluate(js)
        except Exception as e: f.add('JS-exception', f'{js[:40]}: {str(e)[:120]}')
    call('onboardNext(2)'); page.fill('#onboardName', v['name']); call('onboardNext(3)')
    call(f"obSetSex('{v['sex']}')"); page.fill('#onboardAge', v['age'])
    call(f"setHeightUnit('{v['hu']}')"); page.fill('#onboardHeight', v['h'])
    call(f"setWeightUnit('{v['wu']}')"); page.fill('#onboardWeight', v['w']); page.fill('#onboardTarget', v['t'])
    call('onboardNext(4)')
    if v['act']: call(f"obSetActivity('{v['act']}')")
    if v['goal']: call(f"obSetGoal('{v['goal']}')")
    kcal = page.input_value('#onboardKcal'); prot = page.input_value('#onboardProtein')
    if not v['age'] and kcal not in ('', '0'): f.add('check', f'kcal={kcal} computed with no age/height/weight')
    if v['age'] and not kcal: f.add('BUG?', 'no kcal target computed from complete profile')
    call('onboardNext(5)')
    if v['cond']: call(f"obSetCondition('{v['cond']}')")
    call('onboardNext(6)'); call('onboardFinish()'); page.wait_for_timeout(1500)
    ob = page.evaluate("getComputedStyle(document.getElementById('onboardingOverlay')).display")
    if ob != 'none': f.add('BUG', f'wizard still showing after Finish (display={ob})')
    txt = page.inner_text('body')
    for bad in ('NaN', 'undefined', 'null', 'Infinity', '[object'):
        if re.search(r'\b'+re.escape(bad)+r'\b', txt): f.add('BUG', f'"{bad}" visible on Today screen')
    stored = page.evaluate("({kcal:localStorage.getItem('mh_target_kcal'),name:localStorage.getItem('mh_name')||localStorage.getItem('mh_user_name')})")
    print(f"  {v['name']}: kcal field='{kcal}' protein='{prot}' stored={stored}")
    page.screenshot(path=f"/tmp/claude-0/work/p01_{v['name']}.png"); b.close(); return f
total = 0
with fresh_server() as root, sync_playwright() as pw:
    for v in VARIANTS:
        print('variant', v['name'], v['hu'], v['wu'], v['cond']); total += len(run(v, pw))
print('TOTAL findings:', total)
