"""Persona 54: Today food log edit - type the new portion in grams as well as a percentage (single and multi-ingredient entries), and the crockery help tip."""
import sys, re, json; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:160]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200)
    page.evaluate("onboardNext(2)"); page.fill('#onboardName', 'Ola'); page.evaluate("onboardNext(3)")
    page.evaluate("obSetSex('male')"); page.fill('#onboardAge', '58'); page.fill('#onboardHeight', '176')
    page.fill('#onboardWeight', '82'); page.fill('#onboardTarget', '78')
    page.evaluate("onboardNext(4)"); page.evaluate("obSetActivity('light')"); page.evaluate("obSetGoal('lose')")
    page.evaluate("onboardNext(5)"); page.evaluate("obSetCondition('general')")
    page.evaluate("onboardNext(6)"); page.evaluate("onboardFinish()"); page.wait_for_timeout(1200)
    page.evaluate("""() => {
      state.todayLog = [
        { id: 9001, description: 'Chicken', amount: '200g', kcal: 330, protein: 62, fat: 7, carbs: 0, time: '12:00', items: [] },
        { id: 9002, description: 'Chicken and rice', amount: '1 serving', kcal: 500, protein: 40, fat: 10, carbs: 50, time: '13:00',
          items: [ { name: 'Chicken', amount: '100g', kcal: 165, protein: 31, fat: 3.5, carbs: 0 }, { name: 'Rice', amount: '100g', kcal: 335, protein: 9, fat: 6.5, carbs: 50 } ] },
        { id: 9003, description: 'Mixed', amount: '1 serving', kcal: 400, protein: 20, fat: 10, carbs: 40, time: '14:00',
          items: [ { name: 'Salad', amount: '1 bowl', kcal: 100, protein: 2, fat: 5, carbs: 10 }, { name: 'Bread', amount: '60g', kcal: 300, protein: 18, fat: 5, carbs: 30 } ] } ];
      saveState(); updateDashboard(); }""")
    page.evaluate("switchTabById('today')"); page.wait_for_timeout(500)
    # single-item entry: type 300g for a 200g entry -> 150%
    page.evaluate("editLogEntry(9001)"); page.wait_for_timeout(200)
    if not page.evaluate("!!document.getElementById('edit-grams-9001')"): f.add('BUG', 'no grams box on the single-entry edit form')
    else:
        page.fill('#edit-grams-9001', '300'); page.wait_for_timeout(150)
        pct = page.evaluate("parseFloat(document.getElementById('edit-pct-9001').value)")
        kc = page.evaluate("parseFloat(document.getElementById('edit-kcal-9001').value)")
        if abs(pct - 150) > 0.2 or abs(kc - 495) > 1: f.add('BUG', f'300g on a 200g entry should be 150% / 495 kcal, got {pct}% / {kc}')
        for txt in ('300g', '300 g', ' 300G '):   # v3.10.935: the box is text, so a unit typed after the number is accepted
            page.fill('#edit-grams-9001', ''); page.fill('#edit-grams-9001', txt); page.wait_for_timeout(150)
            if abs(page.evaluate("parseFloat(document.getElementById('edit-pct-9001').value)") - 150) > 0.2: f.add('BUG', f'typing "{txt}" was not accepted')
    page.evaluate("cancelLogEdit(9001)")
    # multi-item with grams everywhere: 200g -> 300g, every ingredient x1.5
    page.evaluate("editLogEntry(9002)"); page.wait_for_timeout(200)
    page.fill('#log-edit-scalegrams-9002', '300'); page.evaluate("scaleAllLogEditToGrams(9002)")
    tot = page.evaluate("window._logEditWorkingItems[9002].map(i=>[i.amount,i.kcal])")
    if tot != [['150g', 248], ['150g', 503]] and not (abs(tot[0][1] - 247.5) < 1 and tot[0][0] == '150g'): f.add('BUG', f'multi-item grams scaling wrong: {tot}')
    page.fill('#log-edit-scalegrams-9002', '300g'); page.evaluate("scaleAllLogEditToGrams(9002)")      # again (with a unit): must not compound
    tot2 = page.evaluate("window._logEditWorkingItems[9002].map(i=>i.amount)")
    if tot2 != ['150g', '150g']: f.add('BUG', f'applying twice compounded: {tot2}')
    if '200g' not in page.evaluate("document.getElementById('log-edit-nowgrams-9002').textContent"): f.add('BUG', 'original size not shown beside the grams box')
    page.evaluate("cancelLogEdit(9002)")
    # an ingredient with no gram size: refused, nothing changes
    page.evaluate("editLogEntry(9003)"); page.wait_for_timeout(200)
    page.fill('#log-edit-scalegrams-9003', '500'); page.evaluate("scaleAllLogEditToGrams(9003)")
    if page.evaluate("window._logEditWorkingItems[9003][1].kcal") != 300: f.add('BUG', 'grams scaling changed values even though one ingredient has no gram size')
    page.evaluate("cancelLogEdit(9003)")
    # crockery help tip explains what matters for accuracy
    page.evaluate("switchTabById('manage'); mhTwRender()"); page.wait_for_timeout(300)
    tip = page.evaluate("(document.getElementById('help-tableware')?.textContent || document.querySelector('#mhTwCard .help-slot')?.getAttribute('data-text') || '')")
    for word in ('food area', 'ml you measure', 'same height as the plate rim', 'weigh'):
        if word not in tip: f.add('BUG', f'help tip missing guidance: {word}')
    if errs: f.add('BUG', f'page errors: {errs[:3]}')
    b.close()
print('findings', len(f)); sys.exit(1 if f else 0)
