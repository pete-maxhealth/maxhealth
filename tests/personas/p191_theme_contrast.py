"""Persona 191 (v3.10.1087): text on the Statistics cards, sleep and outcomes reports stays readable in every colour theme x visual theme (WCAG-style contrast, 3:1 floor for small secondary text, 4.5 for main text)."""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
bad=[]
def check(n, ok, info=''):
    print(('PASS ' if ok else 'FAIL ')+n+(f'  {info}' if info and not ok else ''))
    if not ok: bad.append(n)
JS = """(sel)=>{
 const parse=c=>{const m=c.match(/[\\d.]+/g)||[];return {r:+m[0],g:+m[1],b:+m[2],a:m[3]===undefined?1:+m[3]}};
 const lum=({r,g,b})=>{const f=v=>{v/=255;return v<=0.03928?v/12.92:Math.pow((v+0.055)/1.055,2.4)};return 0.2126*f(r)+0.7152*f(g)+0.0722*f(b)};
 const bgOf=e=>{let n=e;while(n){const c=parse(getComputedStyle(n).backgroundColor);if(c.a>0.5)return c;n=n.parentElement}return parse(getComputedStyle(document.body).backgroundColor)};
 const out=[];
 document.querySelectorAll(sel).forEach(e=>{ if(!e.offsetParent||!e.childElementCount===0&&false) return; const t=(e.childNodes.length&&[...e.childNodes].some(n=>n.nodeType===3&&n.textContent.trim().length>2)); if(!t) return;
   const fg=parse(getComputedStyle(e).color), bg=bgOf(e); const l1=lum(fg),l2=lum(bg); const cr=(Math.max(l1,l2)+0.05)/(Math.min(l1,l2)+0.05); out.push([e.textContent.trim().slice(0,30),Math.round(cr*10)/10,getComputedStyle(e).fontSize]) });
 return out }"""
with fresh_server() as root, sync_playwright() as pw:
    br=pw.chromium.launch(); ctx=br.new_context(viewport={'width':430,'height':900},service_workers='block'); page=ctx.new_page()
    errs=[]; page.on('pageerror',lambda e:errs.append(str(e)[:200])); page.on('dialog',lambda d:d.accept())
    page.route(re.compile(r'^https?://(?!localhost)'),lambda r:r.abort())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200)
    ev=page.evaluate
    ev("state.onboarded=true; saveState()")
    ev("""(()=>{const d=n=>{const x=new Date();x.setDate(x.getDate()-n);return String(x.getDate()).padStart(2,'0')+'/'+String(x.getMonth()+1).padStart(2,'0')+'/'+String(x.getFullYear()).slice(2)};
      state.history=[...Array(20).keys()].map(i=>({date:d(i+1),sleep_duration:420+(i%5)*10,sleep_deep:70+(i%3),sleep_rem:90,sleep_light:240,sleep_wake:20,sleep_efficiency:93,bedtime:'23:10',totals:{kcal:1900,protein:100,carbs:25,fat:100},log:[{id:i,time:'08:00',description:'Eggs',kcal:300,protein:20,carbs:1,fat:20,items:[{name:'Eggs',kcal:300,protein:20,carbs:1,fat:20}]}],exercises:[]}));saveState();})()""")
    ev("mhStatSeedDefaults()")
    worst={}
    for theme in ['aurora','carbon','slate','light']:
        for vt in ['none','vital','pulse','forge']:
            ev("(a)=>{document.documentElement.setAttribute('data-theme',a[0]); if(a[1]==='none') document.documentElement.removeAttribute('data-visual-theme'); else document.documentElement.setAttribute('data-visual-theme',a[1]);}",[theme,vt])
            ev("switchTabById('stats'); mhStatsOpen()"); page.wait_for_timeout(250)
            rows=ev(JS,'#statsList *')
            ev("switchTabById('reports'); renderSleepReport(); renderOutcomesReport()"); page.wait_for_timeout(250)
            rows+=ev(JS,'#sleep-report-content *, #outcomes-report-content *')
            low=[r for r in rows if r[1]<3.0]
            worst[(theme,vt)]=low[:3]
            check(f'{theme}/{vt}: statistics and sleep text readable (>=3:1)', not low, str(low[:3]))
    check('no JS errors', not errs, str(errs[:2]))
print('p191: ALL PASS' if not bad else 'p191 FAILED: '+str(len(bad))+' combos')
