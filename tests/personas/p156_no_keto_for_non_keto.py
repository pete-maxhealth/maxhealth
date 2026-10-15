"""Persona 156 (v3.10.1050): non-keto personas never SEE keto/ketone/ketosis wording on the main screens (except inside the Go Keto! row),
and a keto persona still does. Catches new keto text added without a isKetogenicCondition() gate."""
import sys, re; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
rx = re.compile(r'[^.\n]{0,50}\b(keto\w*|ketone\w*|ketosis|GKI)\b[^.\n]{0,50}', re.I)
VIEWS = [("today", "switchTab('today',document.getElementById('maintab-today'))"), ("log", "switchTab('log',document.getElementById('maintab-log'))"),
  ("library", "switchSubTab('log','library',document.getElementById('logtab-library'))"), ("history", "switchSubTab('log','hist',document.getElementById('logtab-hist'))"),
  ("insights", "switchTab('insights',document.getElementById('maintab-insights'))"), ("reports", "switchSubTab('insights','reports',document.getElementById('insightstab-reports'))"),
  ("settings", "switchTab('settings',document.getElementById('maintab-settings'))"), ("customise", "switchSubTab('settings','customise',document.getElementById('settingstab-customise'))"),
  ("import", "switchSubTab('settings','import',document.getElementById('settingstab-import'))")]
JS = """(()=>{const o=[];document.querySelectorAll('body *').forEach(e=>{if(e.children.length===0&&e.offsetParent!==null&&!e.closest('#mhGoKetoRow')){const t=(e.innerText||'').trim();if(t)o.push(t)}});return o.join('\\n')})()"""
def scan(ev, page, pid):
    ev(f"startDemoMode('{pid}')"); page.wait_for_timeout(2200); hits = []
    for name, js in VIEWS:
        try: ev(js)
        except Exception as e: f.add('BUG', f'{pid}/{name}: cannot open ({str(e)[:50]})'); continue
        page.wait_for_timeout(450)
        for m in rx.finditer(ev(JS)): hits.append((name, m.group(0).strip()))
    return hits

def ai_prompts(ev, page, pid):
    ev(f"startDemoMode('{pid}')"); page.wait_for_timeout(2200)
    ev("window.__b=[]; const f0=window.fetch; window.fetch=function(u,o){ try{ if(o&&o.body) window.__b.push(String(o.body)); }catch(e){} return f0.apply(this,arguments); }")
    steps = ["startNextMealFlow()", "startBalanceMacrosFlow()", "openRecipeDiscoverModal(); document.getElementById('recipeDiscoverInput').value='a quick dinner'; submitRecipeDiscover()",
             "switchTab('log',document.getElementById('maintab-log')); document.getElementById('chatInput') && (document.getElementById('chatInput').value='what do I still need today?'); sendChat()"]
    for js in steps:
        try: ev(js)
        except Exception as e: pass
        page.wait_for_timeout(1800)
    return ev("window.__b")

with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page()
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    for pid in ('alex', 'barry', 'karen', 'doris'):
        for name, t in scan(ev, page, pid): f.add('BUG', f'{pid}/{name}: keto wording shown to a non-keto user: "{t}"')
    for pid in ('alex', 'karen'):
        bs = ai_prompts(ev, page, pid)
        if not bs: f.add('BUG', f'{pid}: no AI requests captured, test cannot see prompts')
        for b in bs:
            m = re.search(r'.{0,60}\b(keto\w*|ketosis|ketone\w*)\b.{0,60}', b, re.I)
            if m: f.add('BUG', f'{pid}: AI prompt mentions keto: "{m.group(0)}"')
    if not scan(ev, page, 'raj'): f.add('BUG', 'keto persona (raj) sees no keto wording at all')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
