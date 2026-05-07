#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_soe_chain.py — Tests automatisés de la chaîne SOE (v1.40.7+)

Vérifie le bon fonctionnement de IAbrain_actions_soe.py via le mécanisme
de chargement de plugins externes d'IAbrain v1.40.7.

Usage :
    python test_soe_chain.py                       # Lance tous les tests
    python test_soe_chain.py --verbose             # Affiche les détails
    python test_soe_chain.py --plugin-dir PATH     # Chemin custom du plugin
    python test_soe_chain.py --quick               # Tests rapides seulement

Localisation par défaut du plugin :
    Le script cherche IAbrain_actions_soe.py dans :
      1. ./plugins/IAbrain_actions_soe.py  (distribution finale)
      2. ./IAbrain_actions_soe.py          (même dossier — dev)
      3. ../plugins/IAbrain_actions_soe.py (depuis dossier de tests)

Codes de retour :
    0 : tous les tests passent
    1 : au moins un test échoue
    2 : erreur d'environnement (plugin introuvable, etc.)

Auteur : Suite de tests CI/CD pour IAbrain v1.40.7+
"""

from __future__ import annotations

import argparse
import importlib.util
import random
import re
import string
import sys
import time
import unicodedata
from pathlib import Path
from typing import Any, Callable, List, Optional, Tuple


# ===========================================================================
# Couleurs terminal (sans dépendance externe)
# ===========================================================================

class C:
    """Codes ANSI minimalistes — désactivés si la sortie n'est pas un TTY."""
    if sys.stdout.isatty():
        OK = "\033[92m"
        FAIL = "\033[91m"
        WARN = "\033[93m"
        DIM = "\033[2m"
        BOLD = "\033[1m"
        END = "\033[0m"
    else:
        OK = FAIL = WARN = DIM = BOLD = END = ""


# ===========================================================================
# Mock SessionVarsManager (réplique l'API d'IAbrain_session_vars)
# ===========================================================================

class MockSessionVars:
    """Implémentation minimale du contrat session_vars_manager
    pour permettre aux plugins d'écrire des variables hors d'IAbrain.
    """

    def __init__(self):
        self._vars: dict[str, str] = {}

    def all(self) -> dict[str, str]:
        return dict(self._vars)

    def get(self, name: str) -> Optional[str]:
        return self._vars.get(name)

    def set(self, name: str, value: str) -> bool:
        self._vars[name] = str(value)
        return True

    def save(self) -> None:
        pass  # pas de persistance en mode test

    def count(self) -> int:
        return len(self._vars)

    def names(self) -> List[str]:
        return list(self._vars.keys())


# ===========================================================================
# Localisation et chargement du plugin
# ===========================================================================

def _normalize_text(s: str) -> str:
    """Réplique la normalisation interne du plugin pour les comparaisons."""
    nfd = unicodedata.normalize('NFD', s)
    sans_accents = ''.join(c for c in nfd if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^A-Z]', '', sans_accents.upper())


def find_plugin(custom_path: Optional[str] = None) -> Path:
    """Localise IAbrain_actions_soe.py dans les emplacements habituels."""
    if custom_path:
        p = Path(custom_path)
        if p.is_file():
            return p.resolve()
        raise FileNotFoundError(
            f"Plugin introuvable au chemin spécifié : {custom_path}"
        )

    here = Path(__file__).resolve().parent
    candidates = [
        here / "plugins" / "IAbrain_actions_soe.py",
        here / "IAbrain_actions_soe.py",
        here.parent / "plugins" / "IAbrain_actions_soe.py",
    ]

    for cand in candidates:
        if cand.is_file():
            return cand.resolve()

    raise FileNotFoundError(
        "Plugin IAbrain_actions_soe.py introuvable. Emplacements testés :\n"
        + "\n".join(f"  - {c}" for c in candidates)
    )


def load_plugin(plugin_path: Path):
    """Charge le plugin comme le ferait IAbrain au démarrage."""
    plugin_dir = plugin_path.parent
    if str(plugin_dir) not in sys.path:
        sys.path.insert(0, str(plugin_dir))

    spec = importlib.util.spec_from_file_location(
        plugin_path.stem, plugin_path
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"Impossible de créer un spec pour {plugin_path}")

    mod = importlib.util.module_from_spec(spec)
    sys.modules[plugin_path.stem] = mod
    spec.loader.exec_module(mod)

    # Vérification du contrat d'interface
    required = ("is_action", "execute_action", "list_actions")
    missing = [f for f in required if not hasattr(mod, f)]
    if missing:
        raise ImportError(
            f"Plugin {plugin_path.name} : interface incomplète "
            f"(manque {', '.join(missing)})"
        )
    return mod


