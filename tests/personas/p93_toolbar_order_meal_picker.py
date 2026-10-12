"""Persona 93: the Filter toolbar is the FIRST item on every screen that has one (and exactly one per screen, never piling up);
Next meal idea highlights the tapped pills in the live picker only, even when the picker has been opened twice."""
import sys, re, json; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
SCREENS = [('today','dash'), ('insights','trends'), ('insights','reports'), ('settings','manage'), ('settings','import')]
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("localStorage.setItem('mh_onboarded','1'); localStorage.setItem('mh_pills_open','1')"); page.reload(); page.wait_for_timeout(2000)
    page.evaluate("document.querySelectorAll('[id*=nboard]').forEach(e=>{ if(e.style) e.style.display='none'; })")
    for t, sub in SCREENS:
        page.evaluate(f"switchTab('{t}'); switchSubTab('{t}','{sub}')"); page.wait_for_timeout(900)
        r = page.evaluate("""()=>{ const tbs=[...document.querySelectorAll('.mh-pills-toolbar')]; const vis=tbs.filter(t=>t.getBoundingClientRect().height>0);
          return {total: tbs.length, vis: vis.length, first: vis.map(t=>t.parentNode.firstElementChild===t), labels: vis.map(t=>[...t.querySelectorAll('button')].map(b=>b.textContent.replace(/[^A-Za-z ]/g,'').trim().split(' ')[0]).join(','))}; }""")
        if r['vis'] != 1: f.add('BUG', f'{t}/{sub}: {r["vis"]} visible toolbars')
        elif not all(r['first']): f.add('BUG', f'{t}/{sub}: toolbar is not the first item')
        elif not r['labels'][0].startswith('Filter,Open,Close,Default'): f.add('BUG', f"{t}/{sub}: toolbar order {r['labels'][0]}")
        if r['total'] > 8: f.add('BUG', f'{t}/{sub}: toolbars piling up ({r["total"]})')
    # meal picker
    page.evaluate("""()=>{ saveLibrary([{id:'a',name:'Chicken',kcal:200,protein:30,carbs:0,fat:8,portion:'100g',categories:['meat']},{id:'b',name:'Broccoli',kcal:30,protein:3,carbs:4,fat:0,portion:'100g',categories:['vegetable']},{id:'c',name:'Cheese',kcal:400,protein:25,carbs:1,fat:33,portion:'100g',categories:['dairy']}]); switchTab('log'); startNextMealFlow(); startNextMealFlow(); }""")
    page.wait_for_timeout(500)
    r = page.evaluate("""()=>{ const live=document.querySelectorAll('.mh-mealpicker-live'); const all=document.querySelectorAll('.mh-mealpicker'); const pill=c=>live[0].querySelector('.mealPillEl[data-cat="'+c+'"]');
      toggleMealPillSelection('meat', pill('meat')); toggleMealPillSelection('vegetable', pill('vegetable'));
      const on=[...live[0].querySelectorAll('.mh-meal-on')].map(e=>e.dataset.cat); const old=[...all[0].querySelectorAll('.mh-meal-on')].length; const btn=live[0].querySelector('.mealPillSendBtn'); const sendTxt=btn.textContent;
      toggleMealPillSelection('meat', pill('meat'));
      return {live:live.length, all:all.length, on, old, send:sendTxt, afterOff:[...live[0].querySelectorAll('.mh-meal-on')].map(e=>e.dataset.cat)}; }""")
    if r['live'] != 1 or r['all'] != 2: f.add('BUG', f'picker count wrong {r}')
    if r['on'] != ['meat','vegetable']: f.add('BUG', f'second pill not kept highlighted {r}')
    if r['old']: f.add('BUG', 'older picker got highlighted')
    if '2 selected' not in r['send']: f.add('BUG', f"send button text {r['send']}")
    if r['afterOff'] != ['vegetable']: f.add('BUG', f'toggling off dropped the wrong pill {r}')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
