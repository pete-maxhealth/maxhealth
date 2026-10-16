"""Persona 185 (v3.10.1082): quick colour / chart type on each statistic card, custom colour, hostile colour refused."""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
bad=[]
def check(n, ok, info=''):
    print(('PASS ' if ok else 'FAIL ')+n+(f'  {info}' if info and not ok else ''))
    if not ok: bad.append(n)
with fresh_server() as root, sync_playwright() as pw:
    br=pw.chromium.launch(); ctx=br.new_context(viewport={'width':430,'height':900},service_workers='block'); page=ctx.new_page()
    errs=[]; page.on('pageerror',lambda e:errs.append(str(e)[:200])); page.on('dialog',lambda d:d.accept())
    page.route(re.compile(r'^https?://(?!localhost)'),lambda r:r.abort())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200)
    page.evaluate("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev=page.evaluate
    ev("""(()=>{const d=n=>{const x=new Date();x.setDate(x.getDate()-n);return String(x.getDate()).padStart(2,'0')+'/'+String(x.getMonth()+1).padStart(2,'0')+'/'+String(x.getFullYear()).slice(2)};
      state.history=[1,2,3].map(i=>({date:d(i),totals:{kcal:1900,protein:100,carbs:25,fat:100},log:[{id:i,time:'08:00',description:'Eggs',kcal:300,protein:20,carbs:1,fat:20,items:[{name:'Eggs',kcal:300,protein:20,carbs:1,fat:20}]}],exercises:[]}));saveState();})()""")
    ev("switchTabById('stats')"); ev("mhStatsOpen()"); page.wait_for_timeout(300)
    id0=ev("mhStatLoad()[0].id")
    check('card has a 🎨 button', ev("document.getElementById('stcard-%s').innerText.includes('🎨')"%id0))
    ev("mhStatLook('%s')"%id0)
    t=ev("document.getElementById('stcard-%s').innerText"%id0)
    check('look strip offers chart types and colour', 'SHOW AS' in t and 'COLOUR' in t, t[:200])
    ev("mhStatQuick('%s','output','bars')"%id0)
    check('chart type changes and is saved', ev("mhStatLoad()[0].output")=='bars')
    check('other settings survive', ev("mhStatLoad()[0].subject")=='foods' and ev("mhStatLoad()[0].id")==id0 and ev("mhStatLoad().length")==3)
    ev("mhStatQuick('%s','color','#123abc')"%id0)
    check('custom colour saved', ev("mhStatLoad()[0].color")=='#123abc')
    ev("mhStatQuick('%s','color','red;background:url(x)')"%id0)
    check('hostile colour refused', ev("mhStatLoad()[0].color")==None)
    ev("mhStatQuick('%s','output','nonsense')"%id0)
    check('invalid chart type repaired', ev("MH_ST_SUBJECTS.foods.outputs.includes(mhStatLoad()[0].output)"))
    ev("mhStatEdit('%s')"%id0); ev("mhStatSet('color','#abcdef')")
    check('builder takes a custom colour too', ev("_stDraft.color")=='#abcdef' and 'type="color"' in ev("document.getElementById('statsBuilder').innerHTML"))
    ev("mhStatSet('color','javascript:1')"); check('builder refuses a hostile colour', ev("_stDraft.color")==None)
    check('no JS errors', not errs, str(errs[:2]))
print('p185: ALL PASS' if not bad else 'p185 FAILED: '+', '.join(bad))