# ===========================================================================
# Framework de tests minimaliste
# ===========================================================================

class TestRunner:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.tests: List[Tuple[str, Callable]] = []
        self.results: List[Tuple[str, bool, str, float]] = []

    def add(self, name: str, func: Callable):
        self.tests.append((name, func))

    def run(self) -> bool:
        print(f"\n{C.BOLD}═══════════════════════════════════════════════════════"
              f"═══════════════════{C.END}")
        print(f"{C.BOLD}  Tests automatisés — Chaîne SOE (IAbrain v1.40.7+)"
              f"{C.END}")
        print(f"{C.BOLD}═══════════════════════════════════════════════════════"
              f"═══════════════════{C.END}\n")

        for name, func in self.tests:
            t0 = time.perf_counter()
            try:
                func()
                dt = time.perf_counter() - t0
                print(f"  {C.OK}✓{C.END} {name} {C.DIM}({dt*1000:.1f} ms)"
                      f"{C.END}")
                self.results.append((name, True, "", dt))
            except AssertionError as e:
                dt = time.perf_counter() - t0
                print(f"  {C.FAIL}✗{C.END} {name}")
                print(f"    {C.FAIL}{e}{C.END}")
                self.results.append((name, False, str(e), dt))
            except Exception as e:
                dt = time.perf_counter() - t0
                print(f"  {C.FAIL}✗{C.END} {name}")
                print(f"    {C.FAIL}EXCEPTION : {type(e).__name__} : {e}"
                      f"{C.END}")
                if self.verbose:
                    import traceback
                    print(f"    {C.DIM}{traceback.format_exc()}{C.END}")
                self.results.append((name, False, f"{type(e).__name__}: {e}",
                                     dt))

        ok = sum(1 for _, r, _, _ in self.results if r)
        ko = len(self.results) - ok
        total_ms = sum(d for _, _, _, d in self.results) * 1000

        print(f"\n{C.BOLD}─────────────────────────────────────────────────"
              f"─────────────────────────{C.END}")
        if ko == 0:
            print(f"  {C.OK}{C.BOLD}✓ {ok}/{ok} tests réussis{C.END} "
                  f"{C.DIM}(temps total : {total_ms:.0f} ms){C.END}")
        else:
            print(f"  {C.FAIL}{C.BOLD}✗ {ko} échec(s) sur {ok+ko} tests"
                  f"{C.END} {C.DIM}(temps total : {total_ms:.0f} ms){C.END}")
        print()
        return ko == 0


# ===========================================================================
# Helpers d'extraction de résultats depuis le markdown du plugin
# ===========================================================================

def extract_var_from_md(md: str, var_name: str) -> Optional[str]:
    """Extrait la valeur d'une variable depuis le bloc ``` ``` qui suit
    le titre `### {var_name}` dans le markdown produit par le plugin."""
    pattern = rf"### {re.escape(var_name)}\n+```\n(.+?)\n```"
    m = re.search(pattern, md, re.DOTALL)
    return m.group(1).strip() if m else None


def encode_message(plugin, cle1: str, cle2: str, message: str
                   ) -> Tuple[str, MockSessionVars]:
    """Chiffre un message via le plugin et retourne (CRYPTO, session)."""
    session = MockSessionVars()
    session.set("CLE1", cle1)
    session.set("CLE2", cle2)
    session.set("MESSAGE", message)

    md, _warnings = plugin.execute_action(
        "soe_encode",
        imported_files=(),
        options={
            "session_vars": session.all(),
            "session_vars_manager": session,
        }
    )

    crypto = session.get("CRYPTO") or extract_var_from_md(md, "CRYPTO")
    assert crypto, f"CRYPTO non produite. Markdown reçu :\n{md[:300]}"
    return crypto, session


