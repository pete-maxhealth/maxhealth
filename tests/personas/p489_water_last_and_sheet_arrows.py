"""Persona 489 (v3.10.1407): water card shows when water was last added (every add route, reset, new day); the Paste meal and Log missed day sheets have the
round top-left back arrow that closes them; the floating back arrow shows at the top of a screen you moved to. Invented data only."""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    page = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block').new_page()
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); page.evaluate("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev = page.evaluate
    txt = lambda: ev("(()=>{const e=document.getElementById('waterLast');return getComputedStyle(e).display==='none'?'':e.textContent})()")
    txt() == '' or f.add('FAIL', f'last-added shown with no water: {txt()}')
    ev("logWater(250)"); page.wait_for_timeout(300)
    t = txt(); re.fullmatch(r'Last added \d\d:\d\d · \+250ml', t) or f.add('FAIL', f'after +250: {t!r}')
    ev("logWater(500)"); t = txt(); t.endswith('+500ml') or f.add('FAIL', f'last add should be 500: {t!r}')
    ev("state.waterLast.time='09:41'; updateDashboard()"); txt().startswith('Last added 09:41') or f.add('FAIL', 'time not taken from the stamp')
    ev("state.waterLast.date='01/01/20'; updateDashboard()"); txt() == '' or f.add('FAIL', 'a stamp from another day is still shown')
    ev("_addWaterAndCelebrate(330,'x')"); txt().endswith('+330ml') or f.add('FAIL', 'celebrate path not stamped')
    ev("state.waterLast=null; updateDashboard()"); ev("state.waterToday") == 1080 or f.add('FAIL', f'total wrong {ev("state.waterToday")}')
    # reset
    ev("logWater(250)"); ev("resetWater()"); page.wait_for_timeout(300)
    page.evaluate("document.querySelectorAll('.app-modal-overlay button').forEach(b=>{if(/yes|reset|ok|confirm/i.test(b.textContent))b.click()})"); page.wait_for_timeout(300)
    ev("state.waterToday") == 0 and ev("state.waterLast") is None or f.add('FAIL', f'reset did not clear: {ev("[state.waterToday,state.waterLast]")}')
    txt() == '' or f.add('FAIL', 'last-added still shown after reset')
    # sheets
    for sheet, fn, opener in (('pasteMealModal', 'closePasteMealModal', "openPasteMealModal()"), ('missedDayModal', 'closeMissedDayModal', "openMissedDayModal()")):
        if not ev(f"typeof {opener.split('(')[0]}==='function'"): f.add('FAIL', opener + ' missing'); continue
        ev("switchTab('log'); switchSubTab('log','history')"); page.wait_for_timeout(300); ev(opener); page.wait_for_timeout(400)
        look = ev(f"(()=>{{const b=document.querySelector('#{sheet} .mh-sheet-back'),sh=document.querySelector('.mh-back-ref');if(!b)return null;const r=b.getBoundingClientRect(),s=getComputedStyle(b);return {{w:Math.round(r.width),h:Math.round(r.height),br:s.borderRadius,t:b.textContent,vis:r.width>0&&r.top>=0}}}})()")
        if not look: f.add('FAIL', f'{sheet}: no back arrow'); continue
        look['t'] == '←' and look['w'] == 36 and look['h'] == 36 and look['vis'] or f.add('FAIL', f'{sheet}: arrow look {look}')
        ev(f"document.querySelector('#{sheet} .mh-sheet-back').click()"); page.wait_for_timeout(300)
        ev(f"getComputedStyle(document.getElementById('{sheet}')).display") == 'none' or f.add('FAIL', f'{sheet}: arrow did not close the sheet')
    # floating arrow at the top of a screen you moved to
    ev("switchTab('today')"); ev("switchTab('log'); switchSubTab('log','history')"); page.wait_for_timeout(400)
    ev("getComputedStyle(document.getElementById('globalBackBtn')).display") != 'none' or f.add('FAIL', 'floating back arrow not shown at the top of History')
    ev("document.getElementById('globalBackBtn').click()"); page.wait_for_timeout(300)
    ev("_navSnap().tab") == 'today' or f.add('FAIL', 'floating arrow did not go back')
    errs and f.add('FAIL', f'page errors {errs}'); b.close()
print('findings', len(f))
