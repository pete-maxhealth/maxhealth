#!/usr/bin/env python3
"""13 Nov 2026 (v3.10.1404): shorter 'How do you like to eat?' screen. Columns: es, de, fr, tr, pt, it, pl, nl. Machine-assisted."""
import os, sys; sys.path.insert(0, os.path.dirname(__file__))
from lang_lib import apply
T = {
 'Pick a way of eating, or skip. You can change it any time in Settings.': (
  'Elige una forma de comer, u omite este paso. Puedes cambiarla cuando quieras en Ajustes.',
  'Wähle eine Ernährungsweise oder überspringe den Schritt. Du kannst sie jederzeit in den Einstellungen ändern.',
  'Choisis une façon de manger, ou passe cette étape. Tu peux la changer à tout moment dans les Réglages.',
  'Bir beslenme şekli seç ya da atla. İstediğin zaman Ayarlar\'dan değiştirebilirsin.',
  'Escolhe uma forma de comer, ou salta este passo. Podes mudá-la quando quiseres nas Definições.',
  'Scegli un modo di mangiare, oppure salta. Puoi cambiarlo in qualsiasi momento nelle Impostazioni.',
  'Wybierz sposób odżywiania albo pomiń. Możesz to zmienić w dowolnym momencie w Ustawieniach.',
  'Kies een eetwijze, of sla over. Je kunt dit altijd wijzigen in Instellingen.'),
 'Your condition and goal set your requirements. A way of eating works inside them, shaping the split of carbs, protein and fat. If you have a condition or take medication, check with a health professional first.': (
  'Tu condición y tu objetivo marcan tus requisitos. Una forma de comer funciona dentro de ellos y da forma al reparto de carbohidratos, proteínas y grasas. Si tienes una enfermedad o tomas medicación, consúltalo antes con un profesional de la salud.',
  'Deine Erkrankung und dein Ziel legen deine Anforderungen fest. Eine Ernährungsweise bewegt sich innerhalb davon und bestimmt die Aufteilung von Kohlenhydraten, Eiweiß und Fett. Wenn du eine Erkrankung hast oder Medikamente nimmst, sprich vorher mit einer Fachperson.',
  'Ton état de santé et ton objectif fixent tes besoins. Une façon de manger s\'inscrit dedans et détermine la répartition des glucides, des protéines et des lipides. Si tu as une maladie ou prends des médicaments, demande d\'abord l\'avis d\'un professionnel de santé.',
  'Durumun ve hedefin gereksinimlerini belirler. Bir beslenme şekli bunların içinde çalışır ve karbonhidrat, protein ve yağ dağılımını şekillendirir. Bir rahatsızlığın varsa ya da ilaç kullanıyorsan önce bir sağlık uzmanına danış.',
  'A tua condição e o teu objetivo definem os teus requisitos. Uma forma de comer funciona dentro deles e molda a divisão de hidratos de carbono, proteína e gordura. Se tens uma condição ou tomas medicação, fala primeiro com um profissional de saúde.',
  'La tua condizione e il tuo obiettivo stabiliscono i requisiti. Un modo di mangiare funziona al loro interno e determina la ripartizione di carboidrati, proteine e grassi. Se hai una condizione o prendi farmaci, parlane prima con un professionista della salute.',
  'Twój stan zdrowia i cel wyznaczają wymagania. Sposób odżywiania działa w ich ramach i kształtuje podział węglowodanów, białka i tłuszczu. Jeśli masz schorzenie lub bierzesz leki, najpierw skonsultuj się ze specjalistą.',
  'Je aandoening en je doel bepalen je eisen. Een eetwijze werkt daarbinnen en bepaalt de verdeling van koolhydraten, eiwit en vet. Heb je een aandoening of gebruik je medicatie, overleg dan eerst met een zorgprofessional.'),
 'About 150 everyday foods and simple recipes to begin your library.': (
  'Unos 150 alimentos cotidianos y recetas sencillas para empezar tu biblioteca.',
  'Rund 150 Alltagslebensmittel und einfache Rezepte für den Start deiner Bibliothek.',
  'Environ 150 aliments courants et des recettes simples pour démarrer ta bibliothèque.',
  'Kütüphanene başlamak için yaklaşık 150 günlük yiyecek ve basit tarifler.',
  'Cerca de 150 alimentos do dia a dia e receitas simples para começar a tua biblioteca.',
  'Circa 150 alimenti di tutti i giorni e ricette semplici per iniziare la tua libreria.',
  'Około 150 codziennych produktów i proste przepisy na początek twojej biblioteki.',
  'Zo\'n 150 alledaagse voedingsmiddelen en simpele recepten om je bibliotheek te starten.'),
 'About 150 everyday foods and a set of simple recipes to begin your library, with typical values you can check against your own labels. If you already have a library they merge into it and skip anything with the same name, so nothing is duplicated. Remove them in one tap in Settings.': (
  'Unos 150 alimentos cotidianos y un conjunto de recetas sencillas para empezar tu biblioteca, con valores típicos que puedes comparar con tus propias etiquetas. Si ya tienes una biblioteca, se fusionan con ella y se omite todo lo que tenga el mismo nombre, así que nada se duplica. Quítalos con un toque en Ajustes.',
  'Rund 150 Alltagslebensmittel und einige einfache Rezepte für den Start deiner Bibliothek, mit typischen Werten, die du mit deinen eigenen Etiketten vergleichen kannst. Hast du schon eine Bibliothek, werden sie hineingemischt und alles mit gleichem Namen wird übersprungen, nichts wird doppelt angelegt. Mit einem Tipp in den Einstellungen entfernst du sie wieder.',
  'Environ 150 aliments courants et quelques recettes simples pour démarrer ta bibliothèque, avec des valeurs typiques que tu peux comparer à tes propres étiquettes. Si tu as déjà une bibliothèque, ils s\'y ajoutent en ignorant tout ce qui porte le même nom, donc rien n\'est dupliqué. Retire-les d\'un geste dans les Réglages.',
  'Kütüphanene başlamak için yaklaşık 150 günlük yiyecek ve bir dizi basit tarif; kendi etiketlerinle karşılaştırabileceğin tipik değerlerle gelir. Zaten bir kütüphanen varsa içine eklenir, aynı ada sahip olanlar atlanır, yani hiçbir şey tekrarlanmaz. Ayarlar\'dan tek dokunuşla kaldırabilirsin.',
  'Cerca de 150 alimentos do dia a dia e um conjunto de receitas simples para começar a tua biblioteca, com valores típicos que podes comparar com os teus rótulos. Se já tens uma biblioteca, juntam-se a ela e ignoram tudo o que tenha o mesmo nome, por isso nada fica duplicado. Remove-os com um toque nas Definições.',
  'Circa 150 alimenti di tutti i giorni e una serie di ricette semplici per iniziare la tua libreria, con valori tipici che puoi confrontare con le tue etichette. Se hai già una libreria, vengono uniti e tutto ciò che ha lo stesso nome viene saltato, quindi niente si duplica. Rimuovili con un tocco nelle Impostazioni.',
  'Około 150 codziennych produktów i zestaw prostych przepisów na początek twojej biblioteki, z typowymi wartościami, które możesz porównać z własnymi etykietami. Jeśli masz już bibliotekę, zostaną do niej dołączone, a wszystko o tej samej nazwie zostanie pominięte, więc nic się nie powtórzy. Usuń je jednym dotknięciem w Ustawieniach.',
  'Zo\'n 150 alledaagse voedingsmiddelen en een set simpele recepten om je bibliotheek te starten, met typische waarden die je met je eigen etiketten kunt vergelijken. Heb je al een bibliotheek, dan worden ze erin samengevoegd en wordt alles met dezelfde naam overgeslagen, dus niets wordt dubbel. Verwijder ze met één tik in Instellingen.'),
}
apply(T)
