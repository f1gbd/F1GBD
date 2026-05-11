# Prompts directs pour formation SITREP PDF — v3

> **Validés** sur IAbrain v1.41.3 + plugin SITREP v1.1.7 + qwen2.5:7b local.
> Distribution : ADRASEC 77 / FNRASEC.
>
> La v3 consolide les trois prompts de formation, en utilisant le pattern
> qui fonctionne : SITREP_TEXT pré-fabriqué dans le prompt utilisateur, le
> LLM ne génère que l'histoire courte et le SITREP radio (≤500 tokens en
> sortie au lieu de 1500+ en v1, plus de troncatures, plus d'hallucinations).
>
> **Trois scénarios couvrent trois niveaux de gravité** :
> - Prompt n°1 — HÉLIOS-NOIR-2030 (blackout/canicule, gravité CRITIQUE, 11 cases applicables sur 12)
> - Prompt n°2 — GABRIEL-30 (panne GSM/RRF, gravité MODEREE, 2 cases applicables sur 12 + 4 négations explicites)
> - Prompt n°3 — Squelette libre pour formateur (à adapter à n'importe quel scénario)

---

## Pré-réglages communs (à faire UNE fois en début de séance)

```
/set CALL=F1GBD
/set ADRASEC=ADRASEC 77
```

Remplacer `F1GBD` et `77` par l'indicatif et le département de votre opérateur.

---

## 🎓 Prompt n°1 — HÉLIOS-NOIR-2030 (cas CRITIQUE)

**Objectif pédagogique** : démontrer le remplissage automatique sur un scénario à forte gravité avec 11 cases cochées, 5 demandes de moyens, gravité CRITIQUE, tendance EN DEGRADATION.

```
Tu es opérateur radio ADRASEC en exercice HELIOS-NOIR-2030. Produis SEULEMENT et dans cet ordre exact, RIEN D'AUTRE :

## 📖 Histoire — HELIOS-NOIR-2030
[60 mots maximum sur canicule août 2030, AMOC, arrêt centrales nucléaires, blackout Seine-et-Marne, mobilisation ADRASEC 77]

## 📻 SITREP radio
[3 lignes phonie format ADRASEC]

###IABRAIN_VARS###
SITREP_TEXT = Commune sinistrée : BEAUX-SUR-MARNE, code postal 77105. ADRASEC 77. DTG SITREP : 11/08/2030 14:25. PCS activé OUI depuis 05/08/2030 06:30. DE : F1GBD/PCO BEAUX-SUR-MARNE. À : COD 77 PREFECTURE. Mode TCQ VARA FM. Fréquence 145.275 MHz. Relais F5ZYI VHF 145.4375 UHF 430.4375 CTCSS 77 Hz. Autorité MAIRE DUBOIS Marie, Maire de BEAUX-SUR-MARNE. Population impactée 55000 dont 8500 vulnérables. Coupure électrique totale depuis J+6. GSM Internet HS. Coupure eau potable. Pénurie carburant. Transports publics arrêtés. Climatisation HS EHPAD Les Lilas 4 décès. Évacuations sanitaires en cours. Routes bloquées 2 axes. 5 PDE actifs. PCC ouvert en mairie. Gravité CRITIQUE tendance EN DEGRADATION. Demandes 1. EVACUATION 15 PERS IMMEDIAT P1 EHPAD Les Lilas. 2. EAU POTABLE 30 M3 <3H P1 Place de la Mairie. 3. GROUPE ELECTROGENE 3 UNITE <6H P1 EHPAD Les Lilas. 4. MEDICAL 2 PALETTE <24H P2 Salle des fêtes BEAUX-SUR-MARNE. 5. VIVRES 500 KG J+1 P3 Place de la Mairie. PCC Mairie de BEAUX-SUR-MARNE salle du conseil. GPS 48.9606N 002.8786E. Accès RESTREINT axes endommagés. Contact Adj. MARTIN 09 12 34 56 78.
###END_IABRAIN_VARS###

###IABRAIN_RUN_MACRO###
SITREP PDF
###END_IABRAIN_RUN_MACRO###

RÈGLE ABSOLUE : recopie les 3 blocs ###...### EXACTEMENT comme ci-dessus, sans modifier UN SEUL caractère du SITREP_TEXT.
```

### Résultats attendus

| Champ | Valeur attendue dans le PDF |
|---|---|
| Commune | `BEAUX-SUR-MARNE` |
| CP | `77105` |
| Priorité | `URGENT` ou `FLASH` |
| Gravité | `CRITIQUE` |
| Tendance | `EN DEGRADATION` |
| Population impactée | `55000` |
| Dont vulnérables | `8500` |
| Fréquence | `145.275` (sans "MHz") |
| Indicatif | `F1GBD` (seul, sans ADRASEC) |
| Nom autorité | `DUBOIS Marie` (sans préfixe MAIRE) |
| Fonction | `Maire de BEAUX-SUR-MARNE` |
| GPS | `48.9606N 002.8786E` |
| Contact terrain | `Adj. MARTIN 09 12 34 56 78` |
| Filename PDF | `SITREP_BEAUX-SUR-MARNE_<YYYYMMDD-HHMM>.pdf` |
| Cases cochées | **11/12** — toutes sauf `chk_feu` |
| Demandes de moyens | 5 lignes complètes (EVACUATION, EAU POTABLE, GROUPE ELECTROGENE, MEDICAL, VIVRES) |

### Vérifications anti-régression

- ☑ Aucune mention de MEAUX, DUPONT, 77000 (signes d'hallucination v1.1.3-)
- ☑ Le filename doit commencer par `SITREP_BEAUX-SUR-MARNE_` (pas `SITREP_MEAUX_`)
- ☑ Le pop_impactee doit être `55000` (pas `30000`)

---

## 🎓 Prompt n°2 — GABRIEL-30 VILLANGIS (cas MODÉRÉ avec négations)

**Objectif pédagogique** : démontrer la **sélectivité** du plugin sur un scénario modéré qui mentionne explicitement ce qui **n'est PAS impacté**. Valide que le plugin ne fait pas de faux positifs sur des cases qui sont citées **en négation** dans le SITREP_TEXT.

```
Tu es opérateur radio ADRASEC en exercice GABRIEL-30 (panne GSM/RRF massive Seine-et-Marne suite incident transformateur 225kV à Nangis — PAS de blackout total, eau et hôpitaux fonctionnels). Produis SEULEMENT et dans cet ordre exact, RIEN D'AUTRE :

## 📖 Histoire — GABRIEL-30
[80 mots maximum : panne transformateur 225kV Nangis, propagation RRF + GSM 4 communes, mobilisation ADRASEC palliative]

## 📻 SITREP radio
[3 lignes phonie format ADRASEC]

###IABRAIN_VARS###
SITREP_TEXT = Commune sinistrée : VILLANGIS, code postal 77380. ADRASEC 77. DTG SITREP : 11/05/2030 14:25. PCS activé OUI depuis 11/05/2030 09:15. DE : F1GBD/PCO VILLANGIS. À : COD 77 PREFECTURE. Mode TCQ VARA FM. Fréquence 144.575 MHz. Direct, pas de relais, COD à 35 km à vue. Autorité MAIRE BERNARD Claude, Maire de VILLANGIS. Population impactée 8500 dont 1200 vulnérables. Coupure GSM Internet totale depuis 5h ce matin. PCC ouvert en mairie depuis 09:15. Pas de coupure électrique générale, réseau EDF stable. Eau potable distribuée normalement. Transports SNCF fonctionnels. Pas de victimes signalées. Gravité MODEREE tendance STABLE. Demandes 1. TRANSMISSIONS 2 UNITE <3H P1 Mairie de VILLANGIS relais autonome. 2. PERSONNEL 3 PERS <6H P2 Mairie de VILLANGIS renforts radio. PCC Mairie de VILLANGIS. GPS 48.5556N 003.0094E. Accès LIBRE. Contact SDIS 77 capitaine BROUX 09 22 33 44 55.
###END_IABRAIN_VARS###

###IABRAIN_RUN_MACRO###
SITREP PDF
###END_IABRAIN_RUN_MACRO###

RÈGLE ABSOLUE : recopie les 3 blocs ###...### EXACTEMENT comme ci-dessus, sans modifier UN SEUL caractère du SITREP_TEXT.
```

### Résultats attendus

| Champ | Valeur attendue dans le PDF |
|---|---|
| Commune | `VILLANGIS` |
| CP | `77380` |
| Gravité | `MODEREE` |
| Tendance | `STABLE` |
| Accès | `LIBRE` |
| Population impactée | `8500` |
| Dont vulnérables | `1200` |
| Fréquence | `144.575` |
| Indicatif | `F1GBD` |
| Nom autorité | `BERNARD Claude` |
| Fonction | `Maire de VILLANGIS` |
| GPS | `48.5556N 003.0094E` |
| Filename PDF | `SITREP_VILLANGIS_<YYYYMMDD-HHMM>.pdf` |
| **Cases cochées** | **EXACTEMENT 2/12** : `chk_gsm` + `chk_pcc` |
| **Cases NON cochées** (négations) | `chk_elec`, `chk_eau`, `chk_transp`, `chk_victimes` — bien que mentionnées, le filtre v1.1.7 doit les **rejeter** |
| Warning attendu dans le chat | `ℹ Cases rejetées (négation détectée dans source) : ...` |

### Vérifications anti-régression

- ☑ **2 cases seulement** cochées (pas plus, pas moins)
- ☑ `chk_elec` doit rester **décochée** malgré la mention « coupure électrique » (négation : « **Pas de** coupure électrique »)
- ☑ `chk_eau` doit rester **décochée** malgré la mention « eau potable » (négation : « distribuée **normalement** »)
- ☑ `chk_transp` doit rester **décochée** malgré la mention « Transports SNCF » (négation : « **fonctionnels** »)
- ☑ `chk_victimes` doit rester **décochée** malgré la mention « victimes » (négation : « **Pas de** victimes signalées »)

---

## 🎓 Prompt n°3 — Squelette libre pour formateur

**Objectif pédagogique** : permettre au formateur de **construire ses propres scénarios** sans devoir réinventer le pattern. Le formateur remplit les `[CROCHETS]` directement, le LLM ne fait que produire histoire + SITREP radio.

```
Tu es opérateur radio ADRASEC en exercice [SCÉNARIO en 1 phrase, ex: "CHIMERA-30 — fuite chimique SEVESO contenue sur usine BASF de Roissy-en-Brie"]. Produis SEULEMENT et dans cet ordre exact, RIEN D'AUTRE :

## 📖 Histoire — [NOM EXERCICE]
[60-100 mots sur le contexte de l'incident, les circonstances, et la mobilisation ADRASEC palliative]

## 📻 SITREP radio
[3 lignes phonie format ADRASEC]

###IABRAIN_VARS###
SITREP_TEXT = Commune sinistrée : [COMMUNE], code postal [CP]. ADRASEC [77|75|78|91|92|93|94|95]. DTG SITREP : [JJ/MM/AAAA HH:MM]. PCS activé [OUI|NON|EN COURS] depuis [JJ/MM/AAAA HH:MM]. DE : F1GBD/PCO [COMMUNE]. À : COD [DEP] PREFECTURE. Mode TCQ [VARA FM|VARA HF|VARA SAT|PACKET|ARDOP|LXMF]. Fréquence [MHz]. [Relais F5ZYI VHF/UHF ou Direct, pas de relais]. Autorité [MAIRE|ADJOINT|DGS|PREFECTURE|SDIS|SAMU|GENDARMERIE] [NOM Prénom], [fonction exacte]. Population impactée [N] dont [N] vulnérables. [Lister UNIQUEMENT les éléments APPLICABLES, séparés par des points, parmi : Coupure électrique totale / GSM Internet HS / Coupure eau potable / Pénurie carburant / Transports arrêtés / Climatisation HS / Feux en cours / Évacuations sanitaires en cours / Victimes (N décès) / Routes bloquées / N PDE actifs / PCC ouvert en mairie]. [Pour ce qui N'EST PAS impacté, indiquer explicitement avec négation : "Pas de coupure électrique" / "Eau potable distribuée normalement" / "Transports fonctionnels" / "Pas de victimes signalées" / "Pas de feux en cours" — ces mentions explicites sont importantes pour informer le COD sans cocher les cases]. Gravité [FAIBLE|MODEREE|ELEVEE|CRITIQUE] tendance [STABLE|EN DEGRADATION|EN AMELIORATION]. Demandes [N. TYPE QTE UNITE DELAI PRIO LIEU, max 7, P1 en premier]. PCC [adresse]. GPS [coordonnées ou rien]. Accès [LIBRE|RESTREINT|4x4 UNIQUEMENT|HELIPORTE|INACCESSIBLE]. Contact [NOM tel].
###END_IABRAIN_VARS###

###IABRAIN_RUN_MACRO###
SITREP PDF
###END_IABRAIN_RUN_MACRO###

RÈGLE ABSOLUE : recopie les 3 blocs ###...### EXACTEMENT comme ci-dessus, sans modifier UN SEUL caractère du SITREP_TEXT.
```

### Mode d'emploi pour le formateur

1. **Remplir tous les crochets `[...]`** dans le prompt avant de l'envoyer à IAbrain. Les crochets restants après l'envoi seraient interprétés littéralement par le LLM et casseraient l'extraction.
2. **Ne jamais retirer** la section négations (« Pour ce qui N'EST PAS impacté... »). C'est elle qui permet au plugin v1.1.7 d'éviter les faux positifs sur les cases.
3. **Garder l'ordre** des sections : EN-TÊTE → COMMUNICATIONS → AUTORITÉ → POPULATION → SITUATION → GRAVITÉ → DEMANDES → PCC.

### Idées de scénarios prêts à adapter

| Scénario | Commune type | Gravité | Cases applicables |
|---|---|---|---|
| **CHIMERA-30** — SEVESO chimique périmètre 800m | ROISSY-EN-BRIE 77680 | ELEVEE/EN_DEGRADATION | chk_evac + chk_pcc (+ chk_victimes si décès) |
| **AQUARIUS-30** — crue centennale Seine | PONT-SUR-YONNE 89140 | CRITIQUE/EN_DEGRADATION | chk_elec + chk_eau + chk_routes + chk_evac + chk_victimes + chk_pcc |
| **TEMPETE-30** — vents tempétueux 130 km/h | COULOMMIERS 77120 | ELEVEE/STABLE | chk_elec + chk_routes + chk_pcc |
| **CYBER-30** — cyberattaque réseau SCADA | MELUN 77000 | MODEREE/STABLE | chk_gsm + chk_pcc |
| **TERRO-30** — exercice antiterro confinement | NEMOURS 77140 | CRITIQUE/STABLE | chk_transp + chk_evac + chk_pcc |
| **AVION-30** — crash aéronef léger zone agricole | SAINT-CYR-SUR-MORIN 77750 | MODEREE/STABLE | chk_victimes + chk_evac + chk_pcc |

---

## 🛠 Pourquoi ces prompts marchent et pas les v1

| Aspect | v1 (problématique) | **v3 (consolidée)** |
|---|---|---|
| Demande au LLM | « Recopie la synthèse complète en une ligne avec `\n` littéral » | « Recopie ce bloc IABRAIN_VARS tel quel » |
| Sections markdown à générer | Histoire + SITREP texte + synthèse complète (~1000 tokens) | **Juste histoire (60-100 mots) + SITREP radio (3 lignes)** |
| Taille du SITREP_TEXT | ~1000 tokens (synthèse multi-ligne avec markdown) | **~400 tokens (paragraphe compact en une ligne)** |
| Total tokens sortie LLM | ~1500 (limite num_predict souvent atteinte) | **~300-500 (largement sous la limite)** |
| Risque de troncature | Élevé | **Faible** |
| Risque de confusion section | Le LLM peut recopier l'histoire au lieu de la synthèse | **Aucun** (donné explicitement entre marqueurs) |
| Risque de `\n` non décodés | Élevé (encodage `\n` littéral fragile) | **Aucun** (texte en clair en une ligne) |
| Risque hallucination commune/CP | Modéré (LLM doit "interpréter") | **Nul** (texte donné en clair) |
| Détection négations v1.1.7 | Échoue si LLM omet les négations | **Marche** grâce aux mentions « Pas de... », « fonctionnels », « normalement » dans le squelette |
| Temps de génération (qwen2.5:7b) | 150-180 s | **40-90 s** |
| Taux de remplissage moyen | 21-25/85 (29 %) | **65-70/85 (76-82 %)** |
| Hallucinations | Présentes | **0** |

---

## 🎯 Notes pédagogiques pour la formation

### Pourquoi écrire les négations explicitement ?

Sur un SITREP réel transmis au COD préfecture, **dire ce qui FONCTIONNE est aussi important que dire ce qui est cassé** :

- Le COD doit prioriser ses moyens : il n'a pas besoin de mobiliser ENEDIS si l'électricité fonctionne.
- L'absence de mention peut être interprétée par défaut comme « pas de problème » (ambigu).
- La mention explicite « Pas de coupure électrique » est **non-ambiguë** et confirme que l'opérateur a vérifié ce point.

Le plugin v1.1.7 reflète cette bonne pratique : il **ne coche que ce qui est explicitement positif**, et il **rejette les mentions négatives** détectées par contexte (« Pas de », « sans », « fonctionnel », « normalement », « stable »).

### Comment vérifier que la formation a réussi

Après chaque génération, le stagiaire doit ouvrir le PDF et vérifier **les 3 points opérationnels critiques** :

1. **Filename** correspond à la commune (`SITREP_<COMMUNE>_*.pdf`)
2. **Cases cochées** correspondent EXACTEMENT à ce qui est positivement mentionné dans le SITREP_TEXT
3. **Champs d'identification** (commune, CP, indicatif, fréquence) sont **identiques** au scénario (pas d'hallucination)

Si l'un de ces 3 points échoue → le SITREP serait inutilisable opérationnellement, **on recommence**.

### Que faire si le LLM se trompe quand même

Le plugin v1.1.7 émet des **warnings explicites** dans le chat :

- `ℹ indicatif_op nettoyé : « F1GBD | ADRASEC : ADRASEC 77 » → « F1GBD »` → pollution corrigée
- `ℹ Cases ajoutées par heuristique (oubliées par LLM) : chk_X, chk_Y` → le LLM a sous-extrait, l'heuristique a compensé
- `ℹ Cases rejetées (négation détectée dans source) : chk_X` → le LLM a coché à tort, le filtre négation a corrigé
- `🚨 Anti-hallucination : N champ(s) rejeté(s)` → le LLM a inventé, le filtre a rejeté

Ces warnings sont **utiles pédagogiquement** pour montrer au stagiaire où le LLM a sous-performé et ce que le plugin a compensé automatiquement.

### Que faire si le PDF est incomplet ou faux

Si après la génération automatique le PDF a moins de 60 % de champs renseignés ou des erreurs visibles :

1. **Ouvrir le PDF dans Acrobat Reader** et corriger manuellement les champs manquants.
2. **Signer la zone AUTORITÉ DEMANDEUSE** (zone réservée à l'autorité municipale, jamais auto-remplie).
3. **Vérifier la cohérence** gravité/tendance/cases — pour un usage réel, l'opérateur reste responsable du contenu.
4. **Transmettre** via TCQ → VARA FM/HF/SAT → COD préfecture selon la fiche réflexe TCQ correspondante.

---

## 📋 Configuration recommandée pour la formation

### Variables de session optionnelles

| Variable | Effet | Quand l'utiliser |
|---|---|---|
| `SITREP_MODEL` | Force le modèle d'extraction | `/set SITREP_MODEL=qwen2.5:14b` pour passer au gros modèle si on a la RAM |
| `SITREP_TIMEOUT` | Timeout en secondes (défaut 300) | `/set SITREP_TIMEOUT=600` pour les modèles très gros |
| `SITREP_REEL` | `1` → type REEL au lieu d'EXERCICE | À utiliser uniquement en opération réelle, JAMAIS en formation |
| `SITREP_TEMPLATE` | Chemin custom du PDF | Si le PDF est ailleurs que dans le dossier IAbrain |

### Choix du modèle

| Modèle | Vitesse | Taux remplissage | Recommandation |
|---|---|---|---|
| **qwen2.5:7b** | 11-12 tok/s | 65-70/85 (76-82 %) | **Modèle de référence formation** — bon compromis |
| qwen2.5:14b | 4-5 tok/s | 70-75/85 (82-88 %) | Si RAM > 16 GB et patience |
| llama3.2:3b | 30+ tok/s | 40-50/85 (47-58 %) | Trop léger, à éviter pour SITREP |
| gpt-oss:20b (Ollama Cloud) | 25+ tok/s | 75-80/85 (88-94 %) | Si connectivité OK, **excellent** |

---

*F1GBD / ADRASEC 77 / FNRASEC — mai 2026*
*Compatible IAbrain v1.41.3 / plugin SITREP v1.1.7+*
*Distribution libre dans le cadre des formations ADRASEC départementales.*
