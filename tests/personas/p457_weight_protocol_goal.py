"""Persona 457: Weight vs Protocol knows the goal (Pete, 12 Nov 2026). Losing weight is a win when the goal is Lose (not a yellow warning), a warning when the goal is Gain, and the tile
states the goal and activity level. Same weights, goal switched: the colour and wording flip. Demo persona, invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); ev = page.evaluate
    page.on('pageerror', lambda e: f.add('JS-exception', str(e)[:300])); page.on('dialog', lambda d: d.dismiss())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500); ev("startDemoMode('doris')"); page.wait_for_timeout(2500)
    # a clear downward trend over 21 days, invented
    ev("""(()=>{ const h=[]; for(let i=0;i<21;i++){ const d=new Date(); d.setDate(d.getDate()-(20-i)); const dd=String(d.getDate()).padStart(2,'0')+'/'+String(d.getMonth()+1).padStart(2,'0')+'/'+String(d.getFullYear()).slice(2); h.push({date:dd,weight:Math.round((80-i*0.15)*10)/10,totals:{kcal:1800}}); }
      state.history=h.reverse(); state.weight=77; try{window.getFullBodyCompositionHistory=()=>[]}catch(e){}; })()""")
    def read(goal, act):
        ev(f"localStorage.setItem('mh_goal','{goal}'); localStorage.setItem('mh_activity_level','{act}'); switchTabById('reports'); renderWeightProtocol()"); page.wait_for_timeout(500)
        return ev("""(()=>{ const el=document.getElementById('weight-protocol-content'); if(!el) return null; const t=el.innerText; const tc=[...el.querySelectorAll('div')].find(e=>/kg$/.test(e.textContent.trim())&&!e.children.length&&/^[+-]/.test(e.textContent.trim())); return {t, col: tc?getComputedStyle(tc).color:null, yellow:getComputedStyle(document.documentElement).getPropertyValue('--yellow'), acc:getComputedStyle(document.documentElement).getPropertyValue('--accent')} })()""")
    a = read('lose', 'light')
    if not a or 'Losing weight' not in a['t'] or 'Lightly active' not in a['t']: f.add('BUG', f'1: goal and activity not stated: {a and a["t"][:160]!r}')
    elif 'moving the way you want' not in a['t']: f.add('BUG', f'2: losing on a Lose goal is not shown as a win: {a["t"][:200]!r}')
    b = read('gain', 'moderate')
    if not b or 'moving against your goal' not in b['t']: f.add('BUG', f'3: losing on a Gain goal is not flagged: {b and b["t"][:200]!r}')
    if a and b and a['col'] == b['col']: f.add('BUG', f'4: colour did not change with the goal ({a["col"]})')
    c = read('maintain', 'sedentary')
    if not c or 'Keeping weight steady' not in c['t'] or 'moving against your goal' not in c['t']: f.add('BUG', f'5: maintain: {c and c["t"][:200]!r}')
print('findings', len(f))
for x in f: print(x)
sys.exit(1 if f else 0)
