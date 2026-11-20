#!/usr/bin/env python3
"""20 Nov 2026 (v3.10.1442): strings missed in v3.10.1436 (Back to missing days) and v3.10.1440 (Chart button). Machine-assisted. Columns: es, de, fr, tr, pt, it, pl, nl."""
import os, sys; sys.path.insert(0, os.path.dirname(__file__))
from lang_lib import apply
T = {
 '← Back to missing days': ['← Volver a los días que faltan', '← Zurück zu den fehlenden Tagen', '← Retour aux jours manquants', '← Eksik günlere dön', '← Voltar aos dias em falta', '← Torna ai giorni mancanti', '← Wróć do brakujących dni', '← Terug naar ontbrekende dagen'],
 '📊 Chart': ['📊 Gráfico', '📊 Diagramm', '📊 Graphique', '📊 Grafik', '📊 Gráfico', '📊 Grafico', '📊 Wykres', '📊 Grafiek'],
 'This kind of query cannot be charted': ['Este tipo de consulta no se puede mostrar en un gráfico', 'Diese Art von Abfrage lässt sich nicht als Diagramm darstellen', 'Ce type de requête ne peut pas être affiché en graphique', 'Bu tür bir sorgu grafik olarak gösterilemez', 'Este tipo de consulta não pode ser mostrado num gráfico', 'Questo tipo di ricerca non può essere mostrato in un grafico', 'Tego rodzaju zapytania nie można pokazać na wykresie', 'Dit soort zoekopdracht kan niet als grafiek worden getoond'],
}
if __name__ == '__main__': apply(T)
