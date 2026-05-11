# -*- coding: utf-8 -*-
"""
IAbrain_actions_demo_poi.py — Plugin de démo POI v1.0.0

Plugin pédagogique qui démontre la chaîne complète :
  1. Macro LLM produit un bloc ###IABRAIN_VARS### avec LAT, LON, etc.
  2. Macro LLM produit un bloc ###IABRAIN_RUN_MACRO### avec « SATER MAP PN »
  3. IAbrain v1.41.0 auto-exécute la macro SATER MAP PN
  4. La carte OSM s'affiche

Ce plugin est livré pour démontrer la fonctionnalité d'auto-exécution
mais n'expose pas d'action propre — c'est le LLM (via le prompt système
de la macro SATER POI) qui produit directement les bons blocs.

Le seul utilitaire exposé ici est une action de validation :
  poi_validate : vérifie que les variables de session sont cohérentes
                 pour une utilisation par SATER MAP PN.

Auteur : ADRASEC 77 / FNRASEC
Compatible : IAbrain v1.41.0+
"""

from __future__ import annotations

import re
from typing import Any, List, Sequence, Tuple

__version__ = "1.0.0"

ACTION_POI_VALIDATE = "poi_validate"


def is_action(action_id: str) -> bool:
    return (action_id or "").strip() == ACTION_POI_VALIDATE


def list_actions() -> List[Tuple[str, str, str]]:
    return [(
        ACTION_POI_VALIDATE,
        "POI — Valider les variables de carte",
        "Vérifie que les variables de session LAT, LON, RAYON_M, "
        "INDICATIF_BALISE et SITREP_TS sont définies et cohérentes pour "
        "permettre l'affichage par la macro SATER MAP PN. Affiche un "
        "rapport de validation détaillé. Utile en pédagogie pour "
        "comprendre le format attendu par osm_balise_map."
    )]


def _validate_lat(value: str) -> Tuple[bool, str]:
    try:
        v = float(value)
        if -90 <= v <= 90:
            return True, f"OK ({v:.6f}°)"
        return False, f"hors plage [-90, 90] : {v}"
    except (ValueError, TypeError):
        return False, f"non numérique : {value!r}"


def _validate_lon(value: str) -> Tuple[bool, str]:
    try:
        v = float(value)
        if -180 <= v <= 180:
            return True, f"OK ({v:.6f}°)"
        return False, f"hors plage [-180, 180] : {v}"
    except (ValueError, TypeError):
        return False, f"non numérique : {value!r}"


def _validate_rayon(value: str) -> Tuple[bool, str]:
    try:
        v = float(value)
        if v >= 0:
            return True, f"OK ({v:.0f} m)"
        return False, f"valeur négative : {v}"
    except (ValueError, TypeError):
        return False, f"non numérique : {value!r}"


def _validate_indicatif(value: str) -> Tuple[bool, str]:
    if not value or not value.strip():
        return False, "vide"
    if len(value) > 64:
        return False, f"trop long ({len(value)} caractères, max 64)"
    return True, f"OK (« {value} »)"


def _validate_sitrep_ts(value: str) -> Tuple[bool, str]:
    if not value:
        return False, "vide"
    # Tolère plusieurs formats courants
    formats = [
        r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$",
        r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}",
        r"^\d{4}-\d{2}-\d{2}$",
    ]
    for pattern in formats:
        if re.match(pattern, value):
            return True, f"OK (« {value} »)"
    return False, f"format inattendu : {value!r} (attendu YYYY-MM-DD HH:MM:SS)"


def _action_poi_validate(options: Any) -> Tuple[str, List[str]]:
    sv = (options or {}).get("session_vars", {}) if options else {}

    checks = [
        ("LAT", _validate_lat),
        ("LON", _validate_lon),
        ("RAYON_M", _validate_rayon),
        ("INDICATIF_BALISE", _validate_indicatif),
        ("SITREP_TS", _validate_sitrep_ts),
    ]

    rows = []
    n_ok = n_ko = 0
    for name, validator in checks:
        value = sv.get(name, "")
        ok, msg = validator(value)
        icon = "✅" if ok else "❌"
        if ok:
            n_ok += 1
        else:
            n_ko += 1
        rows.append(f"| {icon} | `{name}` | {msg} |")

    md = []
    md.append("## 🔍 Validation des variables pour SATER MAP PN")
    md.append("")
    md.append(f"**{n_ok}/{len(checks)}** variables valides pour "
              "l'affichage cartographique.")
    md.append("")
    md.append("| Statut | Variable | Diagnostic |")
    md.append("|---|---|---|")
    md.extend(rows)
    md.append("")
    if n_ko == 0:
        md.append("👉 Vous pouvez cliquer sur la macro **SATER MAP PN** "
                  "pour afficher la carte.")
    else:
        md.append(f"⚠️ {n_ko} variable(s) à corriger avant de pouvoir "
                  "utiliser SATER MAP PN.")
        md.append("")
        md.append("Pour redéfinir une variable manquante :")
        md.append("```")
        md.append("/set NOM=VALEUR")
        md.append("```")
        md.append("")
        md.append("Ou demandez à une macro LLM de produire le bloc "
                  "`###IABRAIN_VARS###` correspondant.")

    return "\n".join(md), []


def execute_action(
    action_id: str,
    imported_files: Sequence[Tuple[str, str]] = (),
    options: Any = None,
) -> Tuple[str, List[str]]:
    aid = (action_id or "").strip()
    if aid == ACTION_POI_VALIDATE:
        return _action_poi_validate(options)
    return (
        f"## ❌ Action inconnue : `{aid}`\n\n"
        f"Action disponible : `{ACTION_POI_VALIDATE}`",
        [],
    )


def _autotest():
    """Test simple."""

    class MockMgr:
        def __init__(self, vars_dict): self._v = dict(vars_dict)
        def get(self, n): return self._v.get(n)

    # Cas 1 : tout valide
    sv = {
        "LAT": "48.858370",
        "LON": "2.294481",
        "RAYON_M": "100",
        "INDICATIF_BALISE": "POI-TOUR-EIFFEL",
        "SITREP_TS": "2026-05-07 14:32:00",
    }
    md, _ = execute_action(
        ACTION_POI_VALIDATE,
        options={"session_vars": sv},
    )
    print(md)
    print("\n--- Cas 2 : LAT invalide ---")
    sv["LAT"] = "abc"
    md, _ = execute_action(
        ACTION_POI_VALIDATE,
        options={"session_vars": sv},
    )
    print(md)


if __name__ == "__main__":
    _autotest()
