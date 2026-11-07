"""Persona 423: carer/clinician share guidance (v3.10.1321). Pete 7 Nov: keep the four defaults on, and make sharing more or less foolproof.
Covers: the "Want to share more or less?" line with a working "?" on the share card; the link carries the keys of the items that are OFF (keys only, no data) and follows the ticks;
the carer page (carer.html opened from the link) says what it does not show and to ask the person, changes when an item is switched on, shows nothing when everything is on, and shows a generic line for an older link with no list;
nothing sensitive in the list; no page errors. Invented data."""
import sys, re, json, base64, urllib.parse; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from datetime import date, timedelta
from playwright.sync_api import sync_playwright
f = Findings(); chk = lambda ok, m: None if ok else f.add('BUG', m)
dmy = lambda n: (date.today() - timedelta(days=n)).strftime('%d/%m/%Y')
day = lambda n: {'date': dmy(n), 'mode': 'standard', 'notes': 'standard', 'weight': 80, 'log': [{'id': n, 'time': '08:00', 'description': 'Zzqx Eggs', 'kcal': 400, 'protein': 20, 'carbs': 2, 'fat': 15}], 'totals': {'kcal': 1600, 'protein': 110, 'carbs': 9, 'fat': 55}}
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:200])); ev = page.evaluate
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("state.history = " + json.dumps([day(i) for i in range(1, 13)]) + "; saveState()")
    ev("switchTab('settings'); try{switchSubTab('settings','manage')}catch(e){}; mhShareRender()"); page.wait_for_timeout(400)
    hint = ev("document.getElementById('shareMoreHint')?.textContent||''")
    chk('share more or less' in hint, f'1: hint line missing: {hint!r}')
    page.locator('#shareMoreHint span[onclick]').first.scroll_into_view_if_needed(); page.locator('#shareMoreHint span[onclick]').first.click(); page.wait_for_timeout(400)
    txt = ev("document.getElementById('help-sharemore')?.innerText||''"); chk('GENERATE CARER VIEW LINK' in txt and 'Preview' in txt and 'new link' in txt, '2: the "?" did not open the steps')
    def link():
        ev("generateCarerLink()"); page.wait_for_timeout(400)
        u = ev("document.querySelector('#carerLinkOutput textarea').value"); h = urllib.parse.unquote(u.split('#', 1)[1])
        return json.loads(base64.b64decode(h).decode('utf-8')), h
    def carer_text(hashv):
        p2 = ctx.new_page(); p2.on('pageerror', lambda e: errs.append('carer ' + str(e)[:160])); p2.goto('http://localhost:5757/carer.html#' + hashv); p2.wait_for_timeout(1800)
        t = p2.inner_text('body'); p2.close(); return t
    pl, h = link()
    chk(sorted(pl.get('off', [])) == ['meals', 'supps', 'timing', 'treat'], f'3: default off list is {pl.get("off")}')
    chk('Zzqx' not in json.dumps(pl), '4: food names in the default link')
    t = carer_text(h)
    chk('Not shown on this page' in t and 'meal times and food names' in t and 'Ask the person' in t, f'5: carer page default note missing: {t[-300:]!r}')
    chk('weight' not in t.split('Not shown on this page:')[-1].split('.')[0], '6: weight listed as not shown while it is on')
    ev("mhShareToggle('meals', true)"); pl, h = link()
    chk('meals' not in pl.get('off', []), f'7: off list ignores the tick: {pl.get("off")}')
    t = carer_text(h); note = t.split('Not shown on this page:')[-1].split('.')[0] if 'Not shown on this page' in t else ''
    chk('meal times' not in note, f'8: carer page still lists meals as not shown: {note!r}')
    for k in ('timing', 'treat', 'supps', 'weight', 'exercise', 'sleep'): ev(f"mhShareToggle('{k}', true)")
    pl, h = link(); chk(pl.get('off') == [], f'9: everything on gives off={pl.get("off")}')
    t = carer_text(h); chk('Not shown on this page' not in t and 'may not be shown' not in t, '10: a note shows although everything is on')
    old = dict(pl); old.pop('off', None)
    h2 = base64.b64encode(json.dumps(old).encode('utf-8')).decode()
    t = carer_text(h2); chk('may not be shown' in t and 'Ask the person' in t, f'11: older link has no generic note: {t[-200:]!r}')
    if errs: f.add('BUG', f'page errors {errs[:3]}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
