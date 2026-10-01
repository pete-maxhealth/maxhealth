"""Persona 3: first-time user offline (no CDN) opens each demo profile and expects working charts."""
import sys, re; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); page = b.new_context(viewport={'width':390,'height':844}).new_page()
    page.on('pageerror', lambda e: f.add('JS-exception', str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(2000)
    ver = page.evaluate("typeof Chart !== 'undefined' && Chart.version")
    print('Chart.version:', ver)
    if ver != '4.4.1': f.add('BUG', f'real Chart.js not loaded (got {ver})')
    if page.evaluate("fetch('/lib/chart.umd.js').then(r=>r.status)") != 200: f.add('BUG', '/lib/chart.umd.js not served')
    if page.evaluate("fetch('/lib/../server.py').then(r=>r.status)") != 404: f.add('BUG', 'path traversal not blocked')
    ids = page.evaluate("DEMO_PERSONAS.map(p=>p.id)"); print('demo personas:', ids)
    for pid in ids:
        page.evaluate("localStorage.clear()"); page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
        try: page.evaluate(f"startDemoMode('{pid}')")
        except Exception as e: f.add('JS-exception', f'startDemoMode({pid}): {str(e)[:100]}'); continue
        page.wait_for_timeout(1500)
        for tab in ('today', 'insights'):
            try: page.evaluate(f"switchTab('{tab}')")
            except Exception as e: f.add('JS-exception', f'switchTab {tab}: {str(e)[:100]}')
            page.wait_for_timeout(1200)
        n = page.evaluate("Object.values(Chart.instances||{}).length")
        txt = page.inner_text('body')
        bad = [w for w in ('NaN', 'undefined', 'Infinity') if re.search(r'\b'+w+r'\b', txt)]
        print(f'  {pid}: charts drawn={n} badtext={bad}')
        if n == 0: f.add('check', f'{pid}: no Chart.js instances after opening Today+Insights')
        if bad: f.add('BUG', f'{pid}: {bad} visible')
    b.close()
print('findings', len(f)); sys.exit(1 if any(s == 'BUG' or s == 'JS-exception' for s, _ in f) else 0)
