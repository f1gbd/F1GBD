# -*- coding: utf-8 -*-
"""
IAbrain_actions_sater_loc.py — Plugin SATER LOC v1.0.0

Localisation d'une balise ELT par triangulation par moindres carrés
à partir d'un fichier CSV de relèvements goniométriques importé dans
la session IAbrain.

Action exposée :
    sater_loc_from_csv

Variables LUES :
    (aucune — les données viennent du CSV importé)

Variables ÉCRITES dans la session (consommées par osm_balise_map) :
    LAT               — latitude estimée (degrés décimaux)
    LON               — longitude estimée (degrés décimaux)
    RAYON_M           — incertitude (CEP 95) en mètres
    INDICATIF_BALISE  — identifiant lisible (ex. ELT-ALPHA-BRAVO-CHARLIE)
    SITREP_TS         — horodatage du calcul

Format CSV attendu (séparateur ';') :
    Indicatif;Latitude_Dec;Longitude_Dec;Latitude_DMS;Longitude_DMS;
    Azimut_Deg;Couleur;Date_Heure
Seules les colonnes Indicatif, Latitude_Dec, Longitude_Dec et Azimut_Deg
sont utilisées ; les autres sont ignorées.

Algorithme :
  1. Filtrage des lignes "BALISE ELT" (référence pédagogique éventuelle)
  2. Projection équirectangulaire locale autour du barycentre
  3. Triangulation par moindres carrés (système 2x2 normal, sans numpy)
  4. Rejet itératif des outliers par MAD (Median Absolute Deviation),
     seuil = médiane + 3·1.4826·MAD, plancher 25 m, max 5 itérations
  5. Rayon CEP 95 calculé sur les résidus finaux, plancher 50 m

Auteur : ADRASEC 77 / FNRASEC
Compatible : IAbrain v1.40.7+
"""

from __future__ import annotations

import csv
import io
import math
import re
from datetime import datetime
from typing import Any, List, Optional, Sequence, Tuple

__version__ = "1.0.0"

# ===========================================================================
# Identifiant de l'action
# ===========================================================================

ACTION_SATER_LOC = "sater_loc_from_csv"


def is_action(action_id: str) -> bool:
    return (action_id or "").strip() == ACTION_SATER_LOC


def list_actions() -> List[Tuple[str, str, str]]:
    return [(
        ACTION_SATER_LOC,
        "SATER — Localiser depuis CSV de relèvements",
        "Lit le dernier fichier CSV de relèvements goniométriques importé "
        "dans la session, calcule la position estimée de la balise ELT "
        "par triangulation par moindres carrés (avec rejet automatique "
        "des outliers par MAD), et écrit les variables LAT, LON, RAYON_M, "
        "INDICATIF_BALISE, SITREP_TS dans la session. Ces variables sont "
        "ensuite consommées directement par la macro Action SATER MAP PNG "
        "(osm_balise_map) pour générer la carte OpenStreetMap. Format CSV "
        "attendu : Indicatif;Latitude_Dec;Longitude_Dec;...;Azimut_Deg "
        "(séparateur ';')."
    )]


# ===========================================================================
# Géométrie et triangulation (sans dépendance numpy)
# ===========================================================================

R_EARTH = 6_371_000.0  # rayon moyen terrestre en mètres


def _latlon_to_xy(lat: float, lon: float,
                  lat0: float, lon0: float) -> Tuple[float, float]:
    """Projection équirectangulaire locale (mètres autour de lat0/lon0).
    Suffisamment précise sur des distances < 50 km."""
    x = R_EARTH * math.radians(lon - lon0) * math.cos(math.radians(lat0))
    y = R_EARTH * math.radians(lat - lat0)
    return x, y


def _xy_to_latlon(x: float, y: float,
                  lat0: float, lon0: float) -> Tuple[float, float]:
    lat = lat0 + math.degrees(y / R_EARTH)
    lon = lon0 + math.degrees(x / (R_EARTH * math.cos(math.radians(lat0))))
    return lat, lon


