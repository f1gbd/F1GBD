# Pack de macros IAbrain ADRASEC — 20 macros prêtes à l'emploi

**Version :** 1.0 (mai 2026)
**Auteur :** Jean-Louis (F1GBD) — ADRASEC 77 / FNRASEC
**Compatibilité :** IAbrain v1.40.1 ou supérieur (format `.iabmacro` v1)

Ce pack accompagne le *Guide de Rédaction de Prompts IAbrain v1.40.3*
(chapitre 7 : « Catalogue de macros pour boutons IAbrain »). Il fournit
les 20 macros documentées dans le guide, sous forme de fichiers
`.iabmacro` directement importables dans IAbrain.

---

## Contenu du pack

20 fichiers `.iabmacro` numérotés, classés par domaine :

### 1. Trafic opérationnel ADRASEC
| Fichier                      | Bouton      | Type   |
|------------------------------|-------------|--------|
| `01_sitrep.iabmacro`         | SITREP      | LLM    |
| `02_retex.iabmacro`          | RETEX       | LLM    |
| `03_indicatifs.iabmacro`     | INDICATIFS  | Action |

### 2. Conversion et nettoyage de fichiers
| Fichier                      | Bouton      | Type   |
|------------------------------|-------------|--------|
| `04_csvtomd.iabmacro`        | CSV→MD      | Action |
| `05_anonym.iabmacro`         | ANONYM      | Action |
| `06_stats.iabmacro`          | STATS       | Action |
| `07_resume.iabmacro`         | RÉSUMÉ      | LLM    |

### 3. SATER et radiolocalisation
| Fichier                      | Bouton      | Type   |
|------------------------------|-------------|--------|
| `08_sater_loc.iabmacro`      | SATER LOC   | LLM    |
| `09_sater_map.iabmacro`      | SATER MAP   | Action |
| `10_freqs.iabmacro`          | FREQS       | Action |

### 4. Documentation et requêtes RAG
| Fichier                      | Bouton      | Type   |
|------------------------------|-------------|--------|
| `11_doc.iabmacro`            | DOC         | LLM    |
| `12_proced.iabmacro`         | PROCÉD      | LLM    |
| `13_compar.iabmacro`         | COMPAR      | LLM    |

### 5. Code et configuration radio
| Fichier                      | Bouton      | Type   |
|------------------------------|-------------|--------|
| `14_py.iabmacro`             | PY          | LLM    |
| `15_debug.iabmacro`          | DEBUG       | LLM    |
| `16_vara.iabmacro`           | VARA        | LLM    |

### 6. Utilitaires conversationnels
| Fichier                      | Bouton      | Type   |
|------------------------------|-------------|--------|
| `17_trad_en.iabmacro`        | TRAD EN     | LLM    |
| `18_clair.iabmacro`          | CLAIR       | LLM    |
| `19_plan.iabmacro`           | PLAN        | LLM    |
| `20_voc.iabmacro`            | VOC         | LLM    |

---

## Installation dans IAbrain

Le format `.iabmacro` natif d'IAbrain est mono-macro : chaque fichier
correspond à une macro et un slot. La procédure d'installation se fait
donc fichier par fichier, mais reste très rapide.

### Procédure pour chaque macro

1. **Ouvrir IAbrain** v1.40.1 ou supérieur.
2. **Clic droit** sur un bouton de macro libre dans la barre des macros.
3. Le dialog d'édition s'ouvre. Cliquer sur le bouton **📥 Importer une Macro**.
4. Sélectionner le fichier `.iabmacro` souhaité (par exemple `01_sitrep.iabmacro`).
5. Les champs (label, type, prompt, RAG, action) se remplissent automatiquement.
6. Vérifier le contenu, puis cliquer sur **✓ Enregistrer** pour valider.

> **Astuce :** vous pouvez ajuster le label avant d'enregistrer (par
> exemple raccourcir « INDICATIFS » en « IND. » si votre barre est
> petite). Le label dans le fichier `.iabmacro` n'est qu'une suggestion.

### Ordre d'installation recommandé

Plutôt que d'installer les 20 macros d'un coup, commencer par les **5
macros essentielles** correspondant à votre activité dominante :

#### Profil ADRASEC opérationnel (recommandé en premier)
- `01_sitrep.iabmacro` — rédaction SITREP express
- `04_csvtomd.iabmacro` — conversion CSV (action native, instantanée)
- `08_sater_loc.iabmacro` — triangulation ELT
- `09_sater_map.iabmacro` — carte OSM de la balise (action native)
- `11_doc.iabmacro` — questions documentaires sur la base RAG

#### Profil radio amateur / développeur
- `04_csvtomd.iabmacro`
- `07_resume.iabmacro`
- `11_doc.iabmacro`
- `14_py.iabmacro`
- `15_debug.iabmacro`

#### Profil chef d'unité / encadrement
- `01_sitrep.iabmacro`
- `02_retex.iabmacro`
- `19_plan.iabmacro`
- `11_doc.iabmacro`
- `18_clair.iabmacro`

Une fois les habitudes prises, enrichir progressivement avec les
autres macros selon les besoins.

---

## Le pipeline SATER en deux clics

Les macros 8 (SATER LOC) et 9 (SATER MAP) forment un **enchaînement
opérationnel complet** :

