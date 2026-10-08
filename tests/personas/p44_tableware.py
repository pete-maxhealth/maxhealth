"""Persona 44: tableware sets - Home defaults, overrides + back-to-default arrows, sets inherit from Home, in-use chip, date revert, and the AI prompt carrying the active set."""
import sys, re, json; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
FOOD = {"type": "food", "items": [{"name": "porridge", "amount": "250g", "kcal": 300, "protein": 10, "fat": 5, "carbs": 50}], "message": "ok"}
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []; bodies = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    def stub(route):
        bodies.append(route.request.post_data or '')
        route.fulfill(status=200, content_type='application/json', body=json.dumps({"content": [{"type": "text", "text": json.dumps(FOOD)}], "usage": {"input_tokens": 1, "output_tokens": 1}}))
    ctx.route(re.compile(r'https://(cdn\.jsdelivr\.net|cdnjs\.cloudflare\.com|fonts\.(googleapis|gstatic)\.com)/.*'), lambda r: r.abort())
    ctx.route('https://api.anthropic.com/**', stub)
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:160])); ans = ['Holiday']; page.on('dialog', lambda d: d.accept(ans[0]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200)
    page.evaluate("onboardNext(2)"); page.fill('#onboardName', 'Ola'); page.evaluate("onboardNext(3)")
    page.evaluate("obSetSex('male')"); page.fill('#onboardAge', '58'); page.fill('#onboardHeight', '176')
    page.fill('#onboardWeight', '82'); page.fill('#onboardTarget', '78')
    page.evaluate("onboardNext(4)"); page.evaluate("obSetActivity('light')"); page.evaluate("obSetGoal('lose')")
    page.evaluate("onboardNext(5)"); page.evaluate("obSetCondition('general')")
    page.evaluate("onboardNext(6)"); page.evaluate("onboardFinish()"); page.wait_for_timeout(1500)
    page.evaluate("localStorage.setItem('mh_provider','claude');localStorage.setItem('mh_apikey','sk-ant-test-key-123')")
    page.reload(); page.wait_for_timeout(1500)
    page.evaluate("switchTabById('manage')"); page.wait_for_timeout(500)
    page.evaluate("mhTwRender()")
    inputs = lambda: page.evaluate("document.querySelectorAll('#mhTwCard input[type=number]').length")
    if inputs() != 26: f.add('BUG', f'expected 8 items x 3 fields + 2 plate food areas = 26 inputs, got {inputs()}')
    val = lambda it, fl: page.evaluate("(a)=>{const s=JSON.parse(localStorage.getItem('mh_tableware')||'null');return s}", None)
    arrows = lambda: page.evaluate("[...document.querySelectorAll('#mhTwCard span')].filter(x=>x.textContent==='↺').length")
    if arrows() != 0: f.add('BUG', 'back-to-default arrows shown with nothing changed')
    line = page.evaluate("mhTablewareLine()")
    if '27cm across (typical size, not measured)' not in line: f.add('BUG', 'Home default not marked typical in AI line: ' + line[:300])
    if 'empty weight' in line: f.add('BUG', 'an empty weight was guessed by default')
    if 'set "Home"' not in line: f.add('BUG', 'set name missing from AI line')
    # edit Home: plate 28 -> arrow appears, line now says measured (no typical tag on that field)
    page.evaluate("mhTwEdit('home','dinner_plate','diam','28')")
    if arrows() != 1: f.add('BUG', f'expected 1 back-to-default arrow after editing Home, got {arrows()}')
    line = page.evaluate("mhTablewareLine()")
    if '28cm across' not in line or '28cm across (typical' in line: f.add('BUG', 'edited Home value not used / still tagged typical: ' + line[:200])
    page.evaluate("mhTwReset('home','dinner_plate','diam')")
    if '27cm across' not in page.evaluate("mhTablewareLine()"): f.add('BUG', 'back to default did not restore 27')
    # new set inherits Home, stores only differences
    page.evaluate("mhTwAddSet()"); page.wait_for_timeout(300)
    st = page.evaluate("JSON.parse(localStorage.getItem('mh_tableware'))")
    hol = [x for x in st['sets'] if x['name'] == 'Holiday']
    if not hol: f.add('BUG', 'Holiday set not created'); hid = None
    else:
        hid = hol[0]['id']
        if hol[0]['vals'] != {}: f.add('BUG', 'new set copied values instead of inheriting')
        page.evaluate(f"mhTwEdit('{hid}','dinner_plate','diam','24')")
        page.evaluate("mhTwEdit('home','bowl','cap','400')")
        page.evaluate(f"mhTwUse('{hid}')"); page.wait_for_timeout(300)
        line = page.evaluate("mhTablewareLine()")
        if 'set "Holiday"' not in line or '24cm across' not in line: f.add('BUG', 'Holiday override not in AI line: ' + line[:300])
        if '400ml' not in line: f.add('BUG', 'Holiday did not inherit the Home bowl change: ' + line[:300])
        chip = page.evaluate("(()=>{const c=document.getElementById('mhTwChip');return [c.style.display, c.textContent]})()")
        if chip[0] == 'none' or 'Holiday' not in chip[1]: f.add('BUG', f'in-use chip not shown for non-Home set: {chip}')
        page.evaluate(f"mhTwView('{hid}')")
        if arrows() != 1: f.add('BUG', f'Holiday should show 1 arrow (the plate), got {arrows()}')
        page.evaluate(f"mhTwReset('{hid}','dinner_plate','diam')")
        if '27cm across' not in page.evaluate("mhTablewareLine()"): f.add('BUG', 'Holiday reset did not follow Home')
        # AI request carries the set
        page.click("[onclick^=\"switchTab('log'\"]"); page.wait_for_timeout(500)
        page.fill('#chatInput', 'bowl of porridge'); page.click("[onclick=\"sendChat()\"]"); page.wait_for_timeout(2500)
        if not any('KNOWN TABLEWARE' in x and 'Holiday' in x for x in bodies): f.add('BUG', 'meal request to the AI did not carry the tableware set')
        mc = page.evaluate("mhMultiCheckPrompt('porridge 250g', null)")
        if 'KNOWN TABLEWARE' not in mc: f.add('BUG', 'compare-AI prompt missing tableware')
        # revert date in the past -> back to Home
        page.evaluate("(()=>{const s=JSON.parse(localStorage.getItem('mh_tableware'));s.revertOn='2020-01-01';localStorage.setItem('mh_tableware',JSON.stringify(s));})()")
        page.evaluate("window.dispatchEvent(new Event('focus'))"); page.wait_for_timeout(500)
        st = page.evaluate("JSON.parse(localStorage.getItem('mh_tableware'))")
        if st['activeId'] != 'home' or st['revertOn'] is not None: f.add('BUG', f'did not go back to Home on the date: {st["activeId"]}')
        if page.evaluate("document.getElementById('mhTwChip').style.display") != 'none': f.add('BUG', 'chip still showing after revert')
        # delete set
        page.evaluate(f"mhTwDeleteSet('{hid}')")
        if any(x['id'] == hid for x in page.evaluate("JSON.parse(localStorage.getItem('mh_tableware')).sets")): f.add('BUG', 'set not deleted')
    # custom item + weight line
    page.evaluate("document.getElementById('mhTwNewName') && (document.getElementById('mhTwNewName').value='Soup bowl')")
    page.evaluate("switchTabById('manage'); mhTwRender(); document.getElementById('mhTwNewName').value='Soup bowl'; mhTwAddItem()")
    page.evaluate("(()=>{const s=JSON.parse(localStorage.getItem('mh_tableware'));const id=s.custom[0].id;mhTwEdit('home',id,'wt','350');})()")
    if 'soup bowl empty weight 350g' not in page.evaluate("mhTablewareLine()"): f.add('BUG', 'custom item / empty weight missing: ' + page.evaluate("mhTablewareLine()")[:400])
    # v3.10.908 copy as new: starts from the source's sizes, needs a different name, other sets get the copied sizes, Home is untouched
    page.evaluate("mhTwEdit('home','dinner_plate','diam','29.1')")
    ans[0] = 'Dinner plate'; n0 = page.evaluate("JSON.parse(localStorage.getItem('mh_tableware')).custom.length")
    page.evaluate("mhTwCopy('dinner_plate')")
    if page.evaluate("JSON.parse(localStorage.getItem('mh_tableware')).custom.length") != n0: f.add('BUG', 'copy accepted a name already used')
    ans[0] = ''
    page.evaluate("mhTwCopy('dinner_plate')")
    if page.evaluate("JSON.parse(localStorage.getItem('mh_tableware')).custom.length") != n0: f.add('BUG', 'copy accepted an empty name')
    ans[0] = 'Large plate'
    page.evaluate("mhTwCopy('dinner_plate')")
    cp = page.evaluate("JSON.parse(localStorage.getItem('mh_tableware')).custom.find(c=>c.name==='Large plate')")
    if not cp or cp.get('diam') != 29.1: f.add('BUG', f'copy should start from the source as Home shows it (29.1): {cp}')
    line = page.evaluate("mhTablewareLine()")
    if 'large plate 29.1cm across' not in line.lower(): f.add('BUG', 'copy not in the AI line at the copied size: ' + line[-300:])
    if page.evaluate("document.querySelectorAll('#mhTwCard [onclick^=\"mhTwCopy\"]').length") < 9: f.add('BUG', 'every item should offer copy as new')
    # copy a spoon: keeps the level-spoon wording
    ans[0] = 'Serving spoon'; page.evaluate("mhTwCopy('tablespoon')")
    if 'serving spoon level spoon 15ml' not in page.evaluate("mhTablewareLine()").lower(): f.add('BUG', 'copied spoon lost its spoon wording')
    # in another set the copy carries that set's sizes
    ans[0] = 'Resort'; page.evaluate("mhTwAddSet()")
    sid = page.evaluate("JSON.parse(localStorage.getItem('mh_tableware')).sets.find(x=>x.name==='Resort').id")
    page.evaluate(f"mhTwEdit('{sid}','side_plate','diam','21'); mhTwView('{sid}')")
    ans[0] = 'Resort small'; page.evaluate("mhTwCopy('side_plate')")
    st = page.evaluate("JSON.parse(localStorage.getItem('mh_tableware'))")
    rs = [c for c in st['custom'] if c['name'] == 'Resort small'][0]
    resort = [x for x in st['sets'] if x['id'] == sid][0]
    if rs['diam'] != 19 or resort['vals'].get(rs['id'], {}).get('diam') != 21: f.add('BUG', f'copy in another set: base {rs["diam"]}, set value {resort["vals"].get(rs["id"])}')
    page.evaluate("mhTwView('home')")
    # v3.10.909 food area: only plates carry it, it is optional, and a copy of a plate keeps the field and the value
    if page.evaluate("[mhTwHasFood('dinner_plate'), mhTwHasFood('side_plate'), mhTwHasFood('bowl'), mhTwHasFood('mug')]") != [True, True, False, False]: f.add('BUG', 'food area should be on plates only')
    page.evaluate("mhTwEdit('home','dinner_plate','food','19.5')")
    if 'dinner plate 29.1cm across, food area (inside the rim) about 19.5cm across' not in page.evaluate("mhTablewareLine()").lower(): f.add('BUG', 'food area missing from the AI line: ' + page.evaluate("mhTablewareLine()")[:300])
    ans[0] = 'Big plate 2'; page.evaluate("mhTwCopy('dinner_plate')")
    c2 = page.evaluate("JSON.parse(localStorage.getItem('mh_tableware')).custom.find(c=>c.name==='Big plate 2')")
    if not c2 or c2.get('food') != 19.5 or not page.evaluate("mhTwHasFood(JSON.parse(localStorage.getItem('mh_tableware')).custom.find(c=>c.name==='Big plate 2').id)"): f.add('BUG', f'copy of a plate lost its food area: {c2}')
    ans[0] = 'Bowl 2'; page.evaluate("mhTwCopy('bowl')")
    if page.evaluate("mhTwHasFood(JSON.parse(localStorage.getItem('mh_tableware')).custom.find(c=>c.name==='Bowl 2').id)"): f.add('BUG', 'a copy of a bowl should not get a food area')
    # reorder + hide controls injected like every other settings card, and an existing saved order is kept
    page.evaluate("localStorage.setItem('mh_reorder_manage', JSON.stringify(['set-profile','set-aiprovider','set-water','set-stepsbaseline']))")
    page.reload(); page.wait_for_timeout(1500); page.evaluate("switchTabById('manage')"); page.wait_for_timeout(600)
    ctl = page.evaluate("document.querySelector('#title-set-tableware')?.innerText||''")
    if '▲' not in ctl and '▼' not in ctl and '👁' not in ctl: f.add('BUG', f'tableware card has no reorder/hide controls: {ctl!r}')
    od = page.evaluate("JSON.parse(localStorage.getItem('mh_reorder_manage')||'[]')")
    kept = [k for k in od if k in ('set-profile','set-aiprovider','set-water','set-stepsbaseline')]
    if kept != ['set-profile','set-aiprovider','set-water','set-stepsbaseline']: f.add('BUG', f'a new card disturbed the saved settings order: {kept}')
    if 'set-tableware' not in od: f.add('BUG', 'tableware missing from the order')
    page.evaluate("moveGenericSection('manage','set-tableware','up')")
    od2 = page.evaluate("JSON.parse(localStorage.getItem('mh_reorder_manage')||'[]')")
    if od2.index('set-tableware') >= od.index('set-tableware'): f.add('BUG', f'move up did not move tableware: {od} -> {od2}')
    if errs: f.add('JS-exception', str(errs[:3]))
    b.close()
print('findings', len(f)); sys.exit(1 if f else 0)
