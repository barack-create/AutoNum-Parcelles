# AutoNum Parcelles — Plugin QGIS

Plugin QGIS (Processing) qui numérote automatiquement une couche de
parcelles cadastrales (polygones) de façon **consécutive**, par
**plus proche voisin** : le parcours démarre à la parcelle la plus
au nord-ouest, puis avance toujours vers la parcelle non numérotée
la plus proche.

## Sommaire

- [Fonctionnalités](#fonctionnalités)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Paramètres](#paramètres)
- [Limite connue](#limite-connue)
- [Contribuer](#contribuer)
- [Licence](#licence)

## Fonctionnalités

- Numérotation par plus proche voisin, départ nord-ouest
- Écriture dans un nouveau champ texte, format `0001`, `0002`, ... (4
  chiffres par défaut, personnalisable)
- Numéro de départ configurable
- Intégré à la **Boîte à outils de traitement** de QGIS (Processing
  Toolbox) : utilisable seul, dans un modèle (Graphical Modeler), ou en
  script PyQGIS/CLI
- Fonctionne sur toute couche de polygones (pas seulement du cadastre)

## Installation

### Depuis le ZIP

1. Télécharger la dernière release (`parcel_numbering.zip`).
2. Dans QGIS : **Extensions > Gérer et installer les extensions... >
   Installer depuis un ZIP**.
3. Sélectionner le fichier téléchargé, cliquer sur **Installer**.
4. Redémarrer QGIS si l'algorithme n'apparaît pas immédiatement dans la
   boîte à outils.

### Depuis le dépôt officiel QGIS

Une fois publié : **Extensions > Gérer et installer les extensions...
> Toutes**, rechercher *AutoNum Parcelles*,
cliquer sur **Installer**.

## Utilisation

1. Ouvrir **Traitement > Boîte à outils de traitement**.
2. Chercher **Numéroter les parcelles (plus proche voisin)** (groupe
   *Cadastre*).
3. Renseigner :
   - la couche de parcelles (polygones) en entrée,
   - le nom du champ à créer (par défaut `NUM_PARC`),
   - le numéro de départ (par défaut 1),
   - la couche de sortie.
4. Lancer.

Le résultat est une nouvelle couche identique à l'entrée, avec un champ
supplémentaire contenant le numéro de chaque parcelle.

## Paramètres

| Paramètre | Description | Valeur par défaut |
|---|---|---|
| Couche de parcelles | Couche de polygones en entrée | — |
| Nom du champ | Nom du champ créé pour le numéro | `NUM_PARC` |
| Numéro de départ | Premier numéro attribué | `1` |
| Nombre de chiffres | Longueur du zéro-padding (1 = `1`, 2 = `01`, 3 = `001`, 4 = `0001`...) | `4` |
| Couche de sortie | Fichier ou couche temporaire | Couche temporaire |

## Limite connue

L'algorithme est en **O(n²)** : au-delà de quelques milliers de
parcelles, le calcul peut devenir lent. Pour des couches très
volumineuses, il est recommandé de traiter la couche bloc par bloc
(îlot par îlot).

## Contribuer

Les suggestions et rapports de bug sont les bienvenus via les
[issues](../../issues) de ce dépôt. Idées d'évolution déjà identifiées :
- Numérotation bloc par bloc (redémarrage à 1 par îlot/section, basé
  sur un champ existant)
- Choix du point de départ (autre que nord-ouest) via l'interface
- Optimisation des performances pour les grandes couches (index
  spatial, KD-tree)

## Licence

Ce plugin est distribué sous licence [GPL v2 ou supérieure](LICENSE),
comme l'exige le dépôt officiel des extensions QGIS.

## Auteur

Développé par Moubarak BONI SALIFOU, géomaticien spécialisé en cadastre
et gestion foncière (Bénin).
