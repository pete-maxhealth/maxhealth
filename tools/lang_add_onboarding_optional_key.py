#!/usr/bin/env python3
"""12 Nov 2026 (v3.10.1370): onboarding own-key buttons no longer say "paid". Machine-assisted wording, not native-speaker checked. Column order: es, de, fr, tr, pt, it, pl, nl."""
import os, sys; sys.path.insert(0, os.path.dirname(__file__))
from lang_lib import apply
T = {
 'Own Claude key (optional)': ['Clave propia de Claude (opcional)', 'Eigener Claude-Schlüssel (optional)', 'Clé Claude personnelle (facultatif)', 'Kendi Claude anahtarınız (isteğe bağlı)', 'Chave própria do Claude (opcional)', 'Chiave Claude personale (facoltativo)', 'Własny klucz Claude (opcjonalnie)', 'Eigen Claude-sleutel (optioneel)'],
 'Own OpenAI key (optional)': ['Clave propia de OpenAI (opcional)', 'Eigener OpenAI-Schlüssel (optional)', 'Clé OpenAI personnelle (facultatif)', 'Kendi OpenAI anahtarınız (isteğe bağlı)', 'Chave própria da OpenAI (opcional)', 'Chiave OpenAI personale (facoltativo)', 'Własny klucz OpenAI (opcjonalnie)', 'Eigen OpenAI-sleutel (optioneel)'],
}
apply(T)
