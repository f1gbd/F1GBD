<div align="center">

<img src="https://github.com/f1gbd/F1GBD/blob/master/epirb/doc/images/EPIRBdecoder_logo.jpg?raw=true" alt="EPIRB Decoder" width="220">

# EPIRB 406 MHz Decoder

### Décodeur de balises de détresse COSPAS-SARSAT 406 MHz pour la formation et les opérations ADRASEC

*Décodage EPIRB/ELT/PLB — SDR Direct RTL-SDR — Démodulation FM IQ — Audio Live / Fichier WAV / Hex — Carte OSM avec relèvements goniométriques — Triangulation vectorisée — Thème clair/sombre — Export CSV*

[![Version](https://img.shields.io/badge/version-epirb--v5.1.1-blue)](https://github.com/f1gbd/F1GBD/releases/tag/epirb-v5.1.1)
[![Téléchargements](https://img.shields.io/badge/téléchargements-actifs-brightgreen?logo=github)](https://github.com/f1gbd/F1GBD/releases?q=epirb)
[![Plateforme](https://img.shields.io/badge/plateforme-Windows%2010%2F11-lightgrey.svg)]()
[![Licence](https://img.shields.io/badge/usage-ADRASEC%2FFNRASEC-green.svg)]()
[![Mission](https://img.shields.io/badge/mission-COSPAS--SARSAT-orange.svg)]()

### 📥 [**Télécharger la dernière version stable (v5.1.1)**](https://github.com/f1gbd/F1GBD/releases/download/epirb-v5.1.1/EPIRBdecoder.7z)

</div>

---

## 🎯 Qu'est-ce que EPIRB 406 MHz Decoder ?

**EPIRB Decoder** est un **décodeur complet de balises de détresse 406 MHz** (EPIRB, ELT, PLB) conforme au système **COSPAS-SARSAT**. Il permet de recevoir, décoder et analyser les trames numériques émises par les balises de détresse maritimes et aéronautiques, directement depuis un dongle **RTL-SDR**, un fichier audio WAV, une entrée micro live ou une trame hexadécimale.

L'outil est destiné à la **formation des opérateurs ADRASEC**, aux **exercices de décodage 406 MHz**, et aux **opérations réelles** de recherche et sauvetage dans le cadre COSPAS-SARSAT.

---

## ⭐ Fonctionnalités principales

| Icône | Fonctionnalité | Description |
|:---:|---|---|
| 📡 | **SDR Direct (RTL-SDR)** | Réception IQ directe depuis un dongle RTL-SDR V3/V4 (RTL2832U + R820T/R828D). Démodulation FM logicielle intégrée, détection de burst dans le domaine IQ, décodage automatique des trames 406 MHz. Pas besoin de SDR++ ni d'autre logiciel externe. |
| 📁 | **Décodage fichier audio** | Décodage à partir de fichiers WAV, M4A, MP3, OGG, FLAC. Conversion automatique via FFmpeg si nécessaire. Support des fichiers enregistrés par SDR++ ou tout autre récepteur. |
| 🎙 | **Audio Live** | Capture audio en temps réel depuis le microphone ou une entrée ligne. Démodulation et décodage continu avec seuil de sensibilité ajustable. Idéal pour le décodage en direct depuis un récepteur analogique. |
| 🔢 | **Hex Direct** | Saisie manuelle d'une trame hexadécimale 406 MHz pour décodage immédiat. Utile pour l'analyse de trames capturées par d'autres systèmes ou pour la formation. |
| 🗺 | **Carte OSM interactive** | Carte OpenStreetMap intégrée avec déplacement, zoom, et position curseur en DMS. Affichage automatique de la position de la balise décodée. Préchargement de tuiles pour utilisation hors-ligne en exercice terrain. |
| 📍 | **Relevés goniométriques** | Panneau complet de saisie de relèvements : indicatif opérateur, azimut, force du signal, coordonnées DMS ou collage rapide Google Maps. Chaque relèvement est tracé comme un vecteur coloré sur la carte avec label INDICATIF/N. |
| 🔺 | **Triangulation vectorisée** | Vecteurs colorés par indicatif opérateur (80 km), flèches directionnelles, convergence visuelle des relèvements vers la position estimée de la balise. |
| ⛶ | **Carte plein écran** | Mode plein écran dédié : masque les panneaux de décodage pour afficher la carte et les relevés sur tout l'écran. Idéal pour la projection en exercice collectif. Touche Echap pour revenir. |
| 📋 | **Collage rapide Google Maps** | Saisie directe des coordonnées par copié-collé depuis Google Maps (`44,789, -1,201 120 fort`). Extraction automatique de la latitude, longitude, azimut et force du signal. |
| 🛰 | **GPS NMEA** | Support GPS via port série (NMEA 0183). Mise à jour automatique de la position opérateur sur la carte avec intervalle configurable. |
| 📊 | **Décodage complet COSPAS-SARSAT** | Trames courtes (112 bits) et longues (144 bits). Protocoles : Maritime MMSI, Aviation OACI 24 bits, Serial, National, Test, ELT-DT. BCH-1 et BCH-2 pour la validation. Position en DD°MM'SS" avec résolution fine. |
| 🎨 | **Thème clair / sombre** | Palette SAR Tactical Dark par défaut (optimisée pour le terrain de nuit). Bascule en un clic vers le thème clair. Tous les paramètres sauvegardés automatiquement. |
| 📤 | **Export / Import CSV** | Export des relèvements en CSV (point-virgule) avec indicatif, coordonnées DMS et décimales, azimut, signal et horodatage. Import CSV pour reprise de session ou échange inter-opérateurs. |
| 📝 | **Journal de décodage** | Export du journal complet de la session (trames décodées, horodatages, paramètres) vers un fichier texte. |

---

## 🚀 Modes de réception

### 📡 SDR Direct — RTL-SDR natif

Le mode SDR Direct transforme le programme en **récepteur 406 MHz autonome**. Le dongle RTL-SDR est piloté directement en Python sans logiciel intermédiaire :

- **Pipeline** : IQ brut → filtre passe-bande → démodulation FM → décimation → détection burst IQ → décodage biphase Manchester
- **Fréquences prédéfinies** : 406.022, 406.025 (défaut), 406.028, 406.031, 406.037, 406.040, 406.049, 406.052 MHz
- **Fréquences de test ADRASEC** : 434.000 MHz (ISM 70 cm), 434.275 MHz (test ADRASEC/FNRASEC)
- **Gain** : automatique ou manuel (dB)
- **VU-mètre** : indicateur de niveau IQ en temps réel
- **Seuil SNR** : ajustable pour filtrer le bruit en environnement RF difficile

### 🎙 Audio Live — Microphone / Ligne

Capture directe depuis la carte son. Brancher la sortie audio d'un récepteur analogique (scanner, transceiver) sur l'entrée micro ou ligne du PC :

- Sélection du périphérique d'entrée
- Seuil de sensibilité ajustable
- Décodage continu en temps réel

### 📁 Fichier Audio

Décodage de fichiers audio pré-enregistrés (WAV 48 kHz recommandé). Support FFmpeg pour la conversion automatique des formats M4A, MP3, OGG, FLAC.

### 🔢 Hex Direct

Saisie manuelle d'une trame hexadécimale (28 ou 36 caractères) pour décodage immédiat. Utile pour vérifier une trame capturée par un autre système ou pour la formation au format COSPAS-SARSAT.

---

## 🛠 Comment commencer ?

### 📥 Téléchargement direct de l'archive

<div align="center">

#### 📥 [**Télécharger EPIRBdecoder.7z (v5.1.1)**](https://github.com/f1gbd/F1GBD/releases/download/epirb-v5.1.1/EPIRBdecoder.7z)

*(version `epirb-v5.1.1` — voir [toutes les releases EPIRB Decoder](https://github.com/f1gbd/F1GBD/releases?q=epirb) pour les versions précédentes)*

[![Voir toutes les versions](https://img.shields.io/badge/📜_Voir_toutes_les_versions-Releases-blue)](https://github.com/f1gbd/F1GBD/releases)

</div>

### 🚀 Installation

```powershell
# 1. Décompresser l'archive EPIRBdecoder.7z dans le dossier de votre choix
#    (clic droit → 7-Zip → Extraire ici)
#
#    Vous obtenez l'arborescence suivante :
#    EPIRBdecoder\
#       ├── _internal\           (dépendances PyInstaller)
#       ├── osm_tiles_cache\     (cache des tuiles OSM, créé au 1er usage)
#       └── EPIRB-decoder.exe    ← exécutable principal
#
# 2. Double-cliquer sur EPIRB-decoder.exe pour lancer le décodeur
```

> 💡 **Aucune installation système requise** : pas d'admin, pas de modification du registre, pas de variable d'environnement. Le décodeur est entièrement autonome dans son dossier.

> 💡 **Pour le mode SDR Direct** : installer les drivers WinUSB pour le dongle RTL-SDR via [Zadig](https://zadig.akeo.ie/). Le dongle RTL-SDR V3 ou V4 doit apparaître dans Zadig avec le driver WinUSB sélectionné.

### ⚙ Configuration matérielle pour le mode SDR Direct

| Composant | Description |
|---|---|
| **Dongle RTL-SDR** | RTL-SDR V3 ou V4 (chipset RTL2832U + R820T/R828D), couvre 24-1766 MHz |
| **Driver** | WinUSB installé via Zadig |
| **Antenne** | Antenne adaptée 406 MHz (dipôle, Yagi, ou antenne large bande) |
| **Câble** | SMA vers l'antenne, USB vers le PC |

---

## 📡 Protocoles COSPAS-SARSAT décodés

| Type de balise | Protocole | Informations extraites |
|---|---|---|
| **EPIRB** | Maritime MMSI | MMSI 9 chiffres, numéro de série, position GPS |
| **ELT** | Aviation OACI 24 bits | Adresse OACI, type d'aéronef, position GPS |
| **ELT-DT** | ELT avec données | Données étendues, position haute résolution |
| **PLB** | Serial / National | Numéro de série, code pays, identification nationale |
| **Test** | Protocole de test | Balise d'exercice ADRASEC, mode EXER |

Chaque trame décodée affiche :
- **Type de protocole** et code pays (MID / code OACI)
- **Identification** de la balise (MMSI, adresse OACI, N° série)
- **Position GPS** en DD°MM'SS" (si disponible dans la trame longue 144 bits)
- **Validation BCH** (BCH-1 82 bits, BCH-2 pour trames longues)
- **Horodatage** de la réception

---

## 🗺 Carte OSM et relevés goniométriques

La carte OSM intégrée permet de visualiser en temps réel la position de la balise décodée et les relèvements goniométriques des opérateurs sur le terrain :

- **Position balise** : marqueur automatique dès qu'une trame avec position GPS est décodée
- **Relevés opérateurs** : ajout par clic droit sur la carte, saisie manuelle DMS, ou collage rapide Google Maps
- **Vecteurs colorés** : chaque opérateur a sa couleur, les vecteurs de 80 km montrent la direction du relèvement
- **Labels INDICATIF/N** : chaque vecteur est étiqueté avec l'indicatif de l'opérateur et le numéro du relèvement
- **Force du signal** : colonne dédiée dans le tableau (fort, moyen, faible, nul)
- **Mode plein écran** : bouton ⛶ pour afficher la carte sur tout l'écran avec le panneau de relevés sur le côté
- **Préchargement** : télécharger les tuiles à l'avance pour une utilisation hors-ligne en exercice terrain
- **Export/Import CSV** : sauvegarde et reprise des relevés entre sessions

### Format de collage rapide

Le champ « 📋 Collage rapide » accepte un copié-collé direct depuis Google Maps :

```
44,7889968, -1,2018104 120 signal fort
```

Format : `latitude, longitude [azimut] [force du signal]` — la virgule décimale française (`,`) et le point (`.`) sont tous deux acceptés.

---

## 💼 Cas d'usage

### 🎓 Formation ADRASEC au décodage 406 MHz

```
1. Lancer EPIRB Decoder, sélectionner l'onglet SDR Direct
2. Connecter le dongle RTL-SDR avec antenne 406 MHz
3. Cliquer sur Connecter — le VU-mètre s'active
4. Activer une balise d'exercice ADRASEC (434.275 MHz)
5. Observer le décodage automatique : burst IQ détecté → trame décodée
6. Analyser les champs : type, protocole, MMSI/OACI, position
7. Basculer sur l'onglet Carte pour visualiser la position
```

### 📡 Exercice de triangulation goniométrique

```
1. Ouvrir l'onglet Carte, activer le mode plein écran (⛶)
2. Chaque opérateur sur le terrain communique par radio :
   son indicatif, ses coordonnées GPS, et l'azimut du relèvement
3. Le coordinateur saisit chaque relèvement via le collage rapide :
   « 48,554, 2,631 045 fort »  → clic Ajouter
4. Les vecteurs convergent visuellement vers la position de la balise
5. Export CSV en fin d'exercice pour le rapport
```

### 🔍 Analyse post-exercice

```
1. Charger un fichier WAV enregistré pendant l'exercice
2. Le décodeur analyse toutes les trames présentes
3. Comparer avec les données terrain (relèvements, positions)
4. Exporter le journal de décodage pour le rapport d'exercice
```

---

## 🔧 Configuration matérielle requise

| Composant | Minimum | Recommandé |
|---|---|---|
| **Système** | Windows 10 64 bits | Windows 11 |
| **Processeur** | Intel i3 / Ryzen 3 | Intel i5 / Ryzen 5 ou plus |
| **RAM** | 4 Go | 8 Go |
| **Espace disque** | 150 Mo | 300 Mo (avec tuiles préchargées) |
| **RTL-SDR** | RTL-SDR V3 (R820T) | RTL-SDR V4 (R828D) |
| **Internet** | Requis pour la carte OSM | Mode hors-ligne possible après préchargement |

---

## 🆕 Versions récentes

| Version | Apport principal |
|---|---|
| **v5.1.1** | **Version courante** — Carte plein écran, collage rapide Google Maps, force du signal dans les relevés, panneau relevés optimisé |
| v5.0 | SDR Direct RTL-SDR natif, démodulation FM IQ, détection burst hybride, carte OSM avec relèvements goniométriques vectorisés, thème clair/sombre, GPS NMEA |
| v4.0 | Palette SAR Tactical Dark, préchargement tuiles OSM, labels INDICATIF/N sur les relèvements |
| v3.x | Carte OSM intégrée, relèvements goniométriques, export CSV |
| v2.x | Audio Live, décodage continu temps réel |
| v1.x | Décodage fichier WAV, protocoles COSPAS-SARSAT de base |

Pour le détail de tous les changements, consultez le [changelog complet sur GitHub Releases](https://github.com/f1gbd/F1GBD/releases?q=epirb).

---

## 🌐 Architecture technique

```
┌──────────────────────────────────────────────────────────────┐
│  EPIRB 406 MHz Decoder (interface Tkinter)                   │
│  - 4 onglets d'entrée : Fichier / Audio Live / Hex / SDR     │
│  - 2 onglets de sortie : Résultats / Carte OSM               │
│  - Thème SAR Tactical Dark / Clair                           │
└──────┬──────────┬─────────────┬───────────┬──────────────────┘
       │          │             │           │
┌──────▼──────┐ ┌─▼───────────┐ ┌─▼─────────┐ ┌─▼──────────────┐
│ SDR Direct  │ │ Audio Live  │ │ Fichier   │ │ Carte OSM      │
│             │ │             │ │ WAV/M4A   │ │                │
│ RTL-SDR IQ  │ │ PyAudio     │ │ FFmpeg    │ │ Tuiles OSM     │
│ Démod FM    │ │ Capture     │ │ Conversion│ │ Relevés gonio  │
│ Burst IQ    │ │ Continue    │ │ Décodage  │ │ Vecteurs 80 km │
│ 406 MHz     │ │             │ │           │ │ Plein écran    │
│ scipy/numpy │ │             │ │           │ │ GPS NMEA       │
└──────┬──────┘ └──────┬──────┘ └─────┬─────┘ └────────────────┘
       │               │              │
       └───────────────┴──────────────┘
                       │
              ┌────────▼─────────┐
              │ Décodeur biphase │
              │ Manchester       │
              │                  │
              │ BCH(82,61) t=3   │
              │ BCH-2 validation │
              │ Protocole C/S    │
              │ T.001            │
              └────────┬─────────┘
                       │
              ┌────────▼─────────┐
              │ Affichage        │
              │                  │
              │ Type / Protocole │
              │ MMSI / OACI     │
              │ Position GPS    │
              │ Carte OSM       │
              └──────────────────┘
```

---

## 🤝 Communauté

EPIRB 406 MHz Decoder est un **projet développé pour la communauté ADRASEC**, proposé librement aux opérateurs ADRASEC départementales et à la FNRASEC dans le cadre des missions de décodage **COSPAS-SARSAT 406 MHz**.

Toute contribution, retour d'exercice ou proposition d'amélioration est bienvenue via les *Issues* du dépôt GitHub.

---

<div align="center">

### 📡 Auteur

**Jean-Louis (F1GBD / F4JHW)**
*ADRASEC 77 — FNRASEC*

**Version 5.1.0 — Mai 2026**

---

*Pour toute question, contactez votre référent ADRASEC départemental.*

📡 **EPIRB 406 MHz Decoder** — *Le décodage COSPAS-SARSAT au service de la sécurité civile*

🔗 [https://github.com/f1gbd/F1GBD/tree/master/epirb](https://github.com/f1gbd/F1GBD/tree/master/epirb)

</div>
