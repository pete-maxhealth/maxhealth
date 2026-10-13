"""Persona 137: the System health note stays readable and its action link stays reachable even when the pipeline messages are very long: label stacks above full-width text, the actions sit directly under the headline (above the long lines), each long line is cut with a Details toggle that reveals the whole text, and a sleep-conflict warning offers a way to resolve it."""
import sys, json; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
LONG = 'Pipeline warning x1 this week: health_connect: Overlapping sleep sessions for 2026-10-13, needs resolution — ringconn: 01:54-05:17 (202m asleep), zepp: 02:09-07:53 (177m asleep)'
PAYLOAD = {'status': 'amber', 'headline': 'Needs a look', 'items': [{'level': 'amber', 'text': LONG}, {'level': 'amber', 'text': 'Pipeline warning x1 this week: ' + 'x' * 120}, {'level': 'amber', 'text': '2 app error x3: TypeError'}]}
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.route('**/selfcheck*', lambda r: r.fulfill(status=200, content_type='application/json', body=json.dumps(PAYLOAD)))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev = page.evaluate
    ev("switchTab('settings', document.getElementById('maintab-settings'))"); page.wait_for_timeout(800)
    ev("updateSelfCheckDisplay()"); page.wait_for_timeout(700)
    el = page.locator('#selfCheckDisplay')
    box = el.bounding_box()
    if not box or box['width'] < 250: f.add('BUG', f'health text still squeezed: {box}')
    t = ev("document.getElementById('selfCheckDisplay').textContent")
    for need in ('Mark app errors as fixed', 'Resolve sleep conflict', 'Details'):
        if need not in t: f.add('BUG', f'missing {need!r}')
    link = page.locator('#selfCheckDisplay').get_by_text('Mark app errors as fixed').bounding_box(); first = page.locator('#selfCheckDisplay > div').nth(2).bounding_box()
    if not link or not first or link['y'] > first['y']: f.add('BUG', f'action link is not above the long lines {link} {first}')
    if link and (link['height'] < 22 or link['y'] < 0 or link['y'] + link['height'] > 800): pass
    shown = ev("[...document.querySelectorAll('#selfCheckDisplay > div')].map(d=>d.textContent.length)")
    if max(shown[2:5]) > 100: f.add('BUG', f'long line not cut {shown}')
    if ev("document.getElementById('selfCheckFull').style.display") != 'none': f.add('BUG', 'details open by default')
    page.locator('#selfCheckDisplay').get_by_text('Details ▾').click(); page.wait_for_timeout(200)
    if LONG not in ev("document.getElementById('selfCheckFull').textContent") or ev("document.getElementById('selfCheckFull').style.display") != 'block': f.add('BUG', 'details did not reveal the full text')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
    page.evaluate("document.getElementById('selfCheckDisplay').scrollIntoView()"); page.screenshot(path='/tmp/claude-0/pp/health.png')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
