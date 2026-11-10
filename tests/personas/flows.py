"""Shared flow set-up for the click and house-rules tests (p404, p405): invented foods, an invented order, the control scanner, and set-up of each recently changed flow."""
import re, json
FOODS = [('Zzqx Chicken Breast', 'meat'), ('Zzqx Mince', 'meat'), ('Zzqx Cheddar', 'dairy'), ('Zzqx Milk', 'dairy'), ('Zzqx Apples', 'fruit'),
         ('Zzqx Carrots', 'vegetable'), ('Zzqx Rice', 'grain'), ('Zzqx Beans', 'beansandpulses'), ('Zzqx Bread Rolls', 'bread')]
ORDER = "\n".join(f"1 x {n} 400g\t£1.00" for n, _ in FOODS) + "\n1 x Zzqx Washing Pods 30\t£4.00"
SCAN = """() => { const sel = 'button, [onclick], summary, [role=button], .tab-btn, input[type=checkbox], select'; const out = [];
  const vis = e => { const r = e.getBoundingClientRect(), s = getComputedStyle(e); return r.width > 4 && r.height > 4 && s.visibility !== 'hidden' && s.display !== 'none' && !e.closest('#onboardingOverlay'); };
  document.querySelectorAll(sel).forEach((e, i) => { if (!vis(e)) return; out.push({ i, t: ((e.innerText || e.getAttribute('aria-label') || e.title || e.value || '') + '').trim().slice(0, 50), oc: (e.getAttribute('onclick') || '').slice(0, 80) }); });
  return out; }"""
TEXT = """() => { const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); let o = [], n; while (n = w.nextNode()) { const e = n.parentElement; if (!e || ['SCRIPT','STYLE'].includes(e.tagName)) continue; const r = e.getBoundingClientRect(); if (r.width > 0 && r.height > 0) o.push(n.textContent); } return o.join(' '); }"""
DUPS = """() => { const seen = {}, d = []; document.querySelectorAll('[id]').forEach(e => { if (seen[e.id]) d.push(e.id); seen[e.id] = 1; }); return [...new Set(d)]; }"""
STORE = """() => { const bad = []; for (let i = 0; i < localStorage.length; i++) { const k = localStorage.key(i); if (!k.startsWith('mh_')) continue; const v = localStorage.getItem(k); if (v && /^[\\[{]/.test(v)) { try { JSON.parse(v); } catch (e) { bad.push(k); } } } return bad; }"""
COUNTS = """() => { const n = k => { try { const v = JSON.parse(localStorage.getItem(k) || 'null'); return Array.isArray(v) ? v.length : (v && typeof v === 'object' ? Object.keys(v).length : 0); } catch (e) { return -1; } }; return { lib: n('mh_library'), stock: (typeof loadStock === 'function' ? Object.keys(loadStock() || {}).length : 0) }; }"""

