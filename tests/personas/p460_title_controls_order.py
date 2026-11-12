"""Persona 460: on every screen whose section titles carry the injected controls (Trends, Reports, Settings, Import, History), the order left to right is ▲ then ▼ then 👁, the same as the Today cards (Pete, 12 Nov 2026: "same place, same order everywhere"). Demo persona."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
JS = """() => { const out=[]; document.querySelectorAll('.section-title[data-reorder-injected]').forEach(t=>{ if(!t.offsetParent) return; const xs={}; t.querySelectorAll('*').forEach(e=>{ if(e.children.length) return; const g=e.textContent.trim(); if(['▲','▼','👁'].includes(g)) xs[g]=e.getBoundingClientRect().left }); if(Object.keys(xs).length>=2) out.push([t.id, xs['▲'], xs['▼'], xs['👁']]) }); return out }"""
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); ev = page.evaluate
    page.on('pageerror', lambda e: f.add('JS-exception', str(e)[:300])); page.on('dialog', lambda d: d.dismiss())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500); ev("startDemoMode('doris')"); page.wait_for_timeout(2500)
    total = 0
    for name, js in [('trends', "switchTab('insights'); switchSubTab('insights','trends')"), ('reports', "switchTabById('reports')"), ('manage', "switchTabById('manage')"), ('import', "switchTabById('import')")]:
        ev(js); page.wait_for_timeout(1200); rows = ev(JS); total += len(rows)
        for tid, up, down, eye in rows:
            if None in (up, down, eye): continue
            if not (up < down < eye): f.add('BUG', f'{name}: {tid} shows ▲ {up:.0f}, ▼ {down:.0f}, 👁 {eye:.0f}: not left to right ▲ ▼ 👁')
    if total < 8: f.add('BUG', f'0: only {total} titles with controls were on screen, so the check proves little')
print('findings', len(f))
for x in f: print(x)
sys.exit(1 if f else 0)
