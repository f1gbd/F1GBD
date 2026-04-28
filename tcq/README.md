<div align="center">

<img src="images/TCQ_logo.png" alt="TCQ" width="200">

# TCQ

### La plateforme de communications radio multi-modes pour les opérateurs ADRASEC

*LXMF/Reticulum — VARA HF/FM/SAT — Packet AX.25 — MeshCore LoRa — SSTV — CW/Morse — BBS — PDF Radio*

[![Plateforme](https://img.shields.io/badge/plateforme-Windows%2010%2F11-lightgrey.svg)]()
[![Architecture](https://img.shields.io/badge/arch-x86__64%20%7C%20ARM64-orange.svg)]()
[![Licence](https://img.shields.io/badge/usage-ADRASEC%2FFNRASEC-green.svg)](https://github.com/f1gbd/F1GBD/blob/master/LICENSE.txt)
[![Version TCQ](https://img.shields.io/github/v/release/f1gbd/F1GBD?filter=tcq-*&label=TCQ&color=blue)](https://github.com/f1gbd/F1GBD/releases?q=tcq)

### 📥 Installation rapide en 1 commande PowerShell

```powershell
iwr https://github.com/f1gbd/F1GBD/raw/master/tcq/Install-TCQ.ps1 -OutFile $env:TEMP\Install-TCQ.ps1; & $env:TEMP\Install-TCQ.ps1
```

*(à lancer en PowerShell administrateur — l'installeur télécharge automatiquement la dernière version de TCQ disponible)*

[**📜 Toutes les releases TCQ**](https://github.com/f1gbd/F1GBD/releases?q=tcq) • [**📚 Documentation**](https://github.com/f1gbd/F1GBD/tree/master/tcq/TCQ%20Documentations)

</div>

---

## 🎯 Qu'est-ce que TCQ ?

**TCQ** (TransCommunication Quantique) est une plateforme intégrée de communications radio numériques qui réunit dans une seule application Windows tous les modes utilisés en exercice et en intervention réelle par les opérateurs ADRASEC :

- 📨 **Messagerie chiffrée résiliente** sur Reticulum/LXMF (multi-saut, multi-transport)
- 📡 **Modems haute performance** VARA HF, VARA FM et VARA SAT
- 📻 **Packet radio AX.25** via Direwolf intégré (KISS et AGWPE)
- 🌐 **Réseaux maillés LoRa** via MeshCore natif
- 🖼️ **Réception SSTV temps réel** avec waterfall et templates `.stt`
- 🎵 **Décodage et QSO CW automatiques** (QSObrain)
- 📬 **Bulletin Board System** (BBS) sur TNC Packet et MeshCore
- 📄 **Transmission PDF par radio** avec compression LZMA et fragmentation

Conçu pour les opérations ADRASEC et les exercices de sécurité civile, TCQ privilégie la **robustesse**, la **tolérance aux ruptures de liaison** et la **simplicité d'utilisation sur le terrain**. Le binaire est autonome (PyInstaller) — **aucune installation Python requise**.

<p align="center">
  <img src="images/TCQ_main_interface.png" alt="Interface principale TCQ v10.11" width="800"/>
  <br><i>Interface principale de TCQ v10.11</i>
</p>

---

## ⭐ Fonctionnalités principales

| Icône | Fonctionnalité | Description |
|:---:|---|---|
| 📨 | **LXMF / Reticulum** | Messagerie chiffrée bout-en-bout (X25519 + AES-128 + HMAC-SHA256), multi-saut, résiliente. Compatible TCP, série, LoRa, packet AX.25 et passerelle VARA. |
| 📡 | **VARA HF / FM / SAT** | Modems ARQ haute performance (EA5HVK) intégrés avec protection idle/timeout, suspension/reprise des transferts, détection automatique du chemin VARA. |
| 📻 | **TNC Packet (AX.25)** | Direwolf lancé automatiquement avec configuration adaptée à votre carte son. Modes KISS et AGWPE. Support BBS et PDF radio. |
| 🌐 | **MeshCore LoRa** | Protocole mesh LoRa natif pour communications de proximité en zone d'exercice ou d'intervention. |
| 🖼️ | **SSTV temps réel** | Décodeur porté de slowrx — Scottie (S1/S2/SDX), Martin (M1/M2), Robot (36/72), PD (50→240). Waterfall + visualiseur plein écran + bouton Resync. |
| 🎵 | **CW / Morse** | Décodeur DSP avec seuillage adaptatif et clustering K-means. **QSObrain** pour QSO CW entièrement autonomes (CSMA, WPM adaptatif, anti-self-CQ). |
| 📬 | **BBS Multi-modes** | Bulletin Board System sur TNC Packet et MeshCore avec compteur paquets, réassemblage automatique, persistance SQLite. |
| 📄 | **PDF Radio** | Transmission de documents (SITREP, MEMO) avec compression LZMA, fragmentation adaptative, CRC par fragment, ACK et reprise sélective. |
| 🛰️ | **APRS / SATER** | Module dédié à la recherche de balises et au tracking sur fréquences APRS satellite. |
| 🔐 | **100% local** | Aucune télémétrie, aucune connexion externe non sollicitée. Toutes les communications restent sous le contrôle de l'opérateur. |

---

## 🌌 TCQ : du concept Quantique au programme multi-modes

Le projet TCQ est né d'une exploration de la **TransCommunication Quantique** appliquée aux réseaux radio résilients : une couche éducative sur Reticulum permettant de simuler des principes de communication quantique (Super Dense Coding, téléportation quantique) dans le contexte des messageries radio chiffrées LXMF.

À partir de la version 10.x, TCQ s'est étoffé pour devenir une **plateforme opérationnelle multi-modes** intégrant tous les outils nécessaires aux communications d'urgence ADRASEC, tout en conservant le module quantique éducatif (`qsim_lib`, `qit_lib`) comme couche pédagogique au-dessus de la messagerie LXMF.

> 💡 La présente documentation couvre le **programme TCQ v10.11** (plateforme opérationnelle). Les fondements conceptuels et le mémo TCQ Quantique original sont documentés dans le dossier [TCQ Documentations](https://github.com/f1gbd/F1GBD/tree/master/tcq/TCQ%20Documentations).

---

## 🚀 Pourquoi un opérateur ADRASEC y gagne

> **Une seule application pour tous les modes**
> Plus besoin de jongler entre 6 logiciels différents : LXMF, VARA, Direwolf, MeshCore, SSTV, CW — tout est intégré dans une interface cohérente.

> **Configuration zéro-friction**
> Direwolf est lancé et configuré automatiquement. La carte son est détectée. La passerelle VARA s'auto-installe. Plus de `direwolf.conf` à éditer à la main.

> **Robustesse opérationnelle**
> Reprise sur erreur sans retransmission complète des fichiers. Anti-collision CSMA sur CW. Protection des transferts VARA contre les déconnexions. Pensé pour le terrain.

> **Mise à disposition de la base ADRASEC**
> Compatible avec les protocoles standards (LXMF, AX.25, VARA, MeshCore) — interopère avec les autres stations ADRASEC et la FNRASEC sans configuration spécifique.

> **Confidentialité totale**
> Chiffrement bout-en-bout natif sur LXMF. Aucune télémétrie, aucun cloud. Vos communications restent strictement locales et chiffrées.

> **Compatible toutes architectures Windows**
> Binaires natifs x86_64 ET ARM64 (Surface Pro, mini-PC ARM). Détection automatique de la DLL PortAudio adaptée. Aucune manipulation manuelle nécessaire.

---

## 💼 Cas d'usage concrets

### 📡 Communications d'exercice ADRASEC

```
• Diffusion d'un SITREP en PDF compressé via VARA HF (départemental)
• Messagerie LXMF bidirectionnelle entre PC ADRASEC et stations mobiles
• Activation d'un BBS de section sur fréquence packet régionale
• Réception d'images SSTV en provenance d'une station portable
```

### 🚨 Opérations réelles

```
• Liaison résiliente Reticulum sur LoRa lors d'une coupure des réseaux conventionnels
• Transmission de documents formels par radio (SITREP, fiches d'intervention)
• Recherche de balises ELT 121.5 MHz avec module SDR (RTL-SDR)
• QSO CW automatisé pour maintien de liaison faible signal
```

### 🎓 Formation et entraînement

```
• Démonstration des modes numériques pour nouveaux opérateurs
• Exercices CW automatisés contre QSObrain (mode AUTO)
• Tests de chaîne PDF radio entre deux stations
• Apprentissage du protocole AX.25 via TNC Packet intégré
```

---

## 🛠 Comment commencer ?

### ⚡ Méthode automatique *(recommandée)*

Un script PowerShell **fait toute l'installation pour vous** : recherche de la dernière release TCQ, téléchargement de `TCQ.7z`, vérification SHA-256, décompression dans `C:\TCQ\`, création du raccourci bureau.

> 🔍 **Important** : le dépôt F1GBD héberge plusieurs applications (TCQ, IAbrain, etc.). Le script identifie automatiquement la **dernière release dont le tag commence par `tcq-`** parmi toutes les releases du dépôt — il ne se trompe jamais d'application, même si la dernière release publiée est IAbrain.

**1. Ouvrez PowerShell en mode administrateur**

**2. Lancez la commande** :

```powershell
# Autoriser l'exécution des scripts (cette session uniquement)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

# Télécharger et lancer l'installeur officiel TCQ
iwr https://github.com/f1gbd/F1GBD/raw/master/tcq/Install-TCQ.ps1 -OutFile $env:TEMP\Install-TCQ.ps1
& $env:TEMP\Install-TCQ.ps1
```

Le script :
- Installe 7-Zip via winget si absent
- Interroge l'API GitHub pour trouver la dernière release au tag `tcq-vX.Y.Z`
- Télécharge l'archive `TCQ.7z` depuis l'URL exacte de cette release
- Vérifie le SHA-256 publié dans la description de la release
- Sauvegarde l'installation existante (le cas échéant) avant écrasement
- Crée un raccourci bureau

### 🛠 Méthode manuelle *(utilisateurs avancés)*

Si vous préférez télécharger manuellement (par exemple sur un poste sans accès Internet en PowerShell) :

**1. Allez sur la [page des Releases TCQ filtrées](https://github.com/f1gbd/F1GBD/releases?q=tcq)** *(le filtre `?q=tcq` n'affiche que les releases TCQ, pas IAbrain)*

**2. Cliquez sur la dernière release** *(la plus en haut, tag au format `tcq-vX.Y.Z`)*

**3. Téléchargez `TCQ.7z`** et notez le SHA-256 publié dans la description

**4. Vérifiez l'intégrité et installez** :

```powershell
# Vérifier l'intégrité
Get-FileHash -Algorithm SHA256 TCQ.7z

# Décompresser dans C:\
# (clic droit sur l'archive → 7-Zip → Extraire vers "C:\")

# Lancer C:\TCQ\TCQ.exe
```

> 💡 **Astuce** : créez un raccourci de `TCQ.exe` sur votre bureau pour un lancement rapide.

### 🚀 Première utilisation

Au premier démarrage :

1. **Paramètres → Identité opérateur** : renseignez votre indicatif, locator et nom
2. **Paramètres → Audio** : sélectionnez votre carte son (entrée/sortie radio)
3. **Paramètres → Reticulum** : laissez les valeurs par défaut, ou ajustez selon votre interface RNode/LoRa
4. **Paramètres → VARA** : indiquez le chemin de `VARA.exe` (HF/FM/SAT) si installé
5. Sélectionnez un mode dans la barre d'onglets et commencez à émettre/recevoir

> ⏱ Comptez **5 minutes** pour la première configuration, ensuite TCQ est utilisable au quotidien sans réglage supplémentaire.

---

## 🆕 Nouveautés v10.11

### Module SSTV (refonte majeure)

- ✅ Décodeur SSTV temps réel porté de **slowrx** (open source)
- ✅ **Waterfall spectrogramme** en direct + visualiseur plein écran
- ✅ **Système d'overlays** multi-textes au format `.stt` (JSON)
- ✅ **Champs RSV** + variables de template (`%call`, `%RSV`, `%date`, `%time`, `%utc`, `%mode`)
- ✅ Correction artefacts Robot 36 + recherche DFT du sync pulse
- ✅ Fix décodage couleurs Scottie S1 / S2 / SDX
- ✅ Bouton **Resync** pour re-décoder les WAV de debug

<p align="center">
  <img src="images/TCQ_sstv_decoder.png" alt="Décodeur SSTV avec waterfall" width="800"/>
  <br><i>Décodeur SSTV avec waterfall spectrogramme et visualiseur image</i>
</p>

### Module VARA / PDF radio

- ✅ Protection des transferts PDF/image/fichier (suspension idle/timeout)
- ✅ Système de transmission PDF radio (LZMA + fragmentation TNC, frame unique VARA)
- ✅ Application autonome **PDFteleporter.py**

### Module BBS

- ✅ Intégration BBS pour modes **TNC Packet** et **MeshCore LoRa**
- ✅ Compteur de paquets et réassemblage automatique
- ✅ Debug BBS MeshCore LoRa testé sur matériel réel

### Plateforme

- ✅ Détection automatique des DLL PortAudio ARM64 / x86_64
- ✅ Correctifs DPI scaling Windows 10 vs Windows 11
- ✅ Personnalisation du spec PyInstaller pour build optimisé
- ✅ Intégration GPS NMEA via port COM
- ✅ Améliorations thèmes clair / sombre

---

## 📚 Documentation complète

L'ensemble de la documentation TCQ (manuels, mémos techniques, notes techniques) est rassemblée dans le dossier [**TCQ Documentations**](https://github.com/f1gbd/F1GBD/tree/master/tcq/TCQ%20Documentations) du dépôt.

### 📘 Notes Techniques (NT) — référence opérationnelle

- 📘 [**NT100 TCQ — Pour une Communication Résiliente**](TCQ%20Documentations/NT100%20TCQ%20-%20Pour%20une%20Communication%20R%C3%A9siliente.pdf) — Note de cadrage : pourquoi et comment TCQ assure la résilience des communications ADRASEC
- 📘 [**NT101 TCQ — Station MORSE CW**](TCQ%20Documentations/NT101%20TCQ%20-%20Station%20MORSE%20CW.pdf) — Configuration et exploitation du module CW/Morse de TCQ
- 📘 [**NT103 TCQ-BBS Multimodes**](TCQ%20Documentations/NT103%20TCQ-BBS_Multimodes.pdf) — Architecture du BBS multi-modes (TNC Packet + MeshCore LoRa)
- 📘 [**NT105 TCQ — Manuel Module SSTV**](TCQ%20Documentations/NT105%20TCQ%20-Manuel%20Module%20SSTV.pdf) — Manuel utilisateur complet du module SSTV (décodeur, templates, RSV)

### 📋 MEMOs techniques — guides pratiques

- 📋 [**MEMO — Fiche Technique TCQ-APRS-SATER**](TCQ%20Documentations/MEMO%20-%20Fiche%20Technique%20TCQ-APRS-SATER.pdf) — Mise en œuvre du module APRS/SATER pour la recherche de balises
- 📋 [**MEMO — TCQ-BBS**](TCQ%20Documentations/MEMO%20-%20TCQ-BBS.pdf) — Référence des commandes et fonctionnement du BBS TCQ
- 📋 [**MEMO — TCQ-CW QSO AUTO**](TCQ%20Documentations/MEMO%20-%20TCQ-CW_QSO_AUTO.pdf) — Configuration du mode QSObrain pour QSO CW autonomes
- 📋 [**MEMO — TCQ-Packet BBS**](TCQ%20Documentations/MEMO%20-%20TCQ-Packet_BBS.pdf) — Procédure d'accès au BBS via TNC Packet
- 📋 [**MEMO — TCQ-Packet Script-MTL**](TCQ%20Documentations/MEMO%20-%20TCQ-Packet_Script-MTL.pdf) — Scripts MTL pour automatisation packet radio

> 📂 **[Accéder au dossier complet TCQ Documentations](https://github.com/f1gbd/F1GBD/tree/master/tcq/TCQ%20Documentations)**

### 🔗 Ressources externes

- [Reticulum Network Stack](https://reticulum.network/) (Mark Qvist)
- [LXMF Specification](https://github.com/markqvist/LXMF)
- [Direwolf SoundCard TNC](https://github.com/wb2osz/direwolf) (John Langner WB2OSZ)
- [VARA Modem](https://rosmodem.wordpress.com/) (José Alberto Nieto Ros, EA5HVK)
- [slowrx SSTV decoder](https://github.com/windytan/slowrx) (Oona Räisänen)

---

## 🌐 Architecture technique

```
┌──────────────────────────────────────────────────┐
│  TCQ.exe (binaire PyInstaller autonome)          │
│  - GUI Tkinter, multi-onglets                    │
│  - DSP audio NumPy/SciPy/PortAudio               │
│  - Cryptographie Reticulum native                │
└─┬─────────┬──────────┬───────────┬──────────┬────┘
  │         │          │           │          │
  │         │          │           │          │
┌─▼──────┐ ┌▼────────┐ ┌▼────────┐ ┌▼────────┐ ┌▼─────┐
│ LXMF / │ │ VARA    │ │ TNC     │ │ MeshCore│ │ SSTV │
│ Reticu │ │ HF/FM/  │ │ Packet  │ │  LoRa   │ │  CW  │
│ lum    │ │ SAT     │ │ (Dire-  │ │         │ │ BBS  │
│        │ │         │ │ wolf)   │ │         │ │ PDF  │
└────────┘ └─────────┘ └─────────┘ └─────────┘ └──────┘

┌──────────────────────────────────────────────────┐
│  Configuration locale (C:\TCQ\config\)           │
│  - tcq_settings.json (callsign, locator, ...)    │
│  - reticulum/config (interfaces RNS)             │
│  - sstv_templates/*.stt (overlays SSTV)          │
│  - bbs/messages.db (base BBS SQLite)             │
└──────────────────────────────────────────────────┘
```

---

## 🔧 Prérequis

| Élément | Spécification |
|---|---|
| **OS** | Windows 10 (build 19041+) ou Windows 11 |
| **Architecture** | x86_64 ou ARM64 (binaires natifs) |
| **RAM** | 4 Go minimum, 8 Go recommandé |
| **Disque** | ~500 Mo pour TCQ + dépendances |
| **Python** | **Non requis** (binaire PyInstaller autonome) |
| **Direwolf** | Téléchargé et configuré automatiquement par TCQ |
| **VARA** | À installer séparément depuis [le site éditeur](https://rosmodem.wordpress.com/) |
| **Reticulum** | Configuration `.reticulum/config` créée automatiquement |

### Matériel radio

| Usage | Matériel recommandé |
|---|---|
| **Modes HF numériques** | Transceiver HF + interface CAT/audio (SignaLink, RIGblaster, FT-991A intégré, IC-7300) |
| **Packet VHF/UHF** | TNC matériel ou carte son + transceiver FM |
| **MeshCore LoRa** | Module LoRa USB/série compatible MeshCore |
| **SSTV** | Entrée audio reliée à la sortie casque du transceiver |
| **GPS** *(optionnel)* | Récepteur GPS NMEA sur port COM |
| **SDR** *(optionnel)* | RTL-SDR pour réception 121.5 MHz / écoute panoramique |

<p align="center">
  <img src="images/TCQ_hardware_setup.jpg" alt="Configuration matérielle ADRASEC" width="700"/>
  <br><i>Exemple de configuration de station ADRASEC avec TCQ</i>
</p>

---

## 🛠️ Dépannage

### TCQ ne démarre pas

- Vérifiez que vous avez bien décompressé l'archive dans `C:\` (pas sur un autre lecteur)
- Lancez `TCQ.exe` en mode administrateur la première fois
- Vérifiez les journaux dans `C:\TCQ\logs\`

### Direwolf ne démarre pas en mode Packet

- Vérifiez qu'aucune autre instance de Direwolf ne tourne
- Vérifiez la sélection de la carte son dans **Paramètres → Audio**
- Le pare-feu Windows peut bloquer l'AGWPE — autorisez Direwolf

### VARA n'est pas détecté

- VARA HF / VARA FM doit être installé **séparément** depuis le site éditeur
- Indiquez le chemin de `VARA.exe` dans **Paramètres → VARA**
- Vérifiez que le port TCP local (8300 par défaut) n'est pas utilisé

### Décodage SSTV de mauvaise qualité

- Niveau audio d'entrée recommandé : -3 dB à -6 dB en crête
- Utilisez le bouton **Resync** pour re-décoder le WAV de debug
- Vérifiez que le mode sélectionné correspond bien au mode émis (Scottie S1 ≠ S2)
- Écartez tout filtre numérique du transceiver qui découperait au-dessus de 2400 Hz

### DPI scaling sur Windows 11

Si l'interface apparaît floue ou trop petite : Clic droit sur `TCQ.exe` → **Propriétés → Compatibilité → Modifier les paramètres de PPP élevés** → cocher **Remplacer le comportement de mise à l'échelle PPP élevés** → **Application**.

### Reticulum/LXMF ne reçoit pas les messages

- Vérifiez la configuration `.reticulum/config` (interfaces actives)
- Lancez `rnstatus -v` en parallèle pour diagnostiquer les chemins
- Vérifiez que votre identité LXMF a été annoncée (`Announce` dans le menu Reticulum)

> 📘 Pour les configurations avancées et la mise en œuvre opérationnelle, consultez [**NT100 — Pour une Communication Résiliente**](TCQ%20Documentations/NT100%20TCQ%20-%20Pour%20une%20Communication%20R%C3%A9siliente.pdf).

---

## 🤝 Communauté

TCQ est un **projet open développé pour la communauté ADRASEC**, proposé librement aux opérateurs ADRASEC départementales et à la FNRASEC.

Toute contribution, retour d'expérience ou proposition d'amélioration est bienvenue via les [**Issues du dépôt GitHub**](https://github.com/f1gbd/F1GBD/issues).

---

## 🏆 Crédits

TCQ s'appuie sur l'excellent travail de la communauté open source :

| Composant | Auteur(s) | Licence |
|---|---|---|
| **Reticulum / LXMF** | Mark Qvist | Reticulum License |
| **Direwolf** | John Langner WB2OSZ | GPL |
| **VARA** | José Alberto Nieto Ros (EA5HVK) | Propriétaire (gratuit en bas débit) |
| **slowrx** (SSTV) | Oona Räisänen | MIT |
| **MeshCore** | Projet open source | GPL |

Tous les modules intégrés respectent les licences de leurs auteurs originaux.

---

<div align="center">

### 📡 Auteur

**Jean-Louis (F1GBD / F4JHW)**
*ADRASEC 77 — FNRASEC*

**Version v10.11 — 2026-04-28**

---

*Pour toute question, contactez votre référent ADRASEC départemental.*

📡 **TCQ** — *La plateforme de communications radio multi-modes au service de la sécurité civile*

</div>
