"""Persona 33: the AI sometimes returns numbers as strings ("72", "12g", "<1") - logging must not crash
("after.toFixed is not a function", Pete 5 Oct, duck/beef/broccoli/carrots)."""
import sys, re, json; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
FOOD = {"type": "food", "message": "Duck, beef, broccoli, carrots", "items": [
  {"name": "roast duck", "amount": "150g", "kcal": "330", "protein": "30g", "fat": "22", "carbs": "0"},
  {"name": "beef steak", "amount": "120g", "kcal": "260", "protein": "28", "fat": "16g", "carbs": "<1"},
  {"name": "broccoli", "amount": "100g", "kcal": 34, "protein": 2.8, "fat": 0.4, "carbs": "7", "fibre": "2.6g"},
  {"name": "carrots", "amount": "60g", "kcal": "25", "protein": "0.6", "fat": "0.1", "carbs": "6"}]}
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    ctx.route(re.compile(r'^https://api\.anthropic\.com/.*'), lambda r: r.fulfill(status=200, content_type='application/json',
        body=json.dumps({"content": [{"type": "text", "text": json.dumps(FOOD)}], "usage": {"input_tokens": 1, "output_tokens": 1}})))
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:160])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200)
    page.evaluate("onboardNext(2)"); page.fill('#onboardName', 'Pete'); page.evaluate("onboardNext(3)")
    page.evaluate("obSetSex('male')"); page.fill('#onboardAge', '56'); page.fill('#onboardHeight', '176')
    page.fill('#onboardWeight', '82'); page.fill('#onboardTarget', '78')
    page.evaluate("onboardNext(4)"); page.evaluate("obSetActivity('light')"); page.evaluate("obSetGoal('lose')")
    page.evaluate("onboardNext(5)"); page.evaluate("obSetCondition('gbm')")
    page.evaluate("onboardNext(6)"); page.evaluate("onboardFinish()"); page.wait_for_timeout(1500)
    page.evaluate("localStorage.setItem('mh_provider','claude');localStorage.setItem('mh_apikey','sk-ant-test-123')"); page.reload(); page.wait_for_timeout(1500)
    page.evaluate("switchTab('log')"); page.wait_for_timeout(300)
    page.evaluate("processMessage('Duck, beef, beef slices, broccoli, carrots')"); page.wait_for_timeout(2500)
    chat = page.evaluate("document.getElementById('chatScroll').innerText")
    if 'toFixed' in chat or 'Something broke' in chat: f.add('BUG', 'crash when AI returns numbers as strings: ' + chat[-300:])
    if not page.evaluate("!!document.getElementById('mealPreviewBubble')"): f.add('BUG', 'no meal preview shown')
    else:
        txt = page.evaluate("document.getElementById('mealPreviewBubble').innerText")
        if 'NaN' in txt: f.add('BUG', 'NaN in the preview: ' + txt[:300])
        if not re.search(r'6[4-9]\d\s*kcal|~?6[4-9]\d', txt): f.add('BUG', 'total kcal (649) not shown: ' + txt[:300])
    if errs: f.add('JS-exception', str(errs[:3]))
    b.close()
print('findings', len(f)); sys.exit(1 if f else 0)
