"""Persona 229: Cook Mode is readable on every theme (v3.10.1125). Found while recording the tour: the Cook Mode screen had a fixed dark background but its step
text used the theme's text colour, so on the light theme the steps were dark brown on near-black. Covers: for each theme the step text, the recipe name and the
step counter have a readable contrast against the Cook Mode background (step text 7 or more; the smaller muted labels at least 2.5, since their muted colour is an app-wide design choice, not Cook Mode's). Invented data only."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
JS = """(theme)=>{ applyTheme(theme);
  saveRecipes([{id:'rc1',name:'Test Dish',servings:2,steps:[{text:'Toss everything in the oil.'},{text:'Roast for 35 minutes.'}],ingredients:[{name:'Chicken',amount:100,kcal:100,protein:10,carbs:0,fat:5}]}]);
  openCookMode('rc1');
  const lum=c=>{const m=c.match(/[\\d.]+/g).map(Number); const [r,g,b]=m.slice(0,3).map(v=>{v/=255; return v<=0.03928?v/12.92:Math.pow((v+0.055)/1.055,2.4)}); return 0.2126*r+0.7152*g+0.0722*b};
  const ratio=(a,b)=>{const x=lum(a),y=lum(b); return (Math.max(x,y)+0.05)/(Math.min(x,y)+0.05)};
  const bg=getComputedStyle(document.getElementById('cookModeOverlay')).backgroundColor, out={};
  for (const id of ['cookModeStepText','cookModeRecipeName','cookModeStepCounter']) out[id]=Math.round(ratio(getComputedStyle(document.getElementById(id)).color,bg)*10)/10;
  closeCookMode(); return out; }"""
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    themes = ev("typeof THEMES!=='undefined' ? Object.keys(THEMES) : null") or ['midnight', 'aurora', 'carbon', 'slate', 'light']
    for t in themes:
        out = ev(JS, t); page.wait_for_timeout(150)
        for k, v in out.items():
            need = 7 if k == 'cookModeStepText' else 2.5
            if v < need: f.add('BUG', f'theme {t}: {k} contrast {v} is below {need}')
    if errs: f.add('BUG', f'page errors: {errs[:3]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
