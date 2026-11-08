#!/usr/bin/env python3
"""Adds the v3.10.1330 range labels and the weekly/monthly sleep chart headings to lang/*.json. Only adds keys that are absent.
Column order: es, de, fr, tr, pt, it, pl, nl. Machine-assisted wording, not native-speaker checked (same as the other packs).
@BTN@ and @PRV@ in a value are filled from each pack's own "GENERATE CARER VIEW LINK" and "Preview" so the steps name the buttons exactly as that pack does."""
import json, os, re, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
LANGS = ['es', 'de', 'fr', 'tr', 'pt', 'it', 'pl', 'nl']
T = {
 'EACH WEEK, AVERAGE NIGHT (LINE = {1})': ['CADA SEMANA, NOCHE MEDIA (LÍNEA = {1})', 'JEDE WOCHE, DURCHSCHNITTSNACHT (LINIE = {1})', 'CHAQUE SEMAINE, NUIT MOYENNE (LIGNE = {1})', 'HER HAFTA, ORTALAMA GECE (ÇİZGİ = {1})', 'CADA SEMANA, NOITE MÉDIA (LINHA = {1})', 'OGNI SETTIMANA, NOTTE MEDIA (LINEA = {1})', 'KAŻDY TYDZIEŃ, ŚREDNIA NOC (LINIA = {1})', 'ELKE WEEK, GEMIDDELDE NACHT (LIJN = {1})'],
 'EACH MONTH, AVERAGE NIGHT (LINE = {1})': ['CADA MES, NOCHE MEDIA (LÍNEA = {1})', 'JEDER MONAT, DURCHSCHNITTSNACHT (LINIE = {1})', 'CHAQUE MOIS, NUIT MOYENNE (LIGNE = {1})', 'HER AY, ORTALAMA GECE (ÇİZGİ = {1})', 'CADA MÊS, NOITE MÉDIA (LINHA = {1})', 'OGNI MESE, NOTTE MEDIA (LINEA = {1})', 'KAŻDY MIESIĄC, ŚREDNIA NOC (LINIA = {1})', 'ELKE MAAND, GEMIDDELDE NACHT (LIJN = {1})'],
 'Last 7 days': ['Últimos 7 días', 'Letzte 7 Tage', '7 derniers jours', 'Son 7 gün', 'Últimos 7 dias', 'Ultimi 7 giorni', 'Ostatnie 7 dni', 'Afgelopen 7 dagen'],
 'Last 12 months': ['Últimos 12 meses', 'Letzte 12 Monate', '12 derniers mois', 'Son 12 ay', 'Últimos 12 meses', 'Ultimi 12 mesi', 'Ostatnie 12 miesięcy', 'Afgelopen 12 maanden'],
 'Custom dates': ['Fechas personalizadas', 'Eigener Zeitraum', 'Dates personnalisées', 'Özel tarihler', 'Datas personalizadas', 'Date personalizzate', 'Własne daty', 'Eigen datums'],
 'Next 7 days': ['Próximos 7 días', 'Nächste 7 Tage', '7 prochains jours', 'Sonraki 7 gün', 'Próximos 7 dias', 'Prossimi 7 giorni', 'Następne 7 dni', 'Komende 7 dagen'],
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
