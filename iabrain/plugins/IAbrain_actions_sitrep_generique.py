# -*- coding: utf-8 -*-
"""IAbrain_actions_sitrep_generique.py — Plugin SITREP générique ADRASEC.

Plugin de remplissage du formulaire SITREP_ADRASEC_GENERIQUE.pdf
(AcroForm v1.0 par F1GBD, mai 2026). Ce SITREP est conçu pour le
réseau radio palliatif VHF/UHF / VARA FM via TCQ.

═══════════════════════════════════════════════════════════════════════════
ACTIONS EXPOSÉES (v1.1.0)
═══════════════════════════════════════════════════════════════════════════

  sitrep_generique_meteo
    Génère un SITREP générique pré-rempli avec un BRIEFING MÉTÉO à partir
    des variables {METAR_RAW} et {TAF_RAW} stockées par les plugins METAR
    et TAF. Trois styles de texte disponibles via {SITREP_GEN_STYLE} :

      - "meteofrance" (DÉFAUT v1.2.2) : verbeux déterministe, style
                       bulletin grand public, 100% fiable factuellement
      - "radiogramme" : court, style ADRASEC, transmission VARA FM
      - "llm"         : reformulation Ollama (NON RECOMMANDÉ en réel :
                        risque d'hallucinations sur unités/heures)

  sitrep_generique
    Génère un SITREP générique vide ou pré-rempli depuis {SITREP_GEN_TEXT}.

═══════════════════════════════════════════════════════════════════════════
VARIABLES DE SESSION LUES
═══════════════════════════════════════════════════════════════════════════

Mode METEO :
    METAR_RAW         METAR brut (posé par plugin metar)
    METAR_STATION     OACI METAR
    TAF_RAW           TAF brut (posé par plugin taf)
    TAF_STATION       OACI TAF
    SITREP_GEN_STYLE  "radiogramme" | "meteofrance" | "llm" (défaut radiogramme)

Communes :
    INDICATIF         indicatif opérateur ADRASEC (DE)
    INDICATIF_DEST    indicatif destinataire (A)
    FREQ_TX           fréquence émission MHz
    FREQ_RX           fréquence réception MHz (souvent = FREQ_TX)
    POSITION          QTH locator ou ville
    SITREP_GEN_TEXT   texte libre pour le mode générique
    SITREP_GEN_OBJET  objet du message (sinon auto)
    SITREP_GEN_TEMPLATE  chemin (fichier ou dossier) du template PDF

═══════════════════════════════════════════════════════════════════════════
VARIABLES DE SESSION ÉCRITES
═══════════════════════════════════════════════════════════════════════════

    SITREP_GEN_PDF    chemin du PDF généré
    SITREP_GEN_RAW    texte du message tel qu'écrit dans le PDF

═══════════════════════════════════════════════════════════════════════════
F1GBD - ADRASEC 77 / FNRASEC — v1.1.0 mai 2026
"""

from __future__ import annotations

import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, List, Optional, Sequence, Tuple

__version__ = "1.2.2"

# ---------------------------------------------------------------------------
# 1. Identifiants des actions exposées
# ---------------------------------------------------------------------------

ACTION_METEO = "sitrep_generique_meteo"
ACTION_GENERIQUE = "sitrep_generique"
_ACTIONS = {ACTION_METEO, ACTION_GENERIQUE}

# Nom du PDF source attendu (vierge, avec AcroForm)
_TEMPLATE_PDF_NAME = "SITREP_ADRASEC_GENERIQUE.pdf"

# ---------------------------------------------------------------------------
# 2. Schéma du formulaire AcroForm (extrait par inspection pypdf)
# ---------------------------------------------------------------------------
#
# 31 champs identifiés dans SITREP_ADRASEC_GENERIQUE.pdf :
#   - 16 champs texte libres (/Tx)
#   - 12 listes déroulantes (/Ch) avec valeurs autorisées
#   - 3 cases à cocher (/Btn)
# ---------------------------------------------------------------------------

# Champs texte libres
_TEXT_FIELDS = (
    "num_message", "date_msg", "heure_utc",
    "de_indicatif", "position_emet",
    "a_indicatif", "via_relais",
    "freq_tx", "freq_rx",
    "tcq_version",
    "objet",
    "texte_message",
    "nb_mots", "nb_groupes",
    "redige_par", "heure_tx", "recu_par", "heure_rx",
    "observations",
)

# Listes déroulantes : valeurs autorisées exactes (PDF case-sensitive)
_CHOICE_FIELDS: dict[str, Tuple[str, ...]] = {
    "station_emet":  ("PCO", "PC-ADRASEC", "Mobile", "Portable", "Relais", "Autre"),
    "station_dest":  ("COD", "PCO", "PC-ADRASEC", "Prefecture", "Relais", "Autre"),
    "mode_radio":    ("VARA FM", "VARA HF", "PACKET 1k2", "PACKET 9k6",
                      "Phonie FM", "Phonie SSB", "Reticulum", "LXMF"),
    "rsv_r":         ("5", "4", "3", "2", "1"),
    "rsv_s":         ("9", "8", "7", "6", "5", "4", "3", "2", "1"),
    "rsv_v":         ("Stable", "QSB leger", "QSB fort", "QRM", "QRN"),
    "priorite":      ("FLASH", "URGENT", "PRIORITAIRE", "ROUTINE"),
    "type_msg":      ("SITUATION", "DEMANDE MOYENS", "COMPTE-RENDU", "ALERTE",
                      "LEVEE DE DOUTE", "FIN DE MISSION", "LOGISTIQUE", "AUTRE"),
    "phase":         ("VEILLE", "ALERTE", "CONFINEMENT", "EVACUATION",
                      "FIN ALERTE", "RETEX"),
}

# Cases à cocher
_CHECKBOX_FIELDS = (
    "mode_exercice",   # case EXERCICE - EXERCICE - EXERCICE
    "mode_reel",       # case REEL - REEL - REEL
    "accuse_reception",  # demande d'accusé de réception
)


# ---------------------------------------------------------------------------
# 3. Helpers session
# ---------------------------------------------------------------------------

def _get_session_vars(options: Any) -> dict:
    if not options or not isinstance(options, dict):
        return {}
    sv = options.get("session_vars")
    return sv if isinstance(sv, dict) else {}


def _get_var(session_vars: dict, name: str, default: str = "") -> str:
    v = session_vars.get(name)
    if v is None:
        return default
    s = str(v).strip()
    return s if s else default


def _set_session_var(options: Any, name: str, value: str) -> bool:
    if not options or not isinstance(options, dict):
        return False
    mgr = options.get("session_vars_manager")
    if mgr is None:
        return False
    try:
        ok = mgr.set(name, value)
        if ok:
            mgr.save()
        return bool(ok)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# 4. Recherche du PDF template
# ---------------------------------------------------------------------------

def _trouver_template(session_vars: dict, warnings: List[str]
                      ) -> Optional[Path]:
    """Cherche SITREP_ADRASEC_GENERIQUE.pdf dans plusieurs emplacements.

    v1.0.1 — On combine systématiquement :
      - chaque emplacement RACINE candidat (CWD, exe-dir, plugins/.. etc.)
      - avec chaque SOUS-DOSSIER probable ('', 'SITREP/', 'templates/', ...).
    Cela évite de rater le PDF quand il est rangé dans un sous-dossier
    d'organisation (cas réel ADRASEC 77 : SITREP/SITREP_ADRASEC_GENERIQUE.pdf).
    """
    # 1. Variable de session explicite (chemin direct prioritaire)
    candidats: List[Path] = []
    custom = _get_var(session_vars, "SITREP_GEN_TEMPLATE")
    if custom:
        p = Path(custom)
        # Si c'est un dossier, on cherche le PDF dedans
        if p.is_dir():
            candidats.append(p / _TEMPLATE_PDF_NAME)
        else:
            candidats.append(p)

    # 2. Liste des dossiers RACINE à scanner
    racines: List[Path] = []
    # CWD
    racines.append(Path.cwd())
    # Dossier de l'exécutable / script
    if getattr(sys, "frozen", False):
        racines.append(Path(sys.executable).resolve().parent)
    else:
        try:
            racines.append(Path(sys.argv[0]).resolve().parent)
        except Exception:
            pass
    # Dossier du plugin lui-même et son parent (cas plugins/)
    try:
        plugin_dir = Path(__file__).resolve().parent
        racines.append(plugin_dir)
        racines.append(plugin_dir.parent)
    except Exception:
        pass

    # 3. Sous-dossiers probables (vide = racine, puis SITREP/, etc.)
    #    L'ordre compte : on essaie d'abord la racine, puis SITREP/ qui est
    #    le cas le plus courant ADRASEC 77, puis quelques alternatives.
    sous_dossiers = ["", "SITREP", "sitrep", "templates", "Templates",
                     "forms", "Forms", "Formulaires", "formulaires",
                     "ressources", "resources"]

    # 4. Combinaison : chaque racine × chaque sous-dossier (dédoublonné)
    vus: set = set()
    for racine in racines:
        for sd in sous_dossiers:
            if sd:
                candidat = racine / sd / _TEMPLATE_PDF_NAME
            else:
                candidat = racine / _TEMPLATE_PDF_NAME
            try:
                candidat_resolved = candidat.resolve()
            except Exception:
                continue
            if candidat_resolved in vus:
                continue
            vus.add(candidat_resolved)
            candidats.append(candidat)

    # 5. Première occurrence trouvée gagne
    for c in candidats:
        try:
            if c.is_file():
                return c
        except Exception:
            continue

    # Liste tronquée dans le warning pour rester lisible
    extrait = [str(c) for c in candidats[:10]]
    suite = f" (+{len(candidats)-10} autres)" if len(candidats) > 10 else ""
    warnings.append(
        f"Template PDF '{_TEMPLATE_PDF_NAME}' introuvable. "
        f"Emplacements testés : {extrait}{suite}. "
        f"Astuce : définir /set SITREP_GEN_TEMPLATE=C:\\chemin\\complet\\vers\\"
        f"{_TEMPLATE_PDF_NAME} pour forcer le chemin."
    )
    return None


# ---------------------------------------------------------------------------
# 5. Décodage du METAR brut pour le briefing
# ---------------------------------------------------------------------------
#
# Pour le briefing radio (style radiogramme), on n'a PAS besoin du décodage
# complet du plugin METAR. On extrait juste les éléments clés en mode bref.
# ---------------------------------------------------------------------------

