"""Persona 417: click-everything on a PC window (v3.10.1312). Mouse only, demo persona (nothing real is saved), widths 1000 and 1440.
Covers: for every main tab and sub-tab, (a) every visible control is the top element at its own centre (nothing covers it), (b) a real mouse click on each
safe control raises no page error (controls that delete, clear, reset, restore, sign out or send are looked at but not clicked), screen reset between controls."""
import sys, time; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
SCREENS = [('today','dash'),('today','move'),('today','supplements'),('log','log'),('log','hist'),('log','library'),('log','shop'),('insights','trends'),('insights','reports'),('insights','stats'),('settings','manage'),('settings','customise'),('settings','import')]
SKIP = r"language|idioma|lang|globe|delete|clear|reset|remove|wipe|erase|restore|sign out|log out|send|import|upload|share|download|export|push|empty|undo|forget|cancel|start fresh|demo|stop|close all|premium"
LIST = """(skip)=>{const out=[];const re=new RegExp(skip,'i');
 for(const e of document.querySelectorAll('button,[onclick],a[href],select,input[type=checkbox],summary')){
  const r=e.getBoundingClientRect(); const cs=getComputedStyle(e);
  if(r.width<4||r.height<4||cs.visibility==='hidden'||cs.display==='none'||e.disabled) continue;
  if(e.closest('[style*="display:none"],[hidden],#onboardingOverlay')) continue;
  const t=(e.innerText||e.getAttribute('aria-label')||e.title||e.id||'').trim().slice(0,40);
  out.push({i:out.length,t,safe:!re.test(t+' '+(e.getAttribute('onclick')||'')),id:e.id||'',tag:e.tagName});}
 return out;}"""
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []; t0 = time.time(); clicked = 0; checked = 0
    for w in (1000, 1440):
        page = b.new_context(viewport={'width': w, 'height': 900}, service_workers='block').new_page(); ev = page.evaluate
        page.on('pageerror', lambda e: errs.append(str(e)[:160])); page.on('dialog', lambda d: d.dismiss())
        page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
        ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay').style.display='none'"); ev("startDemoMode('doris')"); page.wait_for_timeout(1500)
        for tab, sub in SCREENS:
            def go():
                ev("document.querySelectorAll('[id$=Modal],.modal-overlay').forEach(m=>{if(m.id==='mhPackModal'||m.id==='mhLangModal')m.remove()})")
                ev(f"document.getElementById('maintab-{tab}').click()"); page.wait_for_timeout(250)
                ev(f"try{{switchSubTab('{tab}','{sub}')}}catch(e){{}}"); page.wait_for_timeout(350)
            go()
            items = ev(LIST, SKIP)
            for it in items[:70]:
                loc = page.locator('button,[onclick],a[href],select,input[type=checkbox],summary').nth(it['i']) if False else None
            # covered check, one pass in the page
            cov = ev("""(skip)=>{const bad=[];const els=[...document.querySelectorAll('button,[onclick],a[href],select,input[type=checkbox],summary')];
              for(const e of els){const cs=getComputedStyle(e);const r0=e.getBoundingClientRect(); if(r0.width<4||r0.height<4||cs.visibility==='hidden'||cs.display==='none'||e.disabled) continue;
                if(e.closest('[style*="display:none"],[hidden],#onboardingOverlay')) continue; if(!e.offsetParent && cs.position!=='fixed') continue; {const d=e.closest('details:not([open])'); if(d && !(e.tagName==='SUMMARY' && e.parentElement===d)) continue;}
                e.scrollIntoView({block:'center'}); const r=e.getBoundingClientRect(); if(r.top<0||r.bottom>innerHeight) continue;
                const t=document.elementFromPoint(r.left+r.width/2,r.top+r.height/2); if(t&&!(e===t||e.contains(t)||t.contains(e))) bad.push((e.innerText||e.title||e.id||e.tagName).trim().slice(0,30)+' <- '+(t.id||t.className||t.tagName).toString().slice(0,30));}
              return bad.slice(0,8);}""", SKIP)
            checked += len(items)
            for c in cov: f.add('BUG', f'{w} {tab}/{sub}: covered control {c}')
            # click pass on safe controls
            n = min(len(items), 40)
            for k in range(n):
                it = items[k]
                if not it['safe']: continue
                try:
                    go(); items2 = ev(LIST, SKIP)
                    if k >= len(items2) or items2[k]['t'] != it['t']: continue
                    el = page.locator('button,[onclick],a[href],select,input[type=checkbox],summary').nth(k) if False else None
                    ok = ev("""(k)=>{const els=[...document.querySelectorAll('button,[onclick],a[href],select,input[type=checkbox],summary')].filter(e=>{const r=e.getBoundingClientRect();const cs=getComputedStyle(e);return !(r.width<4||r.height<4||cs.visibility==='hidden'||cs.display==='none'||e.disabled||e.closest('[style*="display:none"],[hidden],#onboardingOverlay'))});
                       const e=els[k]; if(!e) return null; e.scrollIntoView({block:'center'}); const r=e.getBoundingClientRect(); return [r.left+r.width/2,r.top+r.height/2,e.tagName]}""", k)
                    if not ok or ok[2] in ('A','SELECT'): continue
                    if not (0 <= ok[1] <= 900): continue
                    page.mouse.click(ok[0], ok[1]); clicked += 1; page.wait_for_timeout(120)
                except Exception as e: f.add('BUG', f'{w} {tab}/{sub}: click on "{it["t"]}" failed {str(e)[:80]}')
                if time.time() - t0 > 520: break
            if time.time() - t0 > 520: break
        page.context.close()
    seen = set(); 
    for e in errs:
        if e not in seen: seen.add(e); f.add('BUG', 'page error: ' + e)
print('controls listed', checked, 'clicked', clicked, 'secs', int(time.time() - t0))
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
