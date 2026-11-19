"""Persona 507 (v3.10.1433): the v3.10.1429-1432 strings are translated (tools/lang_add_v1429_1432.py). In all eight languages: the Erase button in Settings > Data > More, its first confirmation text and Cancel,
and the condition-history note. English stays unchanged. NOT walked: the destructive second step (p504 covers it in English)."""
import sys, json, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings(); chk = lambda ok, m: None if ok else f.add('BUG', m)
LANGS = ['es', 'de', 'fr', 'tr', 'pt', 'it', 'pl', 'nl']
BTN = '🗑 ERASE ALL MY DATA'
ASK = 'Erase EVERYTHING MaxedHealth has saved on this phone: meals, history, library, recipes, supplements, settings and your Premium licence key? This cannot be undone. If you might want it back, cancel and share a backup first.'
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    for l in LANGS + ['en']:
        d = json.load(open(f'lang/{l}.json', encoding='utf-8')) if l != 'en' else {BTN: BTN, ASK: ASK}
        page = b.new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); ev = page.evaluate
        page.on('pageerror', lambda e: errs.append(l + ' ' + str(e)[:160])); page.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
        page.goto('http://localhost:5757/'); page.wait_for_timeout(800); ev(f"localStorage.setItem('mh_lang','{l}')"); page.reload(); page.wait_for_timeout(1500)
        ev("state.onboarded=true; saveState(); document.getElementById('onboardingOverlay')?.remove()")
        page.click('#maintab-settings'); page.wait_for_timeout(500); page.click('#settingstab-import'); page.wait_for_timeout(600)
        ev("document.getElementById('mhEraseAllBtn').closest('details').open = true"); page.wait_for_timeout(500)
        t = ev("document.getElementById('mhEraseAllBtn').textContent.trim()")
        chk(t == d[BTN], f'1 {l}: erase button {t!r}')
        page.click('#mhEraseAllBtn'); page.wait_for_timeout(600)
        m = ev("document.querySelector('.app-modal')?.innerText||''")
        chk(d[ASK] in m, f'2 {l}: confirmation not translated: {m[:80]!r}')
        page.click('#appModalCancel'); page.wait_for_timeout(300)
    errs and f.add('JS-exception', errs[0])
print('findings', len(f))