def _extraire_resume_metar(metar_raw: str) -> dict:
    """Extrait un résumé court à partir d'un METAR brut.

    Retourne un dict avec : 'heure' (DDHHMM Z), 'vent_dir', 'vent_kt',
    'rafales_kt' (str ou ''), 'visibilite', 'temp', 'qnh', 'phenomenes' (list),
    'ciel' (str).
    """
    res = {
        "heure": "",
        "vent_dir": "",
        "vent_kt": "",
        "rafales_kt": "",
        "visibilite": "",
        "temp": "",
        "qnh": "",
        "phenomenes": [],
        "ciel": "",
    }
    if not metar_raw:
        return res

    tokens = metar_raw.split()
    if len(tokens) < 2:
        return res

    # Heure (DDHHMM Z)
    for t in tokens[:3]:
        m = re.match(r"^(\d{2})(\d{2})(\d{2})Z$", t)
        if m:
            res["heure"] = f"{m.group(2)}h{m.group(3)}Z (du {m.group(1)})"
            break

    # Vent
    for t in tokens:
        m = re.match(r"^(\d{3}|VRB)(\d{2,3})(?:G(\d{2,3}))?KT$", t)
        if m:
            d, v, g = m.groups()
            res["vent_dir"] = d if d != "VRB" else "VRB"
            res["vent_kt"] = v
            res["rafales_kt"] = g or ""
            break

    # Visibilité
    if "CAVOK" in tokens:
        res["visibilite"] = "CAVOK"
    else:
        for t in tokens:
            if t == "9999":
                res["visibilite"] = ">10km"
                break
            if re.match(r"^\d{4}$", t) and t != tokens[1].rstrip("Z"):
                vis = int(t)
                if 0 < vis < 9000:
                    res["visibilite"] = f"{vis}m"
                    break

    # Température / Rosée (T/Td)
    for t in tokens:
        m = re.match(r"^(M?\d{2})/(M?\d{2})$", t)
        if m:
            t1 = m.group(1).replace("M", "-")
            res["temp"] = f"{t1}°C"
            break

    # QNH
    for t in tokens:
        m = re.match(r"^Q(\d{4})$", t)
        if m:
            res["qnh"] = f"Q{m.group(1)}"
            break

    # Phénomènes (codes 2 lettres : RA, SN, BR, FG, TS, etc.)
    _CODES_PHEN = {"RA", "SN", "DZ", "GR", "GS", "PL", "IC", "SG",
                   "BR", "FG", "FU", "HZ", "VA", "DU", "SA",
                   "TS", "SH", "FZ", "BL", "DR", "MI", "BC", "VC"}
    for t in tokens[2:]:
        # Token type [+/-/VC] + 2..6 lettres
        m = re.match(r"^([+\-]|VC)?([A-Z]{2,6})$", t)
        if m:
            prefix, codes = m.groups()
            # Découpe en paires
            pairs = [codes[i:i+2] for i in range(0, len(codes), 2)]
            if all(p in _CODES_PHEN for p in pairs):
                p_str = "".join(pairs)
                if prefix:
                    p_str = prefix + p_str
                res["phenomenes"].append(p_str)

    # Ciel (1re couche significative)
    couches = []
    for t in tokens:
        m = re.match(r"^(FEW|SCT|BKN|OVC)(\d{3})(CB|TCU)?$", t)
        if m:
            type_n, alt, suff = m.groups()
            ft = int(alt) * 100
            label = f"{type_n}{ft}ft"
            if suff:
                label += suff
            couches.append(label)
    if couches:
        res["ciel"] = " ".join(couches[:3])  # max 3 couches en radiogramme
    elif "CAVOK" in tokens:
        res["ciel"] = "CAVOK"
    elif "NSC" in tokens:
        res["ciel"] = "NSC"

    return res


# ---------------------------------------------------------------------------
# 6. Décodage du TAF brut pour le briefing
# ---------------------------------------------------------------------------

def _extraire_resume_taf(taf_raw: str) -> dict:
    """Extrait les éléments clés d'un TAF pour briefing radio."""
    res = {
        "periode": "",
        "vent_base": "",
        "visi_base": "",
        "ciel_base": "",
        "evolutions": [],  # liste de strings courts
    }
    if not taf_raw:
        return res

    # Période de validité (DDHH/DDHH)
    m = re.search(r"(\d{4})/(\d{4})\b", taf_raw)
    if m:
        d1, d2 = m.group(1), m.group(2)
        res["periode"] = f"{d1[0:2]}/{d1[2:4]}h-{d2[0:2]}/{d2[2:4]}hZ"

    # On split par mots-clés de groupe (BECMG, TEMPO, FM, PROB)
    parts = re.split(r"\s+(BECMG|TEMPO|FM\d{6}|PROB\d{2})\s+", " " + taf_raw)
    # parts contient : [base_line, kw1, content1, kw2, content2, ...]

    if parts:
        base = parts[0].strip()
        # Conditions de base : vent + visi + ciel
        m_vent = re.search(r"\b(\d{3}|VRB)(\d{2,3})(?:G(\d{2,3}))?KT\b", base)
        if m_vent:
            d, v, g = m_vent.groups()
            res["vent_base"] = f"{d}/{v}kt" + (f"G{g}" if g else "")
        if "CAVOK" in base:
            res["visi_base"] = "CAVOK"
        else:
            m_vis = re.search(r"\b(\d{4})\b", base.split(maxsplit=2)[-1] if base else "")
            if m_vis:
                v = int(m_vis.group(1))
                if v == 9999:
                    res["visi_base"] = ">10km"
                elif 0 < v < 9000:
                    res["visi_base"] = f"{v}m"
        m_ciel = re.findall(r"\b(FEW|SCT|BKN|OVC)(\d{3})(CB|TCU)?\b", base)
        if m_ciel:
            res["ciel_base"] = " ".join(
                f"{t}{int(a)*100}ft" + (s if s else "") for t, a, s in m_ciel[:3]
            )

    # Évolutions
    i = 1
    while i < len(parts) - 1:
        kw = parts[i]
        content = parts[i + 1].strip()
        # Extraire période du groupe si présente
        m_p = re.match(r"^(\d{4}/\d{4})\s+(.*)$", content)
        if m_p:
            periode_g = m_p.group(1)
            reste = m_p.group(2)
        else:
            periode_g = ""
            reste = content

        # Phénomènes significatifs dans le groupe
        evol_parts = [kw]
        if periode_g:
            evol_parts.append(periode_g.replace("/", "-") + "Z")

        # Vent
        m_v = re.search(r"\b(\d{3}|VRB)(\d{2,3})(?:G(\d{2,3}))?KT\b", reste)
        if m_v:
            d, v, g = m_v.groups()
            evol_parts.append(f"vent {d}/{v}kt" + (f"G{g}" if g else ""))

        # Phénomènes critiques
        critiques = []
        for code, libelle in [("TS", "ORAGE"), ("GR", "GRELE"),
                              ("FG", "BROUILLARD"), ("FZ", "VERGLAS"),
                              ("+RA", "FORTE PLUIE"), ("+SN", "FORTE NEIGE"),
                              ("SN", "NEIGE")]:
            if code in reste:
                critiques.append(libelle)
                break  # un suffit par groupe pour rester court
        if critiques:
            evol_parts.append("/".join(critiques))

        # Visibilité réduite
        m_vis = re.search(r"\b([0-9]{4})\b", reste)
        if m_vis and m_vis.group(1) != "9999":
            try:
                v = int(m_vis.group(1))
                if 0 < v < 5000:
                    evol_parts.append(f"vis {v}m")
            except ValueError:
                pass

        # Ciel CB/TCU
        if "CB" in reste:
            evol_parts.append("CB")
        elif "TCU" in reste:
            evol_parts.append("TCU")

        res["evolutions"].append(" ".join(evol_parts))
        i += 2

    return res


# ---------------------------------------------------------------------------
# 7. Construction du texte météo — 3 styles disponibles
# ---------------------------------------------------------------------------
#
# Le style choisi dépend de la variable {SITREP_GEN_STYLE} :
#   - "radiogramme"  (défaut) : court, phrases courtes, style ADRASEC
#                     pour transmission VARA FM rapide
#   - "meteofrance"  : verbeux déterministe, style bulletin Météo France
#                     grand public (rédactionnel, sans LLM)
#   - "llm"          : appel Ollama pour reformulation naturelle, fallback
#                     automatique sur "meteofrance" si Ollama est HS
#
# Limite AcroForm /Tx : ~1500-2000 chars selon viewers, on tronque à 1800.
# ---------------------------------------------------------------------------

# Tables de traduction pour le mode verbeux (style Météo France)
_DIR_DEG_TO_FR = [
    (0, "nord"), (22.5, "nord-nord-est"), (45, "nord-est"),
    (67.5, "est-nord-est"), (90, "est"), (112.5, "est-sud-est"),
    (135, "sud-est"), (157.5, "sud-sud-est"), (180, "sud"),
    (202.5, "sud-sud-ouest"), (225, "sud-ouest"), (247.5, "ouest-sud-ouest"),
    (270, "ouest"), (292.5, "ouest-nord-ouest"), (315, "nord-ouest"),
    (337.5, "nord-nord-ouest"), (360, "nord"),
]


def _direction_verbeuse(degres_str: str) -> str:
    """Convertit '270' en 'ouest', 'VRB' en 'variable', etc."""
    if degres_str == "VRB":
        return "de secteur variable"
    try:
        d = int(degres_str) % 360
    except (TypeError, ValueError):
        return ""
    best = min(_DIR_DEG_TO_FR, key=lambda x: abs(x[0] - d))
    return f"de {best[1]}"


def _kt_to_kmh(kt_str: str) -> str:
    """Convertit '15' kt en '28 km/h'."""
    try:
        return f"{round(int(kt_str) * 1.852)} km/h"
    except (TypeError, ValueError):
        return ""


def _decoder_phenomenes_verbeux(codes: List[str]) -> List[str]:
    """Traduit ['+TSRA', 'BR'] en ['fortes pluies orageuses', 'brume']."""
    _PHEN_MAP = {
        "TS": "orages", "TSRA": "orages avec pluie",
        "TSRAGR": "orages avec pluie et grêle", "TSGR": "orages avec grêle",
        "TSSN": "orages avec neige",
        "RA": "pluie", "DZ": "bruine", "SN": "neige", "SG": "neige en grains",
        "GR": "grêle", "GS": "petite grêle",
        "SH": "averses", "SHRA": "averses de pluie", "SHSN": "averses de neige",
        "BR": "brume", "FG": "brouillard", "HZ": "brume sèche",
        "FU": "fumée", "DU": "poussière", "SA": "sable",
        "FZ": "verglas", "FZRA": "pluie verglaçante", "FZDZ": "bruine verglaçante",
        "FZFG": "brouillard givrant",
        "BLSN": "chasse-neige élevée", "DRSN": "chasse-neige basse",
        "MIFG": "brouillard mince", "BCFG": "bancs de brouillard",
        "VCSH": "averses à proximité", "VCTS": "orages à proximité",
        "VCFG": "brouillard à proximité",
        "PL": "granules de glace",
    }
    libelles = []
    for code in codes:
        c = code.lstrip("+-")
        intensite = ""
        if code.startswith("+"):
            intensite = "fortes "
        elif code.startswith("-"):
            intensite = "faibles "
        libelle = _PHEN_MAP.get(c)
        if libelle is None:
            # Tentative décomposition par paires (cas inattendus)
            paires = [c[i:i+2] for i in range(0, len(c), 2)]
            morceaux = [_PHEN_MAP.get(p, p.lower()) for p in paires]
            libelle = " ".join(morceaux)
        if intensite and libelle:
            # Préfixe "fortes" à mettre devant le bon mot
            if libelle.startswith("orages"):
                libelle = "violents " + libelle if intensite == "fortes " \
                          else "faibles " + libelle
            else:
                libelle = intensite + libelle
        libelles.append(libelle)
    return libelles


