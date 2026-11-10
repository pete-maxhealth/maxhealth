"""Persona 447: the v3.10.1358-1362 strings are translated (tools/lang_add_cupboard_moves.py). Pete 10 Nov: translations were on the outstanding list.
Walks, in all eight languages, the real My cupboards card: "Move to another device" and "Turn off" under it, then the three choices that open ("Phone to phone (QR)", "Send stock and list",
"Receive stock and list"). The receipt strings ("Nothing to add", "Mark all as already added", "Add it again anyway", "Go to My cupboards") are checked through the same screen translator by
putting the English text on the screen. English stays unchanged and every pack still parses. NOT walked: the full receipt-already-added screen end to end (p381 covers that screen in English)."""
import sys, json; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings(); chk = lambda ok, m: None if ok else f.add('BUG', m)
LANGS = ['es', 'de', 'fr', 'tr', 'pt', 'it', 'pl', 'nl']
KEYS = ['📲 Move to another device', '⏻ Turn off', '📲 Phone to phone (QR)', '📤 Send stock and list', '📥 Receive stock and list']
EXTRA = ['✓ Nothing to add', '✓ Mark all as already added (adds nothing)', 'Add it again anyway', '🏠 Go to My cupboards']
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    for l in LANGS + ['en']:
        d = json.load(open(f'lang/{l}.json', encoding='utf-8')) if l != 'en' else {k: k for k in KEYS + EXTRA}
        for k in KEYS + EXTRA: chk(k in d and d[k], f'0 {l}: missing {k}')
        page = b.new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); ev = page.evaluate
        page.on('pageerror', lambda e: errs.append(l + ' ' + str(e)[:160]))
        page.goto('http://localhost:5757/'); page.wait_for_timeout(800); ev(f"localStorage.setItem('mh_lang','{l}')"); page.reload(); page.wait_for_timeout(1500)
        ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()"); ev("localStorage.setItem('mh_shop_pane','stock')")
        ev("(()=>{const o=mhStockLoad(); o.enabled=true; mhStockSave(o)})()")
        ev("['Zzqx Rice','Zzqx Beans'].forEach(n=>{mhStockTrack(n,{base:'g',shop:'Asda'}); mhStockSetLevel(mhShopKey(n),400)})")
        ev("mhShopOpen()"); page.wait_for_timeout(900)
        ev("mhStockMoveToggle()"); page.wait_for_timeout(900)
        got = ev("({link: document.getElementById('mhMoveLink')?.textContent||'', off: [...document.querySelectorAll('#stockctlCard span')].map(e=>e.textContent.trim()).filter(t=>t.startsWith('⏻')), btns: [...document.querySelectorAll('#mhMoveChoices button')].map(e=>e.textContent.trim())})")
        chk(got['link'].strip() == d[KEYS[0]], f'1 {l}: move link {got["link"]!r}')
        chk(got['off'] and got['off'][0] == d[KEYS[1]], f'2 {l}: turn off {got["off"]!r}')
        chk(got['btns'] == [d[k] for k in KEYS[2:]], f'3 {l}: choices {got["btns"]!r}')
        ev("(()=>{const e=document.createElement('div'); e.id='zzx'; e.innerHTML=" + json.dumps(''.join(f'<div class="zz">{k}</div>' for k in EXTRA)) + "; document.body.appendChild(e)})()"); page.wait_for_timeout(900)
        zz = ev("[...document.querySelectorAll('#zzx .zz')].map(e=>e.textContent.trim())")
        chk(zz == [d[k] for k in EXTRA], f'4 {l}: receipt strings {zz!r}')
        page.context.close()
    if errs: f.add('BUG', f'page errors {errs[:3]}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