1. **Importer** un CSV de relèvements TCQ dans IAbrain.
2. **Cliquer** sur le bouton SATER LOC.
   Le LLM calcule la position et les variables `LAT`, `LON`,
   `RAYON_M`, `INDICATIF_BALISE`, `SITREP_TS` sont capturées en session.
3. **Cliquer** sur le bouton SATER MAP.
   L'action native `osm_balise_map` lit la session, télécharge les
   tuiles OpenStreetMap, génère un PNG avec marqueur et cercle CEP 95,
   et l'affiche inline dans le chat.

Le badge **🔖 Vars (5)** en haut à droite confirme la capture entre
les deux étapes.

---

## Métalangage utilisé

Les prompts contiennent des références au métalangage IAbrain. Voir
le **chapitre 7.1** du guide pour la liste complète.

### Variables fichier (double accolade)
- `{{lastfile}}` — contenu du dernier fichier importé
- `{{lastfilename}}` — nom du dernier fichier importé
- `{{file:nom.ext}}` — contenu d'un fichier nommé spécifique

### Mots-clés crochets (contexte runtime)
- `[date]` — date du jour
- `[heure]` — heure courante
- `[indicatif]` — indicatif du profil opérateur

### Variables de session (simple accolade, capturées par macro précédente)
- `{LAT}`, `{LON}`, `{RAYON_M}` — coordonnées et précision
- `{INDICATIF_BALISE}`, `{SITREP_TS}` — métadonnées SATER

---

## Modèles LLM recommandés

Les macros LLM sont conçues pour fonctionner aussi bien en **mode
local pur** (Ollama) qu'en **mode hybride** (cloud). Voir le
**chapitre 4** du guide pour le détail.

| Macro       | Local pur       | Hybride (qualité max)        |
|-------------|-----------------|------------------------------|
| SITREP      | qwen2.5:7b      | Claude Sonnet 4.6            |
| RETEX       | qwen2.5:7b      | Claude Sonnet 4.6 / Opus     |
| RÉSUMÉ      | llama3.2:3b     | GPT-4o                       |
| SATER LOC   | qwen2.5:7b      | Claude Sonnet 4.6            |
| DOC         | qwen2.5:7b      | Claude Sonnet 4.6            |
| PROCÉD      | qwen2.5:7b      | Claude Sonnet 4.6            |
| COMPAR      | qwen2.5:7b      | Claude Sonnet 4.6            |
| PY          | qwen3-coder:30b | Claude Sonnet 4.6            |
| DEBUG       | qwen3-coder:30b | Claude Sonnet 4.6            |
| VARA        | qwen2.5:7b      | Claude Sonnet 4.6            |
| TRAD EN     | qwen2.5:7b      | GPT-4o                       |
| CLAIR       | qwen2.5:7b      | Claude Sonnet 4.6            |
| PLAN        | qwen3:8b        | Claude Sonnet 4.6 / Opus     |
| VOC         | qwen2.5:7b      | Claude Sonnet 4.6            |

Les macros de type Action (INDICATIFS, CSV→MD, ANONYM, STATS, SATER MAP,
FREQS) **n'utilisent pas de LLM** — elles sont instantanées et 100 %
locales, sans tokens consommés.

---

## Personnalisation

Les macros sont volontairement **génériques**. Adaptez-les à votre
contexte départemental après import :

- Remplacer « ADRASEC » par votre département (« ADRASEC 77 »,
  « ADRASEC 91 », etc.)
- Ajuster les destinataires SITREP (« COD » → « COD77 », « CODIS »,
  « COZ », etc.)
- Modifier les formats spécifiques (« ACP 121 » → format local en vigueur)
- Ajouter des contraintes supplémentaires propres à vos exercices

Une fois personnalisées, ré-exporter vos macros via le bouton
**📤 Exporter la Macro** dans le dialog d'édition pour les sauvegarder
ou les partager.

---

## Partage communautaire

Ce pack est conçu pour être enrichi et partagé. Si vous développez des
macros utiles à la communauté ADRASEC, deux pistes :

1. **Partage direct** entre opérateurs via Reticulum/LXMF, e-mail, ou
   support physique (clé USB lors d'exercices).
2. **Dépôt FNRASEC** centralisé (à définir avec la communauté).

Format de nommage suggéré pour les contributions :
`NN_NOM_DEPT.iabmacro` (par exemple `21_evac_77.iabmacro`).

---

## Licence et avertissement

Ces macros sont fournies **à titre opérationnel** par F1GBD pour la
communauté ADRASEC / FNRASEC, sans garantie d'aucune sorte.

L'opérateur reste **seul responsable** :
- de la vérification des sorties produites par les LLM avant transmission
  ou exploitation opérationnelle ;
- du choix du mode (LOCAL PUR vs HYBRIDE) en fonction de la sensibilité
  des données traitées ;
- de l'adaptation des macros aux procédures locales en vigueur.

Les LLM peuvent halluciner, en particulier sur les acronymes
polysémiques et les valeurs numériques précises (fréquences, ports COM,
coordonnées). **Toujours relire** une réponse LLM avant de l'utiliser
en transmission opérationnelle.

---

73 de F1GBD — *Mai 2026*
