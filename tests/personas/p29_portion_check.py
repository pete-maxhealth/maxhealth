"""Persona 29: the 3-AI check asks each AI for its OWN portion estimate and flags portion disagreement;
Browse saved prompts is centred."""
import sys, re, json; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    bodies = []
    def route(r):
        u = r.request.url
        if 'workers.dev' in u:
            bodies.append(r.request.post_data or '')
            t = lambda g: f"KCAL: 600\nPROTEIN: 30g\nFAT: 30g\nCARBS: 50g\nPORTION_G: {g}\nPORTION_KCAL: {g*2}"
            r.fulfill(status=200, content_type='application/json', headers={'access-control-allow-origin': '*'},
                      body=json.dumps({'claude': {'ok': True, 'text': t(300)}, 'gemini': {'ok': True, 'text': t(450)}, 'openai': {'ok': True, 'text': t(620)}}))
        elif u.startswith('http://localhost'): r.continue_()
        else: r.fulfill(status=200, body='')
    ctx.route(re.compile(r'^https?://'), route)
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:160]))
    page.goto('http://localhost:5757/', wait_until='domcontentloaded'); page.wait_for_timeout(800)
    r = page.evaluate("""async()=>{
      window._pendingMealText='big bowl of beef stew';
      window._pendingMealFoods=[{name:'Beef stew',amount:'300g',kcal:600,protein:30,fat:30,carbs:50}];
      const d=document.createElement('div');d.id='chatScroll2';document.body.appendChild(d);
      const o=await estimateNutritionViaTripleAI('Beef stew (300g)');
      const c=document.createElement('div');document.body.appendChild(c);
      renderTripleAICompare(c,'Beef stew (300g)',o.providers,o.agreementNote);
      return c.innerText;}""")
    if 'PORTION_G' not in (bodies[0] if bodies else ''): f.add('BUG', 'prompt does not ask for an independent portion')
    if 'Portion size is the shaky part' not in r: f.add('BUG', 'portion disagreement not flagged: ' + r[:200])
    if '~450g' not in r: f.add('BUG', 'per-provider portion not shown')
    # whole multi-item meal through runMultiAICheck: portions shown per AI, compared against the SUM of stated weights
    page.evaluate("window._pendingMealFoods=[{name:'omelette',amount:'200g',kcal:500,protein:30,fat:40,carbs:3},{name:'poached egg',amount:'100g',kcal:150,protein:12,fat:10,carbs:1},{name:'halloumi',amount:'80g',kcal:260,protein:18,fat:20,carbs:1},{name:'mushrooms',amount:'100g',kcal:90,protein:3,fat:7,carbs:3}]; runMultiAICheck()"); page.wait_for_timeout(1200)
    bub = page.evaluate("[...document.querySelectorAll('.chat-bubble')].map(b=>b.innerText).join('\\n')")
    if 'its own portion guess' not in bub: f.add('BUG', 'portion not shown per AI in whole-meal check: ' + bub[-300:])
    if 'the logged amount is 480g' not in bub: f.add('BUG', 'whole meal not compared to 480g total: ' + bub[-300:])
    page.evaluate("document.body.insertAdjacentHTML('beforeend','<div id=sp></div>');renderSavedPromptPills('sp','quickPrompt')")
    box = page.evaluate("(()=>{const e=document.querySelector('#sp .quick-btn').getBoundingClientRect();const p=document.getElementById('sp').getBoundingClientRect();return [e.left-p.left,p.right-e.right]})()")
    if abs(box[0]-box[1]) > 2: f.add('BUG', f'Browse saved prompts not centred {box}')
    if errs: f.add('JS-exception', str(errs[:3]))
    b.close()
print('findings', len(f)); sys.exit(1 if f else 0)
