#!/usr/bin/env python3
"""17 Nov 2026 (v3.10.1407): water card 'Last added'. Columns: es, de, fr, tr, pt, it, pl, nl. Machine-assisted."""
import os, sys; sys.path.insert(0, os.path.dirname(__file__))
from lang_lib import apply
T = {'Last added': ('Última vez', 'Zuletzt hinzugefügt', 'Dernier ajout', 'Son eklenen', 'Último registo', 'Ultima aggiunta', 'Ostatnio dodano', 'Laatst toegevoegd')}
apply(T)
