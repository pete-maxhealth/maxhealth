"""Persona 345 (v3.10.1232): Settings > Data. QR first and open; one main Save button plus Send; One zip/Separate files and setup-only live in More options; the Save/Send paragraph is behind a ?; a confirmation line stays after saving (zip and separate); import button says it previews first; Starter packs live on Manage > Setup. Everything-selected QR stays workable."""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
SHOT = '/tmp/claude-0/shots/'
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 430, 'height': 1100}, service_workers='block', accept_downloads=True)
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    p = ctx.new_page(); p.on('pageerror', lambda e: errs.append(str(e)[:200])); p.on('dialog', lambda d: d.accept()); ev = p.evaluate
    p.goto('http://localhost:5757/'); p.wait_for_timeout(1200); ev("state.onboarded=true; saveState()"); p.reload(); p.wait_for_timeout(1500)
    ev("switchTabById('settings'); switchSubTab('settings','import')"); p.wait_for_timeout(900)
    pos = ev("""(()=>{const q=document.getElementById('title-imp-qr'), e=document.getElementById('bulkDsList');
      return {qrFirst: !!(q && e && (q.compareDocumentPosition(e) & Node.DOCUMENT_POSITION_FOLLOWING)), qrOpen: getComputedStyle(document.getElementById('imp-qr-wrap')).display!=='none'}})()""")
    if not pos['qrFirst']: f.add('BUG', 'QR must come before Export')
    if not pos['qrOpen']: f.add('BUG', 'QR should be open by default')
    vis = ev("""(()=>{const r=document.querySelector('input[name=bulkFmt]'); const d=r&&r.closest('details'); const sp=[...document.querySelectorAll('button')].find(b=>/Share my setup only/.test(b.textContent));
      return {radioInFold: !!d && !d.open, setupInFold: !!(sp && sp.closest('details')), packsOnData: !![...document.querySelectorAll('#view-import button')].find(b=>/Starter packs/.test(b.textContent))}})()""")
    if not vis['radioInFold']: f.add('BUG', 'One zip / Separate files should sit in the closed More options fold')
    if not vis['setupInFold']: f.add('BUG', 'Share my setup only should sit in More options')
    if vis['packsOnData']: f.add('BUG', 'Starter packs should not be on the Data tab')
    if not ev("!![...document.querySelectorAll('button')].find(b=>/Send to another app/.test(b.textContent))"): f.add('BUG', 'Send to another app button missing')
    if not ev("document.getElementById('view-import').innerHTML.includes('bulksavehelp')"): f.add('BUG', 'Save/Send paragraph should be behind a ?')
    if ev("[...document.querySelectorAll('#view-import .settings-hint')].some(h=>/honours the zip/.test(h.textContent))"): f.add('BUG', 'old Save paragraph still shown')
    imp = ev("[...document.querySelectorAll('#view-import button')].map(b=>b.textContent.trim()).filter(t=>/preview/i.test(t))")
    if not imp: f.add('BUG', 'import button should say it opens a preview')
    ev("document.getElementById('title-imp-qr').scrollIntoView({block:'start'})"); p.wait_for_timeout(300)
    p.screenshot(path=SHOT + 'data_order.png')
    # save: one zip -> confirmation line stays
    ev("(()=>{mhStockTrack('Eggs',{base:'each',pack:6});let o=mhStockLoad();o.items.eggs.level=6;o.enabled=true;mhStockSave(o);})()")
    ev("mhBulkSelect(false); document.querySelectorAll('#bulkDsList .bulkDs').forEach(c=>{if(c.value==='stock')c.checked=true})")
    with p.expect_download(): ev("mhExportSelected(false)")
    p.wait_for_timeout(600)
    st = ev("(()=>{const e=document.getElementById('bulkExportStatus');return e&&e.style.display!=='none'?e.textContent:''})()")
    if 'Downloads' not in st or '.zip' not in st: f.add('BUG', f'zip save needs a confirmation line naming the file: {st!r}')
    # separate files
    ev("document.querySelector('input[name=bulkFmt][value=separate]').click()")
    with p.expect_download(): ev("mhExportSelected(false)")
    p.wait_for_timeout(2500)
    st2 = ev("document.getElementById('bulkExportStatus').textContent")
    if 'separate' not in st2: f.add('BUG', f'separate save needs its own confirmation line: {st2!r}')
    p.screenshot(path=SHOT + 'data_saved.png')
    # Starter packs on Manage > Setup
    ev("switchSubTab('settings','manage')"); p.wait_for_timeout(600)
    if not ev("!![...document.querySelectorAll('#set-setup-wrap button')].find(b=>/Starter packs/.test(b.textContent))"): f.add('BUG', 'Starter packs button missing from Manage > Setup')
    ev("document.getElementById('set-setup-wrap').scrollIntoView({block:'center'})"); p.wait_for_timeout(300); p.screenshot(path=SHOT + 'setup_packs.png')
    # everything-selected QR stays workable on a heavy history
    r = ev("""async()=>{const h=[];const d0=new Date();for(let i=1;i<=365;i++){const d=new Date(d0-i*864e5);const ds=String(d.getDate()).padStart(2,'0')+'/'+String(d.getMonth()+1).padStart(2,'0')+'/'+String(d.getFullYear()).slice(2);
      h.push({date:ds,mode:'standard',notes:'',log:[1,2,3,4,5].map(k=>({id:i*10+k,name:Math.random().toString(36).slice(2,12)+' '+Math.random().toString(36).slice(2,9),kcal:Math.round(100+Math.random()*600),protein:Math.round(Math.random()*50),fat:Math.round(Math.random()*40),carbs:Math.round(Math.random()*30),time:'0'+(k+4)+':00'})),totals:{kcal:2000,protein:150,fat:120,carbs:30}})}
      state.history=h;const o=mhxCollect({stock:true,list:true,recipes:true,library:true,history:true,routines:true,supplements:true,symptoms:true,treatments:true,labs:true,settings:true});const r=await mhxPack(o);r.frames.map(x=>MHQR.encodeText(x));return r.frames.length}""")
    if not (0 < r < 600): f.add('BUG', f'a year of unusually random history should need under 600 codes, got {r}')
    if errs: f.add('JS-exception', errs[0])
    b.close()
bad = any(s in ('BUG', 'JS-exception') for s, _ in f); print('BUGS' if bad else 'OK', len(f)); sys.exit(1 if bad else 0)
