"""IAbrain_actions_sitrep — Plugin d'actions natives ADRASEC pour IAbrain v1.41+.

Action exposée
--------------

``fill_sitrep_adrasec`` : remplit automatiquement le PDF SITREP-ADRASEC
saisissable (formulaire AcroForm v1.1 par F1GBD, mai 2026) à partir :

  - du **dernier fichier texte importé** (scénario, prompt, brouillon
    d'opérateur, etc.) ;
  - OU d'un texte placé dans la variable de session ``SITREP_TEXT`` ;
  - OU d'un texte vide → seul l'en-tête (date/heure/indicatif) est rempli,
    le reste du formulaire est laissé vierge pour saisie manuelle.

Le PDF source (template vierge) est cherché dans cet ordre :

  1. Variable de session ``SITREP_TEMPLATE`` (chemin absolu ou relatif).
  2. ``SITREP_ADRASEC.pdf`` dans le CWD.
  3. ``SITREP_ADRASEC.pdf`` à côté de l'exécutable / du script IAbrain.
  4. ``SITREP_ADRASEC.pdf`` dans le dossier parent de ``plugins/``.

Le PDF rempli est écrit à côté du CWD avec le nom
``SITREP_<commune>_<YYYYMMDD-HHMM>.pdf``. Le chemin est annoncé dans la
réponse de l'action ; l'opérateur peut ensuite l'ouvrir / le transmettre
via TCQ.

Extraction des champs
---------------------

Si Ollama est disponible et que la config IAbrain est lisible, l'action
interroge le LLM avec un prompt spécialisé qui demande un JSON strict
respectant le schéma SITREP. La réponse est validée champ par champ
contre la liste des valeurs autorisées (dropdowns) et tronquée si
nécessaire. Les valeurs non reconnues retombent silencieusement sur le
défaut du formulaire (``---``, ``MODEREE``, ``STABLE``...).

Si Ollama n'est pas joignable, l'action remplit ce qu'elle peut depuis
les variables de session ({CALL}, {DTG}, {COMMUNE}, ...) et laisse le
reste vierge.

Contrat d'interface (plugin externe IAbrain v1.40.7+)
-----------------------------------------------------

  - is_action(action_id: str) -> bool
  - execute_action(action_id, imported_files, options=None)
        -> (markdown_result, warnings_list)
  - list_actions() -> list[tuple[str, str, str]]
        retourne [(action_id, label, description), ...]

Auteur : F1GBD / ADRASEC 77 — mai 2026.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, List, Optional, Sequence, Tuple


__version__ = "1.1.6"

# ---------------------------------------------------------------------------
# Identifiant et catalogue des actions
# ---------------------------------------------------------------------------

ACTION_ID = "fill_sitrep_adrasec"
ACTION_LABEL = "SITREP ADRASEC → PDF rempli"
ACTION_DESC = (
    "Remplit automatiquement le formulaire PDF SITREP_ADRASEC.pdf "
    "(AcroForm v1.1) à partir du dernier fichier texte importé ou de la "
    "variable de session SITREP_TEXT. Utilise Ollama pour extraire les "
    "champs structurés (priorité, gravité, demande de moyens…) puis "
    "écrit le PDF rempli à côté du PDF source."
)


def list_actions() -> List[Tuple[str, str, str]]:
    """Catalogue des actions exposées par ce plugin."""
    return [(ACTION_ID, ACTION_LABEL, ACTION_DESC)]


def is_action(action_id: str) -> bool:
    return (action_id or "").strip() == ACTION_ID


# ---------------------------------------------------------------------------
# Schéma SITREP : champs et valeurs autorisées
# ---------------------------------------------------------------------------
# Source de vérité : inspection du PDF SITREP_ADRASEC.pdf (mai 2026) avec
# pypdf. Toute valeur de dropdown non listée ici est rejetée et le champ
# garde sa valeur par défaut.

# Champs texte libres (AcroForm /Tx)
TEXT_FIELDS = (
    "msg_num", "dtg", "de_station", "a_station", "frequence", "indicatif_op",
    "commune", "cp", "dtg_pcs", "nom_autorite", "fonction_autorite",
    "pop_impactee", "pop_vulnerable", "description",
    "qte_1", "lieu_1", "qte_2", "lieu_2", "qte_3", "lieu_3",
    "qte_4", "lieu_4", "qte_5", "lieu_5", "qte_6", "lieu_6",
    "qte_7", "lieu_7",
    "lieu_pcc", "gps", "contact_terrain",
    "sig_autorite", "sig_operateur",
)

# Listes déroulantes (AcroForm /Ch) avec valeurs autorisées
CHOICE_FIELDS: dict[str, Tuple[str, ...]] = {
    "type_operation": ("EXERCICE - EXERCICE - EXERCICE", "REEL - REEL - REEL"),
    "priorite": ("ROUTINE", "PRIORITAIRE", "URGENT", "FLASH"),
    "mode_tcq": ("VARA HF", "VARA FM", "VARA SAT", "PACKET", "ARDOP", "LXMF"),
    "adrasec_concernee": (
        "ADRASEC 77", "ADRASEC 75", "ADRASEC 78", "ADRASEC 91",
        "ADRASEC 92", "ADRASEC 93", "ADRASEC 94", "ADRASEC 95", "AUTRE",
    ),
    "pcs_active": ("OUI", "NON", "EN COURS"),
    "autorite": (
        "MAIRE", "ADJOINT", "DGS", "PREFECTURE", "SDIS", "SAMU",
        "GENDARMERIE", "AUTRE",
    ),
    "gravite": ("FAIBLE", "MODEREE", "ELEVEE", "CRITIQUE"),
    "tendance": ("STABLE", "EN DEGRADATION", "EN AMELIORATION"),
    "acces": ("LIBRE", "RESTREINT", "4x4 UNIQUEMENT", "HELIPORTE", "INACCESSIBLE"),
}

# Listes déroulantes répétées pour les 7 lignes de demande de moyens
TYPE_OPTIONS = (
    "---", "EAU POTABLE", "VIVRES", "CARBURANT", "GROUPE ELECTROGENE",
    "MEDICAL", "EVACUATION", "HEBERGEMENT", "TRANSMISSIONS", "PERSONNEL",
    "AUTRE",
)
UNITE_OPTIONS = ("---", "L", "M3", "KG", "UNITE", "PALETTE", "PERS.", "LIT")
DELAI_OPTIONS = ("---", "IMMEDIAT", "< 1H", "< 3H", "< 6H", "< 24H", "J+1")
PRIO_OPTIONS = ("---", "P1", "P2", "P3", "P4")
for i in range(1, 8):
    CHOICE_FIELDS[f"type_{i}"] = TYPE_OPTIONS
    CHOICE_FIELDS[f"unite_{i}"] = UNITE_OPTIONS
    CHOICE_FIELDS[f"delai_{i}"] = DELAI_OPTIONS
    CHOICE_FIELDS[f"prio_{i}"] = PRIO_OPTIONS

# Cases à cocher (AcroForm /Btn)
CHECKBOX_FIELDS = (
    "chk_elec", "chk_gsm", "chk_eau", "chk_carb", "chk_transp", "chk_clim",
    "chk_feu", "chk_evac", "chk_victimes", "chk_routes", "chk_pde", "chk_pcc",
    "vld_autorite", "vld_tcq", "vld_copie",
)

# Mots-clés français → case correspondante (heuristique de secours quand
# le LLM est indisponible, et garde-fou de validation).
CHECKBOX_KEYWORDS: dict[str, Tuple[str, ...]] = {
    "chk_elec": (
        "coupure électrique", "blackout", "black-out", "panne electrique",
        "panne électrique", "plus d'électricité", "réseau électrique hs",
        "alimentation electrique", "alimentation électrique", "edf hs",
    ),
    "chk_gsm": (
        "gsm", "internet hors", "réseau mobile", "telephone mobile",
        "téléphone mobile", "sms hs", "operateurs telephoniques",
        "opérateurs téléphoniques", "internet coupé", "pas de réseau",
    ),
    "chk_eau": (
        "eau potable", "coupure d'eau", "coupure eau", "rupture eau",
        "château d'eau", "chateau d'eau", "pompes arrêtées", "pompes arretees",
    ),
    "chk_carb": (
        "carburant", "essence", "gazole", "diesel", "pénurie carburant",
        "penurie carburant", "stations service", "stations-service",
        "recharge electrique", "recharge électrique",
    ),
    "chk_transp": (
        "transports publics", "trains", "rer", "transilien", "métro", "metro",
        "bus arrêtés", "bus arretes", "circulation ferroviaire",
    ),
    "chk_clim": (
        "climatisation", "climatiseurs", "clim hs", "climatiseur hs",
        "climatisation hs", "ehpad", "hôpital surchauffe", "hopital surchauffe",
    ),
    "chk_feu": (
        "feu en cours", "incendie", "feux de forêt", "feux de foret",
        "départ de feu", "depart de feu",
    ),
    "chk_evac": (
        "évacuation", "evacuation", "évacuations sanitaires",
        "evacuations sanitaires",
    ),
    "chk_victimes": (
        "victime", "décès", "deces", "mort", "morts", "décédé", "decede",
        "bilan humain",
    ),
    "chk_routes": (
        "routes bloquées", "routes bloquees", "axes coupés", "axes coupes",
        "circulation impossible", "voie impraticable",
    ),
    "chk_pde": (
        "point de distribution", "points de distribution", "pde actif",
        "pde ouvert", "distribution d'eau",
    ),
    "chk_pcc": (
        "pcc ouvert", "pcc en mairie", "poste de commandement communal",
        "pcs activé", "pcs active",
    ),
}


# ---------------------------------------------------------------------------
# Exécution de l'action
# ---------------------------------------------------------------------------

def execute_action(action_id: str,
                   imported_files: Sequence[Tuple[str, str]] = (),
                   options: Optional[dict] = None,
                   ) -> Tuple[str, List[str]]:
    """Point d'entrée de l'action SITREP. Retourne (markdown, warnings)."""
    if not is_action(action_id):
        return (
            f"❌ Action inconnue pour le plugin SITREP : « {action_id} »",
            [f"Action {action_id} non gérée par IAbrain_actions_sitrep"],
        )

    warnings: List[str] = []
    options = options or {}
    session_vars = options.get("session_vars", {}) or {}

    # v1.1.6 : callback de progression optionnel. IAbrain ≥ v1.41.3 peut
    # exposer un callable `options["log"]` qui poste un message système
    # dans le chat en temps réel. Le plugin l'utilise pour publier sa
    # progression aux étapes coûteuses (test Ollama, appel LLM, écriture
    # PDF) afin que l'opérateur ne croie pas que l'application est plantée
    # pendant les 60-150 secondes que dure l'extraction.
    #
    # Fallback : si options["log"] n'est pas fourni (versions antérieures
    # d'IAbrain), on ignore silencieusement les appels. Le plugin reste
    # rétro-compatible.
    log_cb = options.get("log")
    def _progress(msg: str) -> None:
        """Publie un message de progression si callback dispo, sinon ignore."""
        if callable(log_cb):
            try:
                log_cb(msg)
            except Exception:
                pass

    _progress("🔍 SITREP : initialisation…")

    # --- Étape 1 : importer pypdf -------------------------------------------
    try:
        from pypdf import PdfReader, PdfWriter
        from pypdf.generic import NameObject, BooleanObject
    except ImportError as e:
        return (
            "❌ **Module `pypdf` introuvable**\n\n"
            "Installation : `pip install pypdf`\n\n"
            f"Détail : {e}",
            [f"pypdf non installé : {e}"],
        )

    # --- Étape 2 : localiser le PDF template --------------------------------
    template_path = _find_template(session_vars, warnings)
    if template_path is None:
        return (
            "❌ **PDF template SITREP introuvable**\n\n"
            "Cherché dans :\n"
            "1. Variable de session `SITREP_TEMPLATE` (à définir avec "
            "`!set SITREP_TEMPLATE = /chemin/vers/SITREP_ADRASEC.pdf`)\n"
            "2. `./SITREP_ADRASEC.pdf` (répertoire de travail)\n"
            "3. À côté de l'exécutable IAbrain\n"
            "4. Dans le dossier parent de `plugins/`\n\n"
            "👉 **Placez `SITREP_ADRASEC.pdf` à côté d'IAbrain.exe** "
            "ou définissez `SITREP_TEMPLATE` dans les variables de session.",
            ["Template PDF SITREP_ADRASEC.pdf introuvable"],
        )

    # --- Étape 3 : récupérer le texte source --------------------------------
    _progress("📥 SITREP : récupération du texte source…")
    source_text, source_origin = _gather_source_text(imported_files, session_vars)
    if not source_text:
        warnings.append(
            "Aucun texte source trouvé (fichier importé ni SITREP_TEXT) — "
            "seul l'en-tête sera pré-rempli."
        )

    # --- Étape 4 : extraire les champs --------------------------------------
    # Stratégie : si on a du texte ET Ollama est joignable, on appelle le LLM.
    # Sinon, on remplit à minima (DTG, indicatif, type_operation EXERCICE par
    # défaut, etc.) à partir des variables de session disponibles.
    data: dict[str, Any] = {}
    llm_used = False
    llm_error: Optional[str] = None

    if source_text:
        # v1.1.6 : message visible avant l'appel Ollama (qui peut bloquer
        # jusqu'à 300s sur les modèles 14B+). Sans ça, l'opérateur croit
        # que IAbrain est planté pendant 1-3 minutes.
        _progress(
            "🧠 SITREP : extraction par LLM en cours… "
            "(peut prendre 1-3 minutes selon le modèle, "
            "ne cliquez pas — patientez)"
        )
        try:
            data = _extract_via_llm(source_text, session_vars, warnings)
            llm_used = True
            _progress("✅ SITREP : extraction LLM terminée.")
        except _LLMUnavailable as e:
            llm_error = str(e)
            warnings.append(f"Ollama indisponible — extraction LLM ignorée : {e}")
            _progress("⚠️ SITREP : LLM indisponible, bascule heuristique…")
            data = _extract_heuristic(source_text, session_vars)
        except Exception as e:
            llm_error = str(e)
            warnings.append(f"Échec extraction LLM : {e} — bascule heuristique")
            _progress("⚠️ SITREP : extraction LLM en échec, bascule heuristique…")
            data = _extract_heuristic(source_text, session_vars)
    else:
        data = {}

    # --- Étape 5 : compléter / normaliser les valeurs -----------------------
    _progress("⚙️ SITREP : validation et nettoyage des champs…")
    data = _apply_session_defaults(data, session_vars)
    data = _validate_and_clamp(data, warnings)

    # Champs cochés (liste des noms de cases à activer)
    # v1.1.5 : fusion UNION (LLM + heuristique) au lieu de "LLM only sauf
    # si vide". Cas observé F1GBD 11/05/2026 16:15 : LLM coche 4 cases sur
    # un SITREP qui en justifie 10. L'heuristique mots-clés trouve les
    # 6 autres → on en fait l'union pour ne pas perdre d'info.
    llm_checked = list(data.pop("_checkboxes", []) or [])
    heuristic_checked = []
    if source_text:
        heuristic_checked = _infer_checkboxes_from_text(source_text)
    # Union des deux listes, en préservant l'ordre du LLM en premier
    checked = list(llm_checked)
    for c in heuristic_checked:
        if c not in checked:
            checked.append(c)
    # Trace dans warnings si l'heuristique a complété
    added_by_heuristic = [c for c in heuristic_checked if c not in llm_checked]
    if llm_checked and added_by_heuristic:
        warnings.append(
            f"Cases ajoutées par heuristique (oubliées par LLM) : "
            f"{', '.join(added_by_heuristic)}"
        )
    checked = [c for c in checked if c in CHECKBOX_FIELDS]

    # --- Étape 6 : remplir le PDF -------------------------------------------
    try:
        reader = PdfReader(str(template_path))
    except Exception as e:
        return (
            f"❌ Impossible d'ouvrir le PDF template :\n`{template_path}`\n\n{e}",
            warnings + [f"PdfReader: {e}"],
        )

    writer = PdfWriter(clone_from=reader)

    # Activer NeedAppearances pour que le lecteur regénère les glyphes des
    # champs après écriture de /V (pypdf n'écrit pas les apparences visuelles).
    try:
        root = writer._root_object
        if "/AcroForm" in root:
            acroform = root["/AcroForm"]
            acroform[NameObject("/NeedAppearances")] = BooleanObject(True)
    except Exception as e:
        warnings.append(f"NeedAppearances non posé : {e}")

    # Écrire les valeurs des champs texte + dropdown.
    # v1.1.0 : pour le seul champ multi-ligne du formulaire (`description`),
    # on convertit les sauts de ligne LF/CRLF en CR (PDF spec 1.7 §12.7.4.3).
    # v1.1.1 : les AUTRES champs sont mono-ligne ; tout saut de ligne y est
    # un artefact d'extraction et doit être REMPLACÉ par un espace, jamais
    # converti en CR (sinon Acrobat affiche un retour visible cassant).
    MULTILINE_FIELDS = {"description"}
    str_values = {}
    for k, v in data.items():
        if v is None or v == "" or k.startswith("_"):
            continue
        s = str(v)
        if "\n" in s or "\r" in s:
            if k in MULTILINE_FIELDS:
                # Normalise CRLF puis LF vers CR (séparateur PDF canonique)
                s = s.replace("\r\n", "\r").replace("\n", "\r")
            else:
                # Champ mono-ligne : on aplatit en espaces
                s = s.replace("\r\n", " ").replace("\n", " ").replace("\r", " ")
                # Nettoie les doubles espaces résultants
                s = re.sub(r"\s{2,}", " ", s).strip()
        str_values[k] = s

    if str_values:
        try:
            for page in writer.pages:
                writer.update_page_form_field_values(page, str_values)
        except Exception as e:
            warnings.append(f"Échec écriture champs texte : {e}")

    # Cases à cocher : trouver l'état "on" exact de chaque widget et le poser
    if checked:
        _set_checkboxes(writer, checked, warnings, NameObject)

    # --- Étape 7 : déterminer le chemin de sortie ---------------------------
    _progress("📄 SITREP : écriture du PDF rempli…")
    output_path = _build_output_path(template_path, data)
    try:
        with open(output_path, "wb") as f:
            writer.write(f)
    except Exception as e:
        return (
            f"❌ Échec écriture PDF rempli :\n`{output_path}`\n\n{e}",
            warnings + [f"Écriture PDF: {e}"],
        )

    _progress(f"✅ SITREP : PDF généré → {output_path.name}")

    # --- Étape 8 : journaliser dans session_vars (optionnel) ----------------
    svm = options.get("session_vars_manager") if options else None
    if svm is not None:
        try:
            svm.set("SITREP_LAST_PDF", str(output_path))
            svm.set("SITREP_LAST_DTG", str(data.get("dtg", "")))
        except Exception as e:
            warnings.append(f"session_vars.set échoué : {e}")

    # --- Étape 9 : construire le récap Markdown -----------------------------
    md = _build_recap_markdown(
        template_path=template_path,
        output_path=output_path,
        data=data,
        checked=checked,
        source_origin=source_origin,
        llm_used=llm_used,
        llm_error=llm_error,
    )
    return md, warnings


# ---------------------------------------------------------------------------
# Recherche du template PDF
# ---------------------------------------------------------------------------

def _find_template(session_vars: dict, warnings: List[str]) -> Optional[Path]:
    """Cherche le PDF SITREP vierge. Retourne le premier trouvé ou None."""
    candidates: List[Path] = []

    # 1. Variable de session explicite
    sv_path = (session_vars.get("SITREP_TEMPLATE") or "").strip()
    if sv_path:
        candidates.append(Path(sv_path).expanduser())

    # 2. CWD
    candidates.append(Path.cwd() / "SITREP_ADRASEC.pdf")

    # 3. À côté de l'exécutable (frozen) ou du script
    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).resolve().parent
    else:
        # En mode dev, sys.argv[0] pointe vers le script lanceur (IAbrain.py)
        try:
            exe_dir = Path(sys.argv[0]).resolve().parent
        except Exception:
            exe_dir = Path.cwd()
    candidates.append(exe_dir / "SITREP_ADRASEC.pdf")

    # 4. Dossier parent du plugin (./plugins/.. = racine d'IAbrain)
    try:
        plugin_parent = Path(__file__).resolve().parent.parent
        candidates.append(plugin_parent / "SITREP_ADRASEC.pdf")
    except Exception:
        pass

    for p in candidates:
        try:
            if p.is_file():
                return p
        except Exception:
            continue

    # Log debug pour aider l'utilisateur
    warnings.append("PDF template cherché dans : " +
                    " | ".join(str(c) for c in candidates))
    return None


# ---------------------------------------------------------------------------
# Récupération du texte source
# ---------------------------------------------------------------------------

def _gather_source_text(imported_files: Sequence[Tuple[str, str]],
                        session_vars: dict) -> Tuple[str, str]:
    """Retourne (texte, origine_lisible). Origine vide si rien.

    v1.1.3 : décode les `\\n` LITTÉRAUX (séquence de 2 caractères backslash+n)
    en vrais sauts de ligne LF dans SITREP_TEXT. Ce décodage est nécessaire
    parce que le bloc ``###IABRAIN_VARS###`` produit par le LLM contient des
    `\\n` littéraux (pour tenir sur une ligne dans le bloc), et IAbrain
    v1.41.x ne les décode pas automatiquement au moment de la capture
    session_var. Sans ce décodage, ``description`` du PDF apparaît comme
    "Commune : MEAUX\\nADRASEC : ADRASEC 77\\n..." (illisible).

    Idem pour SITREP_TEMPLATE (au cas où il contienne des \\n, peu probable
    mais ne coûte rien).
    """
    def _decode_literal_escapes(s: str) -> str:
        """Décode les séquences d'échappement courantes laissées littérales :
        - ``\\n`` → LF
        - ``\\t`` → TAB
        - ``\\r`` → CR
        - ``\\\\`` → \\

        On NE décode PAS via codecs.escape (trop permissif, accepterait
        \\x00, \\u0041, etc. avec risque d'injection). On fait un décodage
        ciblé des 4 séquences les plus probables uniquement.
        """
        if "\\" not in s:
            return s
        # Ordre important : \\\\ d'abord pour ne pas réinterpréter le \\ déjà décodé
        s = s.replace("\\\\", "\x00")  # sentinel temporaire
        s = s.replace("\\n", "\n")
        s = s.replace("\\r", "\r")
        s = s.replace("\\t", "\t")
        s = s.replace("\x00", "\\")  # restaure les vrais antislashes
        return s

    # 1. Variable de session SITREP_TEXT (prioritaire car explicite)
    sv_text = (session_vars.get("SITREP_TEXT") or "").strip()
    if sv_text:
        sv_text = _decode_literal_escapes(sv_text)
        return sv_text, "variable de session SITREP_TEXT"

    # 2. Dernier fichier importé
    if imported_files:
        name, content = imported_files[-1]
        if content and content.strip():
            return content, f"fichier importé « {name} »"

    # 3. Concaténer tous les fichiers s'il y en a plusieurs (cas rare)
    if imported_files:
        parts = []
        for n, c in imported_files:
            if c and c.strip():
                parts.append(f"=== {n} ===\n{c}")
        if parts:
            return "\n\n".join(parts), f"{len(parts)} fichier(s) importé(s)"

    return "", ""


# ---------------------------------------------------------------------------
# Extraction via LLM (Ollama)
# ---------------------------------------------------------------------------

class _LLMUnavailable(Exception):
    """Levée quand Ollama n'est pas joignable ou pas configuré."""


def _load_iabrain_config() -> dict:
    """Charge IAbrain.json depuis l'emplacement habituel (CWD ou exe-dir).

    Retourne un dict vide si introuvable.
    """
    candidates: List[Path] = [Path.cwd() / "IAbrain.json"]
    if getattr(sys, "frozen", False):
        candidates.append(Path(sys.executable).resolve().parent / "IAbrain.json")
    else:
        try:
            candidates.append(Path(sys.argv[0]).resolve().parent / "IAbrain.json")
        except Exception:
            pass
    for p in candidates:
        try:
            if p.is_file():
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            continue
    return {}


def _extract_via_llm(source_text: str, session_vars: dict,
                     warnings: List[str]) -> dict:
    """Interroge Ollama local pour extraire un JSON SITREP structuré.

    v1.1.0 : utilise les structured outputs Ollama 0.5+ (JSON Schema strict)
    pour forcer le modèle à produire TOUS les champs attendus, et non pas
    juste un champ ``description`` fourre-tout. Fallback automatique sur
    ``"format": "json"`` si Ollama est trop ancien ou si la requête échoue.

    Lève _LLMUnavailable si pas de serveur ou pas de réponse exploitable.
    """
    try:
        import requests
    except ImportError as e:
        raise _LLMUnavailable(f"requests non installé : {e}") from e

    cfg = _load_iabrain_config()
    base_url = (cfg.get("server_url") or "http://localhost:11434").rstrip("/")

    # v1.1.2 : sélection du modèle pour l'extraction structurée SITREP.
    #
    # Priorité (du plus prioritaire au moins prioritaire) :
    #   1. Variable de session ``SITREP_MODEL`` (override explicite opérateur)
    #   2. Config ``model`` (le "gros" modèle d'IAbrain — meilleur pour
    #      l'extraction structurée d'un JSON de 29 clés avec enum strict)
    #   3. Config ``model_simple`` (fallback si ``model`` n'est pas défini)
    #   4. Défaut codé en dur : ``qwen2.5:7b`` (minimum viable)
    #
    # POURQUOI L'INVERSION vs v1.1.0 : la tâche d'extraction SITREP exige
    # un modèle qui respecte strictement un schéma JSON Schema (29 clés
    # required + 9 dropdowns à enum). Les petits modèles 3B (llama3.2:3b,
    # phi3:3b) échouent à respecter le schéma : ils renvoient un JSON
    # syntaxiquement valide mais avec des champs omis ou vides. Le routing
    # "auto" d'IAbrain choisit ``model_simple`` pour les prompts courts,
    # mais le SITREP est une tâche COMPLEXE (long schéma, validation
    # enum). Il faut donc le forcer sur le gros modèle.
    sitrep_model_override = (session_vars.get("SITREP_MODEL") or "").strip()
    model = (sitrep_model_override
             or cfg.get("model")
             or cfg.get("model_simple")
             or "qwen2.5:7b")

    # Logger le modèle utilisé pour aider au diagnostic (apparaît dans le
    # récap Markdown après run). C'est CRUCIAL parce que le bug observé
    # par F1GBD le 11/05/2026 était directement causé par l'auto-route
    # qui sélectionnait llama3.2:3b incapable de produire le JSON complet.
    warnings.append(f"Modèle d'extraction utilisé : {model}")
    if "3b" in model.lower() or "1.5b" in model.lower() or "1b" in model.lower():
        warnings.append(
            f"⚠️ Modèle « {model} » sous-dimensionné pour l'extraction SITREP. "
            "Recommandation : configurer `model: qwen2.5:14b` (ou supérieur) "
            "dans IAbrain.json, ou poser `/set SITREP_MODEL=qwen2.5:14b`. "
            "Le filet de sécurité regex compensera mais la qualité sera dégradée."
        )

    # Test rapide de disponibilité
    try:
        r = requests.get(f"{base_url}/api/tags", timeout=3.0)
        if r.status_code != 200:
            raise _LLMUnavailable(f"Ollama répond HTTP {r.status_code}")
    except requests.RequestException as e:
        raise _LLMUnavailable(f"Ollama injoignable sur {base_url} : {e}") from e

    prompt = _build_extraction_prompt(source_text, session_vars)

    # On limite la longueur du contexte injecté pour éviter les timeouts
    # sur les petits modèles. 6000 caractères couvrent largement un scénario
    # ADRASEC type.
    if len(prompt) > 12000:
        warnings.append(
            f"Texte source tronqué de {len(prompt)} à 12000 caractères "
            "pour l'extraction LLM"
        )
        prompt = prompt[:12000] + "\n... [troncature]"

    # v1.1.3 : timeout configurable via SITREP_TIMEOUT (en secondes).
    # Défaut 300 s (5 min) au lieu de 120 s parce que :
    # - les modèles 14B+ sur hardware modeste (CPU only, GPU petit) tournent
    #   à 3-8 tok/s → un JSON de 29 clés = ~600 tokens = 75-200 s minimum
    # - les structured outputs ralentissent ENCORE le modèle (contraintes)
    # - le timeout précédent (120 s) causait des échecs systématiques sur
    #   qwen2.5:14b en local, observé chez F1GBD le 11/05/2026
    try:
        timeout_str = (session_vars.get("SITREP_TIMEOUT") or "").strip()
        timeout_sec = float(timeout_str) if timeout_str else 300.0
        if timeout_sec < 30 or timeout_sec > 1800:
            timeout_sec = 300.0
    except (ValueError, TypeError):
        timeout_sec = 300.0

    # v1.1.0 : tentative #1 avec JSON Schema structured outputs (Ollama 0.5+).
    schema_format = _build_sitrep_json_schema()
    raw_text = _call_ollama(
        base_url, model, prompt, schema_format, warnings,
        attempt_label="structured outputs", timeout_sec=timeout_sec,
    )

    if not raw_text:
        # Tentative #2 : fallback sur "format": "json" classique
        warnings.append(
            "Structured outputs indisponibles — fallback sur format=json"
        )
        raw_text = _call_ollama(
            base_url, model, prompt, "json", warnings,
            attempt_label="format json simple", timeout_sec=timeout_sec,
        )

    if not raw_text:
        raise _LLMUnavailable("Ollama a renvoyé une réponse vide (2 tentatives)")

    # Parser le JSON (avec garde-fou : extraire un bloc JSON si le modèle a
    # ajouté des commentaires)
    data = _parse_json_loose(raw_text, warnings)
    if not isinstance(data, dict):
        raise _LLMUnavailable(
            f"JSON renvoyé non-dictionnaire : {type(data).__name__}"
        )

    # v1.1.0 : filet de sécurité — si le LLM a quand même mis tout dans
    # ``description``, on essaie d'extraire les champs principaux par regex.
    # v1.1.1 : le filet utilise AUSSI le texte source brut (source_text) quand
    # la description du LLM est vide ou trop courte. Permet de récupérer la
    # commune, le CP, la fréquence, etc. même si le LLM a complètement
    # ignoré la section 2 du formulaire.
    data = _rescue_from_stuffed_description(data, warnings, source_text)

    # v1.1.4 : filtre ANTI-HALLUCINATION. Pour les champs critiques (commune,
    # CP, nom autorité, GPS, téléphone, fréquence…), si la valeur produite
    # par le LLM n'apparaît PAS du tout dans le source_text, c'est une
    # hallucination → on rejette. Sinon on garde.
    #
    # Cas observé F1GBD 11/05/2026 15:45 : input "BEAUX-SUR-MARNE / DUBOIS
    # Marie / 77105 / 145.275 / 09 12 34 56 78" → LLM hallucine "MEAUX /
    # DUPONT Jean / 77000 / 145.375 / 06 12 34 56 78" (recopie partielle
    # de l'exemple one-shot du prompt d'extraction — bug corrigé en v1.1.4
    # mais on ajoute ce filet en plus, ceinture+bretelles).
    data = _filter_hallucinations(data, source_text, warnings)

    # Convertir le tableau de "demandes" en lignes type_X/qte_X/unite_X/...
    data = _unpack_demandes(data, warnings)
    return data


def _filter_hallucinations(data: dict, source_text: str,
                            warnings: List[str]) -> dict:
    """Rejette les valeurs LLM qui n'apparaissent pas dans source_text.

    S'applique uniquement aux champs CRITIQUES (commune, CP, nom autorité,
    fonction, GPS, téléphone, fréquence, station DE/À, lieu PCC, msg_num,
    populations, DTG PCS). Les dropdowns et la description sont épargnés
    (le LLM peut légitimement reformuler).

    Pour chaque champ, on cherche la valeur (normalisée) dans le texte
    source (normalisé aussi). Si absente, on vide le champ et on émet
    un warning explicite. Le filet regex sera ensuite ré-appliqué si
    nécessaire (mais il l'a déjà été juste avant — donc en pratique
    cet appel récupère ce que le LLM aurait pu sauver et qu'on a rejeté).
    """
    if not source_text:
        return data

    # Champs critiques à vérifier (valeurs qui DOIVENT venir du source).
    # On exclut volontairement :
    #   - les dropdowns (priorite, gravite, mode_tcq, autorite, etc.) car le
    #     LLM les INFÈRE légitimement depuis le contenu
    #   - description, qui est un résumé reformulé
    #   - sig_operateur, type_operation, adrasec_concernee (souvent posés
    #     par défaut)
    #   - dtg (auto-rempli si absent)
    critical = (
        "commune", "cp", "nom_autorite", "fonction_autorite",
        "frequence", "gps", "contact_terrain", "lieu_pcc",
        "de_station", "a_station", "msg_num", "dtg_pcs",
        "pop_impactee", "pop_vulnerable", "indicatif_op",
    )

    # Normalisation pour comparaison : casse + accents
    src_norm = _normalize_for_match(source_text)

    rejected = []
    for key in critical:
        val = (data.get(key) or "").strip()
        if not val:
            continue

        # Heuristique : la valeur est "présente" si une part suffisante
        # apparaît dans le source. On découpe la valeur en tokens et on
        # vérifie qu'AU MOINS UN token non-trivial (> 3 caractères) est
        # présent dans le source. Pour les CP/téléphones/fréquences (que
        # des chiffres), on vérifie une substring.
        val_norm = _normalize_for_match(val)

        # Cas 1 : valeur purement numérique (CP, téléphone, populations)
        # → on cherche les chiffres directement
        digits = re.sub(r"\D+", "", val)
        if len(digits) >= 3 and digits in re.sub(r"\D+", "", src_norm):
            continue  # présente, OK

        # Cas 2 : valeur avec mots (commune, nom, fonction, lieu)
        # v1.1.4 : politique stricte — au moins la MOITIÉ des tokens
        # distinctifs (>4 caractères) doivent être dans le source.
        tokens = re.findall(r"[A-Z0-9]{4,}", val_norm)
        # On ignore les tokens "courants" qui apparaîtraient dans tout SITREP
        # (indicatif générique, ADRASEC, COD, PREFECTURE...)
        common_tokens = {
            "F1GBD", "F4JHW", "ADRASEC", "PREFECTURE", "COD", "PCO",
            "MAIRIE", "MAIRE", "PCC", "PCS", "ORSEC", "VARA", "TCQ",
            "EHPAD", "SDIS", "SAMU", "EXERCICE", "SALLE", "CONSEIL",
            "AVENUE", "BOULEVARD", "PLACE", "RUE", "ROUTE", "STADE",
            "GYMNASE", "ECOLE", "CENTRE", "ADJOINT", "ADJ",
            "STATION", "EMETTRICE", "DESTINATAIRE", "MODE", "FREQUENCE",
            "AUTORITE", "NOM", "PRENOM", "FONCTION", "EXACTE",
            "RELAIS", "SITUATION", "DEMANDES",
        }
        distinctive = [tok for tok in tokens if tok not in common_tokens]

        if not distinctive:
            # Pas de token distinctif → valeur soit générique soit
            # entièrement composée de mots communs. Pour éviter
            # "Mairie de Meaux, salle conseil" (où MEAUX a déjà été
            # filtré comme commune ailleurs) qui passerait ici, on
            # vérifie que TOUS les tokens (même communs) sont dans le
            # source. Cas conservateur : si tous les tokens "communs"
            # sont quand même dans le source, OK.
            if tokens and all(tok in src_norm for tok in tokens):
                continue  # OK
            # sinon : hallucination
        else:
            # Au moins la moitié des tokens distinctifs doivent être présents
            found = sum(1 for tok in distinctive if tok in src_norm)
            required = max(1, (len(distinctive) + 1) // 2)
            if found >= required:
                # v1.1.4 : check spécial pour contact_terrain — si le téléphone
                # n'est pas dans le source, c'est une hallucination même si
                # le nom passe. Le téléphone est plus distinctif que le nom.
                if key == "contact_terrain":
                    val_digits = re.sub(r"\D+", "", val)
                    if len(val_digits) >= 8:
                        src_digits = re.sub(r"\D+", "", src_norm)
                        if val_digits not in src_digits:
                            # Téléphone halluciné
                            pass  # tombe en hallucination
                        else:
                            continue  # OK
                    else:
                        continue  # pas de tél → OK
                else:
                    continue  # OK

        # Cas 3 : valeur courte (< 4 caractères) ou stop-word → on garde
        # par défaut (trop court pour distinguer hallucination de signal)
        if len(val) <= 4:
            continue

        # Aucune trace : c'est une hallucination
        rejected.append(f"{key}={val!r}")
        data[key] = ""

    if rejected:
        warnings.append(
            f"🚨 Anti-hallucination : {len(rejected)} champ(s) rejeté(s) "
            f"(absent(s) du SITREP_TEXT) → {', '.join(rejected[:5])}"
            + ("…" if len(rejected) > 5 else "")
        )
        # Relance le filet regex pour récupérer depuis source ce qui peut l'être
        _extract_fields_by_regex(source_text, data)

    return data


def _call_ollama(base_url: str, model: str, prompt: str,
                 fmt, warnings: List[str], attempt_label: str,
                 timeout_sec: float = 300.0) -> str:
    """Effectue UN appel à Ollama /api/generate avec gestion d'erreur souple.

    Retourne le texte de réponse, ou "" si échec (sans lever).

    v1.1.3 : timeout configurable (défaut 300 s au lieu de 120 s pour
    accommoder les modèles 14B+ sur hardware modeste).
    """
    try:
        import requests
    except ImportError:
        return ""
    try:
        resp = requests.post(
            f"{base_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "format": fmt,
                "options": {
                    "temperature": 0.1,
                    "num_ctx": 8192,
                },
            },
            timeout=timeout_sec,
        )
    except requests.RequestException as e:
        warnings.append(f"Ollama erreur réseau ({attempt_label}) : {e}")
        return ""

    if resp.status_code != 200:
        # Ollama < 0.5 ne reconnaît pas un schéma JSON comme valeur de
        # "format" et renvoie HTTP 400. C'est attendu, on bascule.
        warnings.append(
            f"Ollama HTTP {resp.status_code} ({attempt_label}) : "
            f"{resp.text[:200]}"
        )
        return ""

    try:
        body = resp.json()
        return body.get("response", "").strip()
    except Exception as e:
        warnings.append(f"Réponse Ollama illisible ({attempt_label}) : {e}")
        return ""


# JSON Schema des champs SITREP, utilisé par Ollama 0.5+ structured outputs.
# Chaque champ est marqué `required` pour forcer le modèle à le produire
# (au pire avec une valeur vide), ce qui évite le piège « tout dans
# description ».

def _build_sitrep_json_schema() -> dict:
    """Construit le JSON Schema strict pour Ollama structured outputs."""
    # Énums des dropdowns directement intégrés au schéma — Ollama va les
    # respecter strictement.
    return {
        "type": "object",
        "properties": {
            "type_operation": {
                "type": "string",
                "enum": list(CHOICE_FIELDS["type_operation"]),
            },
            "priorite": {
                "type": "string",
                "enum": list(CHOICE_FIELDS["priorite"]),
            },
            "mode_tcq": {
                "type": "string",
                "enum": list(CHOICE_FIELDS["mode_tcq"]),
            },
            "adrasec_concernee": {
                "type": "string",
                "enum": list(CHOICE_FIELDS["adrasec_concernee"]),
            },
            "pcs_active": {
                "type": "string",
                "enum": list(CHOICE_FIELDS["pcs_active"]),
            },
            "autorite": {
                "type": "string",
                "enum": list(CHOICE_FIELDS["autorite"]),
            },
            "gravite": {
                "type": "string",
                "enum": list(CHOICE_FIELDS["gravite"]),
            },
            "tendance": {
                "type": "string",
                "enum": list(CHOICE_FIELDS["tendance"]),
            },
            "acces": {
                "type": "string",
                "enum": list(CHOICE_FIELDS["acces"]),
            },
            "msg_num": {"type": "string"},
            "dtg": {"type": "string"},
            "de_station": {"type": "string"},
            "a_station": {"type": "string"},
            "frequence": {"type": "string"},
            "indicatif_op": {"type": "string"},
            "commune": {"type": "string"},
            "cp": {"type": "string"},
            "dtg_pcs": {"type": "string"},
            "nom_autorite": {"type": "string"},
            "fonction_autorite": {"type": "string"},
            "pop_impactee": {"type": "string"},
            "pop_vulnerable": {"type": "string"},
            "description": {"type": "string"},
            "demandes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "type": {
                            "type": "string",
                            "enum": list(TYPE_OPTIONS),
                        },
                        "qte": {"type": "string"},
                        "unite": {
                            "type": "string",
                            "enum": list(UNITE_OPTIONS),
                        },
                        "delai": {
                            "type": "string",
                            "enum": list(DELAI_OPTIONS),
                        },
                        "prio": {
                            "type": "string",
                            "enum": list(PRIO_OPTIONS),
                        },
                        "lieu": {"type": "string"},
                    },
                    "required": ["type", "qte", "unite", "delai", "prio", "lieu"],
                },
            },
            "lieu_pcc": {"type": "string"},
            "gps": {"type": "string"},
            "contact_terrain": {"type": "string"},
            "checkboxes": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": list(CHECKBOX_FIELDS),
                },
            },
            "sig_operateur": {"type": "string"},
        },
        # On force le modèle à produire TOUTES les clés principales.
        # Sans ça, qwen2.5:7b a tendance à ne renvoyer que "description"
        # avec tout dedans (bug observé en v1.0.0 sur Jean-Louis).
        "required": [
            "type_operation", "priorite", "mode_tcq", "adrasec_concernee",
            "pcs_active", "autorite", "gravite", "tendance", "acces",
            "msg_num", "dtg", "de_station", "a_station", "frequence",
            "indicatif_op", "commune", "cp", "dtg_pcs", "nom_autorite",
            "fonction_autorite", "pop_impactee", "pop_vulnerable",
            "description", "demandes", "lieu_pcc", "gps", "contact_terrain",
            "checkboxes", "sig_operateur",
        ],
    }


