"""Persona 341 (v3.10.1226): Settings > Data rows that can travel by QR carry a QR tag; the ones that cannot (wearable history, devices, full backup) do not,
and the '?' explains why. The QR screen help names what is never sent."""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
bad = []
def check(n, ok, info=''):
    print(('PASS ' if ok else 'FAIL ') + n + (f'  {info}' if info and not ok else ''))
    if not ok: bad.append(n)
SHOT = '/tmp/claude-0/-home-claude/c032a46b-68f2-5aea-a854-98f1a5b7657c/scratchpad/xfer/'
with fresh_server() as root, sync_playwright() as pw:
    br = pw.chromium.launch(); ctx = br.new_context(viewport={'width': 430, 'height': 900}, service_workers='block'); p = ctx.new_page()
    errs = []; p.on('pageerror', lambda e: errs.append(str(e)[:200])); p.on('dialog', lambda d: d.accept())
    p.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    p.goto('http://localhost:5757/'); p.wait_for_timeout(1200); p.evaluate("state.onboarded=true; saveState()"); p.reload(); p.wait_for_timeout(1500)
    rows = p.evaluate("""(()=>{const d=document.createElement('div');d.innerHTML=buildBulkDataActionsCard();
      return [...d.querySelectorAll('#bulkDsList label')].map(l=>[l.querySelector('input').value, /\\bQR\\s*$/.test(l.textContent.trim())])})()""")
    m = dict(rows)
    yes = ['master','library','recipes','routines','supplements','strength','stock','shoplist','symptoms','treatments','reports','tableware','layout']
    no = ['combined','devices','fullstate']
    check('QR rows tagged', all(m.get(k) for k in yes), str(m))
    check('non-QR rows untagged', not any(m.get(k) for k in no), str(m))
    check('all 16 rows still listed', len(rows) == 16, str(len(rows)))
    html = p.evaluate("buildBulkDataActionsCard()")
    check('why-not help present', 'data-id="bulkqrwhy"' in html and 'too many codes' in html and 'licence' in html)
    check('QR screen help names what never goes', 'Not sent by QR, and why' in open('maxhealth.html').read())
    p.evaluate("(h)=>{let d=document.createElement('div');d.id='tmpBulk';d.style.cssText='position:fixed;inset:0;z-index:9000;background:var(--bg);overflow:auto;padding:16px';d.innerHTML=h;document.body.appendChild(d)}", html)
    p.wait_for_timeout(300); p.screenshot(path=SHOT + 'bulk_qr_tags.png')
    check('no page errors', not errs, str(errs))
    br.close()
print('FAILED: ' + ', '.join(bad) if bad else 'ALL PASS'); sys.exit(1 if bad else 0)
