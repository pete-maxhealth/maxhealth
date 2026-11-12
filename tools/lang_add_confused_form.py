#!/usr/bin/env python3
"""12 Nov 2026 (v3.10.1377): feedback-form button in the Something confused me sheet. Machine-assisted. Columns: es, de, fr, tr, pt, it, pl, nl."""
import os, sys; sys.path.insert(0, os.path.dirname(__file__))
from lang_lib import apply
T = {
 'Send through the feedback form': ['Enviar por el formulario de comentarios', 'Über das Feedback-Formular senden', 'Envoyer via le formulaire de retour', 'Geri bildirim formuyla gönder', 'Enviar pelo formulário de feedback', 'Invia tramite il modulo di feedback', 'Wyślij przez formularz opinii', 'Verstuur via het feedbackformulier'],
 'Opens the same feedback form as Settings, already filled in. It asks you to sign in to GitHub; Share or Copy do not.': ['Abre el mismo formulario de comentarios que Ajustes, ya rellenado. Pide iniciar sesión en GitHub; Compartir o Copiar no.', 'Öffnet dasselbe Feedback-Formular wie in den Einstellungen, schon ausgefüllt. Es verlangt eine GitHub-Anmeldung; Teilen oder Kopieren nicht.', 'Ouvre le même formulaire de retour que les Réglages, déjà rempli. Il demande une connexion à GitHub ; Partager ou Copier non.', 'Ayarlar’daki geri bildirim formunu önceden doldurulmuş olarak açar. GitHub oturumu ister; Paylaş veya Kopyala istemez.', 'Abre o mesmo formulário de feedback das Definições, já preenchido. Pede início de sessão no GitHub; Partilhar ou Copiar não.', 'Apre lo stesso modulo di feedback delle Impostazioni, già compilato. Richiede l’accesso a GitHub; Condividi o Copia no.', 'Otwiera ten sam formularz opinii co w Ustawieniach, już wypełniony. Wymaga logowania do GitHub; Udostępnij lub Kopiuj nie.', 'Opent hetzelfde feedbackformulier als Instellingen, al ingevuld. Het vraagt om inloggen bij GitHub; Delen of Kopiëren niet.'],
}
apply(T)
