"""Persona 83: an open app re-reads combined.csv when it comes back to the front (and on a timer), so a finished sync/Zepp merge shows without a reload."""
import sys, re; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    page = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block').new_page()
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(2000)
    page.evaluate("localStorage.setItem('mh_onboarded','1')"); page.reload(); page.wait_for_timeout(2500)
    ev = page.evaluate
    ev("window.__imports = 0; window.__orig = importCombinedCSVText; importCombinedCSVText = function () { window.__imports++; }")
    ev("localStorage.setItem('mh_combined_csv_cache', 'older copy')")
    ev("Object.defineProperty(document, 'hidden', { configurable: true, get: () => false }); document.dispatchEvent(new Event('visibilitychange'))")
    page.wait_for_timeout(1500)
    n = ev("window.__imports"); print("online", ev("_serverOnline"), "imports", n)
    if ev("_serverOnline") and n < 1: f.add('BUG', 'coming back to the front did not re-check combined.csv')
    if errs: f.add('BUG', f'page errors: {errs[:2]}')
print('findings', len(f)); sys.exit(1 if f else 0)