# ---------------------------------------------------------------------------
# Filet de sécurité : extraire des champs depuis une description fourre-tout
# ---------------------------------------------------------------------------

def _rescue_from_stuffed_description(data: dict,
                                     warnings: List[str],
                                     source_text: str = "") -> dict:
    """Filet de sécurité regex pour rattraper les champs que le LLM a omis.

    Deux scénarios déclenchent le filet (v1.1.1+) :

    1. **Stuffing** : ``description`` est longue (>200 char) ET la majorité
       des champs principaux est vide → cas d'un LLM qui a tout entassé
       dans description. On extrait les champs depuis description.

    2. **Omission massive** (v1.1.1+) : ``description`` est vide ou très
       courte ET la majorité des champs principaux est vide → cas d'un LLM
       qui a renvoyé un JSON partiel sans rien dans description. On extrait
       les champs depuis le **texte source brut** (``source_text``).

    Sans effet si les champs sont déjà bien remplis : on touche uniquement
    aux champs vides, donc cette fonction ne peut jamais dégrader le résultat.
    """
    desc = (data.get("description") or "").strip()

    # Compte combien de champs principaux sont vides
    main_keys = ("commune", "cp", "frequence", "de_station", "a_station",
                 "indicatif_op", "nom_autorite", "lieu_pcc", "gps",
                 "contact_terrain", "pop_impactee", "pop_vulnerable")
    empty_count = sum(
        1 for k in main_keys if not (data.get(k) or "").strip()
    )

    # Si moins de la moitié des champs principaux est vide → cas nominal,
    # on ne fait rien (priorité au travail du LLM).
    if empty_count < len(main_keys) // 2:
        return data

    # Sinon : on choisit la source à scanner par ordre de pertinence
    if len(desc) >= 200:
        # Cas 1 : stuffing dans description
        scan_text = desc
        scenario = "stuffing description"
    elif source_text and len(source_text) >= 100:
        # Cas 2 : LLM a omis beaucoup de champs → fallback sur source brut
        scan_text = source_text
        scenario = "omission LLM, fallback sur texte source"
    elif desc:
        # Cas 3 : description courte mais présente, on essaie quand même
        scan_text = desc
        scenario = "description courte"
    else:
        # Cas 4 : rien à scanner
        return data

    warnings.append(
        f"Filet de sécurité activé ({scenario}) — {empty_count} champs "
        "principaux vides à récupérer"
    )

    rescued = _extract_fields_by_regex(scan_text, data)

    if rescued:
        warnings.append(
            f"Filet de sécurité regex : {rescued} champ(s) extrait(s)"
        )

    return data


