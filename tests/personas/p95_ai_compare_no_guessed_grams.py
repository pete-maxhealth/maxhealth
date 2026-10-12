"""Persona 95: the 3-AI comparison on a logged meal sends an amount to the checkers ONLY if the person stated it; guessed grams are left out so each AI judges the portion itself, and the answers are scaled back to the logged amount for comparing/averaging."""
import sys, re, json; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
def worker_reply(route):
    body = json.loads(route.request.post_data or '{}'); bodies.append(body.get('prompt', ''))
    mk = lambda k, g: {'ok': True, 'text': f'KCAL: {k}\nPROTEIN: 3\nFAT: 40\nCARBS: 10\nPORTION_G: {g}\nPORTION_KCAL: {k}'}
    route.fulfill(status=200, content_type='application/json', headers={'Access-Control-Allow-Origin': '*'},
                  body=json.dumps({'claude': mk(400, 80), 'gemini': mk(400, 80), 'openai': mk(400, 80)}))
bodies = []
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.route(re.compile(r'maxhealth-ai\.bogginsuk\.workers\.dev'), worker_reply)
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("localStorage.setItem('mh_onboarded','1')"); page.reload(); page.wait_for_timeout(1800)
    page.evaluate("document.querySelectorAll('[id*=nboard]').forEach(e=>{ if(e.style) e.style.display='none'; })")
    # 1) amounts guessed by the first AI, person gave none
    page.evaluate("""()=>{ switchTab('log'); window._pendingMealText='clotted cream with frozen raspberries'; window._pendingMealFoods=[{name:'clotted cream',amount:'90g',kcal:300,protein:2,carbs:2,fat:30},{name:'frozen raspberries',amount:'70g',kcal:30,protein:1,carbs:6,fat:0}]; }""")
    page.evaluate("runMultiAICheck()"); page.wait_for_timeout(1500)
    p1 = bodies[-1] if bodies else ''
    if re.search(r'90\s*g|70\s*g', p1.split('The person')[0]): f.add('BUG', f'guessed grams were sent: {p1[:160]}')
    if 'judge the realistic portion yourself' not in p1: f.add('BUG', 'no-amount wording missing')
    # scaled: each AI said 400kcal for 80g; logged 160g -> comparison/average uses 800
    k = page.evaluate("(()=>{const r=window._multiAIResults; return null})()")
    # 2) person stated the grams
    page.evaluate("""()=>{ window._pendingMealText='90g clotted cream'; window._pendingMealFoods=[{name:'clotted cream',amount:'90g',kcal:300,protein:2,carbs:2,fat:30}]; }""")
    page.evaluate("runMultiAICheck(0)"); page.wait_for_timeout(1500)
    p2 = bodies[-1]
    if '(90g)' not in p2: f.add('BUG', 'a stated amount was not sent')
    if 'exactly this food and amount' not in p2: f.add('BUG', 'stated-amount wording missing')
    # 3) single guessed item: scaled averaging
    page.evaluate("""()=>{ window._pendingMealText='some clotted cream'; window._pendingMealFoods=[{name:'clotted cream',amount:'160g',kcal:300,protein:2,carbs:2,fat:30}]; }""")
    page.evaluate("runMultiAICheck(0)"); page.wait_for_timeout(1500)
    res = page.evaluate("(()=>{const r=window._multiAIResults; const k=Object.keys(r).pop(); const p=r[k].providers[0]; return {raw:p.parsed.kcal, cmp:p.cmp.kcal}})()")
    if res['raw'] != 400 or round(res['cmp']) != 800: f.add('BUG', f'scaling to logged amount wrong {res}')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
