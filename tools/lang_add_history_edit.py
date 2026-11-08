#!/usr/bin/env python3
"""Adds the v3.10.1323 History strings (tap Water/Weight to edit, + Water) to lang/*.json. Only adds keys that are absent.
Column order: es, de, fr, tr, pt, it, pl, nl. Machine-assisted wording, not native-speaker checked (same as the other packs).
@BTN@ and @PRV@ in a value are filled from each pack's own "GENERATE CARER VIEW LINK" and "Preview" so the steps name the buttons exactly as that pack does."""
import json, os, re, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
LANGS = ['es', 'de', 'fr', 'tr', 'pt', 'it', 'pl', 'nl']
T = {
 '💧 + Water': ['💧 + Agua', '💧 + Wasser', '💧 + Eau', '💧 + Su', '💧 + Água', '💧 + Acqua', '💧 + Woda', '💧 + Water'],
 'Edit water for this day': ['Editar el agua de este día', 'Wasser für diesen Tag bearbeiten', 'Modifier l’eau de ce jour', 'Bu günün su miktarını düzenle', 'Editar a água deste dia', 'Modifica l’acqua di questo giorno', 'Edytuj wodę z tego dnia', 'Water van deze dag bewerken'],
 'Edit weight for this day': ['Editar el peso de este día', 'Gewicht für diesen Tag bearbeiten', 'Modifier le poids de ce jour', 'Bu günün kilosunu düzenle', 'Editar o peso deste dia', 'Modifica il peso di questo giorno', 'Edytuj wagę z tego dnia', 'Gewicht van deze dag bewerken'],
}
added = {l: 0 for l in LANGS}
for i, l in enumerate(LANGS):
    p = os.path.join(ROOT, 'lang', l + '.json'); d = json.load(open(p, encoding='utf-8'))
    btn = re.sub(r'^\W+', '', d.get('👁 GENERATE CARER VIEW LINK', 'GENERATE CARER VIEW LINK')); prv = d.get('Preview', 'Preview')
    for k, v in T.items():
        if len(v) != 8: sys.exit('bad row: ' + k[:40])
        if k in d: continue
        d[k] = v[i].replace('@BTN@', btn).replace('@PRV@', prv); added[l] += 1
    if l in ('pt', 'it', 'pl', 'nl'): out = json.dumps(d, ensure_ascii=False, indent=1)      # these files: insertion order, no trailing newline (same as lang_add_today.py)
    else: out = '{\n' + ',\n'.join(json.dumps(k, ensure_ascii=False) + ': ' + json.dumps(d[k], ensure_ascii=False) for k in sorted(d)) + '\n}\n'
    open(p, 'w', encoding='utf-8').write(out)
print('added', added)
