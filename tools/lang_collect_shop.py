"""Collect the visible English phrases on the shopping screens that are not yet in the language packs (read-only: writes /tmp/sweep/untranslated.json). Run from the repo root."""
import sys, json, re; sys.path.insert(0, 'tests/personas')
from harness import *
from playwright.sync_api import sync_playwright
packs = {l: json.load(open(f'lang/{l}.json', encoding='utf-8')) for l in ['es','de','fr','tr','pt','it','pl','nl']}
have = set(packs['es'])
seen = {}
TXT = "Order: 70000012345678\nSat 9 Nov 2026 10:00 AM to 11:00 AM\nMilk, Butter & Eggs (1 item)\n1 x STORE Whole Milk 2 Litres\nFrozen Vegetables (1 item)\n2 x STORE Sliced Mushrooms 600g\nHousehold (1 item)\n1 x STORE Washing Pods 30\nCooking (1 item)\n1 x STORE Zzqx Unknown Spread 350g\n"
JS = """() => { const out = new Set(); const add = s => { s = (s||'').replace(/\\s+/g,' ').trim(); if (s.length > 2) out.add(s); };
 const w = document.createTreeWalker(document.getElementById('shop')||document.body, NodeFilter.SHOW_TEXT);
 while (w.nextNode()) { const p = w.currentNode.parentElement; if (!p || /SCRIPT|STYLE/.test(p.tagName)) continue; if (p.offsetParent === null && p.tagName !== 'OPTION') continue; add(w.currentNode.nodeValue); }
 document.querySelectorAll('#shop [placeholder],#shop [title],#shop [aria-label]').forEach(e => { add(e.getAttribute('placeholder')); add(e.getAttribute('title')); add(e.getAttribute('aria-label')); });
 return [...out]; }"""
def grab(page, tag):
    for s in page.evaluate(JS):
        if re.search(r'[A-Za-z]{3}', s) and s not in have: seen.setdefault(s, tag)
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); ev = page.evaluate; errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:150])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("(()=>{const o=mhStockLoad(); o.enabled=true; mhStockSave(o)})()")
    ev("saveLibrary([{id:'a',name:'Whole Milk',kcal:60,protein:3.4,carbs:4.7,fat:3.6,portion:'100ml'},{id:'b',name:'Sliced Mushrooms',kcal:22,protein:3,carbs:0.5,fat:0.3,portion:'100g'},{id:'c',name:'Rice',kcal:130,protein:2.7,carbs:28,fat:0.3,portion:'100g'}])")
    ev("[['Whole Milk','ml',1000,'fridge'],['Sliced Mushrooms','g',600,'freezer'],['Rice','g',500,'']].forEach(([n,b,l,s])=>{mhStockTrack(n,{base:b,shop:'Asda'}); mhStockSetLevel(mhShopKey(n),l); if(s) mhStockSetStore(mhShopKey(n),s)})")
    for pane in ('list', 'stock'):
        ev(f"localStorage.setItem('mh_shop_pane','{pane}')"); ev("mhShopOpen()"); page.wait_for_timeout(700); grab(page, 'pane ' + pane)
    for v in ('stocklist','recipes','usuals','quick','lists','sync','csvimport','picker'):
        try: ev(f"mhShopView('{v}')"); page.wait_for_timeout(500); grab(page, 'view ' + v)
        except Exception as e: print('skip', v, str(e)[:80])
    for kind in ('receipt', 'order', 'start', 'list'):
        try:
            ev("switchTabById('shop'); mhShopView('orderimport')"); ev(f"mhOrdOpen('{kind}')"); page.wait_for_timeout(500); grab(page, 'import ' + kind + ' start')
            ev("t=>mhOrdLoad(t,'x')", TXT); page.wait_for_timeout(700); grab(page, 'import ' + kind + ' review')
            ev("mhOrdApply()"); page.wait_for_timeout(600); grab(page, 'import ' + kind + ' after add')
            ev("t=>mhOrdLoad(t,'x')", TXT); page.wait_for_timeout(700); grab(page, 'import ' + kind + ' repeat')
        except Exception as e: print('skip', kind, str(e)[:100])
    print('page errors', errs[:3])
json.dump(seen, open('/tmp/sweep/untranslated.json', 'w'), ensure_ascii=False, indent=1)
print(len(seen), 'untranslated phrases')
