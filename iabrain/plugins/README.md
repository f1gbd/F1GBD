# IAbrain — Dossier `plugins/`

Ce dossier contient les **plugins externes d'actions natives** d'IAbrain, chargés automatiquement au démarrage à partir de la version **v1.40.7**, et enrichis au fil des versions ultérieures (SITREP PDF en v1.41.2).

Un plugin est un simple fichier Python qui ajoute des actions natives à IAbrain (chiffrement, conversion, calcul, génération de cartes…) sans modification ni recompilation de l'exécutable.

---

## 🚀 Comment ça marche

Au lancement d'`IAbrain.exe`, le moteur scanne ce dossier et charge automatiquement tous les fichiers nommés selon le motif :

```
IAbrain_actions_*.py
```

Pour chaque plugin chargé, un message de confirmation apparaît dans le journal système au démarrage :

```
✅ Plugin IAbrain_actions_soe.py chargé (2 action(s))
```

Les actions exposées par les plugins apparaissent ensuite dans le **sélecteur d'action** lors de la configuration d'une macro de type **⚙️ Action** (clic-droit sur un bouton macro → onglet Action).

---

## 📦 Plugins livrés avec IAbrain

| Plugin | Livré en | Actions | Détail |
|---|---|---|---|
| `IAbrain_actions_soe.py` | v1.40.7 | `soe_encode`, `soe_decode` | Chiffrement SOE 1942 (double transposition colonnaire) |
| `IAbrain_actions_sitrep.py` | **v1.41.2** | `fill_sitrep_adrasec` | Remplissage automatique du SITREP PDF ADRASEC (AcroForm v1.1) |

---

### `IAbrain_actions_soe.py` — Chiffrement SOE 1942

Implémente le chiffrement **double transposition colonnaire** historique utilisé par les agents du **Special Operations Executive** britannique pendant la Seconde Guerre mondiale.

Deux actions :

| Action | Variables lues | Variables écrites |
|---|---|---|
| **`soe_encode`** — *SOE — Coder (double transposition)* | `CLE1`, `CLE2`, `MESSAGE` | `CRYPTO` |
| **`soe_decode`** — *SOE — Décoder (double transposition)* | `CLE1`, `CLE2`, `CRYPTO` | `MESSAGE_DECODE` |

#### Conventions cryptographiques

- Numérotation alphabétique des colonnes ; doublons numérotés de gauche à droite.
- Remplissage des grilles ligne par ligne, gauche-droite haut-bas.
- Pas de bourrage X intermédiaire entre les deux transpositions.
- Bourrage X final pour atteindre des groupes de 5 caractères.
- Sortie en groupes de 5, format CW/Morse historique.

#### Chaîne d'utilisation type pour exercice ADRASEC

1. **Configurer les variables** dans la zone de saisie :
   ```
   /set CLE1=RIENNESERTDECOURIR
   /set CLE2=ILFAUTPARTIRAPOINT
   /set MESSAGE=CONFIRME OPERATION TERRAIN HECTOR A PARTIR DU JEUDI NEUF MARS STOP FIN
   ```
   L'indicateur `🔖 Vars (3)` apparaît en haut à droite.

2. **Cliquer sur la macro `SOE COD`** (action `soe_encode`).
   → Le cryptogramme est calculé, affiché, et **stocké automatiquement** dans la variable `{CRYPTO}`. L'indicateur passe à `🔖 Vars (4)`.

3. **Cliquer sur la macro `SOE DECODE`** (action `soe_decode`).
   → Le message clair est restitué dans la variable `{MESSAGE_DECODE}`. L'indicateur passe à `🔖 Vars (5)`.

Toute la chaîne s'exécute **instantanément, sans LLM, sans tokens, sans Internet**, et le résultat est **strictement déterministe** — propriété essentielle pour les exercices où plusieurs opérateurs doivent décoder le même cryptogramme.

#### Pourquoi ne pas utiliser un LLM pour ça ?

