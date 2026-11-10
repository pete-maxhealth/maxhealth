#!/usr/bin/env python3
"""Adds the v3.10.1358-1362 strings (Nothing to add card, Mark all as already added, Move to another device menu) to lang/*.json. Only adds keys that are absent.
Column order: es, de, fr, tr, pt, it, pl, nl. Machine-assisted wording, not native-speaker checked (same as the other packs).
The cupboards wording follows each pack's existing "…not in my cupboards yet" line."""
import json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
LANGS = ['es', 'de', 'fr', 'tr', 'pt', 'it', 'pl', 'nl']
T = {
 '📲 Move to another device': ['📲 Pasar a otro dispositivo', '📲 Auf ein anderes Gerät übertragen', '📲 Transférer vers un autre appareil', '📲 Başka bir cihaza taşı', '📲 Mover para outro dispositivo', '📲 Sposta su un altro dispositivo', '📲 Przenieś na inne urządzenie', '📲 Naar een ander apparaat verplaatsen'],
 '⏻ Turn off': ['⏻ Desactivar', '⏻ Ausschalten', '⏻ Désactiver', '⏻ Kapat', '⏻ Desativar', '⏻ Disattiva', '⏻ Wyłącz', '⏻ Uitschakelen'],
 '📲 Phone to phone (QR)': ['📲 De móvil a móvil (QR)', '📲 Handy zu Handy (QR)', '📲 De téléphone à téléphone (QR)', '📲 Telefondan telefona (QR)', '📲 Celular para celular (QR)', '📲 Da telefono a telefono (QR)', '📲 Telefon do telefonu (QR)', '📲 Van telefoon naar telefoon (QR)'],
 '📤 Send stock and list': ['📤 Enviar existencias y lista', '📤 Vorrat und Liste senden', '📤 Envoyer le stock et la liste', '📤 Stoku ve listeyi gönder', '📤 Enviar estoque e lista', '📤 Invia scorte e lista', '📤 Wyślij zapasy i listę', '📤 Voorraad en lijst versturen'],
 '📥 Receive stock and list': ['📥 Recibir existencias y lista', '📥 Vorrat und Liste empfangen', '📥 Recevoir le stock et la liste', '📥 Stoku ve listeyi al', '📥 Receber estoque e lista', '📥 Ricevi scorte e lista', '📥 Odbierz zapasy i listę', '📥 Voorraad en lijst ontvangen'],
 '✓ Mark all as already added (adds nothing)': ['✓ Marcar todo como ya añadido (no añade nada)', '✓ Alles als bereits hinzugefügt markieren (fügt nichts hinzu)', '✓ Tout marquer comme déjà ajouté (n’ajoute rien)', '✓ Hepsini zaten eklendi olarak işaretle (hiçbir şey eklemez)', '✓ Marcar tudo como já adicionado (não adiciona nada)', '✓ Segna tutto come già aggiunto (non aggiunge nulla)', '✓ Oznacz wszystko jako już dodane (niczego nie dodaje)', '✓ Alles markeren als al toegevoegd (voegt niets toe)'],
 '✓ Nothing to add': ['✓ Nada que añadir', '✓ Nichts hinzuzufügen', '✓ Rien à ajouter', '✓ Eklenecek bir şey yok', '✓ Nada a adicionar', '✓ Niente da aggiungere', '✓ Nic do dodania', '✓ Niets toe te voegen'],
 'Add it again anyway': ['Añadirlo de nuevo de todos modos', 'Trotzdem erneut hinzufügen', 'L’ajouter quand même', 'Yine de tekrar ekle', 'Adicionar mesmo assim', 'Aggiungilo comunque di nuovo', 'Mimo to dodaj ponownie', 'Toch opnieuw toevoegen'],
 '🏠 Go to My cupboards': ['🏠 Ir a mis armarios', '🏠 Zu meinen Vorratsschränken', '🏠 Aller à mes placards', '🏠 Dolaplarıma git', '🏠 Ir para os meus armários', '🏠 Vai alle mie dispense', '🏠 Przejdź do moich szafek', '🏠 Ga naar mijn voorraadkasten'],
}
added = {l: 0 for l in LANGS}
for i, l in enumerate(LANGS):
    p = os.path.join(ROOT, 'lang', l + '.json'); raw = open(p, encoding='utf-8').read(); d = json.loads(raw)
    new = []
    for k, v in T.items():
        if len(v) != 8: sys.exit('bad row: ' + k[:40])
        if k in d: continue
        new.append(json.dumps(k, ensure_ascii=False) + ': ' + json.dumps(v[i], ensure_ascii=False)); added[l] += 1
    if not new: continue
    if not raw.endswith('\n}\n'): sys.exit('unexpected file end: ' + l)
    out = raw[:-3] + ',\n' + ',\n'.join(new) + '\n}\n'      # append only, so the diff is just the new lines (the packs mix two layouts)
    json.loads(out)
    open(p, 'w', encoding='utf-8').write(out)
print('added', added)
