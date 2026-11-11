#!/usr/bin/env python3
"""Shopping screens sweep, part D (11 Nov 2026): the use-soon timing words and the ON LIST badge. Machine-assisted wording, not native-speaker checked. Column order: es, de, fr, tr, pt, it, pl, nl."""
import os, sys; sys.path.insert(0, os.path.dirname(__file__))
from lang_lib import apply
T = {
 'in {1} days · {2}': ['en {1} días · {2}', 'in {1} Tagen · {2}', 'dans {1} jours · {2}', '{1} gün içinde · {2}', 'em {1} dias · {2}', 'tra {1} giorni · {2}', 'za {1} dni · {2}', 'over {1} dagen · {2}'],
 'in {1} days': ['en {1} días', 'in {1} Tagen', 'dans {1} jours', '{1} gün içinde', 'em {1} dias', 'tra {1} giorni', 'za {1} dni', 'over {1} dagen'],
 'today · {1}': ['hoy · {1}', 'heute · {1}', 'aujourd’hui · {1}', 'bugün · {1}', 'hoje · {1}', 'oggi · {1}', 'dziś · {1}', 'vandaag · {1}'],
 'tomorrow · {1}': ['mañana · {1}', 'morgen · {1}', 'demain · {1}', 'yarın · {1}', 'amanhã · {1}', 'domani · {1}', 'jutro · {1}', 'morgen · {1}'],
 'today': ['hoy', 'heute', 'aujourd’hui', 'bugün', 'hoje', 'oggi', 'dziś', 'vandaag'],
 'tomorrow': ['mañana', 'morgen', 'demain', 'yarın', 'amanhã', 'domani', 'jutro', 'morgen'],
 'use today': ['usar hoy', 'heute verbrauchen', 'à utiliser aujourd’hui', 'bugün kullan', 'usar hoje', 'da usare oggi', 'zużyj dziś', 'vandaag gebruiken'],
 'use by tomorrow': ['usar antes de mañana', 'bis morgen verbrauchen', 'à utiliser avant demain', 'yarına kadar kullan', 'usar até amanhã', 'da usare entro domani', 'zużyj do jutra', 'gebruiken voor morgen'],
 'on list': ['en la lista', 'auf der Liste', 'sur la liste', 'listede', 'na lista', 'in lista', 'na liście', 'op lijst'],
 'past its use-by': ['pasada su fecha de caducidad', 'Verbrauchsdatum überschritten', 'date limite dépassée', 'son kullanma tarihi geçti', 'passou da validade', 'scaduto', 'po terminie przydatności', 'over de houdbaarheidsdatum'],
}
apply(T)