La double transposition colonnaire est un **algorithme de permutation de séquence**. Les LLM, même 32B, ne sont **pas fiables** sur cette classe de tâche : ils intervertissent des rangs, sautent des étapes, ou tronquent leurs sorties. Une macro Action déterministe garantit qu'**un message chiffré par un opérateur sera toujours décodable par un autre** — propriété indispensable en cadre opérationnel ADRASEC/FNRASEC.

---

### `IAbrain_actions_sitrep.py` — Remplissage automatique du SITREP PDF ADRASEC *(v1.41.2)*

Remplit automatiquement le formulaire AcroForm officiel **`SITREP_ADRASEC.pdf`** (v1.1, F1GBD / mai 2026) à partir d'un scénario d'exercice importé, d'un brouillon d'opérateur, ou d'un prompt direct. Cible **85 champs** : 33 zones de texte, 9 listes déroulantes, 15 cases à cocher et 28 cellules du tableau « demande de moyens » (7 lignes × 4 colonnes Type/Qté/Unité/Délai/Prio + Lieu).

Une action :

| Action | Variables lues | Variables écrites |
|---|---|---|
| **`fill_sitrep_adrasec`** — *SITREP ADRASEC → PDF rempli* | `SITREP_TEXT`, `SITREP_TEMPLATE`, `CALL`, `INDICATIF`, `ADRASEC`, `SITREP_REEL` | `SITREP_LAST_PDF`, `SITREP_LAST_DTG` |

#### Principe de fonctionnement

