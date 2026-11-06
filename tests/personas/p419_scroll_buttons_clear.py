"""Persona 419: the floating up / down scroll buttons no longer cover values (v3.10.1315). Pete 6 Nov: they hid the right-hand end of the sleep figures on Trends.
Covers: at 400 and 1280 wide, on Trends, Today and Reports, scrolled down, no visible text sits under either button (screen-edge tabs), both buttons still work (up returns to the top), no page errors. Demo persona."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
HIT = """()=>{const out=[]; for(const id of ['globalScrollTopBtn','globalScrollBottomBtn']){const b=document.getElementById(id); if(!b||getComputedStyle(b).display==='none') continue; const r=b.getBoundingClientRect();
 const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT); let n; while(n=w.nextNode()){ if(!n.textContent.trim()) continue; const p=n.parentElement; if(!p||p===b||b.contains(p)) continue; const cs=getComputedStyle(p); if(cs.visibility==='hidden'||cs.display==='none') continue;
  const rg=document.createRange(); rg.selectNodeContents(n); for(const q of rg.getClientRects()){ if(q.width<2) continue; if(q.right>r.left+1&&q.left<r.right&&q.bottom>r.top&&q.top<r.bottom){ const e=document.elementFromPoint(q.left+q.width/2,q.top+q.height/2); if(e&&!b.contains(e)&&e!==document.body&&p.offsetParent!==null) out.push(id+' over "'+n.textContent.trim().slice(0,24)+'"'); } } } }
 return out.slice(0,5)}"""
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    for w in (400, 1280):
        page = b.new_context(viewport={'width': w, 'height': 800}, service_workers='block').new_page(); ev = page.evaluate
        page.on('pageerror', lambda e: errs.append(str(e)[:200]))
        page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
        ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay').style.display='none'"); ev("startDemoMode('doris')"); page.wait_for_timeout(1500)
        for tab in ('insights', 'today', 'log'):
            ev(f"document.getElementById('maintab-{tab}').click()"); page.wait_for_timeout(700)
            for y in (500, 1400):
                ev(f"(()=>{{const s=document.getElementById(window._activeScrollContainerId); if(s){{s.scrollTop={y}; s.dispatchEvent(new Event('scroll'))}}}})()"); page.wait_for_timeout(400)
                for h in ev(HIT): f.add('BUG', f'{w} {tab} y{y}: {h}')
        ev("document.getElementById('maintab-insights').click()"); page.wait_for_timeout(600)
        ev("(()=>{const s=document.getElementById(window._activeScrollContainerId); s.scrollTop=900; s.dispatchEvent(new Event('scroll'))})()"); page.wait_for_timeout(400)
        try:
            page.click('#globalScrollTopBtn', timeout=3000); page.wait_for_timeout(1200)
            if ev("document.getElementById(window._activeScrollContainerId).scrollTop") > 20: f.add('BUG', f'{w}: up button did not return to the top')
        except Exception as e: f.add('BUG', f'{w}: up button not clickable {str(e)[:60]}')
        page.context.close()
    if errs: f.add('BUG', f'page errors {errs[:3]}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