def _extract_fields_by_regex(text: str, data: dict) -> int:
    """Extrait par regex les champs principaux depuis un texte brut.

    Modifie ``data`` en place. Ne remplit JAMAIS un champ déjà rempli.
    Retourne le nombre de champs effectivement extraits.

    v1.1.1 : extrait également de, à, message_num, description, autorité,
    fréquence avec format souple (sans MHz obligatoire après).
    """
    rescued = 0

    def set_if_empty(key: str, value: str) -> bool:
        nonlocal rescued
        if value and not (data.get(key) or "").strip():
            data[key] = value.strip()
            rescued += 1
            return True
        return False

    # Code postal : 5 chiffres consécutifs (premier match)
    m = re.search(r"\b(\d{5})\b", text)
    if m:
        set_if_empty("cp", m.group(1))

    # Fréquence : <chiffres>.<chiffres> avec ou sans " MHz" derrière
    # On préfère le pattern AVEC MHz quand il existe, sinon premier match
    m = re.search(r"\b(\d{2,4}[.,]\d{1,4})\s*M?Hz?\b", text, re.IGNORECASE)
    if not m:
        # Fallback : juste une fréquence-like (XX.XXX ou XXX.XXX)
        m = re.search(r"\b(1[0-9]{2}\.\d{2,4}|4[0-9]{2}\.\d{2,4})\b", text)
    if m:
        set_if_empty("frequence", m.group(1).replace(",", "."))

    # Coordonnées GPS : XX.XXXX[°] [N/S] X.XXXX[°] [E/W]
    m = re.search(
        r"(\d{1,2}[.,]\d{2,6})\s*[°ºo]?\s*[NS][,;\s/]+(\d{1,3}[.,]\d{2,6})\s*[°ºo]?\s*[EWO]",
        text, re.IGNORECASE,
    )
    if m:
        gps_str = f"{m.group(1)}N / {m.group(2)}E".replace(",", ".")
        set_if_empty("gps", gps_str)

    # Indicatif radio : F<chiffre><lettres>, TM/TK..., suivi optionnel /PCO etc.
    # Note : on prend le PREMIER match qui ressemble à un indicatif perso
    # (F + chiffre + 2-4 lettres), pas un indicatif spécial.
    m = re.search(r"\b(F[0-9][A-Z]{2,4})\b", text)
    if m:
        set_if_empty("indicatif_op", m.group(1))

    # Téléphone FR : 0[1-9] XX XX XX XX (impose un 0 + chiffre 1-9 pour
    # ne pas matcher les dates 2026-05-11 14:09)
    m = re.search(
        r"\b(0[1-9])[\s.\-]?(\d{2})[\s.\-]?(\d{2})[\s.\-]?(\d{2})[\s.\-]?(\d{2})\b",
        text,
    )
    if m:
        set_if_empty("contact_terrain", " ".join(m.groups()))

    # Population impactée : <nombre 4-7 chiffres> habitants, ou
    # v1.1.1 : "Population <N>" (format prompt formation)
    # On préfère le pattern avec "habitants" qui est plus précis.
    m = re.search(r"\b(\d{4,7})\s*HABITANTS?\b", text, re.IGNORECASE)
    if not m:
        m = re.search(
            r"\bPOPULATION\s+(?:IMPACT[EÉ]E\s*:?\s*)?(\d{4,7})\b",
            text, re.IGNORECASE,
        )
    if m:
        set_if_empty("pop_impactee", m.group(1))

    # Vulnérables
    # v1.1.3 : accepte aussi le pattern "Dont vulnérables : N" (sans habitants
    # ni personnes derrière, format prompt formation FNRASEC)
    m = re.search(
        r"\b(\d{3,6})\s*(?:PERSONNES?\s+|PERS\.?\s+)?VULN[EÉ]RABLES?\b",
        text, re.IGNORECASE,
    )
    if not m:
        # Pattern "Dont vulnérables : 8500" (forme prompt formation)
        m = re.search(
            r"\b(?:DONT\s+)?VULN[EÉ]RABLES?\s*:?\s*(\d{3,6})\b",
            text, re.IGNORECASE,
        )
    if m:
        set_if_empty("pop_vulnerable", m.group(1))

    # v1.1.1 : Commune — patterns plus robustes
    # Pattern 1 : "Commune sinistrée : XXX, NNNNN" (format prompt formation)
    # Pattern 2 : "à XXX (NNNNN)" ou "MAIRE DE XXX"
    # Pattern 3 : "Mairie de XXX"
    m = re.search(
        r"(?:COMMUNE\s+(?:SINISTR[EÉ]E)?\s*:?\s*|MAIRE\s+DE\s+|MAIRIE\s+DE\s+|PCO\s+)([A-ZÉÈÊÀÔÎÛÇa-zéèêàôîûç\-]{3,}(?:[\s\-][A-ZÉÈÊÀÔÎÛÇa-zéèêàôîûç]+)*)",
        text, re.IGNORECASE,
    )
    if m:
        commune = m.group(1).strip()
        commune = re.split(r"[\(\),:]", commune)[0].strip()
        if 3 <= len(commune) <= 40:
            set_if_empty("commune", commune.upper())

    # v1.1.1 : Station émettrice "DE F1GBD/PCO MEAUX" — ancré end-of-line
    # v1.1.3 : aussi pattern "Station émettrice (DE) : XXX"
    # v1.1.4 : exige au moins un slash, ou un pattern indicatif radio
    # (Fx, TMxx, Pxx) pour éviter de matcher "DE LA SITUATION" ou autres
    # tournures françaises génériques où DE est juste une préposition.
    m = re.search(
        r"(?:Station\s+(?:[ée]mettrice|emettrice)\s*\(DE\)\s*:?\s*|"
        r"(?:^|\s)DE\s*:?\s+)"
        r"([A-Z0-9][A-Z0-9/\-\.\s]{3,40}?)"
        r"(?=\s*$|\s*,|\s+A\s|\s+À\s|\s*[\r\n]|\s+-\s+)",
        text, re.IGNORECASE | re.MULTILINE,
    )
    if m:
        de = m.group(1).strip().rstrip(",")
        # v1.1.4 : valide qu'on a bien une station radio. Patterns attendus :
        # "F1GBD/PCO MEAUX", "F1GBD", "TM77ADR/PCO". Exige soit un /, soit
        # un préfixe indicatif amateur (F/TM/TK/TO/HB/etc + chiffre)
        is_callsign = bool(re.match(r"^[A-Z]{1,2}\d[A-Z]{2,4}\b", de))
        has_slash = "/" in de
        # Mots français à exclure même si match accidentel
        bad_words = {"LA", "LE", "LES", "DES", "DE", "DU", "SITUATION",
                     "COURS", "L'ÉTAT", "L'AUTORITÉ"}
        first_word = de.split()[0] if de.split() else ""
        if (is_callsign or has_slash) and first_word not in bad_words and len(de) >= 3:
            set_if_empty("de_station", de.upper())

    # v1.1.1 : Destinataire "A COD 77 PREFECTURE" — ancré strictement.
    # v1.1.3 : aussi pattern "Destinataire (À) : COD ..."
    m = re.search(
        r"(?:Destinataire\s*\(À\)\s*:?\s*|"
        r"\b(?:A|À)\s*:?\s+)"
        r"(COD\s*\d{1,3}\s+[A-Z]+(?:\s+[A-Z]+){0,2})"
        r"(?=\s*$|\s*[\r\n,]|\s+-\s+)",
        text, re.IGNORECASE | re.MULTILINE,
    )
    if m:
        set_if_empty("a_station", m.group(1).strip().upper())

    # v1.1.1 : Lieu PCC — pattern strict pour éviter de matcher "PCC ouvert"
    # v1.1.3 : ajoute aussi le pattern "PCC : Lieu : Mairie de Meaux" (avec
    # double ':' parce que c'est le format produit par le prompt formation)
    m = re.search(
        r"PCC\s*:?\s*Lieu\s*:?\s*([^\n]{5,80}?)(?=\s*GPS|\s*COORD|\s*$|\s*[\r\n])",
        text, re.IGNORECASE,
    )
    if m:
        lieu = m.group(1).strip().rstrip(",.")
        if 10 <= len(lieu) <= 80:
            set_if_empty("lieu_pcc", lieu)
    # Pattern 2 : "LIEU PCC : XXX" ou "PCC <type d'établissement>"
    if not (data.get("lieu_pcc") or "").strip():
        m = re.search(
            r"(?:LIEU\s+PCC|PCC)\s*:?\s*"
            r"((?:MAIRIE|MAIRE|SALLE|HOTEL|ECOLE|GYMNASE|STADE|CENTRE|"
            r"PR[EÉ]FECTURE|POLE)[^\n,.]{4,80})",
            text, re.IGNORECASE,
        )
        if m:
            lieu = m.group(1).strip().rstrip(",.")
            if 10 <= len(lieu) <= 80:
                set_if_empty("lieu_pcc", lieu)

    # v1.1.1 : Nom + Prénom autorité (pattern "Maire DUBOIS Marie" ou
    # "NOM Prénom" qui suit "MAIRE", "ADJOINT", etc.)
    m = re.search(
        r"\b(?:MAIRE|ADJOINT|DGS|PR[EÉ]FET|DIRECTEUR)\b[^\n]{0,30}?\b([A-ZÉÈÊÀÔÎÛÇ]{2,}\s+[A-Z][a-zéèêàôîûç]+)",
        text,
    )
    if m:
        set_if_empty("nom_autorite", m.group(1).strip())

    return rescued