def _decrire_ciel_verbeux(ciel_str: str) -> str:
    """'BKN1500ftCB' -> 'ciel fragmenté avec cumulonimbus à 1500 ft'."""
    if not ciel_str or ciel_str in ("CAVOK", "NSC", "SKC", "CLR", "NCD"):
        return {
            "CAVOK": "conditions excellentes (visibilité ≥ 10 km, "
                     "aucun nuage significatif, aucun phénomène)",
            "NSC": "aucun nuage significatif",
            "SKC": "ciel clair", "CLR": "ciel clair",
            "NCD": "aucun nuage détecté",
        }.get(ciel_str, ciel_str.lower())

    _COUV = {"FEW": "rares passages nuageux",
             "SCT": "ciel partiellement nuageux",
             "BKN": "ciel fragmenté",
             "OVC": "ciel couvert"}
    _TYPE = {"CB": "cumulonimbus (risque orageux)",
             "TCU": "cumulus bourgeonnants (instabilité)"}

    couches = []
    for m in re.finditer(r"(FEW|SCT|BKN|OVC)(\d+)ft(CB|TCU)?", ciel_str):
        couv, alt_str, suff = m.group(1), m.group(2), m.group(3)
        couv_fr = _COUV.get(couv, couv.lower())
        ft = int(alt_str)
        m_alt = round(ft * 0.3048)
        desc = f"{couv_fr} à {ft} ft (~{m_alt} m)"
        if suff:
            desc += f", " + _TYPE.get(suff, suff.lower())
        couches.append(desc)
    return " ; ".join(couches) if couches else ciel_str.lower()


def _construire_texte_meteo_radiogramme(
        metar_station: str, metar_resume: dict,
        taf_station: str, taf_resume: dict) -> str:
    """Style ADRASEC court (1 fait / ligne) pour transmission VARA FM."""
    lignes: List[str] = []

    lignes.append(f"POINT METEO {metar_station}")
    if taf_station and taf_station != metar_station:
        lignes.append(f"(prevision sur {taf_station} - station voisine)")

    if metar_resume.get("heure"):
        lignes.append("")
        lignes.append(f"OBSERVE A {metar_resume['heure']} :")
        if metar_resume["vent_dir"]:
            vent_l = f"- Vent {metar_resume['vent_dir']}/{metar_resume['vent_kt']}kt"
            if metar_resume["rafales_kt"]:
                vent_l += f" rafales {metar_resume['rafales_kt']}kt"
            lignes.append(vent_l)
        if metar_resume["visibilite"]:
            lignes.append(f"- Visibilite {metar_resume['visibilite']}")
        if metar_resume["ciel"]:
            lignes.append(f"- Ciel {metar_resume['ciel']}")
        if metar_resume["temp"]:
            lignes.append(f"- T {metar_resume['temp']} {metar_resume.get('qnh','')}")
        if metar_resume["phenomenes"]:
            lignes.append(f"- Phenomenes : {' '.join(metar_resume['phenomenes'])}")

    if taf_resume.get("periode"):
        lignes.append("")
        lignes.append(f"PREVISION {taf_resume['periode']} :")
        if taf_resume["vent_base"]:
            lignes.append(f"- Base vent {taf_resume['vent_base']}")
        if taf_resume["visi_base"]:
            lignes.append(f"- Base visi {taf_resume['visi_base']}")
        if taf_resume["ciel_base"]:
            lignes.append(f"- Base ciel {taf_resume['ciel_base']}")
        for evol in taf_resume["evolutions"][:6]:
            lignes.append(f"- {evol}")

    risques = _detecter_risques(metar_resume, taf_resume)
    lignes.append("")
    if risques:
        lignes.append(f"VIGILANCE : {' / '.join(risques)}.")
    else:
        lignes.append("AUCUN PHENOMENE METEO CRITIQUE.")

    lignes.append("")
    lignes.append("Source: METAR+TAF NOAA/Meteo France.")

    texte = "\n".join(lignes)
    if len(texte) > 1800:
        texte = texte[:1700] + "\n... [tronque]"
    return texte


def _construire_texte_meteo_verbeux(
        metar_station: str, metar_resume: dict,
        taf_station: str, taf_resume: dict) -> str:
    """Style Météo France grand public : rédactionnel, phrases complètes.

    Texte 100% déterministe construit depuis les codes METAR/TAF.
    Aucune invention possible — chaque phrase est conditionnée à la
    présence du champ correspondant.
    """
    paragraphes: List[str] = []

    # === En-tête contextuel ===
    entete = (f"POINT DE SITUATION MÉTÉOROLOGIQUE pour la station {metar_station}.")
    if taf_station and taf_station != metar_station:
        entete += (f" Observation issue de {metar_station}, prévision "
                   f"officielle relayée pour la station voisine {taf_station}.")
    paragraphes.append(entete)

    # === Paragraphe 1 : situation actuelle ===
    if metar_resume.get("heure"):
        phrases = []
        phrases.append(f"Conditions observées à {metar_resume['heure']}.")

        # Vent
        if metar_resume.get("vent_dir"):
            dir_fr = _direction_verbeuse(metar_resume["vent_dir"])
            kt = metar_resume["vent_kt"]
            kmh = _kt_to_kmh(kt)
            vent_phrase = f"Le vent souffle {dir_fr} à {kt} kt ({kmh})"
            if metar_resume["rafales_kt"]:
                kt_g = metar_resume["rafales_kt"]
                kmh_g = _kt_to_kmh(kt_g)
                vent_phrase += (f", avec des rafales mesurées à {kt_g} kt "
                                f"({kmh_g})")
            vent_phrase += "."
            phrases.append(vent_phrase)

        # Visibilité + ciel
        visi = metar_resume.get("visibilite", "")
        ciel = metar_resume.get("ciel", "")
        if visi == "CAVOK" or ciel == "CAVOK":
            phrases.append("Les conditions sont CAVOK : visibilité supérieure "
                           "à 10 km, aucun nuage significatif sous 5000 ft, "
                           "aucun phénomène météorologique notable.")
        else:
            if visi:
                if visi == ">10km":
                    phrases.append("La visibilité dépasse 10 kilomètres.")
                elif visi.endswith("m"):
                    try:
                        m = int(visi[:-1])
                        km = m / 1000
                        if m < 1000:
                            qual = " (visibilité fortement réduite)"
                        elif m < 3000:
                            qual = " (visibilité réduite)"
                        elif m < 5000:
                            qual = " (visibilité limitée)"
                        else:
                            qual = ""
                        phrases.append(
                            f"La visibilité horizontale est de {m} mètres "
                            f"({km:.1f} km){qual}."
                        )
                    except ValueError:
                        phrases.append(f"La visibilité horizontale est de {visi}.")
                else:
                    phrases.append(f"La visibilité horizontale est de {visi}.")
            if ciel:
                phrases.append(f"On observe {_decrire_ciel_verbeux(ciel)}.")

        # Phénomènes
        if metar_resume.get("phenomenes"):
            libs = _decoder_phenomenes_verbeux(metar_resume["phenomenes"])
            if libs:
                if len(libs) == 1:
                    phrases.append(f"Phénomène en cours : {libs[0]}.")
                else:
                    phrases.append(f"Phénomènes en cours : {', '.join(libs)}.")

        # Température + QNH
        temp_parts = []
        if metar_resume.get("temp"):
            temp_parts.append(f"température de {metar_resume['temp']}")
        if metar_resume.get("qnh"):
            qnh_str = metar_resume["qnh"]
            # Tentative conversion en valeur lisible
            m_q = re.match(r"Q(\d{4})", qnh_str)
            if m_q:
                hpa = int(m_q.group(1))
                if hpa < 1000:
                    tendance = " (pression basse, perturbé)"
                elif hpa > 1020:
                    tendance = " (pression haute, anticyclonique)"
                else:
                    tendance = ""
                temp_parts.append(f"pression QNH de {hpa} hPa{tendance}")
        if temp_parts:
            phrases.append("Côté ambiance, " + " et ".join(temp_parts) + ".")

        paragraphes.append(" ".join(phrases))

    # === Paragraphe 2 : prévision ===
    if taf_resume.get("periode"):
        phrases = []
        # Période en clair
        periode = taf_resume["periode"]
        m_p = re.match(r"(\d{2})/(\d{2})h-(\d{2})/(\d{2})hZ", periode)
        if m_p:
            j1, h1, j2, h2 = m_p.groups()
            phrases.append(
                f"La prévision officielle Météo France couvre la période "
                f"du {j1} à {h1}h UTC au {j2} à {h2}h UTC."
            )
        else:
            phrases.append(f"Prévision pour la période {periode}.")

        # Conditions de base
        base_parts = []
        if taf_resume.get("vent_base"):
            # Format type "270/15kt" ou "VRB/03kt"
            m_v = re.match(r"(\d{3}|VRB)/(\d+)kt(?:G(\d+))?",
                           taf_resume["vent_base"])
            if m_v:
                d, v, g = m_v.groups()
                dir_fr = _direction_verbeuse(d)
                kmh = _kt_to_kmh(v)
                vbase = f"un vent {dir_fr} à {v} kt ({kmh})"
                if g:
                    kmh_g = _kt_to_kmh(g)
                    vbase += f" avec rafales à {g} kt ({kmh_g})"
                base_parts.append(vbase)
        if taf_resume.get("visi_base"):
            if taf_resume["visi_base"] == "CAVOK":
                base_parts.append("des conditions CAVOK initiales")
            elif taf_resume["visi_base"] == ">10km":
                base_parts.append("une visibilité supérieure à 10 km")
            else:
                base_parts.append(f"une visibilité de {taf_resume['visi_base']}")
        if taf_resume.get("ciel_base") and taf_resume["ciel_base"] != "CAVOK":
            base_parts.append(_decrire_ciel_verbeux(taf_resume["ciel_base"]))

        if base_parts:
            phrases.append("Conditions de base prévues : "
                           + ", ".join(base_parts) + ".")

        # Évolutions
        evolutions = taf_resume.get("evolutions", [])
        if evolutions:
            phrases.append("Plusieurs évolutions sont attendues durant la "
                           "période :")
            for evol in evolutions[:6]:
                # On essaie de produire une phrase plus naturelle
                phrase_evol = _verbaliser_evolution_taf(evol)
                phrases.append(f"– {phrase_evol}")

        paragraphes.append(" ".join(phrases))

    # === Paragraphe 3 : analyse opérationnelle ===
    risques = _detecter_risques(metar_resume, taf_resume)
    if risques:
        intro = ("Points de vigilance opérationnelle identifiés à partir "
                 "des données officielles : ")
        # Reformulation rédactionnelle
        risques_fr = []
        for r in risques:
            if r == "orages":
                risques_fr.append("activité orageuse")
            elif r == "grele":
                risques_fr.append("risque de grêle")
            elif r == "brouillard":
                risques_fr.append("brouillard réduisant fortement la visibilité")
            elif r == "verglas":
                risques_fr.append("risque de verglas")
            elif r == "neige":
                risques_fr.append("chutes de neige")
            elif r.startswith("rafales"):
                risques_fr.append(r.replace("rafales", "rafales de vent à"))
            else:
                risques_fr.append(r)
        paragraphes.append(intro + ", ".join(risques_fr)
                           + ". Prudence requise pour toute opération extérieure "
                             "durant les créneaux concernés.")
    else:
        paragraphes.append(
            "Aucun phénomène météorologique critique n'est observé "
            "ni prévu sur la période couverte. Les conditions sont "
            "favorables aux opérations terrain."
        )

    # === Note de bas ===
    paragraphes.append(
        "Source : METAR (observation) et TAF (prévision officielle) "
        "Météo France relayés par NOAA/NWS. Bulletin à usage opérationnel "
        "ADRASEC — pour les opérations critiques se référer aux services "
        "Aviation de Météo France."
    )

    # Assemblage final : on accepte les accents en mode verbeux car
    # destiné à lecture humaine, pas à packet ASCII
    texte = "\n\n".join(paragraphes)

    # Limite AcroForm
    if len(texte) > 1800:
        # Si on déborde, on rabote en priorité le paragraphe d'évolutions
        texte = texte[:1700] + "\n... [troncature, voir TAF brut en session]"
    return texte


