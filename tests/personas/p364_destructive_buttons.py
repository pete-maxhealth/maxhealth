"""Persona 364: every destructive button (delete / reset / default / clear / import / restore ...) on every screen, pressed on a
throwaway demo user. For each one the confirmation is answered both ways:
  Cancel  -> nothing may change (any data key that changes is a BUG);
  Confirm -> reports what changed, whether the confirmation text said what would happen, and whether anything says how to undo.
Runs only against the disposable test server (fresh_server temp copy + a fresh browser profile): it can never touch a real account."""
import sys, re, json; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
PERSONA = sys.argv[1] if len(sys.argv) > 1 else 'doris'
DESTRUCTIVE = re.compile(r'delete|remove all|reset|erase|wipe|clear all|sign out|log ?out|import|restore|replace|factory|forget|uninstall|revoke|↺ default|^default$|reset dates|🗑', re.I)
VOLATILE = re.compile(r'collapse|nudge|visit|last_|_ts$|session|_ui|scroll|seen|tab|mh_dc_|mh_stk_|installed|focus|hint|opened', re.I)
f = Findings(); report = []
SCAN = """() => { const vis = e => { const r = e.getBoundingClientRect(); const s = getComputedStyle(e); return r.width > 4 && r.height > 4 && s.visibility !== 'hidden' && s.display !== 'none' && !e.closest('[style*="display: none"],[style*="display:none"],[hidden]'); };
  const out = []; document.querySelectorAll('button, [onclick], summary, [role=button], .tab-btn').forEach((e, i) => { if (!vis(e)) return; out.push({ i, t: (e.innerText || e.getAttribute('aria-label') || e.title || '').trim().replace(/\\s+/g, ' ').slice(0, 50), oc: (e.getAttribute('onclick') || '').slice(0, 80) }); }); return out; }"""
SNAP = """() => { const h = s => { let x = 0; for (let i = 0; i < s.length; i++) x = (x * 31 + s.charCodeAt(i)) | 0; return x; }; const o = {}; Object.keys(localStorage).forEach(k => o[k] = h(localStorage.getItem(k))); return o; }"""
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 900}, service_workers='block', accept_downloads=True); page = ctx.new_page(); ev = page.evaluate
    page.on('pageerror', lambda e: f.add('JS-exception', str(e)[:200]))
    native = []; answer = {'v': False}
    page.on('dialog', lambda d: (native.append(d.message), d.accept() if answer['v'] else d.dismiss()))
    page.on('filechooser', lambda fc: native.append('FILE CHOOSER opened'))
    def fresh():
        page.goto('http://localhost:5757/'); page.wait_for_timeout(900); ev("localStorage.clear()"); page.goto('http://localhost:5757/'); page.wait_for_timeout(900)
        ev(f"startDemoMode('{PERSONA}')"); page.wait_for_timeout(1300)
        assert 'localhost:5757' in page.url
        ev("sessionStorage.setItem('__confirms','[]'); window.__rec = m => { try { const a = JSON.parse(sessionStorage.getItem('__confirms') || '[]'); a.push(String(m)); sessionStorage.setItem('__confirms', JSON.stringify(a)); } catch (e) {} }; window.appConfirm = (m, ok, cancel) => { window.__rec(m); if (window.__answer) { ok && ok(); } else { cancel && cancel(); } }; window.confirm = m => { window.__rec(m); return !!window.__answer; };")
    fresh(); tabs = list(ev("Object.keys(NAV_MAP)")); targets = []
    for tab in tabs:
        ev(f"switchTabById('{tab}')"); page.wait_for_timeout(400)
        for it in ev(SCAN):
            if DESTRUCTIVE.search(it['t'] + ' ' + it['oc']): targets.append((tab, it['t'] or it['oc']))
    seen = set(); targets = [t for t in targets if not (t in seen or seen.add(t))]
    print(f'{len(targets)} destructive buttons found on {len(tabs)} screens')
    for tab, label in targets:
        row = dict(screen=tab, button=label[:45])
        for mode in ('cancel', 'confirm'):
            fresh(); ev(f"switchTabById('{tab}')"); page.wait_for_timeout(500)
            ev(f"window.__answer = {'true' if mode == 'confirm' else 'false'}"); answer['v'] = (mode == 'confirm'); native.clear()
            idx = next((it['i'] for it in ev(SCAN) if (it['t'] or it['oc']) == label), None)
            if idx is None: row[mode] = 'button not found'; continue
            before = ev(SNAP)
            try: ev(f"(() => {{ const e = document.querySelectorAll('button, [onclick], summary, [role=button], .tab-btn')[{idx}]; if (e) e.click(); }})()")
            except Exception as e: f.add('JS-exception', f'{tab} / {label}: {str(e)[:100]}')
            page.wait_for_timeout(700); after = ev(SNAP)
            changed = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k) and not VOLATILE.search(k))
            page.wait_for_timeout(300)
            try: conf = json.loads(ev("sessionStorage.getItem('__confirms') || '[]'")) + native
            except Exception: conf = list(native)
            try: txt = ev("document.body.innerText")
            except Exception: page.wait_for_timeout(800); txt = ev("document.body.innerText")
            undo = bool(re.search(r'undo|restore|put (it )?back|backup', txt, re.I))
            row[mode] = dict(asked=conf[:2], changed=changed[:8], undo_mentioned=undo)
            if mode == 'cancel' and changed: f.add('BUG', f"{tab} / '{label}': CANCEL still changed {changed[:6]}")
            if mode == 'confirm' and changed and not conf: f.add('review', f"{tab} / '{label}': changed {changed[:5]} with NO confirmation asked")
        report.append(row)
    json.dump(dict(report=report, findings=[list(x) for x in f]), open('/tmp/claude-0/crawl/p364.json', 'w'), indent=1, ensure_ascii=False)
for r in report: print(r['screen'], '|', r['button'], '| asked:', (r.get('confirm') or {}).get('asked') if isinstance(r.get('confirm'), dict) else r.get('confirm'), '| changed on confirm:', (r.get('confirm') or {}).get('changed') if isinstance(r.get('confirm'), dict) else '-')
bugs = [x for x in f if x[0] in ('BUG', 'JS-exception')]
print('findings:', len(f), 'bugs:', len(bugs)); sys.exit(1 if bugs else 0)