def _build_extraction_prompt(source_text: str, session_vars: dict) -> str:
    """Construit le prompt d'extraction. Format JSON strict imposé.

    v1.1.0 : prompt one-shot avec exemple complet rempli pour empêcher
    le LLM de mettre tout dans `description`. Avec Ollama 0.5+ et le
    JSON Schema strict, ce prompt sert de "amorce" pour montrer le
    format attendu.
    """
    call = (session_vars.get("CALL") or session_vars.get("INDICATIF")
            or "F1GBD").strip()
    adr = (session_vars.get("ADRASEC") or "ADRASEC 77").strip()

    # Listes autorisées injectées DANS le prompt pour guider le modèle
    choices_doc = []
    for fld, opts in CHOICE_FIELDS.items():
        if fld.startswith(("type_", "unite_", "delai_", "prio_")):
            continue
        choices_doc.append(f'  "{fld}": {list(opts)},')

    # v1.1.4 : exemple SCHÉMATIQUE avec PLACEHOLDERS visibles `<XXX>`.
    # CRITIQUE — bug observé en v1.1.0–v1.1.3 : un exemple one-shot avec
    # des valeurs concrètes ("MEAUX", "DUPONT Jean", "55000") contaminait
    # la sortie des petits LLM (qwen2.5:7b en local) qui RECOPIAIENT
    # l'exemple plutôt que d'extraire le SITREP_TEXT. Cas F1GBD 11/05/2026 :
    # input "BEAUX-SUR-MARNE / DUBOIS Marie / 77105" → output "MEAUX /
    # DUPONT Jean / 77000" (= valeurs de l'exemple).
    #
    # Solution : placeholders `<COMMUNE>`, `<CP>` qui ne peuvent JAMAIS
    # être confondus avec des données réelles. Le LLM voit le schéma sans
    # voir de valeurs à recopier.
    example = '''{
  "type_operation": "<EXERCICE - EXERCICE - EXERCICE | REEL - REEL - REEL>",
  "priorite": "<ROUTINE | PRIORITAIRE | URGENT | FLASH>",
  "mode_tcq": "<VARA HF | VARA FM | VARA SAT | PACKET | ARDOP | LXMF>",
  "adrasec_concernee": "<ADRASEC 77 | 75 | 78 | 91 | 92 | 93 | 94 | 95 | AUTRE>",
  "pcs_active": "<OUI | NON | EN COURS>",
  "autorite": "<MAIRE | ADJOINT | DGS | PREFECTURE | SDIS | SAMU | GENDARMERIE | AUTRE>",
  "gravite": "<FAIBLE | MODEREE | ELEVEE | CRITIQUE>",
  "tendance": "<STABLE | EN DEGRADATION | EN AMELIORATION>",
  "acces": "<LIBRE | RESTREINT | 4x4 UNIQUEMENT | HELIPORTE | INACCESSIBLE>",
  "msg_num": "<NUMERO DU MESSAGE — extrait du SITREP_TEXT>",
  "dtg": "<DTG SITREP EXACT du SITREP_TEXT au format JJ/MM/AAAA HH:MM>",
  "de_station": "<STATION EMETTRICE EXACTE du SITREP_TEXT>",
  "a_station": "<DESTINATAIRE EXACT du SITREP_TEXT>",
  "frequence": "<FREQUENCE EXACTE du SITREP_TEXT en MHz>",
  "indicatif_op": "<INDICATIF EXACT du SITREP_TEXT>",
  "commune": "<NOM EXACT DE LA COMMUNE du SITREP_TEXT — ne pas raccourcir, ne pas remplacer par une commune connue>",
  "cp": "<CODE POSTAL EXACT du SITREP_TEXT — 5 chiffres>",
  "dtg_pcs": "<DTG ACTIVATION PCS du SITREP_TEXT, ou vide si non précisé>",
  "nom_autorite": "<NOM Prénom EXACT du SITREP_TEXT>",
  "fonction_autorite": "<FONCTION EXACTE du SITREP_TEXT>",
  "pop_impactee": "<NOMBRE EXACT du SITREP_TEXT, entier>",
  "pop_vulnerable": "<NOMBRE EXACT du SITREP_TEXT, entier>",
  "description": "<3 a 5 phrases courtes RESUMEES depuis le SITREP_TEXT, separees par \\\\n. NE PAS recopier integralement.>",
  "demandes": [
    {"type": "<TYPE>", "qte": "<NOMBRE>", "unite": "<UNITE>", "delai": "<DELAI>", "prio": "<PRIO>", "lieu": "<LIEU EXACT du SITREP_TEXT>"}
  ],
  "lieu_pcc": "<LIEU EXACT du PCC du SITREP_TEXT>",
  "gps": "<COORDONNEES EXACTES du SITREP_TEXT, ou vide>",
  "contact_terrain": "<NOM + TELEPHONE EXACTS du SITREP_TEXT>",
  "checkboxes": ["chk_XXX correspondant aux situations EFFECTIVEMENT mentionnees dans le SITREP_TEXT"],
  "sig_operateur": "<INDICATIF - HH:MM>"
}'''

    prompt = f"""Tu es un assistant d'extraction structurée pour ADRASEC / FNRASEC.
Ton UNIQUE travail est d'extraire les informations PRÉSENTES DANS LE SITREP_TEXT
ci-dessous et de les répartir dans les champs JSON appropriés.

══════════════════════════════════════════════════════════════════════
⚠️  RÈGLE ABSOLUE — INTERDICTION ABSOLUE D'INVENTER
══════════════════════════════════════════════════════════════════════
Tu DOIS extraire UNIQUEMENT les valeurs LITTÉRALEMENT présentes dans le
SITREP_TEXT fourni plus bas. Tu n'as PAS LE DROIT :
  - d'inventer une commune, un code postal, un nom de personne
  - de remplacer un nom de commune par une commune que tu connais mieux
  - d'inventer une fréquence, des coordonnées GPS, un numéro de téléphone
  - de t'inspirer du schéma de référence pour produire des valeurs

Si une information n'est PAS dans le SITREP_TEXT, mets "" (chaîne vide).
══════════════════════════════════════════════════════════════════════

═══ SITREP_TEXT — SOURCE UNIQUE DE VÉRITÉ ═══
\"\"\"
{source_text}
\"\"\"
═══ FIN SITREP_TEXT ═══

⚠️ RÈGLE DE RÉPARTITION (anti-stuffing) :
NE METS PAS TOUT LE CONTENU DANS LE CHAMP "description". Au contraire :
EXTRAIS chaque information dans son champ dédié :
- La commune va dans "commune", PAS dans description
- Le code postal va dans "cp", PAS dans description
- La fréquence va dans "frequence", PAS dans description
- Les coordonnées GPS vont dans "gps", PAS dans description
- Le contact terrain va dans "contact_terrain", PAS dans description
- Les demandes vont dans le tableau "demandes", PAS dans description

Le champ "description" est UNIQUEMENT pour 3-5 phrases de RÉSUMÉ qui
ne rentrent dans aucun autre champ (ex: relais utilisé, contraintes
météo, ETA renforts). Ne pas y mettre les valeurs déjà extraites.

AUTRES RÈGLES :
1. Réponds UNIQUEMENT en JSON valide, rien d'autre.
2. Pour chaque champ <choix> : utilise EXACTEMENT une des valeurs listées.
3. Si une information est absente du SITREP_TEXT, mets "" (chaîne vide).
4. "demandes" peut contenir 0 à 7 entrées. P1 en premier, puis P2, P3, P4.
5. "checkboxes" ne contient que les codes des cases APPLICABLES.
6. "type_operation" reste "EXERCICE - EXERCICE - EXERCICE" sauf "REEL".
7. Indicatif opérateur par défaut si absent du SITREP : {call} | ADRASEC : {adr}.

══════════════════════════════════════════════════════════════════════
SCHÉMA DE RÉFÉRENCE (placeholders <XXX> à REMPLACER par les valeurs
LITTÉRALEMENT présentes dans le SITREP_TEXT ci-dessus —
PAS DE VALEURS CONCRÈTES À RECOPIER, juste le format) :
══════════════════════════════════════════════════════════════════════

{example}

══════════════════════════════════════════════════════════════════════

VALEURS AUTORISÉES POUR LES DROPDOWNS :
{chr(10).join(choices_doc)}

Maintenant produis le JSON conforme au schéma, EN N'UTILISANT QUE LES
INFORMATIONS DU SITREP_TEXT CI-DESSUS. Aucune invention.
"""
    return prompt


