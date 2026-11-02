"""Three-AI check: the calorie range in the agree/disagree note is whole numbers (v3.10.1256).
Found in a phone recording: it printed 95.83333333333334-315kcal when the checkers' portions were scaled to the logged amount.
Stubs the worker reply (no network), runs the real runMultiAICheck, reads the rendered note."""
import sys, re, json; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
src = open('maxhealth.html', encoding='utf-8').read()
if re.search(r'\$\{minK\}\s*-\s*\$\{maxK\}', src): f.add('BUG', 'source still prints unrounded ${minK}-${maxK}')
def reply(rows):
    return {k: {'ok': True, 'text': 'KCAL: %s\nPROTEIN: %s\nFAT: %s\nCARBS: %s\nPORTION_G: %s\nPORTION_KCAL: %s' % r} for k, r in zip(('claude', 'gemini', 'openai'), rows)}
CASES = {
  'disagree': [(230, 30, 10, 1, 140, 230), (310, 40, 15, 1, 170, 310), (500, 30, 30, 2, 110, 500)],
  'agree':    [(230, 30, 10, 1, 140, 230), (240, 31, 10, 1, 150, 240), (250, 32, 11, 1, 155, 250)],
}
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 430, 'height': 1000}, service_workers='block')
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    p = ctx.new_page(); p.on('pageerror', lambda e: errs.append(str(e)[:200])); ev = p.evaluate
    p.goto('http://localhost:5757/'); p.wait_for_timeout(1500); ev("startDemoMode('doris')"); p.wait_for_timeout(2500)
    ev("switchTab('log',document.getElementById('maintab-log'))"); p.wait_for_timeout(500)
    for name, rows in CASES.items():
        body = json.dumps(reply(rows))
        ev("(b)=>{window.fetch=async()=>({json:async()=>JSON.parse(b)})}", body)
        ev("()=>{window._pendingMealText='some roast beef';window._pendingMealFoods=[{name:'Roast beef',amount:'137g',kcal:200,protein:30,fat:8,carbs:0}]}")
        ev("runMultiAICheck(0)"); p.wait_for_timeout(900)
        txt = ev("()=>{const n=[...document.querySelectorAll('div')].filter(d=>/disagree by more than 25%|Reasonably consistent/.test(d.textContent)&&d.children.length===0);return n.length?n[n.length-1].textContent:null}")
        if not txt: f.add('BUG', name + ': no agreement note rendered'); continue
        m = re.search(r'\(([^)]*)kcal\)', txt)
        if not m: f.add('BUG', name + ': no range in note: ' + txt[:80]); continue
        if not re.fullmatch(r'\d+-\d+', m.group(1)): f.add('BUG', name + ': range not whole numbers: ' + m.group(1))
        want = 'disagree' if name == 'disagree' else 'Reasonably'
        if want not in txt: f.add('BUG', name + ': wrong note kind: ' + txt[:60])
        print('info', name, m.group(1))
    if errs: f.add('JS-exception', errs[0])
    b.close()
bad = any(s in ('BUG', 'JS-exception') for s, _ in f)
for s, m in f: print(s, m)
print('BUGS' if bad else 'OK', len(f)); sys.exit(1 if bad else 0)
