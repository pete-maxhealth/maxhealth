#!/usr/bin/env python3
"""v1091 whole-app translation sweep writer. Merges the tables in lang_add_sweep_a.py and lang_add_sweep_b.py into lang/*.json (only keys that are absent). Rerun-safe."""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..'))
LANGS = ['es', 'de', 'fr', 'tr', 'pt', 'it', 'pl', 'nl']
T = {}
for part in ('lang_add_sweep_a.py', 'lang_add_sweep_b.py', 'lang_add_sweep_c.py', 'lang_add_sweep_d.py'):
    ns = {}; exec(open(os.path.join(HERE, part), encoding='utf-8').read(), ns); T.update(ns['T'])
ph = lambda s: sorted(re.findall(r'\{\d+\}', s))
total = 0
for i, c in enumerate(LANGS):
    path = os.path.join(ROOT, 'lang', c + '.json')
    d = json.load(open(path, encoding='utf-8')); n = 0
    # the margin-of-error sentence existed only for a fixed +-500; generalise it from the existing translation
    base = 'Margin of error about ±500 kcal/day - the gap is inside the noise, so the photo estimates cannot be shown to be off. Burn implied by the later period: {1} vs {2} kcal/day in the baseline.'
    gk = base.replace('±500', '±{1}').replace('{2}', '{3}').replace('{1} vs', '{2} vs')
    if base in d and gk not in d and '±500' in d[base]: d[gk] = d[base].replace('{2}', '{3}').replace('{1}', '{2}').replace('±500', '±{1}'); n += 1
    for k, v in T.items():
        if len(v) != 8 or ph(k) != ph(v[i]): print('BAD ENTRY', c, k[:60]); sys.exit(1)
        if k not in d: d[k] = v[i]; n += 1
    if c in ('pt', 'it', 'pl', 'nl'): out = json.dumps(d, ensure_ascii=False, indent=1)
    else: out = '{\n' + ',\n'.join(json.dumps(k, ensure_ascii=False) + ': ' + json.dumps(d[k], ensure_ascii=False) for k in sorted(d)) + '\n}\n'
    open(path, 'w', encoding='utf-8').write(out); print(c, 'added', n); total += n
print('total', total)