def _parse_json_loose(raw: str, warnings: List[str]) -> Any:
    """Parse un JSON renvoyé par le LLM, avec extraction si entouré de texte."""
    raw = raw.strip()
    # Cas idéal : JSON pur
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # Cherche le premier { et le dernier } équilibrés
    start = raw.find("{")
    end = raw.rfind("}")
    if start >= 0 and end > start:
        candidate = raw[start:end + 1]
        try:
            warnings.append(
                "JSON LLM entouré de texte — extraction du bloc principal"
            )
            return json.loads(candidate)
        except json.JSONDecodeError as e:
            warnings.append(f"JSON LLM mal formé : {e}")

    return {}


def _unpack_demandes(data: dict, warnings: List[str]) -> dict:
    """Transforme la liste 'demandes' en lignes type_1, qte_1, ..., type_7, lieu_7."""
    demandes = data.pop("demandes", None)
    if not isinstance(demandes, list):
        return data
    for i, d in enumerate(demandes[:7], start=1):
        if not isinstance(d, dict):
            continue
        data[f"type_{i}"] = (d.get("type") or "---")
        data[f"qte_{i}"] = str(d.get("qte") or "")
        data[f"unite_{i}"] = (d.get("unite") or "---")
        data[f"delai_{i}"] = (d.get("delai") or "---")
        data[f"prio_{i}"] = (d.get("prio") or "---")
        data[f"lieu_{i}"] = (d.get("lieu") or "")
    if len(demandes) > 7:
        warnings.append(
            f"{len(demandes)} demandes générées mais le formulaire en accepte "
            f"7 — les surnuméraires sont ignorées"
        )

    # Cases à cocher : on les déplace vers une clé interne pour le moment
    cb = data.pop("checkboxes", None)
    if isinstance(cb, list):
        data["_checkboxes"] = [str(x).strip() for x in cb if str(x).strip()]

    return data