def decode_crypto(plugin, cle1: str, cle2: str, crypto: str,
                  cryptometa: Optional[str] = None
                  ) -> Tuple[str, MockSessionVars]:
    """Déchiffre un cryptogramme via le plugin et retourne
    (MESSAGE_DECODE, session). Si cryptometa est fourni, il est passé
    au plugin pour un déchiffrement parfaitement non ambigu (v1.40.7+)."""
    session = MockSessionVars()
    session.set("CLE1", cle1)
    session.set("CLE2", cle2)
    session.set("CRYPTO", crypto)
    if cryptometa:
        session.set("CRYPTOMETA", cryptometa)

    md, _warnings = plugin.execute_action(
        "soe_decode",
        imported_files=(),
        options={
            "session_vars": session.all(),
            "session_vars_manager": session,
        }
    )

    decoded = session.get("MESSAGE_DECODE") or \
              extract_var_from_md(md, "MESSAGE_DECODE")
    assert decoded, f"MESSAGE_DECODE non produit. Markdown :\n{md[:300]}"
    return decoded, session


def encode_decode_roundtrip(plugin, cle1: str, cle2: str, message: str
                             ) -> str:
    """Helper pour les tests fuzz : chiffre puis déchiffre en transmettant
    CRYPTOMETA. Retourne le MESSAGE_DECODE final."""
    crypto, enc_session = encode_message(plugin, cle1, cle2, message)
    cryptometa = enc_session.get("CRYPTOMETA")
    decoded, _ = decode_crypto(plugin, cle1, cle2, crypto, cryptometa)
    return decoded


def random_message(min_len: int = 20, max_len: int = 200,
                   rng: Optional[random.Random] = None) -> str:
    """Génère un message aléatoire de longueur variable."""
    rng = rng or random.Random()
    n = rng.randint(min_len, max_len)
    # Mélange lettres + espaces (essentiel pour tester la normalisation)
    chars = string.ascii_uppercase + " " * 4  # 1 espace toutes les ~7 lettres
    msg = ''.join(rng.choice(chars) for _ in range(n))
    return msg.strip() or "MESSAGE TEST"


def random_key(min_len: int = 8, max_len: int = 25,
               rng: Optional[random.Random] = None,
               allow_doubles: bool = True) -> str:
    """Génère une clé aléatoire de longueur variable."""
    rng = rng or random.Random()
    n = rng.randint(min_len, max_len)
    if allow_doubles:
        return ''.join(rng.choice(string.ascii_uppercase) for _ in range(n))
    # Sans doublons : prendre des lettres distinctes
    n = min(n, 26)
    return ''.join(rng.sample(string.ascii_uppercase, n))


# ===========================================================================
# Tests
# ===========================================================================

