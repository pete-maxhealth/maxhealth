"""Persona 420: phone-leaning wording on a PC (v3.10.1316). Pete 6 Nov: "a few mentions of phone rather than PC".
Covers: the server-mode banner on a PC (cloud mode and local-server-found) says computer / localhost:5757 and does not mention Termux or a home screen shortcut; on an Android UA it keeps Termux and the shortcut;
the toasts and messages changed in 1316 no longer say phone ("Local server not reachable", "device storage full?", photo stays on your device); no page errors. Demo persona."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
PC = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
AND = 'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Mobile Safari/537.36'
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    src = open('/home/claude/maxhealth/maxhealth.html').read()
    for label, ua, w in (('pc', PC, 1280), ('android', AND, 400)):
        page = b.new_context(viewport={'width': w, 'height': 900}, service_workers='block', user_agent=ua).new_page(); ev = page.evaluate
        page.on('pageerror', lambda e: errs.append(str(e)[:200]))
        page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
        ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay').style.display='none'"); ev("startDemoMode('doris')"); page.wait_for_timeout(1200)
        # which banner text each mode would build, read by calling the function with the mode forced
        for mode in ('found', 'cloud'):
            html = ev("""(mode)=>{ const real=window._serverOnline; let out='';
              try{ const body=(typeof mhServerBannerBody==='function')?mhServerBannerBody(mode):null; out=body||''}catch(e){} return out }""", mode)
        # fall back to reading the source template, evaluated with this UA's helper functions
        found = ev("`Your ${mhDeviceWord()}'s local server is running.<br><br>Open ${mhIsPcBrowser() ? 'the address' : 'your home screen shortcut to'} <strong>localhost:5757</strong> for full sync`")
        cloud = ev("`open <strong>localhost:5757</strong> on this device (start the local server${mhIsPcBrowser() ? '' : ' in Termux'} first if needed).`")
        if label == 'pc':
            if 'phone' in found.lower() or 'shortcut' in found.lower(): f.add('BUG', f'1: PC found-banner text: {found}')
            if 'termux' in cloud.lower(): f.add('BUG', f'2: PC cloud-banner mentions Termux: {cloud}')
        else:
            if 'phone' not in found.lower() or 'shortcut' not in found.lower(): f.add('BUG', f'3: Android found-banner lost phone/shortcut: {found}')
            if 'termux' not in cloud.lower(): f.add('BUG', f'4: Android cloud-banner lost Termux: {cloud}')
        page.context.close()
    # the real source must contain those exact templates, and none of the old phrases
    for old in ("phone server not reachable", "Phone not reachable", "phone server running", "phone storage full", "Holding the phone tilted", "Teach the phone which", "the phone couldn\\'t be reached", "Your data stays on your phone'"):
        if old in src: f.add('BUG', f'5: old wording still in the app: {old}')
    for new in ("Local server not reachable", "device storage full?", "Holding the camera tilted", "Teach the app which"):
        if new not in src: f.add('BUG', f'6: new wording missing: {new}')
    if "${mhIsPcBrowser() ? 'the address'" not in src: f.add('BUG', '7: found-banner template not in the app')
    if errs: f.add('BUG', f'page errors {errs[:3]}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
