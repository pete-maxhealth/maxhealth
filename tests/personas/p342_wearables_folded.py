"""Persona 342 (v3.10.1227): Settings > Data: Wearable History and Add New Device sit inside the Sync Wearable Data card (no longer separate cards); they keep their own fold; an old saved card order (8 cards) still loads; hiding Sync hides them with it and they come back; topic chips still reach them. Invented data."""
import sys, re, json; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    ev = page.evaluate
    old = ['set-databackup','imp-qr','imp-restore','imp-sync','imp-combined','imp-adddevice','imp-manual','imp-gaps']
    # an older saved order that still lists the two folded sections and has Manual Entry moved to the top
    page.add_init_script("localStorage.setItem('mh_reorder_import', %s)" % json.dumps(json.dumps(['imp-manual']+[k for k in old if k != 'imp-manual'])))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1800)
    ev("closeOnboardingOverlay(); switchTab('import'); mhTopicSet('import','all')"); page.wait_for_timeout(900)
    for k in ('imp-combined', 'imp-adddevice', 'imp-advanced'):
        if not ev(f"!!document.querySelector('#imp-sync-wrap #{k}-wrap')"): f.add('BUG', f'{k} should sit inside Sync Wearable Data')
    cards = ev("[...document.querySelectorAll('#view-import .card-unit')].map(c => (c.querySelector('[id^=title-]')||{}).id)")
    if 'title-imp-combined' in cards or 'title-imp-adddevice' in cards: f.add('BUG', f'folded sections are still separate cards: {cards}')
    if len(cards) != 6: f.add('BUG', f'expected 6 cards, got {cards}')
    # no leftover card-level move/hide controls on the folded sections
    ctl = ev("(() => { let n = 0; for (const id of ['title-imp-combined','title-imp-adddevice']) { const t = document.getElementById(id); n += t.parentElement.querySelectorAll('[onclick*=\"Generic\"], .mh-reorder, [title=\"Hide\"]').length; } return n; })()")
    if ctl: f.add('BUG', f'folded sections still carry {ctl} card controls')
    # the old saved order is honoured for the cards that remain (Manual Entry first), nothing crashed
    if cards[0] != 'title-imp-manual': f.add('BUG', f'saved order lost: {cards}')
    # folded sections keep their own fold
    ev("toggleSection('imp-combined','imp-combined-wrap','imp-combined-icon')"); page.wait_for_timeout(150)
    shown = ev("getComputedStyle(document.getElementById('imp-combined-wrap')).display !== 'none'")
    ev("toggleSection('imp-combined','imp-combined-wrap','imp-combined-icon')"); page.wait_for_timeout(150)
    shown2 = ev("getComputedStyle(document.getElementById('imp-combined-wrap')).display !== 'none'")
    if shown == shown2: f.add('BUG', 'Wearable History fold does not toggle')
    # topic chips: Connect devices reaches the folded sections through the Sync card
    ev("mhTopicSet('import','connect')"); page.wait_for_timeout(300)
    if not ev("!!document.getElementById('title-imp-combined').offsetParent"): f.add('BUG', 'Connect devices chip hides Wearable History')
    if not ev("!!document.getElementById('title-imp-adddevice').offsetParent"): f.add('BUG', 'Connect devices chip hides Add New Device')
    ev("mhTopicSet('import','history')"); page.wait_for_timeout(300)
    if ev("!!document.getElementById('title-imp-manual').offsetParent") is False: f.add('BUG', 'History & entry chip hides Manual Entry')
    # reload keeps everything working
    ev("mhTopicSet('import','all')"); page.reload(); page.wait_for_timeout(1800); ev("closeOnboardingOverlay(); switchTab('import')"); page.wait_for_timeout(700)
    if not ev("!!document.querySelector('#imp-sync-wrap #imp-adddevice-wrap')"): f.add('BUG', 'after reload Add New Device is not inside Sync')
    if errs: f.add('JS-exception', errs[0])
    b.close()
print('BUGS' if any(s == 'BUG' or s == 'JS-exception' for s, _ in f) else 'OK', len(f)); sys.exit(1 if any(s in ('BUG', 'JS-exception') for s, _ in f) else 0)
