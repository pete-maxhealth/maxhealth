"""Persona 101: every Library section has a 👁 like the other pages; hiding puts it under Filter ('Hidden:' list, counted on the button), it stays hidden after a reload,
Open all does not open it, choosing its chip still shows it, Show all / the + chip bring it back, and Default clears it."""
import sys; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("localStorage.setItem('mh_onboarded','1'); localStorage.setItem('mh_pills_open','1')"); page.reload(); page.wait_for_timeout(2000)
    page.evaluate("document.querySelectorAll('[id*=nboard]').forEach(e=>{ if(e.style) e.style.display='none'; })")
    page.evaluate("switchTab('log'); switchSubTab('log','library')"); page.wait_for_timeout(800)
    ev = page.evaluate
    st = lambda: ev("""()=>({eyes: document.querySelectorAll('#libraryScroll [data-libeye]').length,
      ing: getComputedStyle(document.getElementById('dashSection-libIngredients')).display, tools: getComputedStyle(document.getElementById('dashSection-libTools')).display,
      label: document.querySelector('#view-library .mh-pills-toolbar .main').textContent.trim(), strip: (document.getElementById('genericRestoreStrip-library')||{}).textContent||'',
      inPanel: !!document.querySelector('#view-library .mh-filter-panel #genericRestoreStrip-library'), store: localStorage.getItem('mh_library_hidden')})""")
    r = st()
    if r['eyes'] != 5: f.add('BUG', f'eyes {r["eyes"]} != 5')
    if 'hidden' in r['label']: f.add('BUG', 'hidden count shown with nothing hidden')
    ev("document.querySelector('[data-libeye=\"ingredients\"]').click()"); page.wait_for_timeout(300)
    r = st()
    if r['ing'] != 'none' or r['tools'] == 'none': f.add('BUG', f'hide wrong {r}')
    if 'Ingredients' not in r['strip'] or not r['inPanel']: f.add('BUG', f'Hidden list wrong {r}')
    if '1 hidden' not in r['label']: f.add('BUG', f'Filter label {r["label"]}')
    page.reload(); page.wait_for_timeout(2000); ev("switchTab('log'); switchSubTab('log','library')"); page.wait_for_timeout(800)
    if st()['ing'] != 'none': f.add('BUG', 'hidden section came back after reload')
    ev("mhSectionsAll(document.querySelector('#view-library .mh-pills-toolbar button:nth-of-type(2)'), true)"); page.wait_for_timeout(300)
    if ev("document.getElementById('lib-ingredients-wrap').style.display") == 'block' and ev("localStorage.getItem('mh_collapse_lib-ingredients')") == 'open': f.add('BUG', 'Open all opened a hidden section')
    ev("mhLibTopicSet('ingredients')"); page.wait_for_timeout(300)
    if st()['ing'] == 'none': f.add('BUG', "chip did not show a hidden section")
    ev("mhLibTopicSet('all')"); ev("document.querySelector('[data-libeye=\"tools\"]').click()"); page.wait_for_timeout(300)
    r = st()
    if '2 hidden' not in r['label'] or 'Show all' not in r['strip']: f.add('BUG', f'two hidden wrong {r}')
    ev("document.querySelector('#genericRestoreStrip-library button:not([data-showall])').click()"); page.wait_for_timeout(300)
    if '1 hidden' not in st()['label']: f.add('BUG', 'restore chip did not restore one')
    ev("mhLibShowAll()"); page.wait_for_timeout(300)
    r = st()
    if r['ing'] == 'none' or r['tools'] == 'none' or r['strip'].strip(): f.add('BUG', f'Show all failed {r}')
    ev("toggleLibraryHidden('az')")
    keys = ev("mhLayoutKeys(document.getElementById('view-library'))")
    if 'mh_library_hidden' not in keys: f.add('BUG', f'Default would not clear hidden {keys}')
    ev("mhDoResetLayout = mhDoResetLayout; localStorage.removeItem('mh_library_hidden'); mhLibTopicApply()"); page.wait_for_timeout(200)
    if st()['strip'].strip(): f.add('BUG', 'strip not cleared')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
