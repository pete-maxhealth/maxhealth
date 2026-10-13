"""Persona 125: in demo mode no request ever reaches an AI provider or the shared proxy (labelled sample answers instead); outside demo mode fetch is untouched; the Premium preview opens from the demo banner."""
import sys; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
HOSTS = ['https://maxhealth-ai.bogginsuk.workers.dev', 'https://api.anthropic.com/v1/messages', 'https://api.openai.com/v1/chat/completions', 'https://generativelanguage.googleapis.com/v1beta/models/x:generateContent']
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []; hits = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.route('**/*', lambda r: (hits.append(r.request.url), r.abort()) if any(h.split('/')[2] in r.request.url for h in HOSTS) else r.continue_())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev = page.evaluate
    # outside demo: the request really goes out (and our route aborts it)
    r = ev("fetch('https://maxhealth-ai.bogginsuk.workers.dev',{method:'POST',body:'{}'}).then(()=>'ok').catch(()=>'blocked')")
    if r != 'blocked' or not hits: f.add('BUG', f'outside demo the request was not left alone: {r} {hits}')
    hits.clear()
    ev("startDemoMode(DEMO_PERSONAS[0].id)"); page.wait_for_timeout(2000)
    for h in HOSTS:
        t = ev(f"fetch('{h}',{{method:'POST',body:'x'}}).then(r=>r.json()).then(j=>JSON.stringify(j))")
        if 'Sample answer' not in t: f.add('BUG', f'no labelled sample for {h}: {t[:120]}')
    mc = ev("fetch(HOSTS0,{method:'POST',body:JSON.stringify({multiCheck:true,prompt:'x'})}).then(r=>r.json())".replace('HOSTS0', repr(HOSTS[0])))
    if not (mc.get('claude') and mc['claude'].get('ok') and 'KCAL' in mc['claude']['text']): f.add('BUG', f'multiCheck shape wrong {mc}')
    meal = ev("fetch('https://maxhealth-ai.bogginsuk.workers.dev',{method:'POST',body:'You are a precise nutrition assistant'}).then(r=>r.json()).then(j=>JSON.parse(j.content[0].text))")
    if not meal.get('items') or 'Sample' not in meal.get('message', ''): f.add('BUG', f'meal sample shape wrong {meal}')
    rec = ev("fetch('https://api.anthropic.com/v1/messages',{method:'POST',body:'You are a recipe assistant'}).then(r=>r.json()).then(j=>JSON.parse(j.content[0].text))")
    if not rec.get('ingredients') or not rec.get('method'): f.add('BUG', f'recipe sample shape wrong {rec}')
    if hits: f.add('BUG', f'demo mode let real AI requests out: {hits}')
    # premium preview
    ev("mhPremiumPreview()"); page.wait_for_timeout(400)
    t = ev("(document.getElementById('mhPremiumPrev')||{}).textContent||''")
    if 'wearable' not in t.lower() or 'Register interest' not in t: f.add('BUG', 'premium preview missing content')
    if ev("document.querySelector('#mhPremiumPrev a').href") != 'https://pspence.co.uk/maxedhealth/': f.add('BUG', 'premium link wrong')
    ev("document.getElementById('mhPremiumPrev').remove(); exitDemoMode()"); page.wait_for_timeout(1500)
    hits.clear()
    r = ev("fetch('https://api.openai.com/v1/chat/completions',{method:'POST',body:'{}'}).then(()=>'ok').catch(()=>'blocked')")
    if r != 'blocked': f.add('BUG', 'after exiting demo, AI requests are still being faked')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
