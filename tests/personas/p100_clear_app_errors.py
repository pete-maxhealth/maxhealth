"""Persona 100: the System health note about an app error can be cleared with 'Mark app errors as fixed'; it comes back as New if the error repeats;
the link only shows when there is an app error to clear."""
import sys, json, urllib.request; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
def post(path, body): 
    r = urllib.request.Request('http://localhost:5757' + path, data=json.dumps(body).encode(), headers={'Content-Type': 'application/json'}); return urllib.request.urlopen(r).read()
def sc(): return json.loads(urllib.request.urlopen('http://localhost:5757/selfcheck').read())
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("localStorage.setItem('mh_onboarded','1')"); page.reload(); page.wait_for_timeout(1500)
    page.evaluate("updateSelfCheckDisplay()"); page.wait_for_timeout(600)
    if 'Mark app errors' in page.evaluate("document.getElementById('selfCheckDisplay').textContent"): f.add('BUG', 'clear link shown with no errors')
    post('/log-client-error', {'sig': 'TypeError:x:1', 'kind': 'error', 'msg': "TypeError: Cannot read properties of null (reading 'style')", 'src': 'a', 'line': 1, 'v': 'v3.10.974'})
    if not any('app error' in i['text'] for i in sc()['items']): f.add('BUG', 'error not reported by selfcheck')
    page.evaluate("updateSelfCheckDisplay()"); page.wait_for_timeout(600)
    if 'Mark app errors as fixed' not in page.evaluate("document.getElementById('selfCheckDisplay').textContent"): f.add('BUG', 'clear link missing')
    page.evaluate("mhClearAppErrors()"); page.wait_for_timeout(500)
    page.evaluate("(()=>{ const b=[...document.querySelectorAll('button')].filter(b=>b.textContent.trim()==='Clear' && b.offsetParent); if(b[0]) b[0].click(); })()"); page.wait_for_timeout(1200)
    if any('app error' in i['text'] for i in sc()['items']): f.add('BUG', 'error still reported after clearing')
    if 'Mark app errors' in page.evaluate("document.getElementById('selfCheckDisplay').textContent"): f.add('BUG', 'link still showing after clearing')
    post('/log-client-error', {'sig': 'TypeError:x:1', 'kind': 'error', 'msg': 'again', 'src': 'a', 'line': 1, 'v': 'v3.10.978'})
    if not any('New app error' in i['text'] for i in sc()['items']): f.add('BUG', 'repeat not recorded as new')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
