#!/usr/bin/env python3
"""12 Nov 2026 (v3.10.1383): Move body composition range change uses averages at each end. Machine-assisted. Columns: es, de, fr, tr, pt, it, pl, nl."""
import os, sys; sys.path.insert(0, os.path.dirname(__file__))
from lang_lib import apply
apply({'averages at each end': ['promedios en cada extremo', 'Durchschnitte an beiden Enden', 'moyennes à chaque extrémité', 'her iki uçta ortalamalar', 'médias em cada extremo', 'medie a ciascun estremo', 'średnie na obu końcach', 'gemiddelden aan beide kanten'],
       'Weight': ['Peso', 'Gewicht', 'Poids', 'Kilo', 'Peso', 'Peso', 'Waga', 'Gewicht']})
