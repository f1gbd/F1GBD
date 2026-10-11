<p align="center">
  <img src="images/EPIRBandroid-deocder_lite.jpg" width="380" alt="EPIRBdecoder — Sécurité Civile — ADRASEC — au service des recherches SATER">
</p>

<h1 align="center">EPIRBdecoder — Android</h1>

<p align="center">
  <b>Décodeur de balises de détresse 406 MHz (COSPAS-SARSAT) sur tablette et smartphone Android</b><br>
  Réception directe par clé RTL-SDR en USB-OTG · décodage sur l'appareil, sans réseau<br>
  <b>Nouveau v0.4.0</b> : le pocket <b>Quansheng UV-K1 / UV-K5</b> comme récepteur (sources UV-Kx USB et UV-Kx audio)<br>
  <i>F1GBD · ADRASEC 77 · FNRASEC — au service des recherches SATER</i>
</p>

<p align="center">
  <a href="https://github.com/f1gbd/F1GBD/releases/download/epirb-android-v0.4.0/EPIRBdecoder_android-0.4.0.apk"><img src="https://img.shields.io/badge/T%C3%89L%C3%89CHARGER-APK%20v0.4.0-e8661a?style=for-the-badge&logo=android&logoColor=white" alt="Télécharger l'APK v0.4.0"></a>
  &nbsp;
  <a href="https://github.com/f1gbd/F1GBD/releases?q=epirb-android"><img src="https://img.shields.io/badge/Toutes%20les%20versions-releases-1d4f9c?style=for-the-badge&logo=github" alt="Toutes les versions Android"></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Android-7.0%2B-3ddc84?logo=android&logoColor=white" alt="Android 7.0+">
  <img src="https://img.shields.io/badge/ABI-arm64--v8a-555" alt="arm64-v8a">
  <img src="https://img.shields.io/badge/406%20MHz-COSPAS--SARSAT-0b1d3d" alt="406 MHz COSPAS-SARSAT">
  <img src="https://img.shields.io/badge/SDR-RTL2832U%20%2F%20R820T-38bdf8" alt="RTL-SDR">
</p>

> [!WARNING]
> **Vous avez déjà l'ancienne v0.1 « EPIRBpi-decoder-lite » ?** Désinstallez-la **avant** d'installer cette version.
> Sinon Android refuse l'installation avec le message *« L'application n'a pas été installée, car le package semble ne pas être valide »* : l'APK n'est pas en cause, c'est l'ancienne version qui bloque (numéro de version et signature différents).
> Votre main courante (`Téléchargements/EPIRBpi`) est conservée.

---

## ⬇ Téléchargement et installation rapide