def _triangulate_lsq(stations: Sequence[Tuple[float, float, float]]
                     ) -> Tuple[float, float, List[float]]:
    """Triangulation par moindres carrés.

    stations : liste de (x_m, y_m, az_rad) avec convention boussole
               (0 = Nord, 90 = Est, sens horaire).

    Retourne (X, Y, residuals) où residuals[i] est la distance
    perpendiculaire (m) entre la position estimée et la droite de
    relèvement i.

    Implémentation : pour chaque relèvement, la droite passe par (xi, yi)
    avec direction (sin(az), cos(az)). Sa normale est (cos(az), -sin(az)).
    L'équation de droite s'écrit donc :
        cos(az)*X - sin(az)*Y = cos(az)*xi - sin(az)*yi
    Système 2 inconnues, n équations, résolu par équations normales 2x2.
    """
    n = len(stations)
    if n < 2:
        raise ValueError(
            f"Au moins 2 relèvements requis pour la triangulation, "
            f"{n} fourni(s)."
        )

    a11 = a12 = a22 = 0.0
    b1 = b2 = 0.0
    for x, y, az in stations:
        nx = math.cos(az)
        ny = -math.sin(az)
        rhs = nx * x + ny * y
        a11 += nx * nx
        a12 += nx * ny
        a22 += ny * ny
        b1 += nx * rhs
        b2 += ny * rhs

    det = a11 * a22 - a12 * a12
    if abs(det) < 1e-9:
        raise ValueError(
            "Systeme singulier : tous les relevements sont paralleles ou "
            "issus de la meme position. Triangulation impossible."
        )
    X = (a22 * b1 - a12 * b2) / det
    Y = (a11 * b2 - a12 * b1) / det

    residuals = []
    for x, y, az in stations:
        nx = math.cos(az)
        ny = -math.sin(az)
        d = abs(nx * X + ny * Y - (nx * x + ny * y))
        residuals.append(d)

    return X, Y, residuals


