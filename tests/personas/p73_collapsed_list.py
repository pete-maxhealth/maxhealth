"""Persona 73: a collapsed Settings card shrinks to a single tidy list row (title left, controls right, action buttons tucked away) and expands back."""
import sys, re; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("localStorage.setItem('mh_onboarded','1'); switchTab('settings'); switchSubTab('settings','manage'); mhTopicSet('manage','all'); mhTogglePills();"); page.wait_for_timeout(500)
    page.evaluate("[...document.querySelectorAll('#view-manage .mh-pills-toolbar button')].find(b => b.innerText === 'Close all').click()"); page.wait_for_timeout(300)
    info = page.evaluate("""() => [...document.querySelectorAll('#view-manage .section-title.mh-collapsed')].map(t => {
      const r = t.getBoundingClientRect(), c = t.querySelector('.reorder-pos-badge'), cr = c ? c.getBoundingClientRect() : null;
      const vis = [...t.querySelectorAll('button')].filter(b => getComputedStyle(b).display !== 'none').length;
      return {id: t.id, h: Math.round(r.height), badgeInside: cr ? (cr.top >= r.top - 1 && cr.bottom <= r.bottom + 1) : null, buttons: vis, hidden: getComputedStyle(t).display === 'none'}; })""")
    rows = [i for i in info if not i['hidden']]
    if len(rows) < 8: f.add('BUG', f'expected many collapsed rows, found {len(rows)}')
    for i in rows:
        if i['h'] > 56: f.add('BUG', f"{i['id']} collapsed row is {i['h']}px tall, should be one list line")
        if i['badgeInside'] is False: f.add('BUG', f"{i['id']} position badge sits outside its row")
        if i['buttons']: f.add('BUG', f"{i['id']} still shows an action button while collapsed")
    page.evaluate("[...document.querySelectorAll('#view-manage .mh-pills-toolbar button')].find(b => b.innerText === 'Open all').click()"); page.wait_for_timeout(300)
    if page.evaluate("document.querySelectorAll('#view-manage .section-title.mh-collapsed').length") != 0: f.add('BUG', 'Open all should clear every collapsed row')
    if not page.evaluate("[...document.querySelectorAll('#title-set-symptoms button')].some(b => getComputedStyle(b).display !== 'none')"): f.add('BUG', 'Add / Clear all buttons should return when expanded')
    page.evaluate("document.getElementById('title-set-symptoms').click()"); page.wait_for_timeout(200)
    if not page.evaluate("document.getElementById('title-set-symptoms').classList.contains('mh-collapsed')"): f.add('BUG', 'tapping a header to collapse should shrink it too')
    page.reload(); page.wait_for_timeout(1500)
    page.evaluate("switchTab('settings'); switchSubTab('settings','manage'); mhTopicSet('manage','all');"); page.wait_for_timeout(500)
    if not page.evaluate("document.getElementById('title-set-symptoms').classList.contains('mh-collapsed')"): f.add('BUG', 'collapsed row state should persist across reload')
    if errs: f.add('BUG', f'page errors: {errs[:2]}')
print('findings', len(f)); sys.exit(1 if f else 0)
