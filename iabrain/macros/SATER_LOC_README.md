# Plugin SATER LOC v1.0.0

Localisation d'une balise ELT par triangulation par moindres carrés
à partir d'un fichier CSV de relèvements goniométriques.

## Installation

1. Copier `IAbrain_actions_sater_loc.py` dans le dossier `plugins/` à côté
   de `IAbrain.exe`.
2. Lancer IAbrain et vérifier dans le journal système le message :
   ```
   ✅ Plugin IAbrain_actions_sater_loc.py chargé (1 action(s))
   ```
3. Importer la macro `IAbrain_macro_SATER_LOC_CSV_v1407.iabmacro` sur un
   bouton macro libre (clic-droit → 📥 Importer une Macro).

## Workflow opérateur

```
┌─────────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│ 1. Importer CSV     │ →  │ 2. SATER LOC CSV │ →  │ 3. SATER MAP PNG    │
│    de relèvements   │    │   (triangulation)│    │   (carte OSM)       │
└─────────────────────┘    └──────────────────┘    └─────────────────────┘
                              écrit LAT, LON,         lit ces variables
                              RAYON_M, INDICATIF,     et génère le PNG
                              SITREP_TS dans la
                              session
```

### Étape 1 — Importer le CSV

Drag & drop ou bouton « Importer un fichier ». Le plugin reconnaît
automatiquement les CSV dont le nom contient `releve`, `sater` ou `goniom`.

### Étape 2 — Cliquer SATER LOC CSV

Le plugin :
- Parse le CSV, ignore les lignes `BALISE ELT` (référence pédagogique éventuelle)
- Triangule par moindres carrés sur les droites de relèvement
- Rejette automatiquement les outliers par MAD (Median Absolute Deviation)
- Calcule un rayon CEP 95 (95e percentile des résidus, plancher 50 m)
- Écrit les 5 variables dans la session :
  - `LAT`, `LON` — position estimée en degrés décimaux
  - `RAYON_M` — incertitude en mètres
  - `INDICATIF_BALISE` — ex. `ELT-ALPHA-BRAVO-CHARLIE`
  - `SITREP_TS` — horodatage du calcul

### Étape 3 — Cliquer SATER MAP PNG

La macro intégrée `osm_balise_map` consomme directement les variables
ci-dessus et génère la carte avec marqueur et cercle d'incertitude.

## Format CSV attendu

Séparateur `;`, en-tête obligatoire :
```
Indicatif;Latitude_Dec;Longitude_Dec;Latitude_DMS;Longitude_DMS;Azimut_Deg;Couleur;Date_Heure
ALPHA/3;48.403611;3.273889;48°24'13.00"N;03°16'26.00"E;26.0;#ff6b35;2026-05-04 10:13:50
...
```

Seules les colonnes `Indicatif`, `Latitude_Dec`, `Longitude_Dec` et
`Azimut_Deg` sont utilisées. Les autres peuvent être absentes.

**Tolérances** :
- Séparateur `,` (avec warning)
- Décimales avec `,` (ex. `48,403611`)
- Casse variable des en-têtes
- Lignes invalides ignorées (avec warning)

## Algorithme

### Triangulation

Pour chaque relèvement à la station `(xi, yi)` avec azimut `az_i`, la
droite de relèvement passe par `(xi, yi)` avec direction
`(sin(az_i), cos(az_i))` (convention boussole).

Sa normale est `(cos(az_i), -sin(az_i))`. L'équation de la droite est :
```
cos(az_i) · X - sin(az_i) · Y = cos(az_i) · xi - sin(az_i) · yi
```

On résout le système linéaire surdéterminé `A · [X, Y]ᵀ = b` par les
équations normales 2×2 (sans dépendance numpy).

### Rejet d'outliers (MAD itératif)

À chaque itération :
1. Triangule avec les relèvements courants
2. Calcule la médiane et le MAD (Median Absolute Deviation) des résidus
3. Rejette les relèvements dont le résidu dépasse
   `médiane + 3 · 1.4826 · MAD` (équivalent ~3σ pour distribution normale)
4. Itère jusqu'à stabilité (max 5 itérations)

L'estimateur MAD tolère jusqu'à environ 30 % d'outliers. Sur un jeu
typique ADRASEC (10–20 relèvements de 3–4 stations), le filtrage rejette
correctement les saisies aberrantes (azimut inversé, position non
réinitialisée entre deux mesures, etc.).

## Tests automatisés

```bash
python test_sater_loc.py            # 15 tests, ~2 ms
python test_sater_loc.py --verbose  # avec tracebacks complets
```

Le test inclut le CSV réel `releves_sater_ALPHA_BRAVO_CHARLIE_HECTOR`
(16 relèvements, 6 outliers à rejeter) avec validation
**erreur < 200 m vs balise réelle**.

## Validation opérationnelle

Sur l'exercice HECTOR (ADRASEC 77, 4 mai 2026) :
- 16 relèvements analysés (ALPHA/1 à 7, BRAVO/1 à 4, CHARLIE/2 à 6)
- 6 outliers rejetés automatiquement
- Position estimée : (48.429096, 3.292802)
- Position réelle de la balise : (48.429167, 3.291944)
- **Erreur : 64 m** sur une zone de 15 km × 15 km

## Notes

- `RAYON_M` reflète la **dispersion des résidus** des relèvements retenus
  (CEP 95). Sur des jeux peu redondants ou géométriquement défavorables,
  l'erreur réelle peut excéder cette valeur — utiliser la carte comme
  zone de recherche prioritaire, pas comme cercle de certitude absolue.
- Plancher `RAYON_M = 50 m` pour qu'un cercle reste visible sur la carte
  OSM même sur jeux très propres.

## Auteur

ADRASEC 77 / FNRASEC — Compatible IAbrain v1.40.7+
