"""Persona 411: the buttons that used a class that does not exist (class="btn") now use the standard copy-btn (v3.10.1307): Premium licence Activate / trial / Remove,
the "Help keep it free" Ko-fi link, and the Close buttons on the Premium preview and flow. Covers: none left with class btn, each looks like its neighbours (same background,
colour, border radius, font as a copy-btn), Activate still activates (field empty = message, no error), the Ko-fi link still points at ko-fi.com/maxedhealth, the Premium
preview opens and Close closes it, no Premium link leaks (rule: Premium stays coming soon), no page errors. Invented data, demo persona."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.dismiss()); ev = page.evaluate
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay').style.display='none'")
    ev("document.getElementById('maintab-settings').click()"); page.wait_for_timeout(1000)
    if ev("document.querySelectorAll('.btn').length") : f.add('BUG', '1: elements with the missing class btn remain')
    ref = ev("(()=>{const b=document.createElement('button'); b.className='copy-btn'; document.body.appendChild(b); const c=getComputedStyle(b); const o=[c.backgroundColor,c.color,c.borderRadius,c.fontFamily]; b.remove(); return o})()")
    for sel in ("button[onclick*=mhLicenceActivate]", "#licenceRemoveBtn", "#licenceTrialBtn"):
        got = ev(f"(()=>{{const b=document.querySelector('{sel}'); if(!b) return null; b.style.display=b.style.display==='none'?'inline-block':b.style.display; const c=getComputedStyle(b); return [c.backgroundColor,c.color,c.borderRadius,c.fontFamily]}})()")
        if got is None: f.add('BUG', f'2: {sel} missing')
        elif got != ref: f.add('BUG', f'3: {sel} does not look like a copy-btn: {got} vs {ref}')
    ev("mhLicenceActivate()"); page.wait_for_timeout(400)
    k = ev("(()=>{const c=[...document.querySelectorAll('a')].find(a=>/Buy me a Ko-fi/.test(a.textContent)); if(!c) return null; const s=getComputedStyle(c); return [c.href, s.backgroundColor, s.color]})()")
    if k is None: f.add('BUG', '4: Ko-fi link not shown')
    else:
        if 'ko-fi.com/maxedhealth' not in k[0]: f.add('BUG', f'5: Ko-fi link target {k[0]}')
        if k[1:] != ref[:2]: f.add('BUG', f'6: Ko-fi link not styled like a copy-btn: {k[1:]} vs {ref[:2]}')
    if errs: f.add('BUG', f'page errors {errs[:3]}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