# ---------------------------------------------------------------------------
# Extraction heuristique (fallback sans LLM)
# ---------------------------------------------------------------------------

def _extract_heuristic(source_text: str, session_vars: dict) -> dict:
    """Extraction minimaliste utilisée quand le LLM est indisponible.

    v1.1.3 : enrichie pour appeler aussi ``_extract_fields_by_regex``
    qui récupère 11 champs (commune, CP, fréquence, GPS, indicatif, etc.)
    depuis le texte source. Sans cet enrichissement, le PDF en mode
    "Ollama HS" était quasi-vide. Cas observé : qwen2.5:14b sur hardware
    modeste avec timeout 120s qui échouait systématiquement.
    """
    data: dict[str, Any] = {}

    # v1.1.3 : extraction regex full depuis le texte source brut.
    # Ce passage récupère commune, CP, fréquence, GPS, indicatif, contact,
    # populations, lieu PCC, station DE/À, nom autorité — 11 champs.
    _extract_fields_by_regex(source_text, data)

    # Cases à cocher inférées par mots-clés
    data["_checkboxes"] = _infer_checkboxes_from_text(source_text)

    # Gravité par défaut : ELEVEE si > 5 cases cochées, sinon MODEREE
    n_checks = len(data["_checkboxes"])
    if n_checks >= 7:
        data["gravite"] = "CRITIQUE"
    elif n_checks >= 4:
        data["gravite"] = "ELEVEE"
    elif n_checks >= 1:
        data["gravite"] = "MODEREE"
    else:
        data["gravite"] = "FAIBLE"

    # v1.1.3 : valeurs raisonnables par défaut pour les dropdowns SITREP
    # qui sont quasi-toujours les mêmes en exercice ADRASEC. On les pose
    # seulement si l'extraction regex ne les a pas déjà déduites.
    if n_checks >= 4:
        data.setdefault("tendance", "EN DEGRADATION")
        data.setdefault("priorite", "URGENT" if n_checks < 7 else "FLASH")
    if "mode_tcq" not in data:
        # Détection simple dans le texte source
        text_upper = source_text.upper()
        if "VARA FM" in text_upper:
            data["mode_tcq"] = "VARA FM"
        elif "VARA HF" in text_upper:
            data["mode_tcq"] = "VARA HF"
        elif "VARA SAT" in text_upper:
            data["mode_tcq"] = "VARA SAT"
        elif "PACKET" in text_upper:
            data["mode_tcq"] = "PACKET"

    if "autorite" not in data:
        text_upper = source_text.upper()
        for keyword in ("MAIRE", "ADJOINT", "DGS", "PREFECTURE",
                        "SDIS", "SAMU", "GENDARMERIE"):
            if keyword in text_upper:
                data["autorite"] = keyword
                break

    if "pcs_active" not in data:
        text_upper = source_text.upper()
        if re.search(r"PCS\s*ACTIV[EÉ]\s*:?\s*OUI", text_upper):
            data["pcs_active"] = "OUI"
        elif re.search(r"PCS\s*OUVERT|PCC\s*OUVERT", text_upper):
            data["pcs_active"] = "OUI"

    if "acces" not in data:
        text_upper = source_text.upper()
        if "RESTREINT" in text_upper or "ENDOMMAG" in text_upper:
            data["acces"] = "RESTREINT"
        elif "INACCESSIBLE" in text_upper or "IMPRATICABLE" in text_upper:
            data["acces"] = "INACCESSIBLE"

    # v1.1.3 : description = 5 premières lignes non vides du texte source,
    # MAIS uniquement si le source est en multi-ligne (sinon ça pollue
    # avec le SITREP brut). On ne met description que si lignes ≥ 3.
    lines = [ln.strip() for ln in source_text.splitlines() if ln.strip()]
    if len(lines) >= 3:
        data["description"] = "\n".join(lines[:5])

    return data