def setup(page, name):
    ev = page.evaluate
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1000)
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')&&(document.getElementById('onboardingOverlay').style.display='none')")
    ev("startDemoMode('doris')"); page.wait_for_timeout(1800)   # Pete 6 Nov: destructive tests run in the demo persona, where nothing real is saved
    ev("document.getElementById('onboardingOverlay')&&(document.getElementById('onboardingOverlay').style.display='none')")
    ev("l=>{const lib=loadLibrary(); l.forEach(([n,c])=>lib.push({name:n,kcal:100,protein:5,carbs:5,fat:5,categories:[c],portion:'100g',per100g:true})); saveLibrary(lib)}", FOODS)
    if name == 'import_review':
        ev("switchTabById('shop'); mhOrdOpen('order')"); page.wait_for_timeout(300); ev("t=>mhOrdLoad(t,'p404')", ORDER); page.wait_for_timeout(500)
    elif name == 'import_after_partial_add':
        ev("switchTabById('shop'); mhOrdOpen('order')"); page.wait_for_timeout(300); ev("t=>mhOrdLoad(t,'p404')", ORDER); page.wait_for_timeout(500)
        ev("mhOrdAll(false); _shopUi.ord.rows.slice(0,3).forEach(r=>{r.amount=r.amount||'400 g'; r.on=true})")
        try: ev("mhOrdApplyList&&mhOrdApplyList()")
        except Exception: pass
        page.wait_for_timeout(400)
    elif name == 'suggestion_cards':
        ev("switchTabById('chat')")
        ev("()=>renderLibraryComboSuggestions({combos:[{items:['Zzqx Rice','Zzqx Beans'],note:'round one'}]}, loadLibrary(), [], {})")
        ev("()=>renderLibraryComboSuggestions({combos:[{items:['Zzqx Cheddar'],note:'round two'}]}, loadLibrary(), [], {})"); page.wait_for_timeout(300)
    elif name == 'shopping_list':
        ev("switchTabById('shop')"); ev("()=>{try{['Zzqx Milk','Zzqx Apples','Zzqx Rice'].forEach(n=>mhShopAddName&&mhShopAddName(n))}catch(e){}}"); page.wait_for_timeout(400)
    elif name == 'my_cupboards':
        ev("switchTabById('shop')"); page.wait_for_timeout(300)
        ev("()=>{try{const s=loadStock?loadStock():{}; ['Zzqx Milk','Zzqx Rice','Zzqx Mince'].forEach(n=>{s[n.toLowerCase()]={name:n,qty:2,unit:'x'}}); saveStock&&saveStock(s)}catch(e){}}")
    elif name == 'log_search_from_import':
        ev("switchTabById('shop'); mhOrdOpen('order')"); page.wait_for_timeout(300); ev("t=>mhOrdLoad(t,'p404')", ORDER); page.wait_for_timeout(500)
        ev("()=>{try{_shopUi.ord.rows[0].create=true; mhOrdFind(0,'search')}catch(e){}}"); page.wait_for_timeout(500)
    elif name == 'compare_metrics_foods':
        ev("switchTabById('insights')"); page.wait_for_timeout(300)
        ev("openMultiMetricOverlay()"); page.wait_for_timeout(600); ev("toggleMMGroup('Foods')"); page.wait_for_timeout(300)
        ev("()=>{const i=mmFoodIndex(); const f=[...i.foods.values()].sort((a,b)=>b.days.size-a.days.size).slice(0,2); const c=[...i.cats.values()][0]; [...f,c].filter(Boolean).forEach((x,n)=>{const b=document.createElement('button'); b.dataset.k=x.k; b.dataset.t=x.t||x.k; b.dataset.c=(x===c)?'1':'0'; mmFoodAdd(b)})}"); page.wait_for_timeout(600)
    page.wait_for_timeout(300)


FOLD = """() => [...document.querySelectorAll('details, [aria-expanded], [data-ord-sec]')].map(e => (e.tagName === 'DETAILS' ? e.open : e.getAttribute('aria-expanded')) + '|' + (e.id || e.dataset.ordSec || (e.innerText || '').slice(0, 12))).join(';')"""
OVERLAYS = """() => [...document.querySelectorAll('body *')].filter(e => { const s = getComputedStyle(e); if (s.position !== 'fixed') return false; const r = e.getBoundingClientRect(); return r.width > innerWidth * 0.6 && r.height > innerHeight * 0.4 && s.display !== 'none' && s.visibility !== 'hidden' && !/^(ytC|ytH)$/.test(e.id); }).length"""
CLOSER = """() => { const o = [...document.querySelectorAll('body *')].filter(e => { const s = getComputedStyle(e); if (s.position !== 'fixed') return false; const r = e.getBoundingClientRect(); return r.width > innerWidth * 0.6 && r.height > innerHeight * 0.4 && s.display !== 'none' && s.visibility !== 'hidden'; }).pop(); if (!o) return false; const c = [...o.querySelectorAll('button, [onclick], span, div')].find(e => /^(×|✕|x|←|‹|‹ back|← back|close|cancel|back|done|✓ done)$/i.test((e.innerText || e.getAttribute('aria-label') || '').trim())); if (c) { c.click(); return true; } return false; }"""
TOGGLE = re.compile(r'open|close|fold|▸|▾|▴|toggle|show|hide|filter|expand|collapse|default|section|tab', re.I)
