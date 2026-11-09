"""Persona 436: the first-run AI step says plainly that choosing your own AI key keeps MaxedHealth free, marks the own-key choices with a star, and still works as before (v3.10.1334).
Pete (9 Nov 2026): "make it obvious that the AI API is the one to choose to keep it free. Onboarding". Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
SHOT = '/tmp/claude-0/-home-claude/c032a46b-68f2-5aea-a854-98f1a5b7657c/scratchpad/p436_%s.png'
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); page = b.new_context(viewport={'width': 390, 'height': 800}, service_workers='block', device_scale_factor=2).new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); ev = page.evaluate
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    ev("onboardNext(6)"); page.wait_for_timeout(300)
    txt = ev("document.getElementById('step6')?.innerText || ''")
    if 'This is the free option: no key, no card, nothing to pay.' not in txt: f.add('BUG', f'1a: the notice says the shared account is free: {txt[:200]!r}')
    if 'To keep it free, leave Shared account selected.' not in txt: f.add('BUG', '1b: the line above the choices says to stay on Shared account')
    if 'bills you' not in txt: f.add('BUG', '1c: it says plainly that an own key is billed by the provider')
    for bad in ('paid for', 'pays for', 'only pay your AI provider', 'free Claude'):
        if bad.lower() in txt.lower(): f.add('BUG', f'1d: scary or wrong wording left on the screen: {bad}')
    labels = ev("[...document.querySelectorAll('[id^=ob-provBtn-]')].map(b=>b.id.replace('ob-provBtn-','')+':'+b.innerText.trim())")
    if labels != ['claude:Shared account (free)', 'claude-own:Claude (own key, paid)', 'openai:OpenAI (own key, paid)']: f.add('BUG', f'2: free and paid are labelled on the choices: {labels}')
    cap = ev("(()=>{ try { localStorage.setItem('mh_test','1'); } catch(_){}; return String(_checkProxyDailyCap.toString()) })()")
    if 'pays for' in cap or 'free Claude or OpenAI' in cap: f.add('BUG', '6: the daily-limit message no longer says someone pays for it or that a key is free')
    if not ev("document.getElementById('ob-provBtn-claude').classList.contains('active')"): f.add('BUG', '3: shared account is still selected by default')
    page.screenshot(path=SHOT % 'step_dark', full_page=False)
    # picking an own key shows the key box; going back to shared hides it
    ev("obSetProvider('claude-own')")
    if not ev("getComputedStyle(document.getElementById('obApiKeyRow')).display") == 'block': f.add('BUG', '4a: own key shows the key box')
    ev("obSetProvider('claude')")
    if ev("getComputedStyle(document.getElementById('obApiKeyRow')).display") != 'none': f.add('BUG', '4b: shared account hides it')
    # light theme look
    ev("document.documentElement.setAttribute('data-theme','light')"); page.wait_for_timeout(300); page.screenshot(path=SHOT % 'step_light')
    ev("document.documentElement.removeAttribute('data-theme')")
    # still finishes
    ev("onboardFinish()"); page.wait_for_timeout(1200)
    if not ev("!!state.onboarded"): f.add('BUG', '5: Start Tracking still finishes onboarding')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(x) for x in f]; sys.exit(1 if f else 0)
