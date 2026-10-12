"""Persona 103: the Food Library has a category dropdown built from what is really saved; picking one narrows the list (with the warning banner and match count),
'Show everything' resets it, it is NOT remembered after a reload; the Library chips carry icons."""
import sys; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    seed = """saveLibrary([{id:'a',name:'Chicken',kcal:200,protein:30,carbs:0,fat:8,portion:'100g',categories:['meat']},{id:'b',name:'Broccoli',kcal:30,protein:3,carbs:4,fat:0,portion:'100g',categories:['vegetable']},{id:'c',name:'Cheddar',kcal:400,protein:25,carbs:1,fat:33,portion:'100g',categories:['dairy']},{id:'d',name:'Steak',kcal:250,protein:26,carbs:0,fat:17,portion:'100g',categories:['meat']}])"""
    page.evaluate("localStorage.setItem('mh_onboarded','1')"); page.reload(); page.wait_for_timeout(1800)
    page.evaluate("document.querySelectorAll('[id*=nboard]').forEach(e=>{ if(e.style) e.style.display='none'; })")
    ev = page.evaluate
    ev(seed); ev("switchTab('log'); switchSubTab('log','library'); renderLibrary()"); page.wait_for_timeout(700)
    opts = ev("[...document.getElementById('libraryCategory').options].map(o=>o.value)")
    if opts != ['', 'dairy', 'meat', 'vegetable']: f.add('BUG', f'category options {opts}')
    names = lambda: ev("(document.getElementById('libraryIngredientsList').textContent.match(/Chicken|Broccoli|Cheddar|Steak/g)||[]).sort().join(',')")
    if names() != 'Broccoli,Cheddar,Chicken,Steak': f.add('BUG', f'all items not listed: {names()}')
    ev("document.getElementById('libraryCategory').value='meat'; renderLibrary()"); page.wait_for_timeout(300)
    if names() != 'Chicken,Steak': f.add('BUG', f'meat filter wrong: {names()}')
    ban = ev("(()=>{const b=document.getElementById('libraryFilterBanner'); return b.style.display!=='none' ? b.textContent : ''})()")
    if 'meat only' not in ban: f.add('BUG', f'banner missing: {ban}')
    if '2 matches' not in ev("document.getElementById('librarySearchCount').textContent"): f.add('BUG', 'match count missing')
    ev("document.querySelector('#libraryFilterBanner span').click()"); page.wait_for_timeout(300)
    if names() != 'Broccoli,Cheddar,Chicken,Steak' or ev("document.getElementById('libraryCategory').value") != '': f.add('BUG', 'Show everything did not reset')
    ev("document.getElementById('libraryCategory').value='dairy'; renderLibrary()"); page.wait_for_timeout(200)
    page.reload(); page.wait_for_timeout(2000); ev("switchTab('log'); switchSubTab('log','library'); renderLibrary()"); page.wait_for_timeout(500)
    if ev("document.getElementById('libraryCategory').value") != '': f.add('BUG', 'category filter survived a reload')
    chips = ev("[...document.querySelectorAll('#mhTopicBar-library .mh-grp-chip')].map(c=>c.textContent.trim())")
    if len(chips) != 6 or not all(len(c.split(' ')[0]) >= 1 and not c.split(' ')[0].isalpha() for c in chips[1:]): f.add('BUG', f'chips without icons {chips}')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
