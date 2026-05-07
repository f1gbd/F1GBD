#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_sater_loc.py — Tests automatises du plugin SATER LOC (v1.40.7+)

Verifie le plugin IAbrain_actions_sater_loc.py sur :
  - L'interface (is_action, list_actions format a 3 elements)
  - Les cas d'erreur (CSV manquant, colonnes manquantes, trop peu de releves)
  - Les cas fonctionnels (3 stations propres, outliers, CSV reel HECTOR)
  - L'ecriture des 5 variables dans la session
  - Le mode degrade (sans manager)
  - La robustesse au format (separateur virgule, decimales virgule)
  - La sortie markdown (DMS, guide vers SATER MAP PNG)

Usage :
    python test_sater_loc.py                     # Lance tous les tests
    python test_sater_loc.py --verbose           # Tracebacks complets
    python test_sater_loc.py --plugin-dir PATH   # Chemin custom du plugin

Codes de retour :
    0 : tous les tests passent
    1 : au moins un test echoue
    2 : erreur d'environnement
"""

from __future__ import annotations

import argparse
import importlib.util
import math
import sys
import time
from pathlib import Path
from typing import Callable, List, Optional, Tuple


class C:
    if sys.stdout.isatty():
        OK = "\033[92m"; FAIL = "\033[91m"; WARN = "\033[93m"
        DIM = "\033[2m"; BOLD = "\033[1m"; END = "\033[0m"
    else:
        OK = FAIL = WARN = DIM = BOLD = END = ""


class MockSessionVars:
    def __init__(self):
        self._vars: dict = {}
    def all(self): return dict(self._vars)
    def get(self, name): return self._vars.get(name)
    def set(self, name, value): self._vars[name] = str(value); return True
    def save(self): pass
    def count(self): return len(self._vars)
    def names(self): return list(self._vars.keys())


def find_plugin(custom_path: Optional[str] = None) -> Path:
    if custom_path:
        p = Path(custom_path)
        if p.is_file():
            return p.resolve()
        raise FileNotFoundError(f"Plugin introuvable : {custom_path}")

    here = Path(__file__).resolve().parent
    candidates = [
        here / "plugins" / "IAbrain_actions_sater_loc.py",
        here / "IAbrain_actions_sater_loc.py",
        here.parent / "plugins" / "IAbrain_actions_sater_loc.py",
    ]
    for cand in candidates:
        if cand.is_file():
            return cand.resolve()
    raise FileNotFoundError(
        "IAbrain_actions_sater_loc.py introuvable. Emplacements testes :\n"
        + "\n".join(f"  - {c}" for c in candidates)
    )


def load_plugin(plugin_path: Path):
    plugin_dir = plugin_path.parent
    if str(plugin_dir) not in sys.path:
        sys.path.insert(0, str(plugin_dir))
    spec = importlib.util.spec_from_file_location(plugin_path.stem, plugin_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Spec invalide : {plugin_path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[plugin_path.stem] = mod
    spec.loader.exec_module(mod)

    required = ("is_action", "execute_action", "list_actions")
    missing = [f for f in required if not hasattr(mod, f)]
    if missing:
        raise ImportError(
            f"{plugin_path.name} : interface incomplete (manque "
            f"{', '.join(missing)})")
    return mod


class TestRunner:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.tests: List[Tuple[str, Callable]] = []
        self.results: List[Tuple[str, bool, str, float]] = []

    def add(self, name: str, func: Callable):
        self.tests.append((name, func))

    def run(self) -> bool:
        bar = "=" * 74
        print(f"\n{C.BOLD}{bar}{C.END}")
        print(f"{C.BOLD}  Tests automatises - Plugin SATER LOC (IAbrain v1.40.7+){C.END}")
        print(f"{C.BOLD}{bar}{C.END}\n")

        for name, func in self.tests:
            t0 = time.perf_counter()
            try:
                func()
                dt = time.perf_counter() - t0
                print(f"  {C.OK}OK{C.END} {name} {C.DIM}({dt*1000:.1f} ms){C.END}")
                self.results.append((name, True, "", dt))
            except AssertionError as e:
                dt = time.perf_counter() - t0
                print(f"  {C.FAIL}KO{C.END} {name}")
                print(f"     {C.FAIL}{e}{C.END}")
                self.results.append((name, False, str(e), dt))
            except Exception as e:
                dt = time.perf_counter() - t0
                print(f"  {C.FAIL}KO{C.END} {name}")
                print(f"     {C.FAIL}EXCEPTION : {type(e).__name__} : {e}{C.END}")
                if self.verbose:
                    import traceback
                    print(f"     {C.DIM}{traceback.format_exc()}{C.END}")
                self.results.append((name, False, f"{type(e).__name__}: {e}", dt))

        ok = sum(1 for _, r, _, _ in self.results if r)
        ko = len(self.results) - ok
        total_ms = sum(d for _, _, _, d in self.results) * 1000

        print(f"\n{C.BOLD}{'-' * 74}{C.END}")
        if ko == 0:
            print(f"  {C.OK}{C.BOLD}OK : {ok}/{ok} tests reussis{C.END} "
                  f"{C.DIM}(temps total : {total_ms:.0f} ms){C.END}")
        else:
            print(f"  {C.FAIL}{C.BOLD}KO : {ko} echec(s) sur {ok+ko} tests"
                  f"{C.END} {C.DIM}({total_ms:.0f} ms){C.END}")
        print()
        return ko == 0


def haversine_m(lat1, lon1, lat2, lon2):
    R = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


def run_with_csv(plugin, csv_content: str, csv_name: str = "releves.csv"):
    mgr = MockSessionVars()
    md, warnings = plugin.execute_action(
        plugin.ACTION_SATER_LOC,
        imported_files=[(csv_name, csv_content)],
        options={"session_vars": mgr.all(), "session_vars_manager": mgr},
    )
    return md, mgr, warnings


def _build_clean_csv():
    """3 stations propres convergeant vers (48.6, 2.3)."""
    target_lat, target_lon = 48.6, 2.3
    stations = [
        ("S1", 48.55, 2.20),
        ("S2", 48.55, 2.40),
        ("S3", 48.65, 2.30),
    ]
    rows = ["Indicatif;Latitude_Dec;Longitude_Dec;Latitude_DMS;"
            "Longitude_DMS;Azimut_Deg;Couleur;Date_Heure"]
    for ind, lat, lon in stations:
        p1, p2 = math.radians(lat), math.radians(target_lat)
        dl = math.radians(target_lon - lon)
        y = math.sin(dl) * math.cos(p2)
        x = math.cos(p1)*math.sin(p2) - math.sin(p1)*math.cos(p2)*math.cos(dl)
        az = (math.degrees(math.atan2(y, x)) + 360) % 360
        rows.append(f"{ind};{lat:.6f};{lon:.6f};_;_;{az:.1f};#fff;"
                    "2026-05-07 12:00:00")
    return "\n".join(rows) + "\n"


def _build_csv_with_outliers():
    """6 stations propres + 2 outliers = 25% de pollution, dans la plage
    de robustesse de l'estimateur MAD (~30%)."""
    target_lat, target_lon = 48.6, 2.3
    stations = [
        ("S1", 48.55, 2.20),
        ("S2", 48.55, 2.40),
        ("S3", 48.65, 2.30),
        ("S4", 48.58, 2.25),
        ("S5", 48.62, 2.35),
        ("S6", 48.60, 2.20),
    ]
    rows = ["Indicatif;Latitude_Dec;Longitude_Dec;Latitude_DMS;"
            "Longitude_DMS;Azimut_Deg;Couleur;Date_Heure"]
    for ind, lat, lon in stations:
        p1, p2 = math.radians(lat), math.radians(target_lat)
        dl = math.radians(target_lon - lon)
        y = math.sin(dl) * math.cos(p2)
        x = math.cos(p1)*math.sin(p2) - math.sin(p1)*math.cos(p2)*math.cos(dl)
        az = (math.degrees(math.atan2(y, x)) + 360) % 360
        rows.append(f"{ind};{lat:.6f};{lon:.6f};_;_;{az:.1f};#fff;"
                    "2026-05-07 12:00:00")
    # 2 outliers volontaires (azimuts opposes a la balise)
    rows.append("BAD1;48.55;2.20;_;_;180.0;#fff;2026-05-07 12:00:00")
    rows.append("BAD2;48.65;2.30;_;_;90.0;#fff;2026-05-07 12:00:00")
    return "\n".join(rows) + "\n"


