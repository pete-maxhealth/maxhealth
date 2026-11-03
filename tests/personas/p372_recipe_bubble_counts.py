"""AI recipe card: count items read naturally (v3.10.1257).
Found in a phone screenshot (whiteboard photo -> recipe): "8 wholes vine tomatoes". Expect "8 vine tomatoes", cloves still "2 cloves garlic", grams unchanged."""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
R = "{title:'Test bake',servings:2,method:['Mix.'],ingredients:[{name:'vine tomatoes',amount:8,unit:'whole'},{name:'small carrot',amount:1,unit:'whole'},{name:'garlic',amount:2,unit:'clove'},{name:'garlic',amount:1,unit:'clove'},{name:'red onion',amount:100,unit:'g'},{name:'double cream',amount:100,unit:'ml'},{name:'salt',amount:1,unit:'pinch'},{name:'flour',amount:2,unit:'cup'}]}"
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 430, 'height': 1000}, service_workers='block')
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    p = ctx.new_page(); p.on('pageerror', lambda e: errs.append(str(e)[:200])); ev = p.evaluate
    p.goto('http://localhost:5757/'); p.wait_for_timeout(1500); ev("startDemoMode('doris')"); p.wait_for_timeout(2500)
    ev("switchTab('log',document.getElementById('maintab-log'))"); p.wait_for_timeout(500)
    ev("()=>addRecipeBubble(" + R + ")"); p.wait_for_timeout(400)
    items = ev("()=>{const u=[...document.querySelectorAll('#chatScroll ul')].pop();return [...u.querySelectorAll('li')].map(l=>l.textContent.trim())}")
    want = ['8 vine tomatoes', '1 small carrot', '2 cloves garlic', '1 clove garlic', '100g red onion', '100ml double cream', '1 pinch salt', '2 cups flour']
    for w, g in zip(want, items):
        if w != g: f.add('BUG', 'expected %r got %r' % (w, g))
    if len(items) != len(want): f.add('BUG', 'item count %d' % len(items))
    p.screenshot(path='/tmp/p372.png')
    print('info', items)
    if errs: f.add('JS-exception', errs[0])
    b.close()
bad = any(s in ('BUG', 'JS-exception') for s, _ in f)
for s, m in f: print(s, m)
print('BUGS' if bad else 'OK', len(f)); sys.exit(1 if bad else 0)
