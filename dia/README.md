<div align="center">

<img src="images/d-ia_logo.jpg" alt="d-IA" width="300">

### Dialogue autonome entre deux IA, arbitré par un troisième — un outil d'aide à la recherche par IA

*Conversation scientifique guidée — Investigateur & Analyste — **Modérateur conversationnel qui fait converger le dialogue vers une solution (v1.2)** — Presets de sujet importables/exportables (v1.2) — Mode ADRASEC enrichi (modérateur RAG) — Ollama local & cloud — Mémoire glissante — Détection de dérive linguistique — Synthèse vocale SAPI5 deux voix — Synchronisation dialogue/voix — Export JSON / Markdown / RTF — Thèmes secondaires guidés — Configuration persistante*

[![Version](https://img.shields.io/badge/version-dia--v1.2.0-blue)](https://github.com/f1gbd/F1GBD/releases/tag/dia-v1.2.0)
[![Plateforme](https://img.shields.io/badge/plateforme-Windows%2010%2F11-lightgrey.svg)]()
[![Licence](https://img.shields.io/badge/usage-ADRASEC%2FFNRASEC-green.svg)]()
[![Local / Cloud](https://img.shields.io/badge/Ollama-local%20%2F%20cloud-brightgreen.svg)]()
[![Accessibilité](https://img.shields.io/badge/accessibilit%C3%A9-voix%20SAPI5-purple.svg)]()
[![Modérateur](https://img.shields.io/badge/mode-mod%C3%A9rateur%20conversationnel-teal.svg)]()
[![RAG](https://img.shields.io/badge/mode-ADRASEC%20enrichi-orange.svg)]()

### 📥 [**Télécharger la dernière version (v1.2.0)**](https://github.com/f1gbd/F1GBD/releases/download/dia-v1.2.0/d-IA.7z)

</div>

---

## 🎯 Qu'est-ce que d-IA ?

**d-IA** est un **outil d'aide à la recherche par IA**. Il fait **dialoguer en autonomie deux modèles de langage** sur un sujet scientifique ou technique défini par l'utilisateur, pendant qu'un **troisième LLM arbitre la discussion pour la faire aboutir à une solution**.

- 🔬 L'un joue l'**Investigateur** : il pose des questions, creuse, doute, demande des précisions.
- 🧠 L'autre joue l'**Analyste** : il répond avec rigueur et apporte systématiquement un élément neuf.
- 🆕 Le troisième (**v1.2**) joue le **Modérateur conversationnel** : il intervient dans le fil tous les K tours pour faire le bilan, recadrer si la discussion dérive, et **poser une consigne de convergence chiffrée** qui pousse les deux IA vers un verdict.

Le résultat n'est plus seulement une conversation évolutive : c'est une **démarche de recherche dirigée vers une conclusion**. On pose une question ouverte (« peut-on communiquer par ondes gravitationnelles ? »), et d-IA déroule un raisonnement contradictoire et complémentaire qui converge vers une réponse argumentée et chiffrée.

Tout tourne **localement** par défaut (modèles Ollama auto-hébergés), avec une option **cloud** (gpt-oss:120b, deepseek-v3.1:671b, kimi-k2…) si on souhaite faire dialoguer, arbitrer ou modérer avec des modèles XL hébergés.

> 💡 **La différence clé de la v1.2** : jusqu'ici, deux IA pouvaient explorer un sujet sans jamais conclure. Désormais, un modérateur garde le cap et **force la convergence vers une solution** — d-IA devient un véritable assistant de recherche, pas seulement un générateur de dialogue.

---

## ⭐ Fonctionnalités principales

| Icône | Fonctionnalité | Description |
|:---:|---|---|
| 🤖 | **Deux LLM aux rôles asymétriques** | LLM1 (Investigateur) doit terminer chaque tour par une question ouverte. LLM2 (Analyste) doit introduire un élément nouveau dans chaque réponse (analogie, contre-exemple, chiffre…). Ces contraintes empêchent les boucles stériles et donnent un vrai rythme de dialogue. |
| 🆕 | **Modérateur conversationnel (v1.2)** | Un 3ᵉ LLM **intervient directement dans le dialogue** tous les K tours : bilan de ce qui est acquis, point bloquant restant, et **consigne de convergence précise** (chiffre à établir, hypothèse à trancher, verdict à formuler). Son intervention est réinjectée dans le contexte des deux IA, ce qui crée la rétroaction qui **fait aboutir la recherche**. |
| 📋 | **Presets de sujet (v1.2)** | Boutons **Importer / Exporter un preset** : un sujet de recherche complet (sujet principal + thèmes secondaires + objectif de convergence + réglages) se charge en un clic, se sauvegarde au format `.diapreset.json` et **se partage** entre opérateurs. Le format texte est aussi accepté à l'import. |
| 🗂️ | **Modérateur RAG (mode ADRASEC enrichi)** | **v1.1** : un LLM observe le dialogue en arrière-plan et extrait des fiches structurées (JSON) tous les N échanges. Capitalisation automatique dans `rag_adrasec.json`, réutilisable pour exercices, RETEX, ou indexation dans IAbrain. **Compatible avec le modérateur conversationnel** : l'un parle, l'autre fiche. |
| 🌐 | **Ollama local OU cloud, par LLM** | Chaque IA (y compris le modérateur) peut être configurée indépendamment : LLM1 sur un serveur local LAN, LLM2 sur Ollama Cloud, modérateur ailleurs encore. Mixage possible : petit modèle local pose les questions, gros modèle cloud arbitre. |
| 📚 | **Thèmes secondaires guidés** | L'utilisateur définit un sujet principal (fil rouge) + une liste de thèmes secondaires. Le moteur fait défiler les thèmes tous les N tours, garantissant une progression de la conversation sans dérive thématique — et, avec le modérateur, une trajectoire vers la conclusion. |
| 🧠 | **Mémoire à fenêtre glissante** | Les N derniers échanges sont passés intégralement aux LLM ; les plus anciens sont condensés en un **résumé glissant** régénéré périodiquement. Évite l'explosion du contexte au-delà de 20-30 tours. |
| 🔍 | **Détection de dérive linguistique** | Si un modèle bascule en chinois/cyrillique/arabe en cours de génération (bug fréquent de Qwen 2.5 sur les conversations longues), d-IA détecte automatiquement (ratio > 5% caractères non-latins), régénère avec température réduite, et tronque si nécessaire avec un avertissement. S'applique aussi au modérateur. |
| 🎤 | **Synthèse vocale SAPI5 deux voix** | Activation optionnelle. Chaque IA a sa voix configurable parmi celles installées sur Windows ; le modérateur reprend la voix de l'Investigateur. **Le dialogue se synchronise sur la voix** : la génération du tour suivant se fait en parallèle pendant que le TTS parle, mais l'affichage n'arrive qu'à la fin de la lecture précédente. Vrai rythme conversationnel. |
| ✨ | **Déblocage des voix OneCore Windows 10/11** | Bouton intégré qui rend accessibles à SAPI5 les voix modernes Windows (Henri Natural, Julie, Paul, Caroline, Claude, Hortense…) en copiant les clés de registre `Speech_OneCore` vers `Speech`. Opération réversible via un bouton « Restaurer ». |
| ✏️ | **Configuration persistante** | Tous les paramètres (hosts, modèles, clés API offusquées en base64, sujet, thèmes, objectif de convergence, fréquence du modérateur, voix, températures…) sont sauvés dans `d-ia_setup.json` à côté de l'exécutable, et rechargés au démarrage. |
| 📤 | **Export multi-format** | Bouton « Exporter la conversation » : **JSON** (données structurées pour retraitement / RETEX), **Markdown** (fichier `.md` lisible, parfait pour Notion/Obsidian/GitHub), **RTF** (couleurs LLM1 bleu, LLM2 violet et **Modérateur vert**, ouvre directement dans Word / LibreOffice). |
| 🎨 | **Interface tricolore** | Zone de conversation avec messages **bleus pour LLM1**, **mauves pour LLM2** et **verts pour le Modérateur (v1.2)**. Lisibilité optimale, distinction immédiate des trois rôles. Méta-messages en gris italique. |
| ⚙️ | **Fenêtre Paramètres IA modale** | Onglets : **IA 1 - Investigateur**, **IA 2 - Analyste**, **IA 3 - Modérateur**, **Mode ADRASEC** (activation du modérateur conversationnel et du RAG), **Synthèse vocale**. |

---
<img src="images/d-ia_main_screen.jpg" alt="d-IA main screen" width="1024">

## 🆕 Nouveautés v1.2 — Le modérateur qui fait converger la recherche

La **v1.2** transforme d-IA en **outil d'aide à la recherche dirigée**. Jusqu'à la v1.1, le 3ᵉ LLM observait passivement le dialogue pour en extraire des fiches. Désormais, il peut **prendre la parole dans la conversation** pour la piloter vers une solution.

### Le principe

```
                  recadre / fait converger tous les K tours
                  ┌─────────────────────────────────────────┐
                  │                                          ▼
LLM1 (Investigateur)  ⇄  LLM2 (Analyste)  ◄────  LLM3 (Modérateur conversationnel)
                                                          │
                            son intervention est réinjectée dans le contexte
                            des deux IA → rétroaction → convergence vers la solution
```

### Ce que fait le modérateur conversationnel

À chaque intervention (tous les K tours, K configurable), le modérateur produit une note courte et structurée :

1. **Bilan** — ce qui est désormais acquis ou chiffré dans le dialogue.
2. **Point bloquant** — ce qui reste flou, contradictoire ou non tranché.
3. **Consigne de convergence** — une directive *précise et actionnable* pour les prochains tours.

> *Exemple sur le sujet « communication par ondes gravitationnelles » :*
> *« Bilan : la faisabilité de principe est établie. Point bloquant : aucun ordre de grandeur n'a été posé. Consigne : établissez le strain h produit par une masse de 1 t oscillant à 100 Hz, puis comparez-le au plancher de bruit d'un interféromètre type LIGO (~10⁻²¹). »*

Le modérateur **ne répond pas à la place des deux IA** : il oriente, recadre, et exige une conclusion. Comme son message entre dans l'historique et donc dans le contexte du tour suivant, les deux IA en tiennent compte — c'est cette boucle qui les empêche de tourner en rond et les conduit au **verdict chiffré**.

### Pourquoi c'est utile pour la recherche

| Sans modérateur (v1.1) | Avec modérateur conversationnel (v1.2) |
|---|---|
| Deux IA explorent un sujet, parfois indéfiniment | Un arbitre garde le cap et impose une trajectoire |
| Risque de digression ou de boucle | Recadrage explicite dès que le dialogue dérive |
| Pas de conclusion garantie | Consignes de convergence → **verdict chiffré** |
| Matière brute à relire | Démarche dirigée vers une solution exploitable |

### Le modérateur conversationnel et le RAG, ensemble

Les deux modes peuvent tourner **simultanément** : le LLM3 **parle** dans le dialogue (modérateur conversationnel) **et** capitalise en arrière-plan des fiches dans `rag_adrasec.json` (modérateur RAG). Les recadrages du modérateur ne sont pas fichés — seule la matière technique des deux IA l'est.

### Configuration

Dans **Paramètres IA → onglet « Mode ADRASEC »**, section **« Modérateur conversationnel (v1.2) »** :

- **Activer** le modérateur conversationnel (case à cocher)
- **Intervenir tous les K tours** (par défaut 6)
- **Température** du modérateur (par défaut 0.4 — basse pour un recadrage factuel et directif)
- **Objectif de convergence** (champ texte optionnel) : la cible que le modérateur cherchera à atteindre

Le modérateur réutilise la cible (host / cloud / modèle) configurée dans l'onglet **« IA 3 - Modérateur »**. **Modèles recommandés** : `gpt-oss:120b` (Ollama Cloud) pour des consignes nettes, ou `gemma2:9b` / `mistral-nemo:12b` en local.

---

## 📋 Nouveautés v1.2 — Presets de sujet de recherche

Un **preset** capture un sujet de recherche complet et réutilisable : **sujet principal + thèmes secondaires + objectif de convergence + réglages** (tours par thème, fréquence du modérateur, températures, mode ADRASEC…).

Dans la colonne de gauche, le menu **« 📋 Preset de sujet ▼ »** propose :

- **📥 Importer un preset** — charge tout en un clic, avec un aperçu de confirmation. Accepte le format natif `.diapreset.json` **et** le format texte structuré (`.txt`).
- **📤 Exporter le sujet courant** — sauvegarde l'état actuel dans un `.diapreset.json` partageable, nommé d'après le sujet.
- **👁 Aperçu du sujet courant** — récapitulatif rapide sans rien exporter.

### Pourquoi c'est utile

- 🔁 **Reproductibilité** : relancer exactement la même investigation, ou la confier à un autre opérateur.
- 🤝 **Partage** : un fichier preset unique, portable, versionnable (texte/JSON, diff lisible Git).
- 📚 **Bibliothèque de sujets** : constituer une collection de sujets de recherche ADRASEC prêts à l'emploi (propagation, NVIS, blackout HF, communications alternatives…).

### Exemple de preset fourni

Un preset complet **« Communication par ondes gravitationnelles »** est livré (`.diapreset.json` + version texte). Il définit 7 thèmes secondaires ordonnés pour mener le dialogue de la faisabilité brute jusqu'au verdict chiffré, avec le modérateur conversationnel activé. Il suffit de l'importer, de choisir les modèles, et de cliquer Démarrer.

---

## 🗂️ Mode ADRASEC enrichi — Modérateur RAG (v1.1, toujours présent)

En complément du modérateur conversationnel, le **modérateur RAG** observe le dialogue et **extrait automatiquement des fiches documentaires** au format JSON structuré. Chaque dialogue devient une matière première directement réutilisable pour exercices, RETEX, formations ou base de connaissances.

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

L'**onglet « IA 3 — Modérateur »** dans Paramètres IA permet de configurer le LLM3 (host local ou cloud, modèle, clé API). L'**onglet « Mode ADRASEC »** permet d'activer le RAG, de choisir la **fréquence d'extraction** (tous les N échanges complets, par défaut 4), et de voir les **statistiques** (fiches en base, fiches cette session).

**Modèles modérateurs recommandés** (par ordre de qualité pour l'extraction JSON) :
- `gpt-oss:120b` (Ollama Cloud) — **excellent**, JSON très propre, bon respect des consignes
- `qwen3-coder:480b` (Ollama Cloud) — excellent pour le format structuré
- `gemma2:9b` (local) — bon compromis qualité/VRAM
- `mistral-nemo:12b` (local) — très bon en français

Le modérateur peut tourner sur Ollama Cloud pendant que les deux LLM principaux sont en local : configuration idéale pour profiter d'un gros modèle d'arbitrage et d'extraction sans charge GPU supplémentaire.

---

## 🔗 Intégration avec IAbrain

Les fiches générées par d-IA sont **directement consommables par le système RAG d'IAbrain** (autre projet F1GBD/ADRASEC 77). C'est le **chaînon manquant** entre génération de dialogues et interrogation en langage naturel.

### Le scénario complet

```
1. d-IA génère des fiches lors d'un dialogue (arbitré par le modérateur)
        ↓
2. Export Markdown au format IAbrain-friendly
        ↓
3. /index dans IAbrain
        ↓
4. Vous interrogez IAbrain en langage naturel sur vos sujets ADRASEC
```

### Récupération des fiches dans IAbrain

#### Méthode 1 — Export Markdown puis indexation manuelle (recommandée)

1. **Localiser le fichier RAG** : `rag_adrasec.json` se trouve à côté de `d-IA.exe` (typiquement `C:\d-IA\`)
2. **Convertir en Markdown** ou copier-coller le résumé + faits + procédures de chaque fiche dans un fichier `.md` dédié
3. **Placer les fichiers** dans un dossier dédié, par exemple :
   ```
   C:\Users\<user>\Documents\IAbrain_RAG_perso\d-IA\
   ├── 2026-05-17_propagation_F2.md
   ├── 2026-05-17_eruptions_solaires.md
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

#### Méthode 2 — Édition manuelle du JSON

Ouvrir `rag_adrasec.json` avec un éditeur (Notepad++, VS Code) pour corriger, supprimer, enrichir ou fusionner des fiches. Le format JSON est documenté en commentaire en début de fichier et reste lisible à l'œil.

#### Méthode 3 — Sync automatisée (à venir)

Une version future de d-IA proposera **l'indexation directe** dans IAbrain via API à la fin de chaque dialogue.

### Capitalisation départementale

Le fichier `rag_adrasec.json` est **portable** (un seul fichier JSON), **versionnable** (compatible Git), **partageable** (envoyez votre base à un autre opérateur ADRASEC qui l'absorbe dans son IAbrain) et **indépendant** (les fiches restent exploitables même sans d-IA). Une ADRASEC départementale peut ainsi bâtir, dialogue après dialogue, une **mémoire technique structurée** propre à son territoire, partageable au sein de la FNRASEC.

---

## 📋 Pré-requis

### Logiciels

- **Windows 10 ou 11** (le TTS SAPI5 et le binaire pyttsx3 sont Windows-only)
- **Ollama** installé localement : <https://ollama.com/download>
  - ou compte **Ollama Cloud** avec clé API : <https://ollama.com/settings/keys>
- **Au moins deux modèles** téléchargés via Ollama (trois si vous utilisez le modérateur conversationnel et/ou RAG) :

  ```powershell
  ollama pull mistral:7b
  ollama pull llama3.2:3b
  ollama pull gemma2:9b      # pour le modérateur (conversationnel ou RAG)
  ```

  Recommandés pour le français : `mistral:7b`, `mistral-nemo:12b`, `llama3.1:8b`, `llama3.2:3b`, `gemma2:9b`. Éviter `qwen2.5` qui dérive vers le chinois sur les conversations longues (d-IA détecte et corrige mais c'est sous-optimal).

### Matériel

| Configuration | VRAM nécessaire |
|---|---|
| 2 × modèles 3B (llama3.2:3b + gemma3:1b) | ~4 Go |
| 1 × 3B + 1 × 7B (llama3.2:3b + mistral:7b) | ~10 Go |
| 2 × 7B | ~16 Go |
| 1 × 7B + 1 × 12B (mistral:7b + mistral-nemo:12b) | ~20 Go |
| 2 LLM principaux + modérateur sur Ollama Cloud | VRAM des deux principaux seulement |
| Mode éco VRAM (déchargement entre tours) | Pas de minimum (CPU OK) |

Sans GPU, ça marche aussi mais chaque tour prend 30-60 s au lieu de 5-10 s.

> 💡 **Astuce** : pour le modérateur conversationnel, basculer le LLM3 sur Ollama Cloud (`gpt-oss:120b`) laisse tout le GPU aux deux IA principales tout en bénéficiant d'un arbitre de très bonne qualité.

---

## 🚀 Installation

1. Télécharger [`d-IA.7z`](https://github.com/f1gbd/F1GBD/releases/latest) depuis la page Releases
2. Décompresser dans un dossier de votre choix (ex : `C:\d-IA\`)
3. Lancer `d-IA.exe`
4. Cliquer sur **⚙ Paramètres IA…** pour configurer les deux (ou trois) IA
5. *(Optionnel)* Importer un preset de sujet via **📋 Preset de sujet → Importer un preset**
6. Cliquer sur **▶ Démarrer**

---

## 📖 Utilisation

### Premier démarrage

1. **Ouvrir Paramètres IA** (bouton en haut à droite) :
   - **Onglet IA 1** : laisser `http://localhost:11434` si Ollama tourne localement. Cliquer « Tester la connexion », choisir un modèle (ex: `mistral:7b`)
   - **Onglet IA 2** : idem avec un autre modèle (ex: `llama3.2:3b`)
   - **Onglet IA 3 - Modérateur** *(optionnel)* : configurer un 3ᵉ LLM (local ou cloud). Recommandation : `gpt-oss:120b` sur Ollama Cloud
   - **Onglet Mode ADRASEC** :
     - *(v1.2)* Section **Modérateur conversationnel** : cocher « Activer », choisir la fréquence K (6 tours par défaut), la température (0.4), et éventuellement un objectif de convergence
     - *(v1.1)* Section **Mode ADRASEC enrichi** : cocher pour activer l'extraction RAG (facultatif, cumulable)
   - **Onglet Synthèse vocale** : *(optionnel)* cocher « Activer la lecture vocale », choisir une voix pour chaque IA, tester
2. **Fermer** la fenêtre Paramètres
3. **Saisir un sujet principal** + une liste de **thèmes secondaires** (un par ligne) — ou **importer un preset**
4. **Cliquer ▶ Démarrer**

### Pendant la conversation

- **Pause / Reprendre** : suspendre temporairement le dialogue
- **Arrêter** : termine la conversation (et interrompt le TTS en cours). Si le modérateur RAG est actif, déclenche aussi la **synthèse finale** sur l'intégralité du dialogue.
- **Exporter** : choix du format (JSON / Markdown / RTF) via le menu déroulant
- La **colonne droite** affiche le tour courant, le thème actif et le résumé glissant
- Les **interventions du modérateur conversationnel** apparaissent **en vert** dans le fil, avec leur bilan et leur consigne de convergence
- Les **méta-messages du modérateur RAG** apparaissent en gris italique :
  - `[Moderateur] Extraction continue en cours sur N messages...`
  - `[Moderateur] 2 fiche(s) ajoutee(s) [continue] - Total base : 8 | Session : 2`

### Configuration Ollama Cloud

1. Créer un compte sur <https://ollama.com> et générer une clé API
2. Dans **Paramètres IA → Onglet IA 1** (ou 2, ou 3), cocher **« Utiliser Ollama Cloud »**
3. Coller la clé dans le champ « API key »
4. Cliquer « Tester la connexion » → la liste des modèles cloud apparaît avec ☁ devant chaque nom

> ⚠️ **Confidentialité** : en mode cloud, vos prompts sont envoyés à ollama.com. À ne pas utiliser pour des données opérationnelles confidentielles. C'est encore plus vrai pour le modérateur qui voit **l'intégralité** du dialogue.

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

**Quelle est la différence entre le modérateur conversationnel (v1.2) et le modérateur RAG (v1.1) ?**
Le modérateur conversationnel **parle dans le dialogue** pour le piloter vers une solution (bilan + recadrage + consigne de convergence). Le modérateur RAG **observe en silence** et extrait des fiches documentaires en arrière-plan. Les deux utilisent le LLM3 (onglet IA 3) et peuvent être **actifs en même temps**.

**Le modérateur conversationnel ne se déclenche pas.**
Vérifier dans l'ordre : (1) l'onglet **IA 3 - Modérateur** est configuré (host + modèle testé) ; (2) la case « Activer le modérateur conversationnel » est cochée dans l'onglet Mode ADRASEC ; (3) le dialogue a dépassé K tours (par défaut 6) — en dessous, il n'intervient pas encore.

**Peut-on vraiment faire converger un dialogue vers une solution ?**
Oui, c'est l'objet de la v1.2. Le modérateur impose une trajectoire et exige une conclusion. Pour de meilleurs résultats : placez un thème de synthèse/verdict en dernier, renseignez un **objectif de convergence** explicite, et utilisez un modèle d'arbitrage solide (`gpt-oss:120b`, `gemma2:9b`).

**Comment réutiliser un sujet de recherche d'une fois sur l'autre ?**
Utilisez les **presets** (v1.2). « Exporter le sujet courant » produit un `.diapreset.json` que vous rechargez via « Importer un preset ». Le fichier transporte le sujet, les thèmes, l'objectif de convergence et les réglages.

**Erreur Ollama « failed to allocate compute pp buffers ».**
Votre VRAM est saturée. Solutions : (1) cocher « Mode éco VRAM » ; (2) réduire `num_ctx` à 2048 ou 4096 ; (3) utiliser des modèles plus petits ; (4) basculer un des LLM sur Ollama Cloud ; (5) basculer le modérateur sur Ollama Cloud.

**Les conversations en chinois apparaissent en plein milieu d'une réponse.**
C'est Qwen 2.5 qui dérive vers sa langue dominante. d-IA détecte et régénère automatiquement. Préférez `mistral:7b`, `llama3.x`, `mistral-nemo` ou `gemma2:9b`, stables en français sur 20+ tours.

**Les voix OneCore n'apparaissent pas après le déblocage.**
Il faut **redémarrer d-IA** après l'activation (la liste est lue au lancement). Si elles n'apparaissent toujours pas, vérifier dans regedit que `HKLM\SOFTWARE\Microsoft\Speech\Voices\Tokens` contient bien les nouvelles voix.

**Les fiches générées par d-IA peuvent-elles être réimportées dans IAbrain ?**
Oui, c'est le cas d'usage principal du mode RAG. Voir la section [Intégration avec IAbrain](#-intégration-avec-iabrain). La méthode actuelle est manuelle (export JSON → Markdown → `/index`). Une sync automatisée est prévue.

---

## 🤝 Communauté

d-IA est un **projet ouvert développé pour la communauté ADRASEC**, mis à disposition librement aux opérateurs ADRASEC départementales, à la FNRASEC, et plus largement à toute personne intéressée par les dialogues autonomes entre LLM et l'aide à la recherche par IA.

Toute contribution, retour d'expérience ou proposition d'amélioration est bienvenue via les *Issues* du dépôt GitHub.

**Idées d'usage** :
- **Aide à la recherche dirigée** : poser un problème scientifique ouvert et laisser le trio Investigateur/Analyste/Modérateur converger vers une solution chiffrée
- Préparation aux examens radioamateurs (un LLM joue le candidat, l'autre l'examinateur, le modérateur recadre et extrait des fiches de révision)
- Génération de RETEX d'exercices fictifs pour la doc ADRASEC, capitalisés automatiquement
- Exploration pédagogique de la propagation HF, NVIS, satellite, communications quantiques…
- Comparaison qualitative de deux modèles sur le même sujet
- Constitution progressive d'une **base RAG départementale ADRASEC**, réutilisable via IAbrain
- Constitution d'une **bibliothèque de presets** de sujets de recherche partagés au sein de la FNRASEC

---

## 📜 Historique des versions

### v1.2 — Mai 2026 — Modérateur conversationnel & presets : l'aide à la recherche dirigée

- ➕ **Modérateur conversationnel** : un 3ᵉ LLM intervient dans le fil tous les K tours pour faire un bilan, recadrer et poser une consigne de convergence — la conversation **aboutit à une solution**
- ➕ Intervention réinjectée dans le contexte des deux IA (rétroaction → convergence)
- ➕ **Compatible avec le modérateur RAG** : parler et ficher en même temps
- ➕ Section **Modérateur conversationnel** dans l'onglet Mode ADRASEC (activation, fréquence K, température, objectif de convergence)
- ➕ Affichage **vert** dédié au modérateur ; gestion dans les exports JSON / Markdown / RTF (couleur verte)
- ➕ **Presets de sujet** : boutons Importer / Exporter / Aperçu ; format natif `.diapreset.json` + import du format texte
- ➕ Preset d'exemple fourni : « Communication par ondes gravitationnelles »
- ➕ Garde-fou langue appliqué aussi au modérateur ; persistance complète des nouveaux paramètres

### v1.1 — Mai 2026 — Modérateur RAG ADRASEC

- ➕ **Modérateur RAG** : un 3ᵉ LLM extrait des fiches structurées du dialogue en arrière-plan
- ➕ **Mode ADRASEC enrichi** : activation via case à cocher, fréquence d'extraction configurable
- ➕ Onglets « IA 3 - Modérateur » et « Mode ADRASEC » dans Paramètres IA
- ➕ **Synthèse finale** déclenchée automatiquement au clic Arrêter
- ➕ **Parseur JSON robuste** tolérant aux artefacts LLM ; détection de troncature
- ➕ Format de stockage `rag_adrasec.json` portable ; **intégration IAbrain**

### v1.0 — Mai 2026 — Première version stable

- Dialogue entre deux LLM avec rôles asymétriques (Investigateur / Analyste)
- Thèmes secondaires guidés, mémoire à fenêtre glissante, détection de dérive linguistique
- Synthèse vocale SAPI5 deux voix avec synchronisation dialogue/voix
- Déblocage des voix OneCore Windows 10/11
- Export JSON / Markdown / RTF
- Configuration persistante avec offuscation des clés API
- Support Ollama local et cloud

---
### NOUVEAU d-IA lite Pour ANDROID
<div>
  <img src="android/images/dia_android_mainscreen.jpg" alt="d-IA Android main screen" width="640">
</div>
[*d-IA Light Android*](https://github.com/f1gbd/F1GBD/tree/master/dia)
---

<div align="center">

### 📡 Auteur

**Jean-Louis (F1GBD)**
*ADRASEC 77 — FNRASEC*

**Version 1.2 — 2026**

---

*Pour toute question, contactez votre référent ADRASEC départemental.*

🤖 **d-IA v1.2** — *Deux IA cherchent, un troisième arbitre et fait converger. Vos sujets de recherche aboutissent à une solution.*

</div>
