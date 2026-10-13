"""Persona 139: Language is its own Settings section (not buried in Profile): it has a title and folds, the card sits inside it, it belongs to the Me & targets filter, it can be found by settings search, and picking a language still works."""
import sys; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev = page.evaluate
    ev("switchTab('settings', document.getElementById('maintab-settings'))"); page.wait_for_timeout(900)
    if not ev("!!document.getElementById('title-set-language')"): f.add('BUG', 'no Language section title')
    if not ev("!!document.querySelector('#set-language-wrap #mhLangCard')"): f.add('BUG', 'language card not inside its own section')
    if ev("!!document.querySelector('#set-profile-wrap #mhLangCard')"): f.add('BUG', 'language card still inside Profile')
    if ev("document.querySelectorAll('#mhLangSel img').length") != 9: f.add('BUG', 'language buttons missing')
    ev("toggleSection('set-language','set-language-wrap','set-language-icon')"); page.wait_for_timeout(200); a = ev("document.getElementById('set-language-wrap').offsetParent !== null")
    ev("toggleSection('set-language','set-language-wrap','set-language-icon')"); page.wait_for_timeout(200); b = ev("document.getElementById('set-language-wrap').offsetParent !== null")
    if a == b: f.add('BUG', 'Language section does not fold')
    if 'set-language' not in ev("JSON.stringify(MH_TOPIC_SCOPES.manage.groups.me.keys)"): f.add('BUG', 'Language not in a Manage filter group')
    if not ev("SITE_SEARCH_SETTINGS.some(s => s.key === 'set-language')"): f.add('BUG', 'Language not in settings search')
    ev("mhLangSet('fr')"); page.wait_for_timeout(2200)
    if ev("mhLangCode()") != 'fr': f.add('BUG', 'picking French failed')
    ev("mhLangSet('en')"); page.wait_for_timeout(1500)
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
