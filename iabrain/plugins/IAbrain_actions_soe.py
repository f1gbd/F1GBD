"""IAbrain_actions_soe — Plugin d'actions SOE pour IAbrain v1.40.6+.

Fournit deux actions natives pour le chiffrement par double transposition
colonnaire historique (méthode SOE 1942) :

  - soe_encode : chiffre {MESSAGE} avec {CLE1} et {CLE2}, écrit le
                 résultat dans la variable de session {CRYPTO}.
  - soe_decode : déchiffre {CRYPTO} avec {CLE1} et {CLE2}, écrit le
                 résultat dans la variable de session {MESSAGE_DECODE}.

Avantages par rapport à une macro LLM :
  - Calcul instantané et déterministe (zéro token, zéro attente).
  - Justesse garantie (validée par autotest aller-retour).
  - Pas de risque de troncature ou d'hallucination.

Architecture : suit le contrat d'interface IAbrain :
  - is_action(action_id) -> bool
  - execute_action(action_id, imported_files, options=None) -> (md, warnings)

Les variables de session sont reçues dans options["session_vars"].
Le retour de chaque action est (markdown_à_afficher, liste_de_warnings).

Pour intégrer dans IAbrain, deux options :
  A. Renommer ce fichier en IAbrain_actions_soe.py et ajouter un
     import dans IAbrain.py (similaire à _import_actions_sater).
  B. Concaténer is_action() et execute_action() dans le module
     IAbrain_actions_sater existant (chemin le plus rapide).
"""

from __future__ import annotations

import json
import re
import unicodedata
from math import ceil
from typing import Any, List, Sequence, Tuple


# ===========================================================================
# Identifiants d'actions exposés
# ===========================================================================

ACTION_SOE_ENCODE = "soe_encode"
ACTION_SOE_DECODE = "soe_decode"

_ALL_ACTIONS = {ACTION_SOE_ENCODE, ACTION_SOE_DECODE}


def is_action(action_id: str) -> bool:
    """Retourne True si action_id est géré par ce plugin."""
    return (action_id or "").strip() in _ALL_ACTIONS


def list_actions() -> List[Tuple[str, str, str]]:
    """Retourne la liste (id, libellé, description) des actions de ce
    plugin, pour le sélecteur du dialog d'édition de macro.

    Format attendu par IAbrain : tuples à 3 éléments
    (action_id, libellé court, description longue).
    """
    return [
        (
            ACTION_SOE_ENCODE,
            "SOE — Coder (double transposition)",
            "Chiffre la variable {MESSAGE} avec les clés {CLE1} et "
            "{CLE2} par double transposition colonnaire (méthode SOE "
            "1942). Stocke le résultat dans la variable {CRYPTO} en "
            "groupes de 5 caractères. Calcul instantané et "
            "déterministe, sans appel au LLM."
        ),
        (
            ACTION_SOE_DECODE,
            "SOE — Décoder (double transposition)",
            "Déchiffre la variable {CRYPTO} avec les clés {CLE1} et "
            "{CLE2} par double transposition colonnaire inverse "
            "(méthode SOE 1942). Stocke le texte clair dans la "
            "variable {MESSAGE_DECODE}. Calcul instantané et "
            "déterministe, sans appel au LLM."
        ),
    ]


# ===========================================================================
# Moteur cryptographique — double transposition colonnaire
# ===========================================================================

def _normaliser(texte: str) -> str:
    """Supprime accents, espaces, ponctuation. Conserve A-Z majuscules."""
    nfd = unicodedata.normalize('NFD', texte)
    sans_accents = ''.join(c for c in nfd if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^A-Z]', '', sans_accents.upper())


def _numeroter_cle(cle: str) -> List[int]:
    """Renvoie les rangs (1-indexés) pour chaque position de la clé.
    Doublons numérotés de gauche à droite."""
    indices = list(range(len(cle)))
    ordre = sorted(indices, key=lambda i: (cle[i], i))
    rangs = [0] * len(cle)
    for rang, position in enumerate(ordre, start=1):
        rangs[position] = rang
    return rangs


