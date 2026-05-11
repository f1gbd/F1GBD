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


__version__ = "1.0.0"

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
        try:
            data = _extract_via_llm(source_text, session_vars, warnings)
            llm_used = True
        except _LLMUnavailable as e:
            llm_error = str(e)
            warnings.append(f"Ollama indisponible — extraction LLM ignorée : {e}")
            data = _extract_heuristic(source_text, session_vars)
        except Exception as e:
            llm_error = str(e)
            warnings.append(f"Échec extraction LLM : {e} — bascule heuristique")
            data = _extract_heuristic(source_text, session_vars)
    else:
        data = {}

    # --- Étape 5 : compléter / normaliser les valeurs -----------------------
    data = _apply_session_defaults(data, session_vars)
    data = _validate_and_clamp(data, warnings)

    # Champs cochés (liste des noms de cases à activer)
    checked = list(data.pop("_checkboxes", []) or [])
    if source_text and not checked:
        # Filet de sécurité : si le LLM a oublié les cases mais qu'on a un
        # texte source, on infère par mots-clés.
        checked = _infer_checkboxes_from_text(source_text)
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

    # Écrire les valeurs des champs texte + dropdown
    str_values = {k: str(v) for k, v in data.items()
                  if v is not None and v != "" and not k.startswith("_")}
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
    output_path = _build_output_path(template_path, data)
    try:
        with open(output_path, "wb") as f:
            writer.write(f)
    except Exception as e:
        return (
            f"❌ Échec écriture PDF rempli :\n`{output_path}`\n\n{e}",
            warnings + [f"Écriture PDF: {e}"],
        )

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
    """Retourne (texte, origine_lisible). Origine vide si rien."""
    # 1. Variable de session SITREP_TEXT (prioritaire car explicite)
    sv_text = (session_vars.get("SITREP_TEXT") or "").strip()
    if sv_text:
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

    Lève _LLMUnavailable si pas de serveur ou pas de réponse exploitable.
    """
    try:
        import requests
    except ImportError as e:
        raise _LLMUnavailable(f"requests non installé : {e}") from e

    cfg = _load_iabrain_config()
    base_url = (cfg.get("server_url") or "http://localhost:11434").rstrip("/")
    model = cfg.get("model_simple") or cfg.get("model") or "qwen2.5:7b"

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

    try:
        resp = requests.post(
            f"{base_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "format": "json",  # Ollama force la sortie JSON
                "options": {
                    "temperature": 0.1,  # déterministe pour l'extraction
                    "num_ctx": 8192,
                },
            },
            timeout=120.0,
        )
    except requests.RequestException as e:
        raise _LLMUnavailable(f"Erreur réseau Ollama : {e}") from e

    if resp.status_code != 200:
        raise _LLMUnavailable(
            f"Ollama HTTP {resp.status_code} : {resp.text[:200]}"
        )

    try:
        body = resp.json()
        raw_text = body.get("response", "").strip()
    except Exception as e:
        raise _LLMUnavailable(f"Réponse Ollama illisible : {e}") from e

    if not raw_text:
        raise _LLMUnavailable("Ollama a renvoyé une réponse vide")

    # Parser le JSON (avec garde-fou : extraire un bloc JSON si le modèle a
    # ajouté des commentaires)
    data = _parse_json_loose(raw_text, warnings)
    if not isinstance(data, dict):
        raise _LLMUnavailable(
            f"JSON renvoyé non-dictionnaire : {type(data).__name__}"
        )

    # Convertir le tableau de "demandes" en lignes type_X/qte_X/unite_X/...
    data = _unpack_demandes(data, warnings)
    return data


def _build_extraction_prompt(source_text: str, session_vars: dict) -> str:
    """Construit le prompt d'extraction. Format JSON strict imposé."""
    call = (session_vars.get("CALL") or session_vars.get("INDICATIF")
            or "F1GBD").strip()
    adr = (session_vars.get("ADRASEC") or "ADRASEC 77").strip()

    # Listes autorisées injectées DANS le prompt pour guider le modèle
    choices_doc = []
    for fld, opts in CHOICE_FIELDS.items():
        if fld.startswith(("type_", "unite_", "delai_", "prio_")):
            continue  # injecté plus bas une seule fois pour les 7 lignes
        choices_doc.append(f'  "{fld}": {list(opts)},')

    schema = """{
  "type_operation": "EXERCICE - EXERCICE - EXERCICE",
  "priorite": "<ROUTINE|PRIORITAIRE|URGENT|FLASH>",
  "mode_tcq": "<VARA HF|VARA FM|VARA SAT|PACKET|ARDOP|LXMF>",
  "adrasec_concernee": "<ADRASEC 77|75|78|91|92|93|94|95|AUTRE>",
  "pcs_active": "<OUI|NON|EN COURS>",
  "autorite": "<MAIRE|ADJOINT|DGS|PREFECTURE|SDIS|SAMU|GENDARMERIE|AUTRE>",
  "gravite": "<FAIBLE|MODEREE|ELEVEE|CRITIQUE>",
  "tendance": "<STABLE|EN DEGRADATION|EN AMELIORATION>",
  "acces": "<LIBRE|RESTREINT|4x4 UNIQUEMENT|HELIPORTE|INACCESSIBLE>",
  "msg_num": "<numéro court ex: 001>",
  "dtg": "<JJ/MM/AAAA HH:MM>",
  "de_station": "<station émettrice ex: F1GBD/PCO MELUN>",
  "a_station": "<destinataire ex: COD 77 PREFECTURE>",
  "frequence": "<MHz ex: 144.575>",
  "indicatif_op": "<indicatif radio ex: F1GBD>",
  "commune": "<nom de commune>",
  "cp": "<code postal>",
  "dtg_pcs": "<JJ/MM/AAAA HH:MM si PCS activé, sinon vide>",
  "nom_autorite": "<NOM Prénom>",
  "fonction_autorite": "<intitulé exact>",
  "pop_impactee": "<entier ex: 180000>",
  "pop_vulnerable": "<entier ex: 27000>",
  "description": "<3 à 8 phrases courtes, une par ligne (séparées par \\n)>",
  "demandes": [
    {
      "type": "<--- ou EAU POTABLE|VIVRES|CARBURANT|GROUPE ELECTROGENE|MEDICAL|EVACUATION|HEBERGEMENT|TRANSMISSIONS|PERSONNEL|AUTRE>",
      "qte": "<nombre>",
      "unite": "<--- ou L|M3|KG|UNITE|PALETTE|PERS.|LIT>",
      "delai": "<--- ou IMMEDIAT|< 1H|< 3H|< 6H|< 24H|J+1>",
      "prio": "<--- ou P1|P2|P3|P4>",
      "lieu": "<lieu de livraison>"
    }
  ],
  "lieu_pcc": "<lieu du PCC>",
  "gps": "<coord GPS facultatif>",
  "contact_terrain": "<NOM / téléphone>",
  "checkboxes": [
    "chk_elec", "chk_gsm", "chk_eau", "chk_carb", "chk_transp", "chk_clim",
    "chk_feu", "chk_evac", "chk_victimes", "chk_routes", "chk_pde", "chk_pcc"
  ],
  "sig_operateur": "<indicatif + heure TX ex: F1GBD - 14:00>"
}"""

    prompt = f"""Tu es un assistant d'extraction structurée pour ADRASEC / FNRASEC.
Tu lis un scénario d'exercice ou un brouillon d'opérateur radio et tu remplis
un formulaire SITREP au format JSON STRICT.

RÈGLES IMPÉRATIVES :
1. Réponds UNIQUEMENT en JSON valide, rien d'autre (pas de texte hors JSON).
2. Pour chaque champ "<choix>" : utilise EXACTEMENT une des valeurs listées
   entre < et >. Toute valeur hors liste sera rejetée.
3. Si une information est absente du texte source, mets "" (chaîne vide)
   pour les textes et "---" pour les listes déroulantes des demandes.
4. "demandes" peut contenir 0 à 7 entrées. Mets les besoins les plus urgents
   en premier (P1 avant P2 avant P3 avant P4).
5. "checkboxes" ne contient que les codes des cases EFFECTIVEMENT applicables
   (coupures réellement constatées dans le texte). Ne coche rien par défaut.
6. Pour les exercices ADRASEC, "type_operation" doit rester
   "EXERCICE - EXERCICE - EXERCICE" sauf mention explicite "REEL".
7. Indicatif opérateur par défaut : {call} | ADRASEC : {adr}.
8. La "description" doit faire MAXIMUM 8 lignes courtes, une par ligne,
   séparées par \\n. Phrases sans pronom personnel, style SITREP militaire.

SCHÉMA JSON ATTENDU :
{schema}

VALEURS AUTORISÉES SUPPLÉMENTAIRES (rappel) :
{chr(10).join(choices_doc)}

TEXTE SOURCE À ANALYSER :
\"\"\"
{source_text}
\"\"\"

Réponds maintenant en JSON valide UNIQUEMENT.
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
    """Extraction minimaliste : juste l'en-tête + cases à cocher détectées."""
    data: dict[str, Any] = {}

    # Commune et code postal (regex simple — premier code postal trouvé)
    m_cp = re.search(r"\b(\d{5})\b", source_text)
    if m_cp:
        data["cp"] = m_cp.group(1)

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

    # Description : on prend les 5 premières lignes non vides du texte source
    lines = [ln.strip() for ln in source_text.splitlines() if ln.strip()]
    if lines:
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
