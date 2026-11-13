#!/usr/bin/env python3
"""13 Nov 2026 (v3.10.1400): add to home screen button, hint and how-to. Columns: es, de, fr, tr, pt, it, pl, nl. Machine-assisted."""
import os, sys; sys.path.insert(0, os.path.dirname(__file__))
from lang_lib import apply
T = {
 '📲 ADD TO HOME SCREEN': ('📲 AÑADIR A LA PANTALLA DE INICIO', '📲 ZUM STARTBILDSCHIRM HINZUFÜGEN', '📲 AJOUTER À L\'ÉCRAN D\'ACCUEIL', '📲 ANA EKRANA EKLE', '📲 ADICIONAR AO ECRÃ INICIAL', '📲 AGGIUNGI ALLA SCHERMATA HOME', '📲 DODAJ DO EKRANU GŁÓWNEGO', '📲 TOEVOEGEN AAN BEGINSCHERM'),
 'Opens like any app, with no browser bar. Your data stays on this phone.': (
  'Se abre como cualquier app, sin barra del navegador. Tus datos se quedan en este móvil.',
  'Öffnet sich wie jede App, ohne Browserleiste. Deine Daten bleiben auf diesem Handy.',
  'S\'ouvre comme n\'importe quelle appli, sans barre de navigateur. Tes données restent sur ce téléphone.',
  'Herhangi bir uygulama gibi açılır, tarayıcı çubuğu olmadan. Verilerin bu telefonda kalır.',
  'Abre como qualquer app, sem barra do navegador. Os teus dados ficam neste telemóvel.',
  'Si apre come qualsiasi app, senza barra del browser. I tuoi dati restano su questo telefono.',
  'Otwiera się jak każda aplikacja, bez paska przeglądarki. Twoje dane zostają na tym telefonie.',
  'Opent als elke app, zonder browserbalk. Je gegevens blijven op deze telefoon.'),
 '📲 Add to home screen →': ('📲 Añadir a la pantalla de inicio →', '📲 Zum Startbildschirm hinzufügen →', '📲 Ajouter à l\'écran d\'accueil →', '📲 Ana ekrana ekle →', '📲 Adicionar ao ecrã inicial →', '📲 Aggiungi alla schermata Home →', '📲 Dodaj do ekranu głównego →', '📲 Toevoegen aan beginscherm →'),
 'Added to your home screen': ('Añadida a tu pantalla de inicio', 'Zum Startbildschirm hinzugefügt', 'Ajoutée à ton écran d\'accueil', 'Ana ekranına eklendi', 'Adicionada ao teu ecrã inicial', 'Aggiunta alla tua schermata Home', 'Dodano do ekranu głównego', 'Toegevoegd aan je beginscherm'),
 'Add to your home screen': ('Añadir a tu pantalla de inicio', 'Zum Startbildschirm hinzufügen', 'Ajouter à ton écran d\'accueil', 'Ana ekranına ekle', 'Adicionar ao teu ecrã inicial', 'Aggiungi alla tua schermata Home', 'Dodaj do ekranu głównego', 'Toevoegen aan je beginscherm'),
 'In Safari, tap the Share button, then Add to Home Screen, then Add.': (
  'En Safari, toca el botón Compartir, luego Añadir a pantalla de inicio y después Añadir.',
  'Tippe in Safari auf die Teilen-Taste, dann auf „Zum Home-Bildschirm“ und dann auf „Hinzufügen“.',
  'Dans Safari, touche le bouton Partager, puis Sur l\'écran d\'accueil, puis Ajouter.',
  'Safari\'de Paylaş düğmesine, sonra Ana Ekrana Ekle\'ye, sonra Ekle\'ye dokun.',
  'No Safari, toca no botão Partilhar, depois em Adicionar ao ecrã principal e depois em Adicionar.',
  'In Safari tocca il pulsante Condividi, poi Aggiungi alla schermata Home, poi Aggiungi.',
  'W Safari dotknij przycisku Udostępnij, potem Do ekranu początkowego, a potem Dodaj.',
  'Tik in Safari op de knop Deel, dan op Zet op beginscherm en daarna op Voeg toe.'),
 'In Chrome, tap the ⋮ menu at the top right, then Install app (or Add to Home screen).': (
  'En Chrome, toca el menú ⋮ arriba a la derecha y luego Instalar app (o Añadir a la pantalla de inicio).',
  'Tippe in Chrome oben rechts auf das ⋮-Menü und dann auf App installieren (oder Zum Startbildschirm hinzufügen).',
  'Dans Chrome, touche le menu ⋮ en haut à droite, puis Installer l\'application (ou Ajouter à l\'écran d\'accueil).',
  'Chrome\'da sağ üstteki ⋮ menüsüne, sonra Uygulamayı yükle\'ye (veya Ana ekrana ekle\'ye) dokun.',
  'No Chrome, toca no menu ⋮ no canto superior direito e depois em Instalar app (ou Adicionar ao ecrã inicial).',
  'In Chrome tocca il menu ⋮ in alto a destra, poi Installa app (o Aggiungi a schermata Home).',
  'W Chrome dotknij menu ⋮ w prawym górnym rogu, a potem Zainstaluj aplikację (lub Dodaj do ekranu głównego).',
  'Tik in Chrome rechtsboven op het ⋮-menu en dan op App installeren (of Toevoegen aan startscherm).'),
 'Open your browser menu and choose Install or Add to Home screen. If you do not see it, open this page in Chrome (Android, PC) or Safari (iPhone).': (
  'Abre el menú de tu navegador y elige Instalar o Añadir a la pantalla de inicio. Si no lo ves, abre esta página en Chrome (Android, PC) o Safari (iPhone).',
  'Öffne das Menü deines Browsers und wähle Installieren oder Zum Startbildschirm hinzufügen. Siehst du das nicht, öffne diese Seite in Chrome (Android, PC) oder Safari (iPhone).',
  'Ouvre le menu de ton navigateur et choisis Installer ou Ajouter à l\'écran d\'accueil. Si tu ne le vois pas, ouvre cette page dans Chrome (Android, PC) ou Safari (iPhone).',
  'Tarayıcı menünü aç ve Yükle veya Ana ekrana ekle\'yi seç. Görmüyorsan bu sayfayı Chrome\'da (Android, PC) veya Safari\'de (iPhone) aç.',
  'Abre o menu do teu navegador e escolhe Instalar ou Adicionar ao ecrã inicial. Se não o vires, abre esta página no Chrome (Android, PC) ou no Safari (iPhone).',
  'Apri il menu del tuo browser e scegli Installa o Aggiungi alla schermata Home. Se non lo vedi, apri questa pagina in Chrome (Android, PC) o Safari (iPhone).',
  'Otwórz menu przeglądarki i wybierz Zainstaluj lub Dodaj do ekranu głównego. Jeśli tego nie widzisz, otwórz tę stronę w Chrome (Android, PC) lub Safari (iPhone).',
  'Open het menu van je browser en kies Installeren of Toevoegen aan startscherm. Zie je dat niet, open deze pagina dan in Chrome (Android, pc) of Safari (iPhone).'),
}
apply(T)