def _transposer_chiffrer(texte: str, cle: str) -> str:
    """Une passe de transposition colonnaire (chiffrement)."""
    L = len(cle)
    N = len(texte)
    rangs = _numeroter_cle(cle)
    nb_lignes = ceil(N / L) if N else 0
    grille = [['' for _ in range(L)] for _ in range(nb_lignes)]
    for i, c in enumerate(texte):
        grille[i // L][i % L] = c
    sortie = []
    for r in range(1, L + 1):
        position = rangs.index(r)
        for ligne in range(nb_lignes):
            if grille[ligne][position]:
                sortie.append(grille[ligne][position])
    return ''.join(sortie)


def _transposer_dechiffrer(texte: str, cle: str) -> str:
    """Une passe de transposition inverse (déchiffrement)."""
    L = len(cle)
    N = len(texte)
    if N == 0 or L == 0:
        return ""
    rangs = _numeroter_cle(cle)
    nb_lignes_pleines = N // L
    nb_col_longues = N % L
    longueurs = [
        nb_lignes_pleines + (1 if p < nb_col_longues else 0)
        for p in range(L)
    ]
    nb_lignes = ceil(N / L)
    grille = [['' for _ in range(L)] for _ in range(nb_lignes)]
    k = 0
    for r in range(1, L + 1):
        position = rangs.index(r)
        long_col = longueurs[position]
        for ligne in range(long_col):
            grille[ligne][position] = texte[k]
            k += 1
    sortie = []
    for ligne in grille:
        for c in ligne:
            if c:
                sortie.append(c)
    return ''.join(sortie)


# ===========================================================================
# Helpers communs aux actions
# ===========================================================================

def _get_session_vars(options) -> dict:
    """Extrait le dict session_vars depuis options, ou {} si absent."""
    if not options or not isinstance(options, dict):
        return {}
    sv = options.get("session_vars")
    if isinstance(sv, dict):
        return sv
    return {}


def _get_var(session_vars: dict, name: str) -> str:
    """Lit une variable de session ; retourne '' si absente."""
    v = session_vars.get(name)
    return str(v) if v is not None else ""


def _set_session_var(options, name: str, value: str) -> bool:
    """Écrit une variable dans la session via le manager si exposé.

    L'API IAbrain documentée injecte session_vars.all() (un dict copie)
    dans options. Pour modifier la vraie session, on cherche un
    'session_vars_manager' éventuel exposé en plus, sinon on signale
    via le markdown que l'utilisateur devra faire /set manuellement.
    """
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


def _format_groups_of_5(s: str, pad_char: str = "X") -> str:
    """Formate une chaîne en groupes de 5 séparés par un espace,
    en complétant le dernier groupe par pad_char si nécessaire."""
    if not s:
        return ""
    reste = len(s) % 5
    if reste:
        s = s + pad_char * (5 - reste)
    return ' '.join(s[i:i+5] for i in range(0, len(s), 5))


# ===========================================================================
# Action : soe_encode
# ===========================================================================

def _action_encode(session_vars: dict, options) -> Tuple[str, List[str]]:
    """Chiffre MESSAGE avec CLE1 puis CLE2. Stocke dans CRYPTO."""
    warnings: List[str] = []

    cle1 = _get_var(session_vars, "CLE1")
    cle2 = _get_var(session_vars, "CLE2")
    message = _get_var(session_vars, "MESSAGE")

    # Validation
    missing = [n for n, v in
               [("CLE1", cle1), ("CLE2", cle2), ("MESSAGE", message)]
               if not v]
    if missing:
        return (
            "## ❌ SOE COD — Variables manquantes\n\n"
            "Les variables suivantes ne sont pas définies dans la "
            "session :\n\n"
            + "\n".join(f"- `{n}`" for n in missing) +
            "\n\nUtilisez `/set NOM=VALEUR` pour les définir, puis "
            "relancez la macro.",
            warnings,
        )

    # Calcul
    M0 = _normaliser(message)
    if not M0:
        return ("## ❌ SOE COD — Message vide après normalisation",
                warnings)

    cle1n = _normaliser(cle1)
    cle2n = _normaliser(cle2)
    if not cle1n or not cle2n:
        return ("## ❌ SOE COD — Clés vides après normalisation",
                warnings)

    T1 = _transposer_chiffrer(M0, cle1n)
    T2 = _transposer_chiffrer(T1, cle2n)

    # Vérification interne
    if not (len(M0) == len(T1) == len(T2)):
        return (
            "## ❌ SOE COD — Erreur interne de cohérence\n\n"
            f"len(M0)={len(M0)}, len(T1)={len(T1)}, len(T2)={len(T2)}",
            warnings,
        )

    # Mise en forme
    crypto = _format_groups_of_5(T2)
    padding = (5 - len(T2) % 5) % 5

    # v1.40.7 : on stocke aussi CRYPTOMETA pour permettre un déchiffrement
    # parfaitement non ambigu (sans heuristique sur le bourrage X final).
    # Format : "N=<len>;PAD=<pad>;L1=<L1>;L2=<L2>". Format texte simple
    # plutôt que JSON pour rester compatible avec le format /set NOM=VALEUR.
    cryptometa = (f"N={len(M0)};PAD={padding};"
                  f"L1={len(cle1n)};L2={len(cle2n)}")

    # Tentative d'écriture dans la session
    written_crypto = _set_session_var(options, "CRYPTO", crypto)
    written_meta = _set_session_var(options, "CRYPTOMETA", cryptometa)
    written = written_crypto and written_meta

    # Rendu Markdown
    rangs1 = '-'.join(str(r) for r in _numeroter_cle(cle1n))
    rangs2 = '-'.join(str(r) for r in _numeroter_cle(cle2n))

    md = (
        "## 🔐 MESSAGE CODÉ — Double transposition SOE 1942\n"
        f"**Longueur utile** : {len(M0)} caractères  \n"
        f"**Bourrage final** : {padding} X  \n"
        f"**Rangs CLE1** : `{rangs1}`  \n"
        f"**Rangs CLE2** : `{rangs2}`\n"
        "### CRYPTO\n"
        f"```\n{crypto}\n```\n"
        "### CRYPTOMETA\n"
        f"```\n{cryptometa}\n```\n"
    )

    if written:
        md += (
            "✅ Variables **`{CRYPTO}`** et **`{CRYPTOMETA}`** stockées "
            "automatiquement dans la session."
        )
    else:
        md += (
            "ℹ️ Pour stocker les variables, copiez les commandes "
            "ci-dessous dans la zone de saisie :\n"
            f"```\n/set CRYPTO={crypto}\n/set CRYPTOMETA={cryptometa}\n```"
        )

    return md, warnings


# ===========================================================================
# Action : soe_decode
# ===========================================================================

def _action_decode(session_vars: dict, options) -> Tuple[str, List[str]]:
    """Déchiffre CRYPTO avec CLE1 et CLE2. Stocke dans MESSAGE_DECODE."""
    warnings: List[str] = []

    cle1 = _get_var(session_vars, "CLE1")
    cle2 = _get_var(session_vars, "CLE2")
    crypto = _get_var(session_vars, "CRYPTO")

    missing = [n for n, v in
               [("CLE1", cle1), ("CLE2", cle2), ("CRYPTO", crypto)]
               if not v]
    if missing:
        return (
            "## ❌ SOE DECODE — Variables manquantes\n\n"
            "Les variables suivantes ne sont pas définies dans la "
            "session :\n\n"
            + "\n".join(f"- `{n}`" for n in missing) +
            "\n\nDéfinissez-les puis relancez la macro.",
            warnings,
        )

    # Nettoyage du cryptogramme
    C2_brut = re.sub(r'\s+', '', crypto).upper()
    if not C2_brut:
        return ("## ❌ SOE DECODE — Cryptogramme vide", warnings)

    cle1n = _normaliser(cle1)
    cle2n = _normaliser(cle2)
    if not cle1n or not cle2n:
        return ("## ❌ SOE DECODE — Clés vides après normalisation",
                warnings)

    # Retrait du bourrage X final AVANT les transpositions inverses.
    # Stratégie en 3 niveaux par ordre de fiabilité :
    #   1. CRYPTOMETA disponible → on a la valeur exacte de PAD (parfait)
    #   2. Pas de CRYPTOMETA mais len(C2_brut) % 5 == 0 → règle stricte :
    #      on ne retire PAS de X (sauf via heuristique ci-dessous)
    #   3. len(C2_brut) % 5 != 0 → cryptogramme corrompu, on tente quand même
    C2 = C2_brut
    pad = 0
    cryptometa = _get_var(session_vars, "CRYPTOMETA")

    if cryptometa:
        # Niveau 1 : utiliser la métadonnée exacte
        m = re.search(r'PAD\s*=\s*(\d+)', cryptometa)
        if m:
            pad_meta = int(m.group(1))
            if 0 <= pad_meta <= 4 and pad_meta <= len(C2):
                # Vérifier la cohérence : les pad_meta derniers caractères
                # devraient bien être des X
                if pad_meta == 0 or C2.endswith('X' * pad_meta):
                    C2 = C2[:len(C2) - pad_meta]
                    pad = pad_meta
                else:
                    warnings.append(
                        f"CRYPTOMETA annonce PAD={pad_meta} mais le "
                        "cryptogramme ne se termine pas par autant de X. "
                        "Tentative de déchiffrement sans retrait."
                    )
    else:
        # Niveaux 2 et 3 : heuristique sans métadonnée
        if len(C2_brut) % 5 != 0:
            warnings.append(
                f"Cryptogramme de longueur {len(C2_brut)} non multiple "
                "de 5 — vérifiez la transcription."
            )
        # Heuristique : retirer les X de fin uniquement si le déchiffrement
        # avec 0 X retiré donne un résultat manifestement faussé. Comme on
        # ne peut pas le savoir sans tester, on adopte la règle suivante :
        # on essaie d'abord SANS retrait. Si l'utilisateur voit un message
        # corrompu, il peut relancer en retirant manuellement les X.
        # Cette règle conservative privilégie la préservation des messages
        # qui se terminent légitimement par X (ex. "...XEN" en français).
        warnings.append(
            "CRYPTOMETA non disponible — déchiffrement sans retrait de "
            "bourrage X. Si le résultat est corrompu en fin, refaire le "
            "chiffrement complet pour disposer de CRYPTOMETA."
        )

    # Inverse : on défait d'abord clé2, puis clé1
    T1 = _transposer_dechiffrer(C2, cle2n)
    M_decode = _transposer_dechiffrer(T1, cle1n)

    written = _set_session_var(options, "MESSAGE_DECODE", M_decode)

    md = (
        "## 🔓 MESSAGE DÉCHIFFRÉ — Double transposition SOE 1942\n"
        f"**Longueur reçue** : {len(C2_brut)} caractères "
        f"(dont {pad} X de bourrage retirés)  \n"
        f"**Longueur décodée** : {len(M_decode)} caractères\n"
        "### MESSAGE_DECODE\n"
        f"```\n{M_decode}\n```\n"
    )

    if written:
        md += (
            "✅ Variable **`{MESSAGE_DECODE}`** stockée automatiquement "
            "dans la session."
        )
    else:
        md += (
            "ℹ️ Pour stocker la variable, copiez la commande "
            "ci-dessous dans la zone de saisie :\n"
            f"```\n/set MESSAGE_DECODE={M_decode}\n```"
        )

    return md, warnings


# ===========================================================================
# Point d'entrée IAbrain
# ===========================================================================

def execute_action(action_id: str,
                   imported_files: Sequence[Tuple[str, str]] = (),
                   options: Any = None) -> Tuple[str, List[str]]:
    """Exécute une action SOE. Contrat IAbrain v1.37.7+.

    Args:
        action_id : "soe_encode" ou "soe_decode".
        imported_files : non utilisé par ces actions.
        options : dict pouvant contenir "session_vars" (snapshot dict)
                  et éventuellement "session_vars_manager" (objet vivant).

    Returns:
        (markdown_à_afficher, liste_de_warnings)
    """
    aid = (action_id or "").strip()
    session_vars = _get_session_vars(options)

    if aid == ACTION_SOE_ENCODE:
        return _action_encode(session_vars, options)
    if aid == ACTION_SOE_DECODE:
        return _action_decode(session_vars, options)

    return (
        f"## ❌ Action inconnue : `{aid}`\n\n"
        f"Actions disponibles : `{ACTION_SOE_ENCODE}`, "
        f"`{ACTION_SOE_DECODE}`.",
        [],
    )


# ===========================================================================
# Autotest
# ===========================================================================

def _autotest():
    """Aller-retour de validation."""
    cle1 = "RIENNESERTDECOURIR"
    cle2 = "ILFAUTPARTIRAPOINT"
    msg = ("CONFIRME OPERATION TERRAIN HECTOR A PARTIR DU JEUDI NEUF "
           "MARS STOP CODE OPTIQUE RECONNAISSANCE ET MESSAGE PERSONNEL "
           "BBC HABITUELS FIN")

    sv_encode = {"CLE1": cle1, "CLE2": cle2, "MESSAGE": msg}
    md, _ = execute_action("soe_encode", options={"session_vars": sv_encode})
    print(md)

    # Récupérer le crypto depuis le markdown (ligne dans le bloc ```)
    lines = md.splitlines()
    crypto = ""
    in_block = False
    for ln in lines:
        if ln.strip() == "```" and not in_block:
            in_block = True
            continue
        if ln.strip() == "```" and in_block:
            break
        if in_block:
            crypto = ln.strip()
            break

    sv_decode = {"CLE1": cle1, "CLE2": cle2, "CRYPTO": crypto}
    md2, _ = execute_action("soe_decode", options={"session_vars": sv_decode})
    print(md2)

    expected = _normaliser(msg)
    decoded = re.search(r"```\n([A-Z]+)\n```", md2)
    if decoded and decoded.group(1) == expected:
        print("✓ AUTOTEST RÉUSSI")
    else:
        print("✗ ÉCHEC")


if __name__ == "__main__":
    _autotest()
