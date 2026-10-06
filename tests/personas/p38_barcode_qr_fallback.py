"""Persona 38: a QR code (Instagram link) is not treated as a product barcode; a not-found barcode offers to read the label with AI."""
import sys, re, json; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    def route(r):
        u = r.request.url
        if u.startswith('http://localhost'): return r.continue_()
        if 'openfoodfacts' in u:
            return r.fulfill(status=200, content_type='application/json', headers={'access-control-allow-origin': '*'}, body=json.dumps({'status': 0}))
        r.abort()
    ctx.route(re.compile(r'^https?://'), route)
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:160])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200)
    page.evaluate("onboardNext(2)"); page.fill('#onboardName', 'Ola'); page.evaluate("onboardNext(3)")
    page.evaluate("obSetSex('male')"); page.fill('#onboardAge', '58'); page.fill('#onboardHeight', '176')
    page.fill('#onboardWeight', '82'); page.fill('#onboardTarget', '78')
    page.evaluate("onboardNext(4)"); page.evaluate("obSetActivity('light')"); page.evaluate("obSetGoal('lose')")
    page.evaluate("onboardNext(5)"); page.evaluate("obSetCondition('general')")
    page.evaluate("onboardNext(6)"); page.evaluate("onboardFinish()"); page.wait_for_timeout(1500)
    r = page.evaluate("""[
      mhProductCode([{rawValue:'https://www.instagram.com/luvbiltongsnacks/'}]),
      mhProductCode([{rawValue:'https://x.com'},{rawValue:'5065015932000'}]),
      mhProductCode([{rawValue:'ABC-123'}]),
      mhProductCode([])]""")
    if r != [None, '5065015932000', None, None]: f.add('BUG', f'mhProductCode wrong: {r}')
    page.evaluate("switchTabById('log')"); page.wait_for_timeout(300)
    page.evaluate("_lastBarcodeImage='data:image/jpeg;base64,/9j/4AAQ'; const b=addBubble('x','system','thinking'); lookupBarcode('5065015932000', b)")
    page.wait_for_timeout(1200)
    btn = page.locator('button', has_text='Read the label with AI instead')
    if btn.count() != 1: f.add('BUG', 'no label-read button after not-found barcode')
    else:
        btn.evaluate("b=>b.click()"); page.wait_for_timeout(300)
        if page.evaluate("_pendingPhotoBase64") != '/9j/4AAQ': f.add('BUG', 'label photo not attached for AI')
        if btn.count(): f.add('BUG', 'button stayed after use')
    if errs: f.add('JS-exception', str(errs[:3]))
    b.close()
print('findings', len(f)); sys.exit(1 if f else 0)
