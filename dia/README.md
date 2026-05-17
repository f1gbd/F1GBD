<div align="center">

<img src="images/d-ia_logo.jpg" alt="d-IA" width="300">

# d-IA

### Dialogue autonome entre deux IA — pour la recherche et l'exercice ADRASEC

*Conversation scientifique guidée — Investigateur & Analyste — Ollama local & cloud — Mémoire glissante — Détection de dérive linguistique — Synthèse vocale SAPI5 deux voix — Synchronisation dialogue/voix — Export JSON / Markdown / RTF — Thèmes secondaires guidés — Configuration persistante*

[![Version](https://img.shields.io/badge/version-dia--v1.0.0-blue)](https://github.com/f1gbd/F1GBD/releases/tag/dia-v1.0.0)
[![Plateforme](https://img.shields.io/badge/plateforme-Windows%2010%2F11-lightgrey.svg)]()
[![Licence](https://img.shields.io/badge/usage-ADRASEC%2FFNRASEC-green.svg)]()
[![Local / Cloud](https://img.shields.io/badge/Ollama-local%20%2F%20cloud-brightgreen.svg)]()
[![Accessibilité](https://img.shields.io/badge/accessibilit%C3%A9-voix%20SAPI5-purple.svg)]()

### 📥 [**Télécharger la dernière version**](https://github.com/f1gbd/F1GBD/releases/download/dia-v1.0.0/d-IA.7z)

</div>

---

## 🎯 Qu'est-ce que d-IA ?

**d-IA** est une application qui fait **dialoguer en autonomie deux modèles de langage** sur un sujet scientifique défini par l'utilisateur. L'un joue le rôle d'**Investigateur** (pose des questions, creuse, doute), l'autre celui d'**Analyste** (apporte des réponses étayées, ouvre de nouvelles pistes). Le résultat est une conversation **évolutive avec un fil conducteur**, parfaitement adaptée à :

- 🔬 **L'exploration pédagogique** d'un sujet technique (propagation HF, théorie de l'information, communications quantiques…)
- 🧠 **L'entraînement à la réflexion structurée** : voir deux IA dérouler un raisonnement contradictoire et complémentaire
- 📝 **La génération de matière première documentaire** pour exercices ADRASEC, RETEX, formations
- 🎙️ **Une expérience d'écoute** quand la synthèse vocale est activée : on entend deux voix distinctes débattre

Tout tourne **localement** par défaut (modèles Ollama auto-hébergés), avec une option **cloud** (gpt-oss:120b, deepseek-v3.1:671b, kimi-k2…) si on souhaite faire dialoguer des modèles XL hébergés.

---

## ⭐ Fonctionnalités principales

| Icône | Fonctionnalité | Description |
|:---:|---|---|
| 🤖 | **Deux LLM aux rôles asymétriques** | LLM1 (Investigateur) doit terminer chaque tour par une question ouverte. LLM2 (Analyste) doit introduire un élément nouveau dans chaque réponse (analogie, contre-exemple, chiffre…). Ces contraintes empêchent les boucles stériles et donnent un vrai rythme de dialogue. |
| 🌐 | **Ollama local OU cloud, par LLM** | Chaque IA peut être configurée indépendamment : LLM1 sur un serveur local LAN (`http://192.168.x.x:11434`), LLM2 sur Ollama Cloud (`https://ollama.com` avec clé `OLLAMA_API_KEY`). Mixage possible : un petit modèle local pose les questions, un gros modèle cloud répond. |
| 📚 | **Thèmes secondaires guidés** | L'utilisateur définit un sujet principal (fil rouge) + une liste de thèmes secondaires. Le moteur fait défiler les thèmes tous les N tours, garantissant une progression de la conversation sans dérive thématique. |
| 🧠 | **Mémoire à fenêtre glissante** | Les N derniers échanges sont passés intégralement aux LLM ; les plus anciens sont condensés en un **résumé glissant** régénéré périodiquement. Évite l'explosion du contexte au-delà de 20-30 tours. |
| 🔍 | **Détection de dérive linguistique** | Si un modèle bascule en chinois/cyrillique/arabe en cours de génération (bug fréquent de Qwen 2.5 sur les conversations longues), d-IA détecte automatiquement (ratio > 5% caractères non-latins), régénère avec température réduite, et tronque si nécessaire avec un avertissement. |
| 🎤 | **Synthèse vocale SAPI5 deux voix** | Activation optionnelle (case à cocher dans Paramètres IA). Chaque IA a sa voix configurable parmi celles installées sur Windows. **Le dialogue se synchronise sur la voix** : la génération du tour suivant se fait en parallèle pendant que le TTS parle, mais l'affichage n'arrive qu'à la fin de la lecture précédente. Pas de bourrage, vrai rythme conversationnel à deux voix. |
| ✨ | **Déblocage des voix OneCore Windows 10/11** | Bouton intégré qui rend accessibles à SAPI5 les voix modernes Windows (Henri Natural, Julie, Paul, Caroline, Claude, Hortense…) en copiant les clés de registre `Speech_OneCore` vers `Speech`. Opération réversible via un bouton « Restaurer ». |
| ✏️ | **Configuration persistante** | Tous les paramètres (hosts, modèles, clés API offusquées en base64, sujet, thèmes, voix, températures…) sont sauvés dans `d-ia_setup.json` à côté de l'exécutable, et rechargés au démarrage. |
| 📤 | **Export multi-format** | Bouton « Exporter la conversation » avec menu déroulant : **JSON** (données structurées pour retraitement / RETEX), **Markdown** (fichier `.md` lisible avec titres et italiques, parfait pour Notion/Obsidian/GitHub), **RTF** (couleurs LLM1 bleu et LLM2 violet, ouvre directement dans Word / LibreOffice Writer). |
| 🎨 | **Interface bicolore** | Zone de conversation sur fond bleu clair, avec messages **bleus pour LLM1** et **mauves pour LLM2** (rappel du logo). Lisibilité optimale, distinction immédiate des locuteurs. |
| ⚙️ | **Fenêtre Paramètres IA modale** | Trois onglets : configuration **IA 1 - Investigateur** (host local + cloud + clé API + modèle), configuration **IA 2 - Analyste** (idem), et **Synthèse vocale** (activation TTS, choix des voix, débit, déblocage OneCore). |

---

## 📋 Pré-requis

### Logiciels

- **Windows 10 ou 11** (le TTS SAPI5 et le binaire pyttsx3 sont Windows-only)
- **Ollama** installé localement : <https://ollama.com/download>
  - ou compte **Ollama Cloud** avec clé API : <https://ollama.com/settings/keys>
- **Au moins deux modèles** téléchargés via Ollama :

  ```powershell
  ollama pull mistral:7b
  ollama pull llama3.2:3b
  ```

  Recommandés pour le français : `mistral:7b`, `mistral-nemo:12b`, `llama3.1:8b`, `llama3.2:3b`, `gemma2:9b`. Éviter `qwen2.5` qui dérive vers le chinois sur les conversations longues (d-IA détecte et corrige mais c'est sous-optimal).

### Matériel

| Configuration | VRAM nécessaire |
|---|---|
| 2 × modèles 3B (llama3.2:3b + gemma3:1b) | ~4 Go |
| 1 × 3B + 1 × 7B (llama3.2:3b + mistral:7b) | ~10 Go |
| 2 × 7B | ~16 Go |
| 1 × 7B + 1 × 12B (mistral:7b + mistral-nemo:12b) | ~20 Go |
| Mode éco VRAM (déchargement entre tours) | Pas de minimum (CPU OK) |

Sans GPU, ça marche aussi mais chaque tour prend 30-60 s au lieu de 5-10 s.

---

## 🚀 Installation

### Option 1 — Binaire compilé (recommandé)

1. Télécharger [`d-IA.7z`](https://github.com/f1gbd/F1GBD/releases/latest) depuis la page Releases
2. Décompresser dans un dossier de votre choix
3. Lancer `d-IA.exe`
4. Cliquer sur **⚙ Paramètres IA…** pour configurer les deux IA
5. Cliquer sur **▶ Démarrer**

### Option 2 — Depuis les sources Python

```powershell
# Cloner ou télécharger le repo
git clone https://github.com/f1gbd/F1GBD.git
cd F1GBD\dia

# Installer les dépendances
pip install ollama pillow pyttsx3 pywin32

# Lancer
python d-IA.py
```

---

## 📖 Utilisation

### Premier démarrage

1. **Ouvrir Paramètres IA** (bouton en haut à droite) :
   - **Onglet IA 1** : laisser `http://localhost:11434` si Ollama tourne localement. Cliquer « Tester la connexion », choisir un modèle (ex: `mistral:7b`)
   - **Onglet IA 2** : idem avec un autre modèle (ex: `llama3.2:3b`)
   - **Onglet Synthèse vocale** : *(optionnel)* cocher la case « Activer la lecture vocale », choisir une voix pour chaque IA, tester
2. **Fermer** la fenêtre Paramètres
3. **Saisir un sujet principal** dans la colonne gauche (ex: « La propagation des ondes radio dans l'ionosphère »)
4. **Saisir une liste de thèmes secondaires** (un par ligne)
5. **Cliquer ▶ Démarrer**

### Pendant la conversation

- **Pause / Reprendre** : suspendre temporairement le dialogue
- **Arrêter** : termine la conversation (et interrompt immédiatement le TTS en cours)
- **Exporter** : choix du format (JSON / Markdown / RTF) via le menu déroulant
- La **colonne droite** affiche le tour courant, le thème actif, et le résumé glissant régénéré périodiquement

### Configuration Ollama Cloud

1. Créer un compte sur <https://ollama.com> et générer une clé API
2. Dans **Paramètres IA → Onglet IA 1** (ou 2), cocher **« Utiliser Ollama Cloud »**
3. Coller la clé dans le champ « API key »
4. Cliquer « Tester la connexion » → la liste des modèles cloud apparaît avec ☁ devant chaque nom (gpt-oss:120b, deepseek-v3.1:671b…)

> ⚠️ **Confidentialité** : en mode cloud, vos prompts sont envoyés à ollama.com. À ne pas utiliser pour des données opérationnelles confidentielles.

---

## 🎙️ Synthèse vocale et déblocage des voix OneCore

Par défaut, **pyttsx3/SAPI5 ne voit que les voix « Desktop »** de Windows (typiquement Hortense Desktop en FR-FR + Zira Desktop en EN-US). Les voix modernes Windows 10/11 (Henri Natural, Julie, Paul, Caroline, Claude…) sont stockées sous une autre branche de registre (`Speech_OneCore`) et sont invisibles aux applications SAPI5 standards.

**d-IA fournit un déblocage en un clic** :

1. Aller dans **Paramètres IA → Onglet Synthèse vocale**
2. La section « **Voix modernes Windows 10/11 (OneCore)** » détecte automatiquement les voix disponibles non débloquées
3. Cliquer sur **✨ Activer les voix OneCore (admin)**
4. Accepter le prompt UAC : un script PowerShell copie les clés de registre `Speech_OneCore\Voices\Tokens` vers `Speech\Voices\Tokens`
5. Redémarrer d-IA : les nouvelles voix apparaissent dans les combobox

**L'opération est réversible** : bouton « Restaurer » qui retire uniquement les copies, sans toucher aux voix Desktop d'origine.

---

## 🔧 Compilation depuis les sources

### Build PyInstaller

```powershell
# Installer les outils de build
pip install pyinstaller pillow pyttsx3 pywin32 ollama

# Compiler avec le fichier .spec fourni
pyinstaller --clean d-IA.spec
```

Sortie : `dist/d-IA/d-IA.exe` + dossier `_internal/` + ressources.

### Création de l'archive .7z

```powershell
# 7-Zip doit être installé (https://www.7-zip.org)
cd dist
& "C:\Program Files\7-Zip\7z.exe" a d-IA.7z d-IA/
```

### Publication d'une release GitHub

```powershell
# Pré-requis : gh CLI authentifié (gh auth login)
.\Publish-dIARelease.ps1 -Version "1.0.0"
```

Le script s'occupe automatiquement de :
- Vérifier les pré-requis (gh CLI, authentification, archive présente)
- Calculer le SHA-256 de l'archive
- Créer le tag `dia-v1.0.0` avec convention de préfixe monorepo
- Uploader l'archive
- Générer une description Markdown avec lien de téléchargement et empreinte d'intégrité
- Gérer le statut « Latest » du dépôt (préserve les autres projets du monorepo par défaut)

---

## 📂 Structure du projet

```
dia/
├── d-IA.py                       # Application principale
├── d-IA.spec                     # Recette PyInstaller
├── Publish-dIARelease.ps1        # Script de publication GitHub Release
├── README.md                     # Ce fichier
├── images/
│   ├── d-ia_logo.jpg             # Logo (utilisé dans la GUI et l'À propos)
│   └── d-ia_logo.ico             # Icône Windows (barre des tâches, exe)
└── d-ia_setup.json               # (généré au premier lancement)
```

---

## ❓ FAQ

**Le test de voix fonctionne mais le dialogue ne lit rien.**
Vérifié et corrigé en v1.0 : refonte du moteur TTS sur SAPI direct via `win32com` (au lieu de pyttsx3 qui maintenait un singleton incompatible multi-thread). Si vous voyez encore ce comportement, vérifiez que `pywin32` est bien installé (`pip install pywin32`) et regardez la console pour des erreurs `[TTSEngine]`.

**Erreur Ollama « failed to allocate compute pp buffers ».**
Votre VRAM est saturée. Solutions : (1) cocher « Mode éco VRAM (décharge entre tours) » dans les Paramètres avancés, (2) réduire `num_ctx` à 2048 ou 4096, (3) utiliser des modèles plus petits, (4) basculer un des deux LLM sur Ollama Cloud.

**Les conversations en chinois apparaissent en plein milieu d'une réponse.**
C'est Qwen 2.5 qui dérive vers sa langue dominante d'entraînement. d-IA détecte et régénère automatiquement. Pour éviter le problème dès le départ, préférez `mistral:7b`, `llama3.x`, `mistral-nemo` ou `gemma2:9b` qui sont stables en français sur 20+ tours.

**Les voix OneCore n'apparaissent pas après le déblocage.**
Il faut **redémarrer d-IA** après l'activation (la liste est lue au lancement de l'app, pas dynamiquement). Si elles n'apparaissent toujours pas, vérifier dans regedit que `HKLM\SOFTWARE\Microsoft\Speech\Voices\Tokens` contient bien les nouvelles voix.

**Comment voir si une conversation est intéressante pendant qu'elle tourne ?**
La colonne droite « Resume glissant » se met à jour automatiquement toutes les N interventions (paramètre « Fenêtre mémoire »). Le résumé est aussi inclus dans l'export final.

**Peut-on faire dialoguer trois IA au lieu de deux ?**
Pas dans la v1.0. La logique des rôles asymétriques (Investigateur / Analyste) est conçue pour deux. Une v2 pourrait introduire un troisième rôle « Modérateur » qui intervient tous les K tours pour synthétiser ou recadrer.

---

## 🤝 Communauté

d-IA est un **projet open développé pour la communauté ADRASEC**, mis à disposition librement aux opérateurs ADRASEC départementales, à la FNRASEC, et plus largement à toute personne intéressée par les dialogues autonomes entre LLM.

Toute contribution, retour d'expérience ou proposition d'amélioration est bienvenue via les *Issues* du dépôt GitHub.

**Idées d'usage soumises** :
- Préparation aux examens radioamateurs (un LLM joue le candidat, l'autre l'examinateur)
- Génération de RETEX d'exercice fictifs pour la doc ADRASEC
- Exploration pédagogique de la propagation HF, NVIS, satellite, communications quantiques…
- Comparaison qualitative de deux modèles sur le même sujet
- Génération de matière première pour podcasts radioamateurs

---

<div align="center">

### 📡 Auteur

**Jean-Louis (F1GBD)**
*ADRASEC 77 — FNRASEC*

**Version 1.0 — 2026**

---

*Pour toute question, contactez votre référent ADRASEC départemental.*

🤖 **d-IA** — *Deux IA, un dialogue, une conversation qui ne s'arrête jamais*

</div>
