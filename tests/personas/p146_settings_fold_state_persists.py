"""Persona 146: Settings section fold state survives a reload, a demo cycle, and hide/restore (the ordering code used to re-open folded bodies)."""
import sys; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
OPEN = """(()=>{const r=[];document.querySelectorAll('#view-manage [id$="-icon"]').forEach(i=>{const w=document.getElementById(i.id.replace('-icon','-wrap')); if(w && w.style.display!=='none') r.push(i.id.replace('-icon',''))}); return r})()"""
MISMATCH = """(()=>{let n=0;document.querySelectorAll('#view-manage [id$="-icon"]').forEach(i=>{const w=document.getElementById(i.id.replace('-icon','-wrap')); if(!w) return; if((w.style.display!=='none')!==/hide/.test(i.textContent)) n++}); return n})()"""
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    ev = page.evaluate
    ev("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev("switchTab('settings')"); page.wait_for_timeout(800)
    ev("""(()=>{document.querySelectorAll('#view-manage [id$="-icon"]').forEach(i=>{const w=document.getElementById(i.id.replace('-icon','-wrap')); if(!w) return; const k=i.id.replace('-icon',''); const want=(k==='set-profile'||k==='set-about'); if((w.style.display!=='none')!==want) toggleSection(k,w.id,i.id)})})()""")
    if sorted(ev(OPEN)) != ['set-about', 'set-profile']: f.add('BUG', f'setup failed {ev(OPEN)}')
    page.reload(); page.wait_for_timeout(1500); ev("switchTab('settings')"); page.wait_for_timeout(800)
    if sorted(ev(OPEN)) != ['set-about', 'set-profile']: f.add('BUG', f'fold state lost on reload: {ev(OPEN)}')
    if ev(MISMATCH): f.add('BUG', 'label and body out of sync after reload')
    ev("startDemoMode('zara')"); page.wait_for_timeout(800); ev("exitDemoMode()"); page.wait_for_timeout(800); ev("switchTab('settings')"); page.wait_for_timeout(500)
    if sorted(ev(OPEN)) != ['set-about', 'set-profile']: f.add('BUG', f'fold state lost after demo cycle: {ev(OPEN)}')
    # hide then restore a folded section keeps it folded
    ev("toggleGenericSectionHidden('manage','set-language')"); page.wait_for_timeout(300)
    ev("toggleGenericSectionHidden('manage','set-language')"); page.wait_for_timeout(300)
    if 'set-language' in ev(OPEN): f.add('BUG', 'hide then restore re-opened a folded section')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
