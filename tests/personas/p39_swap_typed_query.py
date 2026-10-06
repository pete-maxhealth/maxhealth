"""Persona 39: swapping a suggested item - what you typed in the picker (beef bacon) is what online search / Try AI start from, not the old item's name."""
import sys, re, json; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    def route(r):
        u = r.request.url
        if u.startswith('http://localhost'): return r.continue_()
        if 'openfoodfacts' in u:
            return r.fulfill(status=200, content_type='application/json', headers={'access-control-allow-origin': '*'}, body=json.dumps({'status': 0}))
        r.abort()
    ctx.route(re.compile(r'^https?://'), route)
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:160])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200)
    page.evaluate("onboardNext(2)"); page.fill('#onboardName', 'Ola'); page.evaluate("onboardNext(3)")
    page.evaluate("obSetSex('male')"); page.fill('#onboardAge', '58'); page.fill('#onboardHeight', '176')
    page.fill('#onboardWeight', '82'); page.fill('#onboardTarget', '78')
    page.evaluate("onboardNext(4)"); page.evaluate("obSetActivity('light')"); page.evaluate("obSetGoal('lose')")
    page.evaluate("onboardNext(5)"); page.evaluate("obSetCondition('general')")
    page.evaluate("onboardNext(6)"); page.evaluate("onboardFinish()"); page.wait_for_timeout(1500)
    page.evaluate("switchTabById('log')"); page.wait_for_timeout(300)
    page.evaluate("""window._pendingLibraryCombos=[{type:'items',items:[{name:'Asda Beef Burgers',amount:114,kcal:289,protein:21.7,fat:20.5,carbs:3.8,fibre:0,polyols:0,_base:{kcal:253,protein:19,fat:18,carbs:3.3,fibre:0,polyols:0,baseG:100}}],note:'x',anyMissing:false}]; substituteComboItem(0,0)""")
    page.wait_for_timeout(300)
    start = page.evaluate("document.getElementById('recipeLibSearch').value")
    if start != 'Asda Beef Burgers': f.add('BUG', f'picker did not start from the old name: {start}')
    page.evaluate("document.getElementById('recipeLibSearch').value='beef bacon'; filterRecipeLibPicker('beef bacon'); _libPickerSearchOnline()")
    page.wait_for_timeout(500)
    v = page.evaluate("document.getElementById('foodSearchInput').value")
    if v != 'beef bacon': f.add('BUG', f'online search started from {v!r}, not what was typed')
    page.evaluate("closeFoodSearch(); substituteComboItem(0,0)"); page.wait_for_timeout(200)
    page.evaluate("document.getElementById('recipeLibSearch').value=''; _libPickerSearchOnline()"); page.wait_for_timeout(400)
    v = page.evaluate("document.getElementById('foodSearchInput').value")
    if v != 'Asda Beef Burgers': f.add('BUG', f'with nothing typed, expected old name, got {v!r}')
    if errs: f.add('JS-exception', str(errs[:3]))
    b.close()
print('findings', len(f)); sys.exit(1 if f else 0)
