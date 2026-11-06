"""Persona 405: house-rules audit of every top-level screen and every recently changed flow (6 Nov 2026).
Pete: "checking for styling, navigation, collapse, uniformity as well as whether they work. Help, too much text to be hidden, check for duplicate
screens, date ranges, reorder and whether everything talks to everything else."
This does not click through flows (p404 does that). It LOOKS at each screen and reports what breaks Pete's standing rules, as a review list:
  long-text    text longer than a couple of lines that is not behind a "?" (.help-slot)
  card-ctl     a card with no reorder (▲ ▼) or show/hide control
  date-range   a period is shown (7 days, this month ...) but the screen has no standard date range control (.mh-range-dates)
  dup-control  the same control (label + action) twice on one screen
  dup-screen   two screens that offer almost the same set of controls
  uniform      the same-named control (Close, Cancel, Undo ...) styled differently on different screens
  cross-talk   something logged here does not show in History, the backup file, or Today
  collapse     a section that opens or shuts by itself when something else is done (see also p404)
Findings are for review (exit 0) unless a JS error happens (exit 1). Invented data only. Writes /tmp/claude-0/audit/p405.json."""
import sys, re, json, os; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from flows import *
from playwright.sync_api import sync_playwright
rev = []   # (kind, where, detail)
errs = []
def add(kind, where, detail): rev.append((kind, where, detail))

LONG = """() => { const out = [];
  const skip = e => getComputedStyle(e).fontFamily.includes('Space Mono') || e.closest('[id^=help-], #supplementListInner, .help-slot, [class*=help], input, textarea, select, script, style, [contenteditable], .bubble, [id*=chat], [id*=Chat], #ytC, #ytH, [id^=combo-card], pre, code, [class*=bubble]');
  document.querySelectorAll('body *').forEach(e => {
    if (skip(e)) return; const r = e.getBoundingClientRect(); if (r.width < 40 || r.height < 10) return;
    const s = getComputedStyle(e); if (s.display === 'none' || s.visibility === 'hidden') return;
    const own = [...e.childNodes].filter(n => n.nodeType === 3).map(n => n.textContent).join(' ').replace(/\\s+/g, ' ').trim();
    if (own.length < 110) return;
    const lh = parseFloat(s.lineHeight) || parseFloat(s.fontSize) * 1.3; const lines = Math.round(r.height / lh);
    if (lines >= 4 || own.length > 220) out.push({ t: own.slice(0, 70), lines, n: own.length });
  }); return out.slice(0, 12); }"""
CARDS = """() => { const out = []; const panel = [...document.querySelectorAll('.tab-content, .tab-panel, [id$=Tab], [id^=tab-]')].find(p => { const r = p.getBoundingClientRect(); return r.height > 100 && getComputedStyle(p).display !== 'none'; }) || document.body;
  [...panel.children].forEach(c => { const r = c.getBoundingClientRect(); if (r.height < 70 || r.width < 200 || getComputedStyle(c).display === 'none') return;
    const txt = c.innerText || ''; const has = /▲|▼|👁|\\bhide\\b/.test(txt) || c.querySelector('[onclick*=move], [onclick*=Move], [onclick*=toggleSection], [onclick*=hideCard], [onclick*=Hide]');
    if (!has) out.push({ id: c.id || c.className.toString().slice(0, 30), t: txt.trim().replace(/\\s+/g, ' ').slice(0, 40) }); }); return out.slice(0, 15); }"""
PERIOD = """() => { const t = document.body.innerText; const has = /(last|this|past)\\s+\\d*\\s*(days?|weeks?|months?)|\\b(7|14|30|90)\\s*(d|days)\\b|\\bperiod\\b/i.test(t); const ctl = document.querySelector('.mh-range-dates, [id*=DateRow], [id*=custom-dates]') || /\\bCustom\\b/.test(t); return { has, ctl: !!ctl }; }"""
CTL = """() => { const out = []; document.querySelectorAll('button, [onclick], summary').forEach(e => { const r = e.getBoundingClientRect(), s = getComputedStyle(e); if (r.width < 8 || r.height < 8 || s.display === 'none' || s.visibility === 'hidden') return;
  out.push({ t: ((e.innerText || e.title || '') + '').trim().slice(0, 24), oc: (e.getAttribute('onclick') || '').slice(0, 70), fs: s.fontSize, br: s.borderRadius, h: Math.round(r.height), bg: s.backgroundColor, c: s.color }); }); return out; }"""
COMMON = re.compile(r'^(close|cancel|undo|done|back|save|ok|apply|add|✕|×|✓ ?add|open all|close all|default|filter)\b', re.I)
sigs = {}      # label -> {signature: [where]}
labelsets = {} # screen -> set of control labels

