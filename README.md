Description du projet

Ce projet consiste à développer une application Python capable de jouer et résoudre automatiquement le jeu du Taquin (8-puzzle ou 15-puzzle).
Le jeu est implémenté avec une interface graphique intuitive réalisée en Tkinter, et propose plusieurs modes :
Solo , Multijoueur , Mode IA utilisant l’algorithme A* pour trouver la solution optimale.
L’utilisateur peut également jouer avec des images personnalisées, automatiquement découpées en tuiles grâce à Pillow.

Résolution automatique – Algorithme A*
Le solver IA utilise l’algorithme A*, combiné à deux heuristiques admissibles :
Distance de Hamming (nombre de tuiles mal placées)
Distance de Manhattan (distance minimale pour que chaque tuile rejoigne sa position finale)
A* garantit la solution optimale lorsque l’heuristique ne surestime pas le coût.

Traitement d'image
Grâce à Pillow, l'application peut :
charger une image source , la découper en tuiles , ajouter automatiquement les numéros , gérer la tuile vide , choisir aléatoirement une image parmi un dossier.
Cette fonctionnalité rend le jeu plus attrayant et personnalisable.

Fonctionnalités principales
Interface Tkinter complète
Puzzle 3×3 et 4×4
Déplacements animés
Mode Solo
Mode Multijoueur (tour par tour)
Mode IA avec visualisation
Mélange aléatoire du puzzle
Sélection aléatoire d’images
Génération des tuiles depuis image
Résolution optimale avec A
