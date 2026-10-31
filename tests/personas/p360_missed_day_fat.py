"""Persona 360 (v3.10.1250): the manual "Missed day" form has a Fat box. A typed figure is stored as typed (entry, day total, History after a reload); left blank it counts as 0 and nothing is invented;
a day that already has meals gets the fat added to its total; the form is empty again on reopening; the four boxes fit a phone without overflow. The bug-report hints say "copies" (not "GitHub")
when no public report page is configured. Invented data."""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 900}, service_workers='block', timezone_id='UTC')
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    p = ctx.new_page(); p.on('pageerror', lambda e: errs.append(str(e)[:200])); p.on('dialog', lambda d: d.accept()); ev = p.evaluate
    p.goto('http://localhost:5757/'); p.wait_for_timeout(1500); ev("state.onboarded=true; saveState()"); p.reload(); p.wait_for_timeout(2000)
    ev("""(()=>{const dmy=n=>{const d=new Date(); d.setDate(d.getDate()-n); return String(d.getDate()).padStart(2,'0')+'/'+String(d.getMonth()+1).padStart(2,'0')+'/'+String(d.getFullYear()).slice(2)}; window.__dmy=dmy;
      const L=[{id:8001,time:'08:00',description:'Zed oats',amount:'1 serving',kcal:380,protein:20,fat:10,carbs:8,fibre:1}];
      state.history=[{date:dmy(4),mode:'standard',notes:'Normal',log:L,totals:{kcal:380,protein:20,fat:10,carbs:8}}]; state.todayLog=[]; saveState();})()""")
    day = lambda n: ev("state.history.find(h=>h.date===__dmy(%d))" % n)
    def miss(n, k, pr, c, fat, note):
        ev("openMissedDayModal(__dmy(%d)); setMissedMode('manual')" % n)
        if fat is None and ev("document.getElementById('missedFat')") is None: f.add('BUG', '0: the Fat box exists'); return
        ev("document.getElementById('missedKcal').value=%r; document.getElementById('missedProtein').value=%r; document.getElementById('missedCarbs').value=%r; document.getElementById('missedFat').value=%r; document.getElementById('missedNotes').value=%r" % (k, pr, c, fat, note))
        if n == 2 and fat == '12.5':
            ev("switchTabById('log')"); p.wait_for_timeout(300)
            r = ev("(()=>{const m=document.getElementById('missedDayModal'); const ids=['missedKcal','missedProtein','missedCarbs','missedFat']; return {over:m.scrollWidth>m.clientWidth+1, boxes:ids.map(i=>{const r=document.getElementById(i).getBoundingClientRect(); return [Math.round(r.left),Math.round(r.right),Math.round(r.width)]}), vis:ids.every(i=>document.getElementById(i).offsetParent!==null)}})()")
            if r['over'] or not r['vis'] or any(x[1] > 390 or x[2] < 60 for x in r['boxes']): f.add('BUG', f'1: four boxes fit a 390px phone: {r}')
            p.screenshot(path='/tmp/claude-0/p360_missed_modal.png')
        ev("saveMissedDay()"); p.wait_for_timeout(300)
    # typed fat -> new day
    miss(2, '1800', '100', '30', '12.5', 'Zed trip')
    d = day(2)
    if not d or d['totals']['fat'] != 12.5 or d['log'][0]['fat'] != 12.5: f.add('BUG', f'2: typed fat is stored on the entry and the day: {d and d["totals"]}')
    # blank fat -> 0, nothing invented
    miss(3, '1500', '90', '20', '', 'Zed quiet')
    d = day(3)
    if not d or d['totals']['fat'] != 0 or d['totals']['kcal'] != 1500: f.add('BUG', f'3: blank fat counts as 0 and the rest is kept: {d and d["totals"]}')
    # day with meals: added to the total
    miss(4, '500', '30', '20', '7', '')
    d = day(4)
    if d['totals']['fat'] != 17 or d['totals']['kcal'] != 880 or len(d['log']) != 2: f.add('BUG', f'4: fat is added to a day that has meals (10+7): {d["totals"]} {len(d["log"])}')
    # form is empty on reopening
    ev("openMissedDayModal(__dmy(6))")
    if ev("document.getElementById('missedFat').value") != '': f.add('BUG', '5: Fat box is empty when the form is reopened')
    ev("closeMissedDayModal()")
    # reload, then History shows the figure
    p.reload(); p.wait_for_timeout(2000)
    ev("window.__dmy=n=>{const d=new Date(); d.setDate(d.getDate()-n); return String(d.getDate()).padStart(2,'0')+'/'+String(d.getMonth()+1).padStart(2,'0')+'/'+String(d.getFullYear()).slice(2)}")
    d = day(2)
    if not d or d['totals']['fat'] != 12.5: f.add('BUG', f'6: fat survives a reload: {d and d["totals"]}')
    ev("document.getElementById('maintab-log').click()"); p.wait_for_timeout(400); ev("document.getElementById('logtab-hist').click()"); p.wait_for_timeout(700)
    i = ev("[...document.querySelectorAll('.hist-day')].findIndex(x=>x.querySelector('.hist-day-date').textContent.trim()==__dmy(2))")
    if i < 0: f.add('BUG', '7: the new day shows in History')
    else:
        ev("document.querySelectorAll('.hist-day')[%d].querySelector('.hist-day-body').classList.add('open')" % i)
        if '12.5' not in ev("document.querySelectorAll('.hist-day')[%d].innerText" % i): f.add('BUG', '7: History shows the 12.5 g fat')
    # bug-report hints follow MH_HOME.issues
    ev("switchTabById('settings')") if ev("typeof switchTabById==='function'") else None
    h = ev("[document.getElementById('mhBugHint1')?.textContent||'', document.getElementById('mhBugHint2')?.textContent||'']")
    if 'GitHub' not in h[0] or 'GitHub' not in h[1]: f.add('BUG', f'8: with GitHub configured the hints still name GitHub: {h}')
    # same page with no public report page configured: hints say it copies, and the button copies
    ctx2 = b.new_context(viewport={'width': 390, 'height': 900}, service_workers='block')
    def _mod(route):
        r = route.fetch(); body = r.text().replace("issues: 'https://github.com/pete-maxhealth/maxhealth/issues/new'", "issues: ''")
        route.fulfill(response=r, body=body)
    ctx2.route('http://localhost:5757/', _mod); ctx2.route('http://localhost:5757/maxhealth.html', _mod)
    ctx2.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    p2 = ctx2.new_page(); p2.goto('http://localhost:5757/'); p2.wait_for_timeout(2000)
    h2 = p2.evaluate("[document.getElementById('mhBugHint1')?.textContent||'', document.getElementById('mhBugHint2')?.textContent||'', MH_HOME.issues]")
    if h2[2] != '' or 'GitHub' in h2[0] or 'GitHub' in h2[1] or 'Copies' not in h2[0]: f.add('BUG', f'9: with no report page the hints say it copies: {h2}')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