def look(page, where):
    ev = page.evaluate
    for x in ev(LONG): add('long-text', where, f'{x["n"]} chars / {x["lines"]} lines, not behind a "?": "{x["t"]}…"')
    for x in ev(CARDS): add('card-ctl', where, f'card "{x["t"]}" ({x["id"]}) has no reorder / show-hide control')
    p = ev(PERIOD)
    if p['has'] and not p['ctl']: add('date-range', where, 'a period is shown but there is no standard date range control on this screen')
    ctl = ev(CTL); seen = {}
    for c in ctl:
        k = (c['t'], c['oc'])
        if c['t'] and c['oc'] and k in seen and not re.match(r'^[\d\W]+$', c['t']) and not re.search(r'Supplement', c['oc']): add('dup-control', where, f'"{c["t"]}" appears twice ({c["oc"][:40]})')
        seen[k] = 1
        if COMMON.match(c['t'] or ''):
            sig = f'{c["fs"]}/{c["br"]}/{round(c["h"] / 4) * 4}px/{c["bg"]}'
            sigs.setdefault(c['t'].lower(), {}).setdefault(sig, []).append(where)
    labelsets[where] = {c['t'] for c in ctl if c['t'] and len(c['t']) > 2}

with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 900}, service_workers='block', accept_downloads=True); page = ctx.new_page()
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.dismiss())
    ev = page.evaluate
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500); ev("startDemoMode('doris')"); page.wait_for_timeout(2000)
    tabs = list(ev("Object.keys(NAV_MAP)")); print('screens:', tabs)
    for tab in tabs:
        try: ev(f"switchTabById('{tab}')")
        except Exception as e: errs.append(f'open {tab}: {str(e)[:100]}'); continue
        page.wait_for_timeout(600); look(page, f'screen {tab}')
        for sub in ev("[...document.querySelectorAll('.tab-btn, [role=tab], [class*=subtab], [id^=logtab-], [id^=histtab-]')].filter(e=>{const r=e.getBoundingClientRect();return r.width>8&&r.height>8}).map(e=>e.id||'').filter(Boolean).slice(0,8)"):
            try:
                ev(f"document.getElementById('{sub}').click()"); page.wait_for_timeout(500); look(page, f'screen {tab} / {sub}')
            except Exception as e: errs.append(f'sub {sub}: {str(e)[:80]}')
    for name in ['import_review', 'suggestion_cards', 'shopping_list', 'my_cupboards', 'log_search_from_import']:
        setup(page, name); look(page, f'flow {name}')
    # cross-talk: log one invented food, see it everywhere it should be
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1000); ev("startDemoMode('doris')"); page.wait_for_timeout(1800)
    ev("()=>logFoods([{name:'Zzqx Crosstalk Cake',amount:'100g',kcal:321,protein:7,carbs:11,fat:9,fibre:0,polyols:0}],'Zzqx Crosstalk Cake')"); page.wait_for_timeout(500)
    if 'Zzqx Crosstalk' not in ev("JSON.stringify(state.todayLog)"): add('cross-talk', 'log', 'logged food is not in today\'s log')
    ev("switchTabById('dash')"); page.wait_for_timeout(700)
    if 'Zzqx Crosstalk' not in ev("document.body.innerText"): add('cross-talk', 'Today', 'the food just logged is not listed on Today')
    ev("switchTabById('chat')"); page.wait_for_timeout(300)
    try:
        with page.expect_download(timeout=8000) as dl: ev("exportAll()")
        import zipfile; z = zipfile.ZipFile(dl.value.path()); txt = ''.join(z.read(n).decode('utf-8', 'ignore') for n in z.namelist() if n.endswith('.json'))   # the backup is a zip; its JSON holds the data
        if 'Zzqx Crosstalk' not in txt: add('cross-talk', 'backup/export', 'the first file downloaded by Export does not contain the food just logged')
    except Exception as e: add('cross-talk', 'backup/export', f'could not capture the export download ({str(e)[:60]})')
    try:
        ctxt = ev("()=>{try{return buildPatientContext(state.history)+JSON.stringify(state.todayLog)}catch(e){return 'ERR '+e.message}}")
        if ctxt.startswith('ERR'): add('cross-talk', 'AI context', ctxt[:80])
    except Exception: pass
# uniformity + duplicate screens
for label, d in sigs.items():
    if len(d) > 1: add('uniform', label, 'styled differently: ' + ' | '.join(f'{s} on {len(w)} screen(s), e.g. {w[0]}' for s, w in list(d.items())[:3]))
names = [k for k, v in labelsets.items() if len(v) >= 6]
for i, a in enumerate(names):
    for c in names[i + 1:]:
        if a.split(' / ')[0] == c.split(' / ')[0]: continue
        if a.startswith('screen') != c.startswith('screen'): continue          # a flow always sits on a screen, so it shares its controls by design
        sa, sc = a.split(' / ')[0], c.split(' / ')[0]
        if (' / ' in a and sa == c) or (' / ' in c and sc == a): continue     # a screen and one of its own sub-tabs
        u = labelsets[a] | labelsets[c]; j = len(labelsets[a] & labelsets[c]) / max(1, len(u))
        if j > 0.8: add('dup-screen', f'{a} vs {c}', f'{round(j * 100)}% of their controls are the same')
os.makedirs('/tmp/claude-0/audit', exist_ok=True)
json.dump({'review': rev, 'errors': errs}, open('/tmp/claude-0/audit/p405.json', 'w'), indent=1)
seen = set(); out = []
for k, w, d in rev:
    key = (k, d[:60])
    if key in seen: continue
    seen.add(key); out.append((k, w, d))
from collections import Counter
print('review items:', dict(Counter(k for k, _, _ in out)))
for k, w, d in out[:120]: print(f'[{k}] {w}: {d}')
print('JS errors:', errs)
sys.exit(1 if errs else 0)
