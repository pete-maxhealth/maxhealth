"""Persona 55: Settings > Notifications card shows the real permission state without needing Reports or a header tap."""
import sys, re; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    for perm, expect_btn in (('granted', False), ('default', True), ('denied', False)):
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
        ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
        ctx.add_init_script("""(() => { let p = '%s'; try { Object.defineProperty(Notification, 'permission', { get: () => window.__np || p }); } catch (e) {} })()""" % perm)
        page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:160]))
        page.goto('http://localhost:5757/'); page.wait_for_timeout(1200)
        page.evaluate("onboardNext(2)"); page.fill('#onboardName', 'Ola'); page.evaluate("onboardNext(3)")
        page.evaluate("obSetSex('male')"); page.fill('#onboardAge', '58'); page.fill('#onboardHeight', '176')
        page.fill('#onboardWeight', '82'); page.fill('#onboardTarget', '78')
        page.evaluate("onboardNext(4)"); page.evaluate("obSetActivity('light')"); page.evaluate("obSetGoal('lose')")
        page.evaluate("onboardNext(5)"); page.evaluate("obSetCondition('general')")
        page.evaluate("onboardNext(6)"); page.evaluate("onboardFinish()"); page.wait_for_timeout(1500)
        page.evaluate("switchTabById('settings')"); page.wait_for_timeout(3200)    # never visits Reports, never taps the header
        shown = page.evaluate("getComputedStyle(document.getElementById('rptNotifBtn')).display !== 'none'")
        if shown != expect_btn: f.add('BUG', f'permission {perm}: ENABLE button shown={shown}, expected {expect_btn}')
        if perm == 'granted' and 'enabled' not in page.evaluate("document.getElementById('rpt-notif-status').textContent"): f.add('BUG', 'granted but status does not say enabled')
        if perm == 'default':
            # permission changes while the card is on screen (e.g. allowed from Android settings): the card follows
            page.evaluate("window.__np = 'granted'"); page.wait_for_timeout(2600)
            if page.evaluate("getComputedStyle(document.getElementById('rptNotifBtn')).display !== 'none'"): f.add('BUG', 'card did not follow permission turning granted')
        ctx.close()
    if errs: f.add('BUG', f'page errors: {errs[:3]}')
    b.close()
print('findings', len(f)); sys.exit(1 if f else 0)
