# Plugin SITREP ADRASEC — Macro IAbrain v1.41.2

Plugin externe d'IAbrain qui remplit **automatiquement** le formulaire
PDF `SITREP_ADRASEC.pdf` (AcroForm v1.1, F1GBD / mai 2026) à partir d'un
scénario, brouillon ou prompt direct.

## Installation

1. Copier `IAbrain_actions_sitrep.py` dans le dossier `plugins/` à côté
   d'`IAbrain.exe`.
2. Copier le **template** `SITREP_ADRASEC.pdf` à côté d'`IAbrain.exe`
   (ou dans le dossier de travail courant).
3. Lancer IAbrain. Au démarrage, le plugin est chargé automatiquement
   (message « ✅ Plugin IAbrain_actions_sitrep.py chargé (1 action) »
   dans `IAbrain.log`).
4. La **Macro 2** est pré-câblée comme « SITREP PDF » (type Action,
   action `fill_sitrep_adrasec`) dans les configurations vierges.
   Sur une config existante, configurer manuellement une macro :
   clic-droit sur la macro vierge → *Type Action* → choisir
   « SITREP ADRASEC → PDF rempli ».

## Utilisation type

### Mode 1 — Avec scénario importé (recommandé)

1. **Importer** le fichier de scénario (`prompt_HELIOS-NOIR.txt`,
   `scenario_exercice.md`, brouillon d'opérateur, etc.) via le bouton
   *Importer un fichier*.
2. **Cliquer** sur la macro « SITREP PDF ».
3. Le plugin :
   - interroge Ollama local (modèle `model_simple` ou `model` de la
     config) pour extraire les champs structurés ;
   - valide chaque valeur contre la liste autorisée du PDF ;
   - remplit le PDF et l'écrit dans le répertoire de travail
     (`SITREP_<COMMUNE>_<YYYYMMDD-HHMM>.pdf`).
4. Le chat affiche un récapitulatif Markdown avec le chemin du PDF
   généré.

### Mode 2 — Via variable de session

```
/set SITREP_TEXT = Coupure totale à Melun depuis 14h, 3 décès EHPAD,
distribution d'eau en cours stade municipal. Demande 20 m3 d'eau
P1 immédiat et 2 groupes électrogènes.
```

Puis cliquer sur la macro SITREP PDF. Le contenu de `SITREP_TEXT` est
utilisé prioritairement sur le dernier fichier importé.

### Mode 3 — En-tête seul (saisie manuelle)

Sans fichier importé et sans `SITREP_TEXT` : le plugin pré-remplit
uniquement la date, l'indicatif (`CALL` ou `INDICATIF`), l'ADRASEC,
le type EXERCICE et la signature. L'opérateur saisit le reste à la
main dans Acrobat Reader.

## Variables de session reconnues

| Variable           | Usage                                                       |
|--------------------|-------------------------------------------------------------|
| `CALL` / `INDICATIF` | Indicatif opérateur (défaut F1GBD si non posé)            |
| `ADRASEC`          | ADRASEC concernée (ex: "ADRASEC 77")                        |
| `SITREP_TEXT`      | Texte source prioritaire (override fichier importé)         |
| `SITREP_TEMPLATE`  | Chemin custom vers le PDF template                          |
| `SITREP_REEL`      | `1` / `true` / `oui` → type "REEL - REEL - REEL"            |

## Variables écrites par le plugin (après chaque exécution)

| Variable           | Contenu                                                     |
|--------------------|-------------------------------------------------------------|
| `SITREP_LAST_PDF`  | Chemin absolu du dernier PDF généré                         |
| `SITREP_LAST_DTG`  | DTG du dernier SITREP                                       |

## Recherche du template PDF (ordre de priorité)

1. Variable `SITREP_TEMPLATE` (chemin absolu ou relatif).
2. `./SITREP_ADRASEC.pdf` (répertoire de travail).
3. À côté d'`IAbrain.exe` (mode frozen) ou de `IAbrain.py` (dev).
4. Dossier parent de `plugins/`.

Si aucun n'est trouvé, l'action retourne un message d'erreur clair
listant les emplacements testés.

## Garde-fous

- **Validation stricte** des listes déroulantes : toute valeur LLM
  hors-liste est rejetée (warning + champ laissé par défaut).
- **Tolérance casse + accents** : `"élevée"`, `"Elevée"`, `"ELEVEE"`
  sont tous mappés vers `ELEVEE`.
- **JSON entouré de texte** : si le LLM ajoute du blabla autour du
  JSON, le bloc `{...}` est extrait automatiquement.
- **Tableau de demandes** : les 7 premières lignes max sont écrites ;
  les surnuméraires sont ignorées avec warning.
- **Types ignorés** : un champ inventé par le LLM (`champ_invente`)
  ne pollue pas le PDF.
- **Fallback heuristique** : si Ollama est HS, l'action coche tout de
  même les cases par mots-clés français et fixe une gravité raisonnable.
- **PDF source jamais modifié** : on lit + clone + écrit dans un
  nouveau fichier horodaté.

## Convention de nommage du PDF rempli

```
SITREP_<COMMUNE>_<YYYYMMDD-HHMM>.pdf
```

- `COMMUNE` : valeur du champ `commune` en MAJUSCULES, caractères
  non-alphanumériques remplacés par `_` (ex: `SAINT-DENIS` → `SAINT_DENIS`).
- Pas de commune extraite → `SITE`.
- Le fichier est écrit dans le **répertoire de travail** d'IAbrain.

## Mise à jour FNRASEC du formulaire

Si le PDF source évolue (nouveaux champs, nouvelles valeurs dropdown),
mettre à jour les constantes dans `IAbrain_actions_sitrep.py` :

- `TEXT_FIELDS` : noms des `/Tx`
- `CHOICE_FIELDS` : noms `/Ch` + tuple de valeurs autorisées
- `CHECKBOX_FIELDS` : noms `/Btn`
- `CHECKBOX_KEYWORDS` : mots-clés FR pour le fallback heuristique

Pour les inspecter rapidement :

```python
from pypdf import PdfReader
r = PdfReader("SITREP_ADRASEC.pdf")
for n, f in r.get_fields().items():
    print(f.get("/FT"), n, f.get("/Opt", ""))
```

---
*F1GBD / ADRASEC 77 — mai 2026 — IAbrain v1.41.2*
