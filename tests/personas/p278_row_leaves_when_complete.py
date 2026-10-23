"""Persona 278: Needs details has no ticking or pop-up; each food picks Cupboards / Shopping list / Both on its own row, and leaves the list when complete and chosen (v3.10.1174). Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("""(()=>{['Zzqx Alpha','Zzqx Beta','Zzqx Gamma'].forEach(n=>mhStockTrack(n,{base:'g',shop:'Asda'}));})()""")
    ev("switchTabById('shop')"); ev("mhSlOpen()"); page.wait_for_timeout(400)
    ev("mhSlF('gaps')"); page.wait_for_timeout(300)
    rows = "document.querySelectorAll('#mhSlRows [data-sl]').length"
    if ev(rows) != 3: f.add('BUG', f'three foods need details: {ev(rows)}')
    if ev("document.querySelectorAll('#mhSlRows [data-pick]').length"): f.add('BUG', 'no tick boxes in Needs details')
    if page.locator('button:has-text("Tick all shown")').count(): f.add('BUG', 'no Tick all shown in Needs details')
    if ev("getComputedStyle(document.getElementById('mhSlBulk')).display") != 'none': f.add('BUG', 'no pop-up bar in Needs details')
    if ev("document.querySelectorAll('#mhSlRows [data-dest]').length") != 9: f.add('BUG', 'every row asks where it goes (3 buttons x 3)')
    k = ev("mhShopKey('Zzqx Alpha')"); sel = '[data-sl="%s"]' % k
    # fill every amount first: it must NOT leave until a destination is chosen
    for fld, val in (('amt', '300'), ('thr', '100'), ('serv', '50')):
        page.fill(sel + ' [data-f="%s"]' % fld, val); page.dispatch_event(sel + ' [data-f="%s"]' % fld, 'change'); page.wait_for_timeout(250)
    page.wait_for_timeout(1000)
    if not ev("!!document.querySelector('%s')" % sel): f.add('BUG', 'a food stays until you say where it goes')
    if 'choose one' not in page.inner_text(sel + ' [data-destreq]'): f.add('BUG', 'the row says a choice is still needed')
    page.click(sel + ' [data-dest="both"]'); page.wait_for_timeout(1300)
    if ev("!!document.querySelector('%s')" % sel): f.add('BUG', 'complete and chosen: the food leaves the list')
    if not ev("mhShopLoad().items.some(i=>i.name==='Zzqx Alpha')"): f.add('BUG', 'Both puts it on the shopping list')
    if ev("mhStockLoad().items[%r].level" % k) != 300: f.add('BUG', 'and it keeps its amounts in the cupboards')
    if ev(rows) != 2 or '2 shown' not in page.inner_text('#mhSlShownN'): f.add('BUG', 'the shown count updates')
    # choosing for one food touches only that food
    k2 = ev("mhShopKey('Zzqx Beta')")
    page.click('[data-sl="%s"] [data-dest="list"]' % k2); page.wait_for_timeout(400)
    names = sorted(ev("mhShopLoad().items.map(i=>i.name)"))
    if names != ['Zzqx Alpha', 'Zzqx Beta']: f.add('BUG', f'Shopping list puts only that food on the list: {names}')
    if not ev("!!document.querySelector('[data-sl=\"%s\"]')" % ev("mhShopKey('Zzqx Gamma')")): f.add('BUG', 'the other food is untouched')
    # other lists still tick, with a slim bar that names the food
    ev("mhSlF('all')"); page.wait_for_timeout(300)
    page.click('[data-sl] [data-pick] >> nth=0'); page.wait_for_timeout(300)
    nm = page.inner_text('#mhSlTickNames')
    if not nm.startswith('Zzqx'): f.add('BUG', f'the bar says which food is ticked: {nm!r}')
    hh = ev("document.getElementById('mhSlBulk').offsetHeight")
    if hh > 150: f.add('BUG', f'the bar stays small: {hh}px')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