def make_tests(plugin, runner: TestRunner, quick: bool = False):
    """Construit la suite de tests. Si quick=True, on saute les tests
    longs (génération aléatoire massive)."""

    # -------------------------------------------------------------------
    # Tests d'interface du plugin
    # -------------------------------------------------------------------

    def test_interface_complete():
        assert plugin.is_action("soe_encode"), "soe_encode non reconnue"
        assert plugin.is_action("soe_decode"), "soe_decode non reconnue"
        assert not plugin.is_action("inconnue"), \
            "is_action devrait rejeter une action inconnue"

    def test_list_actions_format():
        actions = plugin.list_actions()
        assert isinstance(actions, list), \
            f"list_actions doit retourner une list, reçu {type(actions)}"
        assert len(actions) >= 2, \
            f"Au moins 2 actions attendues, reçu {len(actions)}"
        for entry in actions:
            assert len(entry) == 3, (
                f"Chaque entrée doit être un tuple à 3 éléments "
                f"(id, label, desc), reçu {len(entry)} dans {entry!r}"
            )
            aid, label, desc = entry
            assert isinstance(aid, str) and aid, f"id invalide : {aid!r}"
            assert isinstance(label, str) and label, \
                f"label invalide : {label!r}"
            assert isinstance(desc, str) and desc, \
                f"description invalide : {desc!r}"

    def test_unknown_action():
        md, _ = plugin.execute_action(
            "action_qui_nexiste_pas",
            imported_files=(),
            options={"session_vars": {}}
        )
        assert "inconnue" in md.lower() or "❌" in md, \
            f"Une action inconnue doit retourner un markdown d'erreur, reçu :\n{md[:200]}"

    runner.add("Interface — is_action() reconnaît les bonnes actions",
               test_interface_complete)
    runner.add("Interface — list_actions() retourne des tuples à 3 éléments",
               test_list_actions_format)
    runner.add("Interface — action inconnue produit un markdown d'erreur",
               test_unknown_action)

    # -------------------------------------------------------------------
    # Tests fonctionnels — cas de référence
    # -------------------------------------------------------------------

    def test_reference_hector():
        """Cas de référence ADRASEC : message d'exercice HECTOR."""
        cle1 = "RIENNESERTDECOURIR"
        cle2 = "ILFAUTPARTIRAPOINT"
        msg = ("CONFIRME OPERATION TERRAIN HECTOR A PARTIR DU JEUDI NEUF "
               "MARS STOP CODE OPTIQUE RECONNAISSANCE ET MESSAGE "
               "PERSONNEL BBC HABITUELS FIN")
        decoded = encode_decode_roundtrip(plugin, cle1, cle2, msg)
        expected = _normalize_text(msg)
        assert decoded == expected, (
            f"Aller-retour HECTOR cassé.\n"
            f"  Attendu : {expected[:60]}...\n"
            f"  Obtenu  : {decoded[:60]}..."
        )

    def test_session_writeback():
        """Le plugin doit écrire CRYPTO et CRYPTOMETA dans la session
        via le manager."""
        session = MockSessionVars()
        session.set("CLE1", "RIENNESERTDECOURIR")
        session.set("CLE2", "ILFAUTPARTIRAPOINT")
        session.set("MESSAGE", "TEST")

        assert "CRYPTO" not in session.names()
        assert "CRYPTOMETA" not in session.names()
        plugin.execute_action(
            "soe_encode",
            imported_files=(),
            options={
                "session_vars": session.all(),
                "session_vars_manager": session,
            }
        )
        assert "CRYPTO" in session.names(), (
            "CRYPTO doit être écrit dans la session via session_vars_manager. "
            f"Variables présentes : {session.names()}"
        )
        assert "CRYPTOMETA" in session.names(), (
            "CRYPTOMETA doit être écrit dans la session (v1.40.7+). "
            f"Variables présentes : {session.names()}"
        )
        assert session.get("CRYPTO"), "CRYPTO ne doit pas être vide"
        meta = session.get("CRYPTOMETA")
        assert meta and "N=" in meta and "PAD=" in meta, \
            f"CRYPTOMETA doit contenir N et PAD : {meta!r}"

    def test_no_manager_fallback():
        """Sans manager exposé, le plugin doit retourner les commandes /set."""
        md, _ = plugin.execute_action(
            "soe_encode",
            imported_files=(),
            options={"session_vars": {
                "CLE1": "RIENNESERTDECOURIR",
                "CLE2": "ILFAUTPARTIRAPOINT",
                "MESSAGE": "FALLBACK TEST",
            }}
            # PAS de session_vars_manager — comportement v1.40.6 et inférieur
        )
        assert "/set CRYPTO=" in md, (
            "Sans manager, le plugin doit fournir une commande "
            f"/set CRYPTO=. Reçu :\n{md[-300:]}"
        )
        assert "/set CRYPTOMETA=" in md, (
            "Sans manager, le plugin doit aussi fournir /set CRYPTOMETA=. "
            f"Reçu :\n{md[-300:]}"
        )

    runner.add("Fonctionnel — aller-retour message HECTOR (référence)",
               test_reference_hector)
    runner.add("Fonctionnel — écriture automatique de CRYPTO dans la session",
               test_session_writeback)
    runner.add("Fonctionnel — mode dégradé (sans manager) produit /set",
               test_no_manager_fallback)

    # -------------------------------------------------------------------
    # Tests de robustesse — variables manquantes
    # -------------------------------------------------------------------

    def test_missing_vars_encode():
        md, _ = plugin.execute_action(
            "soe_encode", imported_files=(),
            options={"session_vars": {"CLE1": "ABCDEF"}}  # CLE2 et MESSAGE manquantes
        )
        assert "manquant" in md.lower() or "❌" in md, (
            f"Variables manquantes doivent produire une erreur claire. "
            f"Reçu :\n{md[:200]}"
        )

    def test_missing_vars_decode():
        md, _ = plugin.execute_action(
            "soe_decode", imported_files=(),
            options={"session_vars": {"CLE1": "ABCDEF"}}
        )
        assert "manquant" in md.lower() or "❌" in md, \
            "Variables manquantes au décodage doivent produire une erreur"

    runner.add("Robustesse — encode sans variables → message d'erreur",
               test_missing_vars_encode)
    runner.add("Robustesse — decode sans variables → message d'erreur",
               test_missing_vars_decode)

    # -------------------------------------------------------------------
    # Tests de normalisation
    # -------------------------------------------------------------------

    def test_accents_handled():
        """Le message avec accents doit être normalisé puis chiffré."""
        cle1 = "RIENNESERTDECOURIR"
        cle2 = "ILFAUTPARTIRAPOINT"
        msg = "Évacuation immédiate du bâtiment FIN"
        decoded = encode_decode_roundtrip(plugin, cle1, cle2, msg)
        # Le décodé doit correspondre à la normalisation (sans accents/espaces)
        expected = _normalize_text(msg)  # "EVACUATIONIMMEDIATEDUBATIMENTFIN"
        assert decoded == expected, (
            f"Normalisation accents cassée.\n"
            f"  Attendu : {expected}\n"
            f"  Obtenu  : {decoded}"
        )

    def test_lowercase_keys():
        """Les clés en minuscules doivent être normalisées en majuscules."""
        msg = "MESSAGE EN MINUSCULES TEST"
        c1, _ = encode_message(plugin, "secret", "passphrase", msg)
        c2, _ = encode_message(plugin, "SECRET", "PASSPHRASE", msg)
        assert c1 == c2, (
            "Le résultat doit être identique avec clés minuscules ou "
            f"majuscules.\n  c1 = {c1[:40]}...\n  c2 = {c2[:40]}..."
        )

    runner.add("Normalisation — message avec accents",
               test_accents_handled)
    runner.add("Normalisation — clés en minuscules",
               test_lowercase_keys)

    # -------------------------------------------------------------------
    # Tests de propriétés algorithmiques
    # -------------------------------------------------------------------

    def test_keys_matter():
        """Deux jeux de clés différents doivent produire des cryptogrammes
        différents pour le même message."""
        msg = "MESSAGE STANDARD POUR TEST DE CLES"
        c1, _ = encode_message(plugin, "ALPHABET", "GAMMADELTA", msg)
        c2, _ = encode_message(plugin, "BETAOMEGA", "EPSILONTHETA", msg)
        assert c1 != c2, (
            "Deux jeux de clés distincts doivent produire des cryptos "
            "distincts."
        )

    def test_deterministic():
        """Le chiffrement doit être déterministe : même entrée → même sortie."""
        msg = "DETERMINISTIC TEST MESSAGE FIN"
        c1, _ = encode_message(plugin, "CLEDETEST", "AUTRECLE", msg)
        c2, _ = encode_message(plugin, "CLEDETEST", "AUTRECLE", msg)
        assert c1 == c2, (
            "Le chiffrement doit être déterministe.\n"
            f"  Premier : {c1}\n  Second : {c2}"
        )

    def test_groups_of_5():
        """La sortie doit toujours être en groupes de 5 séparés par espace."""
        msg = "TEST GROUPS OF FIVE FIN"
        crypto, _ = encode_message(plugin, "KEYONE", "KEYTWOO", msg)
        groups = crypto.split(" ")
        for i, g in enumerate(groups):
            if i < len(groups) - 1:
                # Tous les groupes sauf éventuellement le dernier font 5
                assert len(g) == 5, (
                    f"Groupe {i} a {len(g)} caractères, attendu 5 : {g!r}\n"
                    f"Crypto : {crypto}"
                )
            # Le dernier peut avoir 1-5 caractères avec X de bourrage
            assert g.isalpha() and g.isupper(), \
                f"Groupe {i} contient des caractères invalides : {g!r}"

    runner.add("Algorithme — clés différentes → cryptos différents",
               test_keys_matter)
    runner.add("Algorithme — chiffrement déterministe",
               test_deterministic)
    runner.add("Algorithme — sortie en groupes de 5",
               test_groups_of_5)

    # -------------------------------------------------------------------
    # Tests fuzz — chiffrements aléatoires
    # -------------------------------------------------------------------

    if not quick:

        def test_fuzz_short_messages():
            """50 aller-retours sur des messages courts (10-50 chars)."""
            rng = random.Random(42)  # graine fixe pour reproductibilité
            n_iter = 50
            for i in range(n_iter):
                msg = random_message(10, 50, rng)
                k1 = random_key(5, 15, rng)
                k2 = random_key(5, 15, rng)
                if not msg or not k1 or not k2:
                    continue
                try:
                    d = encode_decode_roundtrip(plugin, k1, k2, msg)
                except AssertionError:
                    raise
                except Exception as e:
                    raise AssertionError(
                        f"Itération {i} : exception inattendue\n"
                        f"  msg={msg!r}\n  k1={k1!r}\n  k2={k2!r}\n"
                        f"  Erreur : {e}"
                    )
                expected = _normalize_text(msg)
                assert d == expected, (
                    f"Aller-retour fuzz court #{i} cassé.\n"
                    f"  msg = {msg!r}\n  k1 = {k1!r}\n  k2 = {k2!r}\n"
                    f"  attendu = {expected}\n  obtenu  = {d}"
                )

        def test_fuzz_long_messages():
            """20 aller-retours sur des messages longs (100-300 chars)."""
            rng = random.Random(123)
            for i in range(20):
                msg = random_message(100, 300, rng)
                k1 = random_key(8, 25, rng)
                k2 = random_key(8, 25, rng)
                if not msg or not k1 or not k2:
                    continue
                d = encode_decode_roundtrip(plugin, k1, k2, msg)
                expected = _normalize_text(msg)
                assert d == expected, (
                    f"Aller-retour fuzz long #{i} cassé.\n"
                    f"  msg longueur = {len(expected)}\n"
                    f"  k1 = {k1!r} (len={len(k1)})\n"
                    f"  k2 = {k2!r} (len={len(k2)})\n"
                    f"  attendu = {expected[:60]}...\n"
                    f"  obtenu  = {d[:60]}..."
                )

        def test_fuzz_keys_with_doubles():
            """Clés contenant beaucoup de doublons (cas litigieux)."""
            cases = [
                ("AAAA", "BBBB"),       # tout en doublons
                ("AABBCC", "DDEEFF"),   # paires
                ("AAAAB", "ABABA"),     # alternances
                ("ZZZAAA", "MNOPMNOP"), # doublons multiples
            ]
            msg = "MESSAGE TEST POUR CLES AVEC DOUBLONS NOMBREUX FIN"
            for k1, k2 in cases:
                d = encode_decode_roundtrip(plugin, k1, k2, msg)
                expected = _normalize_text(msg)
                assert d == expected, (
                    f"Doublons cassés : k1={k1!r} k2={k2!r}\n"
                    f"  attendu = {expected}\n  obtenu = {d}"
                )

        def test_fuzz_edge_lengths():
            """Messages très courts, très longs, et longueurs limites."""
            cases = [
                "A",                          # 1 caractère
                "AB",                         # 2
                "ABCDE",                      # exactement 1 groupe
                "ABCDEFGHIJ",                 # 2 groupes
                "X" * 500,                    # gros message tout en X
                "A" * 17 + "B",               # juste sous une clé de 18
                "A" * 18,                     # exactement 1 ligne de grille
                "A" * 19,                     # 1 ligne + 1
            ]
            k1 = "RIENNESERTDECOURIR"
            k2 = "ILFAUTPARTIRAPOINT"
            for msg in cases:
                d = encode_decode_roundtrip(plugin, k1, k2, msg)
                expected = _normalize_text(msg)
                assert d == expected, (
                    f"Edge case cassé : msg longueur {len(msg)}\n"
                    f"  attendu = {expected[:60]}...\n"
                    f"  obtenu  = {d[:60]}..."
                )

        runner.add("Fuzz — 50 aller-retours sur messages courts",
                   test_fuzz_short_messages)
        runner.add("Fuzz — 20 aller-retours sur messages longs",
                   test_fuzz_long_messages)
        runner.add("Fuzz — clés avec doublons multiples",
                   test_fuzz_keys_with_doubles)
        runner.add("Fuzz — longueurs limites (1, 2, 5, 18, 500)",
                   test_fuzz_edge_lengths)

    # -------------------------------------------------------------------
    # Test de chaîne complète SOE INIT → SOE COD → SOE DECODE
    # -------------------------------------------------------------------

    def test_full_chain():
        """Simule l'enchaînement complet : init des variables, COD, DECODE.
        Reproduit le workflow de l'opérateur en exercice ADRASEC."""
        # ÉTAPE 1 : opérateur saisit /set CLE1=, /set CLE2=, /set MESSAGE=
        session = MockSessionVars()
        session.set("CLE1", "RIENNESERTDECOURIR")
        session.set("CLE2", "ILFAUTPARTIRAPOINT")
        session.set("MESSAGE", "EXERCICE ADRASEC SEINE ET MARNE BALISE "
                               "DETECTEE TERMINE")
        assert session.count() == 3, "Étape 1 : 3 variables attendues"

        # ÉTAPE 2 : clic sur SOE COD → produit CRYPTO + CRYPTOMETA
        plugin.execute_action(
            "soe_encode", imported_files=(),
            options={
                "session_vars": session.all(),
                "session_vars_manager": session,
            }
        )
        # 3 + CRYPTO + CRYPTOMETA = 5
        assert session.count() == 5, (
            f"Étape 2 : 5 variables attendues "
            f"(CLE1, CLE2, MESSAGE, CRYPTO, CRYPTOMETA), "
            f"reçu {session.count()} : {session.names()}"
        )
        assert session.get("CRYPTO"), "CRYPTO doit être présent"
        assert session.get("CRYPTOMETA"), "CRYPTOMETA doit être présent"

        # ÉTAPE 3 : clic sur SOE DECODE → produit MESSAGE_DECODE
        plugin.execute_action(
            "soe_decode", imported_files=(),
            options={
                "session_vars": session.all(),
                "session_vars_manager": session,
            }
        )
        # 5 + MESSAGE_DECODE = 6
        assert session.count() == 6, (
            f"Étape 3 : 6 variables attendues, reçu {session.count()} : "
            f"{session.names()}"
        )
        assert session.get("MESSAGE_DECODE"), \
            "MESSAGE_DECODE doit être présent"

        # ÉTAPE 4 : validation
        original = _normalize_text(session.get("MESSAGE"))
        decoded = session.get("MESSAGE_DECODE")
        assert decoded == original, (
            f"Chaîne complète cassée.\n"
            f"  Original (normalisé) : {original}\n"
            f"  Décodé : {decoded}"
        )

    runner.add("Chaîne complète — INIT → COD → DECODE (workflow opérateur)",
               test_full_chain)

    # -------------------------------------------------------------------
    # Vérification que CRYPTO ne contient que A-Z et espaces
    # -------------------------------------------------------------------

    def test_crypto_charset():
        """Le cryptogramme ne doit contenir que [A-Z ]."""
        msg = "MESSAGE NORMAL POUR VERIFIER LE CHARSET"
        c, _ = encode_message(plugin, "CLEDETEST", "AUTRECLE", msg)
        assert re.fullmatch(r"[A-Z ]+", c), (
            f"Le cryptogramme ne doit contenir que A-Z et espaces. "
            f"Reçu : {c!r}"
        )

    runner.add("Sortie — cryptogramme uniquement [A-Z ]",
               test_crypto_charset)


# ===========================================================================
# Main
# ===========================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Tests automatisés de la chaîne SOE pour IAbrain v1.40.7+"
    )
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Afficher les tracebacks complets")
    parser.add_argument("--plugin-dir",
                        help="Chemin direct vers IAbrain_actions_soe.py")
    parser.add_argument("--quick", action="store_true",
                        help="Skip les tests fuzz (plus rapide)")
    args = parser.parse_args()

    # Localisation et chargement du plugin
    try:
        plugin_path = find_plugin(args.plugin_dir)
        print(f"\n{C.DIM}Plugin chargé depuis : {plugin_path}{C.END}")
        plugin = load_plugin(plugin_path)
    except (FileNotFoundError, ImportError) as e:
        print(f"\n{C.FAIL}❌ Erreur d'environnement :{C.END}\n   {e}\n")
        return 2

    # Construction et exécution des tests
    runner = TestRunner(verbose=args.verbose)
    make_tests(plugin, runner, quick=args.quick)
    success = runner.run()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
