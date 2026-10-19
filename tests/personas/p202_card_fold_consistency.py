"""Persona 202: Today-card fold consistency (v3.10.1113). Pete Spence, from three screenshots: "A show/
hide missing, calories burned not showing. Uppiecase HIDE and lowercase hide? What happened to
consistency?" Audit of every moveDashboardSection(...) card found 7 with no fold-to-bar control at all
(daymode, goalcheck, ketosis, macroratio, macros, mealplan, weather - "guides" and "log" already had one
via toggleSection) plus a text-transform:uppercase leak onto Today's Log's "hide" label. Covers: every
card's 4th control now folds its body and flips the label, Today's Log's label stays lowercase, and the
fold state survives a reload (same localStorage mechanism as Water/Fibre/Fasting)."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev("startDemoMode('alex')"); page.wait_for_timeout(2500)
    ev("document.getElementById('maintab-today').click()"); page.wait_for_timeout(500)
    ev("try{ localStorage.setItem('mh_wx_loc', JSON.stringify({name:'Testville', lat:51.5, lon:-0.1})); }catch(e){}")
    ev("try{ mhWxRender(); }catch(e){}")
    page.wait_for_timeout(300)

    cards = ['daymode', 'ketosis', 'macros', 'macroratio', 'goalcheck', 'mealplan', 'weather']
    for k in cards:
        has_icon = ev(f"!!document.getElementById('{k}BodyIcon')")
        has_body = ev(f"!!document.getElementById('{k}Body')")
        if not has_icon or not has_body:
            f.add('BUG', f'{k}: missing fold control (icon={has_icon}, body={has_body})')
            continue
        label0 = ev(f"document.getElementById('{k}BodyIcon').textContent")
        if 'hide' not in label0:
            f.add('BUG', f'{k}: fold icon should start as "hide", got {label0!r}')
            continue
        ev(f"mhCardBody('{k}')"); page.wait_for_timeout(100)
        disp = ev(f"document.getElementById('{k}Body').style.display")
        label1 = ev(f"document.getElementById('{k}BodyIcon').textContent")
        if disp != 'none' or 'show' not in label1:
            f.add('BUG', f'{k}: folding did not hide the body or flip the label (display={disp!r}, label={label1!r})')
        # survives reload
        page.reload(); page.wait_for_timeout(1500)
        ev("document.getElementById('maintab-today').click()"); page.wait_for_timeout(500)
        disp2 = ev(f"document.getElementById('{k}Body')?.style.display")
        if disp2 != 'none':
            f.add('BUG', f'{k}: folded state did not survive reload (display={disp2!r})')
        # unfold again, leave in default (open) state for cleanliness
        ev(f"mhCardBody('{k}')"); page.wait_for_timeout(100)

    # Today's Log: "hide" stays lowercase (CSS text-transform:uppercase on .log-title was leaking onto it)
    log_label = ev("document.getElementById('log-today-icon').textContent")
    if 'HIDE' in log_label or 'hide' not in log_label:
        f.add('BUG', f'Todays Log fold label should read lowercase "hide", got {log_label!r}')
    cs = ev("getComputedStyle(document.getElementById('log-today-icon')).textTransform")
    if cs == 'uppercase':
        f.add('BUG', f'Todays Log fold label still computes text-transform:uppercase ({cs})')

    if errs: f.add('BUG', f'page errors {errs[:3]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