def _infer_checkboxes_from_text(text: str) -> List[str]:
    """Retourne la liste des cases à cocher déduites du texte par mots-clés."""
    text_low = text.lower()
    hits = []
    for chk_name, keywords in CHECKBOX_KEYWORDS.items():
        for kw in keywords:
            if kw in text_low:
                hits.append(chk_name)
                break
    return hits


# ---------------------------------------------------------------------------
# Application des valeurs par défaut depuis les variables de session
# ---------------------------------------------------------------------------

def _apply_session_defaults(data: dict, session_vars: dict) -> dict:
    """Complète les champs vides avec les valeurs de session (CALL, ADRASEC...).

    Ne remplace JAMAIS une valeur déjà présente — seules les chaînes vides
    et les "---" sont susceptibles d'être réécrits.
    """
    # Date / heure courante si vide
    now = datetime.now()
    if not (data.get("dtg") or "").strip():
        data["dtg"] = now.strftime("%d/%m/%Y %H:%M")

    # Indicatif opérateur
    if not (data.get("indicatif_op") or "").strip():
        call = (session_vars.get("CALL") or session_vars.get("INDICATIF")
                or "").strip()
        if call:
            data["indicatif_op"] = call

    # ADRASEC concernée
    if not (data.get("adrasec_concernee") or "").strip():
        adr = (session_vars.get("ADRASEC") or "").strip()
        if adr:
            data["adrasec_concernee"] = adr

    # Type d'opération : EXERCICE par défaut sauf SITREP_REEL explicite
    if not (data.get("type_operation") or "").strip():
        is_reel = str(session_vars.get("SITREP_REEL", "")).strip().lower() in (
            "1", "true", "oui", "yes"
        )
        data["type_operation"] = (
            "REEL - REEL - REEL" if is_reel else "EXERCICE - EXERCICE - EXERCICE"
        )

    # Signature opérateur : "INDICATIF - HH:MM"
    if not (data.get("sig_operateur") or "").strip():
        call_for_sig = (data.get("indicatif_op") or "").strip()
        if call_for_sig:
            data["sig_operateur"] = f"{call_for_sig} - {now.strftime('%H:%M')}"

    return data


# ---------------------------------------------------------------------------
# Validation et clamping
# ---------------------------------------------------------------------------

def _validate_and_clamp(data: dict, warnings: List[str]) -> dict:
    """Garde uniquement les champs connus et valide les listes déroulantes."""
    valid_fields = set(TEXT_FIELDS) | set(CHOICE_FIELDS.keys()) | {"_checkboxes"}
    cleaned: dict[str, Any] = {}

    for key, val in data.items():
        if key not in valid_fields:
            warnings.append(f"Champ ignoré (inconnu du schéma) : « {key} »")
            continue

        if key == "_checkboxes":
            cleaned[key] = val
            continue

        if val is None:
            continue

        sval = str(val).strip()

        # Champ choix : doit être dans la liste autorisée
        if key in CHOICE_FIELDS:
            opts = CHOICE_FIELDS[key]
            # Tolérance casse + accents : on essaie un match insensible
            sval_norm = _normalize_for_match(sval)
            matched = None
            for opt in opts:
                if _normalize_for_match(opt) == sval_norm:
                    matched = opt
                    break
            if matched is None and sval and sval != "---":
                # Pour les champs "type_X" qui sont vraiment optionnels,
                # silencieux. Pour les champs principaux, on warn.
                if not key.startswith(("type_", "unite_", "delai_", "prio_")):
                    warnings.append(
                        f"Valeur hors-liste pour « {key} » : "
                        f"« {sval} » ignorée (valeurs autorisées : "
                        f"{', '.join(opts)})"
                    )
                continue
            if matched is not None:
                cleaned[key] = matched
            continue

        # Champ texte : on tronque à 500 caractères pour éviter d'exploser
        # un champ AcroForm de description (généralement 2000+ ok mais on
        # reste conservateur). Sauf 'description' qui peut être plus long.
        max_len = 4000 if key == "description" else 500
        if len(sval) > max_len:
            warnings.append(
                f"Champ « {key} » tronqué de {len(sval)} à {max_len} caractères"
            )
            sval = sval[:max_len]
        cleaned[key] = sval

    # v1.1.5 : nettoyages anti-pollution observés en pratique.

    # 1. indicatif_op : ne garder que le premier token "indicatif radio"
    #    (F+chiffre+lettres ou TM/TK+chiffres+lettres). Le LLM a tendance
    #    à inclure "F1GBD | ADRASEC : ADRASEC 77" — on coupe au premier
    #    indicatif valide trouvé.
    if "indicatif_op" in cleaned:
        v = cleaned["indicatif_op"]
        m = re.search(r"\b([A-Z]{1,2}\d[A-Z]{2,4})\b", v.upper())
        if m and m.group(1) != v.strip():
            warnings.append(
                f"indicatif_op nettoyé : « {v} » → « {m.group(1)} »"
            )
            cleaned["indicatif_op"] = m.group(1)

    # 2. frequence : ne garder que les chiffres+point (sans " MHz" ni "Hz")
    #    Le formulaire affiche "FREQUENCE (MHz)" comme label, l'unité est
    #    déjà indiquée — on évite la redondance.
    if "frequence" in cleaned:
        v = cleaned["frequence"]
        m = re.search(r"(\d{2,4}[.,]\d{1,4})", v)
        if m and m.group(1) != v.strip():
            cleaned["frequence"] = m.group(1).replace(",", ".")

    # 3. nom_autorite : supprimer un préfixe "MAIRE ", "ADJOINT ", etc. qui
    #    se serait glissé dans le nom (le rôle a déjà son propre champ
    #    `autorite` dropdown).
    if "nom_autorite" in cleaned:
        v = cleaned["nom_autorite"]
        # Patterns : "MAIRE DUBOIS Marie", "ADJOINT DUPONT Jean", etc.
        m = re.match(
            r"^\s*(?:MAIRE|ADJOINT|DGS|PREFET|PR[EÉ]FECTURE|SDIS|SAMU|"
            r"GENDARMERIE|DIRECTEUR|RESPONSABLE|M\.|MME)\s+(.+)$",
            v, re.IGNORECASE,
        )
        if m:
            cleaned_nom = m.group(1).strip()
            if cleaned_nom and cleaned_nom != v:
                cleaned["nom_autorite"] = cleaned_nom

    # 4. sig_operateur : si on voit "F1GBD | ADRASEC : ADRASEC 77 - HH:MM",
    #    nettoyer en "F1GBD - HH:MM". Le LLM (rarement) injecte la chaîne
    #    complète si on lui a donné un placeholder pollué.
    if "sig_operateur" in cleaned:
        v = cleaned["sig_operateur"]
        # Pattern : "<indicatif> [| ADRASEC : ADRASEC XX]? - HH:MM"
        m = re.match(
            r"^\s*([A-Z]{1,2}\d[A-Z]{2,4})"
            r"(?:\s*\|\s*ADRASEC\s*:\s*ADRASEC\s+\d+)?"
            r"\s*[-–]\s*(\d{1,2}[:h]\d{2})\s*$",
            v, re.IGNORECASE,
        )
        if m:
            new_sig = f"{m.group(1).upper()} - {m.group(2)}"
            if new_sig != v.strip():
                cleaned["sig_operateur"] = new_sig

    return cleaned


