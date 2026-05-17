<div align="center">

<img src="images/d-ia_logo.jpg" alt="d-IA" width="300">

# d-IA

### Dialogue autonome entre deux IA — pour la recherche et l'exercice ADRASEC

*Conversation scientifique guidée — Investigateur & Analyste — Mode ADRASEC enrichi (modérateur RAG) — Ollama local & cloud — Mémoire glissante — Détection de dérive linguistique — Synthèse vocale SAPI5 deux voix — Synchronisation dialogue/voix — Export JSON / Markdown / RTF — Thèmes secondaires guidés — Configuration persistante*

[![Version](https://img.shields.io/badge/version-dia--v1.1.0-blue)](https://github.com/f1gbd/F1GBD/releases/tag/dia-v1.1.0)
[![Plateforme](https://img.shields.io/badge/plateforme-Windows%2010%2F11-lightgrey.svg)]()
[![Licence](https://img.shields.io/badge/usage-ADRASEC%2FFNRASEC-green.svg)]()
[![Local / Cloud](https://img.shields.io/badge/Ollama-local%20%2F%20cloud-brightgreen.svg)]()
[![Accessibilité](https://img.shields.io/badge/accessibilit%C3%A9-voix%20SAPI5-purple.svg)]()
[![RAG](https://img.shields.io/badge/mode-ADRASEC%20enrichi-orange.svg)]()

### 📥 [**Télécharger la dernière version (v1.1.0)**](https://github.com/f1gbd/F1GBD/releases/download/dia-v1.1.0/d-IA.7z)

</div>

---
## 🎯 Qu'est-ce que d-IA ?

**d-IA** est une application qui fait **dialoguer en autonomie deux modèles de langage** sur un sujet scientifique défini par l'utilisateur. L'un joue le rôle d'**Investigateur** (pose des questions, creuse, doute), l'autre celui d'**Analyste** (apporte des réponses étayées, ouvre de nouvelles pistes). Avec la v1.1, un **3ᵉ LLM modérateur** observe en arrière-plan et capitalise automatiquement les informations dans une base de fiches structurées.

Le résultat est une conversation **évolutive avec un fil conducteur**, parfaitement adaptée à :

- 🔬 **L'exploration pédagogique** d'un sujet technique (propagation HF, théorie de l'information, communications quantiques…)
- 🧠 **L'entraînement à la réflexion structurée** : voir deux IA dérouler un raisonnement contradictoire et complémentaire
- 📝 **La génération de matière première documentaire** pour exercices ADRASEC, RETEX, formations
- 🗂️ **La constitution d'une base RAG** (mode ADRASEC enrichi v1.1) interrogeable ensuite via IAbrain
- 🎙️ **Une expérience d'écoute** quand la synthèse vocale est activée : on entend deux voix distinctes débattre

Tout tourne **localement** par défaut (modèles Ollama auto-hébergés), avec une option **cloud** (gpt-oss:120b, deepseek-v3.1:671b, kimi-k2…) si on souhaite faire dialoguer ou modérer avec des modèles XL hébergés.

---

## ⭐ Fonctionnalités principales

| Icône | Fonctionnalité | Description |
|:---:|---|---|
| 🤖 | **Deux LLM aux rôles asymétriques** | LLM1 (Investigateur) doit terminer chaque tour par une question ouverte. LLM2 (Analyste) doit introduire un élément nouveau dans chaque réponse (analogie, contre-exemple, chiffre…). Ces contraintes empêchent les boucles stériles et donnent un vrai rythme de dialogue. |
| 🆕 | **Modérateur RAG (mode ADRASEC enrichi)** | **v1.1** : un 3ᵉ LLM observe le dialogue en arrière-plan et extrait des fiches structurées (JSON) tous les N échanges. Capitalisation automatique dans `rag_adrasec.json`, réutilisable pour exercices, RETEX, ou indexation dans IAbrain. |
| 🌐 | **Ollama local OU cloud, par LLM** | Chaque IA (y compris le modérateur) peut être configurée indépendamment : LLM1 sur un serveur local LAN, LLM2 sur Ollama Cloud, modérateur ailleurs encore. Mixage possible : petit modèle local pose les questions, gros modèle cloud répond. |
| 📚 | **Thèmes secondaires guidés** | L'utilisateur définit un sujet principal (fil rouge) + une liste de thèmes secondaires. Le moteur fait défiler les thèmes tous les N tours, garantissant une progression de la conversation sans dérive thématique. |
| 🧠 | **Mémoire à fenêtre glissante** | Les N derniers échanges sont passés intégralement aux LLM ; les plus anciens sont condensés en un **résumé glissant** régénéré périodiquement. Évite l'explosion du contexte au-delà de 20-30 tours. |
| 🔍 | **Détection de dérive linguistique** | Si un modèle bascule en chinois/cyrillique/arabe en cours de génération (bug fréquent de Qwen 2.5 sur les conversations longues), d-IA détecte automatiquement (ratio > 5% caractères non-latins), régénère avec température réduite, et tronque si nécessaire avec un avertissement. |
| 🎤 | **Synthèse vocale SAPI5 deux voix** | Activation optionnelle (case à cocher dans Paramètres IA). Chaque IA a sa voix configurable parmi celles installées sur Windows. **Le dialogue se synchronise sur la voix** : la génération du tour suivant se fait en parallèle pendant que le TTS parle, mais l'affichage n'arrive qu'à la fin de la lecture précédente. Pas de bourrage, vrai rythme conversationnel à deux voix. |
| ✨ | **Déblocage des voix OneCore Windows 10/11** | Bouton intégré qui rend accessibles à SAPI5 les voix modernes Windows (Henri Natural, Julie, Paul, Caroline, Claude, Hortense…) en copiant les clés de registre `Speech_OneCore` vers `Speech`. Opération réversible via un bouton « Restaurer ». |
| ✏️ | **Configuration persistante** | Tous les paramètres (hosts, modèles, clés API offusquées en base64, sujet, thèmes, voix, températures, fréquence d'extraction RAG…) sont sauvés dans `d-ia_setup.json` à côté de l'exécutable, et rechargés au démarrage. |
| 📤 | **Export multi-format** | Bouton « Exporter la conversation » avec menu déroulant : **JSON** (données structurées pour retraitement / RETEX), **Markdown** (fichier `.md` lisible avec titres et italiques, parfait pour Notion/Obsidian/GitHub), **RTF** (couleurs LLM1 bleu et LLM2 violet, ouvre directement dans Word / LibreOffice Writer). |
| 🎨 | **Interface bicolore** | Zone de conversation sur fond bleu clair, avec messages **bleus pour LLM1** et **mauves pour LLM2** (rappel du logo). Lisibilité optimale, distinction immédiate des locuteurs. Méta-messages du modérateur en gris italique. |
| ⚙️ | **Fenêtre Paramètres IA modale** | Onglets : **IA 1 - Investigateur**, **IA 2 - Analyste**, **IA 3 - Modérateur** (v1.1), **Mode ADRASEC** (v1.1, activation et fréquence d'extraction), **Synthèse vocale**. |

---
<img src="images/d-ia_main_screen.jpg" alt="d-IA main screen" width="1024">

## 🆕 Nouveautés v1.1 — Mode ADRASEC enrichi (modérateur RAG)

La **v1.1** introduit un **3ᵉ LLM modérateur** qui observe le dialogue en arrière-plan et **extrait automatiquement des fiches documentaires** au format JSON structuré. Le résultat : **chaque dialogue devient une matière première directement réutilisable** pour exercices, RETEX, formations ou base de connaissances RAG.

### Principe

```
LLM1 (Investigateur)  ⇄  LLM2 (Analyste)
                  │
                  └─ chaque message ──→  LLM3 (Modérateur)
                                              │
                                              ├─ tous les N échanges → extraction continue
                                              └─ fin du dialogue   → synthèse finale
                                                        │
                                                        ▼
                                          rag_adrasec.json (base de fiches)
                                                        │
                                                        ▼
                                          Réinjectable dans IAbrain ↓
```

### Ce qu'on récolte

Pour un dialogue de 30 tours sur la propagation HF, on obtient typiquement **8 à 12 fiches structurées** comme celle-ci :

```json
{
  "titre": "Variations diurnes de la couche F2",
  "domaine": "HF_NVIS",
  "tags": ["F2", "photoionisation", "vent neutre", "température thermosphérique"],
  "resume": "La densité maximale NmF2 et la fréquence de coupure foF2 varient quotidiennement sous l'effet combiné de la photoionisation solaire et de la recombinaison...",
  "faits": [
    "Photoionisation crée des électrons, recombinaison avec O⁺ les détruit, pic NmF2 vers 14-16h locales",
    "foF2 atteint 15 MHz en journée et 2-3 MHz le matin, retard de 2-3h dû au transport d'électrons",
    "Hausse de 100 K de la température thermosphérique → temps de transport réduit de 15 min"
  ],
  "procedures": [],
  "sources_citees": ["satellite DMSP", "radar incohérent de Saint-Santin"],
  "confiance": "haute",
  "source_dialogue": {
    "type": "dialogue_d-IA",
    "mode_extraction": "continue",
    "tour_debut": 0,
    "tour_fin": 7,
    "theme": "La couche F2 et ses variations diurnes",
    "moderateur_modele": "gpt-oss:120b"
  },
  "date": "2026-05-17T14:51:20"
}
```

Chaque fiche contient :
- **Métadonnées** : titre, domaine ADRASEC, tags, niveau de confiance
- **Contenu** : résumé synthétique + faits techniques détaillés (avec chiffres, fréquences, seuils)
- **Procédures** opérationnelles quand applicable
- **Sources citées** par les LLM
- **Traçabilité complète** : modèles utilisés, tours concernés, thème actif

### Configuration

L'**onglet « IA 3 — Modérateur »** dans Paramètres IA permet de :
- Configurer le LLM3 (host local ou cloud, modèle, clé API)
- Choisir la **fréquence d'extraction** (tous les N échanges complets, par défaut 4)
- Voir les **statistiques** : fiches en base, fiches cette session
- Ouvrir le fichier `rag_adrasec.json` ou en sauvegarder une copie

**Modèles modérateurs recommandés** (par ordre de qualité pour l'extraction JSON) :
- `gpt-oss:120b` (Ollama Cloud) — **excellent**, JSON très propre, bon respect des consignes
- `qwen3-coder:480b` (Ollama Cloud) — excellent pour le format structuré
- `gemma2:9b` (local) — bon compromis qualité/VRAM
- `mistral-nemo:12b` (local) — très bon en français

Le modérateur peut tourner sur Ollama Cloud pendant que les deux LLM principaux sont en local : configuration idéale pour profiter d'un gros modèle d'extraction sans charge GPU supplémentaire.

---

## 🔗 Intégration avec IAbrain

Les fiches générées par d-IA sont **directement consommables par le système RAG d'IAbrain** (autre projet F1GBD/ADRASEC 77). C'est le **chaînon manquant** entre génération de dialogues et interrogation en langage naturel.

### Le scénario complet

```
1. d-IA génère des fiches lors d'un dialogue
        ↓
2. Export Markdown au format IAbrain-friendly
        ↓
3. /index dans IAbrain
        ↓
4. Vous interrogez IAbrain en langage naturel sur vos sujets ADRASEC
```

### Récupération des fiches dans IAbrain

#### Méthode 1 — Export Markdown puis indexation manuelle (recommandée)

1. **Localiser le fichier RAG** : `rag_adrasec.json` se trouve à côté de `d-IA.exe` (typiquement `C:\d-IA\``)

2. **Convertir en Markdown** (script à venir) ou ouvrir le JSON et copier-coller le résumé + faits + procédures de chaque fiche dans un fichier `.md` dédié

3. **Placer les fichiers** dans un dossier dédié de votre choix, par exemple :
   ```
   C:\Users\<user>\Documents\IAbrain_RAG_perso\d-IA\
   ├── 2026-05-17_propagation_F2.md
   ├── 2026-05-17_eruptions_solaires.md
   ├── 2026-05-17_NVIS_turbulences.md
   └── ...
   ```

4. **Indexer dans IAbrain** :
   ```
   /index C:\Users\<user>\Documents\IAbrain_RAG_perso\d-IA\
   ```
   IAbrain absorbe les fiches dans sa **base personnelle vectorielle** (pas dans la base principale ADRASEC, ce qui préserve son intégrité).

5. **Interroger** IAbrain en langage naturel :
   - *« Quelle est la fréquence de coupure foF2 typique et son cycle diurne ? »*
   - *« Comment la propagation NVIS est affectée par les turbulences Kelvin-Helmholtz ? »*
   - *« Quels paramètres surveiller pour anticiper un blackout HF après une éruption solaire ? »*

   IAbrain répond en s'appuyant sur **les fiches d-IA + sa base principale ADRASEC**.

#### Méthode 2 — Édition manuelle du JSON

Vous pouvez aussi ouvrir `rag_adrasec.json` directement avec un éditeur (Notepad++, VS Code) pour :
- **Corriger** les imprécisions éventuelles produites par le LLM
- **Supprimer** les fiches non pertinentes
- **Enrichir** les fiches avec vos propres notes ADRASEC (référence FNRASEC, dates d'exercice, etc.)
- **Fusionner** des fiches similaires

Le format JSON est documenté en commentaire en début de fichier et reste lisible à l'œil.

#### Méthode 3 — Sync automatisée (à venir)

Une version future de d-IA proposera **l'indexation directe** dans IAbrain via API à la fin de chaque dialogue. Pour l'instant, le passage par les fichiers `.md` ou JSON est manuel.

### Capitalisation départementale

Le fichier `rag_adrasec.json` est :
- 📦 **Portable** : un seul fichier JSON, copiable d'un poste à l'autre
- 🔄 **Versionnable** : compatible Git (texte structuré, diff lisible)
- 🤝 **Partageable** : envoyez votre base à un autre opérateur ADRASEC qui peut l'absorber dans son IAbrain
- 🛡️ **Indépendant** : les fiches restent exploitables même sans d-IA (simple JSON)

Une ADRASEC départementale peut ainsi bâtir, dialogue après dialogue, une **mémoire technique structurée** propre à son territoire et à ses spécificités, partageable au sein de la FNRASEC.

---



## 📋 Pré-requis

### Logiciels

- **Windows 10 ou 11** (le TTS SAPI5 et le binaire pyttsx3 sont Windows-only)
- **Ollama** installé localement : <https://ollama.com/download>
  - ou compte **Ollama Cloud** avec clé API : <https://ollama.com/settings/keys>
- **Au moins deux modèles** téléchargés via Ollama (trois si vous utilisez le modérateur RAG) :

  ```powershell
  ollama pull mistral:7b
  ollama pull llama3.2:3b
  ollama pull gemma2:9b      # pour le modérateur (mode v1.1)
  ```

  Recommandés pour le français : `mistral:7b`, `mistral-nemo:12b`, `llama3.1:8b`, `llama3.2:3b`, `gemma2:9b`. Éviter `qwen2.5` qui dérive vers le chinois sur les conversations longues (d-IA détecte et corrige mais c'est sous-optimal).

### Matériel

| Configuration | VRAM nécessaire |
|---|---|
| 2 × modèles 3B (llama3.2:3b + gemma3:1b) | ~4 Go |
| 1 × 3B + 1 × 7B (llama3.2:3b + mistral:7b) | ~10 Go |
| 2 × 7B | ~16 Go |
| 1 × 7B + 1 × 12B (mistral:7b + mistral-nemo:12b) | ~20 Go |
| 2 LLM principaux + modérateur sur Ollama Cloud (v1.1) | VRAM des deux principaux seulement |
| Mode éco VRAM (déchargement entre tours) | Pas de minimum (CPU OK) |

Sans GPU, ça marche aussi mais chaque tour prend 30-60 s au lieu de 5-10 s.

---

## 🚀 Installation

1. Télécharger [`d-IA.7z`](https://github.com/f1gbd/F1GBD/releases/latest) depuis la page Releases
2. Décompresser dans un dossier de votre choix (ex : `C:\d-IA\`)
3. Lancer `d-IA.exe`
4. Cliquer sur **⚙ Paramètres IA…** pour configurer les deux (ou trois) IA
5. Cliquer sur **▶ Démarrer**

---

## 📖 Utilisation

### Premier démarrage

1. **Ouvrir Paramètres IA** (bouton en haut à droite) :
   - **Onglet IA 1** : laisser `http://localhost:11434` si Ollama tourne localement. Cliquer « Tester la connexion », choisir un modèle (ex: `mistral:7b`)
   - **Onglet IA 2** : idem avec un autre modèle (ex: `llama3.2:3b`)
   - **Onglet IA 3 - Modérateur** *(v1.1 optionnel)* : configurer un 3ᵉ LLM (local ou cloud). Recommandation : `gpt-oss:120b` sur Ollama Cloud pour la meilleure qualité d'extraction
   - **Onglet Mode ADRASEC** *(v1.1)* : cocher « Activer le mode ADRASEC enrichi », choisir la fréquence d'extraction (4 échanges par défaut)
   - **Onglet Synthèse vocale** : *(optionnel)* cocher « Activer la lecture vocale », choisir une voix pour chaque IA, tester
2. **Fermer** la fenêtre Paramètres
3. **Saisir un sujet principal** dans la colonne gauche (ex: « La propagation des ondes radio dans l'ionosphère »)
4. **Saisir une liste de thèmes secondaires** (un par ligne)
5. **Cliquer ▶ Démarrer**

### Pendant la conversation

- **Pause / Reprendre** : suspendre temporairement le dialogue
- **Arrêter** : termine la conversation (et interrompt immédiatement le TTS en cours). Si le modérateur RAG est actif, déclenche aussi la **synthèse finale** sur l'intégralité du dialogue.
- **Exporter** : choix du format (JSON / Markdown / RTF) via le menu déroulant
- La **colonne droite** affiche le tour courant, le thème actif, et le résumé glissant régénéré périodiquement
- Les **méta-messages du modérateur** apparaissent en gris italique dans la conversation :
  - `[Moderateur] Extraction continue en cours sur N messages...`
  - `[Moderateur] 2 fiche(s) ajoutee(s) [continue] - Total base : 8 | Session : 2`
  - `[Moderateur] Synthese finale terminee - Total base : 12 | Session : 6`

### Configuration Ollama Cloud

1. Créer un compte sur <https://ollama.com> et générer une clé API
2. Dans **Paramètres IA → Onglet IA 1** (ou 2, ou 3), cocher **« Utiliser Ollama Cloud »**
3. Coller la clé dans le champ « API key »
4. Cliquer « Tester la connexion » → la liste des modèles cloud apparaît avec ☁ devant chaque nom (gpt-oss:120b, deepseek-v3.1:671b…)

> ⚠️ **Confidentialité** : en mode cloud, vos prompts sont envoyés à ollama.com. À ne pas utiliser pour des données opérationnelles confidentielles. C'est encore plus vrai pour le modérateur RAG qui voit **l'intégralité** du dialogue.

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

## ❓ FAQ

**Le test de voix fonctionne mais le dialogue ne lit rien.**
Vérifié et corrigé en v1.0 : refonte du moteur TTS sur SAPI direct via `win32com` (au lieu de pyttsx3 qui maintenait un singleton incompatible multi-thread). Si vous voyez encore ce comportement, vérifiez que `pywin32` est bien installé (`pip install pywin32`) et regardez la console pour des erreurs `[TTSEngine]`.

**Erreur Ollama « failed to allocate compute pp buffers ».**
Votre VRAM est saturée. Solutions : (1) cocher « Mode éco VRAM (décharge entre tours) » dans les Paramètres avancés, (2) réduire `num_ctx` à 2048 ou 4096, (3) utiliser des modèles plus petits, (4) basculer un des deux LLM sur Ollama Cloud, (5) basculer le modérateur RAG sur Ollama Cloud (il consomme 4-8 Go selon le modèle pendant l'extraction).

**Les conversations en chinois apparaissent en plein milieu d'une réponse.**
C'est Qwen 2.5 qui dérive vers sa langue dominante d'entraînement. d-IA détecte et régénère automatiquement. Pour éviter le problème dès le départ, préférez `mistral:7b`, `llama3.x`, `mistral-nemo` ou `gemma2:9b` qui sont stables en français sur 20+ tours.

**Les voix OneCore n'apparaissent pas après le déblocage.**
Il faut **redémarrer d-IA** après l'activation (la liste est lue au lancement de l'app, pas dynamiquement). Si elles n'apparaissent toujours pas, vérifier dans regedit que `HKLM\SOFTWARE\Microsoft\Speech\Voices\Tokens` contient bien les nouvelles voix.

**Comment voir si une conversation est intéressante pendant qu'elle tourne ?**
La colonne droite « Resume glissant » se met à jour automatiquement toutes les N interventions (paramètre « Fenêtre mémoire »). Le résumé est aussi inclus dans l'export final.

**Le modérateur RAG (v1.1) ne crée pas de fiches malgré l'activation.**
Vérifier dans l'ordre :
1. **L'onglet IA 3 - Modérateur** est bien configuré (host + modèle testé)
2. Le seuil d'extraction est atteint : par défaut **8 messages** (= 4 échanges complets). Au-dessous, rien ne se déclenche.
3. Le modèle modérateur **existe vraiment** : tester la connexion pour voir la liste réelle. Un nom inventé (ex: `qwen3.5:397b`) provoque une erreur 403 silencieuse.
4. Le modèle est **adapté au JSON structuré** : préférer `gpt-oss:120b`, `gemma2:9b`, `mistral-nemo:12b`. Éviter les très petits modèles (< 7B) qui produisent du JSON cassé.

**Le fichier `rag_adrasec.json` se remplit, mais les fiches sont parfois tronquées.**
Le LLM modérateur a dépassé la limite `num_predict` (4096 tokens par défaut). d-IA détecte ces troncatures et émet un avertissement dans la conversation. Les fiches **complètes** sont quand même extraites — seule la dernière fiche d'un cycle peut être perdue. Pour éviter : demander moins de fiches dans le prompt (au moins 2 max), ou utiliser un modèle plus concis.

**Peut-on faire dialoguer trois IA au lieu de deux ?**
Pas en mode dialogue : la logique des rôles asymétriques (Investigateur / Analyste) est conçue pour deux. **Mais avec la v1.1, un 3ᵉ LLM modérateur intervient en arrière-plan** pour extraire des fiches du dialogue. Une v2 pourrait introduire un vrai 3ᵉ interlocuteur (« Modérateur conversationnel » qui intervient tous les K tours pour synthétiser ou recadrer).

**Les fiches générées par d-IA peuvent-elles être réimportées dans IAbrain ?**
Oui, c'est même le cas d'usage principal de la v1.1. Voir la section [Intégration avec IAbrain](#-intégration-avec-iabrain) ci-dessus. La méthode actuelle est manuelle (export JSON → conversion Markdown → `/index` dans IAbrain). Une sync automatisée est prévue pour une future version.

---

## 🤝 Communauté

d-IA est un **projet open développé pour la communauté ADRASEC**, mis à disposition librement aux opérateurs ADRASEC départementales, à la FNRASEC, et plus largement à toute personne intéressée par les dialogues autonomes entre LLM.

Toute contribution, retour d'expérience ou proposition d'amélioration est bienvenue via les *Issues* du dépôt GitHub.

**Idées d'usage soumises** :
- Préparation aux examens radioamateurs (un LLM joue le candidat, l'autre l'examinateur, le modérateur extrait des fiches de révision)
- Génération de RETEX d'exercice fictifs pour la doc ADRASEC, capitalisés automatiquement par le modérateur
- Exploration pédagogique de la propagation HF, NVIS, satellite, communications quantiques…
- Comparaison qualitative de deux modèles sur le même sujet
- **(v1.1) Constitution progressive d'une base RAG départementale ADRASEC**, réutilisable via IAbrain pour des consultations en langage naturel
- Génération de matière première pour podcasts radioamateurs

---

## 📜 Historique des versions

### v1.1 — Mai 2026 — Modérateur RAG ADRASEC

- ➕ **Modérateur RAG** : un 3ᵉ LLM extrait des fiches structurées du dialogue en arrière-plan
- ➕ **Mode ADRASEC enrichi** : activation via case à cocher, fréquence d'extraction configurable
- ➕ **Onglet « IA 3 - Modérateur »** dans Paramètres IA
- ➕ **Onglet « Mode ADRASEC »** : statistiques, accès au fichier `rag_adrasec.json`, boutons Voir/Ouvrir/Sauvegarder
- ➕ **Synthèse finale** déclenchée automatiquement au clic Arrêter
- ➕ **Parseur JSON robuste** tolérant aux artefacts LLM (fences markdown, raisonnement préliminaire, virgules traînantes)
- ➕ **Détection de troncature** : avertissement clair si la réponse modérateur dépasse `num_predict`
- ➕ **Format de stockage** `rag_adrasec.json` : portable, versionnable, indépendant
- ➕ **Intégration IAbrain** : les fiches peuvent être réinjectées dans le système RAG IAbrain pour interrogation en langage naturel

### v1.0 — Mai 2026 — Première version stable

- Dialogue entre deux LLM avec rôles asymétriques (Investigateur / Analyste)
- Thèmes secondaires guidés, mémoire à fenêtre glissante, détection de dérive linguistique
- Synthèse vocale SAPI5 deux voix avec synchronisation dialogue/voix
- Déblocage des voix OneCore Windows 10/11
- Export JSON / Markdown / RTF
- Configuration persistante avec offuscation des clés API
- Support Ollama local et cloud

---

<div align="center">

### 📡 Auteur

**Jean-Louis (F1GBD)**
*ADRASEC 77 — FNRASEC*

**Version 1.1 — 2026**

---

*Pour toute question, contactez votre référent ADRASEC départemental.*

🤖 **d-IA v1.1** — *Deux IA dialoguent, un troisième capitalise. Votre base de connaissances se construit toute seule.*

</div>
