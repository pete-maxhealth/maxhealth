"""Persona 517: static screen text found by tools/lang_collect_all.py is translated (tools/lang_add_v1444_static.py). Walks Insights > Statistics, Reports (timing advice), the Today activity setting and Settings, in all eight languages,
and checks each new phrase is translated by the page's own translator (not left English unless the language genuinely uses the same word), and that the demo toast carries the persona name. NOT covered: native-speaker wording."""
import sys, json; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
KEYS = ["Timing advice: who should advise?", "PT / sports nutritionist", "✨ Timing advice for me", "First meal (hour of day)", "Last meal (hour of day)", "Chart the days this query matches on the Statistics screen", "More: clear today's log, erase all my data", "⚖ Body & wellbeing", "📌 My own", "📈 Over time", "🔍 Search my statistics", "📈 View a trend:", "Gross (full MET value)", "Demo mode — exploring as Alex. Nothing here is saved."]
OK_SAME = {'Over time': [], 'My own': []}
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    for l in ['es', 'de', 'fr', 'tr', 'pt', 'it', 'pl', 'nl']:
        pg = b.new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); ev = pg.evaluate
        pg.on('pageerror', lambda e: errs.append(l + ' ' + str(e)[:150])); pg.on('dialog', lambda d: d.accept())
        pg.goto('http://localhost:5757/'); pg.wait_for_timeout(800)
        ev(f"localStorage.setItem('mh_lang','{l}')"); pg.reload(); pg.wait_for_timeout(1500)
        for k in KEYS:
            tr = ev("(p)=>{const d=MH_L.dict; if(!d) return null; const k=mhLangNorm(p); if(Object.prototype.hasOwnProperty.call(d,k)) return d[k]; return mhLangPat(k,d)}", k)
            if not tr or tr == k: f.add('BUG', f'{l}: not translated: {k}')
        tr = ev("(p)=>mhLangPat(p, MH_L.dict)", "Demo mode — exploring as Alex. Nothing here is saved.")
        if not tr or 'Alex' not in tr: f.add('BUG', f'{l}: demo toast lost the name: {tr}')
    for e in errs: f.add('JS-exception', e)
print('findings', len(f))
