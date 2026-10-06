"""Persona 34: tapping a notification opens the app on the screen it was about (Pete 6 Oct)."""
import sys, re; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
def sub(page): return page.evaluate("JSON.stringify([_activeSubTab, document.querySelector('.tab-btn.active, .maintab.active')?.id||''])")
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, permissions=['notifications'])   # service workers allowed
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:160])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200)
    page.evaluate("onboardNext(2)"); page.fill('#onboardName', 'Ola'); page.evaluate("onboardNext(3)")
    page.evaluate("obSetSex('male')"); page.fill('#onboardAge', '58'); page.fill('#onboardHeight', '176')
    page.fill('#onboardWeight', '82'); page.fill('#onboardTarget', '78')
    page.evaluate("onboardNext(4)"); page.evaluate("obSetActivity('light')"); page.evaluate("obSetGoal('lose')")
    page.evaluate("onboardNext(5)"); page.evaluate("obSetCondition('general')")
    page.evaluate("onboardNext(6)"); page.evaluate("onboardFinish()"); page.wait_for_timeout(1500)
    # 1. app closed, opened from a notification: ?tab=reports
    page.goto('http://localhost:5757/?tab=reports', wait_until='domcontentloaded'); page.wait_for_timeout(3000)
    st = page.evaluate("_activeSubTab.insights")
    if st != 'reports': f.add('BUG', f'?tab=reports did not open Reports (insights sub-tab = {st})')
    if 'tab=' in page.url: f.add('BUG', 'tab param left in the address bar')
    # 2. app open elsewhere; the service worker's click handler focuses it and tells it where to go
    page.evaluate("switchTabById('dash'); switchTabById('manage')"); page.wait_for_timeout(2500)
    sws = ctx.service_workers
    if not sws: f.add('BUG', 'no service worker running to test the click handler')
    else:
        # headless Chromium does not reliably create OS notifications, so fire the handler with an equivalent event
        sws[0].evaluate("async()=>{const ev=new ExtendableEvent('notificationclick'); ev.notification={close(){},data:{tab:'supplements'}}; self.dispatchEvent(ev);}")
        page.wait_for_timeout(1000)
        if page.evaluate("_activeSubTab.today") != 'supplements' or page.evaluate("document.getElementById('maintab-today')?.classList.contains('active')") is False:
            f.add('BUG', 'notification click did not take the open app to Supplements: ' + page.evaluate("JSON.stringify(_activeSubTab)"))
    if errs: f.add('JS-exception', str(errs[:3]))
    b.close()
print('findings', len(f)); sys.exit(1 if f else 0)
