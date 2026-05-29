<div align="center">

<img src="https://github.com/f1gbd/F1GBD/blob/master/epirb/doc/images/EPIRBdecoder_logo.jpg?raw=true" alt="EPIRB Suite" width="400">

### Suite complète de décodage et génération de balises de détresse COSPAS-SARSAT 406 MHz pour la formation et les opérations ADRASEC

*Décodage EPIRB/ELT/PLB — Génération de trames d'exercice — SDR Direct RTL-SDR — Démodulation FM IQ — Audio Live / Fichier WAV / Hex — Carte OSM avec relèvements goniométriques — Triangulation ELT — **APRS-IS (compatible SATERfinder Android)** — SITREP PDF — MGRS — Thème clair/sombre — Export CSV*

[![Decoder](https://img.shields.io/badge/decoder-v5.6.0-blue)](https://github.com/f1gbd/F1GBD/releases/download/epirb-v5.6.0/EPIRBdecoder.7z)
[![Generator](https://img.shields.io/badge/generator-v3.6.1-blue)](https://github.com/f1gbd/F1GBD/releases?q=epirb)
[![SATERfinder](https://img.shields.io/badge/SATERfinder_Android-v1.0-orange?logo=android)](https://github.com/f1gbd/F1GBD/tree/master/epirb/saterfinder)
[![Téléchargements](https://img.shields.io/badge/téléchargements-actifs-brightgreen?logo=github)](https://github.com/f1gbd/F1GBD/releases?q=epirb)
[![Plateforme](https://img.shields.io/badge/plateforme-Windows%2010%2F11-lightgrey.svg)]()
[![Licence](https://img.shields.io/badge/usage-ADRASEC%2FFNRASEC-green.svg)]()
[![Mission](https://img.shields.io/badge/mission-COSPAS--SARSAT-orange.svg)]()

### 🆕 v5.6.0 — Intégration APRS-IS et compatibilité SATERfinder Android

Les relèvements goniométriques d'EPIRBdecoder sont désormais **partagés en temps réel** via APRS-IS avec les équipes terrain équipées de [SATERfinder Android](https://github.com/f1gbd/F1GBD/tree/master/epirb/saterfinder). Le PCS voit apparaître automatiquement sur sa carte les relevés émis par chaque équipe ; la triangulation collective devient immédiate.

### 📥 [**Télécharger EPIRB Suite v5.6.0 (Windows)**](https://github.com/f1gbd/F1GBD/releases/download/epirb-v5.6.0/EPIRBdecoder.7z) · [**SATERfinder Android v1.0 (APK)**](https://github.com/f1gbd/F1GBD/tree/master/epirb/saterfinder)

</div>

---

## 🎯 Qu'est-ce que la suite EPIRB 406 MHz ?

La **EPIRB 406 MHz Suite** regroupe désormais **trois outils complémentaires** (deux Windows + une appli Android compagnon) pour la formation, les exercices et les opérations ADRASEC sur les balises de détresse COSPAS-SARSAT :

| Outil | Plateforme | Rôle |
|---|---|---|
| 📡 **EPIRB Decoder** (v5.6.0) | Windows 10/11 | Décodeur complet de trames 406 MHz — RTL-SDR, Audio Live, fichier WAV, Hex direct, carte OSM avec triangulation, SITREP PDF, **APRS-IS** (v5.6.0) |
| 🛰 **EPIRB Generator** (v3.6.1) | Windows 10/11 | Générateur de trames d'exercice 406 MHz — émission audio directe, PTT série, signal Manchester 400 bauds conforme COSPAS-SARSAT T.001 |
| 📱 **SATERfinder** (v1.0) | Android 7+ | Application terrain de relevés goniométriques pour équipes mobiles — carte OSM, GPS interne, triangulation ELT, **partage APRS-IS** avec EPIRBdecoder PC |

Les trois outils forment un **écosystème intégré** : le générateur produit des trames d'exercice décodées par EPIRBdecoder, les équipes terrain équipées de SATERfinder émettent leurs relèvements vers le PCS via APRS-IS, et la triangulation collective converge en temps réel sur la carte du chef de mission. Cela permet des scénarios de formation et des opérations réelles complets, sans dépendre de balises matérielles.

L'ensemble est destiné à la **formation des opérateurs ADRASEC**, aux **exercices de décodage 406 MHz**, et aux **opérations réelles** de recherche et sauvetage dans le cadre COSPAS-SARSAT.

---

## ⭐ Fonctionnalités principales

### 📡 EPIRB Decoder v5.6.0

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
| 🎯 | **Pré-positionnement visuel** | Marqueur temporaire noir sur la carte au clic droit, permettant de vérifier visuellement la position avant de confirmer le relèvement. Effacé automatiquement au relèvement suivant ou à la confirmation. |
| 🔲 | **Coordonnées MGRS** | Conversion bidirectionnelle lat/lon ↔ MGRS (Military Grid Reference System, ex: `31U DQ 52482 11717`). Mise à jour automatique dans les deux sens. Conversion WGS84 autonome intégrée, sans dépendance externe. |
| 📌 | **Zone par défaut** | Sauvegarde de la zone d'affichage courante de la carte (position et zoom) dans `decoder_setup.json`. Au redémarrage, la carte s'ouvre directement sur la dernière zone sauvegardée. Activable/désactivable par un bouton bascule. |
| 🎯 | **Triangulation ELT** | Localisation de la balise ELT par triangulation par moindres carrés avec rejet itératif des outliers (MAD). Affichage du marqueur BALISE et du cercle d'incertitude CEP 95% sur la carte. Cartouche avec position DMS, décimale, MGRS et horodatage. |
| 📋 | **SITREP SATER** | Génération d'un rapport de situation SATER complet : données balise 406 décodée, main courante des relevés ELT, résultat de triangulation. Export en texte ou en PDF professionnel type Sécurité Civile avec logo ADRASEC, tableaux formatés et capture carte OSM. |
| 🛰 | **GPS NMEA** | Support GPS via port série (NMEA 0183). Mise à jour automatique de la position opérateur sur la carte avec intervalle configurable. |
| 📍 | **Position GPS → Relevé** | Bouton « Position GPS » apparaissant dès qu'un fix GPS est valide. Un clic place le marqueur de pré-positionnement aux coordonnées GPS et pré-remplit le formulaire : il ne reste qu'à saisir l'azimut et cliquer Ajouter. |
| 📡 | **APRS-IS — partage des relevés** (v5.6.0) | Connexion à un serveur APRS-IS (`euro.aprs2.net` par défaut) pour échanger les relèvements goniométriques en temps réel avec les autres stations équipées de **SATERfinder Android** ou d'EPIRBdecoder PC. Émission sous deux formes (message texte auto-descriptif `EPIRB-GONIO` + trame objet positionnée visible sur aprs.fi), réception automatique avec ajout sur la carte. Mode émission automatique pour relayer chaque nouveau relevé. |
| 📊 | **Décodage complet COSPAS-SARSAT** | Trames courtes (112 bits) et longues (144 bits). Protocoles : Maritime MMSI, Aviation OACI 24 bits, Serial, National, Test, ELT-DT. BCH-1 et BCH-2 pour la validation. Position en DD°MM'SS" avec résolution fine. |
| 🎨 | **Thème clair / sombre** | Palette SAR Tactical Dark par défaut (optimisée pour le terrain de nuit). Bascule en un clic vers le thème clair. Tous les paramètres sauvegardés automatiquement. |
| 📤 | **Export / Import CSV** | Export des relèvements en CSV (point-virgule) avec indicatif, coordonnées DMS et décimales, azimut, signal et horodatage. Import CSV pour reprise de session ou échange inter-opérateurs. |
| 📝 | **Journal de décodage** | Export du journal complet de la session (trames décodées, horodatages, paramètres) vers un fichier texte. |

### 🛰 EPIRB Generator v3.6.1

| Icône | Fonctionnalité | Description |
|:---:|---|---|
| 🎛 | **Génération de trames 144 bits** | Construction complète d'une trame COSPAS-SARSAT T.001 : sync DETR/EXER, format long, code pays MID, protocole, identification, position GPS, codes d'urgence, BCH-1 et BCH-2 calculés automatiquement. |
| 📻 | **Encodage Manchester 400 bauds** | Signal biphase-L (Manchester) en bande de base à 400 bauds, échantillonné 48 kHz 16 bits mono. Manchester carré pur (v3.6) — spectre fidèle à une vraie balise 406 MHz. |
| 🌍 | **Base pays MID intégrée** | Plus de 25 codes pays MID (UIT-R M.585) intégrés : France (227, 228), Royaume-Uni, Allemagne, Italie, Espagne, États-Unis, Canada, Australie, Japon, etc. |
| 📡 | **Émission audio directe** | Transmission temps réel via PyAudio sur carte son ou interface CAT/Audio (Yaesu SCU-17, Digirig Mobile, etc.). Compatible avec tout émetteur radio amateur en mode FM Packet. |
| 🎚 | **PTT série multimode** | RTS, DTR ou CAT série dédié. Support de 16 transceivers HF/VHF/UHF : Yaesu (FT-817/818, FT-991, FT-710, FT-DX10/101, FTX-1...), Icom (IC-7300, IC-7100, IC-9700, IC-705...), Kenwood, Elecraft, FlexRadio, Xiegu. |
| 💾 | **Export WAV** | Génération de fichiers WAV PCM 48 kHz 16 bits mono — exploitable par tout décodeur 406 MHz, archivable pour exercices ou formation. |
| 🔄 | **Test aller-retour** | Boucle automatique de validation : génération → WAV → décodage via EPIRB Decoder → comparaison des paramètres. Validation immédiate de la conformité de la trame. |
| 🎯 | **Mode EXER ADRASEC** | Émission cyclique automatique conforme aux exercices SATER (cycle 50 s, sync SELFTEST). Activation/désactivation en un clic. |
| 🎵 | **Signal de calibration** | Tonalité continue 1 kHz pour réglage du niveau audio entre PC et émetteur. Indispensable avant tout exercice. |
| 📐 | **Conversion DMS ↔ décimal** | Saisie de position en degrés-minutes-secondes ou décimal, conversion bidirectionnelle automatique. |
| 🎨 | **Thème clair / sombre** | Palette SAR Tactical Dark cohérente avec le décodeur. Préférence persistante dans `generator_setup.json`. |

---

## ✅ Chaîne radio validée terrain (mai 2026)

Une **chaîne radio complète a été validée en émission/réception réelles** sur 434,275 MHz (fréquence de test ADRASEC) et permet le décodage parfait des trames d'exercice avec BCH-1 et BCH-2 conformes :

```
PC ──USB──▶ Yaesu SCU-17 ──audio/PTT──▶ FT-817ND (mode PKT, 434.275 MHz)
                                              │
                                              ▼
                                       Antenne 70 cm
                                              │
                                              ▼
PC ◀──USB── Digirig Mobile ◀──audio── FT-5DE (mode FM, 12.5 kHz)
```

| Étape | Équipement | Configuration |
|---|---|---|
| **1. Source logicielle** | EPIRB Generator v3.6 | Trame test : 227 (France), protocole 14 (Std Loc. RLS), ID 0425A4 |
| **2. Interface TX** | Yaesu SCU-17 | Carte son USB + PTT série CAT (Yaesu FT-817 dans `generator_setup.json`) |
| **3. Émetteur** | Yaesu FT-817ND | **Mode PKT** (Packet FM), 434,275 MHz, 0,5-5 W, entrée audio DATA arrière |
| **4. Récepteur** | Yaesu FT-5DE | Mode FM standard, 12,5 kHz, sortie audio jack 3,5 mm |
| **5. Interface RX** | Digirig Mobile | Carte son USB miniature, câble dédié Yaesu FT-5 |
| **6. Décodeur** | EPIRB Decoder v5.6.0 | Mode **Audio Live** (entrée USB Audio Codec) — décodage immédiat |

> ⚠ **Configurations à éviter** : Le mode FM standard sur l'entrée MIC du FT-817ND introduit du pre-emphasis incompatible avec le Manchester. Le mode DIG (SSB Data) utilise un filtre IF trop étroit (~2,4 kHz). Le décodage Audio Live à partir d'un récepteur FM physique calibré reste la solution la plus robuste pour la formation et les exercices.

---

## 🚀 Modes de réception (Decoder)

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
- **Mode recommandé** pour la chaîne validée FT-5DE + Digirig

### 📁 Fichier Audio

Décodage de fichiers audio pré-enregistrés (WAV 48 kHz recommandé). Support FFmpeg pour la conversion automatique des formats M4A, MP3, OGG, FLAC.

### 🔢 Hex Direct

Saisie manuelle d'une trame hexadécimale (28 ou 36 caractères) pour décodage immédiat. Utile pour vérifier une trame capturée par un autre système ou pour la formation au format COSPAS-SARSAT.

---

## 🚀 Modes de transmission (Generator)

### 🎵 Export WAV

Génération d'un fichier WAV PCM 48 kHz 16 bits exploitable par tout décodeur 406 MHz. Idéal pour préparer un kit pédagogique de trames test.

### 📡 Transmission audio directe

Envoi du signal audio en temps réel via PyAudio vers la carte son sélectionnée (généralement la sortie USB de la SCU-17 ou du Digirig). Combiné au PTT série pour piloter automatiquement l'émetteur.

### 🔄 Test aller-retour avec le décodeur

Bouton dédié qui lance automatiquement la chaîne : génération → WAV → EPIRB Decoder en mode fichier → comparaison résultats. Validation immédiate de la conformité de la trame.

### 🎯 Mode EXER ADRASEC

Émission cyclique automatique sur cycle de 50 secondes, conforme aux protocoles d'exercice FNRASEC. La trame utilise systématiquement le pattern SELFTEST (EXER) pour signaler son caractère d'exercice.

---

## 🛠 Comment commencer ?

### 📥 Téléchargement direct de l'archive

<div align="center">

#### 📥 [**Télécharger EPIRBdecoder.7z (Suite complète)**](https://github.com/f1gbd/F1GBD/releases/download/epirb-v5.6.0/EPIRBdecoder.7z)

*(archive contenant Decoder v5.6.0 + Generator v3.6.1 — voir [toutes les releases EPIRB](https://github.com/f1gbd/F1GBD/releases?q=epirb) pour les versions précédentes)*

[![Voir toutes les versions](https://img.shields.io/badge/📜_Voir_toutes_les_versions-Releases-blue)](https://github.com/f1gbd/F1GBD/releases)

</div>

### 🚀 Installation

```powershell
# 1. Décompresser l'archive EPIRBdecoder.7z dans le dossier de votre choix
#    (clic droit → 7-Zip → Extraire ici)
#
#    Vous obtenez l'arborescence suivante :
#    EPIRBdecoder\
#       ├── _internal\              (dépendances PyInstaller)
#       ├── osm_tiles_cache\        (cache des tuiles OSM, créé au 1er usage)
#       ├── EPIRB-decoder.exe       ← décodeur principal
#       └── EPIRB-generator.exe     ← générateur compagnon
#
# 2. Double-cliquer sur EPIRB-decoder.exe ou EPIRB-generator.exe pour lancer
```

> 💡 **Aucune installation système requise** : pas d'admin, pas de modification du registre, pas de variable d'environnement. La suite est entièrement autonome dans son dossier.

> 💡 **Pour le mode SDR Direct** : installer les drivers WinUSB pour le dongle RTL-SDR via [Zadig](https://zadig.akeo.ie/). Le dongle RTL-SDR V3 ou V4 doit apparaître dans Zadig avec le driver WinUSB sélectionné.

### ⚙ Configuration matérielle

#### Pour le mode SDR Direct (Decoder)

| Composant | Description |
|---|---|
| **Dongle RTL-SDR** | RTL-SDR V3 ou V4 (chipset RTL2832U + R820T/R828D), couvre 24-1766 MHz |
| **Driver** | WinUSB installé via Zadig |
| **Antenne** | Antenne adaptée 406 MHz (dipôle, Yagi, ou antenne large bande) |
| **Câble** | SMA vers l'antenne, USB vers le PC |

#### Pour la chaîne radio Generator → Decoder (validée terrain)

| Composant | Description |
|---|---|
| **Émetteur TX** | Yaesu FT-817ND (mode PKT recommandé) ou tout TX FM Packet équivalent |
| **Interface TX** | Yaesu SCU-17 ou interface équivalente (USB Audio + PTT série) |
| **Récepteur RX** | Yaesu FT-5DE (mode FM standard) ou tout RX FM 12,5 kHz |
| **Interface RX** | Digirig Mobile avec câble dédié Yaesu FT-5 |
| **Fréquence** | 434,275 MHz (test ADRASEC/FNRASEC) — JAMAIS 406,025 MHz opérationnel |

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
- **Pré-positionnement** : marqueur temporaire noir au clic droit pour vérifier la position avant confirmation
- **Coordonnées MGRS** : champ MGRS synchronisé avec les coordonnées lat/lon (conversion bidirectionnelle WGS84)
- **Préchargement** : télécharger les tuiles à l'avance pour une utilisation hors-ligne en exercice terrain
- **Zone par défaut** : bouton 📌 pour sauvegarder la position/zoom courants et retrouver la même vue au prochain lancement
- **Triangulation ELT** : bouton 🎯 Balise ELT — triangulation par moindres carrés avec rejet MAD des outliers, cercle CEP 95% affiché sur la carte
- **SITREP SATER** : bouton 📋 SITREP — rapport de situation complet exportable en texte ou PDF professionnel (logo ADRASEC, tableaux, capture carte OSM)
- **Export/Import CSV** : sauvegarde et reprise des relevés entre sessions

### Format de collage rapide

Le champ « 📋 Collage rapide » accepte un copié-collé direct depuis Google Maps :

```
44,7889968, -1,2018104 120 signal fort
```

Format : `latitude, longitude [azimut] [force du signal]` — la virgule décimale française (`,`) et le point (`.`) sont tous deux acceptés.

<img src="https://github.com/f1gbd/F1GBD/blob/master/epirb/doc/images/EPIRBdecoder_v56.jpg?raw=true" alt="EPIRBdécoder carte" width="400">

---

## 📡 APRS-IS — partage temps réel avec SATERfinder Android (v5.6.0)

Depuis la **v5.6.0**, l'onglet Carte d'EPIRBdecoder intègre un client **APRS-IS** qui permet d'échanger les relèvements goniométriques avec les opérateurs terrain équipés de l'application Android **[SATERfinder](https://github.com/f1gbd/F1GBD/tree/master/epirb/saterfinder)** (et entre stations EPIRBdecoder).

### Principe

Chaque relevé est diffusé sur le réseau **APRS-IS** sous deux formes complémentaires :

- Un **message APRS auto-descriptif** de préfixe `EPIRB-GONIO` contenant tous les paramètres (indicatif, lat, lon, azimut, signal, horodatage). Ce format propriétaire est reconnu et automatiquement ajouté à la carte par toute station EPIRBdecoder ou SATERfinder connectée à APRS-IS.
- Une **trame objet APRS positionnée** (format standard) qui apparaît sur **aprs.fi** et chez toutes les stations APRS classiques.

### Configuration

Dans l'onglet **Carte**, sous la ligne GPS, la section *APRS-IS* permet de saisir :

| Champ | Description |
|---|---|
| **Indicatif** | Indicatif amateur utilisé pour l'authentification APRS-IS |
| **Passcode** | Code numérique amateur (bouton **Calc** pour calcul automatique) |
| **Serveur** | `euro.aprs2.net` par défaut, port `14580` |
| **Émission auto** | Si coché, chaque nouveau relevé ajouté est automatiquement diffusé |
| **Envoyer relevé sélectionné** | Diffuse manuellement le relevé sélectionné dans la liste |

Le bouton **Se connecter** établit la liaison ; le statut sous le panneau confirme l'authentification (`Connecté APRS-IS en tant que ...`) puis chaque émission et réception. Tous ces paramètres sont mémorisés dans **`decoder_setup.json`** et restaurés au prochain lancement.

### Cas d'usage opérationnel ADRASEC

- **Chef de mission au PCS** : équipe son PC avec EPIRBdecoder, se connecte à APRS-IS et reçoit en temps réel sur sa carte tous les relèvements émis par les équipes terrain via leur smartphone.
- **Équipes goniométrie terrain** : utilisent **SATERfinder Android** sur smartphone, prennent le relèvement à l'antenne Yagi, l'envoient en un geste sur APRS-IS — il apparaît immédiatement au PCS.
- **Triangulation collective** : dès que plusieurs équipes ont émis leur relèvement, le PCS lance la **Triangulation ELT** (bouton dédié) qui calcule la position estimée et le cercle CEP95 à partir de l'ensemble des azimuts reçus.

> Le passcode APRS-IS n'est nécessaire que pour **émettre**. La réception seule fonctionne avec un passcode `-1` (lecture seule), utile pour un poste d'observation passif.

---

## 💼 Cas d'usage

### 🎓 Formation ADRASEC au décodage 406 MHz (avec le Generator)

```
1. Lancer EPIRB Generator, configurer la trame d'exercice :
   - Pays 227 (France), protocole Std Loc. RLS (14)
   - ID balise (ex : 0425A4), position fictive
   - Cocher le mode EXER (sync SELFTEST)
2. Lancer EPIRB Decoder en mode Audio Live (entrée Digirig)
3. Mettre le FT-817ND en mode PKT sur 434,275 MHz
4. Mettre le FT-5DE en mode FM sur 434,275 MHz
5. Cliquer « Transmettre » dans le Generator
6. Observer le décodage instantané dans le Decoder :
   burst détecté → trame décodée → carte mise à jour
7. Analyser les champs avec les stagiaires : type, protocole, position, BCH
```

### 📡 Exercice de triangulation goniométrique

```
1. Ouvrir l'onglet Carte du Decoder, activer le mode plein écran (⛶)
2. Si un GPS est connecté, activer le GPS NMEA (port COM)
3. Chaque opérateur sur le terrain communique par radio :
   son indicatif, ses coordonnées GPS, et l'azimut du relèvement
4. Le coordinateur saisit chaque relèvement :
   - Via le bouton « 📍 Position GPS » si le GPS est actif (pré-remplit les coordonnées)
   - Ou via le collage rapide : « 48,554, 2,631 045 fort » → clic Ajouter
5. Cliquer sur « 🎯 Balise ELT » pour trianguler la position estimée
6. Le cercle CEP 95% s'affiche sur la carte avec le marqueur BALISE
7. Cliquer sur « 📋 SITREP » pour générer le rapport de situation
8. Exporter en PDF professionnel avec logo ADRASEC et capture carte
```

### 🔄 Validation de chaîne radio avant exercice

```
1. Lancer le Generator, mode EXER actif
2. Lancer le Decoder en Audio Live (Digirig)
3. Vérifier l'arrivée propre du signal de calibration 1 kHz
   (VU-mètre dans la zone Optimal/verte)
4. Émettre une trame de test, vérifier décodage BCH-1 OK, BCH-2 OK
5. Si OK : chaîne validée, exercice peut commencer
6. Si KO : vérifier mode TX (PKT), niveau audio, fréquence, antennes
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
| **Espace disque** | 200 Mo | 400 Mo (avec tuiles préchargées) |
| **RTL-SDR (Decoder)** | RTL-SDR V3 (R820T) | RTL-SDR V4 (R828D) |
| **Interface TX (Generator)** | Câble USB-série + PTT | Yaesu SCU-17 ou équivalent |
| **Interface RX (Decoder Audio)** | Carte son PC | Digirig Mobile ou équivalent |
| **Internet** | Requis pour la carte OSM | Mode hors-ligne possible après préchargement |

---

## 🆕 Versions récentes

### 📡 EPIRB Decoder

| Version | Apport principal |
|---|---|
| **v5.6.0** | **Version courante** — Intégration **APRS-IS** dans l'onglet Carte : connexion à `euro.aprs2.net`, émission et réception de relèvements goniométriques en temps réel avec les autres stations EPIRBdecoder et avec l'application Android compagnon **SATERfinder**. Protocole `EPIRB-GONIO` partagé. Sauvegarde indicatif / passcode / serveur dans `decoder_setup.json`. Émission automatique optionnelle de chaque nouveau relevé. |
| v5.5.1 | Triangulation ELT par moindres carrés avec CEP 95%, SITREP SATER PDF professionnel avec logo ADRASEC et capture carte, bouton Position GPS → Relevé |
| v5.3.x | Coordonnées MGRS, pré-positionnement visuel, zone carte sauvegardée, bouton Position GPS |
| v5.2.x | Carte plein écran, collage rapide Google Maps, force du signal dans les relevés, panneau relevés optimisé |
| v5.0 | SDR Direct RTL-SDR natif, démodulation FM IQ, détection burst hybride, carte OSM avec relèvements goniométriques vectorisés, thème clair/sombre, GPS NMEA |
| v4.0 | Palette SAR Tactical Dark, préchargement tuiles OSM, labels INDICATIF/N sur les relèvements |
| v3.x | Carte OSM intégrée, relèvements goniométriques, export CSV |
| v2.x | Audio Live, décodage continu temps réel |
| v1.x | Décodage fichier WAV, protocoles COSPAS-SARSAT de base |

### 🛰 EPIRB Generator

| Version | Apport principal |
|---|---|
| **v3.6.1** | **Version courante** — Suppression du filtre passe-bas en bande de base, Manchester carré pur fidèle au signal d'une vraie balise 406, marge de décodage maximale en chaîne FM Packet |
| v3.5 | Filtre passe-bas 1200 Hz Butterworth ordre 4, contenu spectral élargi |
| v3.4 | Version initiale GUI Pro, palette SAR Tactical Dark, support 16 transceivers CAT, mode EXER ADRASEC |

Pour le détail de tous les changements, consultez le [changelog complet sur GitHub Releases](https://github.com/f1gbd/F1GBD/releases?q=epirb).

---

## 🌐 Architecture technique

```
┌──────────────────────────────────────────────────────────────────────┐
│                    EPIRB 406 MHz Suite                               │
│                                                                      │
│  ┌────────────────────────────┐  ┌────────────────────────────────┐  │
│  │  EPIRB Generator v3.6      │  │  EPIRB Decoder v5.4            │  │
│  │  (interface Tkinter)       │  │  (interface Tkinter)           │  │
│  │                            │  │                                │  │
│  │  - Construction trame 144  │  │  - 4 onglets d'entrée :        │  │
│  │  - Encodage Manchester     │  │    Fichier / Audio Live /      │  │
│  │  - Export WAV / TX direct  │  │    Hex / SDR Direct            │  │
│  │  - PTT RTS/DTR/CAT         │  │  - 2 onglets de sortie :       │  │
│  │  - Mode EXER ADRASEC       │  │    Résultats / Carte OSM       │  │
│  └────────────┬───────────────┘  └────────┬───────────────────────┘  │
└───────────────┼───────────────────────────┼──────────────────────────┘
                │                           │
                ▼                           ▼
┌──────────────────────────┐  ┌──────────────────────────────────────┐
│  Émetteur radio amateur  │  │  Décodage multi-mode                 │
│                          │  │                                      │
│  - SCU-17 / Digirig      │  │  - SDR Direct (RTL-SDR IQ)           │
│  - FT-817ND (PKT)        │  │  - Audio Live (PyAudio)              │
│  - 434,275 MHz           │  │  - Fichier WAV/M4A (FFmpeg)          │
│  - 5 W max               │  │  - Hex Direct (saisie)               │
└─────────────┬────────────┘  └──────────────┬───────────────────────┘
              │                              │
              ▼                              │
        Onde radio 70 cm                     │
              │                              │
              ▼                              │
┌──────────────────────────┐                 │
│  Récepteur radio amateur │                 │
│                          │                 │
│  - FT-5DE (mode FM)      │                 │
│  - Digirig Mobile        │─────────────────┘
│  - Audio USB             │
└──────────────────────────┘
                                             │
                                             ▼
                              ┌──────────────────────────────┐
                              │ Décodeur biphase Manchester  │
                              │                              │
                              │ BCH(82,61) t=3               │
                              │ BCH-2 validation             │
                              │ Protocole COSPAS-SARSAT      │
                              │ T.001                        │
                              └──────────────┬───────────────┘
                                             │
                                             ▼
                              ┌──────────────────────────────┐
                              │ Affichage                    │
                              │                              │
                              │ Type / Protocole             │
                              │ MMSI / OACI                  │
                              │ Position GPS                 │
                              │ Carte OSM + Triangulation    │
                              │ SITREP PDF ADRASEC           │
                              └──────────────────────────────┘
```

---

## 📜 Mention légale

La suite EPIRB 406 MHz est destinée à la **formation et aux exercices ADRASEC** dans le cadre des activités de la FNRASEC.

**Toute émission radioélectrique sur 406,025 MHz (fréquence opérationnelle COSPAS-SARSAT) est strictement interdite.** Les transmissions de test du Generator doivent s'effectuer sur charge fictive ou sur les fréquences amateurs autorisées (434,275 MHz typiquement), exclusivement avec le pattern de synchronisation SELFTEST (EXER).

La responsabilité de l'usage opérationnel incombe à l'opérateur radio amateur titulaire de la licence.

---

## 🤝 Communauté

EPIRB 406 MHz Suite est un **projet développé pour la communauté ADRASEC**, proposé librement aux opérateurs ADRASEC départementales et à la FNRASEC dans le cadre des missions de décodage **COSPAS-SARSAT 406 MHz**.

Toute contribution, retour d'exercice ou proposition d'amélioration est bienvenue via les *Issues* du dépôt GitHub.

---

<div align="center">

### 📡 Auteur

**Jean-Louis (F1GBD / F4JHW)**
*ADRASEC 77 — FNRASEC*

**EPIRB Decoder v5.6.0 + EPIRB Generator v3.6.1 — Mai 2026**

---

*Pour toute question, contactez votre référent ADRASEC départemental.*

📡 **EPIRB 406 MHz Suite** — *Le décodage et la génération COSPAS-SARSAT au service de la sécurité civile*

🔗 [https://github.com/f1gbd/F1GBD/tree/master/epirb](https://github.com/f1gbd/F1GBD/tree/master/epirb)

</div>
