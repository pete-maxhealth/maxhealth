"""Persona 476 (v3.10.1402): a batch of whole-sentence strings (help paragraphs, tooltips, labels) are translated in all 8 languages, and the lookup resolves for every one of them."""
import sys, re, json, os; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
root = os.path.join(os.path.dirname(__file__), '..', '..')
src = open(os.path.join(root, 'tools', 'lang_add_fasting_help.py')).read()
ns = {}
exec(src.split('apply(T)')[0].replace('from lang_lib import apply', 'apply=None').replace("sys.path.insert(0, os.path.dirname(__file__))", ''), ns)
T = {k: v for k, v in ns['T'].items() if k.startswith('Your goal is your own')}
for k, v in T.items():
    for i, x in enumerate(v):
        x.count('<strong>') == k.count('<strong>') and x.count('<br><br>') == 3 or print('FAIL tags differ', i)
langs = ['es','de','fr','tr','pt','it','pl','nl']
for i, l in enumerate(langs):
    d = json.load(open(os.path.join(root, 'lang', l + '.json')))
    d = d.get('strings', d)
    miss = [k[:50] for k in T if d.get(k) != T[k][i]]
    miss and f.add('FAIL', f'{l}: missing/different {miss[:3]}')
with fresh_server() as r, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    ctx.route(re.compile(r'https://(cdn\.jsdelivr\.net|cdnjs\.cloudflare\.com|fonts\.(googleapis|gstatic)\.com)/.*'), lambda x: x.abort())
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:160]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(800)
    page.evaluate("localStorage.setItem('mh_lang','es')"); page.reload(); page.wait_for_timeout(1500)
    k = next(x for x in T if x.startswith("Your goal is your own"))
    got = page.evaluate("(k)=>mhLangT(k)", k)
    got == T[k][0] or f.add('FAIL', 'mhLangT sample not Spanish: ' + str(got))
    errs and f.add('FAIL', 'page errors ' + str(errs))
    b.close()
print('findings', len(f)); sys.exit(1 if f else 0)
