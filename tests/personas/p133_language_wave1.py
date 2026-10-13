"""Persona 133: wave-1 language packs (Portuguese-BR, Italian, Polish, Dutch). Files exist and cover almost all English keys, {n} placeholders survive, the picker lists nine languages with flags, and switching to each new language translates the tabs and sets speech/html lang."""
import sys, json, os, re; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
en_union = set()
for c in ['es', 'de', 'fr', 'tr']: en_union |= set(json.load(open(os.path.join(ROOT, 'lang', c + '.json'), encoding='utf-8')))
ph = lambda s: sorted(re.findall(r'\{\d+\}', s))
for c in ['pt', 'it', 'pl', 'nl']:
    d = json.load(open(os.path.join(ROOT, 'lang', c + '.json'), encoding='utf-8'))
    miss = len(en_union - set(d))
    if miss > 60: f.add('BUG', f'{c} misses {miss} keys')
    for k, v in d.items():
        if ph(k) != ph(v): f.add('BUG', f'{c} placeholder mismatch {k[:40]!r}'); break
    if d.get('Today') in (None, 'Today'): f.add('BUG', f'{c} Today untranslated')
want = {'pt': ('pt-BR', 'hoje'), 'it': ('it-IT', 'oggi'), 'pl': ('pl-PL', 'dzi'), 'nl': ('nl-NL', 'vandaag')}
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    def serve(route):
        p = os.path.join(ROOT, 'lang', route.request.url.split('/lang/')[1].split('?')[0])
        if os.path.exists(p): route.fulfill(status=200, content_type='application/json', body=open(p, 'rb').read())
        else: route.fulfill(status=404, body='')
    page.route('**/raw.githubusercontent.com/**/lang/*.json', serve)
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev = page.evaluate
    if ev("MH_LANGS.length") != 9: f.add('BUG', 'not nine languages')
    if ev("MH_LANGS.filter(l=>!MH_FLAG_SVG[l.code]).length"): f.add('BUG', 'a language lacks a flag')
    for c, (sp, tab) in want.items():
        ev(f"mhLangSet('{c}')"); page.wait_for_timeout(2200)
        if ev("mhSpeechLang()") != sp: f.add('BUG', f'{c} speech {ev("mhSpeechLang()")}')
        if ev("document.documentElement.lang") != c: f.add('BUG', f'{c} html lang')
        t = ev("document.getElementById('maintab-today').textContent").lower()
        if tab not in t: f.add('BUG', f'{c} tab text {t!r}')
    ev("mhLangSet('en')"); page.wait_for_timeout(1500)
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
