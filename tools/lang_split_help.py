#!/usr/bin/env python3
"""v3.10.1301: long explainers moved behind a "?" were split into a short visible line and a hidden rest, so their old whole-text pack keys no longer match.
This adds the pieces to lang/*.json by cutting each existing translation at the same point as the English (first/second sentence, colon or dash).
Only adds keys that are absent; skips a language where the translation does not cut cleanly (that piece then stays English, as the app already allows)."""
import json, os, re, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
LANGS = ['es', 'de', 'fr', 'tr', 'pt', 'it', 'pl', 'nl']
norm = lambda t: re.sub(r'\s+', ' ', t).strip()
DASH = r'\s[—–-]\s'
def cut(t, how):
    """how = ('dot', n) nth sentence end; ('colon',); ('dash', n) nth spaced dash. returns (head, tail) or None"""
    if how[0] == 'colon': m = re.search(r':\s+', t); return (t[:m.start()], t[m.end():]) if m else None
    if how[0] == 'dot':
        ms = list(re.finditer(r'(?<=[.!?])\s+(?=\S)', t)); n = how[1]
        return (t[:ms[n-1].start()], t[ms[n-1].end():]) if len(ms) >= n else None
    if how[0] == 'dash':
        ms = list(re.finditer(DASH, t)); n = how[1]
        return (t[:ms[n-1].start()], t[ms[n-1].end():]) if len(ms) >= n else None