def _verbaliser_evolution_taf(evol_str: str) -> str:
    """Transforme un groupe TAF condensé en phrase naturelle.

    Entrée : 'TEMPO 1015-1018Z vent 290/25ktG45 ORAGE vis 2000m CB'
    Sortie : 'temporairement entre 15h et 18h UTC, vent d'ouest-nord-ouest
              à 25 kt avec rafales à 45 kt, orage et visibilité réduite
              à 2000 m sous cumulonimbus.'
    """
    parts = evol_str.split()
    if not parts:
        return evol_str

    kw = parts[0]
    # Préfixe selon type
    if kw == "BECMG":
        prefixe = "à partir de"
    elif kw == "TEMPO":
        prefixe = "temporairement"
    elif kw.startswith("FM"):
        prefixe = "à partir de"
    elif kw.startswith("PROB"):
        try:
            p = int(kw[4:])
            prefixe = f"avec probabilité {p}%"
        except ValueError:
            prefixe = kw.lower()
    else:
        prefixe = kw.lower()

    # Période
    periode = ""
    suite_idx = 1
    if len(parts) > 1 and re.match(r"\d{2}/\d{2}-\d{2}/\d{2}Z", parts[1]):
        m = re.match(r"(\d{2})/(\d{2})-(\d{2})/(\d{2})Z", parts[1])
        if m:
            j1, h1, j2, h2 = m.groups()
            if j1 == j2:
                periode = f" entre {h1}h et {h2}h UTC"
            else:
                periode = f" du {j1} à {h1}h au {j2} à {h2}h UTC"
            suite_idx = 2

    # Reste : on parcourt les tokens
    composants = []
    i = suite_idx
    while i < len(parts):
        t = parts[i]
        # "vent" + "270/25ktG45"
        if t == "vent" and i + 1 < len(parts):
            m_v = re.match(r"(\d{3}|VRB)/(\d+)kt(?:G(\d+))?", parts[i + 1])
            if m_v:
                d, v, g = m_v.groups()
                dir_fr = _direction_verbeuse(d)
                kmh = _kt_to_kmh(v)
                vent = f"vent {dir_fr} à {v} kt ({kmh})"
                if g:
                    vent += f" avec rafales à {g} kt ({_kt_to_kmh(g)})"
                composants.append(vent)
                i += 2
                continue
        # "vis" + "2000m"
        if t == "vis" and i + 1 < len(parts):
            m_vis = re.match(r"(\d+)m", parts[i + 1])
            if m_vis:
                composants.append(f"visibilité réduite à {m_vis.group(1)} m")
                i += 2
                continue
        # Mots-clés directs
        _MOT_KEY = {
            "ORAGE": "orages",
            "GRELE": "grêle",
            "BROUILLARD": "brouillard",
            "VERGLAS": "verglas",
            "NEIGE": "neige",
            "CB": "présence de cumulonimbus (risque orageux)",
            "TCU": "présence de cumulus bourgeonnants",
            "FORTE": "intensité forte",
        }
        # "FORTE PLUIE" et "FORTE NEIGE" comme expression
        if t == "FORTE" and i + 1 < len(parts):
            if parts[i + 1] == "PLUIE":
                composants.append("fortes pluies")
                i += 2
                continue
            if parts[i + 1] == "NEIGE":
                composants.append("fortes chutes de neige")
                i += 2
                continue
        if t in _MOT_KEY:
            composants.append(_MOT_KEY[t])
            i += 1
            continue
        # Tokens slash : ORAGE/GRELE
        if "/" in t and all(p in _MOT_KEY for p in t.split("/")):
            morceaux = [_MOT_KEY[p] for p in t.split("/")]
            composants.append(" et ".join(morceaux))
            i += 1
            continue
        i += 1

    phrase = prefixe + periode
    if composants:
        phrase += ", " + ", ".join(composants)
    return phrase + "."


def _detecter_risques(metar_resume: dict, taf_resume: dict) -> List[str]:
    """Détecte les risques opérationnels (commun aux 3 styles)."""
    risques: List[str] = []
    metar_phen_str = " ".join(metar_resume.get("phenomenes", []))
    taf_evol_str = " ".join(taf_resume.get("evolutions", []))
    combined = metar_phen_str + " " + taf_evol_str

    if "TS" in combined or "ORAGE" in combined:
        risques.append("orages")
    if "GR" in combined or "GRELE" in combined:
        risques.append("grele")
    if metar_resume.get("rafales_kt") and \
            metar_resume["rafales_kt"].isdigit() and \
            int(metar_resume["rafales_kt"]) > 30:
        risques.append(f"rafales {metar_resume['rafales_kt']}kt")
    if "FG" in combined or "BROUILLARD" in combined:
        risques.append("brouillard")
    if "FZ" in combined or "VERGLAS" in combined:
        risques.append("verglas")
    if "SN" in combined or "NEIGE" in combined:
        risques.append("neige")
    return risques


def _construire_texte_meteo_llm(
        metar_station: str, metar_raw: str,
        taf_station: str, taf_raw: str,
        session_vars: dict,
        diagnostic: List[str]) -> Optional[str]:
    """Demande à Ollama de reformuler en style Météo France.

    v1.2.1 — Remonte un diagnostic verbeux dans la liste `diagnostic`.
    Chaque étape est tracée. Retourne le texte produit, ou None si
    Ollama HS / non configuré / réponse invalide. Le caller doit alors
    retomber sur le mode verbeux ET afficher le diagnostic à l'opérateur.
    """
    try:
        import json
        import urllib.request
        import urllib.error
    except Exception as e:
        diagnostic.append(f"❌ import urllib/json impossible : {e}")
        return None

    base_url, model, conf_source = _lire_conf_ollama(session_vars)
    diagnostic.append(f"🔧 Configuration Ollama : URL={base_url}, "
                      f"modèle={model}, source={conf_source}")

    # Préconnexion : on teste si Ollama répond du tout
    try:
        tags_url = base_url.rstrip("/") + "/api/tags"
        req_t = urllib.request.Request(tags_url)
        with urllib.request.urlopen(req_t, timeout=5) as resp_t:
            tags_data = json.loads(resp_t.read().decode("utf-8", errors="replace"))
        modeles = [m.get("name", "?") for m in tags_data.get("models", [])]
        diagnostic.append(f"✅ Ollama joint : {len(modeles)} modèle(s) "
                          f"disponible(s)")
        # Vérifier que le modèle demandé est dans la liste
        modele_trouve = any(
            m == model or m.startswith(model + ":") or model in m
            for m in modeles
        )
        if not modele_trouve:
            diagnostic.append(
                f"⚠️ Modèle '{model}' absent. Modèles disponibles : "
                f"{', '.join(modeles[:10])}"
            )
            # On laisse Ollama répondre quand même : il pourra essayer
            # de pull le modèle, ou le caller pourra basculer.
            if modeles:
                diagnostic.append(
                    f"💡 Définir /set OLLAMA_MODEL=<un_modèle_dispo> "
                    f"pour utiliser un modèle existant."
                )
    except urllib.error.URLError as e:
        diagnostic.append(
            f"❌ Ollama injoignable à {base_url} ({e.reason}). "
            f"Vérifiez que le service Ollama tourne (ollama serve), "
            f"que le port 11434 est ouvert, et que l'URL dans IAbrain.json "
            f"est correcte."
        )
        return None
    except Exception as e:
        diagnostic.append(f"❌ Pré-test Ollama échoué : {type(e).__name__} — {e}")
        return None

    prompt = f"""Tu es un présentateur météo de Météo France. Tu rédiges un point de situation météorologique destiné à une équipe ADRASEC sur le terrain.

DONNÉES SOURCE OFFICIELLES :
- METAR (observation actuelle) de la station {metar_station} :
  {metar_raw}
- TAF (prévision officielle Météo France) de la station {taf_station} :
  {taf_raw}

RÈGLES IMPÉRATIVES :
1. N'INVENTE RIEN. N'utilise QUE les éléments présents dans les codes METAR et TAF ci-dessus.
2. N'EXTRAPOLE PAS au-delà de la période de validité du TAF.
3. Garde les heures en UTC, ne convertis pas en heure locale.
4. Style rédactionnel français naturel, phrases complètes (pas de tirets ni liste à puces).
5. Réponse en 3 paragraphes maximum, sans titres :
   - Paragraphe 1 : conditions actuelles observées (vent, visibilité, ciel, phénomènes, température)
   - Paragraphe 2 : prévision pour la période couverte (conditions de base + évolutions notables)
   - Paragraphe 3 : analyse opérationnelle (vigilances + créneau favorable)
6. Maximum 1500 caractères au total. Sois précis mais concis.
7. Ne mets PAS de méta-commentaire, ne signe pas, ne mets pas de date d'émission. Commence directement par le contenu météo.

Rédige le bulletin maintenant :"""

    # Timeout configurable (défaut 60s — cold start de llama3.2:3b peut prendre 20-30s)
    try:
        timeout_s = int(_get_var(session_vars, "OLLAMA_TIMEOUT", "60"))
    except ValueError:
        timeout_s = 60

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "keep_alive": "30m",
        "options": {
            "temperature": 0.3,
            "num_predict": 800,
        },
    }
    url = base_url.rstrip("/") + "/api/generate"

    diagnostic.append(f"⏳ Appel Ollama (timeout {timeout_s}s, "
                      f"prompt {len(prompt)} chars)...")

    try:
        import time
        t0 = time.time()
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="replace"))
        dt = time.time() - t0
        texte = data.get("response", "").strip()
        diagnostic.append(f"✅ Ollama a répondu en {dt:.1f}s "
                          f"({len(texte)} chars).")
        if not texte:
            diagnostic.append(
                "❌ Réponse vide. Vérifiez que le modèle existe "
                "(ollama list) et qu'il n'est pas corrompu."
            )
            return None
        if len(texte) < 50:
            diagnostic.append(
                f"❌ Réponse trop courte ({len(texte)} chars < 50). "
                f"Le modèle a peut-être refusé ou hallucine. "
                f"Réponse reçue : « {texte[:100]} »"
            )
            return None
        # Tronque si déborde de la limite AcroForm
        if len(texte) > 1700:
            texte = texte[:1600] + "\n... [troncature LLM]"
        entete = (f"POINT DE SITUATION MÉTÉOROLOGIQUE — station {metar_station}")
        if taf_station and taf_station != metar_station:
            entete += f" (prévision sur {taf_station})"
        entete += ".\n\n"
        pied = ("\n\nSource : METAR + TAF officiels Météo France via NOAA. "
                "Bulletin reformulé par LLM local pour usage opérationnel ADRASEC.")
        full = entete + texte + pied
        if len(full) > 1800:
            full = full[:1750] + "..."
        diagnostic.append(f"✅ Bulletin LLM accepté ({len(full)} chars finaux).")
        return full
    except urllib.error.HTTPError as e:
        # Ollama renvoie 404 si le modèle n'existe pas, 500 si crash
        try:
            err_body = e.read().decode("utf-8", errors="replace")[:200]
        except Exception:
            err_body = ""
        diagnostic.append(
            f"❌ Ollama a renvoyé HTTP {e.code} : {e.reason}. "
            f"Détail : {err_body}. "
            f"Cause probable : le modèle '{model}' n'est pas installé. "
            f"Solution : ouvrir un terminal et exécuter "
            f"`ollama pull {model}`."
        )
        return None
    except urllib.error.URLError as e:
        diagnostic.append(
            f"❌ Connexion Ollama interrompue : {e.reason}. "
            f"Le service a peut-être planté pendant l'appel."
        )
        return None
    except TimeoutError:
        diagnostic.append(
            f"❌ Timeout après {timeout_s}s. Le modèle '{model}' charge "
            f"peut-être en RAM (cold start). Réessayer une 2e fois, "
            f"ou définir /set OLLAMA_TIMEOUT=120 pour patienter plus."
        )
        return None
    except Exception as e:
        diagnostic.append(f"❌ Erreur inattendue : {type(e).__name__} — {e}")
        return None


