"""Persona 111: language packs. English stays default and untouched; choosing Spanish translates screens, placeholders and later renders; the 🌐 button
and ?lang=en always return to English; speech language and the AI note follow the choice; a missing file leaves English; every lang file is valid."""
import sys, json, os, glob; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
for c in ['es', 'de', 'fr', 'tr', 'pt', 'it', 'pl', 'nl']:
    p = os.path.join(ROOT, 'lang', c + '.json')
    if not os.path.exists(p): f.add('BUG', f'missing lang/{c}.json'); continue
    d = json.load(open(p, encoding='utf-8'))
    if len(d) < 500: f.add('BUG', f'{c} too small {len(d)}')
    if any((not isinstance(k, str)) or (not isinstance(v, str)) or not v.strip() for k, v in d.items()): f.add('BUG', f'{c} bad entries')
    if d.get('Today') in (None, 'Today'): f.add('BUG', f'{c} Today not translated')
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 800}, service_workers='block'); page = ctx.new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    def serve(route):
        name = route.request.url.split('/lang/')[1].split('?')[0]
        path = os.path.join(ROOT, 'lang', name)
        if os.path.exists(path): route.fulfill(status=200, content_type='application/json', body=open(path, 'rb').read())
        else: route.fulfill(status=404, body='')
    page.route('**/raw.githubusercontent.com/**/lang/*.json', serve)
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev = page.evaluate
    ob_lang = ev("!!document.getElementById('mhLangObSel')")
    if not ob_lang: f.add('BUG', 'onboarding language picker missing')
    # v3.10.1095: collapsed into one Language button; the nine flags open on tap
    if not ev("!!document.getElementById('mhLangObBtn')"): f.add('BUG', 'onboarding Language button missing')
    if ev("getComputedStyle(document.getElementById('mhLangObSel')).display") != 'none': f.add('BUG', 'language list should start closed')
    ev("document.getElementById('mhLangObBtn').click()")
    if ev("getComputedStyle(document.getElementById('mhLangObSel')).display") == 'none': f.add('BUG', 'Language button did not open the list')
    if ev("document.querySelectorAll('#mhLangObSel img').length") != 9: f.add('BUG', 'onboarding list should hold 9 languages')
    if ev("mhLangCode()") != 'en': f.add('BUG', 'default not English')
    if 'today' not in ev("document.getElementById('maintab-today').textContent").lower(): f.add('BUG', 'English tab changed')
    if ev("!!document.getElementById('mhLangFab')"): f.add('BUG', 'language button in English mode')
    if not ev("!!document.querySelector('#mhLangHdr img')"): f.add('BUG', 'header flag missing')
    if ev("document.querySelectorAll('#mhLangSel img').length") != 9: f.add('BUG', 'settings flag buttons missing')
    if not ev("!!document.getElementById('mhLangSel')"): f.add('BUG', 'settings language select missing')
    if ev("mhSpeechLang()") != 'en-GB' or ev("mhLangAINote()") != '': f.add('BUG', 'English speech/AI note')
    # numbered sentences (patterns)
    page.evaluate("mhLangSet('fr')"); page.wait_for_timeout(2500)
    r = ev("""(()=>{ const d=document.createElement('div'); d.textContent="🚶 ~104min walk would close today's 567kcal gap"; document.body.appendChild(d); mhLangWalk(d); const a=d.textContent;
      const e=document.createElement('div'); e.textContent='Every tag zzz logged'; document.body.appendChild(e); mhLangWalk(e); const b=e.textContent; d.remove(); e.remove(); return [a,b]; })()""")
    if '104 min' not in r[0] or '567 kcal' not in r[0]: f.add('BUG', f'pattern not translated {r[0]!r}')
    if r[1] != 'Every tag zzz logged': f.add('BUG', f'short pattern hijacked text {r[1]!r}')
    page.evaluate("mhLangSet('en')"); page.wait_for_timeout(2000)
    # switch to Spanish
    page.evaluate("mhLangSet('es')"); page.wait_for_timeout(2500)
    if ev("mhLangCode()") != 'es': f.add('BUG', 'Spanish not stored')
    tab = ev("document.getElementById('maintab-today').textContent.trim()")
    if tab.lower().replace('🏠','').strip() != 'hoy': f.add('BUG', f'tab text {tab!r}')
    if 'ajustes' not in ev("document.getElementById('maintab-settings').textContent").lower(): f.add('BUG', 'settings tab')
    ph = ev("document.getElementById('chatInput').placeholder")
    if 'Registra' not in ph: f.add('BUG', 'placeholder ' + ph)
    if ev("document.documentElement.lang") != 'es': f.add('BUG', 'html lang')
    if ev("mhSpeechLang()") != 'es-ES': f.add('BUG', 'speech lang')
    if 'Spanish' not in ev("mhLangAINote()"): f.add('BUG', 'AI note')
    if not ev("!!document.getElementById('mhLangFab')"): f.add('BUG', 'language button missing')
    # dynamic render gets translated
    ev("switchTab('settings', document.getElementById('maintab-settings'))"); page.wait_for_timeout(800)
    ev("showToast('Plan removed. Edit what you actually ate and send it.')")
    ev("(()=>{ const d=document.createElement('div'); d.id='dyn'; d.textContent='Cancel'; document.body.appendChild(d); })()"); page.wait_for_timeout(300)
    if ev("document.getElementById('dyn').textContent") != 'Cancelar': f.add('BUG', 'dynamic node not translated')
    # data-nolang + untranslated stays English
    ev("(()=>{ const d=document.createElement('div'); d.id='dyn2'; d.textContent='zzz not in dictionary'; document.body.appendChild(d); })()"); page.wait_for_timeout(200)
    if ev("document.getElementById('dyn2').textContent") != 'zzz not in dictionary': f.add('BUG', 'untranslated text changed')
    # the way back
    page.click('#mhLangFab'); page.wait_for_timeout(300)
    if 'back to english' not in ev("document.getElementById('mhLangModal').innerText").lower(): f.add('BUG', 'modal not in English')
    page.click('.mh-lang-opt[data-c="en"]'); page.wait_for_timeout(2000)
    if ev("mhLangCode()") != 'en' or 'today' not in ev("document.getElementById('maintab-today').textContent").lower(): f.add('BUG', 'did not return to English')
    # ?lang=de then ?lang=en
    page.goto('http://localhost:5757/?lang=de'); page.wait_for_timeout(2500)
    if 'heute' not in ev("document.getElementById('maintab-today').textContent").lower(): f.add('BUG', 'German via URL')
    page.goto('http://localhost:5757/?lang=en'); page.wait_for_timeout(2000)
    if ev("mhLangCode()") != 'en': f.add('BUG', '?lang=en')
    # offline / missing file: stays English, no crash
    ctx2 = b.new_context(viewport={'width': 390, 'height': 800}, service_workers='block'); p2 = ctx2.new_page()
    p2.route('**/raw.githubusercontent.com/**', lambda r: r.abort())
    p2.route('**/lang/fr.json', lambda r: r.abort())   # since v1063 the app's own copy is tried first, so block it too for the 'no file anywhere' case
    p2.goto('http://localhost:5757/?lang=fr'); p2.wait_for_timeout(2500)
    if 'today' not in p2.evaluate("document.getElementById('maintab-today').textContent").lower(): f.add('BUG', 'missing file should stay English')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
