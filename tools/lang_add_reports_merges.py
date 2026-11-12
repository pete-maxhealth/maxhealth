#!/usr/bin/env python3
"""12 Nov 2026 (v3.10.1376): Reports merges. Machine-assisted wording, not native-speaker checked. Column order: es, de, fr, tr, pt, it, pl, nl."""
import os, sys; sys.path.insert(0, os.path.dirname(__file__))
from lang_lib import apply
T = {
 'Fasting & when you eat': ['Ayuno y cuándo comes', 'Fasten & wann du isst', 'Jeûne et quand vous mangez', 'Oruç ve ne zaman yediğiniz', 'Jejum e quando comes', 'Digiuno e quando mangi', 'Post i pora jedzenia', 'Vasten & wanneer je eet'],
 'Insights & what moves what': ['Observaciones y qué mueve qué', 'Erkenntnisse & was was bewegt', 'Observations et ce qui fait bouger quoi', 'Çıkarımlar ve neyin neyi etkilediği', 'Observações e o que move o quê', 'Osservazioni e cosa muove cosa', 'Wnioski i co na co wpływa', 'Inzichten & wat wat beïnvloedt'],
}
apply(T)
