# IAbrain — Dossier `plugins/`

Ce dossier contient les **plugins externes d'actions natives** d'IAbrain, chargés automatiquement au démarrage à partir de la version **v1.40.7**.

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

## 📦 Plugins livrés avec IAbrain v1.40.7

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
- **Aucune dépendance non-stdlib** : seuls les modules standards Python sont garantis disponibles dans la distribution PyInstaller. Si votre plugin nécessite `numpy`, `requests`, `pillow`, etc., ces packages doivent être présents dans l'environnement Python utilisateur ou bundlés à part.
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
- [Changelog v1.40.x](../README.md#-évolution-récente---v133--v140)
- [Documentation des macros et actions natives](../README.md#-macros-et-actions-natives-v137)

---

*Documentation à jour pour IAbrain v1.40.7 — Système de plugins externes.*