def _lire_conf_ollama(session_vars: Optional[dict] = None
                      ) -> Tuple[str, str, str]:
    """Récupère (base_url, model, source) depuis variables session ou IAbrain.json.

    v1.2.1 — Priorité :
      1. Variables de session OLLAMA_URL / OLLAMA_MODEL (override explicite)
      2. IAbrain.json — accepte de nombreuses variantes de clés
      3. Defaults raisonnables (localhost:11434, llama3.2:3b)

    Retourne (url, modèle, source_textuelle) — source pour diagnostic.
    """
    session_vars = session_vars or {}

    # 1. Override par variable de session
    sv_url = _get_var(session_vars, "OLLAMA_URL", "")
    sv_model = _get_var(session_vars, "OLLAMA_MODEL", "")
    if sv_url and sv_model:
        return sv_url, sv_model, "variables de session"

    # 2. IAbrain.json — beaucoup de variantes de clés acceptées
    try:
        import json as _json
        candidats: List[Path] = [Path.cwd() / "IAbrain.json"]
        if getattr(sys, "frozen", False):
            candidats.append(Path(sys.executable).resolve().parent / "IAbrain.json")
        else:
            try:
                candidats.append(Path(sys.argv[0]).resolve().parent / "IAbrain.json")
            except Exception:
                pass
        try:
            plugin_dir = Path(__file__).resolve().parent
            candidats.append(plugin_dir.parent / "IAbrain.json")
        except Exception:
            pass

        for p in candidats:
            if not p.is_file():
                continue
            with open(p, "r", encoding="utf-8") as f:
                conf = _json.load(f)
            # Variantes possibles de la clé URL
            base_url = None
            for k in ("ollama_url", "ollama_base_url", "OLLAMA_URL",
                      "OLLAMA_BASE_URL", "ollamaUrl", "ollama_endpoint",
                      "ollama_host"):
                if k in conf and conf[k]:
                    base_url = str(conf[k]).strip()
                    break
            # Variantes possibles de la clé modèle (priorité "simple" puis défaut)
            model = None
            for k in ("model_simple", "ollama_model_simple", "modele_simple",
                      "MODEL_SIMPLE", "model_default", "model", "ollama_model",
                      "MODEL", "OLLAMA_MODEL", "modele"):
                if k in conf and conf[k]:
                    model = str(conf[k]).strip()
                    break
            # Override partiel par var session
            if sv_url:
                base_url = sv_url
            if sv_model:
                model = sv_model
            if base_url and model:
                return base_url, model, f"IAbrain.json ({p.name})"
    except Exception:
        pass

    # 3. Defaults
    final_url = sv_url or "http://127.0.0.1:11434"
    final_model = sv_model or "llama3.2:3b"
    return final_url, final_model, "défaut codé en dur"


def _construire_texte_meteo(metar_station: str, metar_resume: dict,
                            taf_station: str, taf_resume: dict,
                            metar_raw: str = "", taf_raw: str = "",
                            session_vars: Optional[dict] = None,
                            diagnostic: Optional[List[str]] = None) -> str:
    """Dispatcher : choisit le style selon {SITREP_GEN_STYLE}.

    - "radiogramme" (défaut) : court, ADRASEC, transmission radio
    - "meteofrance"          : verbeux déterministe, rédactionnel
    - "llm"                   : reformulation Ollama + fallback meteofrance

    v1.2.1 — Le caller peut passer une liste `diagnostic` qui sera
    remplie d'événements (mode LLM uniquement, pour debug).
    """
    session_vars = session_vars or {}
    if diagnostic is None:
        diagnostic = []
    # Défaut v1.2.2 : 'meteofrance' (verbeux déterministe).
    # Décision opérationnelle ADRASEC 77 (15 mai 2026) : on privilégie la
    # fiabilité factuelle absolue sur la fluidité rédactionnelle. Les LLM
    # locaux (testés : qwen2.5:7b, llama3.2:3b) hallucinent les unités
    # (kt ↔ m/s), les heures (interprétation des plages TAF JJHH/JJHH) et
    # ajoutent des affirmations rassurantes non sourcées. Le mode 'llm'
    # reste disponible pour formation/démo via /set SITREP_GEN_STYLE=llm.
    style = str(session_vars.get("SITREP_GEN_STYLE", "meteofrance")).strip().lower()

    if style in ("llm", "ai", "ia", "ollama"):
        texte = _construire_texte_meteo_llm(
            metar_station, metar_raw, taf_station, taf_raw,
            session_vars, diagnostic,
        )
        if texte:
            return texte
        diagnostic.append(
            "↩️ Fallback automatique sur le mode 'meteofrance' (verbeux "
            "déterministe). Le texte du SITREP est donc construit en local "
            "sans LLM."
        )
        return _construire_texte_meteo_verbeux(
            metar_station, metar_resume, taf_station, taf_resume
        )

    if style in ("meteofrance", "verbeux", "bulletin", "verbose", "long"):
        return _construire_texte_meteo_verbeux(
            metar_station, metar_resume, taf_station, taf_resume
        )

    return _construire_texte_meteo_radiogramme(
        metar_station, metar_resume, taf_station, taf_resume
    )


def _construire_objet_meteo(metar_station: str, metar_resume: dict,
                            taf_resume: dict) -> str:
    """Construit le champ OBJET (court, en-tête radiogramme)."""
    obj = f"POINT METEO {metar_station}"
    # Ajout des risques principaux si présents
    risques_courts = []
    metar_phen = " ".join(metar_resume.get("phenomenes", []))
    taf_evol = " ".join(taf_resume.get("evolutions", []))
    if "TS" in (metar_phen + taf_evol):
        risques_courts.append("orages")
    if "GR" in (metar_phen + taf_evol):
        risques_courts.append("grele")
    if "FG" in metar_phen:
        risques_courts.append("brouillard")
    if risques_courts:
        obj += " - vigilance " + "/".join(risques_courts)
    return obj[:90]  # limite raisonnable pour un champ objet


def _compter_mots_groupes(texte: str) -> Tuple[int, int]:
    """Compte les mots et 'groupes' (5 mots = 1 groupe en télégraphie)."""
    mots = re.findall(r"\S+", texte)
    nb_mots = len(mots)
    nb_groupes = (nb_mots + 4) // 5  # arrondi supérieur
    return nb_mots, nb_groupes


# ---------------------------------------------------------------------------
# 8. Préparation des données du formulaire
# ---------------------------------------------------------------------------

def _format_dtg(now: Optional[datetime] = None) -> Tuple[str, str]:
    """Retourne (date_msg JJ/MM/AAAA, heure_utc HHMM)."""
    if now is None:
        now = datetime.now(timezone.utc)
    return now.strftime("%d/%m/%Y"), now.strftime("%H%M") + "Z"