cap = lambda t: re.sub(r'^(\W*)(\w)', lambda m: m.group(1) + m.group(2).upper(), t, count=1)
dot = lambda t: t if t[-1:] in '.!?' else t + '.'
# (original English text node, how to cut, English head as shown now, English tail as shown now)
CASES = [
 ("Ask your own data a question and keep the answer: top foods, calories per week, your biggest lifts, whatever you like. Save as many as you want, copy or download them to share, and delete what you no longer need.", ('colon',), None, None),
 ("Reports is for period analysis — looking across days, weeks and months to find patterns. Use the Query Builder to filter any column from your wearable and nutrition data. Save queries to re-run with fresh dates.", ('dot', 1), None, None),
 ("English is the default and always one tap away. Translations cover most screens; anything not translated yet stays in English. Health wording is machine-assisted and has not been checked by clinicians who speak the language, so check anything important in English. Medical terms with no safe translation are left in English rather than guessed. If any English is left, use ✨ next to the flag.", ('dot', 1), None, None),
 ("Type in readings by hand for a date — works like importing a device's CSV, feeding the same pipeline every other device uses. A value entered here always wins for that date, whatever a device already recorded.", ('dash', 1), None, None),
 ("Filling in many days at once? Download a blank CSV with your current fields as columns, fill it in (a spreadsheet app, or any export you can copy values from), then upload it back — no device mapping needed, since the column headers already match this app's own.", ('dot', 1), None, None),
 ("Not enough paired data yet to surface a genuine pattern — group checks need at least {1} days in each comparison group (or the difference found wasn't large enough to be worth mentioning); the early-warning checks need 20+ baseline days plus 5 recent ones.", ('dash', 1), None, None),
 ("(the default) shows the raw carbs figure exactly as printed on the label — polyols (sugar alcohols like erythritol, xylitol) are still counted in full, since that's how UK/EU labels state the number.", ('dash', 1), None, None),
 ("Calories = MET × weight (kg) × hours. For walks, runs and rides with a distance and a time, the MET follows your real speed (2011 Compendium of Physical Activities, level ground); otherwise it follows the Easy / Moderate / Hard level. Counted net of resting energy (MET minus 1), because your daily target already includes what you would burn sitting still. Once your watch has calibrated a kind of exercise, its measured ratio replaces this. Pick Gross to count the full MET value instead.", ('dot', 1), None, None),
 ("Off by default (shows total/gross carbs). Deliberately does not also subtract fibre — UK/EU labels already exclude fibre from the printed carbs figure before it reaches this app (fibre is its own separate line, not part of the carbohydrate total the way US labelling includes it), so subtracting it again would double-count something already excluded. Only reliably applied to recent days with real polyol data recorded — older days may not have it.", ('dot', 1), None, None),
 ("Your daily step baseline (default 7,500, set above) represents ordinary day-to-day movement assumed already accounted for. Steps beyond a logged walk's own estimated count, and beyond this baseline, are credited as additional \"Easy effort\" activity calories — steps within the baseline add nothing extra, since that's the assumption already built into your calorie target.", ('dot', 1), None, None),
 ("Weather comes from the free Open-Meteo service for the town you choose on Today (only rounded coordinates are sent). These are rule-of-thumb guides, not clinical advice or measurements, and your own \"Not right? Adjust\" figure always overrides the forecast. Weather never changes your calorie, protein or carb targets.", ('dot', 1), None, None),
 ("Pauses the app's own background activity (notification checks, chart updates) after a period with no taps, scrolls, or typing - genuinely reduces what the app is doing while you're not actually using it, rather than it quietly running in the background the whole time the tab is open. Nothing you've typed or logged is ever lost - it's a pause, not a reset.", ('dash', 1), None, None),
 ("Lost your way? This puts the cards back to their standard open/closed state, order and visibility on every screen. Nothing you have logged is touched. Each screen also has its own ↺ Default button beside Open all / Close all.", ('dot', 2), None, None),
 ("Track whatever's actually relevant to you day to day - energy, cognitive clarity, sleep quality, headaches, mood, or anything else. Logged 1-5 daily from the Today dashboard. Nothing is tracked by default; add what you actually want to watch.", ('dot', 1), None, None),
 ("Track sessions of anything you do outside normal daily logging — PEMF, physio, massage, or anything else — with a real timestamp per session, not just a daily yes/no. That's what makes \"how did I do in the days around this session\" a question Reports can actually answer later. Nothing tracked by default; add what's actually relevant to you.", ('dot', 1), None, None),
 ("Set up a reusable report for sending to a treatment provider, clinician, coach, or anyone else you're sharing regular progress with — pick the treatment it's about, which metrics matter, and an optional reminder. Nothing is sent automatically; you review and send it yourself each time.", ('dot', 1), None, None),
]
LEADS = {  # new visible lines that had no earlier text to cut from; column order es de fr tr pt it pl nl
 "How the filter row, starter packs, nudges and voice commands work.": ["Cómo funcionan la fila de filtros, los paquetes iniciales, los avisos y los comandos de voz.", "So funktionieren die Filterzeile, Startpakete, Hinweise und Sprachbefehle.", "Comment fonctionnent la barre de filtres, les packs de démarrage, les rappels et les commandes vocales.", "Filtre satırı, başlangıç paketleri, hatırlatmalar ve sesli komutlar nasıl çalışır.", "Como funcionam a barra de filtros, os pacotes iniciais, os lembretes e os comandos de voz.", "Come funzionano la riga dei filtri, i pacchetti iniziali, i promemoria e i comandi vocali.", "Jak działają pasek filtrów, pakiety startowe, przypomnienia i polecenia głosowe.", "Zo werken de filterbalk, startpakketten, herinneringen en spraakopdrachten."],
 "What each feature sends to the AI.": ["Qué envía cada función a la IA.", "Was jede Funktion an die KI sendet.", "Ce que chaque fonction envoie à l’IA.", "Her özelliğin yapay zekâya ne gönderdiği.", "O que cada função envia à IA.", "Cosa invia ogni funzione all’IA.", "Co każda funkcja wysyła do AI.", "Wat elke functie naar de AI stuurt."],
}
# the pcmp note moved its last sentence to the front: head = last sentence, tail = the first two
PCMP = "Assumes your real burn was similar in both periods apart from steps. Short periods can only show a large error (margin of error shrinks with longer periods and more weigh-ins); scale weight moves half a kilo or more with water and salt alone. Treat it as a guide, not a measurement."
def run(write):
    added = {l: 0 for l in LANGS}; skipped = []
    for l in LANGS:
        path = os.path.join(ROOT, 'lang', l + '.json'); orig = open(path, encoding='utf-8').read(); d = json.loads(orig); idx = {norm(k): k for k in d}; before = set(d)
        def put(en, tr):
            en = norm(en)
            if en and tr and en not in d and en not in idx: d[en] = norm(tr); added[l] += 1
        for en, how, _, _ in CASES:
            k = idx.get(norm(en))
            if not k: skipped.append((l, en[:40], 'no existing key')); continue
            he, te = cut(norm(en), how), cut(norm(d[k]), how)
            if he and not te and how[0] == 'dash': te = cut(norm(d[k]), ('colon',))   # es / it write a colon where English has a dash
            if not he or not te: skipped.append((l, en[:40], 'translation does not cut')); continue
            if how[0] == 'colon': put(dot(he[0]), dot(te[0])); put(cap(he[1]), cap(te[1]))
            else: put(dot(he[0]), dot(te[0])); put(cap(he[1]), cap(te[1]))
        for en_, trs in LEADS.items(): put(en_, trs[LANGS.index(l)])
        k = idx.get(norm(PCMP))
        if k:
            ms = list(re.finditer(r'(?<=[.!?])\s+(?=\S)', norm(d[k])))
            if len(ms) == 2:
                t = norm(d[k]); put("Treat it as a guide, not a measurement.", t[ms[1].end():]); put(PCMP.rsplit('. Treat', 1)[0] + '.', t[:ms[1].start()])
            else: skipped.append((l, 'pcmp', 'translation does not cut'))
        new = [k for k in d if k not in before]
        if write and new: open(path, 'w', encoding='utf-8').write(orig.rstrip()[:-1].rstrip() + ',\n' + ',\n'.join(json.dumps(k, ensure_ascii=False) + ': ' + json.dumps(d[k], ensure_ascii=False) for k in new) + '\n}\n')   # append only: keeps each pack's own layout, so the diff is just the new lines
    return added, skipped
if __name__ == '__main__':
    a, sk = run('--write' in sys.argv); print('added', a); print('skipped', len(sk)); [print(' ', x) for x in sk[:30]]
