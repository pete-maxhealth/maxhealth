"""Persona 462 (v3.10.1377, Pete 12 Nov): the Paste Meal sheet fills itself from the clipboard, so the "Paste from clipboard" button is not shown; it only appears again if the automatic read finds nothing usable."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
vis = "(()=>{const b=document.getElementById('pasteMealRetry'); return !!b && b.offsetParent!==null})()"
with fresh_server() as root, sync_playwright() as pw:
    ctx = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block', permissions=['clipboard-read', 'clipboard-write']); page = ctx.new_page(); ev = page.evaluate
    page.on('pageerror', lambda e: f.add('JS-exception', str(e)[:300])); page.on('dialog', lambda d: d.dismiss())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500); ev("startDemoMode('doris')"); page.wait_for_timeout(2500)
    ev("navigator.clipboard.writeText('just some words')")
    ev("openPasteMealModal()"); page.wait_for_timeout(800)
    if ev("document.getElementById('pasteMealModal').style.display") != 'flex': f.add('BUG', '1: sheet did not open')
    if not ev(vis): f.add('BUG', '2: with nothing usable on the clipboard the fallback button should show')
    ev("pasteMealModal.style.display='none'")
    ev("navigator.clipboard.writeText('Test porridge (200 g) — 300 kcal, 10 g protein, 5 g fat, 40 g carbs')")
    ev("openPasteMealModal()"); page.wait_for_timeout(900)
    if ev(vis): f.add('BUG', '3: a usable copied meal fills the sheet, so the button must stay hidden')
    if 'porridge' not in ev("document.getElementById('pasteMealDesc').value").lower(): f.add('BUG', '4: the sheet did not fill itself from the clipboard')
    ev("document.getElementById('pasteMealModal').style.display='none'")
print('findings', len(f))
for x in f: print(x)
sys.exit(1 if f else 0)
