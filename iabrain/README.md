<div align="center">

<img src="IAbrain_logo.png" alt="IAbrain" width="200">

# IAbrain

### L'assistant IA local pour les opérateurs ADRASEC

*Communications résilientes — Documentation opérationnelle — Rédaction de SITREP*

[![Version](https://img.shields.io/github/v/release/f1gbd/F1GBD?label=version&color=blue)](https://github.com/f1gbd/F1GBD/releases/latest)
[![Téléchargements](https://img.shields.io/github/downloads/f1gbd/F1GBD/total?label=téléchargements&color=brightgreen)](https://github.com/f1gbd/F1GBD/releases)
[![Plateforme](https://img.shields.io/badge/plateforme-Windows%2010%2F11-lightgrey.svg)]()
[![Licence](https://img.shields.io/badge/usage-ADRASEC%2FFNRASEC-green.svg)]()
[![100% local](https://img.shields.io/badge/100%25-local-brightgreen.svg)]()

### 📥 [**Télécharger la dernière version**](https://github.com/f1gbd/F1GBD/releases/latest/download/IAbrain.7z)

</div>

---

## 🎯 Qu'est-ce qu'IAbrain ?

**IAbrain** est un assistant intelligent qui tourne **entièrement sur votre ordinateur personnel**, sans aucune dépendance à Internet ou à des services cloud externes. Il combine deux technologies modernes pour vous offrir une aide concrète au quotidien :

- 🤖 **Un modèle de langage local (LLM)** qui comprend vos questions en français et rédige des réponses claires.
- 📚 **Une base de connaissances ADRASEC indexée intelligemment (RAG)** qui permet à IAbrain de s'appuyer sur les notes techniques, MEMO, fiches réflexes et SITREP officiels pour répondre avec précision.

Concrètement, c'est un outil qui répond à vos questions opérationnelles, rédige des documents administratifs ou techniques, vous aide à configurer un poste radio, à comprendre un protocole, à réviser pour un examen ou un exercice — tout cela depuis votre laptop, en quelques secondes, et **sans qu'aucune information ne quitte votre machine**.

---

## ⭐ Fonctionnalités principales

| Icône | Fonctionnalité | Description |
|:---:|---|---|
| 💬 | **Conversation en français naturel** | Posez vos questions comme à un collègue expérimenté. IAbrain comprend votre demande, raisonne, et répond de manière structurée. Pas de syntaxe technique à apprendre. |
| 📚 | **Base de connaissances ADRASEC intégrée** | Toutes les notes techniques, MEMO, fiches réflexes et SITREP sont indexés et consultables. IAbrain cite ses sources et indique de quel document provient chaque information. |
| ⚡ | **Routage automatique entre modèles** | IAbrain choisit automatiquement entre un modèle rapide (questions simples) et un modèle puissant (analyses complexes). Réponses immédiates pour le quotidien, qualité maximale quand c'est nécessaire. |
| 🎯 | **Reranking RAG intelligent** | Pipeline en 2 étapes (embedding + reranking via bge-m3) pour une pertinence maximale des sources citées. Détection automatique des modèles disponibles. |
| ⚙️ | **Paramètres RAG exposés** *(v1.33.3+)* | Cinq paramètres avancés (top_k, seuil similarité, recherche hybride, poids lexical, taille contexte) configurables directement dans Options → Paramètres, sans éditer le JSON. |
| 📝 | **Rédaction de documents structurés** | Génère des SITREP, fiches techniques, procédures et notes en quelques secondes. Bouton dédié pour exporter directement en fichier Markdown réutilisable. |
| 🔄 | **Mise à jour OTA depuis GitHub** | La base de connaissances ADRASEC se met à jour d'un seul clic depuis ce dépôt officiel. Tous les opérateurs disposent de la même version à jour, vérifiée par signature SHA-256. |
| 🆕 | **Vérification automatique des MAJ** *(v1.33.5+)* | Au démarrage, IAbrain vérifie discrètement si une nouvelle version est disponible sur GitHub et notifie l'utilisateur dans la zone de chat. Asynchrone, échec silencieux si pas d'Internet, désactivable. |
| 🔒 | **100% local et confidentiel** | Aucune donnée ne sort de votre machine. Aucune connexion Internet requise après installation. Idéal pour les contextes opérationnels sensibles ou les zones blanches. |

---

## 🚀 Pourquoi un opérateur ADRASEC y gagne

> **Gain de temps massif**
> Une question qui demandait 10 minutes de recherche dans les notes techniques obtient une réponse en 10 secondes.

> **Montée en compétence accélérée**
> Les nouveaux opérateurs accèdent immédiatement au savoir-faire consolidé de l'ADRASEC. Plus besoin d'attendre une formation pour savoir configurer un mode radio.

> **Cohérence des documents produits**
> SITREP, MEMO et fiches générés à partir de la même base partagée. Style et terminologie homogènes entre tous les opérateurs.

> **Disponibilité opérationnelle**
> Outil utilisable en exercice, en mission, en astreinte. Fonctionne même quand le réseau ADRASEC est isolé ou que l'électricité est coupée (sur batterie laptop).

> **Préservation du savoir collectif**
> Les RETEX, procédures locales et MEMO d'exercices passés restent consultables même si leur auteur n'est plus joignable. La connaissance ADRASEC se transmet par la base, pas par les personnes.

> **Confidentialité totale**
> Aucune trace ailleurs que sur votre poste. Pas d'historique sur des serveurs externes. Pas de question opérationnelle qui fuite vers une IA américaine ou chinoise.

---

## 💼 Cas d'usage concrets

Voici quelques exemples de ce que vous pouvez demander à IAbrain au quotidien.

### 🎓 Préparation d'exercice

```
« Rédige un SITREP type pour l'exercice HELIOS sur scénario tempête solaire. »

« Quelles sont les fréquences VHF utilisées en exercice ADRASEC en Île-de-France ? »

« Donne-moi la procédure de configuration TCQ-BBS pour un exercice de niveau régional. »
```

### 📡 Configuration matérielle

```
« Comment configurer Reticulum sur un poste ADRASEC ? »

« Quels paramètres VARA-FM utiliser pour une liaison HF en bande basse ? »

« Mon Yaesu FT-991 ne reçoit plus correctement, quelles vérifications faire ? »
```

### 📖 Documentation et formation

```
« Explique-moi le fonctionnement du protocole packet AX.25 en termes simples. »

« Génère un cours de 20 minutes sur la goniométrie pour la recherche d'ELT. »

« Liste les fiches techniques qui mentionnent le mode FT8. »
```

### 🚨 Opérationnel

```
« Rédige un message radio standard pour une activation de plan ORSEC. »

« Quel est le rôle de l'ADRASEC dans une coupure électrique départementale ? »

« Donne-moi les indicatifs FNRASEC pour les liaisons inter-départementales. »
```

---

## 📊 Le quotidien d'un opérateur, avant et avec IAbrain

| Sans IAbrain | Avec IAbrain |
|---|---|
| **Recherche d'une procédure dans 30 PDF :** feuilleter les notes techniques, ouvrir plusieurs documents, lire en diagonale.<br>⏱ *Durée : 5 à 15 minutes.* | **Question en langage naturel :** « Comment configurer TCQ-BBS pour HELIOS ? »<br>⏱ *Réponse synthétique en 10 secondes avec les sources citées.* |
| **Rédaction d'un SITREP type :** partir d'une feuille blanche ou copier-coller un ancien.<br>⏱ *Durée : 30 à 60 minutes.* | **Demande à IAbrain :** « Rédige un SITREP pour exercice X »<br>⏱ *Document structuré généré en 30 secondes, à éditer puis exporter en .md.* |
| **Connaissance dispersée :** chaque opérateur a ses propres notes, niveaux d'expertise hétérogènes. | **Base de connaissances commune** mise à jour depuis GitHub d'un seul clic.<br>Tous les opérateurs au même niveau. |
| **Dépendance Internet et services cloud :** risque opérationnel en zone blanche ou pendant un incident électrique. | **100% local, hors ligne, confidentiel.** Fonctionne en exercice ou opération réelle sans aucune connexion externe. |

---

## 👥 Pour qui est conçu IAbrain ?

IAbrain s'adresse à **tous les opérateurs ADRASEC**, quels que soient leur niveau d'expérience et leurs missions :

- 🆕 Le **nouvel opérateur** qui découvre les procédures et le matériel
- 🎯 L'**opérateur expérimenté** qui veut accéder rapidement à une référence
- 👨‍🏫 Le **formateur** qui prépare un cours ou une session d'exercice
- 📋 Le **responsable de section** qui doit rédiger un SITREP ou un RETEX
- 📡 L'**opérateur de terrain** en mission, qui a besoin d'une réponse rapide loin du QG
- 🌙 L'**opérateur d'astreinte** qui révise une procédure spécifique

---

## 🛠 Comment commencer ?

### ⚡ Méthode automatique *(recommandée — Nouveauté v1.33)*

Depuis la v1.33, un script PowerShell **fait toute l'installation pour vous** : Ollama, modèles, IAbrain, variables d'environnement, raccourcis bureau et menu Démarrer. Une seule commande à lancer, environ 30 minutes en arrière-plan.

**1. Téléchargez le script** `Install-IAbrain.ps1` depuis ce dépôt.

**2. Ouvrez PowerShell en mode administrateur** (clic droit → « Exécuter en tant qu'administrateur »).

**3. Lancez le script** :

```powershell
# Naviguer vers le dossier de téléchargement
cd $env:USERPROFILE\Downloads

# Autoriser l'exécution du script (cette session uniquement)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

# Lancer l'installation automatique
.\Install-IAbrain.ps1
```

Le script affiche sa progression phase par phase et vous prévient quand l'installation est terminée. Pendant les 25 minutes de téléchargement des modèles, vous pouvez faire autre chose : le script tourne sans surveillance.

> 💡 **Astuce** : la procédure détaillée est dans le **« Guide d'installation IAbrain v1.33.6 »** livré séparément. Il inclut aussi la procédure manuelle pas-à-pas en annexe pour les utilisateurs avancés.

### 🛠 Méthode manuelle *(utilisateurs avancés)*

Si vous préférez maîtriser chaque étape (postes non-Windows, contraintes IT particulières, formation), la méthode manuelle pas-à-pas est documentée en annexe du guide d'installation.

**Vérification rapide des prérequis** :

> **Configuration minimale** : Windows 10/11, Ryzen 5+ ou Intel i5+, 16 Go RAM (32 Go recommandés en dual-channel)
>
> **Configuration de référence light** : Mini-PC type Geekom A7Max, Beelink SER8, ou équivalent Ryzen 7000+ avec 32 Go DDR5 dual-channel.

**Modèles à installer manuellement** :

```powershell
# Sur le serveur Ollama (HX99G ou A7Max)
ollama pull nomic-embed-text    # Embedder RAG (obligatoire, 274 Mo)
ollama pull llama3.2:3b         # Modèle léger (auto-route, 2 Go)
ollama pull qwen2.5:7b          # Modèle complexe (RAG + analyse, 4.7 Go)
ollama pull bge-m3              # Reranking RAG (recommandé, 1.2 Go)
```

**Téléchargement direct de l'archive** :

<div align="center">

#### 📥 [**Télécharger IAbrain.7z**](https://github.com/f1gbd/F1GBD/releases/latest/download/IAbrain.7z)

*(toujours la dernière version stable)*

[![Voir toutes les versions](https://img.shields.io/badge/📜_Voir_toutes_les_versions-Releases-blue)](https://github.com/f1gbd/F1GBD/releases)

</div>

Une fois téléchargé :

```powershell
# 1. Décompresser l'archive IAbrain.7z dans C:\
#    (clic droit → 7-Zip → Extraire vers "C:\")
#
# 2. Ouvrir l'Explorateur dans C:\IAbrain\
#
# 3. Double-cliquer sur IAbrain.exe pour lancer le programme
```

> 💡 **Astuce** : créez un raccourci de `IAbrain.exe` sur votre bureau pour un lancement rapide au quotidien.

### 🚀 Première utilisation

Une fois IAbrain installé et lancé :

1. **Menu Connaissances → 🔄 Mettre à jour la base depuis GitHub** *(récupère les 182 fichiers, 2092 chunks de la base ADRASEC officielle)*
2. **Options → Paramètres → cocher « Activer le RAG »** *(case en haut de la section « Paramètres RAG »)*
3. Posez votre première question : **« Parle-moi du logiciel TCQ »**

> ⏱ Comptez environ **30 minutes** pour la première installation, ensuite IAbrain est utilisable au quotidien sans configuration supplémentaire.

---

## 📚 Documentation complète

Ce dépôt contient également les manuels suivants :

- 📋 **Fiche de présentation v1.33.6**
- 📖 **Guide d'installation IAbrain v1.33.6** *(méthode automatique + annexe manuelle)*
- 📘 **Manuel utilisateur IAbrain v1.33.6** *(complet, 21 pages)*
- 🔧 **Prérequis matériel utilisateur**
- 🎯 **Procédure d'activation du reranking RAG**
- 📊 **Synthèse benchmark de modèles**

---

## 🌐 Architecture technique

```
┌────────────────────────────────────────┐
│  IAbrain (interface graphique)         │
│  - Conversation, RAG, export Markdown  │
│  - Vérification automatique des MAJ    │
└──────────────┬─────────────────────────┘
               │ HTTP localhost:11434
┌──────────────▼─────────────────────────┐
│  Ollama (moteur d'inférence local)     │
│  - llama3.2:3b (questions simples)     │
│  - qwen2.5:7b (questions complexes)    │
│  - nomic-embed-text (RAG embedder)     │
│  - bge-m3 (reranking)                  │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│  Base RAG ADRASEC (locale)             │
│  - 182 fichiers indexés                │
│  - 2092 chunks vectorisés              │
│  - Mise à jour OTA depuis GitHub       │
└────────────────────────────────────────┘
```

---

## 🆕 Nouveautés v1.33.x

La branche 1.33 apporte plusieurs améliorations majeures, listées chronologiquement :

| Version | Apport principal |
|---|---|
| **1.33.0** | Architecture reranking RAG via bge-m3 (qualité des réponses ×2) |
| 1.33.1 | Hotfix nom du modèle reranker (bge-m3 au lieu de bge-reranker-v2-m3) |
| 1.33.2 | Filtre embedders dans le sélecteur de modèles |
| **1.33.3** | Paramètres RAG exposés dans l'UI + min_similarity 0.30 + qwen2.5:7b par défaut |
| 1.33.4 | Case « Activer le RAG » bien en évidence dans Options → Paramètres |
| **1.33.5** | Vérification automatique des mises à jour GitHub au démarrage |
| 1.33.6 | Fenêtres Paramètres et À propos compactes (compatible petits écrans) |

Pour le détail des changements, consultez le [changelog complet sur GitHub Releases](https://github.com/f1gbd/F1GBD/releases).

---

## 🤝 Communauté

IAbrain est un **projet open développé pour la communauté ADRASEC**, proposé librement aux opérateurs ADRASEC départementales et à la FNRASEC.

Toute contribution, retour d'expérience ou proposition d'amélioration est bienvenue via les *Issues* du dépôt GitHub.

---

<div align="center">

### 📡 Auteur

**Jean-Louis (F1GBD / F4JHW)**
*ADRASEC 77 — FNRASEC*

**Version 1.33.6 — 2026-04-28**

---

*Pour toute question, contactez votre référent ADRASEC départemental.*

🧠 **IAbrain** — *L'intelligence artificielle au service de la sécurité civile*

</div>
