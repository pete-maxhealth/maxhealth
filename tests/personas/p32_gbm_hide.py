"""Persona 32: a GBM user can hide the GBM Monthly Summary and Research Digest (👁) and they STAY hidden after a re-render."""
import sys; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    page = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block').new_page()
    page.on('pageerror', lambda e: errs.append(str(e)[:150]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("onboardNext(2)"); page.fill('#onboardName', 'Pete'); page.evaluate("onboardNext(3)")
    page.evaluate("obSetSex('male')"); page.fill('#onboardAge', '56'); page.fill('#onboardHeight', '176')
    page.fill('#onboardWeight', '82'); page.fill('#onboardTarget', '78')
    page.evaluate("onboardNext(4)"); page.evaluate("obSetActivity('light')"); page.evaluate("obSetGoal('maintain')")
    page.evaluate("onboardNext(5)"); page.evaluate("obSetCondition('gbm')")
    page.evaluate("onboardNext(6)"); page.evaluate("onboardFinish()"); page.wait_for_timeout(1500)
    page.evaluate("switchTab('insights')"); page.wait_for_timeout(500)
    vis = lambda id: page.evaluate(f"(()=>{{const e=document.getElementById('{id}');return !!e && getComputedStyle(e).display!=='none'}})()")
    page.evaluate("renderReports()"); page.wait_for_timeout(400)
    if not (vis('rpt-gbm-wrap') and vis('rpt-research-wrap')): f.add('BUG', 'GBM sections not visible for a GBM user to begin with')
    for k in ('rpt-gbm', 'rpt-research'):
        page.evaluate(f"toggleGenericSectionHidden('reports','{k}')")
    page.wait_for_timeout(300)
    page.evaluate("renderReports()"); page.wait_for_timeout(400)
    page.evaluate("updateGBMSectionVisibility()")
    for k in ('rpt-gbm', 'rpt-research'):
        if vis(f'{k}-title') or vis(f'{k}-wrap'): f.add('BUG', f'{k} came back after hiding')
    page.reload(wait_until='domcontentloaded'); page.wait_for_timeout(2000)
    page.evaluate("switchTab('insights')"); page.wait_for_timeout(600)
    if vis('rpt-gbm-wrap') or vis('rpt-research-wrap'): f.add('BUG', 'hidden GBM reports reappeared after reload')
    # and they can be restored
    for k in ('rpt-gbm', 'rpt-research'):
        page.evaluate(f"toggleGenericSectionHidden('reports','{k}')")
    page.wait_for_timeout(300)
    if not (vis('rpt-gbm-title') and vis('rpt-research-title')): f.add('BUG', 'restore did not bring GBM reports back')
    if errs: f.add('JS-exception', str(errs[:3]))
    b.close()
print('findings', len(f)); sys.exit(1 if f else 0)
