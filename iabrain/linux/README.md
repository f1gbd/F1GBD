<div align="center">

<img src="../IAbrain_logo.png" alt="IAbrain" width="200">

# IAbrain — Linux Edition

### L'assistant IA local pour les opérateurs ADRASEC — version Linux

*LLM local Ollama — Base RAG ADRASEC + base perso — Macros et actions natives — Cartographie interactive — Mémoire conversationnelle — Profil opérateur — Variables de session — Pipeline SATER complet — SITREP PDF auto-rempli — Plugins externes — Auto-exécution de macros par le LLM — 100 % local et confidentiel*

[![Version](https://img.shields.io/badge/version-iabrain--linux--v1.42.1-blue)](https://github.com/f1gbd/F1GBD/releases/tag/iabrain-linux-v1.42.1)
[![Plateforme](https://img.shields.io/badge/plateforme-Linux%20x86__64-orange.svg)]()
[![Distros](https://img.shields.io/badge/cible-Ubuntu%2024.04%2B%20%7C%20Debian%2012%2B-success.svg)]()
[![Licence](https://img.shields.io/badge/usage-ADRASEC%2FFNRASEC-green.svg)]()
[![100% local](https://img.shields.io/badge/100%25-hors--ligne-brightgreen.svg)]()

### 🐧 [**Télécharger la dernière version Linux**](https://github.com/f1gbd/F1GBD/releases/download/iabrain-linux-v1.42.1/IAbrain-1.42.1-linux-x86_64.tar.gz)

*Version Windows disponible dans le [dossier parent](https://github.com/f1gbd/F1GBD/tree/master/iabrain)*

</div>

---

## 🆕 Quoi de neuf en v1.42.1

> **Correctif important du module RAG** — Cette version corrige un bug bloquant de la v1.42 initiale qui empêchait l'initialisation du moteur RAG sous Linux avec le message *« cannot load module more than once per process »*. La cause : NumPy 2.x embarqué dans le binaire PyInstaller refuse son chargement multiple (mécanisme de sécurité introduit dans NumPy 2.0). La correction passe par un downgrade vers NumPy 1.26.4, qui n'a pas cette restriction.
>
> **Ajout des extracteurs PDF / DOCX** — La v1.42.1 embarque désormais explicitement `pypdf` et `python-docx`, indispensables pour l'indexation des PDF et DOCX de la base de connaissances ADRASEC. Sans ces modules, la création du RAG échouait silencieusement sur les fichiers non-texte.
>
> **Action recommandée** : si vous avez installé la v1.42 et rencontré l'erreur RAG, désinstallez-la (`./install.sh --uninstall`) avant d'installer la v1.42.1.
>
> **Pas de changement sur les autres fonctionnalités** — conversation LLM Ollama, macros, actions natives, pipeline SATER, SITREP PDF, mémoire conversationnelle, profil opérateur, plugins externes, auto-exécution de macros : tout reste identique à la v1.42.

---

## 📋 Historique des versions Linux

| Version | Date | Changements |
|---|---|---|
| **v1.42.1** | Mai 2026 | 🛠 Correctif RAG : downgrade NumPy 2.x → 1.26.4, ajout pypdf + python-docx |
| v1.42 | Mai 2026 | 🐧 Première édition Linux d'IAbrain (sous forme de binaire PyInstaller autonome) |

---

## 🎯 À propos de la version Linux

Cette version Linux apporte le support complet d'Ubuntu et Debian récents, sous forme de **binaire PyInstaller autonome** (~52 Mo compressé / 134 Mo extrait). Aucune dépendance Python à installer — Python 3.12, NumPy 1.26, requests, Pillow, staticmap, pypdf et python-docx sont tous embarqués dans le binaire.

**Fonctionnalités** : 100 % des fonctionnalités principales de la version Windows sont conservées — conversation LLM Ollama, RAG ADRASEC + base perso, macros et actions natives, pipeline SATER, SITREP PDF auto-rempli, mémoire conversationnelle, profil opérateur, plugins externes, auto-exécution de macros, cartographie interactive de la base.

**Différence unique** : l'interface vocale (STT Vosk + TTS) est désactivée dans cette version, car elle s'appuie sur des composants Windows (SAPI5). Un backend Piper TTS Linux est prévu pour une version ultérieure. Les boutons 🎤 🔊 🔇 restent visibles mais inactifs.

**Migration depuis Windows** : si vous copiez votre `IAbrain.json` Windows sur Linux, les chemins de type `C:/QITdevsrc/IAbrain` sont **automatiquement remplacés** par leurs équivalents Linux (`~/IAbrain/...`) au premier démarrage. Aucune action manuelle requise.

---

## 🎯 À qui s'adresse cette version ?

La version **Linux** d'IAbrain est destinée aux opérateurs ADRASEC qui :

- 🐧 Utilisent **Linux** comme système principal sur leur poste opérationnel (Ubuntu 24.04+, Debian 12+, Linux Mint 22+)
- 🔋 Disposent d'un **laptop léger** ou d'un mini-PC pour leurs sorties terrain
- 🔒 Privilégient **l'indépendance vis-à-vis de Microsoft** pour leurs documents sensibles ADRASEC
- 🎓 Préparent des **VM Linux** de formation pour leur section départementale
- 🏢 Travaillent sur des **postes mutualisés** des cellules de coordination FNRASEC sous Linux

**Toutes les fonctionnalités principales** de la version Windows sont disponibles sous Linux, à l'exception de l'interface vocale qui reste sur la roadmap.

---

## 📦 Ce que contient l'archive

```
IAbrain-1.42.1-linux-x86_64.tar.gz       (~52 Mo compressé / ~134 Mo extrait)
└── IAbrain-1.42.1-linux-x86_64/
    ├── bin/                    Binaire PyInstaller autonome
    │   ├── IAbrain             Exécutable ELF 64-bit (7.6 Mo, stripped)
    │   └── _internal/          Python 3.12 + NumPy 1.26 + requests + Pillow + staticmap + pypdf + python-docx + Tkinter
    ├── IAbrain.png             Icône 1024×1024
    ├── install.sh              Script d'installation (utilisateur / système / uninstall)
    ├── iabrain                 Lanceur direct (sans installation)
    └── README.md               Documentation détaillée
```

**Aucune dépendance Python à installer** — tout est embarqué dans le binaire. Aucune source Python visible — code livré sous forme de binaire compilé.

---

## 🚀 Installation en 3 étapes

### Étape 1 — Télécharger

👉 **[IAbrain-1.42.1-linux-x86_64.tar.gz](https://github.com/f1gbd/F1GBD/releases/download/iabrain-linux-v1.42.1/IAbrain-1.42.1-linux-x86_64.tar.gz)** (~52 Mo)

Ou en ligne de commande :

```bash
wget https://github.com/f1gbd/F1GBD/releases/download/iabrain-linux-v1.42.1/IAbrain-1.42.1-linux-x86_64.tar.gz
wget https://github.com/f1gbd/F1GBD/releases/download/iabrain-linux-v1.42.1/IAbrain-1.42.1-linux-x86_64.tar.gz.sha256
sha256sum -c IAbrain-1.42.1-linux-x86_64.tar.gz.sha256
```

### Étape 2 — Extraire

```bash
tar xzf IAbrain-1.42.1-linux-x86_64.tar.gz
cd IAbrain-1.42.1-linux-x86_64
```

### Étape 3 — Installer (au choix selon votre besoin)

#### Option A — Lancer sans rien installer *(le plus rapide)*

```bash
./iabrain
```

L'application démarre immédiatement. Idéal pour tester ou pour un usage ponctuel depuis une clé USB.

#### Option B — Installation utilisateur *(recommandée)*

```bash
chmod +x install.sh
./install.sh
```

Cela installe IAbrain dans `~/.local/share/IAbrain/`, crée un raccourci dans le **menu Applications** et la commande terminal `iabrain`. **Pas de droits root requis** (sauf si des libs système manquent).

Après cette étape, vous pouvez lancer IAbrain :

- 🖱 Depuis le **menu Applications** → chercher « IAbrain »
- 💻 Depuis un **terminal** → taper `iabrain`
- 📌 En **épinglant l'icône** au dock ou à la barre des tâches

#### Option C — Installation système *(pour postes partagés)*

```bash
chmod +x install.sh
sudo ./install.sh --system
```

Installe dans `/opt/IAbrain/`, raccourci pour tous les utilisateurs de la machine. Utile pour les **postes opérationnels partagés** en cellule de coordination.

#### Désinstallation

```bash
./install.sh --uninstall                  # mode utilisateur
sudo ./install.sh --uninstall --system    # mode système
```

⚠ **La désinstallation conserve vos données utilisateur** (`~/IAbrain/` : config, conversations, RAG, cartes SATER). Pour tout effacer :

```bash
rm -rf ~/IAbrain
```

---

## 🐧 Distributions cibles

| Distribution | Version | Statut |
|---|---|---|
| **Ubuntu** | 24.04 LTS et plus récent | ✅ Cible principale (build et test) |
| **Debian** | 12 (Bookworm) et plus récent | ✅ Compatible (glibc 2.36+) |
| **Linux Mint** | 22.x | ✅ Compatible (basé Ubuntu 24.04) |
| **Raspberry Pi OS** (aarch64) | Pi 4/5 | ❌ Incompatible — binaire x86_64 uniquement |
| **Fedora / openSUSE** | Récentes | ⚠️ Devrait fonctionner mais `install.sh` cible `apt` |

### Dépendances système

Le binaire embarque Python et toutes ses libs, mais a besoin des bibliothèques X11 / Tkinter de base. Normalement déjà présentes sur tout système graphique :

```bash
sudo apt install libxcb-shape0 libxcb-cursor0 libxcb-icccm4 \
                 libxcb-keysyms1 libxkbcommon-x11-0 libfontconfig1 \
                 libtk8.6 libxft2
```

En pratique, sur un poste avec un environnement de bureau (GNOME, KDE, XFCE, Cinnamon, MATE…), tout est déjà installé.

---

## 🤖 Configuration d'Ollama

IAbrain communique avec un serveur **Ollama** (local ou réseau) pour l'inférence LLM. Si vous n'en avez pas encore, l'installation se fait en une commande :

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Puis téléchargez les modèles utilisés par défaut :

```bash
ollama pull mistral-nemo:12b      # modèle principal (12B paramètres)
ollama pull llama3.2:3b           # modèle léger pour requêtes simples (routage automatique)
ollama pull nomic-embed-text      # embeddings pour le RAG (obligatoire)
ollama pull bge-m3                # reranking RAG (recommandé)
```

L'URL du serveur Ollama est configurée par défaut à `http://192.168.1.250:11434` (serveur réseau ADRASEC type). Pour une installation locale, modifiez l'URL dans **Options → Serveur Ollama** au premier lancement vers `http://localhost:11434`.

---

## 🎤 Interface vocale — statut Linux

L'interface vocale STT/TTS, présente dans la version Windows, est **désactivée** dans cette première édition Linux. Les composants Windows utilisés (Vosk via Python, SAPI5 via pywin32, pyttsx3) ne sont pas compatibles tels quels avec l'écosystème audio Linux (PulseAudio/PipeWire/ALSA).

Un backend **Piper TTS** (offline, neuronal, voix française naturelle `fr_FR-siwis-medium`) couplé à **Vosk Linux natif** pour le STT est prévu pour une version ultérieure. Concrètement, dans cette v1.42.1-linux :

- Les boutons 🎤 🔊 🔇 sous le bouton **Envoyer** restent visibles mais sans effet (cohérence visuelle avec la version Windows)
- Les raccourcis clavier `F2` (écoute) et `F3` (interrompre TTS) sont sans effet
- La section « 🎤 Voix » des Options reste accessible mais les paramètres ne sont pas pris en compte
- Les flags `voice.stt_enabled` et `voice.tts_enabled` sont automatiquement forcés à `false` au démarrage si la config Windows les avait à `true`

**Toutes les autres fonctionnalités** (LLM, RAG, macros, SATER, SITREP, mémoire, profil…) fonctionnent strictement à l'identique de la version Windows.

---

## 🔍 Vérification d'intégrité

Le SHA-256 de l'archive est publié sur la page de release GitHub :

```bash
sha256sum IAbrain-1.42.1-linux-x86_64.tar.gz
```

Comparez avec la valeur publiée sur :
👉 https://github.com/f1gbd/F1GBD/releases/tag/iabrain-linux-v1.42.1

Ou via le fichier `.sha256` joint à la release :

```bash
wget https://github.com/f1gbd/F1GBD/releases/download/iabrain-linux-v1.42.1/IAbrain-1.42.1-linux-x86_64.tar.gz.sha256
sha256sum -c IAbrain-1.42.1-linux-x86_64.tar.gz.sha256
```

---

## 🎨 Captures d'écran

L'interface Linux est **strictement identique** à la version Windows : même thème clair/sombre, mêmes boutons, mêmes panneaux, même rendu Markdown des réponses.

<div align="center">

<img src="../docs/images/main_screen.png" alt="IAbrain sous Linux" width="900">

*IAbrain v1.42.1 tournant nativement sous Linux — interface identique à Windows*

</div>

---

## ⭐ Fonctionnalités

Identiques à la version Windows (à l'exception de l'interface vocale) :

| Icône | Fonctionnalité |
|:---:|---|
| 💬 | **Conversation en français naturel** avec routage automatique entre modèles |
| 📚 | **Base de connaissances ADRASEC** indexée (RAG hybride embedding + lexical) |
| 📂 | **Base RAG personnelle** isolée, jamais écrasée par les mises à jour OTA |
| 🌐 | **Cartographie interactive de la base RAG** 100% hors-ligne (HTML autonome) |
| 📢 | **Corrections manuelles** indexées dans la base perso et appliquées en priorité |
| 🆕 | **Macros utilisateur** (8 boutons configurables) avec méta-langage `{{lastfile}}`, `{{date}}`, `{{call}}`… |
| ⚙️ | **5 actions natives** : CSV→MD, extraction d'indicatifs/fréquences, anonymisation, statistiques fichiers |
| 📋 | **SITREP PDF auto-rempli** : Ollama remplit le formulaire AcroForm `SITREP_ADRASEC.pdf` automatiquement |
| 🎯 | **Pipeline SATER complet** : carte OSM PNG centrée sur balise ELT avec cercle CEP 95 et cartouche complet |
| 🔌 | **Plugins externes** : déposez vos `IAbrain_actions_*.py` dans `~/IAbrain/plugins/` pour étendre IAbrain |
| 🚀 | **Auto-exécution de macros par le LLM** via bloc `###IABRAIN_RUN_MACRO###` |
| 🔖 | **Variables de session** `{LAT}`, `{LON}`, `{RAYON_M}`… persistantes entre redémarrages |
| 📤 | **Import/Export de macros** au format `.iabmacro` partageable entre opérateurs |
| 📝 | **Rendu Markdown complet** : titres, tableaux, cases à cocher, code, liens cliquables |
| ☁ | **Connectivité Ollama Cloud** pour accéder aux modèles XL (gpt-oss:120b, deepseek-v3.1:671b…) |
| 🧠 | **Mémoire conversationnelle persistante** : « Souviens-toi » indexe la conversation dans la base perso |
| 👤 | **Profil opérateur déclaratif** : indicatif, département, niveau d'expertise, spécialités |
| ⚡ | **Routage automatique** entre modèle léger (questions simples) et modèle puissant (analyses) |
| 🎯 | **Reranking RAG** via bge-m3 pour la pertinence maximale des sources citées |
| 🔄 | **Mise à jour OTA** depuis GitHub, base perso jamais écrasée |
| 🔒 | **100 % local et confidentiel** (sauf mode Ollama Cloud explicitement activé) |

### Différences avec la version Windows

| Point | Windows | Linux |
|---|---|---|
| Dossier utilisateur | `%APPDATA%\IAbrain\` ou à côté de l'exe | `~/IAbrain/` |
| Ouverture de fichier / dossier | `os.startfile()` (Explorer) | `xdg-open` (gestionnaire du DE) |
| Interface vocale STT/TTS | ✅ Disponible (Vosk + SAPI5/pyttsx3) | ❌ Désactivée — Piper TTS prévu |
| Format de distribution | Binaire PyInstaller `.7z` (~200 Mo) | Binaire PyInstaller `.tar.gz` (~52 Mo) |
| Python embarqué | Oui (PyInstaller) | Oui (PyInstaller) |
| DPI awareness | Géré pour Windows 10/11 (ShCore) | Géré nativement par X11 / Wayland |
| Console au démarrage | Masquée automatiquement (ctypes) | Lancé via `.desktop`, pas de console |
| Modèle Vosk français | Téléchargeable `./models/vosk-fr/` | Non utilisé (STT désactivé) |
| Migration de config | N/A | Automatique : `C:/...` → `~/IAbrain/...` |

---

## 🐛 Dépannage

### `error while loading shared libraries: libXxx.so`

Une bibliothèque X11 manque. Installez les dépendances listées dans la section *Distributions cibles*.

### `cannot open display`

Vous êtes connecté en SSH sans display X11. IAbrain est une application graphique — il faut soit un environnement de bureau local, soit un SSH avec X11 forwarding (`ssh -X user@host`).

### Le binaire ne s'exécute pas (`Permission denied`)

```bash
chmod +x bin/IAbrain install.sh iabrain
```

### L'application démarre mais affiche « Erreur serveur Ollama »

Le serveur Ollama configuré n'est pas accessible. Ouvrez **Options → Serveur Ollama** et indiquez l'URL correcte (par exemple `http://localhost:11434` si Ollama tourne sur la même machine).

### Le menu Applications ne montre pas IAbrain après installation

Forcez la mise à jour des caches :

```bash
update-desktop-database ~/.local/share/applications
gtk-update-icon-cache -f -t ~/.local/share/icons/hicolor
```

Puis déconnectez et reconnectez votre session.

### `command not found: iabrain`

Le dossier `~/.local/bin/` n'est pas dans votre `PATH`. Ajoutez à `~/.bashrc` :

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Puis `source ~/.bashrc` ou ouvrez un nouveau terminal.

### Mes chemins Windows dans `IAbrain.json` ne sont pas migrés

La migration automatique des chemins `C:/...` → `~/IAbrain/...` se fait au **chargement de la config**, mais n'est persistée sur disque qu'à la prochaine sauvegarde (fermeture propre de l'app, modification d'un paramètre dans Options, etc.). Pour forcer une sauvegarde, ouvrez **Options → Valider** sans rien changer.

### Les boutons 🎤 🔊 🔇 sont visibles mais sans effet

C'est le comportement attendu sous Linux dans cette version (voir section *Interface vocale*). Le support vocal Linux est sur la roadmap.

### « Impossible de charger le module RAG : cannot load module more than once per process »

C'est un bug spécifique à la v1.42 initiale, **corrigé en v1.42.1**. Si vous voyez cette erreur, vous utilisez l'ancienne version. Téléchargez la v1.42.1 ou plus récente :

```bash
~/.local/share/IAbrain/install.sh --uninstall    # désinstaller v1.42
# puis installer v1.42.1 :
tar xzf IAbrain-1.42.1-linux-x86_64.tar.gz
cd IAbrain-1.42.1-linux-x86_64 && ./install.sh
```

Vos données utilisateur (`~/IAbrain/`) sont préservées entre les versions.

### Le RAG indexe les .txt mais pas les .pdf ou .docx

Vous utilisez une version antérieure à 1.42.1. La v1.42.1 embarque les modules `pypdf` et `python-docx` nécessaires à l'extraction de texte depuis les PDF et DOCX. Mettez à jour vers la dernière version.

---

## 📚 Documentation associée

- 🪟 **[Version Windows](https://github.com/f1gbd/F1GBD/tree/master/iabrain)** — README et téléchargement Windows
- 📡 **[TCQ — TransCommunication Quantique](https://github.com/f1gbd/F1GBD/tree/master/tcq)** — Plateforme de communication multi-mode (couplée à IAbrain via SITREP/VARA)
- 📄 **[PDFteleporter](https://github.com/f1gbd/F1GBD/tree/master/pdfteleporter)** — Téléportation radio de documents PDF (couplée à IAbrain via Winlink)
- 🛰️ **[SATER SIM3D](https://github.com/f1gbd/F1GBD/tree/master/satersim3d)** — Simulateur ARMA 3 de recherche de balises ELT

---

## 🤝 Communauté

IAbrain est un **projet open développé pour la communauté ADRASEC**, proposé librement aux opérateurs ADRASEC départementales et à la FNRASEC.

L'application s'inscrit dans l'écosystème **TCQ / IAbrain / PDFteleporter / SATER SIM** dans la chaîne d'outils de communications d'urgence en sécurité civile.

La version Linux est particulièrement adaptée :

- 💻 Aux **opérateurs migrés sous Linux** pour leur poste personnel
- 🎓 Aux **VM de formation** distribuées en section
- 🏢 Aux **postes mutualisés** sous Linux des cellules de coordination FNRASEC
- 🔬 Aux **environnements isolés** où Windows ne peut pas être déployé

Toute contribution, retour d'expérience et proposition d'amélioration sont bienvenus via les *Issues* du dépôt GitHub.

---

<div align="center">

### 📡 Auteur

**Jean-Louis Naudin (F1GBD / F4JHW)**
*ADRASEC 77 — FNRASEC*

**Version 1.42.1 Linux — Mai 2026**

---

*Pour toute question, contactez votre référent ADRASEC départemental.*

🐧 **IAbrain Linux** — *L'assistant IA local au service de la sécurité civile*

</div>
