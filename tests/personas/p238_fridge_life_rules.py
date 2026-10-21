"""Persona 238: fridge life rules you type yourself (v3.10.1131). Pete: cheese keeps much longer than the blanket 3 days. None are built in; words in a food's name plus days;
a food's own length wins; dates the app worked out move by the difference (bought date kept), a date you typed does not; deleting a rule puts it back; bad input is refused. Invented data only."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()"); ev("mhShopOpen()")
    ev("""()=>{ ['Seriously Strong Cheddar','Whole Milk','Mild Cheese Slices','Typed Date Cheese'].forEach(n=>{ mhStockTrack(n,{base:'g',pack:400,shop:'Asda'}); mhStockSetLevel(mhShopKey(n),400); mhStockSetStore(mhShopKey(n),'fridge'); });
      mhStockSetStore(mhShopKey('Mild Cheese Slices'),'fridge',5); mhStockSetUseBy && mhStockSetUseBy(mhShopKey('Typed Date Cheese'),'2030-01-02'); }""")
    life = lambda n: ev("n=>mhItemLife(mhStockLoad().items[mhShopKey(n)])", n)
    ub = lambda n: ev("n=>mhStockLoad().items[mhShopKey(n)].useBy", n)
    days = lambda n: ev("n=>Math.round((new Date(mhStockLoad().items[mhShopKey(n)].useBy+'T12:00:00')-new Date(mhISO()+'T12:00:00'))/86400000)", n)
    if ev("mhRulesLoad().lifeRules.length") != 0: f.add('BUG', '0: no rules are built in')
    if life('Seriously Strong Cheddar') != 3 or days('Seriously Strong Cheddar') != 3: f.add('BUG', f'1: before any rule it is the plain 3 days: {life("Seriously Strong Cheddar")} {days("Seriously Strong Cheddar")}')
    ev("mhShopView('list'); mhShopRender()")
    ev("mhRulesLifeEdit(r=>{ r.lifeRules=[{words:['cheese','cheddar'],days:28}]; })")
    if life('Seriously Strong Cheddar') != 28: f.add('BUG', f'2: cheddar uses the rule: {life("Seriously Strong Cheddar")}')
    if life('Whole Milk') != 3: f.add('BUG', f'3: milk is untouched: {life("Whole Milk")}')
    if life('Mild Cheese Slices') != 5: f.add('BUG', f'4: a food\'s own length wins over a rule: {life("Mild Cheese Slices")}')
    if days('Seriously Strong Cheddar') != 28 or days('Whole Milk') != 3: f.add('BUG', f'5: the auto date moved to 28 days, milk stayed: {days("Seriously Strong Cheddar")} {days("Whole Milk")}')
    if ub('Typed Date Cheese') != '2030-01-02': f.add('BUG', f'6: a date typed by hand is never moved: {ub("Typed Date Cheese")}')
    ev("mhRulesLifeEdit(r=>{ r.lifeRules=[]; })")
    if days('Seriously Strong Cheddar') != 3: f.add('BUG', f'7: removing the rule puts the date back: {days("Seriously Strong Cheddar")}')
    # the settings form
    ev("mhShopView('list')"); ev("mhShopRender()")
    ev("_shopUi.rulesOpen=true; mhShopRender()")
    if ev("!!document.getElementById('mhLifeWords')"):
        ev("document.getElementById('mhLifeWords').value='cheese, cheddar'; document.getElementById('mhLifeDays').value='0'; mhRulesLifeAdd()")
        if ev("mhRulesLoad().lifeRules.length") != 0: f.add('BUG', '8: 0 days refused')
        ev("document.getElementById('mhLifeWords').value=''; document.getElementById('mhLifeDays').value='20'; mhRulesLifeAdd()")
        if ev("mhRulesLoad().lifeRules.length") != 0: f.add('BUG', '9: empty words refused')
        ev("document.getElementById('mhLifeWords').value='Cheese, Cheddar'; document.getElementById('mhLifeDays').value='28'; mhRulesLifeAdd()")
        r = ev("mhRulesLoad().lifeRules")
        if r != [{'words': ['cheese', 'cheddar'], 'days': 28}]: f.add('BUG', f'10: the form adds a rule: {r}')
        if days('Seriously Strong Cheddar') != 28: f.add('BUG', '11: the form rule moves the date')
    else: f.add('BUG', '8: the Fridge life by type of food form is on the Stock rules screen')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
