"""Collect visible English phrases on every main screen (demo persona) that are not in the language packs. Read-only: writes /tmp/sweep/untranslated_all.json. Run from the repo root."""
import sys, json, re; sys.path.insert(0, 'tests/personas')
from harness import *
from playwright.sync_api import sync_playwright
have = set(json.load(open('lang/es.json', encoding='utf-8')))
seen = {}
JS = """() => { const out = new Set(); const add = s => { s = (s||'').replace(/\\s+/g,' ').trim(); if (s.length > 2) out.add(s); };
 const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
 while (w.nextNode()) { const p = w.currentNode.parentElement; if (!p || /SCRIPT|STYLE|NOSCRIPT/.test(p.tagName)) continue; if (p.offsetParent === null && p.tagName !== 'OPTION') continue; add(w.currentNode.nodeValue); }
 document.querySelectorAll('[placeholder],[title],[aria-label]').forEach(e => { if (e.offsetParent===null) return; add(e.getAttribute('placeholder')); add(e.getAttribute('title')); add(e.getAttribute('aria-label')); });
 return [...out]; }"""
def grab(page, tag):
    for s in page.evaluate(JS):
        if re.search(r'[A-Za-z]{4}', s) and s not in have and not re.fullmatch(r'[\W\d\sA-Za-z]{0,3}', s): seen.setdefault(s, tag)
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); ev = page.evaluate; errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:150])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/?demo=alex'); page.wait_for_timeout(3500)
    ev("document.getElementById('onboardingOverlay')?.remove()")
    for t in ('dash','supplements','move','chat','hist','library','shop','trends','stats','reports','manage','customise','import'):
        try:
            ev(f"switchTabById('{t}')"); page.wait_for_timeout(700); grab(page, t)
            # open every collapsed <details> and section toggle on this screen, then grab again
            ev("document.querySelectorAll('details').forEach(d=>d.open=true)"); page.wait_for_timeout(300); grab(page, t + ' (open)')
        except Exception as e: print('skip', t, str(e)[:80])
    print('page errors', errs[:3])
json.dump(seen, open('/tmp/sweep/untranslated_all.json', 'w'), ensure_ascii=False, indent=1)
print(len(seen), 'untranslated phrases')