def _preparer_data_meteo(session_vars: dict
                         ) -> Tuple[dict, str, List[str]]:
    """Prépare le dict de remplissage du formulaire en mode METEO.

    Retourne (data, texte_message_complet, diagnostic_llm).
    Le diagnostic est rempli uniquement quand le style 'llm' est demandé,
    sinon il reste vide.
    """
    metar_station = _get_var(session_vars, "METAR_STATION", "")
    metar_raw = _get_var(session_vars, "METAR_RAW", "")
    taf_station = _get_var(session_vars, "TAF_STATION", metar_station)
    taf_raw = _get_var(session_vars, "TAF_RAW", "")

    metar_resume = _extraire_resume_metar(metar_raw)
    taf_resume = _extraire_resume_taf(taf_raw)

    diagnostic_llm: List[str] = []
    texte = _construire_texte_meteo(
        metar_station or "?", metar_resume,
        taf_station or "?", taf_resume,
        metar_raw=metar_raw, taf_raw=taf_raw,
        session_vars=session_vars,
        diagnostic=diagnostic_llm,
    )
    objet = _construire_objet_meteo(metar_station or "?", metar_resume, taf_resume)
    nb_mots, nb_groupes = _compter_mots_groupes(texte)

    date_msg, heure_utc = _format_dtg()

    data = {
        # En-tête
        "date_msg": date_msg,
        "heure_utc": heure_utc,
        "mode_exercice": True,  # par défaut EXERCICE pour formation
        # Acheminement
        "de_indicatif": _get_var(session_vars, "INDICATIF", "F1GBD"),
        "station_emet": "PCO",
        "position_emet": _get_var(session_vars, "POSITION", ""),
        "a_indicatif": _get_var(session_vars, "INDICATIF_DEST", "COD-77"),
        "station_dest": "COD",
        # Liaison radio
        "freq_tx": _get_var(session_vars, "FREQ_TX", ""),
        "freq_rx": _get_var(session_vars, "FREQ_RX",
                            _get_var(session_vars, "FREQ_TX", "")),
        "mode_radio": "VARA FM",
        "rsv_r": "5",
        "rsv_s": "9",
        "rsv_v": "Stable",
        "tcq_version": _get_var(session_vars, "TCQ_VERSION", "10.10"),
        # Priorité / objet
        "priorite": "ROUTINE",
        "type_msg": "SITUATION",
        "phase": "VEILLE",
        "objet": objet,
        # Texte
        "texte_message": texte,
        "nb_mots": str(nb_mots),
        "nb_groupes": str(nb_groupes),
        "accuse_reception": False,  # ROUTINE → pas d'AR demandé
        # Rédacteur
        "redige_par": _get_var(session_vars, "INDICATIF", "F1GBD"),
        "heure_tx": heure_utc,
    }

    return data, texte, diagnostic_llm


def _preparer_data_generique(session_vars: dict) -> Tuple[dict, str]:
    """Mode générique : texte depuis {SITREP_GEN_TEXT} ou vide."""
    texte = _get_var(session_vars, "SITREP_GEN_TEXT", "")
    objet = _get_var(session_vars, "SITREP_GEN_OBJET", "")
    nb_mots, nb_groupes = _compter_mots_groupes(texte) if texte else (0, 0)
    date_msg, heure_utc = _format_dtg()

    data = {
        "date_msg": date_msg,
        "heure_utc": heure_utc,
        "mode_exercice": True,
        "de_indicatif": _get_var(session_vars, "INDICATIF", "F1GBD"),
        "station_emet": "PCO",
        "position_emet": _get_var(session_vars, "POSITION", ""),
        "a_indicatif": _get_var(session_vars, "INDICATIF_DEST", "COD-77"),
        "station_dest": "COD",
        "freq_tx": _get_var(session_vars, "FREQ_TX", ""),
        "freq_rx": _get_var(session_vars, "FREQ_RX",
                            _get_var(session_vars, "FREQ_TX", "")),
        "mode_radio": "VARA FM",
        "rsv_r": "5",
        "rsv_s": "9",
        "rsv_v": "Stable",
        "tcq_version": _get_var(session_vars, "TCQ_VERSION", "10.10"),
        "priorite": _get_var(session_vars, "PRIORITE", "ROUTINE"),
        "type_msg": _get_var(session_vars, "TYPE_MSG", "SITUATION"),
        "phase": _get_var(session_vars, "PHASE", "VEILLE"),
        "objet": objet,
        "texte_message": texte,
        "nb_mots": str(nb_mots) if nb_mots else "",
        "nb_groupes": str(nb_groupes) if nb_groupes else "",
        "accuse_reception": False,
        "redige_par": _get_var(session_vars, "INDICATIF", "F1GBD"),
        "heure_tx": heure_utc,
    }
    return data, texte


# ---------------------------------------------------------------------------
# 9. Validation des valeurs (rejet silencieux des choix invalides)
# ---------------------------------------------------------------------------

def _valider_data(data: dict, warnings: List[str]) -> dict:
    """Valide chaque champ contre le schéma. Rejette les valeurs invalides."""
    out = {}
    for key, val in data.items():
        if key in _CHOICE_FIELDS:
            options = _CHOICE_FIELDS[key]
            if val in options:
                out[key] = val
            else:
                # Cherche un match insensible à la casse
                vlow = str(val).lower()
                matched = None
                for opt in options:
                    if opt.lower() == vlow:
                        matched = opt
                        break
                if matched:
                    out[key] = matched
                else:
                    warnings.append(
                        f"Valeur '{val}' rejetée pour champ '{key}' "
                        f"(non listée). Défaut conservé. "
                        f"Options : {options}"
                    )
        elif key in _CHECKBOX_FIELDS:
            # Coercition en bool
            if isinstance(val, bool):
                out[key] = val
            elif isinstance(val, str):
                out[key] = val.strip().lower() in ("oui", "yes", "true", "1", "x")
            else:
                out[key] = bool(val)
        elif key in _TEXT_FIELDS:
            # Coercition string + troncature soft pour les champs courts
            s = str(val) if val is not None else ""
            out[key] = s
        else:
            warnings.append(f"Champ '{key}' inconnu, ignoré")
    return out


# ---------------------------------------------------------------------------
# 10. Remplissage du PDF
# ---------------------------------------------------------------------------

def _remplir_pdf(template_path: Path, output_path: Path, data: dict,
                 warnings: List[str]) -> bool:
    """Remplit le PDF AcroForm avec les valeurs de data."""
    try:
        from pypdf import PdfReader, PdfWriter
        from pypdf.generic import NameObject, BooleanObject, TextStringObject
    except ImportError as e:
        warnings.append(f"pypdf non installé : {e}. "
                        f"Installer avec : pip install pypdf")
        return False

    try:
        reader = PdfReader(str(template_path))
    except Exception as e:
        warnings.append(f"Lecture template échouée : {e}")
        return False

    # PdfWriter(clone_from=reader) clone l'ensemble du document (pages +
    # racine + AcroForm) en une seule opération atomique. C'est la
    # méthode recommandée par pypdf 4.x ; combiner append_pages_from_reader
    # + clone_reader_document_root provoque IndexError sur pypdf >= 5.
    writer = PdfWriter(clone_from=reader)

    # Champs texte et choix : via update_page_form_field_values
    text_and_choice_data = {
        k: v for k, v in data.items()
        if k in _TEXT_FIELDS or k in _CHOICE_FIELDS
    }
    if text_and_choice_data:
        try:
            for page in writer.pages:
                writer.update_page_form_field_values(page, text_and_choice_data)
        except Exception as e:
            warnings.append(f"Remplissage texte/choix échoué : {e}")

    # Cases à cocher : on les traite manuellement en parcourant les widgets
    checkbox_data = {k: v for k, v in data.items() if k in _CHECKBOX_FIELDS}
    if checkbox_data:
        _cocher_cases(writer, checkbox_data, warnings)

    # Sauvegarde
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            writer.write(f)
        return True
    except Exception as e:
        warnings.append(f"Écriture PDF échouée : {e}")
        return False


def _cocher_cases(writer, checkbox_data: dict, warnings: List[str]) -> None:
    """Coche/décoche les cases AcroForm en manipulant /V et /AS directement."""
    from pypdf.generic import NameObject

    wanted_on = {k for k, v in checkbox_data.items() if v}
    wanted_off = {k for k, v in checkbox_data.items() if not v}
    found_on = set()
    found_off = set()

    for page in writer.pages:
        if "/Annots" not in page:
            continue
        annots = page["/Annots"]
        for a in annots:
            try:
                obj = a.get_object()
            except Exception:
                continue
            if obj.get("/Subtype") != "/Widget":
                continue
            if obj.get("/FT") != "/Btn":
                # Peut aussi être hérité du parent
                parent = obj.get("/Parent")
                if not parent or parent.get_object().get("/FT") != "/Btn":
                    continue

            # Récupère le nom du champ (avec parent éventuel)
            name = obj.get("/T")
            if not name:
                parent = obj.get("/Parent")
                if parent:
                    name = parent.get_object().get("/T")
            if not name:
                continue
            name = str(name)

            if name not in (wanted_on | wanted_off):
                continue

            # Détermine l'état "on" du widget
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
                if name in wanted_on:
                    obj[NameObject("/V")] = NameObject(on_state)
                    obj[NameObject("/AS")] = NameObject(on_state)
                    found_on.add(name)
                else:
                    obj[NameObject("/V")] = NameObject("/Off")
                    obj[NameObject("/AS")] = NameObject("/Off")
                    found_off.add(name)
            except Exception as e:
                warnings.append(f"Case '{name}' non traitée : {e}")

    missing = (wanted_on | wanted_off) - (found_on | found_off)
    if missing:
        warnings.append(
            f"Cases demandées mais widget introuvable : {', '.join(sorted(missing))}"
        )


# ---------------------------------------------------------------------------
# 11. Construction du chemin de sortie
# ---------------------------------------------------------------------------

_FNAME_BAD = re.compile(r"[^A-Za-z0-9_-]+")


def _build_output_path(mode: str, data: dict) -> Path:
    """Construit un chemin de sortie en CWD."""
    label = "METEO" if mode == ACTION_METEO else "GEN"
    now = datetime.now().strftime("%Y%m%d-%H%M")
    fname = f"SITREP_GEN_{label}_{now}.pdf"
    return Path.cwd() / fname


# ---------------------------------------------------------------------------
# 12. Construction du récap Markdown
# ---------------------------------------------------------------------------

