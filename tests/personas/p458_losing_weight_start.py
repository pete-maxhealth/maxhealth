"""Persona 458: the first-run wizard offers "Losing weight" (Pete, 12 Nov 2026: dieters should not see Symptoms and Treatment).
A general-condition user who chose Lose is pre-selected into it; it applies no symptom/treatment lists and hides the Symptoms and Treatment cards and the advanced cards;
Today, Log and Trends show no Symptoms/Treatment text; Keep it simple and Brain are unchanged; the embedded pack matches starter_packs/losing_weight_start.json. Invented person."""
import sys, json, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
R = __import__('os').path.abspath(__import__('os').path.join(__import__('os').path.dirname(__file__), '..', '..')) + '/'
m = re.search(r'const MH_FIRST_RUN_PACKS = (\{.*?\});\n', open(R + 'maxhealth.html').read())
if json.loads(m.group(1)).get('loss', {}).get('sets') != json.load(open(R + 'starter_packs/losing_weight_start.json'))['sets']: f.add('BUG', '0: embedded loss pack drifted from starter_packs/losing_weight_start.json')
SEE = "[...document.querySelectorAll('body *')].filter(e=>e.offsetParent&&!e.children.length&&/symptom|treatment/i.test(e.textContent)&&!e.closest('#toast,.mh-grp-chip')).map(e=>e.textContent.trim().slice(0,60))"
def walk(pw, goal, cond, pick=None):
    ctx = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 844}, service_workers='block'); page = ctx.new_page(); ev = page.evaluate
    page.on('pageerror', lambda e: f.add('JS-exception', str(e)[:300])); page.on('dialog', lambda d: d.dismiss())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    ev('onboardNext(2)'); page.fill('#onboardName', 'Sam'); ev('onboardNext(3)'); ev("obSetSex('female')"); page.fill('#onboardAge', '33'); ev("setHeightUnit('cm')"); page.fill('#onboardHeight', '165'); ev("setWeightUnit('kg')"); page.fill('#onboardWeight', '75'); page.fill('#onboardTarget', '60')
    ev('onboardNext(4)'); ev("obSetActivity('light')"); ev(f"obSetGoal('{goal}')"); ev('onboardNext(5)'); ev(f"obSetCondition('{cond}')"); ev("onboardNext('5b')")
    pre = ev('_obStart'); shown = ev("!!document.getElementById('ob-startBtn-loss') && document.getElementById('ob-startBtn-loss').offsetParent !== null")
    if pick: ev(f"obSetStart('{pick}')")
    ev('onboardNext(6)')
    with page.expect_navigation(timeout=8000): ev('onboardFinish()')
    page.wait_for_timeout(2500); return page, ev, pre, shown
with fresh_server() as root, sync_playwright() as pw:
    page, ev, pre, shown = walk(pw, 'lose', 'general')
    if not shown: f.add('BUG', '1: the Losing weight choice is not on the start screen')
    if pre != 'loss': f.add('BUG', f'2: general + Lose should pre-select loss, got {pre}')
    if ev("(loadSymptomDefs()||[]).length") != 0: f.add('BUG', '3: symptom list was added')
    if ev("(typeof loadTreatmentDefs==='function'?loadTreatmentDefs():[]).length||0") != 0: f.add('BUG', '3b: treatment list was added')
    hid = json.loads(ev("localStorage.getItem('mh_dashboard_hidden')") or '[]')
    for k in ('symptoms', 'treatment', 'ketosis', 'fasting'):
        if k not in hid: f.add('BUG', f'4: {k} card not hidden: {hid}')
    for name, js in [('today', "switchTab('today'); switchSubTab('today','dash')"), ('log', "switchTab('log')"), ('trends', "switchTab('insights'); switchSubTab('insights','trends')")]:
        ev(js); page.wait_for_timeout(700); seen = ev(SEE)
        if not ev("[...document.querySelectorAll('.subview.active, #view-log.active')].some(e=>e.offsetParent)||document.querySelector('.card-unit,.water-card')?.offsetParent!==null"): f.add('BUG', f'5z: {name} is not showing, so the text check proves nothing')
        if seen: f.add('BUG', f'5: {name} still shows symptom/treatment text: {seen}')
    # the cards come back from Filter (nothing is lost): un-hide one
    ev("localStorage.setItem('mh_dashboard_hidden','[]')"); ev("switchTab('today'); switchSubTab('today','dash')"); page.wait_for_timeout(500)
    if not ev("!!document.getElementById('dashSection-symptoms')"): f.add('BUG', '6: the Symptoms card cannot be brought back')
    p2, e2, pre2, _ = walk(pw, 'lose', 'gbm')
    if pre2 != 'brain': f.add('BUG', f'7: gbm should still pre-select brain, got {pre2}')
    p3, e3, pre3, _ = walk(pw, 'maintain', 'general')
    if pre3 != 'simple': f.add('BUG', f'8: general + Maintain should still pre-select simple, got {pre3}')
    p4, e4, pre4, _ = walk(pw, 'lose', 'general', pick='simple')
    if e4("(loadSymptomDefs()||[]).length") != 6: f.add('BUG', '9: choosing Keep it simple after Lose did not give its six symptoms')
print('findings', len(f))
for x in f: print(x)
sys.exit(1 if f else 0)
