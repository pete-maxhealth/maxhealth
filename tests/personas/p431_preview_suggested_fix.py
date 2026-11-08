"""Persona 431: when the meal preview flags something and the app knows what the right figures would be, it says so and offers an Apply (Pete 8 Nov: "if you know what's wrong, you should know what's right"). Nothing changes until Apply; Apply changes only what was named."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay').style.display='none'"); ev("switchTabById('log')"); page.wait_for_timeout(400)
    txt = lambda: ev("(document.getElementById('mealPreviewBubble')||{innerText:''}).innerText")
    # 1. cream with far too little fat for 100g
    ev("window._pendingMealFoods=[{name:'Double cream', amount:'100g', kcal:60, protein:2, fat:5, carbs:3, _source:'ai'}]; renderMealPreview()"); page.wait_for_timeout(300)
    t = txt()
    if 'expect roughly 50g' not in t or 'kcal becomes' not in t: f.add('BUG', 'says what it expects: ' + t[:500])
    if not ev("!!document.querySelector('#previewFixes button')"): f.add('BUG', 'an Apply button is offered')
    if 'If you agree, tap Apply' not in t: f.add('BUG', 'says that agreeing means tapping Apply')
    if ev("window._pendingMealFoods[0].fat") != 5: f.add('BUG', 'nothing changes before Apply')
    ev("document.querySelector('#previewFixes button').click()"); page.wait_for_timeout(300)
    r = ev("(({fat,protein,carbs,kcal,amount})=>({fat,protein,carbs,kcal,amount}))(window._pendingMealFoods[0])")
    if r != {'fat': 50, 'protein': 2, 'carbs': 3, 'kcal': 470, 'amount': '100g'}: f.add('BUG', f'Apply sets fat 50 and kcal 470 and nothing else: {r}')
    if ev("!!document.querySelector('#previewFixes')"): f.add('BUG', 'the suggestion goes once applied')
    # 2. per-100g figures for a 40g amount
    ev("window._pendingMealFoods=[{name:'Chicken breast', amount:'40g', kcal:165, protein:31, fat:3.6, carbs:0, _source:'ai'}]; renderMealPreview()"); page.wait_for_timeout(300)
    t = txt()
    if 'per-100g' not in t or '12.4g P' not in t: f.add('BUG', 'names the 40g figures: ' + t[:500])
    ev("document.querySelector('#previewFixes button').click()"); page.wait_for_timeout(300)
    r = ev("(({protein,fat,kcal,amount})=>({protein,fat,kcal,amount}))(window._pendingMealFoods[0])")
    if r != {'protein': 12.4, 'fat': 1.4, 'kcal': 66, 'amount': '40g'}: f.add('BUG', f'Apply scales to 40g: {r}')
    # 3. nothing known to be wrong: no suggestion box
    ev("window._pendingMealFoods=[{name:'Eggs', amount:'150g', kcal:215, protein:19, fat:15, carbs:1, _source:'ai'}]; renderMealPreview()"); page.wait_for_timeout(300)
    if ev("!!document.querySelector('#previewFixes')"): f.add('BUG', 'no suggestion box when nothing is flagged')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
