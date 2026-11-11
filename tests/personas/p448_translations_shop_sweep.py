"""Persona 448: the shopping screens are translated (tools/lang_add_shop_sweep_a/b/c/d.py). Pete 10 Nov: translation sweep for shopping, My cupboards, receipt, Use by and plan wording.
Walks the same screens the collector (tools/lang_collect_shop.py) lists, in all eight languages: both Shopping panes, the stock list, recipes, usuals, quick, saved lists, other phone, CSV import and picker, and the
four Import kinds (receipt, order, starting my cupboards, a list) through start, review, after Add and the repeat warning. Every English phrase that was found untranslated (tests/personas/p448_phrases.json) must no
longer appear verbatim unless the language genuinely uses the same word (the page's own translator is asked). Then, in each language, an order import is applied and the stock and its stores come out the same as in
English, and the Kept in / Bought at choices keep their English values (only their text is translated). NOT covered (listed as gaps): "Bought at: <shop>", "Save <shop> (n)" and "My usuals (<shop>)" because the shop
name is part of the same text; shop and food names are data and stay as typed; dates follow the language but are not checked word by word."""
import sys, json, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings(); chk = lambda ok, m: None if ok else f.add('BUG', m)
LANGS = ['en', 'es', 'de', 'fr', 'tr', 'pt', 'it', 'pl', 'nl']
src = open('tools/lang_collect_shop.py', encoding='utf-8').read(); ns = {}
exec(re.search(r'^TXT = .*$', src, re.M).group(0), ns); exec(re.search(r'^JS = """.*?"""', src, re.M | re.S).group(0), ns)
TXT, JS = ns['TXT'], ns['JS']
ATTRS = ['Details', 'Show it in my cupboards', 'Someone else ate it: take it off stock', '🔍 Search, or add a food', 'Kept in: cupboard (tap to change)', 'Kept in: fridge (tap to change)', 'Kept in: freezer (tap to change)', 'Running low: put it on my shopping list', 'Used up or binned', 'Remove from my cupboards', 'Search your library and cupboards (any words, any order)', 'Tick to change several at once', 'Counted in', 'Search your ingredients, or type a new one', 'Search ingredients', 'Paste your receipt, order or list here', 'On your shopping list (tap to take it off)', 'e.g. 9 pack', 'e.g. 125 g', 'e.g. 500 g', 'e.g. 30', 'e.g. 1 pack or 500 g', 'e.g. Weekly shop', 'e.g. Butchers']
PHRASES = json.load(open('tests/personas/p448_phrases.json', encoding='utf-8'))
def walk(page, ev, grab):
    for pane in ('list', 'stock'):
        ev(f"localStorage.setItem('mh_shop_pane','{pane}')"); ev("mhShopOpen()"); page.wait_for_timeout(600); grab()
    for v in ('stocklist', 'recipes', 'usuals', 'quick', 'lists', 'sync', 'csvimport', 'picker'):
        try: ev(f"mhShopView('{v}')"); page.wait_for_timeout(400); grab()
        except Exception as e: f.add('BUG', f'view {v} failed: {str(e)[:80]}')
    for kind in ('receipt', 'order', 'start', 'list'):
        try:
            ev("switchTabById('shop'); mhShopView('orderimport')"); ev(f"mhOrdOpen('{kind}')"); page.wait_for_timeout(400); grab()
            ev("t=>mhOrdLoad(t,'x')", TXT); page.wait_for_timeout(600); grab()
            ev("mhOrdApply()"); page.wait_for_timeout(500); grab()
            ev("t=>mhOrdLoad(t,'x')", TXT); page.wait_for_timeout(600); grab()
        except Exception as e: f.add('BUG', f'import {kind} failed: {str(e)[:100]}')
base = {}
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    for l in LANGS:
        page = b.new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); ev = page.evaluate
        page.on('pageerror', lambda e: errs.append(l + ' ' + str(e)[:150])); page.on('dialog', lambda d: d.accept())
        page.goto('http://localhost:5757/'); page.wait_for_timeout(800)
        ev(f"localStorage.setItem('mh_lang','{l}')" if l != 'en' else "localStorage.removeItem('mh_lang')"); page.reload(); page.wait_for_timeout(1500)
        ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
        ev("(()=>{const o=mhStockLoad(); o.enabled=true; mhStockSave(o)})()")
        ev("saveLibrary([{id:'a',name:'Whole Milk',kcal:60,protein:3.4,carbs:4.7,fat:3.6,portion:'100ml'},{id:'b',name:'Sliced Mushrooms',kcal:22,protein:3,carbs:0.5,fat:0.3,portion:'100g'},{id:'c',name:'Rice',kcal:130,protein:2.7,carbs:28,fat:0.3,portion:'100g'}])")
        ev("[['Whole Milk','ml',1000,'fridge'],['Sliced Mushrooms','g',600,'freezer'],['Rice','g',500,'']].forEach(([n,b,l,s])=>{mhStockTrack(n,{base:b,shop:'Asda'}); mhStockSetLevel(mhShopKey(n),l); if(s) mhStockSetStore(mhShopKey(n),s)})")
        seen = set(); 
        def grab():
            for s in ev(JS): seen.add(s)
        walk(page, ev, grab)
        if l != 'en':
            left = []
            for p in PHRASES:
                if p not in seen: continue
                tr = ev("(p)=>{const d=MH_L.dict; if(!d) return null; const k=mhLangNorm(p); if(Object.prototype.hasOwnProperty.call(d,k)) return d[k]; const pt=mhLangPat(k,d); if(pt) return pt; if(k===k.toUpperCase()&&k!==k.toLowerCase()){const lk=k.toLowerCase(); const hit=Object.keys(d).find(e=>e.toLowerCase()===lk&&e!==lk||e===lk); if(hit) return d[hit].toLocaleUpperCase(MH_L.code)} return null}", p)
                if tr is None: left.append(p)
            chk(not left, f'1 {l}: still English on the shopping screens ({len(left)}): {left[:4]}')
        else:
            chk(len(PHRASES) - sum(1 for p in PHRASES if p in seen) <= 12, f'0 en: walk no longer shows the sample phrases (only {sum(1 for p in PHRASES if p in seen)} of {len(PHRASES)} seen)')
        if l != 'en':
            d = json.load(open(f'lang/{l}.json', encoding='utf-8')); miss = [a for a in ATTRS if a not in d]
            chk(not miss, f'4 {l}: hover tips / hints without a translation: {miss[:3]}')
            ev("localStorage.setItem('mh_shop_pane','stock'); mhShopOpen()"); page.wait_for_timeout(700)
            ph = ev("document.getElementById('mhCbQ')?.placeholder || ''")
            chk(ph == d['🔍 Search, or add a food'], f'5 {l}: search box hint shows {ph!r}')
        ev("switchTabById('shop'); mhShopView('stocklist')"); page.wait_for_timeout(500)
        vals = ev("[...document.querySelectorAll('#mhSlBulkStore option')].map(o=>o.value)")
        st = ev("(()=>{const o=mhStockLoad(); return Object.keys(o.items).sort().map(k=>k+':'+(o.items[k].store||''))})()")
        if l == 'en': base['vals'], base['st'] = vals, st
        else:
            chk(vals == base['vals'], f'2 {l}: Kept in values changed {vals}')
            chk(st == base['st'], f'3 {l}: stock after the same imports differs from English {st} vs {base["st"]}')
        page.context.close()
    if errs: f.add('BUG', f'page errors {errs[:3]}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
