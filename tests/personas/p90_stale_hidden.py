"""Persona 90: a hidden key for a card that no longer exists must not count as '1 hidden' on the Filter button or leave a dead restore chip; real hidden cards still count and restore; applies to Reports/Manage (generic), Today and Trends cards."""
import sys; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    errs = []
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 844}, service_workers='block').new_page()
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("localStorage.setItem('mh_onboarded','1')"); page.reload(); page.wait_for_timeout(2500)
    ev = page.evaluate
    ev("document.querySelectorAll('[id*=nboard]').forEach(e=>{ if(e.style) e.style.display='none'; })")
    label = lambda root_id: ev("(r)=>{const tb=document.getElementById(r).querySelector('.mh-pills-toolbar'); return tb ? tb.querySelector('button.main').textContent.trim() : null}", root_id)
    # generic scope (Reports)
    ev("switchTab('insights'); switchSubTab('insights','reports')"); page.wait_for_timeout(500)
    ev("saveGenericHidden('reports', ['seasonal']); applyGenericOrder('reports'); mhEnsurePillsToolbars()"); page.wait_for_timeout(300)
    if 'hidden' in (label('view-reports') or ''): f.add('BUG', f"stale key counted as hidden on Reports: {label('view-reports')}")
    if 'seasonal' in ev("localStorage.getItem('mh_reorder_hidden_reports')"): f.add('BUG', 'stale key not removed from storage')
    ev("saveGenericHidden('reports', ['rpt-askai','seasonal']); applyGenericOrder('reports'); mhEnsurePillsToolbars()"); page.wait_for_timeout(300)
    if '1 hidden' not in (label('view-reports') or ''): f.add('BUG', f"real hidden card should count once: {label('view-reports')}")
    # Today dashboard
    ev("switchTab('dashboard')"); page.wait_for_timeout(500)
    ev("localStorage.setItem('mh_dashboard_hidden', JSON.stringify(['gone-card'])); applyDashboardOrder(); mhEnsurePillsToolbars()"); page.wait_for_timeout(300)
    if 'hidden' in (label('view-dash') or ''): f.add('BUG', f"stale dashboard key counted: {label('view-dash')}")
    # Trends metric cards
    ev("switchTab('insights'); switchSubTab('insights','trends')"); page.wait_for_timeout(500)
    ev("localStorage.setItem('mh_trend_cards_hidden', JSON.stringify(['mcNothing'])); applyTrendCardsOrderAndVisibility(); mhEnsurePillsToolbars()"); page.wait_for_timeout(300)
    if 'hidden' in (label('view-trends') or ''): f.add('BUG', f"stale trend card key counted: {label('view-trends')}")
    if errs and any('ServiceWorker' not in e for e in errs): f.add('BUG', f'page errors: {errs[:2]}')
print('findings', len(f)); sys.exit(1 if f else 0)
