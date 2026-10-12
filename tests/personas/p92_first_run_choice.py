"""Persona 92: the first-run wizard offers 'what to start with'. Brain/simple apply their pack lists and layout, Everything applies nothing, preview applies nothing, the condition pre-selects, and the embedded packs match starter_packs/*.json."""
import sys, re, json; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
R = '/home/claude/maxhealth/'
html = open(R + 'maxhealth.html').read()
m = re.search(r'const MH_FIRST_RUN_PACKS = (\{.*?\});\n', html)
emb = json.loads(m.group(1)) if m else {}
for k, fn in (('brain', 'brain_tumour_tracking'), ('simple', 'general_wellbeing')):
    if emb.get(k, {}).get('sets') != json.load(open(R + f'starter_packs/{fn}.json'))['sets']:
        f.add('BUG', f'embedded {k} pack drifted from starter_packs/{fn}.json')

def run(pw, cond, choose, preview=False):
    b = pw.chromium.launch()
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page = ctx.new_page(); errs = []; page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("document.getElementById('onboardingOverlay').style.display='block'")
    if preview: page.evaluate("previewOnboarding()"); page.wait_for_timeout(300)
    page.evaluate(f"onboardNext(5); obSetCondition('{cond}')")
    page.evaluate("onboardNext('5b')")
    vis = page.evaluate("getComputedStyle(document.getElementById('step5b')).display")
    pre = page.evaluate("_obStart")
    if choose: page.evaluate(f"obSetStart('{choose}')")
    page.evaluate("onboardNext(6)")
    with page.expect_navigation(timeout=8000) if (choose != 'everything' and not preview) else page.expect_event('console', timeout=100) if False else __import__('contextlib').nullcontext():
        page.evaluate("onboardFinish()")
    page.wait_for_timeout(2500)
    res = page.evaluate("""() => ({ sym: (loadSymptomDefs()||[]).map(s=>s.name), hidden: localStorage.getItem('mh_dashboard_hidden'),
       fast: localStorage.getItem('mh_collapse_dc_fasting'), base: localStorage.getItem('mh_layout_base') })""")
    b.close(); return vis, pre, res, errs
with fresh_server() as root, sync_playwright() as pw:
    vis, pre, res, errs = run(pw, 'gbm', None)
    if vis != 'block': f.add('BUG', 'step 5b not shown')
    if pre != 'brain': f.add('BUG', f'gbm should pre-select brain, got {pre}')
    if 'Brain fog' not in res['sym'] and not res['sym']: f.add('BUG', 'brain pack lists not applied')
    if res['fast'] != 'closed' or not res['base']: f.add('BUG', f'brain layout not applied {res}')
    vis, pre, res, errs = run(pw, 'general', None)
    if pre != 'simple': f.add('BUG', f'general should pre-select simple, got {pre}')
    if not res['hidden'] or 'ketosis' not in res['hidden']: f.add('BUG', f'simple layout not applied {res}')
    if 'Low mood' not in res['sym']: f.add('BUG', f"simple symptoms missing {res['sym']}")
    vis, pre, res, errs = run(pw, 'gbm', 'everything')
    if res['hidden'] or res['base'] or res['sym']: f.add('BUG', f'everything must apply nothing {res}')
    vis, pre, res, errs = run(pw, 'general', 'simple', preview=True)
    if res['hidden'] or res['base']: f.add('BUG', f'preview must not apply anything {res}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
