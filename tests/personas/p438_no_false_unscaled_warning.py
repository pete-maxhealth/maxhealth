"""Persona 438: the "protein may not be scaled / look like per-100g" warning and its Apply never fire on figures that are right (v3.10.1336).
Pete (9 Nov 2026): whey straight from the barcode (80g protein per 100g) at 25g = 101kcal, 20g P was flagged as unscaled and Apply would have made it 25kcal, 5g P.
Trusted figures (barcode, label, library, per-100g base) are never second-guessed, protein powders are not flagged by name, and a genuinely unscaled AI chicken still is. Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); ev = page.evaluate
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200)
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay').style.display='none'")
    ev("switchTab('log', document.getElementById('maintab-log')); switchSubTab('log','log', document.getElementById('logtab-log'))"); page.wait_for_timeout(500)
    WHEY = "name:'Zzqx Diet Whey Protein', amount:'25g', kcal:101, protein:20, fat:1.9, carbs:1"
    def show(foods):
        ev(f"window._pendingMealFoods={foods}; renderMealPreview()"); page.wait_for_timeout(350)
        return ev("[(document.getElementById('mealPreviewBubble')||{innerText:''}).innerText, !!document.querySelector('#previewFixes')]")
    cases = [('barcode base', "[{%s, _per100gBase:{kcal:402,protein:80,fat:7.4,carbs:3.9,per:100}, _base:{kcal:402,protein:80,fat:7.4,carbs:3.9,baseG:100}}]" % WHEY),
             ('library source', "[{%s, _source:'library'}]" % WHEY),
             ('per100g flag', "[{%s, _per100g:true}]" % WHEY),
             ('manual pick', "[{%s, _source:'manual'}]" % WHEY),
             ('AI, protein powder name', "[{%s, _source:'ai'}]" % WHEY)]
    for name, foods in cases:
        t, fix = show(foods)
        if 'look like per-100g' in t or fix: f.add('BUG', f'{name}: correct whey figures were flagged as unscaled (Apply offered: {fix})')
    # still catches a genuinely unscaled AI food
    t, fix = show("[{name:'Zzqx Chicken breast', amount:'40g', kcal:165, protein:31, fat:3.6, carbs:0, _source:'ai'}]")
    if 'look like per-100g' not in t or not fix: f.add('BUG', 'an unscaled AI chicken at 40g is still flagged with a suggestion')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f]; sys.exit(1 if f else 0)
