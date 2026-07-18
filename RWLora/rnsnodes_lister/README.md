<p align="center"><img src="images/RNSnodes_lister.png" alt="RNSnodes_lister" width="260"></p>

# RNSnodes_lister

Application Windows de listage, filtrage et sélection des points d'accès
(*nodes*) du réseau **Reticulum**, recensés en temps réel par
[rns.fyi](https://rns.fyi/).

RNSnodes_lister interroge l'annuaire public rns.fyi, présente les nodes avec
leurs métriques de qualité (santé, uptime, fiabilité d'annonce, nombre de
sauts, latence), permet de les filtrer et d'en sélectionner, puis met à jour
le fichier de configuration Reticulum — **sans jamais toucher aux interfaces
déclarées à la main** (bloc géré délimité, sauvegarde automatique).

Le cœur applicatif est fourni par la librairie `rnslister_lib`, également
réutilisée par **TCQ** et par **RWLoRa Console** pour choisir un hôte
Reticulum.

## Téléchargement

**[⬇ Télécharger RNSnodes_lister (dernière version)](https://github.com/f1gbd/F1GBD/releases/latest/download/RNSnodes_lister.7z)**

Version épinglée : [RNSnodes_lister v1.0.2](https://github.com/f1gbd/F1GBD/releases/download/rnsnodeslister-v1.0.2/RNSnodes_lister.7z) · [page de la release](https://github.com/f1gbd/F1GBD/releases/tag/rnsnodeslister-v1.0.2)

- Archive : `RNSnodes_lister.7z` (7-Zip) — Windows 64 bits
- Taille : 8,55 Mo
- SHA-256 : `80f3e05b32103942ed023cf46b9d00763cd15872fbd7c0564157c2bb70557662`

## Installation

1. Télécharger puis décompresser `RNSnodes_lister.7z` avec [7-Zip](https://www.7-zip.org/).
2. Lancer `RNSnodes_lister.exe`.

Aucune installation, aucune dépendance : l'exécutable est autonome
(build PyInstaller `--onedir`).

## Fonctionnalités

- Récupération en direct des nodes publics depuis rns.fyi (ou depuis un
  fichier JSON local).
- Tableau triable : Nom, Hôte, Port, Type, Santé, Uptime, Fiabilité, Sauts,
  Latence, Joignabilité, Localisation.
- Filtres qualité : santé minimale, uptime minimal, fiabilité minimale,
  *floor-pass* (nodes sains), sauts maximum, type, recherche par nom.
- Test de joignabilité TCP en parallèle.
- Sélection multiple des nodes intéressants (cases à cocher).
- Mise à jour du fichier de configuration Reticulum : bloc géré, interfaces
  manuelles préservées, sauvegarde horodatée automatique.
- Export de la sélection au format config Reticulum ou JSON.
- Thèmes clair / sombre.

## Source des données

Les données proviennent de l'annuaire public rns.fyi (*canary* Reticulum).
RNSnodes_lister ne fait qu'interroger son API publique : il **n'émet aucune
annonce** sur le réseau et ne modifie rien côté rns.fyi.

## Écosystème

RNSnodes_lister s'intègre à l'écosystème de communications d'urgence F1GBD /
ADRASEC : la librairie `rnslister_lib` est partagée avec **TCQ** (plateforme
multi-modes) et **RWLoRa Console** (passerelle LoRa/Reticulum).

---

*Distribué en exécutable uniquement (sans sources).*

73 de **F1GBD**