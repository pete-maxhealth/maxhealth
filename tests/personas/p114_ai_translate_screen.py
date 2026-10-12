"""Persona 114: AI 'Translate this screen'. Only offered when a non-English language is on; asks first and says how many phrases; the answers translate the screen, are kept on the phone and never override the shipped pack; failure stores nothing; Forget clears; no page errors."""
import sys, os; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings(); ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    def serve(route):
        name = route.request.url.split('/lang/')[1].split('?')[0]
        route.fulfill(status=200, content_type='application/json', body=open(os.path.join(ROOT, 'lang', name), 'rb').read())
    page.route('**/raw.githubusercontent.com/**/lang/*.json', serve)
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev = page.evaluate
    if ev("!!document.querySelector('#mhLangHdr span')"): f.add('BUG', 'sparkle shown in English')
    ev("mhLangOpen()")
    if ev("!!document.getElementById('mhLangAI')"): f.add('BUG', 'AI button offered in English')
    ev("document.getElementById('mhLangModal').remove()")
    page.evaluate("mhLangSet('fr')"); page.wait_for_timeout(2500)
    if not ev("!!document.querySelector('#mhLangHdr span')"): f.add('BUG', 'sparkle missing in French')
    ev("""(()=>{ const d=document.createElement('div'); d.id='zq'; d.textContent='Zebra quokka is not the best day'; d.style.cssText='position:fixed;top:300px;left:10px;'; document.body.appendChild(d);
      const e=document.createElement('div'); e.id='zk'; e.textContent='Your plan is on the day'; e.style.cssText='position:fixed;top:340px;left:10px;'; document.body.appendChild(e);
      window.__calls=0; window.callHealthAI=async (p)=>{ window.__calls++; const m=/\\[[\\s\\S]*\\]/.exec(p); const a=JSON.parse(m[0]); return {ok:true,text:JSON.stringify(a.map(x=>'XX '+x))}; }; })()""")
    ev("mhLangOpen()"); page.click('#mhLangAI'); page.wait_for_timeout(300)
    if 'phrases' not in ev("document.getElementById('mhLangModal').innerText"): f.add('BUG', 'no confirm step with count')
    if ev("window.__calls") != 0: f.add('BUG', 'sent before confirming')
    page.click('#mhLangGo'); page.wait_for_timeout(1200)
    if ev("window.__calls") < 1: f.add('BUG', 'AI never called')
    if ev("document.getElementById('zq').textContent") != 'XX Zebra quokka is not the best day': f.add('BUG', 'zq not translated')
    if 'Zebra quokka is not the best day' not in ev("localStorage.getItem('mh_lang_user_fr')||''"): f.add('BUG', 'not kept on phone')
    if ev("mhLangMerge({'Zebra quokka is not the best day':'PACK'})['Zebra quokka is not the best day']") != 'PACK': f.add('BUG', 'AI translation overrides the pack')
    # failure path stores nothing new
    ev("window.callHealthAI=async()=>({ok:false,error:'down'}); document.getElementById('zk').textContent='Another zebra is not for the day'")
    before = ev("localStorage.getItem('mh_lang_user_fr')")
    ev("mhLangOpen()"); page.click('#mhLangAI'); page.click('#mhLangGo'); page.wait_for_timeout(800)
    if ev("localStorage.getItem('mh_lang_user_fr')") != before: f.add('BUG', 'failed call changed stored translations')
    if ev("document.getElementById('zk').textContent") != 'Another zebra is not for the day': f.add('BUG', 'text changed after failure')
    ev("mhLangOpen()")
    if not ev("!!document.getElementById('mhLangForget')"): f.add('BUG', 'forget link missing')
    page.click('#mhLangForget'); page.wait_for_timeout(2000)
    if ev("localStorage.getItem('mh_lang_user_fr')"): f.add('BUG', 'forget did not clear')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
