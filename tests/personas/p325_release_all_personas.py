"""Persona 325 (release suite, v3.10.1219): the changes of this release walked through on every demo persona - Move cards (order, controls, ranges, empty notes, same header as the existing cards), Reports and Trends without the moved cards, History edit tags, shopping list quantities, cupboards without the use-most box, no page errors."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
PERSONAS = ['alex', 'doris', 'sam', 'maria', 'raj', 'priya', 'john', 'tom', 'grace', 'frank']
with fresh_server() as root, sync_playwright() as pw:
    br = pw.chromium.launch()
    for pid in PERSONAS:
        ctx = br.new_context(viewport={'width': 390, 'height': 900}, service_workers='block'); page = ctx.new_page(); errs = []
        page.on('pageerror', lambda e: errs.append(str(e)[:160])); page.on('dialog', lambda d: d.accept())
        page.goto('http://localhost:5757/'); page.wait_for_timeout(1000); ev = page.evaluate
        ev("state.onboarded=true; saveState()")
        try: ev(f"startDemoMode('{pid}')")
        except Exception as e: f.add('BUG', f'{pid}: demo did not start: {str(e)[:80]}'); ctx.close(); continue
        page.wait_for_timeout(2200)
        W = lambda m: f.add('BUG', f'{pid}: {m}')
        # Move
        ev("switchTabById('move')"); page.wait_for_timeout(900)
        order = ev("[...document.querySelectorAll('#moveScroll > .activity-card')].map(e=>e.id)")
        if order != ['dailyStepsCard', 'activityCard', 'planCard', 'moveExerciseCard', 'moveBodycompCard', 'moveJourneyCard']: W(f'Move card order {order}')
        for k, inner in [('Exercise', 'exercise-report-section'), ('Bodycomp', 'bodyCompCard'), ('Journey', 'journeyCard')]:
            card, note = f'move{k}Card', f'move{k}Empty'
            if ev(f"document.querySelectorAll('#{card} .trends-filter-btn').length") != 5: W(f'{k} has five range chips incl. Custom')
            txt = ev(f"document.getElementById('{card}').innerText")
            for g in ['▲', '▼', '👁']:
                if g not in txt: W(f'{k} card has {g}')
            innerHidden = ev(f"document.getElementById('{inner}').style.display === 'none'"); noteShown = ev(f"document.getElementById('{note}').style.display === 'block'")
            if innerHidden != noteShown: W(f'{k}: empty note matches whether there is data (hidden={innerHidden}, note={noteShown})')
            for n in [7, 30, 90, 0]:
                ev(f"mhMoveSetRange('{k.lower()}',{n})")
            ev(f"mhMoveSetRange('{k.lower()}',{ {'Exercise': 30, 'Bodycomp': 0, 'Journey': 0}[k] })")
        # same header look as the existing Today's activity card
        hs = lambda sel: ev(f"(function(){{const e=document.querySelector('{sel}'); const c=getComputedStyle(e); return [c.fontSize,c.fontFamily,c.letterSpacing,c.color,c.marginBottom,c.display].join('|')}})()")
        if hs('#activityCard .activity-card-title') != hs('#moveExerciseCard .activity-card-title'): W('Move card header looks like the existing Move card header')
        # hide / show round trip
        ev("toggleMoveSectionHidden('exercise')"); page.wait_for_timeout(150)
        if ev("document.getElementById('moveExerciseCard').style.display") != 'none': W('hide works')
        ev("toggleMoveSectionHidden('exercise')"); page.wait_for_timeout(150)
        # Reports / Trends no longer carry them
        ev("switchTabById('reports')"); page.wait_for_timeout(500)
        if ev("!!document.querySelector('#view-reports #exercise-report-section')"): W('Reports no longer has the Exercise card')
        ev("switchTabById('insights'); switchSubTab('insights','trends',document.getElementById('insightstab-trends'))"); page.wait_for_timeout(700)
        if ev("!!document.querySelector('#view-trends #journeyCard, #view-trends #bodyCompCard')"): W('Trends no longer has Journey / Body composition')
        # History edit tags
        ev("switchTabById('history'); renderHistory()"); page.wait_for_timeout(900)
        if ev("document.querySelectorAll('.hist-day-date').length") > 0:
            d = ev("document.querySelector('.hist-day-date').textContent.trim()")
            ev("document.querySelectorAll('.hist-day-totals-edit').forEach(x=>x.remove())"); ev(f"editHistDayTotalsByDate('{d}')"); page.wait_for_timeout(300)
            tags = ev("(document.querySelector('[id^=histTagPicker-]')||{innerText:''}).innerText")
            if 'Hospital day' not in tags: W('History tag picker has the standard tags')
            if 'Birthday' in tags and 'birthday' not in ev("JSON.stringify(state.history.map(h=>h.notes||'')).toLowerCase()"): W('Birthday only shows if it is in use')
        # shopping list quantity
        ev("switchTabById('shop'); mhShopOpen()"); page.wait_for_timeout(500)
        ev("(()=>{ let e=document.getElementById('mhShopOwn'); if(!e){ e=document.createElement('input'); e.id='mhShopOwn'; document.body.appendChild(e);} e.value='2 x Zz Cream'; mhShopAddOwn(); })()"); page.wait_for_timeout(200)
        if ev("(mhShopLoad().items.find(i=>i.key===mhShopKey('Zz Cream'))||{}).qty") != 2: W('typing "2 x Zz Cream" gives a count of 2')
        # cupboards screen has no use-most box
        ev("mhShopView('list')"); page.wait_for_timeout(300)
        if 'use most' in ev("document.body.innerText"): W('no "The ones I use most" box')
        if errs: W(f'page errors: {errs[:2]}')
        ctx.close()
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
