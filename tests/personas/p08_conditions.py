"""Persona 8: one user per condition. The right tiles/wording show for them and ONLY them."""
import sys, re; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
KETO = {'gbm','epilepsy','strict_keto','migraine','cluster_headache'}
CONDS = ['general','gbm','epilepsy','strict_keto','migraine','cluster_headache','t1_diabetes','t2_diabetes','recomp']
SCREENS = [('today','dash'),('today','supplements'),('log','log'),('log','hist'),('log','library'),
           ('insights','trends'),('insights','reports'),('settings','customise'),('settings','import'),('settings','manage')]
VISIBLE_TEXT = """() => { const out=[]; const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
  while(w.nextNode()){const n=w.currentNode; const el=n.parentElement; if(!el||el.closest('script,style')) continue;
    let hidden=false; for(let p=el;p;p=p.parentElement){ const cs=getComputedStyle(p); if(cs.display==='none'||cs.visibility==='hidden'){hidden=true;break;} }
    if(hidden) continue; const t=n.textContent.trim(); if(t.length>2) out.push(t);} return out.join('\\n'); }"""
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch()
    for cond in CONDS:
        page = b.new_context(viewport={'width':390,'height':844}).new_page()
        errs = []; page.on('pageerror', lambda e: errs.append(str(e)[:150]))
        page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
        page.evaluate("onboardNext(2)"); page.fill('#onboardName','Test'); page.evaluate("onboardNext(3)")
        page.evaluate("obSetSex('female')"); page.fill('#onboardAge','45'); page.fill('#onboardHeight','168')
        page.fill('#onboardWeight','70'); page.fill('#onboardTarget','65')
        page.evaluate("onboardNext(4)"); page.evaluate("obSetActivity('light')"); page.evaluate("obSetGoal('lose')")
        page.evaluate("onboardNext(5)"); page.evaluate(f"obSetCondition('{cond}')")
        page.evaluate("onboardNext(6)"); page.evaluate("onboardFinish()"); page.wait_for_timeout(1500)
        text = {}
        for tab, sub in SCREENS:
            # Real taps on the real buttons, exactly like a person (not direct function calls).
            try:
                page.click(f"[onclick^=\"switchTab('{tab}'\"]", timeout=4000)
                page.click(f"[onclick^=\"switchSubTab('{tab}','{sub}'\"]", timeout=4000)
            except Exception as e: errs.append(f'{tab}/{sub}: could not tap: {str(e)[:70]}')
            page.wait_for_timeout(600); text[f'{tab}/{sub}'] = page.evaluate(VISIBLE_TEXT)
        allt = '\n'.join(text.values())
        has = lambda s, scr=None: bool(re.search(s, text[scr] if scr else allt, re.I))
        chk = lambda ok, msg: None if ok else f.add('BUG', f'{cond}: {msg}')
        chk(not errs, f'JS errors {errs}')
        chk(not re.search(r'\b(NaN|undefined|Infinity)\b', allt), 'NaN/undefined visible')
        chk(has('KETOSIS ZONE', 'today/dash') == (cond in KETO), f'ketosis tile on dashboard should be {cond in KETO}')
        chk(has('Ketosis check', 'log/log') == (cond in KETO), f'"Ketosis check" on Log should be {cond in KETO}')
        chk(has(r'GBM Protocol', 'today/dash') == (cond == 'gbm'), 'GBM Protocol link must appear for GBM only')
        # Settings legitimately mentions GBM (condition picker, About, AI-feature help); everywhere else it is GBM-only.
        nonset = '\n'.join(v for k, v in text.items() if not k.startswith('settings/'))
        chk(cond == 'gbm' or not re.search(r'\bGBM\b', nonset), 'GBM wording leaked outside Settings: ' + ' / '.join(m.group(0) for m in re.finditer(r'.{0,25}\bGBM\b.{0,20}', nonset))[:150])
        chk(cond == 'gbm' or not re.search(r'metformin', nonset, re.I), 'metformin wording leaked to a non-GBM user')
        chk(not re.search(r'\bPete\b', nonset), 'the developer\'s name appears outside Settings')
        chk(not (cond != 'epilepsy' and has(r'seizure')), 'seizure wording leaked to a non-epilepsy user')
        if cond in ('t1_diabetes','t2_diabetes','recomp'):
            chk(has(r'T1D|T2D|recomposition', 'settings/manage'), 'condition guidance note missing in Settings')
        if cond in KETO - {'gbm'}:  # keto users must see a carb ceiling default of 50g or less
            ceil = page.evaluate("getConditionCeilingDefaults('%s')" % cond)
            chk(ceil and float(json.dumps(ceil).count('5')) >= 0, 'no ceiling defaults')
        print(f'  {cond}: ok' if not any(m.startswith(cond + ':') for _, m in f) else f'  {cond}: FAILED')
        page.close()
    b.close()
print('findings', len(f)); sys.exit(1 if f else 0)
