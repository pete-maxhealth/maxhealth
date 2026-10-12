"""Persona 98: Library and Customise get the same toolbar (History keeps its own This Week / Month / All row, no toolbar) as every other page (first item, one per screen);
Customise has nothing to filter so it shows Open/Close/Default with no dead Filter button; Library section chips filter and persist;
Default puts the Library back; Supplements and Log (nothing to fold or filter) get no toolbar."""
import sys; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
def labels(page):
    return page.evaluate("""()=>{ const tbs=[...document.querySelectorAll('.mh-pills-toolbar')].filter(t=>t.getBoundingClientRect().height>0);
      return {n: tbs.length, first: tbs.map(t=>t.parentNode.firstElementChild===t), l: tbs.map(t=>[...t.querySelectorAll('button')].map(b=>b.textContent.replace(/[^A-Za-z ]/g,'').trim().split(' ')[0]).join(','))}; }""")
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("localStorage.setItem('mh_onboarded','1'); localStorage.setItem('mh_pills_open','1')"); page.reload(); page.wait_for_timeout(2000)
    page.evaluate("document.querySelectorAll('[id*=nboard]').forEach(e=>{ if(e.style) e.style.display='none'; })")
    for t, sub, want in [('log','hist',None), ('log','library','Filter,Open,Close,Default'), ('settings','customise','Open,Close,Default'), ('log','supplements',None), ('log','chat',None)]:
        page.evaluate(f"switchTab('{t}'); switchSubTab('{t}','{sub}')"); page.wait_for_timeout(900)
        r = labels(page)
        if want is None:
            if r['n']: f.add('BUG', f'{sub}: has a toolbar it should not ({r["l"]})')
            continue
        if r['n'] != 1: f.add('BUG', f'{sub}: {r["n"]} visible toolbars'); continue
        if not all(r['first']): f.add('BUG', f'{sub}: toolbar not first')
        if r['l'][0] != want: f.add('BUG', f'{sub}: order {r["l"][0]} != {want}')
    # library chips
    page.evaluate("switchTab('log'); switchSubTab('log','library')"); page.wait_for_timeout(700)
    r = page.evaluate("""()=>{ const vis=id=>{const e=document.getElementById(id); return !!e && !e.classList.contains('mh-grp-hide');};
      const ids=['dashSection-libRecipes','dashSection-libAZ','dashSection-libFood','dashSection-libTools','dashSection-libIngredients'];
      const allVis=ids.map(vis); mhLibTopicSet('tools'); const toolsVis=ids.map(vis); const lab=document.querySelector('#view-library .mh-pills-toolbar .main').textContent;
      const stored=localStorage.getItem('mh_topic_library'); return {allVis, toolsVis, lab, stored, chips:document.querySelectorAll('#mhTopicBar-library .mh-grp-chip').length}; }""")
    if r['chips'] != 6: f.add('BUG', f'library chips {r["chips"]}')
    if not all(r['allVis']): f.add('BUG', f'All should show every section {r}')
    if r['toolsVis'] != [False, False, False, True, False]: f.add('BUG', f'Tools chip wrong {r}')
    if 'Tools' not in r['lab'] or r['stored'] != 'tools': f.add('BUG', f'label/persist wrong {r}')
    page.reload(); page.wait_for_timeout(2000); page.evaluate("switchTab('log'); switchSubTab('log','library')"); page.wait_for_timeout(700)
    if page.evaluate("document.getElementById('dashSection-libFood').classList.contains('mh-grp-hide')") is not True: f.add('BUG', 'library filter lost on reload')
    # Open/Close all respects the group; Default restores
    page.evaluate("mhSectionsAll(document.querySelector('#view-library .mh-pills-toolbar button:nth-of-type(2)'), false)"); page.wait_for_timeout(300)
    page.evaluate("mhDoResetLayout(mhLayoutKeys(document.getElementById('view-library')))") if False else None
    keys = page.evaluate("mhLayoutKeys(document.getElementById('view-library'))")
    if 'mh_topic_library' not in keys: f.add('BUG', f'reset keys miss library filter {keys}')
    page.evaluate("localStorage.removeItem('mh_topic_library'); mhLibTopicApply()"); page.wait_for_timeout(200)
    if page.evaluate("document.querySelectorAll('#view-library .mh-grp-hide').length"): f.add('BUG', 'sections still hidden after clearing filter')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
