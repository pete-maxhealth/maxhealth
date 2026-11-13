#!/usr/bin/env python3
"""13 Nov 2026 (v3.10.1397): profile focus line, shopping list line, manual body fat help. Columns: es, de, fr, tr, pt, it, pl, nl. Machine-assisted."""
import os, sys; sys.path.insert(0, os.path.dirname(__file__))
from lang_lib import apply
T = {
 'This sets your carb target and how reports are framed. What you track (symptoms, treatments, screens) comes from 27 starter packs:': (
  'Esto fija tu objetivo de carbohidratos y cómo se presentan los informes. Lo que registras (síntomas, tratamientos, pantallas) viene de 27 paquetes iniciales:',
  'Das legt dein Kohlenhydratziel fest und wie Berichte formuliert werden. Was du erfasst (Symptome, Behandlungen, Bildschirme), stammt aus 27 Starterpaketen:',
  'Cela fixe ton objectif de glucides et la façon dont les rapports sont présentés. Ce que tu suis (symptômes, traitements, écrans) vient de 27 packs de départ :',
  'Bu, karbonhidrat hedefini ve raporların nasıl çerçevelendiğini belirler. Takip ettiklerin (belirtiler, tedaviler, ekranlar) 27 başlangıç paketinden gelir:',
  'Isto define a tua meta de hidratos de carbono e como os relatórios são apresentados. O que acompanhas (sintomas, tratamentos, ecrãs) vem de 27 pacotes iniciais:',
  'Questo imposta il tuo obiettivo di carboidrati e come vengono presentati i report. Ciò che monitori (sintomi, trattamenti, schermate) arriva da 27 pacchetti iniziali:',
  'To ustawia twój cel węglowodanów i sposób ujęcia raportów. To, co śledzisz (objawy, terapie, ekrany), pochodzi z 27 pakietów startowych:',
  'Dit bepaalt je koolhydraatdoel en hoe rapporten worden opgesteld. Wat je bijhoudt (symptomen, behandelingen, schermen) komt uit 27 startpakketten:'),
 'Your list in the order you walk the shop. Tap a row to tick it off; ✎ Edit shows the extras. Tick things as you go and press Shopping complete at the end: it empties the basket and, with stock switched on, adds what you bought to your cupboards.': (
  'Tu lista en el orden en que recorres la tienda. Toca una fila para tacharla; ✎ Editar muestra los extras. Marca las cosas sobre la marcha y pulsa Compra completada al final: vacía la cesta y, con el stock activado, añade lo comprado a tus armarios.',
  'Deine Liste in der Reihenfolge, in der du durch den Laden gehst. Tippe auf eine Zeile, um sie abzuhaken; ✎ Bearbeiten zeigt die Extras. Hake unterwegs ab und tippe am Ende auf Einkauf abgeschlossen: Der Korb wird geleert und, wenn der Vorrat aktiv ist, wird das Gekaufte zu deinen Vorratsschränken hinzugefügt.',
  'Ta liste dans l\'ordre où tu parcours le magasin. Touche une ligne pour la cocher ; ✎ Modifier affiche les extras. Coche au fur et à mesure et appuie sur Courses terminées à la fin : cela vide le panier et, si le stock est activé, ajoute ce que tu as acheté à tes placards.',
  'Listen, mağazada gezdiğin sıraya göre. Bir satıra dokunup işaretle; ✎ Düzenle ekstraları gösterir. Giderken işaretle ve sonunda Alışveriş tamam\'a bas: sepeti boşaltır ve stok açıksa aldıklarını dolaplarına ekler.',
  'A tua lista pela ordem em que percorres a loja. Toca numa linha para a riscar; ✎ Editar mostra os extras. Vai marcando e carrega em Compras concluídas no fim: esvazia o cesto e, com o stock ligado, junta o que compraste aos teus armários.',
  'La tua lista nell\'ordine in cui giri il negozio. Tocca una riga per spuntarla; ✎ Modifica mostra gli extra. Spunta man mano e premi Spesa completata alla fine: svuota il carrello e, con le scorte attive, aggiunge ciò che hai comprato alle tue dispense.',
  'Twoja lista w kolejności, w jakiej chodzisz po sklepie. Dotknij wiersza, aby go odhaczyć; ✎ Edytuj pokazuje dodatki. Odhaczaj na bieżąco i na końcu naciśnij Zakupy zakończone: opróżnia to koszyk, a przy włączonym zapasie dodaje kupione rzeczy do twoich szafek.',
  'Je lijst in de volgorde waarin je door de winkel loopt. Tik op een rij om af te vinken; ✎ Bewerken toont de extra\'s. Vink onderweg af en druk aan het eind op Boodschappen klaar: de mand wordt leeggemaakt en, met voorraad aan, komt wat je kocht in je kasten.'),
 'Manual body fat % (fallback)': (
  'Grasa corporal manual % (alternativa)', 'Körperfett manuell % (Ersatzwert)', 'Masse grasse manuelle % (secours)', 'Elle girilen vücut yağı % (yedek)', 'Gordura corporal manual % (alternativa)', 'Grasso corporeo manuale % (alternativa)', 'Tkanka tłuszczowa ręcznie % (zapasowa)', 'Lichaamsvet handmatig % (terugval)'),
}
apply(T)
