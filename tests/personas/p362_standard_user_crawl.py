"""Persona 362: a standard (non-clinical, General Health) user clicks every visible button on every screen.
Reports: JS errors, NaN/undefined text, and clinical wording (ketone, GBM, seizure, insulin ...) that a standard user can see.
Destructive buttons (delete/reset/erase/sign out/import/restore) are skipped. Findings are for review, not all are bugs."""
import sys, re, json; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
PERSONA = sys.argv[1] if len(sys.argv) > 1 else 'doris'
CLIN = re.compile(r'ketone|ketosis|ketogenic|\bGKI\b|glioma|\bGBM\b|glioblastoma|seizure|epilep|migraine|cluster headache|insulin|hypoglyc|\bMRI\b|chemo|temozolomide|TTField|oncolog|diabet|dexamethasone|radiotherapy', re.I)
SKIP = re.compile(r'delete|remove all|reset|erase|wipe|clear all|sign out|log ?out|import|restore|replace|factory|forget|uninstall|stop sharing|revoke', re.I)
f = Findings(); seen_clin = {}; clicked = 0; skipped = []
SCAN = """() => { const out = []; const vis = e => { const r = e.getBoundingClientRect(); const s = getComputedStyle(e); return r.width > 4 && r.height > 4 && s.visibility !== 'hidden' && s.display !== 'none' && !e.closest('[style*="display: none"],[style*="display:none"],[hidden]'); };
  document.querySelectorAll('button, [onclick], summary, [role=button], .tab-btn').forEach((e, i) => { if (!vis(e)) return; const t = (e.innerText || e.getAttribute('aria-label') || e.title || '').trim().slice(0, 50); out.push({ i, t, oc: (e.getAttribute('onclick') || '').slice(0, 80) }); }); return out; }"""
def visible_text(page):
    return page.evaluate("""() => { const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); let o = [], n; while (n = w.nextNode()) { const e = n.parentElement; if (!e || ['SCRIPT','STYLE'].includes(e.tagName)) continue; const r = e.getBoundingClientRect(), s = getComputedStyle(e); if (r.width > 2 && r.height > 2 && s.display !== 'none' && s.visibility !== 'hidden') o.push(n.nodeValue.trim()); } return o.filter(Boolean).join(' | '); }""")
def check_text(where, txt):
    for m in CLIN.finditer(txt):
        ctx = txt[max(0, m.start() - 50):m.end() + 50].replace('\n', ' ')
        key = (m.group(0).lower(), ctx[:40])
        if key not in seen_clin: seen_clin[key] = where; f.add('clinical-wording', f'{where}: "…{ctx}…"')
    for w in ('NaN', 'undefined', 'Infinity', '[object Object]', 'null'):
        if re.search(r'(?<![\w-])' + re.escape(w) + r'(?![\w-])', txt): f.add('BUG', f'{where}: "{w}" visible')
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 900}, service_workers='block'); page = ctx.new_page()
    page.on('pageerror', lambda e: f.add('JS-exception', str(e)[:200])); page.on('dialog', lambda d: d.dismiss())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate(f"startDemoMode('{PERSONA}')"); page.wait_for_timeout(1800); ev = page.evaluate
    print('condition:', ev("localStorage.getItem('mh_condition')"), 'goal:', ev("localStorage.getItem('mh_goal')"))
    tabs = list(ev("Object.keys(NAV_MAP)")); print('screens:', tabs)
    for tab in tabs:
        ev("window.appConfirm=(m,ok)=>{}"); 
        def open_tab():
            try: ev(f"switchTabById('{tab}')")
            except Exception as e: f.add('JS-exception', f'open {tab}: {str(e)[:100]}'); return False
            page.wait_for_timeout(500); return True
        if not open_tab(): continue
        check_text(f'screen {tab}', visible_text(page))
        items = ev(SCAN); n_here = 0
        for it in items[:60]:
            if SKIP.search(it['t'] + ' ' + it['oc']): skipped.append(f"{tab}: {it['t'] or it['oc']}"); continue
            if not open_tab(): break
            cur = ev(SCAN)
            if it['i'] not in [c['i'] for c in cur]: continue
            before = len(f)
            try: ev(f"(() => {{ const e = document.querySelectorAll('button, [onclick], summary, [role=button], .tab-btn')[{it['i']}]; if (e) e.click(); }})()")
            except Exception as e: f.add('JS-exception', f"{tab} / {it['t']}: {str(e)[:100]}")
            page.wait_for_timeout(250); clicked += 1; n_here += 1
            check_text(f"{tab} > '{it['t'] or it['oc']}'", visible_text(page))
            try: page.keyboard.press('Escape')
            except Exception: pass
        print(f'  {tab}: clicked {n_here}')
        page.reload(); page.wait_for_timeout(900)
    print(f'clicked {clicked} buttons, skipped {len(skipped)} destructive ones')
    json.dump({'skipped': skipped, 'findings': [list(x) for x in f]}, open('/tmp/claude-0/crawl/%s.json' % PERSONA, 'w'), indent=1)
bugs = [x for x in f if x[0] in ('BUG', 'JS-exception')]
print('findings:', len(f), 'bugs/exceptions:', len(bugs)); sys.exit(1 if bugs else 0)
