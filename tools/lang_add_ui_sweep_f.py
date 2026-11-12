#!/usr/bin/env python3
"""12 Nov 2026 (v3.10.1367): Sun theme, Statistics shelf, scroll arrow hover tips. Machine-assisted wording, not native-speaker checked. Column order: es, de, fr, tr, pt, it, pl, nl."""
import os, sys; sys.path.insert(0, os.path.dirname(__file__))
from lang_lib import apply
T = {
 'Sun': ['Sol', 'Sonne', 'Soleil', 'Güneş', 'Sol', 'Sole', 'Słońce', 'Zon'],
 'Light from sunrise, dark from sunset': ['Claro desde el amanecer, oscuro desde el atardecer', 'Hell ab Sonnenaufgang, dunkel ab Sonnenuntergang', 'Clair dès le lever du soleil, sombre dès le coucher', 'Gün doğumundan itibaren açık, gün batımından itibaren koyu', 'Claro desde o nascer do sol, escuro desde o pôr do sol', 'Chiaro dall’alba, scuro dal tramonto', 'Jasny od wschodu słońca, ciemny od zachodu', 'Licht vanaf zonsopgang, donker vanaf zonsondergang'],
 '📚 Put back in Library': ['📚 Devolver a la biblioteca', '📚 Zurück in die Bibliothek', '📚 Remettre dans la bibliothèque', '📚 Kitaplığa geri koy', '📚 Devolver à biblioteca', '📚 Rimetti nella libreria', '📚 Odłóż do biblioteki', '📚 Terug in de bibliotheek'],
 '↩ Put back': ['↩ Devolver', '↩ Zurücklegen', '↩ Remettre', '↩ Geri koy', '↩ Devolver', '↩ Rimetti', '↩ Przywróć', '↩ Terugzetten'],
 '📥 Taken off my statistics': ['📥 Quitadas de mis estadísticas', '📥 Aus meinen Statistiken genommen', '📥 Retirées de mes statistiques', '📥 İstatistiklerimden çıkarılanlar', '📥 Retiradas das minhas estatísticas', '📥 Tolte dalle mie statistiche', '📥 Zdjęte z moich statystyk', '📥 Van mijn statistieken gehaald'],
 'Kept here, not shown anywhere. Put one back whenever you like.': ['Se guardan aquí, sin mostrarse en ningún sitio. Devuelve una cuando quieras.', 'Hier aufbewahrt, nirgends angezeigt. Leg eine zurück, wann immer du möchtest.', 'Conservées ici, affichées nulle part. Remettez-en une quand vous voulez.', 'Burada saklanır, hiçbir yerde gösterilmez. İstediğin zaman birini geri koy.', 'Guardadas aqui, não aparecem em lado nenhum. Devolve uma quando quiseres.', 'Conservate qui, non mostrate da nessuna parte. Rimettine una quando vuoi.', 'Przechowywane tutaj, nigdzie niewyświetlane. Przywróć wybraną, kiedy chcesz.', 'Hier bewaard, nergens getoond. Zet er een terug wanneer je wilt.'],
 'Ready-made': ['Ya preparadas', 'Vorgefertigt', 'Prêtes à l’emploi', 'Hazır olanlar', 'Já preparadas', 'Già pronte', 'Gotowe', 'Kant-en-klaar'],
 '📥 on your shelf': ['📥 en tu estante', '📥 in deinem Fach', '📥 sur votre étagère', '📥 rafında', '📥 na tua prateleira', '📥 sul tuo ripiano', '📥 na twojej półce', '📥 op je plank'],
 'Back to top': ['Volver arriba', 'Nach oben', 'Retour en haut', 'Başa dön', 'Voltar ao topo', 'Torna su', 'Na górę', 'Terug naar boven'],
 'Down to the bottom': ['Ir al final', 'Nach unten', 'Tout en bas', 'En alta in', 'Ir para o fim', 'Vai in fondo', 'Na dół', 'Naar beneden'],
 'Back': ['Atrás', 'Zurück', 'Retour', 'Geri', 'Voltar', 'Indietro', 'Wstecz', 'Terug'],
 'Hide': ['Ocultar', 'Ausblenden', 'Masquer', 'Gizle', 'Ocultar', 'Nascondi', 'Ukryj', 'Verbergen'],
 'Show': ['Mostrar', 'Anzeigen', 'Afficher', 'Göster', 'Mostrar', 'Mostra', 'Pokaż', 'Tonen'],
 '👁 Show': ['👁 Mostrar', '👁 Anzeigen', '👁 Afficher', '👁 Göster', '👁 Mostrar', '👁 Mostra', '👁 Pokaż', '👁 Tonen'],
 '📥 Taken off my statistics ({1})': ['📥 Quitadas de mis estadísticas ({1})', '📥 Aus meinen Statistiken genommen ({1})', '📥 Retirées de mes statistiques ({1})', '📥 İstatistiklerimden çıkarılanlar ({1})', '📥 Retiradas das minhas estatísticas ({1})', '📥 Tolte dalle mie statistiche ({1})', '📥 Zdjęte z moich statystyk ({1})', '📥 Van mijn statistieken gehaald ({1})'],
}
apply(T)