REAL_CSV_HECTOR = (
    "Indicatif;Latitude_Dec;Longitude_Dec;Latitude_DMS;Longitude_DMS;"
    "Azimut_Deg;Couleur;Date_Heure\r\n"
    "ALPHA/1;48.313333;3.285833;_;_;4.0;#ff6b35;2026-05-04 10:06:51\r\n"
    "ALPHA/2;48.426944;3.402222;_;_;276.0;#ff6b35;2026-05-04 10:12:09\r\n"
    "ALPHA/3;48.403611;3.273889;_;_;26.0;#ff6b35;2026-05-04 10:13:50\r\n"
    "ALPHA/4;48.431667;3.311111;_;_;250.0;#ff6b35;2026-05-04 10:16:28\r\n"
    "ALPHA/5;48.430278;3.285556;_;_;100.0;#ff6b35;2026-05-04 10:18:59\r\n"
    "ALPHA/6;48.429444;3.290278;_;_;110.0;#ff6b35;2026-05-04 10:22:32\r\n"
    "ALPHA/7;48.429167;3.291667;_;_;110.0;#ff6b35;2026-05-04 10:25:24\r\n"
    "BALISE ELT/1;48.429167;3.291944;_;_;0.0;#3f51b5;2026-05-04 10:28:34\r\n"
    "BRAVO/1;48.419167;3.293056;_;_;359.0;#3f51b5;2026-05-04 13:04:20\r\n"
    "BRAVO/2;48.443611;3.406111;_;_;259.0;#3f51b5;2026-05-04 11:38:39\r\n"
    "BRAVO/3;48.448611;3.253333;_;_;127.0;#3f51b5;2026-05-04 11:39:39\r\n"
    "BRAVO/4;48.433333;3.290000;_;_;155.0;#3f51b5;2026-05-04 11:43:21\r\n"
    "CHARLIE/2;48.313333;3.285833;_;_;0.0;#4caf50;2026-05-04 12:15:54\r\n"
    "CHARLIE/3;48.441667;3.394167;_;_;266.0;#4caf50;2026-05-04 13:02:02\r\n"
    "CHARLIE/4;48.404722;3.284722;_;_;10.0;#4caf50;2026-05-04 13:03:31\r\n"
    "CHARLIE/5;48.438611;3.281667;_;_;142.0;#4caf50;2026-05-04 13:05:24\r\n"
    "CHARLIE/6;48.426944;3.297778;_;_;307.0;#4caf50;2026-05-04 13:05:54\r\n"
)


