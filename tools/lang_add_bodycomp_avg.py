#!/usr/bin/env python3
"""12 Nov 2026 (v3.10.1383): Move body composition range change uses averages at each end. Machine-assisted. Columns: es, de, fr, tr, pt, it, pl, nl."""
import os, sys; sys.path.insert(0, os.path.dirname(__file__))
from lang_lib import apply
apply({'averages at each end': ['promedios en cada extremo', 'Durchschnitte an beiden Enden', 'moyennes à chaque extrémité', 'her iki uçta ortalamalar', 'médias em cada extremo', 'medie a ciascun estremo', 'średnie na obu końcach', 'gemiddelden aan beide kanten'],
       'Weight': ['Peso', 'Gewicht', 'Poids', 'Kilo', 'Peso', 'Peso', 'Waga', 'Gewicht']})
apply({
 'Same scale for every line, drawn as change from where the range started.': ['La misma escala para todas las líneas, dibujada como cambio desde el inicio del rango.', 'Gleicher Maßstab für alle Linien, gezeichnet als Veränderung seit Beginn des Zeitraums.', 'Même échelle pour toutes les lignes, tracée comme variation depuis le début de la période.', 'Tüm çizgiler için aynı ölçek; aralığın başlangıcından itibaren değişim olarak çizilir.', 'A mesma escala para todas as linhas, desenhada como variação desde o início do intervalo.', 'Stessa scala per tutte le linee, disegnata come variazione dall’inizio dell’intervallo.', 'Ta sama skala dla wszystkich linii, rysowana jako zmiana od początku zakresu.', 'Dezelfde schaal voor elke lijn, getekend als verandering sinds het begin van de periode.'],
 'Muscle was about {0}% of the weight lost.': ['El músculo fue aproximadamente el {0} % del peso perdido.', 'Muskeln machten etwa {0} % des verlorenen Gewichts aus.', 'Le muscle représentait environ {0} % du poids perdu.', 'Kaybedilen kilonun yaklaşık %{0}’i kastı.', 'O músculo foi cerca de {0} % do peso perdido.', 'Il muscolo è stato circa il {0}% del peso perso.', 'Mięśnie stanowiły około {0}% utraconej wagi.', 'Spieren waren ongeveer {0}% van het verloren gewicht.'],
})