| | |
|---|---|
| **APK** | [`EPIRBdecoder_android-0.4.0.apk`](https://github.com/f1gbd/F1GBD/releases/download/epirb-android-v0.4.0/EPIRBdecoder_android-0.4.0.apk) (release [`epirb-android-v0.4.0`](https://github.com/f1gbd/F1GBD/releases/tag/epirb-android-v0.4.0)) |
| **Appareil** | Android 7.0 ou plus, processeur 64 bits (arm64-v8a), port USB avec mode **hôte (OTG)** |
| **Récepteur** | clé **RTL-SDR**, ou pocket **Quansheng UV-K1 / UV-K5 v3** sous [EPIRBdecoder v1.1](https://github.com/f1gbd/F1GBD/blob/HEAD/quansheng/apps/EPIRBdecoder.md) (v0.4.0) |
| **Driver SDR** | « **SDR Driver** » de Martin Marinov — [Google Play](https://play.google.com/store/apps/details?id=marto.rtl_tcp_andro) · [F-Droid](https://f-droid.org/packages/marto.rtl_tcp_andro/) |
| **Documentation** | 📘 [Manuel utilisateur (PDF)](documentation/MEMO%20-%20MANUEL_EPIRBdecoder-android.pdf) · 📄 [Fiche technique (PDF)](documentation/MEMO%20-%20FICHE-TECHNIQUE_EPIRBdecoder-android.pdf) |

1. Installez le **SDR Driver** (Play Store ou F-Droid).
2. Téléchargez l'APK depuis le téléphone ou la tablette, ouvrez-le et autorisez l'installation depuis cette source.
3. Au premier lancement, acceptez **« Accès à tous les fichiers »** : la main courante et les captures IQ seront rangées dans `Téléchargements/EPIRBpi`.
4. Branchez la clé RTL-SDR par un câble **OTG**, appuyez sur **▶ DÉMARRER L'ÉCOUTE** et autorisez l'accès USB demandé par le driver.
5. Avec un pocket Quansheng : bouton **SOURCE** → **UV-Kx USB** ou **UV-Kx audio**, puis touche **3** (DATA) sur la radio — voir [Source UV-Kx](#source-uv-kx--le-pocket-quansheng-comme-récepteur-v040).

> **Mise à jour** : depuis la v0.2.0, chaque nouvelle version s'installe **par-dessus** (réglages et main courante conservés). Le bouton **?** → **🔄 Vérifier les mises à jour** indique si une version plus récente est publiée et propose de la télécharger.

<p align="center">
  <img src="images/EPIRBdecoder_android_MAJ.png" width="400" alt="Fenêtre À propos : bouton Vérifier les mises à jour"><br>
  <sub>Bouton <b>?</b> → fenêtre <b>À propos</b> → <b>🔄 Vérifier les mises à jour</b></sub>
</p>
>
> **Venant de la v0.1.0** (EPIRBpi-decoder-lite, version Kivy) : ⚠️ **désinstallez-la d'abord** (voir l'avertissement en haut de page). La main courante de `Téléchargements/EPIRBpi` n'est pas effacée.

---

## Aperçu

<table>
  <tr>
    <td align="center" width="33%"><img src="images/EPIRBdecoder_android_screen.png" width="300" alt="Écran principal : balise décodée"></td>
    <td align="center" width="33%"><img src="images/Position_Balise.png" width="300" alt="Position de la balise dans Google Maps"></td>
    <td align="center" width="33%"><img src="images/EPIRBdecoder_android_Journal.png" width="300" alt="Main courante"></td>
  </tr>
  <tr>
    <td align="center"><b>Balise décodée</b><br><sub>Identifiant 15 HEX, pays, protocole, position décimale / DMS / MGRS, pastilles 121.5 · BCH · SYNC</sub></td>
    <td align="center"><b>Carte</b><br><sub>Position de la balise ouverte dans Google Maps, itinéraire routier en un geste</sub></td>
    <td align="center"><b>Main courante</b><br><sub>Journal horodaté de chaque balise décodée (TXT + CSV) dans Téléchargements/EPIRBpi</sub></td>
  </tr>
</table>

<p align="center">
  <img src="images/EPIRBdecoder_android_UV-K1.jpg" width="380" alt="Pocket Quansheng UV-K1 relié en OTG : balise décodée sur la tablette">
  &nbsp;
  <img src="images/EPIRBdecoder_android_UV-K1_map.jpg" width="380" alt="Position de la balise dans Google Maps"><br>
  <sub><b>v0.4.0 : le pocket Quansheng UV-K1 comme récepteur</b> (source UV-Kx USB) — balise d'entraînement décodée avec MGRS, puis ouverte dans Google Maps</sub>
</p>

<p align="center">
  <img src="images/Balise406AD77.jpg" width="800" alt="Balise 406 ADRASEC IDF"><br>
  <sub><b> Balise 406 d'Exercice SATER de l'ADRASEC IDF</b></sub>
</p>

---

## Sommaire

- [⬇ Téléchargement et installation rapide](#-téléchargement-et-installation-rapide)
- [Aperçu](#aperçu)
- [Sommaire](#sommaire)
- [Présentation](#présentation)
- [Fonctionnalités](#fonctionnalités)
  - [Réception](#réception)
  - [Décodage et affichage](#décodage-et-affichage)
  - [Terrain](#terrain)
  - [Application](#application)
- [Spécifications techniques](#spécifications-techniques)
- [Matériel requis](#matériel-requis)
- [Utilisation](#utilisation)
- [Lecture de l'écran](#lecture-de-lécran)
- [Source UV-Kx : le pocket Quansheng comme récepteur (v0.4.0)](#source-uv-kx--le-pocket-quansheng-comme-récepteur-v040)
- [Réglage du gain et diagnostic de réception](#réglage-du-gain-et-diagnostic-de-réception)
- [Captures IQ et échantillons de test](#captures-iq-et-échantillons-de-test)
- [Main courante et fichiers](#main-courante-et-fichiers)
- [Permissions](#permissions)
- [Captures terrain](#captures-terrain)
- [Historique des versions](#historique-des-versions)
- [Documentation](#documentation)
- [Crédits](#crédits)

---

## Présentation

**EPIRBdecoder Android** transforme une tablette ou un smartphone en **poste de
réception et de décodage des balises de détresse 406 MHz** pour les équipes
ADRASEC engagées en **recherche SATER** (sauvetage aéroterrestre) et lors des
exercices FNRASEC.

Une simple clé **RTL-SDR** reliée en **USB-OTG** suffit : l'application capte les
bursts de la balise (EPIRB maritime, ELT aéronautique, PLB personnelle), les
**décode entièrement sur l'appareil** — sans réseau, sans serveur — et affiche
immédiatement l'**identifiant**, le **pays**, le **protocole** et la
**position transmise** (décimale, DMS et **MGRS** pour la carto opérationnelle),
avec ouverture directe dans **Google Maps** ou **navigation routière** vers la
balise.

**Depuis la v0.4.0**, l'opérateur sur zone de recherche peut aussi utiliser son **pocket
Quansheng UV-K1 / UV-K5 v3** comme récepteur : la radio, sous l'App **EPIRBdecoder v1.1**,
reçoit et décode la balise, puis envoie le message complet à la tablette par le **câble de
programmation** ou par l'**audio**, en OTG. La tablette refait le décodage complet et
ajoute le **MGRS**, la carte, l'itinéraire et la main courante.

Le moteur de décodage est **celui de la version PC EPIRBdecoder v5.22**
(récepteur MLSE, contrôles BCH, conversion MGRS), embarqué tel quel : un burst
décodé sur Android donne exactement le même résultat que sur le PC.

---

## Fonctionnalités

### Réception
- Réception **directe RTL-SDR** en USB-OTG via le serveur `rtl_tcp` du SDR Driver (lancé automatiquement).
- **Canaux 406 MHz** : 406.022 · 406.025 · 406.028 · 406.031 · 406.037 · 406.040 MHz, et **fréquences de test** 434.000 / 434.275 MHz.
- **Gain RF manuel** réglable (20,7 à 49,6 dB) ou automatique ; fréquence et gain **mémorisés**.
- **Détection automatique des bursts** et décodage sans intervention.
- **Indicateur SIGNAL** : puissance brute (dBFS), rapport signal/bruit dans le canal de la balise, **alerte SATURATION**.
- **v0.4.0 — bouton SOURCE** : **Clé SDR**, **UV-Kx USB** (câble de programmation du pocket Quansheng, 38400 bauds) ou **UV-Kx audio** (Packet AFSK 1200 bauds de la sortie écouteur sur l'entrée micro) ; choix mémorisé.

### Décodage et affichage
- **Identifiant 15 HEX**, **pays** (MID), **protocole** (User, Standard / National Location, RLS…).
- **Position** : décimale, **DMS**, **MGRS** (y compris les offsets fins du protocole Standard Location).
- **Contrôles BCH-1 / BCH-2**, **synchronisation** (x/24), présence du **homing 121.5 MHz**.
- **Filtrage des fausses trames** : seule une trame avec **BCH-1 valide** est affichée et journalisée.
- **Tonalité d'alerte** à chaque balise décodée ; écran maintenu allumé pendant l'écoute.

### Terrain
- **Carte** : ouvre la position de la balise dans Google Maps (repli : autre appli de cartographie, puis navigateur).
- **Itinéraire** : navigation routière guidée jusqu'à la balise.
- **Main courante** automatique (**CSV** et **TXT**) : date, heure, identifiant, pays, protocole, position, MGRS, BCH, synchro, fréquence.
- **Enregistrement IQ** des bursts reçus (rejouables sur Android et sur le PC).
- **Chargement de captures IQ** `.npy` (PC ou Android) : entraînement et exercices sans balise ni dongle.

### Application
- Interface **Sécurité Civile** : cartes BALISE / POSITION, pastilles d'état colorées, lisible en extérieur, tailles de caractères **auto-ajustées** (téléphone comme tablette).
- **Écran de lancement** EPIRBdecoder.
- **À propos** : versions des composants et **🔄 Vérifier les mises à jour** (releases GitHub `epirb-android-v…`, téléchargement proposé).

---

## Spécifications techniques

| Élément | Valeur |
|---|---|
| Signal traité | Balises COSPAS-SARSAT 1ʳᵉ génération, 406 MHz, biphase-L 400 bit/s, PSK ±1,1 rad |
| Trames | Messages de 144 bits (formats court et long), synchro normale et auto-test |
| Échantillonnage dongle | 250 kéch/s, IQ 8 bits (`rtl_tcp`) |
| Accord | Oscillateur local **40 kHz sous la fréquence de la balise** (la balise n'est plus superposée au pic DC du RTL2832) |
| Gain | Manuel, **49,6 dB par défaut** ; AGC numérique RTL2832 **désactivée** |
| Canalisation | Retrait DC, transposition, filtre FIR ±10 kHz, décimation à **62,5 kéch/s** |
| Détection de burst | Puissance dans le canal, seuil **+6 dB** au-dessus du plancher de bruit suivi en continu (blocs de 100 ms) |
| Démodulation | Récepteur **MLSE** NumPy (horloge calée sur les transitions Manchester), filtres de phase **5 / 3,5 / 2,5 kHz** essayés tant que BCH-1 échoue |
| Validation | **BCH-1** obligatoire (trame rejetée sinon), BCH-2 affiché |
| Doublons | Même balise re-décodée en moins de 8 s : non rejournalisée |
| Décodeur | Moteur **EPIRBdecoder PC v5.22** (BeaconDecoder, BCH, MGRS), embarqué à l'identique |
| Captures IQ | NumPy `.npy` complex64 + `.txt` descriptif (`center_freq_hz`, `sample_rate_hz`, …) — format identique au PC |
| Fonctionnement | 100 % local : aucune connexion réseau requise (sauf « Vérifier les mises à jour ») |
| Source UV-Kx USB (v0.4.0) | Câble de programmation Kenwood (prise K : CH340, CP210x, PL2303, FTDI) en OTG, 38400 bauds 8N1, bibliothèque usb-serial-for-android |
| Source UV-Kx audio (v0.4.0) | Entrée micro 16 / 44,1 / 48 kHz ; démodulateur AFSK 1200 bauds (Bell 202) + HDLC / AX.25 avec contrôle FCS, plusieurs équilibres de tonalités ; décode jusqu'à S/B 8 dB |
| Message UV-Kx | « 406:N » (ou « S » auto-test) + 30 hex = bits 25 à 144 ; trame reconstituée, correction BCH et décodage par le moteur PC |
| Système | Android 7.0+ (API 24), arm64-v8a ; application Kotlin, traitement Python 3.13 + NumPy embarqués |

Validation : captures IQ réelles d'une balise d'exercice ADRASEC 77 (NESDR v5,
26/09/2026) rejouées à travers un serveur `rtl_tcp` simulé : décodage à chaque
burst (BCH OK, sync 24/24) ; avec bruit ajouté, la balise reste décodée ~5 dB
plus bas qu'avec la v0.1.

---

## Matériel requis

- Clé **RTL-SDR** (RTL2832U + R820T/R828D) : NooElec NESDR v5, RTL-SDR Blog V3/V4, ou clé DVB-T compatible.
- Tablette ou smartphone Android avec **USB hôte (OTG)**.
- **Câble / adaptateur OTG** adapté au connecteur de l'appareil (voir `images/OTGcable.jpg`).
- **Antenne 406 MHz** : dipôle, Yagi directive pour la goniométrie, ou antenne large bande.
- **Ou (v0.4.0)** : un pocket **Quansheng UV-K1 / UV-K5 v3** (firmware F4HWN Labs) avec l'App **EPIRBdecoder v1.1**, et son **câble de programmation** (prise K) ou un **adaptateur audio USB-C** / câble audio vers l'entrée micro.

<p align="center">
  <img src="images/SDR_SMArtSDR_v5.png" width="800" alt="SMArtSDR"><br>
  <sub><b> Fonctionne avec une Clé SDR Nooelec NESDR SMArt v5</b></sub>
</p>


---

## Utilisation

| Commande | Rôle |
|---|---|
| **SOURCE** (en bas à gauche) | **Clé SDR**, **UV-Kx USB** ou **UV-Kx audio** (v0.4.0). Se change à l'arrêt. |
| **Fréquence** (bandeau) | Choix du canal 406 MHz ou de test (clé SDR ; grisé en UV-Kx : la fréquence se règle sur la radio). Réglable pendant l'écoute. |
| **Gain** (bandeau) | Gain RF manuel ou auto (clé SDR). Réglable pendant l'écoute. |
| **▶ DÉMARRER L'ÉCOUTE** | Lance le SDR Driver (accès USB au dongle), puis l'écoute ; **■ ARRÊTER L'ÉCOUTE** pour stopper. |
| **CHARGER IQ** | Décode une capture `.npy` (sélectionnez aussi son `.txt` si possible). Fonctionne sans dongle. |
| **● ENREGISTRER** | Sauve chaque burst reçu en capture IQ (**REC ON** en rouge quand actif). |
| **JOURNAL** | Affiche la main courante, avec effacement confirmé. |
| **Carte / Itinéraire** | Position de la balise dans Google Maps / navigation vers la balise (actifs dès qu'une position est décodée). |
| **?** | À propos : versions, crédits, **🔄 Vérifier les mises à jour**. |

---

## Lecture de l'écran

<p align="center">
  <img src="images/EPIRBdecoder_android_screen.png" width="800" alt="EPIRBdecoder Android en réception terrain">
</p>

- **Bandeau** : emblème, heure et date.
- **Poste** : voyant d'état (gris = arrêté, orange = attente / burst, vert = écoute / balise décodée, rouge = erreur), statut, fréquence et gain.
- **SIGNAL** : barre du S/B dans le canal (verte au-delà de +6 dB), niveau brut en dBFS, **SATURATION** en rouge.
- **Carte BALISE** : heure et source du dernier décodage (réception, **UV-Kx USB**, **UV-Kx audio** ou fichier IQ, fréquence), identifiant 15 HEX, pays et protocole.
- **Carte POSITION** : coordonnées décimales, DMS et **MGRS** (vert), boutons Carte et Itinéraire.
- **Pastilles** : `121.5 MHz` (homing), `BCH` (OK en vert), `SYNC` (x/24).

---

## Source UV-Kx : le pocket Quansheng comme récepteur (v0.4.0)

<p align="center">
  <img src="images/EPIRBdecoder_mode_data.png" width="800" alt="Mode DATA : du pocket UV-K1 à la tablette EPIRBdecoder Android">
</p>

Le pocket **Quansheng UV-K1 / UV-K5 v3**, sous l'App **[EPIRBdecoder v1.1](https://github.com/f1gbd/F1GBD/blob/HEAD/quansheng/apps/EPIRBdecoder.md)**
(firmware F4HWN Labs, installable depuis l'[UV-K1 Apps Uploader](https://f1gbd.github.io/F1GBD/quansheng/)),
reçoit et décode la balise 406 MHz (ou la balise d'entraînement sur 434,000 MHz). En **mode DATA**
(touche **3** de la radio), il envoie chaque trame reçue à la tablette, **sans émettre** :

| Source | Câblage | Liaison |
|---|---|---|
| **UV-Kx USB** | câble de programmation Kenwood (prise K, celui de CHIRP / UV Studio) + adaptateur **OTG** | ligne texte, 38400 bauds |
| **UV-Kx audio** | sortie écouteur de la radio → entrée micro (adaptateur audio USB-C sur l'OTG, ou prise casque) ; pour un premier essai, le haut-parleur de la radio contre le micro suffit | Packet AFSK 1200 bauds |

1. **SOURCE** → **UV-Kx USB** ou **UV-Kx audio**, puis **▶ DÉMARRER L'ÉCOUTE** (autoriser l'accès au câble ou au micro la première fois).
2. Sur la radio : touche **3** (« DATA ON ») ; la balise affichée arrive aussitôt, puis chaque nouvelle trame.
3. La carte BALISE indique **UV-Kx USB** ou **UV-Kx audio** : nom du pays, protocole, position décimale, DMS et **MGRS**, BCH, Carte, Itinéraire, main courante — comme avec la clé SDR.

<p align="center">
  <img src="images/EPIRBdecoder_android_UV-K1.jpg" alt="UV-K1 en mode DATA relié en OTG à la tablette EPIRBdecoder Android : balise décodée avec MGRS" width="380">
  &nbsp;
  <img src="images/EPIRBdecoder_android_UV-K1_map.jpg" alt="Position de la balise ouverte dans Google Maps depuis EPIRBdecoder Android" width="380">
</p>
<p align="center"><em>Essai réel du 11 octobre 2026 : balise d'entraînement (générateur EPIRB OC + HackRF, 434,000 MHz) décodée par le UV-K1 sous
EPIRBdecoder v1.1 en mode DATA, transmise par le câble de programmation en OTG à la tablette sous EPIRBdecoder Android v0.4.0
(source UV-Kx USB) : 1C7E12D23F81FE0, France (227), National Loc. (Test), 48.5544° N 2.6311° E, MGRS 31U DP 72777 77988,
BCH OK, 121,5 MHz ; à droite, la position ouverte dans Google Maps par le bouton Carte</em></p>

La radio envoie le **message complet** de la balise (`406:N` + 30 caractères hexadécimaux) :
la tablette le décode avec le moteur PC, elle ne recopie pas l'écran de la radio. La source
audio décode aussi le **relais Packet** d'un autre UV-Kx (PTT ou AUTO) entendu par un récepteur
branché sur la tablette. Ligne SIGNAL : niveau audio en dBFS ; « SATURATION » → baisser le volume de la radio.

| Message | Action |
|---|---|
| « Câble UV-Kx non détecté » | câble de programmation (CH340, CP210x, PL2303, FTDI) et adaptateur OTG ; un câble de charge seul ne convient pas |
| « Accès au câble UV-Kx refusé » | relancer et accepter la demande d'accès USB |
| Rien n'arrive | « DATA ON » sur la radio (touche 3), bonne source choisie, volume de la radio (audio) |

---

## Réglage du gain et diagnostic de réception

| Ce que montre la ligne SIGNAL | Signification / action |
|---|---|
| Le S/B monte à chaque burst (toutes les ~50 s) et la balise s'affiche | Réception correcte. |
| Le S/B monte mais le statut indique **« Burst reçu — BCH invalide »** | Signal trop faible ou brouillé : orienter / changer l'antenne, se rapprocher. |
| **SATURATION** en rouge | Gain trop fort (balise proche) : baisser le gain (ex. 37,2 dB). |
| Rien ne bouge jamais | Vérifier le SDR Driver (accès USB accordé), le câble OTG, l'alimentation USB, la fréquence. |
| « Driver SDR introuvable » | Installer le SDR Driver de M. Marinov. |
| « Serveur rtl_tcp non démarré » | Accès USB refusé ou dongle déjà utilisé par une autre application. |
| « Le package semble ne pas être valide » à l'installation | L'ancienne v0.1 EPIRBpi-decoder-lite est encore installée : la désinstaller, puis relancer l'installation. |

Astuce : activez **● ENREGISTRER** pendant les essais ; les captures permettent
d'analyser a posteriori ce que l'appareil a réellement reçu.

---

## Captures IQ et échantillons de test

Des captures réelles de balises 406 MHz sont fournies dans
**[`406_samples/`](406_samples/)** pour tester le décodage **sans dongle** :

1. Copiez un `.npy` et son `.txt` de `406_samples/` sur l'appareil (ex. dans `Téléchargements`).
2. **CHARGER IQ** → sélectionnez le `.npy` (et le `.txt`).

Formats acceptés :
- captures du **PC** EPIRBdecoder (« Capturer IQ → fichier », 250 kéch/s) ;
- captures **Android** (`capture_<fréquence>_62500Hz_<horodatage>.npy`, bande de base 62,5 kéch/s) — la fréquence d'échantillonnage est lue dans le `.txt` ou, à défaut, dans le nom du fichier ;
- les captures Android se relisent aussi sur le PC (« Décoder IQ brut (MLSE) »).

---

## Main courante et fichiers

Avec l'accès à tous les fichiers accordé, tout est rangé dans
**`Téléchargements/EPIRBpi/`** (sinon dans le dossier de l'application,
`Android/data/fr.adrasec77.epirbpilite/files/EPIRBpi/`) :

| Fichier | Contenu |
|---|---|
| `main_courante.csv` | Journal tabulé, séparateur `;` (Excel / LibreOffice) |
| `main_courante.txt` | Journal lisible |
| `capture_<freq>_62500Hz_<date>.npy` + `.txt` | Bursts enregistrés (IQ complex64 + descriptif) |

Exemple de ligne de main courante :

```
2026-09-26 17:49:10 | 1C7C084B48FFBFF | France(227) | RLS/Std Loc. (code 14) | 48.55330,2.63220 | 31U DP 72858 77865 | BCH OK | sync 24/24 | 406.028 MHz
```

---

## Permissions

| Permission | Usage |
|---|---|
| Internet | Connexion au serveur `rtl_tcp` **local** du SDR Driver (127.0.0.1) ; vérification des mises à jour à la demande |
| Accès à tous les fichiers | Main courante et captures dans `Téléchargements/EPIRBpi` (facultatif) |
| Maintien de l'écran | Écoute prolongée |
| Micro (v0.4.0) | Source **UV-Kx audio** seulement, demandé au premier démarrage de cette source |
| Accès USB (v0.4.0) | Câble de programmation du pocket (source **UV-Kx USB**), demandé au premier démarrage |

Le dongle SDR est ouvert par le SDR Driver ; le câble UV-Kx par l'application. Aucune donnée n'est transmise à l'extérieur.

---

## Captures terrain

<p align="center">
  <img src="images/EPIRBandroid-decoder.jpg" width="800" alt="EPIRBdecoder Android en réception terrain">
</p>

<p align="center">
  <img src="images/EPIRBandroid-deocder_lite.jpg" width="420" alt="Ensemble téléphone + RTL-SDR + antenne 406 sur trépied">
  &nbsp;
  <img src="images/OTGcable.jpg" width="420" alt="Raccordement USB-OTG du dongle au téléphone">
</p>

<p align="center">
  <img src="images/EPIRBandroid-deocder_lite_toMap.jpg" width="800" alt="Navigation directe vers la balise 406">
</p>

<p align="center">
  <img src="images/EPIRBgenerator-decoder_Android_HackRFtx.jpeg" width="800" alt="Test SATER"><br>
  <sub><b> Utilisation d'EPIRBgenerator avec le HackRF pour tester le EPIRBdecoder Android</b></sub>
</p>

<p align="center">
  <img src="images/EPIRBandoid-VS_LVT-decoder.jpeg" width="800" alt="Test SATER"><br>
  <sub><b> Comparaison au banc de test d'EPIRBdecoder Android avec le Décodeur LVT</b></sub>
</p>

<p align="center">
  <img src="images/EPIRBandoid-VS_LVT-decoder-test.jpeg" width="800" alt="Test SATER"><br>
  <sub><b> Les trames EPIRB sont bien décodées par l'EPIRBdecoder Android et identiques à celle du Décodeur LVT</b></sub>
</p>

---

## Historique des versions

| Version | Date | Principales évolutions |
|---|---|---|
| **0.4.0** | 10/2026 | **Pocket Quansheng UV-K1 / UV-K5 comme récepteur** : bouton **SOURCE** (Clé SDR, **UV-Kx USB**, **UV-Kx audio**), avec l'App EPIRBdecoder v1.1 de la radio en mode DATA ; démodulateur AFSK 1200 bauds intégré ; MGRS, carte et main courante comme en SDR |
| 0.3.2 | 09/2026 | **Position National Location corrigée** (écart d'environ 800 m avec le décodeur F1LVT : décalage fin PDF-2 au format C/S T.001), **Hex ID** corrigé, codes National 8 / 10 / 11 décodés, moteur PC v5.22 |
| 0.3.1 | 09/2026 | **Correctifs réception SDR** : ouverture du dongle (gain), plantage au démarrage de l'écoute, relance de l'écoute (clé occupée), faux « Burst détecté » ; installation par-dessus la v0.1 signalée clairement |
| 0.3.0 | 09/2026 | Interface **Sécurité Civile** (cartes BALISE / POSITION, pastilles d'état), écran de lancement, **Vérifier les mises à jour** dans À propos |
| **0.2.0** | 09/2026 | **Réception SDR corrigée** (gain manuel, AGC coupée, accord décalé, canal étroit, MLSE multi-filtre, filtrage BCH-1), mise en page tablette, moteur PC v5.20, application Kotlin + Python |
| 0.1.0 | 06/2026 | Première version (EPIRBpi-decoder-lite, Kivy) |

---

## Documentation

| Document | Contenu |
|---|---|
| 📘 [Manuel utilisateur](documentation/MEMO%20-%20MANUEL_EPIRBdecoder-android.pdf) | Installation du driver et de l'application, description de l'écran, réception, réglage du gain, carte et itinéraire, captures IQ, main courante, mise à jour, test sans antenne, dépannage |
| 📄 [Fiche technique](documentation/MEMO%20-%20FICHE-TECHNIQUE_EPIRBdecoder-android.pdf) | Identification, architecture, matériel, chaîne de réception SDR, spécifications de décodage, fichiers produits, sécurité, validation, limites |

Anciennes versions (v0.1, EPIRBpi-decoder-lite) : [`documentation/v0.1/`](documentation/v0.1/).

---

## Crédits

Développé par **Jean-Louis NAUDIN — F1GBD / F4JHW** pour l'**ADRASEC 77** et la **FNRASEC**,
au service des recherches SATER de la Sécurité Civile.

- Driver RTL-SDR : *SDR Driver* de **Martin Marinov** (`marto.rtl_tcp_andro`, open source).
- Spécifications des balises : documents **COSPAS-SARSAT** C/S T.001.

© 2026 F1GBD — ADRASEC 77 / FNRASEC.