def _build_recap(template_path: Path, output_path: Path, data: dict,
                 texte: str, mode_label: str,
                 diagnostic_llm: Optional[List[str]] = None) -> str:
    """Récapitulatif Markdown pour le chat IAbrain.

    v1.2.1 — Si diagnostic_llm est fourni et non vide, affiche un bloc
    de diagnostic Ollama pour aider l'opérateur à comprendre pourquoi
    le mode LLM a fonctionné ou pas.
    """
    lines = []
    lines.append(f"## ✅ SITREP générique « {mode_label} » généré")
    lines.append("")
    lines.append(f"📄 **Template** : `{template_path}`")
    lines.append(f"📤 **PDF rempli** : `{output_path}`")
    lines.append("")

    # Bloc diagnostic LLM si activé (mode 'llm' demandé)
    if diagnostic_llm:
        lines.append("### 🧠 Diagnostic Ollama (mode LLM demandé)")
        lines.append("")
        for ligne in diagnostic_llm:
            lines.append(f"- {ligne}")
        lines.append("")

    lines.append("### 📋 En-tête radiogramme")
    lines.append("")
    lines.append("| Champ | Valeur |")
    lines.append("|---|---|")
    rows = [
        ("Date", data.get("date_msg", "—")),
        ("Heure UTC", data.get("heure_utc", "—")),
        ("Mode", "EXERCICE" if data.get("mode_exercice") else "RÉEL"),
        ("DE", f"{data.get('de_indicatif','')} ({data.get('station_emet','')})"),
        ("À", f"{data.get('a_indicatif','')} ({data.get('station_dest','')})"),
        ("Position", data.get("position_emet", "—") or "—"),
        ("FREQ TX/RX", f"{data.get('freq_tx','')} / {data.get('freq_rx','')}"),
        ("Mode radio", data.get("mode_radio", "—")),
        ("Priorité", data.get("priorite", "—")),
        ("Type", data.get("type_msg", "—")),
        ("Phase", data.get("phase", "—")),
        ("Objet", data.get("objet", "—") or "—"),
    ]
    for label, val in rows:
        lines.append(f"| {label} | {val} |")
    lines.append("")

    lines.append(f"### 📡 Texte du message ({data.get('nb_mots','?')} mots, "
                 f"{data.get('nb_groupes','?')} groupes)")
    lines.append("")
    lines.append("```")
    lines.append(texte)
    lines.append("```")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(
        "💡 **Étapes suivantes** : ouvrir le PDF, vérifier le contenu, "
        "ajuster manuellement la priorité/type/phase si besoin, puis "
        "transmettre via TCQ (VARA FM → relais ADRASEC → COD)."
    )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 13. Actions
# ---------------------------------------------------------------------------

def _action_meteo(session_vars: dict, options: Any) -> Tuple[str, List[str]]:
    warnings: List[str] = []

    # Vérifier qu'on a au moins un METAR ou un TAF
    metar_raw = _get_var(session_vars, "METAR_RAW", "")
    taf_raw = _get_var(session_vars, "TAF_RAW", "")
    if not metar_raw and not taf_raw:
        return (
            "## ⚠️ Données météo absentes\n\n"
            "Aucun METAR ni TAF disponible en session. Cliquez d'abord sur "
            "un bouton « METAR — LFXX » puis « TAF — LFXX » avant de "
            "générer ce SITREP météo.",
            ["SITREP météo : ni METAR_RAW ni TAF_RAW disponibles"]
        )

    template_path = _trouver_template(session_vars, warnings)
    if template_path is None:
        return (
            "## ❌ Template PDF introuvable\n\n"
            f"Le fichier `{_TEMPLATE_PDF_NAME}` n'a été trouvé dans aucun "
            "des emplacements habituels. Vérifiez qu'il est présent à la "
            "racine de l'installation IAbrain (à côté de IAbrain.exe / "
            "IAbrain.py).\n\n"
            f"Détails : {'; '.join(warnings)}",
            warnings,
        )

    data, texte, diagnostic_llm = _preparer_data_meteo(session_vars)
    data = _valider_data(data, warnings)

    output_path = _build_output_path(ACTION_METEO, data)
    success = _remplir_pdf(template_path, output_path, data, warnings)

    if not success:
        return (
            f"## ❌ Échec de la génération du PDF\n\n"
            f"Erreurs rencontrées :\n" +
            "\n".join(f"- {w}" for w in warnings),
            warnings,
        )

    _set_session_var(options, "SITREP_GEN_PDF", str(output_path))
    _set_session_var(options, "SITREP_GEN_RAW", texte)

    return (_build_recap(template_path, output_path, data, texte, "MÉTÉO",
                         diagnostic_llm=diagnostic_llm),
            warnings)


def _action_generique(session_vars: dict, options: Any) -> Tuple[str, List[str]]:
    warnings: List[str] = []

    template_path = _trouver_template(session_vars, warnings)
    if template_path is None:
        return (
            "## ❌ Template PDF introuvable\n\n"
            f"Détails : {'; '.join(warnings)}",
            warnings,
        )

    data, texte = _preparer_data_generique(session_vars)
    data = _valider_data(data, warnings)

    output_path = _build_output_path(ACTION_GENERIQUE, data)
    success = _remplir_pdf(template_path, output_path, data, warnings)

    if not success:
        return (
            f"## ❌ Échec de la génération du PDF\n\n" +
            "\n".join(f"- {w}" for w in warnings),
            warnings,
        )

    _set_session_var(options, "SITREP_GEN_PDF", str(output_path))
    _set_session_var(options, "SITREP_GEN_RAW", texte)

    if not texte:
        warnings.append(
            "Variable {SITREP_GEN_TEXT} vide. PDF généré avec en-tête seul, "
            "à compléter manuellement."
        )

    return _build_recap(template_path, output_path, data, texte,
                        "GÉNÉRIQUE"), warnings


# ---------------------------------------------------------------------------
# 14. Point d'entrée IAbrain
# ---------------------------------------------------------------------------

def is_action(action_id: str) -> bool:
    return (action_id or "").strip() in _ACTIONS


def list_actions() -> List[Tuple[str, str, str]]:
    return [
        (
            ACTION_METEO,
            "SITREP générique → POINT MÉTÉO",
            "Génère un SITREP générique pré-rempli avec un point météo "
            "construit à partir des variables {METAR_RAW} et {TAF_RAW} "
            "stockées par les plugins METAR et TAF. Trois styles de texte "
            "via {SITREP_GEN_STYLE} : 'meteofrance' (DÉFAUT, verbeux "
            "rédactionnel style Météo France, 100% fiable factuellement), "
            "'radiogramme' (court, style ADRASEC pour transmission VARA "
            "FM), 'llm' (reformulation Ollama — non recommandé en "
            "opérationnel, risque d'hallucinations sur unités/heures). "
            "Objet, texte et compte mots/groupes automatiques. Pré-requis : "
            "METAR et TAF déjà récupérés. Template attendu : "
            "SITREP_ADRASEC_GENERIQUE.pdf."
        ),
        (
            ACTION_GENERIQUE,
            "SITREP générique → message libre",
            "Génère un SITREP générique pré-rempli depuis la variable "
            "{SITREP_GEN_TEXT} (texte du message) et {SITREP_GEN_OBJET} "
            "(objet). Si {SITREP_GEN_TEXT} est vide, seul l'en-tête est "
            "rempli (date/heure/indicatif). Variables optionnelles : "
            "{PRIORITE}, {TYPE_MSG}, {PHASE}, {FREQ_TX}, {FREQ_RX}, "
            "{POSITION}, {INDICATIF_DEST}."
        ),
    ]


def execute_action(action_id: str,
                   imported_files: Sequence[Tuple[str, str]] = (),
                   options: Any = None) -> Tuple[str, List[str]]:
    aid = (action_id or "").strip()
    session_vars = _get_session_vars(options)

    try:
        if aid == ACTION_METEO:
            return _action_meteo(session_vars, options)
        if aid == ACTION_GENERIQUE:
            return _action_generique(session_vars, options)
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        return (
            f"## ❌ Erreur interne du plugin SITREP générique\n\n"
            f"`{type(e).__name__}` : {e}\n\n"
            f"```\n{tb}\n```\n\n"
            f"Action : `{aid}`",
            [f"plugin SITREP générique : exception {type(e).__name__}"],
        )

    return f"## ❌ Action inconnue : `{aid}`", []


# ---------------------------------------------------------------------------
# 15. Autotest
# ---------------------------------------------------------------------------

