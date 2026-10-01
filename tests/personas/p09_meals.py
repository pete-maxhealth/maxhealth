"""Persona 9: logging meals. AI provider is stubbed (no network, no cost). Real taps, real preview, real totals."""
import sys, re; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
FOOD = {"type": "food", "items": [
    {"name": "chicken breast", "amount": "150g", "kcal": 248, "protein": 46.0, "fat": 5.4, "carbs": 0.0},
    {"name": "white rice", "amount": "100g", "kcal": 130, "protein": 2.7, "fat": 0.3, "carbs": 28.0}],
    "message": "Assumed 150g chicken and 100g cooked rice"}
PHRASES = ['chicken breast and rice', 'chicken and rice', 'I had chicken breast and rice for dinner', '150g chicken breast and 100g rice']
f = Findings()

def setup(page, cond, ctx_calls):
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200)
    page.evaluate("onboardNext(2)"); page.fill('#onboardName', 'Tess'); page.evaluate("onboardNext(3)")
    page.evaluate("obSetSex('female')"); page.fill('#onboardAge', '45'); page.fill('#onboardHeight', '168')
    page.fill('#onboardWeight', '70'); page.fill('#onboardTarget', '65')
    page.evaluate("onboardNext(4)"); page.evaluate("obSetActivity('light')"); page.evaluate("obSetGoal('maintain')")
    page.evaluate("onboardNext(5)"); page.evaluate(f"obSetCondition('{cond}')")
    page.evaluate("onboardNext(6)"); page.evaluate("onboardFinish()"); page.wait_for_timeout(1200)
    page.evaluate("localStorage.setItem('mh_provider','claude');localStorage.setItem('mh_apikey','sk-ant-test-key-123')")
    page.reload(); page.wait_for_timeout(1200)

with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch()
    for cond in ('general', 'gbm', 't1_diabetes'):
        for phrase in PHRASES:
            ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
            page = ctx.new_page(); errs = []; calls = []
            page.on('pageerror', lambda e: errs.append(str(e)[:150]))
            def stub(route):
                calls.append(route.request.post_data or '')
                route.fulfill(status=200, content_type='application/json',
                              body=json.dumps({"content": [{"type": "text", "text": json.dumps(FOOD)}], "usage": {"input_tokens": 1, "output_tokens": 1}}))
            ctx.route(re.compile(r'https://(cdn\.jsdelivr\.net|cdnjs\.cloudflare\.com|fonts\.(googleapis|gstatic)\.com)/.*'), lambda r: r.abort())  # fail fast, no 30s waits
            ctx.route('https://api.anthropic.com/**', stub)
            setup(page, cond, calls)
            page.click("[onclick^=\"switchTab('log'\"]"); page.wait_for_timeout(400)
            page.fill('#chatInput', phrase); page.click("[onclick=\"sendChat()\"]"); page.wait_for_timeout(2500)
            tag = f'{cond} / "{phrase}"'
            body = page.inner_text('body')
            if not calls: f.add('BUG', f'{tag}: meal never reached the AI; screen says: ' + re.sub(r"\s+", ' ', body[body.find(phrase):][:170]))
            else:
                sysprompt = str(json.loads(calls[0]).get('system', ''))
                ketoish = cond == 'gbm'
                if ('strict low-carb' in sysprompt) != ketoish: f.add('BUG', f'{tag}: AI told "strict low-carb" = {"strict low-carb" in sysprompt}, should be {ketoish}')
                if 'Total: 378kcal' not in body: f.add('BUG', f'{tag}: preview total wrong/missing')
                else:
                    page.click("[onclick='confirmMealLog()']"); page.wait_for_timeout(1500)
                    page.click("[onclick^=\"switchTab('today'\"]"); page.wait_for_timeout(800)
                    t = page.inner_text('body')
                    if '378kcal' not in t: f.add('BUG', f'{tag}: 378kcal not shown on Today after logging')
                    st = page.evaluate("(JSON.parse(localStorage.getItem('maxhealth_v1')||'{}').todayLog||[]).map(m=>(m.items||[]).length)")
                    if st != [2]: f.add('BUG', f'{tag}: expected one logged meal with 2 foods, stored {st}')
            if errs: f.add('JS-exception', f'{tag}: {errs[:2]}')
            print(f'  {tag}: done'); ctx.close()
    b.close()

# Suggestion requests (a generic category word + something) must STILL be treated as requests, not logs
SUGGEST = ['protein and pasta', 'meat and 2 veg']
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch()
    for phrase in SUGGEST:
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block'); page = ctx.new_page(); calls = []
        ctx.route(re.compile(r'https://(cdn\.jsdelivr\.net|cdnjs\.cloudflare\.com|fonts\.(googleapis|gstatic)\.com)/.*'), lambda r: r.abort())
        ctx.route('https://api.anthropic.com/**', lambda r: (calls.append(1), r.abort()))
        setup(page, 'general', calls); calls.clear()
        page.click("[onclick^=\"switchTab('log'\"]"); page.fill('#chatInput', phrase); page.click("[onclick=\"sendChat()\"]"); page.wait_for_timeout(1500)
        if 'library is empty' not in page.inner_text('body'): f.add('BUG', f'"{phrase}" was no longer treated as a suggestion request')
        ctx.close()
    b.close()
print('findings', len(f)); sys.exit(1 if f else 0)
