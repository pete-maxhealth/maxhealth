"""Persona 48: photo/meal prompt teaches count x per-piece weights, fresh vs jarred fruit, and small-portion sizing (the 80g 'fresh cherries' over-estimate, 7 Oct)."""
import sys, re, json; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
FOOD = {"type": "food", "items": [{"name": "cherries", "amount": "30g", "kcal": 20, "protein": 0.3, "fat": 0.1, "carbs": 4}], "message": "ok"}
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []; bodies = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    def stub(route):
        bodies.append(route.request.post_data or '')
        route.fulfill(status=200, content_type='application/json', body=json.dumps({"content": [{"type": "text", "text": json.dumps(FOOD)}], "usage": {"input_tokens": 1, "output_tokens": 1}}))
    ctx.route(re.compile(r'https://(cdn\.jsdelivr\.net|cdnjs\.cloudflare\.com|fonts\.(googleapis|gstatic)\.com)/.*'), lambda r: r.abort())
    ctx.route('https://api.anthropic.com/**', stub)
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:160]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200)
    page.evaluate("onboardNext(2)"); page.fill('#onboardName', 'Ola'); page.evaluate("onboardNext(3)")
    page.evaluate("obSetSex('male')"); page.fill('#onboardAge', '58'); page.fill('#onboardHeight', '176')
    page.fill('#onboardWeight', '82'); page.fill('#onboardTarget', '78')
    page.evaluate("onboardNext(4)"); page.evaluate("obSetActivity('light')"); page.evaluate("obSetGoal('lose')")
    page.evaluate("onboardNext(5)"); page.evaluate("obSetCondition('general')")
    page.evaluate("onboardNext(6)"); page.evaluate("onboardFinish()"); page.wait_for_timeout(1500)
    page.evaluate("localStorage.setItem('mh_provider','claude');localStorage.setItem('mh_apikey','sk-ant-test-key-123')")
    page.reload(); page.wait_for_timeout(1500)
    page.click("[onclick^=\"switchTab('log'\"]"); page.wait_for_timeout(500)
    page.fill('#chatInput', 'bowl of cherries'); page.click("[onclick=\"sendChat()\"]"); page.wait_for_timeout(2500)
    body = ' '.join(bodies)
    for needle in ['COUNTABLE ITEMS', 'jarred/tinned cherry ~4-5g', 'FRESH vs PRESERVED', 'SMALL PORTIONS']:
        if needle not in body: f.add('BUG', f'prompt missing: {needle}')
    if errs: f.add('BUG', f'page errors {errs[:3]}')
    b.close()
print('findings', len(f)); sys.exit(1 if f else 0)