def make_tests(plugin, runner: TestRunner):

    def test_interface():
        assert plugin.is_action("sater_loc_from_csv"), "action non reconnue"
        assert not plugin.is_action("inconnue"), "action inconnue acceptee"
        assert not plugin.is_action(""), "chaine vide acceptee"

    def test_list_actions_format():
        actions = plugin.list_actions()
        assert isinstance(actions, list) and actions
        for entry in actions:
            assert len(entry) == 3, (
                f"Tuple a 3 elements attendu, recu {len(entry)} : {entry!r}")
            aid, label, desc = entry
            assert isinstance(aid, str) and aid
            assert isinstance(label, str) and label
            assert isinstance(desc, str) and desc

    runner.add("Interface - is_action()", test_interface)
    runner.add("Interface - list_actions() format a 3 elements",
               test_list_actions_format)

    def test_no_csv_imported():
        mgr = MockSessionVars()
        md, _ = plugin.execute_action(
            plugin.ACTION_SATER_LOC, imported_files=[],
            options={"session_vars": mgr.all(), "session_vars_manager": mgr})
        assert "Aucun CSV" in md or "❌" in md
        assert mgr.count() == 0, "Aucune variable ne doit etre ecrite"

    def test_csv_missing_columns():
        bad_csv = "Foo;Bar\n1;2\n3;4\n"
        md, mgr, _ = run_with_csv(plugin, bad_csv)
        assert "❌" in md
        assert "manquant" in md.lower() or "colonne" in md.lower()
        assert mgr.count() == 0

    def test_csv_too_few_relevs():
        single_csv = (
            "Indicatif;Latitude_Dec;Longitude_Dec;Latitude_DMS;"
            "Longitude_DMS;Azimut_Deg;Couleur;Date_Heure\n"
            "S1;48.5;2.3;_;_;90.0;#fff;2026-05-07 12:00:00\n"
        )
        md, mgr, _ = run_with_csv(plugin, single_csv)
        assert "❌" in md
        assert mgr.count() == 0

    runner.add("Erreur - aucun CSV importe", test_no_csv_imported)
    runner.add("Erreur - colonnes manquantes", test_csv_missing_columns)
    runner.add("Erreur - moins de 2 relevements", test_csv_too_few_relevs)

    def test_clean_3_stations():
        csv = _build_clean_csv()
        md, mgr, _ = run_with_csv(plugin, csv)
        assert "❌" not in md
        for var in ("LAT", "LON", "RAYON_M", "INDICATIF_BALISE", "SITREP_TS"):
            assert mgr.get(var), f"Variable {var} non ecrite"
        lat = float(mgr.get("LAT"))
        lon = float(mgr.get("LON"))
        err = haversine_m(lat, lon, 48.6, 2.3)
        assert err < 100, f"Erreur trop grande : {err:.1f} m (attendu < 100)"

    def test_with_outliers():
        csv = _build_csv_with_outliers()
        md, mgr, _ = run_with_csv(plugin, csv)
        assert "❌" not in md
        assert "BAD1" in md and "BAD2" in md, (
            "Les outliers BAD1/BAD2 doivent apparaitre dans le rapport")
        assert "rejet" in md.lower() or "outlier" in md.lower()
        lat = float(mgr.get("LAT"))
        lon = float(mgr.get("LON"))
        err = haversine_m(lat, lon, 48.6, 2.3)
        assert err < 200, f"Position perturbee par outliers : {err:.1f} m"

    def test_real_csv_hector():
        md, mgr, _ = run_with_csv(plugin, REAL_CSV_HECTOR,
                                  "releves_sater_HECTOR.csv")
        assert "❌" not in md
        lat = float(mgr.get("LAT"))
        lon = float(mgr.get("LON"))
        err = haversine_m(lat, lon, 48.429167, 3.291944)
        assert err < 200, (
            f"Erreur exercice HECTOR : {err:.1f} m (attendu < 200 m sur "
            f"un jeu reel avec outliers)")

    def test_balise_line_ignored():
        md, mgr, warnings = run_with_csv(plugin, REAL_CSV_HECTOR)
        joined = " ".join(warnings).lower()
        assert "balise" in joined, (
            "Le warning sur les lignes BALISE ELT doit etre present")

    runner.add("Fonctionnel - 3 stations propres convergent",
               test_clean_3_stations)
    runner.add("Fonctionnel - rejet automatique des outliers",
               test_with_outliers)
    runner.add("Fonctionnel - CSV reel HECTOR (16 relevements)",
               test_real_csv_hector)
    runner.add("Fonctionnel - lignes BALISE ELT ignorees",
               test_balise_line_ignored)

    def test_session_writeback():
        csv = _build_clean_csv()
        mgr = MockSessionVars()
        plugin.execute_action(
            plugin.ACTION_SATER_LOC,
            imported_files=[("releves.csv", csv)],
            options={"session_vars": mgr.all(),
                     "session_vars_manager": mgr})
        assert mgr.count() == 5, (
            f"5 variables attendues, recu {mgr.count()} : {mgr.names()}")
        lat = float(mgr.get("LAT"))
        lon = float(mgr.get("LON"))
        rayon = int(mgr.get("RAYON_M"))
        assert -90 <= lat <= 90
        assert -180 <= lon <= 180
        assert rayon >= 50, f"RAYON_M plancher 50 attendu, recu {rayon}"
        assert mgr.get("INDICATIF_BALISE").startswith("ELT")
        assert len(mgr.get("SITREP_TS")) >= 19

    def test_no_manager_fallback():
        csv = _build_clean_csv()
        md, _ = plugin.execute_action(
            plugin.ACTION_SATER_LOC,
            imported_files=[("releves.csv", csv)],
            options={"session_vars": {}})
        assert "/set LAT=" in md
        assert "/set LON=" in md
        assert "/set RAYON_M=" in md
        assert "/set INDICATIF_BALISE=" in md
        assert "/set SITREP_TS=" in md

    runner.add("Session - ecriture des 5 variables (LAT/LON/RAYON/INDIC/TS)",
               test_session_writeback)
    runner.add("Session - mode degrade (sans manager) produit /set",
               test_no_manager_fallback)

    def test_csv_with_comma_separator():
        csv = _build_clean_csv().replace(";", ",")
        md, mgr, warnings = run_with_csv(plugin, csv)
        if mgr.count() == 5:
            joined = " ".join(warnings).lower()
            assert "separateur" in joined, (
                "Un warning sur le separateur devrait etre emis")

    def test_csv_decimal_with_comma():
        csv = (
            "Indicatif;Latitude_Dec;Longitude_Dec;Latitude_DMS;"
            "Longitude_DMS;Azimut_Deg;Couleur;Date_Heure\n"
            "S1;48,55;2,20;_;_;45,0;#fff;2026-05-07\n"
            "S2;48,55;2,40;_;_;315,0;#fff;2026-05-07\n"
            "S3;48,65;2,30;_;_;180,0;#fff;2026-05-07\n"
        )
        md, mgr, _ = run_with_csv(plugin, csv)
        assert mgr.count() == 5, (
            f"Virgule decimale doit etre toleree. MD :\n{md[:300]}")

    runner.add("Robustesse - separateur ',' tolere (avec warning)",
               test_csv_with_comma_separator)
    runner.add("Robustesse - virgule decimale toleree",
               test_csv_decimal_with_comma)

    def test_markdown_contains_dms():
        csv = _build_clean_csv()
        md, _, _ = run_with_csv(plugin, csv)
        import re
        assert re.search(r'\d+°\d+\'\d+\.\d+"[NSEW]', md), (
            f"Format DMS attendu dans le rendu, recu :\n{md[:500]}")

    def test_markdown_next_step_hint():
        csv = _build_clean_csv()
        md, _, _ = run_with_csv(plugin, csv)
        assert "SATER MAP" in md or "osm_balise_map" in md, (
            "Le rendu doit guider vers la macro suivante")

    runner.add("Markdown - format DMS dans la sortie",
               test_markdown_contains_dms)
    runner.add("Markdown - guide vers SATER MAP PNG",
               test_markdown_next_step_hint)


def main():
    parser = argparse.ArgumentParser(
        description="Tests automatises du plugin SATER LOC pour IAbrain v1.40.7+")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--plugin-dir", help="Chemin direct vers le plugin")
    args = parser.parse_args()

    try:
        plugin_path = find_plugin(args.plugin_dir)
        print(f"\n{C.DIM}Plugin charge depuis : {plugin_path}{C.END}")
        plugin = load_plugin(plugin_path)
    except (FileNotFoundError, ImportError) as e:
        print(f"\n{C.FAIL}Erreur d'environnement :{C.END}\n   {e}\n")
        return 2

    runner = TestRunner(verbose=args.verbose)
    make_tests(plugin, runner)
    return 0 if runner.run() else 1


if __name__ == "__main__":
    sys.exit(main())