_ACCENTS = str.maketrans(
    "àáâãäåçèéêëìíîïñòóôõöùúûüýÿÀÁÂÃÄÅÇÈÉÊËÌÍÎÏÑÒÓÔÕÖÙÚÛÜÝ",
    "aaaaaaceeeeiiiinooooouuuuyyAAAAAACEEEEIIIINOOOOOUUUUY",
)


def _normalize_for_match(s: str) -> str:
    """Normalise pour comparaison : casse, accents, espaces."""
    return s.translate(_ACCENTS).upper().strip()


# ---------------------------------------------------------------------------
# Pose des cases à cocher (gestion AS / V dynamique selon le widget)
# ---------------------------------------------------------------------------

def _set_checkboxes(writer, checked_names: List[str],
                    warnings: List[str], NameObject):
    """Pose /V et /AS sur les annotations widget des checkboxes.

    Chaque case AcroForm peut avoir un export name différent (généralement
    /Yes mais pas toujours). On l'extrait du dictionnaire /AP/N de chaque
    widget pour rester compatible avec tous les générateurs de PDF.
    """
    wanted = set(checked_names)
    found = set()

    for page in writer.pages:
        annots = page.get("/Annots")
        if annots is None:
            continue
        for annot in annots:
            try:
                obj = annot.get_object()
            except Exception:
                continue
            if obj.get("/Subtype") != "/Widget":
                continue
            name = obj.get("/T")
            if name is None:
                continue
            name = str(name)
            if name not in wanted:
                continue

            # Trouver l'état "on" exact (clé /AP/N différente de /Off)
            on_state = "/Yes"
            try:
                ap = obj.get("/AP")
                if ap is not None:
                    n_dict = ap.get("/N")
                    if n_dict is not None:
                        for k in n_dict.keys():
                            if str(k) != "/Off":
                                on_state = str(k)
                                break
            except Exception:
                pass

            try:
                obj[NameObject("/V")] = NameObject(on_state)
                obj[NameObject("/AS")] = NameObject(on_state)
                found.add(name)
            except Exception as e:
                warnings.append(f"Case « {name} » non cochée : {e}")

    missing = wanted - found
    if missing:
        warnings.append(
            f"Cases demandées mais widget introuvable : {', '.join(sorted(missing))}"
        )


# ---------------------------------------------------------------------------
# Construction du chemin de sortie
# ---------------------------------------------------------------------------

_FNAME_BAD_RE = re.compile(r"[^A-Za-z0-9_-]+")


def _build_output_path(template_path: Path, data: dict) -> Path:
    """Construit un chemin SITREP_<commune>_<YYYYMMDD-HHMM>.pdf à côté du CWD."""
    commune = _FNAME_BAD_RE.sub(
        "_", (data.get("commune") or "").strip().upper()
    ).strip("_") or "SITE"
    now = datetime.now().strftime("%Y%m%d-%H%M")
    fname = f"SITREP_{commune}_{now}.pdf"
    # On écrit dans le CWD pour que l'opérateur le retrouve facilement,
    # pas à côté du template (qui peut être en lecture seule dans certaines
    # installations).
    return Path.cwd() / fname


# ---------------------------------------------------------------------------
# Récap Markdown
# ---------------------------------------------------------------------------

def _build_recap_markdown(template_path: Path,
                          output_path: Path,
                          data: dict,
                          checked: List[str],
                          source_origin: str,
                          llm_used: bool,
                          llm_error: Optional[str]) -> str:
    """Génère un récapitulatif Markdown pour affichage dans le chat IAbrain."""
    lines: List[str] = []
    lines.append("## ✅ SITREP ADRASEC généré")
    lines.append("")
    lines.append(f"📄 **Template** : `{template_path}`")
    lines.append(f"📤 **PDF rempli** : `{output_path}`")
    if source_origin:
        lines.append(f"📥 **Source du texte** : {source_origin}")
    if llm_used:
        lines.append("🧠 **Extraction** : via Ollama (LLM)")
    elif llm_error:
        lines.append(f"⚙️ **Extraction** : heuristique (LLM HS — {llm_error})")
    else:
        lines.append("⚙️ **Extraction** : heuristique (pas de texte source)")
    lines.append("")

    # Bloc en-tête
    lines.append("### En-tête")
    lines.append("")
    lines.append("| Champ | Valeur |")
    lines.append("|---|---|")
    header_fields = (
        ("type_operation", "Type"),
        ("priorite", "Priorité"),
        ("dtg", "DTG"),
        ("de_station", "DE"),
        ("a_station", "À"),
        ("mode_tcq", "Mode TCQ"),
        ("frequence", "Fréquence"),
        ("indicatif_op", "Indicatif"),
        ("adrasec_concernee", "ADRASEC"),
    )
    for key, label in header_fields:
        v = data.get(key) or "—"
        lines.append(f"| {label} | {v} |")
    lines.append("")

    # Bloc localisation
    lines.append("### Localisation")
    lines.append("")
    lines.append("| Champ | Valeur |")
    lines.append("|---|---|")
    loc_fields = (
        ("commune", "Commune"),
        ("cp", "CP"),
        ("pcs_active", "PCS"),
        ("autorite", "Autorité"),
        ("nom_autorite", "Nom"),
        ("fonction_autorite", "Fonction"),
    )
    for key, label in loc_fields:
        v = data.get(key) or "—"
        lines.append(f"| {label} | {v} |")
    lines.append("")

    # Évaluation
    lines.append("### Évaluation")
    lines.append("")
    lines.append("| Champ | Valeur |")
    lines.append("|---|---|")
    eval_fields = (
        ("gravite", "Gravité"),
        ("tendance", "Tendance"),
        ("pop_impactee", "Pop. impactée"),
        ("pop_vulnerable", "Dont vulnérables"),
    )
    for key, label in eval_fields:
        v = data.get(key) or "—"
        lines.append(f"| {label} | {v} |")
    lines.append("")

    # Cases cochées
    if checked:
        lines.append("### Situation cochée")
        lines.append("")
        checkbox_labels = {
            "chk_elec": "Coupure électrique totale",
            "chk_gsm": "GSM / Internet HS",
            "chk_eau": "Coupure eau potable",
            "chk_carb": "Pénurie carburant",
            "chk_transp": "Transports publics arrêtés",
            "chk_clim": "Climatisation HS (hôpital / EHPAD)",
            "chk_feu": "Feux en cours",
            "chk_evac": "Évacuations sanitaires",
            "chk_victimes": "Victimes / décès",
            "chk_routes": "Routes bloquées",
            "chk_pde": "Points distribution eau actifs",
            "chk_pcc": "PCC ouvert en mairie",
            "vld_autorite": "Message validé par autorité",
            "vld_tcq": "Envoyé via TCQ avec AR",
            "vld_copie": "Copie archivée main courante",
        }
        for c in checked:
            lines.append(f"- ☑ {checkbox_labels.get(c, c)}")
        lines.append("")

    # Demandes de moyens
    demandes_rows = []
    for i in range(1, 8):
        t = (data.get(f"type_{i}") or "").strip()
        if not t or t == "---":
            continue
        demandes_rows.append((
            t,
            data.get(f"qte_{i}", ""),
            data.get(f"unite_{i}", "") if data.get(f"unite_{i}") != "---" else "",
            data.get(f"delai_{i}", "") if data.get(f"delai_{i}") != "---" else "",
            data.get(f"prio_{i}", "") if data.get(f"prio_{i}") != "---" else "",
            data.get(f"lieu_{i}", ""),
        ))
    if demandes_rows:
        lines.append("### Demande de moyens")
        lines.append("")
        lines.append("| Type | Qté | Unité | Délai | Prio | Lieu |")
        lines.append("|---|---|---|---|---|---|")
        for row in demandes_rows:
            lines.append("| " + " | ".join(str(c) or "—" for c in row) + " |")
        lines.append("")

    # Description
    desc = (data.get("description") or "").strip()
    if desc:
        lines.append("### Description libre")
        lines.append("")
        for ln in desc.splitlines():
            ln = ln.strip()
            if ln:
                lines.append(f"> {ln}")
        lines.append("")

    # PCC
    if any(data.get(k) for k in ("lieu_pcc", "gps", "contact_terrain", "acces")):
        lines.append("### PCC / Contacts")
        lines.append("")
        lines.append("| Champ | Valeur |")
        lines.append("|---|---|")
        pcc_fields = (
            ("lieu_pcc", "Lieu PCC"),
            ("gps", "Coord. GPS"),
            ("acces", "Accès"),
            ("contact_terrain", "Contact terrain"),
        )
        for key, label in pcc_fields:
            v = data.get(key) or "—"
            lines.append(f"| {label} | {v} |")
        lines.append("")

    # Tip de fin
    lines.append("---")
    lines.append("")
    lines.append(
        "💡 **Étapes suivantes** : ouvrez le PDF dans Acrobat Reader pour "
        "vérification, signez la zone *AUTORITE DEMANDEUSE*, puis transmettez "
        "via TCQ → VARA FM/HF/SAT → COD préfecture."
    )
    return "\n".join(lines)
