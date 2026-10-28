"""Persona 118: Share must not silently behave like Export. With a share menu that refuses (not an abort) a fresh-tap modal appears and nothing downloads yet; its Share button calls share again; Cancel closes. With no share support the toast says so. Buttons are labelled Save to Downloads / Share…."""
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
    ev("saveSymptomDefs([{id:'a',name:'Headache',active:true}])")
    ev("document.body.insertAdjacentHTML('beforeend','<div id=tmpx>'+ (typeof mhBulkHtml==='function'?'':'')+'</div>')")
    html = ev("(()=>{const fn=Object.keys(window).find(k=>/Bulk.*Html|bulkActions/i.test(k)&&typeof window[k]==='function');return fn||''})()")
    ev("""window.__calls=0; window.__dl=0; navigator.canShare=()=>true;
      navigator.share=async()=>{window.__calls++; const e=new Error('x'); e.name='NotAllowedError'; throw e;};
      const oc=HTMLAnchorElement.prototype.click; HTMLAnchorElement.prototype.click=function(){ if(this.download) window.__dl++; };""")
    ev("document.body.insertAdjacentHTML('beforeend','<div id=\"bulkDsList\"><input type=checkbox class=bulkDs value=symptoms checked></div>')")
    ev("mhExportSelected(true)"); page.wait_for_timeout(1200)
    if not ev("!!document.getElementById('mhShareRetry')"): f.add('BUG', 'no retry modal after refused share')
    if ev("window.__dl") != 0: f.add('BUG', 'downloaded silently before the user chose')
    page.click('#mhShRGo'); page.wait_for_timeout(600)
    if ev("window.__calls") < 2: f.add('BUG', 'fresh-tap Share did not call share again')
    if ev("window.__dl") != 1: f.add('BUG', 'all refused should save to Downloads')
    ev("mhShareRetryModal(new File(['x'],'a.zip'),new Blob(['x']),'a.zip','x',[{name:'a.csv',text:'1,2',type:'text/csv'}])"); page.click('#mhShRNo')
    if ev("!!document.getElementById('mhShareRetry')"): f.add('BUG', 'cancel did not close')
    ev("navigator.share=undefined; window.__t=[]; const st=window.showToast; window.showToast=m=>{__t.push(m); return st(m);}"); ev("mhExportSelected(true)"); page.wait_for_timeout(1200)
    if "can't open the share menu" not in ' '.join(str(x) for x in ev("window.__t")): f.add('BUG', 'no honest toast when share unsupported')
    src = open('maxhealth.html').read()
    if 'Save to Downloads</button>' not in src or '📤 Send to another app…</button>' not in src: f.add('BUG', 'buttons not relabelled')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
