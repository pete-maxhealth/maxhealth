"""Shared helper for the language-pack writers: append-only, adds only keys that are absent, keeps each file's layout.
Column order of every row: es, de, fr, tr, pt, it, pl, nl."""
import json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
LANGS = ['es', 'de', 'fr', 'tr', 'pt', 'it', 'pl', 'nl']
def apply(T):
    added = {l: 0 for l in LANGS}
    for k, v in T.items():
        if len(v) != 8: sys.exit('bad row (need 8 translations): ' + k[:60])
        for ph in set(__import__('re').findall(r'\{\d\}', k)):
            for i, t in enumerate(v):
                if ph not in t: sys.exit('placeholder %s missing in %s for: %s' % (ph, LANGS[i], k[:60]))
    for i, l in enumerate(LANGS):
        p = os.path.join(ROOT, 'lang', l + '.json'); raw = open(p, encoding='utf-8').read(); d = json.loads(raw)
        new = []
        for k, v in T.items():
            if k in d: continue
            new.append(json.dumps(k, ensure_ascii=False) + ': ' + json.dumps(v[i], ensure_ascii=False)); added[l] += 1
        if not new: continue
        if not raw.endswith('\n}\n'): sys.exit('unexpected file end: ' + l)
        out = raw[:-3] + ',\n' + ',\n'.join(new) + '\n}\n'
        json.loads(out)
        open(p, 'w', encoding='utf-8').write(out)
    print('added', added)