def _autotest() -> int:
    print(f"=== Autotest IAbrain_actions_sitrep_generique v{__version__} ===\n")
    erreurs = 0

    # Test 1 : contrat d'interface
    print("[1] Contrat d'interface")
    actions = list_actions()
    assert len(actions) == 2
    assert is_action(ACTION_METEO)
    assert is_action(ACTION_GENERIQUE)
    assert not is_action("metar_LFPM")
    assert not is_action("taf_LFPG")
    assert not is_action("sitrep_inconnu")
    print(f"    OK ({len(actions)} actions exposées)")

    # Test 2 : résumé METAR
    print("[2] Résumé METAR depuis brut")
    metar = "LFPG 150730Z 27015G25KT 9999 BKN040 13/08 Q1015 NOSIG"
    r = _extraire_resume_metar(metar)
    assert r["vent_dir"] == "270", f"vent_dir={r['vent_dir']}"
    assert r["vent_kt"] == "15"
    assert r["rafales_kt"] == "25"
    assert r["visibilite"] == ">10km"
    assert r["temp"] == "13°C"
    assert r["qnh"] == "Q1015"
    print(f"    OK : vent {r['vent_dir']}/{r['vent_kt']}G{r['rafales_kt']}, "
          f"vis {r['visibilite']}, {r['temp']}, {r['qnh']}")

    # Test 3 : résumé METAR avec phénomènes
    print("[3] Résumé METAR avec phénomène TSRA")
    metar2 = "LFBO 151030Z 22018G30KT 3000 +TSRA BKN015CB 18/16 Q1008"
    r2 = _extraire_resume_metar(metar2)
    assert "+TSRA" in r2["phenomenes"] or "TSRA" in " ".join(r2["phenomenes"]), \
        f"phenomenes={r2['phenomenes']}"
    assert "CB" in r2["ciel"], f"ciel={r2['ciel']}"
    print(f"    OK : phenomenes={r2['phenomenes']}, ciel={r2['ciel']}")

    # Test 4 : résumé TAF
    print("[4] Résumé TAF")
    taf = ("LFBO 100303Z 1003/1106 14010KT CAVOK "
           "TEMPO 1015/1018 29025G45KT 2000 TSRAGR BKN025CB")
    rt = _extraire_resume_taf(taf)
    assert rt["periode"] == "10/03h-11/06hZ", f"periode={rt['periode']}"
    assert "CAVOK" in rt["visi_base"]
    assert len(rt["evolutions"]) >= 1
    evol_str = " ".join(rt["evolutions"])
    assert "TEMPO" in evol_str
    assert "ORAGE" in evol_str or "TS" in evol_str
    print(f"    OK : periode={rt['periode']}, "
          f"{len(rt['evolutions'])} évolution(s)")

    # Test 5 : construction texte radiogramme (force le style explicite
    # car le défaut v1.2.2 est passé à 'meteofrance')
    print("[5] Texte radiogramme météo (style explicite)")
    texte = _construire_texte_meteo(
        "LFPG", _extraire_resume_metar(metar),
        "LFPG", _extraire_resume_taf(taf),
        session_vars={"SITREP_GEN_STYLE": "radiogramme"},
    )
    assert "POINT METEO LFPG" in texte
    assert "OBSERVE A" in texte
    assert "PREVISION" in texte
    nb_mots, nb_groupes = _compter_mots_groupes(texte)
    print(f"    OK ({nb_mots} mots, {nb_groupes} groupes, "
          f"{len(texte)} chars)")

    # Test 6 : objet automatique avec vigilance
    print("[6] Objet automatique avec détection orage")
    objet = _construire_objet_meteo("LFBO", _extraire_resume_metar(metar2),
                                    _extraire_resume_taf(taf))
    assert "POINT METEO LFBO" in objet
    assert "orages" in objet.lower(), f"objet={objet}"
    print(f"    OK : '{objet}'")

    # Test 7 : validation des choix invalides
    print("[7] Validation : rejet d'un choix invalide")
    data = {"priorite": "MEGA-URGENT", "rsv_r": "5", "objet": "test"}
    warns = []
    out = _valider_data(data, warns)
    assert "priorite" not in out, "priorite invalide aurait dû être rejeté"
    assert out["rsv_r"] == "5"
    assert out["objet"] == "test"
    assert len(warns) == 1
    print(f"    OK ({len(warns)} warning, {len(out)} champs validés)")

    # Test 8 : génération du PDF (cas critique avec META+TAF orageux)
    print("[8] Génération PDF (template local)")
    template = Path("/home/claude/SITREP_ADRASEC_GENERIQUE.pdf")
    if not template.exists():
        print(f"    SKIP : template absent ({template})")
    else:
        sv = {
            "METAR_STATION": "LFBO",
            "METAR_RAW": metar2,
            "TAF_STATION": "LFBO",
            "TAF_RAW": taf,
            "INDICATIF": "F1GBD",
            "POSITION": "JN18CR",
            "FREQ_TX": "144.575",
            "FREQ_RX": "144.575",
        }
        data, texte, _diag_llm = _preparer_data_meteo(sv)
        data = _valider_data(data, warns)
        out_pdf = Path("/tmp/test_sitrep_gen_meteo.pdf")
        w2 = []
        ok = _remplir_pdf(template, out_pdf, data, w2)
        if ok:
            print(f"    OK : PDF généré {out_pdf} ({out_pdf.stat().st_size} octets)")
            print(f"    Warnings : {w2 if w2 else 'aucun'}")
        else:
            print(f"    ÉCHEC : {w2}")
            erreurs += 1

    # Test 9 : action complète (offline)
    print("[9] Action sitrep_generique_meteo end-to-end")
    sv = {
        "METAR_STATION": "LFPG",
        "METAR_RAW": metar,
        "TAF_STATION": "LFPG",
        "TAF_RAW": taf,
        "INDICATIF": "F1GBD",
    }
    options = {"session_vars": sv}
    md, ws = execute_action(ACTION_METEO, options=options)
    assert "SITREP générique" in md, f"md={md[:200]}"
    assert "MÉTÉO" in md or "METEO" in md.upper()
    print(f"    OK ({len(md)} chars de récap)")

    # Test 10 : action sans données météo → message d'aide
    print("[10] Mode METEO sans données → message d'aide")
    md, ws = execute_action(ACTION_METEO, options={"session_vars": {}})
    assert "absentes" in md.lower() or "ni metar" in md.lower(), \
        f"message d'aide attendu, reçu : {md[:150]}"
    print("    OK")

    # Test 11 : action générique avec texte
    print("[11] Mode générique avec SITREP_GEN_TEXT")
    sv = {
        "SITREP_GEN_TEXT": "Test message. Phrase 2.",
        "SITREP_GEN_OBJET": "TEST OBJET",
        "INDICATIF": "F1GBD",
    }
    md, ws = execute_action(ACTION_GENERIQUE, options={"session_vars": sv})
    assert "GÉNÉRIQUE" in md or "GENERIQUE" in md.upper()
    print(f"    OK")

    # Test 12 (v1.0.1) : template dans sous-dossier SITREP/ (cas réel ADRASEC 77)
    print("[12] v1.0.1 — Template dans sous-dossier SITREP/")
    import tempfile, shutil
    err12 = 0
    cwd_origine = Path.cwd()
    template_src = Path("/home/claude/SITREP_ADRASEC_GENERIQUE.pdf")
    if not template_src.exists():
        print("    SKIP : template source absent")
    else:
        try:
            with tempfile.TemporaryDirectory() as tmp:
                tmp_path = Path(tmp)
                # On reproduit l'arborescence ADRASEC 77 :
                #   <CWD>/IAbrain.exe       (simulé : tmp_path est le CWD)
                #   <CWD>/SITREP/SITREP_ADRASEC_GENERIQUE.pdf
                sitrep_dir = tmp_path / "SITREP"
                sitrep_dir.mkdir()
                shutil.copy(template_src, sitrep_dir / _TEMPLATE_PDF_NAME)

                # On bascule le CWD pour simuler le lancement depuis IAbrain
                os.chdir(tmp_path)
                try:
                    warns = []
                    p = _trouver_template({}, warns)
                    if p is None:
                        print(f"    ÉCHEC : template non trouvé dans SITREP/")
                        print(f"            warnings : {warns}")
                        err12 += 1
                    elif p.parent.name != "SITREP":
                        print(f"    ÉCHEC : template trouvé ailleurs : {p}")
                        err12 += 1
                    else:
                        print(f"    OK : template localisé à {p.relative_to(tmp_path)}")
                finally:
                    os.chdir(cwd_origine)

                # Test bonus : variable SITREP_GEN_TEMPLATE pointant sur un dossier
                os.chdir(tmp_path)
                try:
                    warns = []
                    p = _trouver_template(
                        {"SITREP_GEN_TEMPLATE": str(sitrep_dir)}, warns
                    )
                    if p and p.is_file():
                        print(f"    OK bonus : SITREP_GEN_TEMPLATE=<dossier> "
                              f"résolu en {p.name}")
                    else:
                        print(f"    ÉCHEC bonus : variable dossier non résolue")
                        err12 += 1
                finally:
                    os.chdir(cwd_origine)
        except Exception as e:
            print(f"    ERREUR test 12 : {e}")
            err12 += 1
    erreurs += err12

    # Test 13 (v1.1.0) : helpers verbeux (direction, kt->kmh, phénomènes)
    print("[13] v1.1.0 — Helpers de verbalisation")
    err13 = 0
    cas_dir = [("0", "nord"), ("90", "est"), ("180", "sud"), ("270", "ouest"),
               ("45", "nord-est"), ("VRB", "variable"), ("335", "nord-nord-ouest")]
    for d_in, attendu_kw in cas_dir:
        out = _direction_verbeuse(d_in)
        if attendu_kw not in out.lower():
            print(f"    ÉCHEC direction : '{d_in}' -> '{out}' (attendu mot-clé '{attendu_kw}')")
            err13 += 1
    if _kt_to_kmh("15") != "28 km/h":
        print(f"    ÉCHEC kt->kmh : 15 kt -> {_kt_to_kmh('15')}")
        err13 += 1
    libs = _decoder_phenomenes_verbeux(["+TSRA", "BR", "FZRA"])
    txt = " | ".join(libs)
    if "violents" not in txt or "brume" not in txt or "verglaç" not in txt:
        print(f"    ÉCHEC phen verbeux : {txt}")
        err13 += 1
    if err13 == 0:
        print(f"    OK : directions, conversions, phénomènes verbeux")
    erreurs += err13

    # Test 14 (v1.1.0) : mode verbeux complet (style Météo France)
    print("[14] v1.1.0 — Mode verbeux (style Météo France)")
    err14 = 0
    metar_resume2 = _extraire_resume_metar(metar2)  # LFBO TSRA
    taf_resume2 = _extraire_resume_taf(taf)
    texte_verbeux = _construire_texte_meteo_verbeux(
        "LFBO", metar_resume2, "LFBO", taf_resume2
    )
    # Vérifs : phrases complètes, vocabulaire rédactionnel, info préservée
    checks = [
        ("POINT DE SITUATION", "en-tête présent"),
        ("Le vent souffle", "phrase rédactionnelle vent"),
        ("UTC", "heures UTC conservées"),
        ("officielle Météo France", "mention source officielle"),
        ("orageuse", "vigilance orage verbalisée"),
    ]
    for terme, desc in checks:
        if terme not in texte_verbeux:
            print(f"    ÉCHEC : '{terme}' absent ({desc})")
            print(f"    Texte : {texte_verbeux[:300]}...")
            err14 += 1
    # Doit être significativement plus long que le radiogramme
    texte_radio = _construire_texte_meteo_radiogramme(
        "LFBO", metar_resume2, "LFBO", taf_resume2
    )
    if len(texte_verbeux) <= len(texte_radio):
        print(f"    ÉCHEC : verbeux ({len(texte_verbeux)}) pas plus long "
              f"que radiogramme ({len(texte_radio)})")
        err14 += 1
    # Doit respecter la limite AcroForm
    if len(texte_verbeux) > 1800:
        print(f"    ÉCHEC : dépasse 1800 chars ({len(texte_verbeux)})")
        err14 += 1
    if err14 == 0:
        print(f"    OK : {len(texte_verbeux)} chars rédactionnels "
              f"(vs {len(texte_radio)} en radiogramme)")
    erreurs += err14

    # Test 15 (v1.2.2) : dispatcher selon SITREP_GEN_STYLE
    # NB v1.2.2 : défaut changé en 'meteofrance' (décision ADRASEC fiabilité)
    print("[15] v1.2.2 — Dispatcher de style (défaut = meteofrance)")
    err15 = 0
    cas_dispatcher = [
        ({"SITREP_GEN_STYLE": "radiogramme"}, "POINT METEO", False),
        ({"SITREP_GEN_STYLE": "meteofrance"}, "POINT DE SITUATION", True),
        ({"SITREP_GEN_STYLE": "verbeux"}, "POINT DE SITUATION", True),
        ({}, "POINT DE SITUATION", True),  # défaut v1.2.2 = meteofrance
    ]
    for sv, marqueur, doit_etre_long in cas_dispatcher:
        out = _construire_texte_meteo(
            "LFBO", metar_resume2, "LFBO", taf_resume2,
            metar_raw=metar2, taf_raw=taf, session_vars=sv,
        )
        if marqueur not in out:
            print(f"    ÉCHEC style={sv.get('SITREP_GEN_STYLE','défaut')} "
                  f": marqueur '{marqueur}' absent")
            err15 += 1
            continue
        if doit_etre_long and len(out) < 800:
            print(f"    ÉCHEC : style verbeux mais texte trop court "
                  f"({len(out)} chars)")
            err15 += 1
    if err15 == 0:
        print(f"    OK : 4 styles dispatchés correctement "
              f"(défaut v1.2.2 = meteofrance)")
    erreurs += err15

    print(f"\n=== {'TOUS LES TESTS PASSENT' if not erreurs else f'{erreurs} ÉCHEC(S)'} ===")
    return 0 if not erreurs else 1


if __name__ == "__main__":
    sys.exit(_autotest())
