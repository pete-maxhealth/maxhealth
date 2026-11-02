"""p370: boxes that save on their own keep what you type. Finds every box that says it saves itself (an onchange/onblur handler, so no Save button is expected), types a
valid value (inside its min/max), lets the app run its refresh and a sync-style update, reloads, and reads it back. A box that comes back EMPTY is a bug (it lost the
value). A different value is listed for review (rounding, or the app's own limits). Boxes that need a Save button, secrets, files and one-shot inputs are not in scope.
Invented data. Writes the table to /tmp/claude-0/crawl/p370.json."""
import sys, json, os; sys.path.insert(0, 'tests/personas')
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
SKIP = ('apiKeyInput', 'licenceKeyInput', 'carerEmailInput', 'photoInput', 'cameraInput', 'barcodeInput', 'chatInput', 'debugWatchDateInput', 'librarySearch',
        'trendsCustomFromInput', 'trendsCustomToInput', 'rptDateFrom', 'rptDateTo', 'rptAskInput', 'researchDigestInput', 'customOccasionInput', 'wiInput')
# Boxes that are search/filter/one-shot inputs, not stored settings, are skipped by name pattern.
import re
SKIPRE = re.compile(r'(search|filter|sort|query|rptQuery|export|Selector|import|new|custom|debug|ask|chat|barcode|camera|photo|licen|apikey|email|mhTw)', re.I)
TABS = ('manage', 'customise', 'import', 'move')
VAL = {'number': '53', 'text': 'Zed', 'textarea': 'Zed note', 'select-one': None}
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); ev = page.evaluate
    page.on('pageerror', lambda e: f.add('JS-exception', str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200)
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay').style.display='none'"); page.reload(); page.wait_for_timeout(1500)
    for tb in TABS:
        ev(f"try {{ switchTabById('{tb}'); }} catch (e) {{}}"); page.wait_for_timeout(500)
    ids = ev("""[...document.querySelectorAll('input:not([type=checkbox]):not([type=hidden]):not([type=file]):not([type=date]):not([type=password]):not([type=email]):not([type=range]),textarea,select')]
      .filter(e => e.id && !e.closest('.modal,[id$=Modal],.app-modal-overlay,#onboardingOverlay') && (e.hasAttribute('onchange') || e.hasAttribute('onblur')))
      .map(e => [e.id, e.tagName === 'SELECT' ? 'select-one' : e.type, e.value, e.min || '', e.max || ''])""")
    ids = [x for x in ids if x[0] not in SKIP and not SKIPRE.search(x[0])]
    typed = {}
    for (i, t, cur, mn, mx) in ids:
        v = (str(round((float(mn) + float(mx)) / 2)) if (t == 'number' and mn and mx) else '23.5k' if i == 'dailyStepsInput' else VAL.get(t, '7')) if t != 'select-one' else ev("(id => { const s = document.getElementById(id); if (!s) return null; const o = [...s.options].find(o => o.value !== s.value && !o.disabled); return o ? o.value : null; })", i)
        if v is None: continue
        if t == 'number': 
            mn = ev("document.getElementById(arguments[0]||'x')", i) if False else None
        ok = ev("""(a) => { const e = document.getElementById(a[0]); if (!e) return false; e.value = a[1]; ['input', 'change', 'blur'].forEach(n => e.dispatchEvent(new Event(n, { bubbles: true }))); return e.value; }""", [i, v])
        if ok is False: continue
        typed[i] = (t, v, ok)
        page.wait_for_timeout(60)
    page.wait_for_timeout(1500); ev("try { updateDashboard(); } catch (e) {}"); page.wait_for_timeout(800)
    ev("try { autoImportCombinedIfStale(); } catch (e) {}"); page.wait_for_timeout(8000)   # the real sync round trip: what you typed is saved to the server and read back (this blanked the steps box before v3.10.1255)
    ev("try { updateDashboard(); } catch (e) {}"); page.wait_for_timeout(500)
    page.reload(); page.wait_for_timeout(2000)
    for tb in TABS:
        ev(f"try {{ switchTabById('{tb}'); }} catch (e) {{}}"); page.wait_for_timeout(600)
    rows = []
    for i, (t, v, acc) in typed.items():
        got = ev("(id) => { const e = document.getElementById(id); return e ? e.value : null; }", i)
        status = 'kept' if got == acc else ('EMPTY' if got in ('', None) else 'changed')
        rows.append((i, t, v, acc, got, status))
    os.makedirs('/tmp/claude-0/crawl', exist_ok=True); json.dump(rows, open('/tmp/claude-0/crawl/p370.json', 'w'))
    for r in rows:
        if r[5] == 'EMPTY' and r[1] != 'select-one': f.add('BUG', f'{r[0]}: typed {r[2]!r}, came back empty after reload')
        elif r[5] != 'kept': f.add('REVIEW', f'{r[0]} ({r[1]}): typed {r[2]!r} (box showed {r[3]!r}), after reload {r[4]!r}')
    print('boxes typed into:', len(typed), '| kept:', sum(1 for r in rows if r[5] == 'kept'), '| changed:', sum(1 for r in rows if r[5] == 'changed'), '| empty:', sum(1 for r in rows if r[5] == 'EMPTY'))
bugs = [x for x in f if x[0] in ('BUG', 'JS-exception')]
for x in f:
    if x[0] == 'REVIEW': print('  review:', x[1][:170])
print('findings:', len(f), 'bugs:', len(bugs)); [print(x) for x in bugs]; sys.exit(1 if bugs else 0)