def _median(values: Sequence[float]) -> float:
    s = sorted(values)
    n = len(s)
    return s[n // 2] if n % 2 == 1 else (s[n // 2 - 1] + s[n // 2]) / 2.0


def _percentile(values: Sequence[float], p: float) -> float:
    s = sorted(values)
    n = len(s)
    if n == 1:
        return s[0]
    k = (p / 100.0) * (n - 1)
    f = int(k)
    c = min(f + 1, n - 1)
    return s[f] + (s[c] - s[f]) * (k - f)


def _filter_outliers_mad(stations_full: Sequence[Tuple[float, float, float]],
                         max_iter: int = 5
                         ) -> Tuple[List[int], float, float, List[float]]:
    """Filtrage iteratif des outliers par MAD."""
    indices = list(range(len(stations_full)))
    X = Y = 0.0
    residuals: List[float] = []

    for _ in range(max_iter):
        if len(indices) < 2:
            break
        sub = [stations_full[i] for i in indices]
        X, Y, residuals = _triangulate_lsq(sub)

        median_r = _median(residuals)
        mad = _median([abs(r - median_r) for r in residuals])
        # Plancher 25 m pour ne pas rejeter sur un jeu trop propre
        threshold = max(median_r + 3.0 * 1.4826 * mad, 25.0)

        new_indices = [
            indices[i] for i, r in enumerate(residuals) if r <= threshold
        ]
        if len(new_indices) == len(indices):
            break
        if len(new_indices) < 2:
            break
        indices = new_indices

    if len(indices) >= 2:
        sub = [stations_full[i] for i in indices]
        X, Y, residuals = _triangulate_lsq(sub)
    return indices, X, Y, residuals


# ===========================================================================
# Lecture du CSV
# ===========================================================================

def _parse_csv_releves(content: str
                       ) -> Tuple[List[Tuple[str, float, float, float]],
                                  List[str]]:
    """Parse un CSV de relevements TCQ/SATER.

    Retourne (relevements, warnings) avec relevements = liste de tuples
    (indicatif, lat_dec, lon_dec, azimut_deg).
    """
    warnings: List[str] = []
    relevements: List[Tuple[str, float, float, float]] = []

    if not content or not content.strip():
        raise ValueError("Le fichier CSV est vide.")

    sample = content[:1024]
    sep = ';' if sample.count(';') >= sample.count(',') else ','
    if sep != ';':
        warnings.append(
            f"Separateur CSV detecte : '{sep}' (le format SATER standard "
            "utilise ';')."
        )

    reader = csv.DictReader(io.StringIO(content), delimiter=sep)
    if reader.fieldnames is None:
        raise ValueError("CSV vide ou sans en-tete.")

    field_map = {f.strip().lower(): f for f in reader.fieldnames}
    required = {"indicatif", "latitude_dec", "longitude_dec", "azimut_deg"}
    missing = required - set(field_map.keys())
    if missing:
        raise ValueError(
            f"Colonnes manquantes dans le CSV : {sorted(missing)}.\n"
            f"Colonnes trouvees : {list(field_map.keys())}\n"
            "Format attendu : Indicatif;Latitude_Dec;Longitude_Dec;...;"
            "Azimut_Deg;... (separateur ';')"
        )

    f_indic = field_map["indicatif"]
    f_lat = field_map["latitude_dec"]
    f_lon = field_map["longitude_dec"]
    f_az = field_map["azimut_deg"]

    n_balise = 0
    n_invalid = 0

    for row in reader:
        indic = (row.get(f_indic) or "").strip()
        if not indic:
            n_invalid += 1
            continue

        if indic.upper().startswith("BALISE"):
            n_balise += 1
            continue

        try:
            lat = float((row.get(f_lat) or "").replace(",", "."))
            lon = float((row.get(f_lon) or "").replace(",", "."))
            az = float((row.get(f_az) or "").replace(",", "."))
        except (ValueError, AttributeError):
            n_invalid += 1
            warnings.append(f"Ligne ignoree (valeur non numerique) : {indic}")
            continue

        if not (-90.0 <= lat <= 90.0) or not (-180.0 <= lon <= 180.0):
            n_invalid += 1
            warnings.append(
                f"Ligne ignoree (lat/lon hors plage) : {indic} ({lat}, {lon})"
            )
            continue

        az = az % 360.0
        relevements.append((indic, lat, lon, az))

    if n_balise:
        warnings.append(
            f"{n_balise} ligne(s) BALISE ELT ignoree(s) (reference "
            "pedagogique non utilisee pour la triangulation)."
        )

    return relevements, warnings


# ===========================================================================
# Helpers IAbrain et formatage
# ===========================================================================

def _set_session_var(options: Optional[dict], name: str, value: str) -> bool:
    """Ecrit une variable de session via le manager si expose."""
    if not options or not isinstance(options, dict):
        return False
    mgr = options.get("session_vars_manager")
    if mgr is None:
        return False
    try:
        ok = mgr.set(name, value)
        if ok:
            try:
                mgr.save()
            except Exception:
                pass
        return bool(ok)
    except Exception:
        return False


def _find_csv_in_imported(imported_files: Sequence[Tuple[str, str]]
                          ) -> Optional[Tuple[str, str]]:
    """Cherche le CSV de relevements le plus pertinent."""
    if not imported_files:
        return None
    csvs = [(n, c) for n, c in imported_files if n.lower().endswith(".csv")]
    if not csvs:
        return None
    for name, content in reversed(csvs):
        nlow = name.lower()
        if "releve" in nlow or "sater" in nlow or "goniom" in nlow:
            return name, content
    return csvs[-1]


def _format_dms(deg: float, is_lat: bool) -> str:
    """Format degres/minutes/secondes pour affichage."""
    hemi = ("N" if deg >= 0 else "S") if is_lat else ("E" if deg >= 0 else "W")
    deg = abs(deg)
    d = int(deg)
    m_total = (deg - d) * 60.0
    m = int(m_total)
    s = (m_total - m) * 60.0
    return f"{d:02d}°{m:02d}'{s:05.2f}\"{hemi}"


def _build_indicatif_balise(kept_indices: Sequence[int],
                            relevs: Sequence[Tuple[str, float, float, float]]
                            ) -> str:
    """Construit ELT-XXX-YYY-ZZZ depuis les prefixes des releves retenus."""
    seen = []
    for i in kept_indices:
        m = re.match(r"^([A-Za-zÀ-ÿ_-]+)", relevs[i][0])
        if m:
            p = m.group(1).upper()
            if p not in seen:
                seen.append(p)
    if not seen:
        return "ELT-INCONNU"
    return "ELT-" + "-".join(seen[:3])


# ===========================================================================
# Action principale
# ===========================================================================

def _action_sater_loc(imported_files: Sequence[Tuple[str, str]],
                      options: Any) -> Tuple[str, List[str]]:
    warnings: List[str] = []

    csv_entry = _find_csv_in_imported(imported_files)
    if csv_entry is None:
        return (
            "## ❌ SATER LOC — Aucun CSV trouve\n\n"
            "Aucun fichier `.csv` n'a ete importe dans la session.\n\n"
            "**Action requise** : importez d'abord le fichier de "
            "relevements (drag & drop ou bouton « Importer un fichier »), "
            "puis relancez la macro.",
            warnings,
        )
    csv_name, csv_content = csv_entry

    try:
        relevs, parse_warnings = _parse_csv_releves(csv_content)
        warnings.extend(parse_warnings)
    except Exception as e:
        return (
            f"## ❌ SATER LOC — Erreur de lecture du CSV\n\n"
            f"**Fichier** : `{csv_name}`\n\n"
            f"**Erreur** : {e}",
            warnings,
        )

    n_relevs = len(relevs)
    if n_relevs < 2:
        return (
            f"## ❌ SATER LOC — Trop peu de relevements\n\n"
            f"**Fichier** : `{csv_name}`\n\n"
            f"Au moins 2 relevements valides sont necessaires pour la "
            f"triangulation, {n_relevs} trouve(s).",
            warnings,
        )

    lat0 = sum(r[1] for r in relevs) / n_relevs
    lon0 = sum(r[2] for r in relevs) / n_relevs
    stations_full = [
        (*_latlon_to_xy(lat, lon, lat0, lon0), math.radians(az))
        for _, lat, lon, az in relevs
    ]

    try:
        kept, X, Y, residuals = _filter_outliers_mad(stations_full)
    except ValueError as e:
        return (
            f"## ❌ SATER LOC — Echec de triangulation\n\n"
            f"{e}\n\n"
            "Verifiez que les relevements ne sont pas tous paralleles "
            "ou pris depuis la meme position.",
            warnings,
        )

    if len(kept) < 2:
        return (
            f"## ❌ SATER LOC — Trop d'outliers detectes\n\n"
            f"Sur {n_relevs} relevements, seuls {len(kept)} ont passe "
            f"le filtre MAD. La triangulation n'est pas fiable.\n\n"
            f"Verifiez la qualite des relevements (azimuts coherents, "
            f"saisie correcte).",
            warnings,
        )

    lat_est, lon_est = _xy_to_latlon(X, Y, lat0, lon0)
    rms = math.sqrt(sum(r * r for r in residuals) / len(residuals))
    cep95 = _percentile(residuals, 95.0)
    rayon_m = max(round(cep95), 50)

    indicatif_balise = _build_indicatif_balise(kept, relevs)
    sitrep_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    written = (
        _set_session_var(options, "LAT", f"{lat_est:.6f}") and
        _set_session_var(options, "LON", f"{lon_est:.6f}") and
        _set_session_var(options, "RAYON_M", str(rayon_m)) and
        _set_session_var(options, "INDICATIF_BALISE", indicatif_balise) and
        _set_session_var(options, "SITREP_TS", sitrep_ts)
    )

    rejected = [i for i in range(n_relevs) if i not in kept]
    md = []
    md.append("## 🎯 SATER LOC — Localisation par triangulation")
    md.append("")
    md.append(f"**Fichier source** : `{csv_name}`  ")
    md.append(f"**Relevements analyses** : {n_relevs}  ")
    rejet_txt = (f"(rejet de {len(rejected)} outlier(s))" if rejected
                 else "(aucun outlier detecte)")
    md.append(f"**Relevements retenus** : {len(kept)} {rejet_txt}")
    md.append("")
    md.append("### Position estimee")
    md.append("```")
    md.append(f"Latitude  : {lat_est:.6f}°  ({_format_dms(lat_est, True)})")
    md.append(f"Longitude : {lon_est:.6f}°  ({_format_dms(lon_est, False)})")
    md.append(f"Rayon CEP95 : {rayon_m} m  (RMS residus : {rms:.1f} m)")
    md.append(f"Indicatif balise : {indicatif_balise}")
    md.append(f"Horodatage : {sitrep_ts}")
    md.append("```")
    md.append("")

    md.append("### Relevements retenus")
    md.append("| Indicatif | Lat | Lon | Azimut | Residu |")
    md.append("|---|---|---|---|---|")
    for idx, i in enumerate(kept):
        ind, lat, lon, az = relevs[i]
        md.append(f"| {ind} | {lat:.4f} | {lon:.4f} | "
                  f"{az:.0f}° | {residuals[idx]:.0f} m |")

    if rejected:
        md.append("")
        md.append("### Relevements rejetes (outliers)")
        md.append("| Indicatif | Lat | Lon | Azimut |")
        md.append("|---|---|---|---|")
        for i in rejected:
            ind, lat, lon, az = relevs[i]
            md.append(f"| {ind} | {lat:.4f} | {lon:.4f} | {az:.0f}° |")

    md.append("")
    if written:
        md.append(
            "✅ Variables `{LAT}`, `{LON}`, `{RAYON_M}`, "
            "`{INDICATIF_BALISE}`, `{SITREP_TS}` stockees automatiquement "
            "dans la session."
        )
        md.append("")
        md.append(
            "👉 **Etape suivante** : cliquer sur la macro **SATER MAP PNG** "
            "pour generer la carte OpenStreetMap avec marqueur et cercle "
            "d'incertitude."
        )
    else:
        md.append(
            "ℹ️ Pour stocker les variables manuellement, copier les "
            "commandes ci-dessous dans la zone de saisie :"
        )
        md.append("```")
        md.append(f"/set LAT={lat_est:.6f}")
        md.append(f"/set LON={lon_est:.6f}")
        md.append(f"/set RAYON_M={rayon_m}")
        md.append(f"/set INDICATIF_BALISE={indicatif_balise}")
        md.append(f"/set SITREP_TS={sitrep_ts}")
        md.append("```")

    md.append("")
    md.append(
        "_Note : RAYON_M reflete la **dispersion des residus** des "
        "relevements retenus (CEP 95). Sur des jeux peu redondants ou "
        "geometriquement defavorables, l'erreur reelle peut exceder cette "
        "valeur — utiliser la carte comme **zone de recherche prioritaire**, "
        "pas comme cercle de certitude absolue._"
    )

    return "\n".join(md), warnings


# ===========================================================================
# Point d'entree IAbrain
# ===========================================================================

def execute_action(action_id: str,
                   imported_files: Sequence[Tuple[str, str]] = (),
                   options: Any = None) -> Tuple[str, List[str]]:
    aid = (action_id or "").strip()
    if aid == ACTION_SATER_LOC:
        return _action_sater_loc(imported_files, options)
    return (
        f"## ❌ Action inconnue : `{aid}`\n\n"
        f"Action disponible dans ce plugin : `{ACTION_SATER_LOC}`",
        [],
    )


# ===========================================================================
# Autotest
# ===========================================================================

def _autotest():
    sample_csv = (
        "Indicatif;Latitude_Dec;Longitude_Dec;Latitude_DMS;Longitude_DMS;"
        "Azimut_Deg;Couleur;Date_Heure\n"
        "ALPHA/3;48.403611;3.273889;_;_;26.0;#fff;2026-05-04 10:13:50\n"
        "ALPHA/5;48.430278;3.285556;_;_;100.0;#fff;2026-05-04 10:18:59\n"
        "BRAVO/1;48.419167;3.293056;_;_;359.0;#fff;2026-05-04 13:04:20\n"
        "BRAVO/4;48.433333;3.290000;_;_;155.0;#fff;2026-05-04 11:43:21\n"
        "CHARLIE/5;48.438611;3.281667;_;_;142.0;#fff;2026-05-04 13:05:24\n"
    )

    class MockMgr:
        def __init__(self): self._v = {}
        def set(self, n, v): self._v[n] = str(v); return True
        def save(self): pass
        def get(self, n): return self._v.get(n)

    mgr = MockMgr()
    md, warns = execute_action(
        ACTION_SATER_LOC,
        imported_files=[("releves_test.csv", sample_csv)],
        options={"session_vars": {}, "session_vars_manager": mgr},
    )
    print(md)
    print("\n--- Variables session ---")
    for k in ("LAT", "LON", "RAYON_M", "INDICATIF_BALISE", "SITREP_TS"):
        print(f"  {k} = {mgr.get(k)}")
    if warns:
        print("\n--- Warnings ---")
        for w in warns:
            print(f"  - {w}")


if __name__ == "__main__":
    _autotest()
