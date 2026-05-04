<div align="center">

<img src="IAbrain_logo.png" alt="IAbrain" width="200">

# IAbrain

### L'assistant IA local pour les opérateurs ADRASEC

*Communications résilientes — Documentation opérationnelle — Rédaction de SITREP — Cartographie interactive — Corrections manuelles — Macros et actions natives — Connectivité Ollama Cloud — Mémoire conversationnelle — Profil opérateur — Variables de session — Pipeline SATER complet*

[![Version](https://img.shields.io/badge/version-iabrain--v1.40.3-blue)](https://github.com/f1gbd/F1GBD/releases/tag/iabrain-v1.40.3)
[![Téléchargements](https://img.shields.io/badge/téléchargements-100%2B-brightgreen?logo=github)](https://github.com/f1gbd/F1GBD/releases)
[![Plateforme](https://img.shields.io/badge/plateforme-Windows%2010%2F11-lightgrey.svg)]()
[![Licence](https://img.shields.io/badge/usage-ADRASEC%2FFNRASEC-green.svg)]()
[![100% local](https://img.shields.io/badge/local%20%2F%20cloud-hybride-brightgreen.svg)]()

### 📥 [**Télécharger la dernière version**](https://github.com/f1gbd/F1GBD/releases/download/iabrain-v1.40.3/IAbrain.7z)

</div>

---

## 📸 Aperçu

<div align="center">

### Écran principal d'IAbrain

<img src="docs/images/main_screen.png" alt="Écran principal IAbrain" width="900">

*Interface conversationnelle avec routage automatique entre modèles, RAG ADRASEC intégré, macros utilisateur, rendu Markdown complet, corrections manuelles et thème clair/sombre.*

### Cartographie interactive de la base RAG *(v1.35)*

<img src="docs/images/cartographie.png" alt="Cartographie interactive" width="900">

*Visualisation arborescente de la base de connaissances : Base → Cluster thématique → Fichier → Chunk, fonctionne 100% hors-ligne.*

</div>

---

## 🎯 Qu'est-ce qu'IAbrain ?

**IAbrain** est un assistant intelligent qui tourne **entièrement sur votre ordinateur personnel**, sans aucune dépendance à Internet ou à des services cloud externes. Il combine plusieurs technologies modernes pour vous offrir une aide concrète au quotidien :

- 🤖 **Un modèle de langage local (LLM)** qui comprend vos questions en français et rédige des réponses claires.
- 📚 **Une base de connaissances ADRASEC indexée intelligemment (RAG)** qui permet à IAbrain de s'appuyer sur les notes techniques, MEMO, fiches réflexes et SITREP officiels pour répondre avec précision.
- ⚙️ **Des macros et actions natives** *(v1.37+)* pour automatiser vos tâches récurrentes : conversion CSV→Markdown, extraction d'indicatifs, anonymisation, le tout sans solliciter le LLM.

Concrètement, c'est un outil qui répond à vos questions opérationnelles, rédige des documents administratifs ou techniques, vous aide à configurer un poste radio, à comprendre un protocole, à réviser pour un examen ou un exercice, et qui automatise les transformations de fichiers — tout cela depuis votre laptop, en quelques secondes, et **sans qu'aucune information ne quitte votre machine**.

---

## ⭐ Fonctionnalités principales

| Icône | Fonctionnalité | Description |
|:---:|---|---|
| 💬 | **Conversation en français naturel** | Posez vos questions comme à un collègue expérimenté. IAbrain comprend votre demande, raisonne, et répond de manière structurée. Pas de syntaxe technique à apprendre. |
| 📚 | **Base de connaissances ADRASEC intégrée** | Toutes les notes techniques, MEMO, fiches réflexes et SITREP sont indexés et consultables. IAbrain cite ses sources et indique de quel document provient chaque information. |
| 📂 | **Base RAG personnelle** *(v1.34+)* | En plus de la base ADRASEC officielle (alimentée par OTA), une **seconde base perso** isolée vous permet d'indexer vos propres notes, RETEX et documents locaux. Les deux bases sont fouillées simultanément ; la base perso est **toujours préservée** lors des mises à jour OTA. |
| 🌐 | **Cartographie interactive de la base** *(v1.35+)* | Visualisation arborescente de la base RAG (Base → Cluster thématique → Fichier → Chunk). Force-directed dynamique style Reticulum MeshChat, embarqué 100% hors-ligne dans un fichier HTML autonome. Recherche temps réel avec auto-expand des branches pertinentes et surlignage des chunks matchant. |
| 📢 | **Corrections manuelles intégrées** *(v1.36+)* | Quand IAbrain produit une réponse imprécise ou incorrecte, **clic-droit → « 📢 Corriger cette réponse »** suffit. Votre correction est indexée dans la base perso et **automatiquement appliquée aux questions similaires futures, en priorité absolue**. Format Markdown versionable, partageable entre opérateurs via export/import ZIP. |
| 🆕 | **Macros utilisateur** *(v1.37+)* | 8 boutons configurables au-dessus de la liste des fichiers pour automatiser vos tâches récurrentes. Deux types : **🤖 Macro LLM** (envoie un prompt à l'IA, avec méta-langage `{{lastfile}}`, `{{date}}`, `{{call}}`...) et **⚙️ Macro Action** (exécute une fonction native déterministe, sans LLM). |
| ⚙️ | **5 actions natives livrées** *(v1.37.7+)* | `csv_to_markdown` (conversion CSV ↔ tableaux Markdown), `extract_callsigns` (extrait F1XYZ/TM/TK/TO/FW), `extract_frequencies` (Hz/kHz/MHz/GHz par bande), `anonymize` (téléphones/emails/adresses), `file_stats` (statistiques fichiers). 100% offline, instantané, déterministe, zéro hallucination. |
| 📤 | **Import/Export de macros** *(v1.40.1+)* | Deux nouveaux boutons **📥 Importer une Macro** et **📤 Exporter la Macro** dans le dialogue d'édition. Format `.iabmacro` (JSON UTF-8 versionable) qui permet de partager des macros entre opérateurs ADRASEC. Idéal pour distribuer des macros standardisées dans une section, archiver des versions de travail, ou récupérer une macro depuis un autre poste. |
| 🔖 | **Variables de session persistantes** *(v1.40.2+)* | Permet de **chaîner des macros** : une macro LLM produit un bloc structuré `###IABRAIN_VARS###` qu'IAbrain capture silencieusement, puis ces variables sont substituables dans tout prompt suivant via la syntaxe `{LAT}`, `{LON}`, etc. Persistance disque entre sessions. Indicateur cliquable « 🔖 Vars (n) » dans la barre du haut pour inspecter/éditer/effacer manuellement. Cas d'usage typique : analyse SATER en deux temps (calcul de position via LLM + génération de carte OSM via macro action). |
| 🎯 | **Pipeline SATER complet** *(v1.40.3+)* | Action native `osm_balise_map` qui lit les variables de session **LAT**, **LON**, **RAYON_M** et génère un **vrai PNG OpenStreetMap** centré sur la balise ELT avec marqueur, cercle d'incertitude CEP 95 et cartouche complet (position DMS + décimal + horodatage). **Image affichée directement dans le chat IAbrain** + sauvegardée dans `IAbrain_sater_maps/` pour archivage opérationnel. Combinée à la macro SATER LOC, elle ferme la boucle d'analyse SATER en deux clics : du CSV de relèvements TCQ à la carte exploitable. |
| 📝 | **Rendu Markdown complet dans le chat** *(v1.37+)* | Les réponses de l'IA sont rendues visuellement : titres, gras, italique, tableaux pipe-style avec colonnes alignées, citations, listes, **cases à cocher** (`- [ ]`/`- [x]`), liens cliquables, séparateurs, code inline et blocs de code. |
| 🌍 | **Détection auto d'encodage à l'import** *(v1.37.8+)* | Détecte automatiquement UTF-8, UTF-8 BOM, UTF-16, CP1252 (Windows-1252 français), ISO-8859-15 et ISO-8859-1. Les CSV exportés depuis Excel français sont enfin lus correctement, sans `◇` à la place des accents. |
| ☁ | **Connectivité Ollama Cloud** *(v1.38.0+)* | Accès aux grands modèles XL hébergés (gpt-oss:20b, gpt-oss:120b, deepseek-v3.1:671b…) sans avoir à les exécuter localement. Idéal pour démos sur petites machines, tests ponctuels, formations. Deux modes : direct (appel ollama.com) ou proxy local (via `ollama signin`). L'embedder RAG reste **toujours local** pour préserver la confidentialité de la base. |
| 🧠 | **Mémoire conversationnelle persistante** *(v1.39.0+)* | IAbrain apprend des conversations au fil de l'usage. Quand l'utilisateur dit « **Souviens-toi** » ou « **Rappelle-toi** » (ou clique sur le bouton « 🧠 Se souvenir » sous une réponse), la conversation est sauvegardée dans la base RAG perso et indexée automatiquement. Les futures questions bénéficient de cette mémoire enrichie. Reprise de conversation possible via le menu dédié. *(v1.39.1+)* : édition avant mémorisation pour garantir la qualité de la base. |
| 👤 | **Profil opérateur déclaratif** *(v1.40.0+)* | IAbrain peut connaître qui est l'opérateur dès le premier mot : indicatif, département ADRASEC, niveau d'expertise, spécialités radio, préférences de format. Permet l'accueil personnalisé (« Bonjour F1GBD, je suis IAbrain. Nous sommes le 3 mai 2026 et il est 08h30 ») et l'adaptation des réponses au niveau déclaré (débutant pédagogique vs expert direct). Édité via Options → Profil opérateur, opt-in, strictement local. |
| ⚡ | **Routage automatique entre modèles** | IAbrain choisit automatiquement entre un modèle rapide (questions simples) et un modèle puissant (analyses complexes). Réponses immédiates pour le quotidien, qualité maximale quand c'est nécessaire. |
| 🎯 | **Reranking RAG intelligent** | Pipeline en 2 étapes (embedding + reranking via bge-m3) pour une pertinence maximale des sources citées. Détection automatique des modèles disponibles. |
| ⚙️ | **Paramètres RAG exposés** *(v1.33.3+)* | Cinq paramètres avancés (top_k, seuil similarité, recherche hybride, poids lexical, taille contexte) configurables directement dans Options → Paramètres, sans éditer le JSON. |
| 📊 | **`num_ctx` adaptatif** *(v1.37.4+)* | IAbrain augmente automatiquement la fenêtre de contexte Ollama (4096 → 8192 → 16384 → 32768) quand le prompt enrichi par le RAG dépasserait 40% de la taille configurée. Évite les réponses tronquées sur les requêtes longues. |
| 📝 | **Rédaction de documents structurés** | Génère des SITREP, fiches techniques, procédures et notes en quelques secondes. Bouton « 💾 Enregistrer » dédié pour exporter directement en **Markdown** (réutilisable, archivable) ou **RTF** *(v1.38.3+, ouvrable directement dans Word, WordPad, LibreOffice — idéal pour échanges avec les autorités)*. |
| 🔄 | **Mise à jour OTA depuis GitHub** | La base de connaissances ADRASEC se met à jour d'un seul clic depuis ce dépôt officiel. Tous les opérateurs disposent de la même version à jour, vérifiée par signature SHA-256. La base perso (v1.34+) n'est jamais écrasée. |
| 🔔 | **Vérification automatique des MAJ** *(v1.33.5+)* | Au démarrage, IAbrain vérifie discrètement si une nouvelle version est disponible sur GitHub et notifie l'utilisateur dans la zone de chat. Asynchrone, échec silencieux si pas d'Internet, désactivable. |
| 🔒 | **100% local et confidentiel** | Aucune donnée ne sort de votre machine. Aucune connexion Internet requise après installation. Idéal pour les contextes opérationnels sensibles ou les zones blanches. |

---

## 🚀 Pourquoi un opérateur ADRASEC y gagne

> **Gain de temps massif**
> Une question qui demandait 10 minutes de recherche dans les notes techniques obtient une réponse en 10 secondes. Une conversion de bilan opérationnel CSV en tableaux Markdown se fait en moins d'une seconde via la macro `⚙ CSV To MD`.

> **Apprentissage continu de l'IA** *(v1.36+)*
> Quand IAbrain se trompe sur une fréquence, un acronyme ou une procédure locale, vous le corrigez en deux clics. La correction est appliquée pour toujours, et elle peut être partagée avec toute votre section ADRASEC via un fichier ZIP.

> **Automatisation des tâches répétitives** *(v1.37+)*
> Configurez un bouton macro pour vos cas d'usage récurrents : « Résume ce SITREP en 5 puces », « Extrait tous les indicatifs de ce log », « Anonymise ce rapport avant diffusion ». Un clic suffit.

> **Chaînage de macros pour pipelines opérationnels** *(v1.40.2+)*
> Une macro qui calcule (par exemple, une localisation de balise ELT par triangulation à partir d'un CSV de relèvements TCQ) peut désormais transmettre son résultat à la macro suivante via des **variables de session**. Plus besoin de copier-coller manuellement les coordonnées entre étapes : `{LAT}`, `{LON}`, `{RAYON_M}` sont substituées automatiquement. Et puisque les variables persistent entre sessions, vous retrouvez vos derniers calculs au démarrage suivant.

> **Partage de macros entre opérateurs** *(v1.40.1+)*
> Les macros utilisateur sont désormais exportables au format `.iabmacro` et réimportables sur un autre poste. Idéal pour distribuer des macros validées au sein d'une section ADRASEC, ou pour archiver une macro de travail avant modification.

> **Démos et formations sur petites machines** *(v1.38+)*
> Lancez IAbrain sur un laptop entrée de gamme ou une tablette, et exploitez les modèles XL (gpt-oss:120b, deepseek-v3.1:671b…) hébergés par Ollama Cloud pour montrer le meilleur de ce qu'IAbrain peut faire. La base ADRASEC reste sur votre machine ; seul le LLM tourne dans le cloud.

> **Montée en compétence accélérée**
> Les nouveaux opérateurs accèdent immédiatement au savoir-faire consolidé de l'ADRASEC. Plus besoin d'attendre une formation pour savoir configurer un mode radio.

> **Cohérence des documents produits**
> SITREP, MEMO et fiches générés à partir de la même base partagée. Style et terminologie homogènes entre tous les opérateurs.

> **Disponibilité opérationnelle**
> Outil utilisable en exercice, en mission, en astreinte. Fonctionne même quand le réseau ADRASEC est isolé ou que l'électricité est coupée (sur batterie laptop). Les actions natives fonctionnent même si Ollama est arrêté.

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

### ⚙️ Automatisation via macros Action *(v1.37.7+)*

```
1. Importer un fichier CSV (ex: bilan opérationnel exporté depuis Excel)
2. Cliquer sur le bouton ⚙ CSV To MD (pré-installé en macro 1)
3. Conversion instantanée en tableaux Markdown structurés, 100% offline, 0 hallucination
```

D'autres actions disponibles via clic-droit sur un bouton de macro vide :

- 📡 **Extraire les indicatifs radio** d'un log ou d'un radiogramme (F1XYZ, TM/TK/TO/FW)
- 📻 **Extraire les fréquences** classées par bande (HF/VHF/UHF/SHF)
- 🔒 **Anonymiser** un rapport (téléphones, emails, adresses postales → balises `<TELEPHONE>`, etc.)
- 📈 **Statistiques** sur les fichiers importés

### 🎯 Pipeline SATER : localisation de balise ELT en deux clics *(v1.40.2 + v1.40.3)*

Le pipeline SATER complet d'IAbrain combine la **macro LLM `SATER LOC`** (calcul de la position par triangulation, v1.40.2) et l'**action native `SATER MAP PNG`** (génération de carte OSM, v1.40.3) pour passer du CSV de relèvements goniométriques à la carte exploitable en quelques secondes.

#### Étape 1 — Macro LLM `SATER LOC` (analyse + capture)

```
1. Importer le CSV de relèvements (Indicatif ; Lat ; Lon ; Azimut ; Date_Heure)
   exporté par la cartographie TCQ.
2. Cliquer sur la macro « 🎯 SATER LOC ».
3. IAbrain calcule la triangulation pondérée (moindres carrés sur les LOB,
   rejet des outliers, ellipse d'erreur), produit un SITREP au format ADRASEC,
   et capture silencieusement les variables suivantes :
       LAT=48.429167
       LON=3.291944
       RAYON_M=280
       INDICATIF_BALISE=BALISE ELT
       SITREP_TS=2026-05-04 13:42
4. L'indicateur en haut à droite affiche : 🔖 Vars (5) : LAT, LON, RAYON_M, +2
```

#### Étape 2 — Action native `SATER MAP PNG` (carte automatique)

```
1. Cliquer sur la macro « 🗺 SATER MAP PNG ».
2. IAbrain :
   - lit les variables de session capturées à l'étape 1
   - télécharge les tuiles OpenStreetMap centrées sur la balise
   - dessine le marqueur, le cercle d'incertitude CEP 95
   - ajoute le cartouche (position DMS + décimal + horodatage)
   - sauvegarde le PNG dans IAbrain_sater_maps/
   - affiche l'image directement dans le chat
3. La réponse contient également des liens cliquables vers OSM, Géoportail
   et Google Maps en complément.
```

**Exemple de carte produite par la macro `SATER MAP PNG`** (rendu réel sur la balise du CSV de test, position 48°25'45"N 003°17'31"E, rayon CEP 95 ± 280 m) :

<div align="center">

<img src="docs/images/sater_map_png_exemple.png" alt="Exemple de carte SATER MAP PNG" width="800">

*Marqueur rouge SAR, cercle d'incertitude CEP 95 (280 m de rayon), cartouche avec position DMS et décimale, horodatage du calcul, attribution OpenStreetMap et échelle.*

</div>

#### Bénéfice opérationnel

Avant la v1.40.3, l'opérateur devait :

1. Calculer manuellement la triangulation (calculatrice ou tableur)
2. Recopier les coordonnées dans un service cartographique web
3. Capturer une copie d'écran pour le SITREP
4. Sauvegarder le tout à part

**Avec le pipeline SATER complet, ces 4 étapes manuelles deviennent 2 clics**. Le PNG est immédiatement utilisable dans un SITREP, un mail à la chaîne de commandement, ou comme support de débrief d'exercice. Et puisque les variables persistent sur disque, on peut reprendre l'analyse plusieurs jours plus tard sans rien retaper.

> 💡 **Variantes possibles** : avec le système de variables de session, on peut intercaler entre `SATER LOC` et `SATER MAP PNG` un message de chat libre du type « *Reformule le SITREP pour la chaîne préfectorale en 4 lignes* », ou un appel à une macro tierce qui exploite `{LAT}`, `{LON}`, `{INDICATIF_BALISE}` pour générer un fichier KML, un point APRS, un message Winlink, etc.

### 📤 Partager une macro entre opérateurs *(v1.40.1+)*

```
1. Clic-droit sur le bouton macro à partager → ouvre l'éditeur
2. Cliquer sur « 📤 Exporter la Macro » → fichier .iabmacro généré
3. Transmettre le fichier au collègue (mail, clé USB, partage ADRASEC)
4. Côté destinataire : clic-droit sur un bouton vide → « 📥 Importer une Macro »
5. Sélectionner le fichier reçu, vérifier le contenu, cliquer sur Enregistrer
```

Le format `.iabmacro` est un simple JSON UTF-8 versionable, lisible et auditable. Idéal pour distribuer des macros validées dans une section, ou versionner ses propres macros via un dossier Git/Synology/Dropbox.

### 🌐 Exploration de la base RAG *(v1.35+)*

```
Menu : Connaissances → 🌐 Cartographie interactive de la base…
```

Ouvre la cartographie dans votre navigateur. **Au démarrage** : vue d'ensemble en 5-8 clusters thématiques (VARA, TCQ, SATER, ADRASEC, etc.) auto-détectés par k-means.

**Cliquez sur un cluster** pour voir ses fichiers, **cliquez sur un fichier** pour voir ses extraits, **cliquez sur un extrait** pour afficher son contenu intégral dans le panneau latéral.

**Saisissez une requête** dans la barre de recherche (ex. « VARA HF Winlink ») : l'arbre se déplie automatiquement pour révéler les chunks pertinents, qui sont surlignés en rouge vif.

> 💡 Idéal pour préparer un exercice : visualisez d'un coup d'œil tout ce que la base sait sur un thème donné.

### 📢 Corrections manuelles *(v1.36+)*

```
1. Posez votre question : « Quelle est la fréquence VHF ADRASEC en Île-de-France ? »
2. IAbrain répond, mais vous remarquez qu'il manque la fréquence du transpondeur F5ZYI
3. Clic-droit sur la réponse → « 📢 Corriger cette réponse… »
4. Saisissez la bonne réponse : « 145.4375 MHz CTCSS 77.0 Hz et 430.4375 MHz pour le transpondeur F5ZYI ADRASEC 77 IDF »
5. Validez. La correction est immédiatement indexée.
6. Reposez la même question : IAbrain donne désormais la réponse correcte avec attribution explicite (« Selon une correction validée par F1GBD… »)
```

Toutes vos corrections sont consultables et gérables dans `Connaissances → 📢 Gérer les corrections manuelles…`. Vous pouvez les exporter en ZIP pour les partager avec votre section, ou en importer venant d'autres opérateurs.

> 💡 Particulièrement utile pour les **valeurs spécifiques à votre département** (fréquences locales, indicatifs, procédures internes) que la base officielle ADRASEC ne peut pas connaître.

### ☁ Démos et tests avec modèles XL via Ollama Cloud *(v1.38.0+)*

```
1. Options → Paramètres → cocher « Activer l'accès aux modèles Ollama Cloud »
2. Saisir l'API key (ou définir OLLAMA_API_KEY dans l'environnement)
3. Cliquer sur « 🔌 Tester la connexion cloud » pour vérifier
4. Sélectionner ☁ gpt-oss:120b dans la liste des modèles
5. Poser des questions à un modèle 120B sans avoir de GPU 80 Go en local
```

Particulièrement utile pour :

- 💻 **Démos terrain** sur Surface Pro, mini-PC, laptop entrée de gamme : montrer la qualité d'un modèle XL devant un public ADRASEC sans matériel haut de gamme
- 🎓 **Formations** : présenter le meilleur de ce qu'IAbrain peut faire à des opérateurs qui n'ont pas encore investi dans du matériel adapté
- 🧪 **Tests ponctuels** d'un nouveau modèle avant décision de téléchargement local
- 📊 **Comparaisons qualitatives** : poser la même question à qwen2.5:7b local vs gpt-oss:120b cloud pour évaluer l'écart

> 🔒 **Confidentialité préservée** : la base RAG ADRASEC, vos corrections manuelles et l'embedder restent **strictement locaux**. Seul le prompt de chat (et le contenu des fichiers que vous importez intentionnellement) transite vers ollama.com en mode cloud direct. Un avertissement explicite est posté dans le chat à chaque activation.

---

## 🆕 Macros et actions natives *(v1.37+)*

IAbrain dispose d'une **barre de 8 boutons macros** dans le panneau latéral, configurables individuellement. Chaque bouton peut être l'un des deux types :

### 🤖 Macros LLM — envoient un prompt à l'IA

Vous écrivez un prompt programmé qui peut contenir des **variables** automatiquement substituées :

| Méta-langage | Exemple |
|---|---|
| `{{lastfile}}` | Contenu du dernier fichier importé |
| `{{lastfilename}}` | Nom du dernier fichier importé |
| `{{allfiles}}` | Tous les fichiers importés concaténés |
| `{{filenames}}` | Liste des noms de fichiers |
| `{{date}}`, `{{time}}`, `{{utc}}` | Date/heure |
| `{{call}}` | Indicatif de l'opérateur (configurable) |
| `{{selection}}` | Texte sélectionné dans le chat |
| `{{file:nom.ext}}` | Contenu d'un fichier spécifique |
| `[fichier:nom.ext]`, `[dernier]`, `[date]`... | Alternative en crochets |
| `"nom.ext"` (auto) | Détection automatique d'un nom de fichier importé entre guillemets |

Cas d'usage typiques :
- **Résumé** : `Résume {{lastfile}} en 5 puces concises.`
- **SITREP daté** : `Rédige un SITREP daté du {{date}} à {{time}}, indicatif {{call}}, basé sur {{lastfile}}.`
- **Comparaison** : `Compare {{allfiles}} et liste les différences clés.`

Option **🚫 Désactiver le RAG pour cette macro** *(v1.37.6+)* : recommandée pour les transformations pures où le RAG ADRASEC ajoute du bruit non pertinent (résumé, traduction, anonymisation par LLM).

### ⚙️ Macros Action — exécutent une fonction native d'IAbrain

Pas de LLM, pas de prompt, pas de tokens. Une fonction Python interne d'IAbrain est appelée directement avec les fichiers importés. Résultat **instantané, 100% déterministe, 0 hallucination, fonctionne offline**.

5 actions natives livrées en v1.37.7+ :

| Action | Description |
|---|---|
| 📊 **csv_to_markdown** | Auto-détection délimiteur (`;` `,` `\t` `\|`), découpage en sections, filtrage colonnes vides, échappement pipes. Multi-tableaux dans un même fichier. |
| 📡 **extract_callsigns** | Indicatifs F[0-9][A-Z]{2,4}, TM, TK, TO, FW. Dédoublonnage et compte d'occurrences par fichier. |
| 📻 **extract_frequencies** | Hz, kHz, MHz, GHz (formats `145.4375 MHz` ou `145,4375 MHz`). Classement par bande HF/VHF/UHF/SHF. |
| 🔒 **anonymize** | Téléphones FR, emails, adresses postales (rue/avenue/...), code postal+ville → `<TELEPHONE>`, `<EMAIL>`, etc. |
| 📈 **file_stats** | Taille, lignes, mots, caractères. Total multi-fichiers. |

### 🎁 Macro pré-installée : `⚙ CSV To MD` *(v1.37.8+)*

Au premier lancement, le bouton **Macro 1** est déjà pré-programmé comme **`⚙ CSV To MD`** (action `csv_to_markdown`). Vous pouvez l'utiliser immédiatement :

1. **Importer un fichier CSV** (bilan opérationnel, log d'exercice, export Excel...)
2. **Cliquer sur `⚙ CSV To MD`** dans la barre des macros
3. **Conversion instantanée** en tableaux Markdown structurés, rendus visuellement dans le chat

Le préfixe **⚙** différencie visuellement les macros Action des macros LLM dans la barre.

> 💡 Pour configurer une macro : **clic-droit** sur un bouton vide → choisir le type (LLM ou Action) → renseigner les paramètres → Enregistrer.

### 📤 Import/Export de macros *(v1.40.1+)*

Le dialogue d'édition d'une macro contient deux nouveaux boutons :

| Bouton | Effet |
|---|---|
| **📥 Importer une Macro** | Ouvre un sélecteur de fichier `.iabmacro`, charge la macro dans les widgets de l'éditeur sans sauvegarder. L'opérateur peut relire/ajuster avant de cliquer sur Enregistrer pour valider. Demande confirmation si le slot n'est pas vide. |
| **📤 Exporter la Macro** | Exporte la macro telle qu'affichée dans le dialogue (même non sauvegardée), au format `.iabmacro`. Le nom de fichier proposé inclut le label de la macro et un horodatage. |

**Format `.iabmacro`** — JSON UTF-8 indenté, versionable :

```json
{
  "iabrain_macro_version": 1,
  "exported_at": "2026-05-04T13:10:00",
  "exported_by": "IAbrain 1.40.2",
  "macro": {
    "label": "🎯 Localiser balise SATER",
    "prompt": "Tu es un assistant SATER...",
    "rag_disabled": true,
    "type": "llm",
    "action": ""
  }
}
```

Le slot d'origine n'est **pas** sauvegardé dans le fichier — c'est volontaire : à l'import, l'opérateur choisit dans quel slot de destination la macro sera placée.

> 💡 **Cas d'usage typiques** : distribuer une macro standardisée à toute une section ADRASEC, archiver une macro de travail avant de la modifier, transférer ses macros vers un nouveau poste, partager une macro de démonstration en formation.

---

## 🔖 Variables de session persistantes *(v1.40.2+)*

Depuis la v1.40.2, IAbrain peut **chaîner des macros** via un mécanisme de variables capturées automatiquement depuis les réponses du LLM, puis substituables dans les prompts suivants. C'est l'aboutissement naturel du système de macros : ce qu'une macro calcule peut nourrir la macro suivante sans intervention manuelle.

### Principe de fonctionnement

1. **Une macro LLM produit un bloc structuré** à la fin de sa réponse :

```
###IABRAIN_VARS###
LAT=48.429167
LON=3.291944
RAYON_M=280
###END_IABRAIN_VARS###
```

2. **IAbrain capture silencieusement le bloc** : extraction des paires `KEY=VALUE`, suppression du bloc dans le chat (l'opérateur ne le voit pas), sauvegarde sur disque. Une notification système discrète confirme : « 🔖 3 variable(s) capturée(s) : LAT, LON, RAYON_M ».

3. **Les variables sont substituables dans tout prompt suivant** via la syntaxe `{NOM}` :

```
Avant envoi : « Génère une carte centrée sur {LAT}, {LON} rayon {RAYON_M}m »
Après substitution : « Génère une carte centrée sur 48.429167, 3.291944 rayon 280m »
```

La substitution est active aussi bien dans les prompts de macro que dans le chat libre.

### Indicateur cliquable et dialogue d'inspection

Un nouvel indicateur s'affiche en haut à droite, à côté du badge `📚 RAG` :

```
🔖 Vars : 0                          (aucune variable définie)
🔖 Vars (3) : LAT, LON, RAYON_M      (jusqu'à 3 noms affichés)
🔖 Vars (8) : LAT, LON, RAYON_M, +5  (au-delà de 3, compteur)
🔖 Vars : —                          (module indisponible)
```

**Un clic ouvre le dialogue « Variables de session »** qui permet :

- de visualiser toutes les variables actuelles (Treeview Nom | Valeur tronquée)
- d'éditer manuellement une valeur (ex : corriger une coordonnée)
- de supprimer une variable individuellement
- d'effacer toutes les variables d'un coup (bouton « 🧹 Tout effacer »)

### Conventions et règles

| Aspect | Règle |
|---|---|
| Nommage | `[A-Z][A-Z0-9_]*` (SHOUTING_SNAKE_CASE). Ex : `LAT`, `LON`, `RAYON_M`, `INDICATIF_BALISE`. Les autres formats sont rejetés silencieusement. |
| Échappement | `{{NOM}}` produit le littéral `{NOM}` dans le prompt envoyé (utile pour expliquer la syntaxe à l'IA). |
| Variable inconnue | `{INCONNUE}` est laissée telle quelle + warning système (ne casse pas le prompt). |
| Capacité | 64 variables max par session, 4 ko par valeur. |
| Persistance | Disque : `IAbrain_session_vars.json` à côté d'`IAbrain.json`. Restauré au démarrage. |
| Portée | Globale au programme, partagée entre toutes les conversations (≠ profil opérateur qui est statique). |

### Cas d'usage SATER : localisation de balise ELT

C'est l'usage prototype de la fonctionnalité, en deux étapes :

**Étape 1** — macro LLM `🎯 Localiser balise SATER` :

Le prompt programmé demande à l'IA d'analyser un CSV de relèvements goniométriques (export TCQ) et de produire un SITREP. À la fin du prompt, une instruction explicite demande :

```
À LA TOUTE FIN de ta réponse, ajoute un bloc structuré sur 3 lignes
strictement conforme à ce format, sans texte autour, sans backticks :

###IABRAIN_VARS###
LAT=xx.xxxxxx
LON=x.xxxxxx
RAYON_M=xxx
###END_IABRAIN_VARS###
```

**Étape 2** — chat libre ou macro 2 utilisant les variables :

```
« Génère une carte OSM PNG centrée sur {LAT}, {LON} avec un cercle
  d'incertitude de {RAYON_M}m. Joins l'image au chat. »
```

Le chaînage permet ainsi de séparer proprement le **calcul** (étape LLM, qualité de raisonnement) de l'**action** (étape déterministe, génération de carte). Et puisque les variables persistent sur disque, on peut reprendre l'analyse plusieurs jours plus tard.

### Garde-fous

> 🔇 **Capture silencieuse** — le bloc `###IABRAIN_VARS###` n'apparaît jamais dans l'export du chat ni dans la mémoire conversationnelle. Seule l'information utile (le SITREP, les coordonnées en DMS) est conservée pour l'opérateur.

> 🔒 **100% local** — les variables de session ne quittent jamais la machine, même en mode cloud Ollama (v1.38+). Elles sont traitées côté IAbrain avant tout envoi au LLM (substitution) et après réception (extraction).

> ✏ **Édition manuelle possible** — le dialogue Variables de session permet de corriger une valeur capturée incorrectement, ou de définir manuellement une variable pour l'utiliser dans un prompt sans passer par une macro LLM.

> 🧹 **Effacement à la demande** — bouton « 🧹 Tout effacer » dans le dialogue. Aucune purge automatique : c'est l'opérateur qui décide quand recommencer une session.

---

## 🗺 Action native `SATER MAP PNG` *(v1.40.3+)*

Action native qui exploite les variables de session capturées par la macro `SATER LOC` pour générer automatiquement une **carte OpenStreetMap PNG** centrée sur la balise ELT, avec marqueur, cercle d'incertitude et cartouche complet. C'est l'aboutissement du pipeline SATER initié en v1.40.2.

### Variables consommées

L'action lit les variables de session définies par la macro précédente (ou par l'opérateur via le dialogue 🔖 Vars) :

| Variable | Obligatoire | Format | Rôle |
|---|---|---|---|
| `LAT` | ✅ Oui | Décimal WGS84 (ex. `48.429167`) | Latitude du centre de la carte |
| `LON` | ✅ Oui | Décimal WGS84 (ex. `3.291944`) | Longitude du centre de la carte |
| `RAYON_M` | Optionnelle | Entier en mètres (ex. `280`) | Rayon CEP 95 du cercle d'incertitude. Si absent ou `N/A`, pas de cercle dessiné. |
| `INDICATIF_BALISE` | Optionnelle | Texte libre | Étiquette du marqueur. Défaut : `BALISE ELT`. |
| `SITREP_TS` | Optionnelle | Texte libre | Horodatage affiché en sous-titre. |

### Sortie produite

L'action retourne dans le chat IAbrain un bloc Markdown structuré :

1. **Tableau récapitulatif** (indicatif, lat/lon décimal, rayon, fichier généré)
2. **Image PNG affichée inline** dans le chat (rendu Markdown automatique)
3. **Liens cliquables** vers OSM, Géoportail IGN, Google Maps en complément
4. **Chemin absolu** du fichier PNG sauvegardé pour archivage

### Exemple de carte générée

Position de la balise du CSV de test ADRASEC 77 (48°25'45"N 003°17'31"E, rayon CEP 95 ± 280 m) :

<div align="center">

<img src="docs/images/sater_map_png_exemple.png" alt="Exemple de carte SATER MAP PNG" width="800">

</div>

Éléments visuels du rendu :

- **Marqueur rouge SAR** centré sur la position calculée, avec étiquette de l'indicatif balise sur fond blanc
- **Cercle d'incertitude CEP 95 %** (contour rouge), avec un cercle interne au tiers du rayon pour repère de centrage
- **Cartouche** en bas à gauche : position en DMS (`48°25'45.00"N 003°17'31.00"E`), position décimale (`48.429167, 3.291944`), incertitude (`± 280 m (CEP 95 %)`), horodatage du calcul, attribution OpenStreetMap
- **Échelle** en bas à droite (calibrée selon le zoom auto)
- **Titre** avec l'indicatif balise et la date de calcul
- **Auto-zoom intelligent** : le niveau de zoom OSM est choisi automatiquement pour que le cercle d'incertitude occupe environ 1/4 de la largeur de carte (zoom 12-17 selon le rayon)

### Fichiers et stockage

```
IAbrain/
├── IAbrain.exe
└── IAbrain_sater_maps/                                    ← créé automatiquement
    ├── balise_BALISE_ELT_20260504_134205.png             ← naming auto avec horodatage
    ├── balise_F-OBJZ_20260504_141532.png
    └── ...
```

Format de nom : `balise_<INDICATIF>_<YYYYMMDD_HHMMSS>.png`. Les caractères spéciaux de l'indicatif sont nettoyés (slashes, espaces, accents → `_`). 

**Personnalisation du dossier de sortie** : définir la variable d'environnement `IABRAIN_SATER_OUTPUT_DIR` pour rediriger les PNG vers un autre dossier (utile pour des partages réseau ou des archives par exercice).

### Macro prête à importer

Pour utiliser l'action, importer la macro **`SATER MAP PNG`** livrée avec IAbrain v1.40.3 :

```
1. Clic-droit sur un bouton macro vide → ouvre l'éditeur de macro
2. Cliquer sur « 📥 Importer une Macro »
3. Sélectionner le fichier IAbrain_macro_SATER_MAP_PNG_v1403.iabmacro
4. Cliquer sur « Enregistrer »
```

La macro est de type **Action**, action `osm_balise_map`, sans dépendance au LLM. Exécution **instantanée** côté Python (3-10 s pour le téléchargement des tuiles OSM selon la connexion).

### Garde-fous

> 🌐 **Connexion Internet requise** — les tuiles OSM viennent de `tile.openstreetmap.org`. En zone blanche, l'action retourne un message d'erreur clair listant les causes fréquentes (pas d'Internet, pare-feu, quota).

> 🔒 **Coordonnées non envoyées au LLM** — l'action est purement locale Python : pas de prompt, pas de tokens, pas de RAG. Seules les coordonnées vont vers le serveur de tuiles OSM (qui ne permet pas de remonter à un opérateur particulier — pas de cookies, pas d'auth).

> ⚠ **Validation des entrées** — si `LAT`/`LON` sont absentes, non numériques ou hors plage, l'action retourne un message Markdown explicite plutôt que de planter. Idem si le module `osm_balise_png` ou les paquets `staticmap`/`Pillow` sont absents.

> 📋 **Conformité OSM Tile Usage Policy** — IAbrain identifie ses requêtes avec un User-Agent dédié `IAbrain/1.40 (ADRASEC SATER tool; F1GBD)` conforme à la [politique d'usage des tuiles OSM](https://operations.osmfoundation.org/policies/tiles/). Pour un usage opérationnel ADRASEC (quelques cartes par exercice), l'usage est conforme. Pour un usage très intensif, basculer vers un serveur de tuiles dédié.

---

## ☁ Connectivité Ollama Cloud *(v1.38.0+)*

Depuis la v1.38.0, IAbrain peut accéder aux **grands modèles XL** hébergés par [Ollama Cloud (Turbo)](https://ollama.com/turbo) sans avoir à les exécuter localement. Cela ouvre l'usage d'IAbrain à des cas où le matériel local ne permet pas de faire tourner un modèle 70B+ : démos sur tablette, formations sur laptop entrée de gamme, tests ponctuels de modèles XL avant achat de matériel.

### Modèles cloud disponibles

| Modèle | Taille | Cas d'usage |
|---|---|---|
| `gpt-oss:20b` | 20B params | Compromis qualité / coût pour tests généralistes |
| `gpt-oss:120b` | 120B params | ⭐ Référence pour démos qualité maximale |
| `deepseek-v3.1:671b` | 671B params | Tâches complexes, raisonnement multi-étapes |

La liste exacte est récupérée dynamiquement à chaque démarrage via l'API d'Ollama, donc IAbrain reste à jour automatiquement quand de nouveaux modèles cloud sont publiés.

### Deux modes au choix

| Mode | Comment ça marche | Idéal pour |
|---|---|---|
| **Direct** | IAbrain appelle directement `https://ollama.com/api/chat` avec une API key (header `Authorization: Bearer`) | Démos sur petite machine **sans Ollama installé** |
| **Proxy local** | IAbrain passe par l'Ollama local + suffixe `-cloud` après `ollama signin` | Workflow Ollama natif, gestion centralisée |

### Configuration

L'API key est résolue selon l'ordre de priorité suivant :

1. **Variable d'environnement `OLLAMA_API_KEY`** (recommandé pour les déploiements partagés et la sécurité)
2. **Champ `cloud_api_key` dans `IAbrain.json`** (fallback pratique pour les démos rapides)

Pour configurer :

```powershell
# Méthode A (recommandée) : variable d'environnement persistante
setx OLLAMA_API_KEY "votre_cle_obtenue_sur_ollama.com"
# Redémarrer IAbrain pour la prise en compte

# Méthode B (rapide) : Options → Paramètres → champ « API key »
```

Puis dans IAbrain :

```
Options → Paramètres → section « ☁ Ollama Cloud »
   → cocher « Activer l'accès aux modèles Ollama Cloud »
   → choisir le mode (Direct ou Proxy local)
   → cliquer sur « 🔌 Tester la connexion cloud »
   → Valider
```

### Indicateur visuel : préfixe ☁

Les modèles cloud apparaissent dans le sélecteur avec un préfixe ☁ pour les distinguer visuellement des modèles locaux :

```
qwen2.5:7b              ← modèle local
☁ gpt-oss:20b          ← modèle cloud
☁ gpt-oss:120b         ← modèle cloud (idéal pour démos)
☁ deepseek-v3.1:671b   ← modèle cloud
```

Cohérent avec le préfixe ⚙ utilisé pour les macros Action.

### Garde-fous de confidentialité

> 🔒 **L'embedder RAG reste TOUJOURS local** — quel que soit le mode cloud activé, la base ADRASEC, vos notes perso, vos corrections manuelles et l'embedder (`nomic-embed-text`) ne quittent **jamais** votre machine. Seul le prompt de chat (et le contenu des fichiers que vous importez intentionnellement dans le chat) est envoyé à ollama.com en mode direct.

> ⚠ **Avertissement automatique** — quand vous activez le mode cloud direct, un message système est posté dans le chat pour rappeler que les prompts seront envoyés à un service distant. Le message reste tracé dans l'historique de conversation.

> ⚠ **Cas non recommandés** — le mode cloud n'est **pas adapté** aux opérations sensibles, aux SITREP confidentiels, aux questions relatives à la sécurité civile en cours d'incident. Le mode local pur reste la configuration de référence pour l'opérationnel ADRASEC.


---

## 🧠 Mémoire conversationnelle persistante *(v1.39.0+)*

Depuis la v1.39.0, IAbrain peut **apprendre des conversations** au fil de l'usage. Quand une conversation contient une information importante (procédure, fréquence, indicatif, retour d'expérience), l'opérateur peut demander à IAbrain de s'en souvenir. Cette mémoire **enrichit automatiquement la base RAG perso** et devient consultable lors des futures questions.

C'est une évolution architecturale : IAbrain passe d'un assistant *stateless* à un **compagnon qui s'enrichit au fil des exercices** ADRASEC.

### Trois façons de mémoriser

| Méthode | Quand l'utiliser |
|---|---|
| 🎤 **Mots-clés naturels** : « Souviens-toi », « Rappelle-toi », « Retiens », « Mémorise », « N'oublie pas » | Pendant la conversation, sans interruption |
| 🟢 **Bouton « 🧠 Se souvenir »** sous une réponse | Décision après-coup qu'une réponse mérite d'être mémorisée |
| 📋 **Menu Conversations → Mémoriser la conversation courante** | Mémorisation rétrospective avec confirmation |

### Architecture

```
IAbrain_rag_db_perso/
├── corrections/                              ← v1.36+
└── memories/                                 ← NOUVEAU v1.39.0
    └── 2026-05-03_05h25_le-boson-de-higgs.md
        → Indexé dans la base RAG perso (consultable par futures questions)

IAbrain_conversations/                        ← NOUVEAU v1.39.0
└── 2026-05-03_05h25_le-boson-de-higgs.json
        → Permet de reprendre la conversation plus tard
```

### Nouveau menu « 💬 Conversations »

| Item | Action |
|---|---|
| ✨ **Nouvelle conversation** *(Ctrl+N)* | Propose d'archiver l'actuelle puis vide le contexte |
| 📂 **Reprendre une conversation…** | Browser de toutes les conversations archivées, double-clic pour reprendre |
| 🧠 **Mémoriser la conversation courante…** | Mémorisation rétrospective |
| 🗂 **Ouvrir le dossier des conversations** | Ouvre `IAbrain_conversations/` dans l'explorateur |

### Garde-fous architecturaux

> 🔒 **L'embedder reste TOUJOURS local** — la mémoire conversationnelle ne quitte jamais la machine, même quand IAbrain utilise un modèle Ollama Cloud (v1.38+). Cohérent avec la philosophie ADRASEC : la base de connaissances reste locale et confidentielle.

> ⚠ **Pas de mémorisation silencieuse** — chaque mémorisation est confirmée par un message dans le chat avec le chemin du fichier créé. L'opérateur sait toujours ce qui a été ajouté.

> 🗑 **Suppression manuelle possible** — les fichiers `.md` et `.json` sont accessibles via le menu Conversations → Ouvrir le dossier. Suppression = oubli garanti à la prochaine réindexation.

> 📝 **Traçabilité** — chaque mémoire contient son indicatif d'auteur, sa date, le modèle utilisé. Pas d'effet « boîte noire ».

---

## 👤 Profil opérateur déclaratif *(v1.40.0+)*

À partir de la v1.40.0, IAbrain peut **connaître qui est l'opérateur** dès le premier mot de la conversation. Le profil est édité explicitement par l'utilisateur (pas généré automatiquement) et reste strictement local.

### Pourquoi un profil ?

- **Convivialité** : accueil personnalisé au démarrage (« Bonjour F1GBD, je suis IAbrain. Nous sommes le 3 mai 2026 et il est 08h30 »)
- **Pertinence** : le modèle adapte son ton et sa profondeur au niveau déclaré (débutant pédagogique vs expert direct)
- **Cohérence** : approche **déclarative** (l'opérateur décide) plutôt que **observée** (où le système devine), respectueuse de l'autonomie ADRASEC

### Champs du profil

| Champ | Description |
|---|---|
| Indicatif | Validé contre un pattern radio standard (F1GBD, K1ABC, DL5XYZ, F1GBD/P, …) |
| Prénom | Optionnel, pour adresse personnalisée |
| Département ADRASEC | Numéro (« 77 ») ou nom (« Seine-et-Marne ») |
| Niveau d'expertise | `debutant` / `intermediaire` / `expert` |
| Spécialités radio | Multi-sélection parmi 16 suggérées (HF, VHF/UHF, VARA HF/FM, Reticulum/LXMF, TCQ, ARDOP, SDR, satellite, SOTA/POTA, antennes portables, FlmSG/Winlink, etc.) |
| Préférence de format | `concise` / `detailed` / `technical` / `balanced` |
| Notes personnelles | Texte libre (max 500 chars) |

### Architecture

Le profil est sauvegardé dans `IAbrain_profile.json` (à côté d'`IAbrain.json`) puis :

1. **Chargé au démarrage** dans `self.operator_profile`
2. **Injecté en tête du système prompt** à chaque conversation (préambule ~150-200 tokens)
3. **Affiché comme accueil** sur l'écran de démarrage entre le titre et le logo

```
┌─────────────────────────────────────────────────────┐
│       IAbrain v1.40.3                                │
│  Assistant IA local pour ADRASEC — by F1GBD          │
│                                                       │
│  Bonjour Jean-Louis, je suis IAbrain.                │
│  Nous sommes le 4 mai 2026 et il est 08h30.          │
│                                                       │
│              [logo IAbrain]                          │
└─────────────────────────────────────────────────────┘
```

### Garde-fous

> 🔒 **Strictement local** — le profil ne quitte jamais la machine, **même en mode cloud Ollama (v1.38+)**. Il est juste prepended au système prompt local. Aucune donnée personnelle ne fuit.

> ⚙ **Opt-in explicite** — la fonctionnalité est désactivée par défaut. L'opérateur doit aller dans Options → Profil opérateur, remplir les champs, et cocher « Activer le profil ».

> 🔄 **Modification à chaud** — pas besoin de redémarrer IAbrain. Les changements s'appliquent dès la prochaine conversation. Un aperçu temps réel dans le dialog d'édition montre exactement ce qui sera injecté.

> 🚫 **Désactivation conservatrice** — un bouton « Désactiver le profil » désactive sans effacer les données. Réactivation possible plus tard.

### Différence avec les `userMemories`

Le profil opérateur d'IAbrain est volontairement différent du système `userMemories` automatique d'autres assistants :

| Aspect | userMemories (auto) | Profil opérateur (IAbrain) |
|---|---|---|
| Source | Observée automatiquement | Déclarée par l'opérateur |
| Mise à jour | Algorithmes opaques | L'opérateur via menu Options |
| Contenu | Résumé conceptuel généré | Métadonnées structurées |
| Réversibilité | Édition possible mais opaque | Modification/désactivation immédiates |
| Adapté à ADRASEC | Variable | Oui (chaque opérateur maîtrise ses données) |

---

## 📊 Le quotidien d'un opérateur, avant et avec IAbrain

| Sans IAbrain | Avec IAbrain |
|---|---|
| **Recherche d'une procédure dans 30 PDF :** feuilleter les notes techniques, ouvrir plusieurs documents, lire en diagonale.<br>⏱ *Durée : 5 à 15 minutes.* | **Question en langage naturel :** « Comment configurer TCQ-BBS pour HELIOS ? »<br>⏱ *Réponse synthétique en 10 secondes avec les sources citées.* |
| **Rédaction d'un SITREP type :** partir d'une feuille blanche ou copier-coller un ancien.<br>⏱ *Durée : 30 à 60 minutes.* | **Demande à IAbrain :** « Rédige un SITREP pour exercice X »<br>⏱ *Document structuré généré en 30 secondes, à éditer puis exporter en .md.* |
| **Conversion d'un bilan CSV en tableau lisible :** ouvrir Excel, copier-coller dans Word, retravailler la mise en forme manuellement.<br>⏱ *Durée : 5-10 minutes par tableau, fragile.* | **Importer le CSV → cliquer sur `⚙ CSV To MD`**<br>⏱ *Conversion en moins d'une seconde, plusieurs tableaux à la fois, multi-encodages, fidèle au CSV original.* |
| **L'IA se trompe sur une fréquence locale :** rien à faire, elle continuera à donner la mauvaise réponse à chaque question. | **Clic-droit → « Corriger cette réponse »** *(v1.36+)*<br>La correction est appliquée pour toujours, partageable avec votre section. |
| **Connaissance dispersée :** chaque opérateur a ses propres notes, niveaux d'expertise hétérogènes. | **Base de connaissances commune** mise à jour depuis GitHub d'un seul clic.<br>Tous les opérateurs au même niveau. |
| **Dépendance Internet et services cloud :** risque opérationnel en zone blanche ou pendant un incident électrique. | **100% local, hors ligne, confidentiel.** Fonctionne en exercice ou opération réelle sans aucune connexion externe. |
| **Démo / formation sur laptop entrée de gamme :** impossible de faire tourner un modèle 70B+ pour montrer la qualité maximale. | **Mode cloud activable** *(v1.38+)* : sélectionner `☁ gpt-oss:120b` dans la liste, et exploiter un modèle XL hébergé sans contrainte matérielle.<br>La base ADRASEC reste sur la machine. |
| **Information apprise en exercice perdue à la prochaine session :** une consigne dictée à l'oral, un retour d'expérience, une procédure spécifique à un exercice — tout repart de zéro à chaque fois. | **« Souviens-toi de cette procédure »** *(v1.39+)*<br>IAbrain mémorise la conversation dans la base perso. La connaissance s'enrichit naturellement au fil des exercices. |
| **Pipeline d'analyse SATER manuel :** calculer la triangulation à la main, recopier les coordonnées dans une carte web, capturer une copie d'écran pour le SITREP, sauvegarder le résultat à part. Erreurs de saisie possibles entre étapes.<br>⏱ *Durée : 5-10 minutes par balise.* | **Pipeline complet en deux clics** *(v1.40.2 + v1.40.3)*<br>Macro `SATER LOC` → variables de session → action native `SATER MAP PNG`. La triangulation est calculée par le LLM, les coordonnées sont capturées automatiquement, et la carte OSM PNG est générée et affichée directement dans le chat avec marqueur, cercle d'incertitude et cartouche prêts pour le SITREP.<br>⏱ *Durée : ~30 secondes, zéro erreur de transcription, zéro copie d'écran.* |

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

> 💡 **Astuce** : la procédure détaillée est dans le **« Guide d'installation IAbrain v1.40 »** livré séparément. Il inclut aussi la procédure manuelle pas-à-pas en annexe pour les utilisateurs avancés.

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

#### 📥 [**Télécharger IAbrain.7z**](https://github.com/f1gbd/F1GBD/releases/download/iabrain-v1.40.3/IAbrain.7z)

*(version `iabrain-v1.40.3` — voir [toutes les releases IAbrain](https://github.com/f1gbd/F1GBD/releases?q=iabrain) pour les versions précédentes)*

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
4. Pour tester les actions natives : **importer un CSV → cliquer sur `⚙ CSV To MD`** (macro pré-installée)

> ⏱ Comptez environ **30 minutes** pour la première installation, ensuite IAbrain est utilisable au quotidien sans configuration supplémentaire.

---

## 📚 Documentation complète

Ce dépôt contient également les manuels suivants :

- 📋 **Fiche de présentation v1.40**
- 📖 **Guide d'installation IAbrain v1.40** *(méthode automatique + annexe manuelle)*
- 📘 **Manuel utilisateur IAbrain v1.40** *(complet, incluant la cartographie interactive, les corrections manuelles, les macros/actions natives, l'import/export de macros, les variables de session, le pipeline SATER complet, la connectivité Ollama Cloud, la mémoire conversationnelle, et le profil opérateur)*
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
│  - Cartographie interactive (v1.35+)   │
│  - Corrections manuelles (v1.36+)      │
│  - Macros LLM + Action (v1.37+)        │
│  - Rendu Markdown complet (v1.37+)     │
│  - Connectivité Ollama Cloud (v1.38+)  │
└──────┬─────────────────────────┬───────┘
       │                         │
       │ HTTP localhost:11434    │ HTTPS ollama.com (cloud direct)
       │ (toujours utilisé pour  │ (uniquement pour le LLM de chat
       │  l'embedder + RAG)      │  quand un modèle ☁ est sélectionné)
       │                         │
┌──────▼──────────────────┐  ┌───▼────────────────────────────┐
│  Ollama LOCAL           │  │  Ollama CLOUD (Turbo)          │
│  - llama3.2:3b          │  │  - ☁ gpt-oss:20b               │
│  - qwen2.5:7b           │  │  - ☁ gpt-oss:120b              │
│  - nomic-embed-text     │  │  - ☁ deepseek-v3.1:671b        │
│    (RAG embedder)       │  │  Auth : OLLAMA_API_KEY (env)   │
│  - bge-m3 (reranking)   │  │  ou cloud_api_key (config)     │
└─────────────────────────┘  └────────────────────────────────┘

┌────────────────────────────────────────┐
│  Bases RAG (locales, double-base v1.34)│
│  ┌──────────────────────────────────┐  │
│  │ Base principale ADRASEC          │  │
│  │  - 182 fichiers indexés          │  │
│  │  - 2092 chunks vectorisés        │  │
│  │  - Mise à jour OTA depuis GitHub │  │
│  └──────────────────────────────────┘  │
│  ┌──────────────────────────────────┐  │
│  │ Base perso (jamais écrasée)      │  │
│  │  - Vos notes, RETEX, ajouts      │  │
│  │  - Indexation à la demande       │  │
│  │  - Corrections manuelles (v1.36+)│  │
│  │  - Mémoires conv. (v1.39+)       │  │
│  └──────────────────────────────────┘  │
│  🔒 Confidentialité : ne sortent       │
│     JAMAIS de la machine, même en      │
│     mode cloud (l'embedder est local)  │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│  Mémoire conversationnelle (v1.39+)    │
│  ┌──────────────────────────────────┐  │
│  │ IAbrain_memory.py                │  │
│  │  - detect_memory_trigger()       │  │
│  │  - save_memory_file()            │  │
│  │  - save_conversation_archive()   │  │
│  │  - load_conversation_archive()   │  │
│  └──────────────────────────────────┘  │
│  Stockage :                            │
│  - perso/memories/*.md (indexé RAG)    │
│  - IAbrain_conversations/*.json        │
│    (reprise possible)                  │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│  Actions natives (v1.37.7+)            │
│  ┌──────────────────────────────────┐  │
│  │ IAbrain_actions.py               │  │
│  │  - csv_to_markdown               │  │
│  │  - extract_callsigns             │  │
│  │  - extract_frequencies           │  │
│  │  - anonymize                     │  │
│  │  - file_stats                    │  │
│  │  Pas de LLM, pas d'Ollama        │  │
│  │  Instantané, déterministe        │  │
│  └──────────────────────────────────┘  │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│  Variables de session (v1.40.2+)       │
│  ┌──────────────────────────────────┐  │
│  │ IAbrain_session_vars.py          │  │
│  │  - extract_vars_block()          │  │
│  │  - substitute_vars()             │  │
│  │  - SessionVarsManager            │  │
│  │    (set/get/save/load)           │  │
│  │  Hooks dans IAbrainApp :         │  │
│  │  - capture après _finalize_stream│  │
│  │  - subst. dans send_message +    │  │
│  │    _exec_macro_impl              │  │
│  │  Stockage :                      │  │
│  │  - IAbrain_session_vars.json     │  │
│  │  Persistance entre sessions      │  │
│  │  Sans dépendance Tk, testable    │  │
│  └──────────────────────────────────┘  │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│  Macros — Import/Export (v1.40.1+)     │
│  ┌──────────────────────────────────┐  │
│  │ Format .iabmacro (JSON UTF-8)    │  │
│  │  - iabrain_macro_version: 1      │  │
│  │  - exported_at, exported_by      │  │
│  │  - macro {label, prompt, type,   │  │
│  │    rag_disabled, action}         │  │
│  │  Boutons 📥📤 dans l'éditeur     │  │
│  │  Validation de version à l'import│  │
│  └──────────────────────────────────┘  │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│  Plugin Actions SATER (v1.40.3+)       │
│  ┌──────────────────────────────────┐  │
│  │ IAbrain_actions_sater.py         │  │
│  │  - osm_balise_map                │  │
│  │    (lit LAT/LON/RAYON_M depuis   │  │
│  │     session_vars, génère PNG OSM)│  │
│  │  Plugin séparé de IAbrain_actions│  │
│  │  même API list_actions/execute   │  │
│  │  Routage automatique côté        │  │
│  │  IAbrain._exec_macro_action      │  │
│  └──────────────────────────────────┘  │
│  ┌──────────────────────────────────┐  │
│  │ osm_balise_png.py                │  │
│  │  (compilé dans le PYZ via spec)  │  │
│  │  - generate_osm_png()            │  │
│  │  - Auto-zoom, marqueur, cercle,  │  │
│  │    cartouche, attribution OSM    │  │
│  │  Dépendances : staticmap, Pillow │  │
│  └──────────────────────────────────┘  │
│  Stockage : IAbrain_sater_maps/*.png   │
└────────────────────────────────────────┘
```

---

## 🆕 Évolution récente — v1.33 → v1.40

Les versions récentes ont apporté plusieurs améliorations majeures, du RAG hybride aux corrections manuelles, en passant par la cartographie, les macros utilisateur, la connectivité cloud, la mémoire conversationnelle et désormais le profil opérateur.

### 👤 v1.40.x — Profil opérateur, partage de macros, variables de session, pipeline SATER

La série v1.40 personnalise l'expérience opérateur, ouvre le partage de macros entre opérateurs ADRASEC, permet le chaînage de macros via des variables capturées automatiquement, et boucle le pipeline SATER complet (analyse + cartographie OSM en deux clics).

| Version | Apport principal |
|---|---|
| **1.40.0** | Module `IAbrain_profile.py` (~430 lignes), profil opérateur éditable via Options → Profil opérateur (indicatif, prénom, département ADRASEC, niveau d'expertise, spécialités, format préféré, notes), greeting personnalisé au démarrage (« Bonjour F1GBD, nous sommes le 3 mai 2026 et il est 08h30 »), injection en tête du prompt système pour adapter ton et profondeur au niveau déclaré. **Inclut aussi la fonctionnalité v1.39.1** : éditeur de mémorisation (relecture/correction de la question + réponse avant gravure dans la base RAG perso), évite de propager les coquilles de l'IA dans la base. |
| **1.40.1** | **Import/Export de macros au format `.iabmacro`** : deux nouveaux boutons « 📥 Importer une Macro » et « 📤 Exporter la Macro » dans le dialogue d'édition. Format JSON UTF-8 versionable (champs `iabrain_macro_version`, `exported_at`, `exported_by`, `macro`). Permet de partager des macros standardisées au sein d'une section ADRASEC, archiver des versions de travail, ou récupérer une macro depuis un autre poste. Validation de version à l'import, demande de confirmation avant écrasement, l'enregistrement effectif est différé jusqu'au clic sur « Enregistrer » pour permettre la relecture. |
| **1.40.2** | **Variables de session persistantes** : nouveau module `IAbrain_session_vars.py` (~360 lignes, sans dépendance Tk, 14 tests unitaires). Capture silencieuse des blocs `###IABRAIN_VARS###` produits par les macros LLM, substitution automatique de `{NOM}` dans les prompts suivants (macro ou chat libre), persistance disque dans `IAbrain_session_vars.json`, indicateur cliquable « 🔖 Vars (n) » dans la barre du haut, dialogue d'inspection/édition manuelle (Treeview, ajout/modif/suppression). Validation des noms (`[A-Z][A-Z0-9_]*`), échappement `{{NOM}}`, capacité 64 vars × 4 ko. Ouvre la voie aux pipelines opérationnels chaînés. |
| **1.40.3** | **Pipeline SATER complet** : nouveau module plugin `IAbrain_actions_sater.py` (~340 lignes) avec l'action native `osm_balise_map` qui lit les variables de session (`LAT`, `LON`, `RAYON_M`, `INDICATIF_BALISE`, `SITREP_TS`) et génère un PNG OpenStreetMap centré sur la balise (marqueur, cercle CEP 95, cartouche de légende), affiché directement dans le chat IAbrain et archivé dans `IAbrain_sater_maps/`. L'utilitaire `osm_balise_png.py` est compilé dans le PYZ pour une distribution tout-en-un (un seul exécutable, aucun fichier .py séparé à distribuer). Routage automatique des actions entre le module standard `IAbrain_actions` et le plugin SATER ; le combobox d'édition liste les actions des deux modules. Macro pré-configurée `IAbrain_macro_SATER_MAP_PNG_v1403.iabmacro` livrée pour import direct. |

### 🧠 v1.39.x — Mémoire conversationnelle persistante

La v1.39.0 ferme la boucle d'apprentissage : IAbrain peut désormais **mémoriser des conversations** dans sa base perso, en plus des corrections manuelles ponctuelles introduites en v1.36.

| Version | Apport principal |
|---|---|
| **1.39.0** | Module `IAbrain_memory.py` (~470 lignes), détection auto des mots-clés (« Souviens-toi », « Rappelle-toi », etc.), bouton « 🧠 Se souvenir » à côté de « 💾 Enregistrer », nouveau menu « 💬 Conversations » (nouvelle / reprendre / mémoriser / ouvrir dossier), nouveau menu « 🗺 Cartographie Base » de premier niveau, raccourci `Ctrl+N`, archivage `.json` pour reprise + indexation `.md` automatique dans la base perso |

### ☁ v1.38.x — Connectivité Ollama Cloud

La v1.38.0 ouvre IAbrain aux **modèles XL hébergés** (gpt-oss:120b, deepseek-v3.1:671b, mistral-large-3:675b…) sans avoir à les exécuter localement, tout en préservant la confidentialité de la base RAG. Validée en production avec `mistral-large-3:675b` sur des questions complexes (boson de Higgs, téléportation quantique avec RAG perso).

| Version | Apport principal |
|---|---|
| **1.38.0** | Module `IAbrain_cloud.py` (~470 lignes), section UI dans Options → Paramètres, deux modes (direct / proxy local), résolution API key via `OLLAMA_API_KEY` ou `IAbrain.json`, préfixe ☁ dans le sélecteur de modèles, bouton de test de la connexion, avertissement de confidentialité automatique, embedder RAG strictement local |
| 1.38.1 | Hotfix : strip systématique du préfixe ☁ + cache `_known_cloud_names` côté `OllamaClient` (source de vérité au-dessus de l'heuristique) + heuristique élargie (qwen3.5, qwen3.6, qwen4, glm-4.7, glm-5, deepseek-v4, kimi-) |
| 1.38.2 | Hotfix : sanitisation conditionnelle de `num_predict` pour le cloud direct (Ollama Cloud rejette `-1`, plafonne à 16384, contrairement au local) |
| **1.38.3** | **UX : bouton « 💾 Enregistrer » global avec choix Markdown OU RTF (nouveau `_markdown_to_rtf()` ASCII-safe), suppression des boutons par bloc de code, fenêtre d'édition de macro élargie (720×740, minsize 680×600), option « Corriger cette réponse » accessible sur tous les éléments Markdown** |

### ⚙️ v1.37.x — Macros, rendu Markdown, actions natives, encodage

La v1.37 est une **release majeure** qui transforme IAbrain en outil d'automatisation personnalisable. Elle introduit :

| Sous-version | Apport principal |
|---|---|
| **1.37.0** | Sortie initiale : 8 boutons macros LLM avec méta-langage 3-en-1 (variables `{{...}}`, brackets `[...]`, détection auto `"nom.ext"`) + rendu Markdown niveau Complet (titres, gras, italique, tables, citations, listes, **cases à cocher**, liens cliquables, images, séparateurs) |
| 1.37.1 | Hotfix : exécution des macros (correction d'un bug de référence widget) |
| 1.37.2 | Recherche corrections sur prompt épuré (évite faux matches sur les macros avec contenu fichier) |
| 1.37.3 | Séparation affichage chat / envoi LLM (badge 📎 nom.ext au lieu du contenu brut) + ordre de résolution méta-langage corrigé |
| 1.37.4 | `num_ctx` adaptatif : auto-augmentation de la fenêtre contexte Ollama si prompt > 40% |
| 1.37.5 | Seuil de pertinence corrections augmenté de 0.55 à 0.65 + skip des corrections sur macros avec fichier référencé |
| 1.37.6 | Option **🚫 Désactiver le RAG pour cette macro** (recommandée pour les transformations pures) |
| **1.37.7** | **Macros « Action » : 5 fonctions natives (csv_to_markdown, extract_callsigns, extract_frequencies, anonymize, file_stats), exécution déterministe sans LLM** |
| **1.37.8** | **Détection auto d'encodage à l'import (UTF-8, UTF-16, CP1252, ISO-8859-15/1) + macro 1 pré-programmée `⚙ CSV To MD`** |

### 📢 v1.36.x — Corrections manuelles intégrées

Le système de corrections manuelles permet à l'opérateur de **corriger les erreurs ou imprécisions du LLM** directement depuis le chat. Chaque correction est :

- Stockée en fichier Markdown versionable dans `IAbrain_rag_db_perso/corrections/`
- Indexée dans la base perso avec un format dense optimisé pour l'embedding
- **Pré-injectée prioritairement** dans le contexte RAG des requêtes futures (priorité absolue, indépendamment du seuil de similarité et du reranking)
- Partageable entre opérateurs via export/import ZIP

| Version | Apport principal |
|---|---|
| **1.36.0** | Architecture initiale du système de corrections (clic-droit, dialog, fenêtre de gestion, export/import ZIP) + hotfix migration config OTA |
| **1.36.1** | **Fix critique** : pré-injection prioritaire des corrections, format dense pour l'embedding (sim 0.65 → 0.85), bouton « Réindexer toutes », console terminale cachée, prompt anti-bégaiement |
| **1.36.2** | **Fix qualité** : seuil de pertinence des corrections augmenté de 0.30 à 0.55 (évite les injections hors-sujet), instruction de prompt nuancée, paramètre `rag_correction_min_similarity` configurable |

### 🌐 v1.35.0 — Cartographie interactive de la base RAG

Visualisation arborescente de la base de connaissances qui s'ouvre dans le navigateur. Quatre niveaux d'exploration :

```
⭐ Base RAG
└── 🟪 Cluster thématique  (k-means, 5-8 selon la taille)
    └── 📄 Fichier         (rond bleu = principale, losange orange = perso)
        └── 🟢 Chunk         (extrait de texte)
```

- **Force-directed dynamique** via vis-network (la même bibliothèque qu'utilise Reticulum MeshChat). Drag, zoom, animation physique.
- **Mode 100% hors-ligne** : `vis-network.min.js` (~700 Ko) embarqué inline dans le HTML généré. Le fichier final fait ~700 Ko et fonctionne sans aucune connexion Internet — le HTML peut être copié sur clé USB ou envoyé par mail.
- **Recherche locale temps réel** dans la barre du haut : auto-déplie les branches contenant des matches, surlignage rouge des chunks pertinents.
- **Breadcrumb dynamique** : `📚 Base RAG › 📂 Cluster › 📄 Fichier`. Permet de remonter d'un clic.
- **Clic-droit** sur un nœud déplié pour le replier (lui et tous ses descendants).
- **Pas de dépendance Python supplémentaire** : tout le calcul (PCA, k-means, labels TF-IDF) est en pur NumPy, pas de matplotlib ni scikit-learn.

### 📂 v1.34.0 — Base RAG personnelle

Architecture double-base qui sépare strictement la documentation officielle ADRASEC de vos ajouts perso :

| Base | Origine | Mise à jour |
|---|---|---|
| **Principale ADRASEC** | OTA GitHub officiel | Écrasée à chaque OTA |
| **Perso** | Vos `Indexer un fichier`, vos notes, vos corrections (v1.36+) | **Jamais écrasée par l'OTA** |

Les deux bases sont fouillées simultanément à chaque requête RAG. Dans la cartographie v1.35, les chunks perso apparaissent en losanges orange — d'un coup d'œil vous voyez où vos notes s'intègrent thématiquement par rapport à la base officielle.

Cas d'usage typiques : vos RETEX d'exercice locaux, vos fiches techniques personnelles, des copies de mails opérationnels, des PV de réunion ADRASEC départementaux.

### 🔧 v1.33.x — Reranking RAG, paramètres exposés, MAJ auto

| Version | Apport principal |
|---|---|
| **1.33.0** | Architecture reranking RAG via bge-m3 (qualité des réponses ×2) |
| 1.33.1 | Hotfix nom du modèle reranker (bge-m3 au lieu de bge-reranker-v2-m3) |
| 1.33.2 | Filtre embedders dans le sélecteur de modèles |
| **1.33.3** | Paramètres RAG exposés dans l'UI + min_similarity 0.30 + qwen2.5:7b par défaut |
| 1.33.4 | Case « Activer le RAG » bien en évidence dans Options → Paramètres |
| **1.33.5** | Vérification automatique des mises à jour GitHub au démarrage |
| 1.33.6 | Fenêtres Paramètres et À propos compactes (compatible petits écrans) |

Pour le détail de tous les changements, consultez le [changelog complet sur GitHub Releases](https://github.com/f1gbd/F1GBD/releases).

---

## 🤝 Communauté

IAbrain est un **projet open développé pour la communauté ADRASEC**, proposé librement aux opérateurs ADRASEC départementales et à la FNRASEC.

Toute contribution, retour d'expérience ou proposition d'amélioration est bienvenue via les *Issues* du dépôt GitHub.

---

<div align="center">

### 📡 Auteur

**Jean-Louis (F1GBD / F4JHW)**
*ADRASEC 77 — FNRASEC*

**Version 1.40.3 — 2026-05-04**

---

*Pour toute question, contactez votre référent ADRASEC départemental.*

🧠 **IAbrain** — *L'intelligence artificielle au service de la sécurité civile*

</div>
