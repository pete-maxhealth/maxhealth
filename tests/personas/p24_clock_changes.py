"""Persona 24: UK clock changes and the midnight-to-1am BST window. Dates must be the local day, never yesterday."""
import sys, re, csv, io; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright
f = Findings(); BLOCK = re.compile(r'^https?://(?!localhost)')
CASES = [  # (UTC instant, expected local dd/mm/yy, expected iso, note)
    ('2026-09-30T23:30:00Z', '01/10/26', '2026-10-01', '00:30 BST'),
    ('2026-10-24T23:30:00Z', '25/10/26', '2026-10-25', '00:30 BST, day clocks go back'),
    ('2026-10-25T00:30:00Z', '25/10/26', '2026-10-25', '01:30 BST (first)'),
    ('2026-10-25T01:30:00Z', '25/10/26', '2026-10-25', '01:30 GMT (second)'),
    ('2026-10-25T23:30:00Z', '25/10/26', '2026-10-25', '23:30 GMT'),
    ('2026-10-26T00:30:00Z', '26/10/26', '2026-10-26', '00:30 GMT'),
    ('2027-03-28T00:30:00Z', '28/03/27', '2027-03-28', '00:30 GMT, day clocks go forward'),
    ('2027-03-28T01:30:00Z', '28/03/27', '2027-03-28', '02:30 BST'),
    ('2027-03-28T23:30:00Z', '29/03/27', '2027-03-29', '00:30 BST next day'),
]
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block', timezone_id='Europe/London', accept_downloads=True)
    ctx.route(BLOCK, lambda r: r.abort())
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:150]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    for utc, dmy, iso, note in CASES:
        ms = int(datetime.fromisoformat(utc.replace('Z', '+00:00')).timestamp() * 1000)
        got = page.evaluate("ms => { const R = Date; const fixed = ms; const D = class extends R { constructor(...a){ if(a.length===0) super(fixed); else super(...a);} static now(){return fixed;} }; window.Date = D; const out = [todayStr(), localISODate(new Date())]; window.Date = R; return out; }", ms)
        if got != [dmy, iso]: f.add('BUG', f'{note}: expected {dmy}/{iso}, app says {got}')
    # the manual-entry CSV template must start at the real local day in the 00:00-01:00 BST window
    ms = int(datetime(2026, 9, 30, 23, 30, tzinfo=timezone.utc).timestamp() * 1000)
    page.evaluate("ms => { const R = Date; const D = class extends R { constructor(...a){ if(a.length===0) super(ms); else super(...a);} static now(){return ms;} }; window.Date = D; window.__R = R; }", ms)
    page.evaluate("loadManualTemplateFields && (document.body.insertAdjacentHTML('beforeend','<input id=manualCsvDaysBack value=3>'))")
    with page.expect_download() as dl:
        page.evaluate("downloadManualEntryCsvTemplate()")
    text = open(dl.value.path()).read().splitlines()
    page.evaluate("window.Date = window.__R")
    if len(text) < 2 or not text[1].startswith('2026-10-01'): f.add('BUG', f'template first date at 00:30 BST should be 2026-10-01, got {text[1][:12] if len(text) > 1 else text}')
    if errs: f.add('JS-exception', str(errs[:3]))
    b.close()
print('findings', len(f)); sys.exit(1 if f else 0)