1. **Localise** le PDF template `SITREP_ADRASEC.pdf` (variable de session `SITREP_TEMPLATE` → CWD → à côté de l'exécutable → dossier parent de `plugins/`).
2. **Récupère** le texte source : variable de session `SITREP_TEXT` en priorité, sinon dernier fichier importé.
3. **Appelle Ollama local** (modèle `model_simple` puis `model` de la config) avec un prompt d'extraction structurée qui demande un **JSON strict** conforme au schéma SITREP.
4. **Valide** chaque champ contre les listes autorisées du PDF (priorités, gravités, modes TCQ, types de besoin, …). Tolérance casse + accents : `"Élevée"` → `ELEVEE`, `"vara fm"` → `VARA FM`.
5. **Écrit** le PDF rempli dans le CWD sous le nom `SITREP_<COMMUNE>_<YYYYMMDD-HHMM>.pdf` (l'AcroForm d'origine est préservé, `/NeedAppearances` est activé pour la régénération des glyphes).
6. **Renvoie** un récapitulatif Markdown dans le chat IAbrain (chemin du PDF, tableau des champs renseignés, cases cochées, warnings).

#### Quatre niveaux de robustesse

1. **LLM disponible + JSON propre** → tous les champs validés sont écrits.
2. **JSON entouré de texte** → bloc `{...}` extrait automatiquement, warning émis.
3. **LLM indisponible** → bascule heuristique : 12 mots-clés FR (`coupure électrique`, `gsm`, `ehpad`, `pénurie carburant`, …) cochent les bonnes cases ; gravité inférée du nombre de cases.
4. **Aucune source** → en-tête seul pré-rempli (DTG, indicatif, ADRASEC, type EXERCICE, signature), reste vierge pour saisie manuelle.

#### Dépendances

Le plugin requiert le module Python **`pypdf`** (lecture et écriture d'AcroForm). Ce package est bundlé dans la distribution officielle d'IAbrain v1.41.2+. En mode développement, installer avec :

```bash
pip install pypdf
```

#### Chaîne d'utilisation type pour exercice ADRASEC

1. **Configurer les variables** dans la zone de saisie :
   ```
   /set CALL=F1GBD
   /set ADRASEC=ADRASEC 77
   ```

2. **Importer un scénario** (`prompt_HELIOS-NOIR.txt`, brouillon d'opérateur, RETEX, …) via le bouton *Importer un fichier*. L'indicateur `🔖 Vars (2)` est visible en haut.

3. **Cliquer sur la macro `📋 SITREP PDF`** (action `fill_sitrep_adrasec`, pré-câblée sur Macro 2 en v1.41.2+).
   → Ollama extrait les champs en JSON, validation stricte champ par champ, PDF rempli généré dans le CWD. Le récapitulatif Markdown s'affiche, les variables `SITREP_LAST_PDF` et `SITREP_LAST_DTG` sont posées (indicateur `🔖 Vars (4)`).

4. **Ouvrir le PDF**, signer la zone *AUTORITE DEMANDEUSE*, transmettre via TCQ → VARA FM/HF/SAT → COD préfecture.

#### Pourquoi un PDF rempli plutôt qu'un texte Markdown ?

Le formulaire `SITREP_ADRASEC.pdf` est le **support officiel FNRASEC** transmis aux autorités (préfecture, COD, mairies). Sa structure AcroForm est conçue pour être **lisible mécaniquement** (extraction des champs côté COD pour main courante, archivage horodaté, parseur automatique). Un texte libre — même bien structuré en Markdown — perd cette propriété et nécessite une saisie manuelle côté destinataire.

Le plugin garantit aussi que **les valeurs des dropdowns sont conformes** à la nomenclature FNRASEC (priorités `ROUTINE/PRIORITAIRE/URGENT/FLASH`, gravités `FAIBLE/MODEREE/ELEVEE/CRITIQUE`, modes TCQ `VARA HF/FM/SAT/PACKET/ARDOP/LXMF`) — un LLM produisant directement le PDF inventerait régulièrement des valeurs hors-liste qui seraient silencieusement rejetées côté Acrobat.

#### Documentation détaillée

Voir le fichier dédié **[`LISEZMOI_SITREP.md`](LISEZMOI_SITREP.md)** dans ce même dossier pour :

- L'ordre de recherche du PDF template (4 emplacements testés)
- La liste complète des variables de session lues / écrites
- La procédure de mise à jour si le formulaire FNRASEC évolue
- Les exemples des trois modes d'utilisation (scénario importé, variable de session, en-tête seul)

---

## 🔧 Écrire votre propre plugin

Un plugin est un simple fichier Python qui expose **trois fonctions** :

```python
# IAbrain_actions_monplugin.py

def is_action(action_id: str) -> bool:
    """Retourne True si action_id est gérée par ce plugin."""
    return action_id in ("mon_action_1", "mon_action_2")

def list_actions() -> list[tuple[str, str, str]]:
    """Retourne la liste des (id, libellé, description) à afficher dans le sélecteur."""
    return [
        ("mon_action_1", "Mon plugin — Action 1", "Description longue affichée sous le sélecteur."),
        ("mon_action_2", "Mon plugin — Action 2", "Description longue de l'action 2."),
    ]

def execute_action(action_id, imported_files=(), options=None):
    """Exécute l'action et retourne (markdown_à_afficher, liste_de_warnings).

    options peut contenir :
      - "session_vars" : dict snapshot des variables de session (lecture)
      - "session_vars_manager" : manager vivant pour ÉCRITURE (v1.40.7+)
    """
    sv = (options or {}).get("session_vars", {})
    mgr = (options or {}).get("session_vars_manager")

    # Exemple : lire une variable
    nom = sv.get("INDICATIF", "")

    # Exemple : écrire une variable (v1.40.7+)
    if mgr is not None:
        mgr.set("RESULTAT", "valeur calculée")
        mgr.save()

    # Retour : markdown + warnings
    md = f"## Résultat\n\nIndicatif lu : `{nom}`"
    return md, []
```

### Contraintes

- **Nom de fichier** : doit commencer par `IAbrain_actions_` et finir par `.py`.
- **Dépendances** : les modules de la bibliothèque standard Python sont toujours disponibles. Les modules tiers bundlés dans la distribution PyInstaller (à jour pour IAbrain v1.41.2+) incluent : `requests`, `numpy`, `Pillow`, `staticmap`, `pypdf`. Si votre plugin nécessite une autre dépendance non listée (`opencv`, `pandas`, …), elle doit être présente dans l'environnement Python utilisateur ou bundlée à part — sinon le plugin se chargera mais échouera au premier appel d'action avec un `ModuleNotFoundError`.
- **Imports relatifs** : si votre plugin importe ses propres sous-modules placés dans ce même dossier, le chargement les trouvera (le dossier `plugins/` est ajouté à `sys.path` au démarrage).
- **Robustesse** : capturez vos exceptions internes et retournez plutôt un markdown d'erreur explicite. Une exception non gérée empêchera votre action de produire un résultat exploitable, mais ne crashera pas IAbrain.

### Test en mode développement

Avant la compilation finale, vous pouvez tester votre plugin directement :

```bash
python IAbrain.py
```

Le dossier `plugins/` est cherché à côté du script Python, donc il suffit d'y déposer votre fichier et de relancer.

---

## ⚠️ Sécurité — IMPORTANT

Le code des plugins **s'exécute avec les mêmes droits que l'application IAbrain**. Un plugin malveillant peut lire des fichiers, accéder au réseau, ou modifier le système.

**N'installez que des plugins de sources fiables :**

- ✅ Plugins livrés officiellement avec IAbrain (signés par le mainteneur)
- ✅ Plugins développés par votre équipe ADRASEC ou FNRASEC
- ✅ Plugins partagés au sein de la communauté ADRASEC après revue de code
- ❌ Plugins reçus de sources inconnues, par e-mail, ou téléchargés sur des sites tiers

Pour désactiver temporairement un plugin sans le supprimer, renommez-le en ajoutant un suffixe :

```
IAbrain_actions_soe.py        →  IAbrain_actions_soe.py.disabled
```

Le motif de chargement (`IAbrain_actions_*.py`) ne le matchera plus et il sera ignoré au prochain lancement.

Pour désactiver tous les plugins d'un coup, supprimez ou renommez le dossier `plugins/`.

---

## 📋 Diagnostic

En cas de problème, consultez :

1. **Le journal système d'IAbrain** au démarrage : tout plugin en erreur est listé avec un message `❌` explicite.
2. **Le fichier `IAbrain.log`** à côté de l'exécutable : trace détaillée de chaque tentative de chargement.

Erreurs typiques :

| Symptôme | Cause probable | Remède |
|---|---|---|
| `❌ Plugin X.py : interface incomplète (manque execute_action)` | Le plugin n'expose pas les 3 fonctions requises | Vérifier le contrat d'interface ci-dessus |
| `❌ Plugin X.py : ModuleNotFoundError: No module named 'numpy'` | Dépendance non-stdlib absente | Installer la dépendance, ou réécrire le plugin sans elle |
| `❌ Plugin X.py : SyntaxError` | Fichier Python invalide | Tester avec `python -m py_compile X.py` |
| Plugin chargé mais aucune action visible dans le sélecteur | `list_actions()` retourne une liste vide | Vérifier le retour de `list_actions()` |

---

## 🔗 Liens utiles

- [README principal d'IAbrain](../README.md)
- [Changelog v1.40.x — Plugins externes](../README.md#-évolution-récente---v133--v140)
- [Changelog v1.41.x — Auto-exécution macros et SITREP PDF](../README.md#-v141x--auto-exécution-de-macros-depuis-le-llm-et-sitrep-pdf-auto-rempli)
- [Documentation des macros et actions natives](../README.md#-macros-et-actions-natives-v137)
- [Documentation détaillée du plugin SITREP](LISEZMOI_SITREP.md)

---

*Documentation à jour pour IAbrain v1.41.2 — Système de plugins externes (v1.40.7+), plugin SITREP PDF (v1.41.2+).*
