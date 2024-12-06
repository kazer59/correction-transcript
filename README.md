# Correcteur Orthographique

Une application de bureau pour la correction orthographique en français avec une interface graphique conviviale.

## Fonctionnalités

- Interface graphique intuitive
- Correction orthographique en français
- Ouverture et sauvegarde de fichiers texte
- Surlignage des erreurs en temps réel
- Suggestions de corrections
- Mise en évidence et navigation automatique vers les mots sélectionnés
- Possibilité d'ignorer des mots
- Dictionnaire personnalisé de corrections avec :
  - Gestion intelligente des majuscules/minuscules
  - Conservation de la casse d'origine lors des corrections
  - Support de la ponctuation (virgules, points, etc.)
  - Affichage optimisé des variantes sur plusieurs lignes
  - Hauteur des lignes ajustable avec la souris
  - Tri alphabétique des variantes (insensible à la casse et aux accents)
  - Correction directe depuis le dictionnaire personnel
  - Ajout automatique des variantes lors des corrections
- Correction automatique basée sur le dictionnaire personnel
- Gestion des accents et caractères spéciaux
- Vérification orthographique automatique à l'ouverture des fichiers
- Barre de progression montrant l'avancement du traitement
- Affichage en temps réel :
  - Du nombre d'erreurs dans le titre du panneau de correction
  - Du statut et du nombre de mots traités
  - Du nombre de corrections automatiques effectuées
- Tri alphabétique du dictionnaire personnel
- Affichage du nombre total de mots dans le dictionnaire

## Prérequis

- Python 3.x
- Tkinter (généralement inclus avec Python)
- pyspellchecker
- unidecode (pour le tri insensible aux accents)

## Installation

1. Clonez ce dépôt ou téléchargez les fichiers
2. Installez les dépendances :
```bash
pip install pyspellchecker unidecode
```

## Interface

L'interface principale comprend :
- Une barre d'outils avec les boutons principaux
- Une zone de texte pour écrire ou coller votre texte
- Un panneau latéral pour les corrections et suggestions contenant :
  - Le nombre d'erreurs trouvées dans le titre
  - La liste des mots mal orthographiés
  - Les suggestions pour chaque mot sélectionné
- Une barre de progression indiquant l'avancement du traitement
- Un indicateur de statut affichant :
  - Le chargement du fichier
  - La progression de la vérification orthographique
  - Le nombre de mots traités
  - Le nombre de corrections automatiques effectuées
  - Le résultat final avec le nombre d'erreurs trouvées
- Un dictionnaire personnel affichant :
  - Le nombre total de mots dans le titre
  - Les corrections dans la première colonne
  - Les variantes associées dans la seconde colonne, affichées sur plusieurs lignes pour une meilleure lisibilité
  - Possibilité de trier en cliquant sur les en-têtes de colonnes
  - Hauteur des lignes ajustable avec la souris

## Organisation du Code

Le projet est organisé en plusieurs modules pour une meilleure maintenabilité :

1. `main.py` : Point d'entrée de l'application
2. `gui.py` : Interface graphique et gestion des interactions utilisateur
3. `spell_checker.py` : Logique de vérification orthographique
4. `dictionary_manager.py` : Gestion du dictionnaire personnalisé

## Utilisation

1. Lancez l'application :
```bash
python main.py
```

2. L'interface principale comprend :
   - Une barre d'outils avec les boutons principaux
   - Une zone de texte pour écrire ou coller votre texte
   - Un panneau latéral pour les corrections et suggestions
   - Une barre de progression indiquant l'avancement du traitement
   - Un indicateur de statut affichant :
     - Le chargement du fichier
     - La progression de la vérification orthographique
     - Le nombre de mots traités
     - Le nombre de corrections automatiques effectuées

3. Fonctions principales :
   - **Ouvrir** : Charger un fichier texte
   - **Sauvegarder** : Enregistrer le texte dans un fichier
   - **Corriger** : Lancer la vérification orthographique
   - **Effacer surlignages** : Supprimer les marquages d'erreurs

4. Pour corriger une erreur :
   - Cliquez sur un mot dans la liste des erreurs pour :
     - Le mettre en évidence dans le texte (surligné en jaune)
     - Voir automatiquement sa position dans le texte
     - Afficher les suggestions de correction
   - Choisissez une suggestion dans la liste ou :
     - Sélectionnez un mot dans le dictionnaire personnel
     - Confirmez la correction et l'ajout de la variante
   - Cliquez sur "Corriger" pour appliquer ou "Ignorer" pour ajouter le mot au dictionnaire

5. Gestion du dictionnaire personnel :
   - Pour ajouter un mot :
     - Sélectionnez un mot dans la liste des erreurs
     - Sélectionnez une suggestion
     - Cliquez sur "Ajouter" dans le panneau du dictionnaire
   - Pour supprimer un mot :
     - Sélectionnez une entrée dans le tableau du dictionnaire
     - Cliquez sur "Supprimer"
   - Pour trier le dictionnaire :
     - Cliquez sur l'en-tête "Correction" pour trier par mot correct
     - Cliquez sur l'en-tête "Variantes" pour trier par variantes
     - Le tri est insensible à la casse et aux accents
     - Un second clic inverse l'ordre de tri
   - Affichage des variantes :
     - Les variantes sont affichées sur plusieurs lignes pour une meilleure lisibilité
     - La hauteur des lignes est ajustable avec la souris
     - Les variantes sont triées alphabétiquement
   - Correction directe depuis le dictionnaire :
     - Sélectionnez un mot erroné dans la liste des erreurs
     - Cliquez sur le mot correct dans le dictionnaire
     - Confirmez la correction et l'ajout de la variante

## Gestion des Mots

1. Traitement des majuscules/minuscules :
   - Les mots sont reconnus indépendamment de leur casse
   - La casse d'origine est préservée lors des corrections
   - Les variantes sont automatiquement ajoutées en majuscules et minuscules

2. Gestion de la ponctuation :
   - Les mots sont correctement reconnus même suivis de ponctuation
   - La ponctuation est préservée lors des corrections
   - Le surlignage ne s'applique qu'au mot, pas à la ponctuation

3. Dictionnaire personnel :
   - Les mots corrects sont automatiquement ajoutés avec leurs variantes
   - Chaque mot est stocké avec ses versions majuscules et minuscules
   - Les corrections préservent le format d'origine du texte
   - Les variantes sont affichées de manière claire et organisée
   - Les variantes peuvent être ajoutées automatiquement lors des corrections

## Fichiers de Configuration

- `dictionnaire_ignore.txt` : Liste des mots à ignorer
- `mots-corrections.txt` : Dictionnaire personnalisé de corrections
  - Format : `mot_correct:variante1,variante2,...`
  - Les variantes seront automatiquement corrigées en utilisant le mot correct
  - Le fichier est automatiquement mis à jour lors des modifications
  - Les variantes sont affichées sur plusieurs lignes dans l'interface

## Support

Pour signaler un bug ou suggérer une amélioration, n'hésitez pas à créer une issue.
