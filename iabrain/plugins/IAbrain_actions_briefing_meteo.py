# -*- coding: utf-8 -*-
"""IAbrain_actions_briefing_meteo.py — Plugin BRIEFING MÉTÉO déterministe.

Produit un briefing météorologique opérationnel ADRASEC en 5 sections,
à partir des variables {METAR_RAW} et {TAF_RAW} stockées en session par
les plugins METAR et TAF.

═══════════════════════════════════════════════════════════════════════════
POURQUOI CE PLUGIN ?
═══════════════════════════════════════════════════════════════════════════

Une macro LLM « BRIEFING MÉTÉO » existe (qwen2.5:7b ou autre) mais les
modèles locaux 7B et moins hallucinent sur :
  - les altitudes des couches nuageuses (BKN040 = 4000 ft, pas 40 m)
  - les notations d'heures (mélange « 15:21 UTC » ambigu avec « 15 à 21h »)
  - les bornes des plages PROB/TEMPO (premier groupe = début, second = fin)
  - les dates complètes (invente mois et année non présents dans le METAR)

Ce plugin reprend la structure de briefing de la macro LLM mais en Python
déterministe. Aucune invention possible : chaque phrase est conditionnée à
la présence du champ correspondant dans le METAR/TAF brut.

═══════════════════════════════════════════════════════════════════════════
ACTIONS EXPOSÉES (v1.0)
═══════════════════════════════════════════════════════════════════════════

  briefing_meteo
    Produit un briefing complet (5 sections) à partir de {METAR_RAW} et
    {TAF_RAW}. Affiche le résultat en Markdown dans le chat. Stocke le
    briefing en clair dans {BRIEFING_METEO_RAW}.

═══════════════════════════════════════════════════════════════════════════
VARIABLES DE SESSION
═══════════════════════════════════════════════════════════════════════════

Lues :
    METAR_RAW         METAR brut (posé par plugin metar)
    METAR_STATION     OACI METAR
    TAF_RAW           TAF brut (posé par plugin taf)
    TAF_STATION       OACI TAF

Écrites :
    BRIEFING_METEO_RAW   briefing complet en texte (pour réutilisation)

═══════════════════════════════════════════════════════════════════════════
F1GBD - ADRASEC 77 / FNRASEC — v1.0 mai 2026
"""

from __future__ import annotations

import re
from typing import Any, List, Optional, Sequence, Tuple

__version__ = "1.1.0"

ACTION_BRIEFING = "briefing_meteo"
_ACTIONS = {ACTION_BRIEFING}


# ---------------------------------------------------------------------------
# 1. Tables de traduction (style Météo France grand public)
# ---------------------------------------------------------------------------

_DIR_DEG_FR = [
    (0, "nord"), (22.5, "nord-nord-est"), (45, "nord-est"),
    (67.5, "est-nord-est"), (90, "est"), (112.5, "est-sud-est"),
    (135, "sud-est"), (157.5, "sud-sud-est"), (180, "sud"),
    (202.5, "sud-sud-ouest"), (225, "sud-ouest"), (247.5, "ouest-sud-ouest"),
    (270, "ouest"), (292.5, "ouest-nord-ouest"), (315, "nord-ouest"),
    (337.5, "nord-nord-ouest"), (360, "nord"),
]


def _direction_fr(degres_str: str) -> str:
    """'270' -> 'd'ouest', 'VRB' -> 'de secteur variable'."""
    if degres_str == "VRB":
        return "de secteur variable"
    try:
        d = int(degres_str) % 360
    except (TypeError, ValueError):
        return ""
    best = min(_DIR_DEG_FR, key=lambda x: abs(x[0] - d))
    nom = best[1]
    return f"d'{nom}" if nom[0] in "aeiouéè" else f"de {nom}"


def _kt_to_kmh(kt_str: str) -> str:
    try:
        return f"{round(int(kt_str) * 1.852)} km/h"
    except (TypeError, ValueError):
        return ""


def _cap(s: str) -> str:
    """Met UNIQUEMENT la première lettre en majuscule, préserve la suite.

    Contrairement à str.capitalize() qui passe tout le reste en minuscules
    (cassant UTC, QNH, hPa, km/h...), cette fonction respecte la casse
    des acronymes.
    """
    if not s:
        return s
    return s[0].upper() + s[1:]


def _ft_to_m(ft: int) -> int:
    """Conversion pieds → mètres arrondie."""
    return round(ft * 0.3048)


# Phénomènes décodés en français
_PHENOMENES_FR = {
    "TS": "orages", "TSRA": "orages avec pluie",
    "TSRAGR": "orages avec pluie et grêle",
    "TSGR": "orages avec grêle", "TSSN": "orages avec neige",
    "RA": "pluie", "DZ": "bruine", "SN": "neige", "SG": "neige en grains",
    "GR": "grêle", "GS": "petite grêle", "PL": "granules de glace",
    "SH": "averses", "SHRA": "averses de pluie", "SHSN": "averses de neige",
    "BR": "brume", "FG": "brouillard", "HZ": "brume sèche",
    "FU": "fumée", "DU": "poussière", "SA": "sable",
    "FZ": "verglas", "FZRA": "pluie verglaçante",
    "FZDZ": "bruine verglaçante", "FZFG": "brouillard givrant",
    "BLSN": "chasse-neige élevée", "DRSN": "chasse-neige basse",
    "MIFG": "brouillard mince", "BCFG": "bancs de brouillard",
    "VCSH": "averses à proximité", "VCTS": "orages à proximité",
    "VCFG": "brouillard à proximité",
}

# Couches nuageuses
_COUV_FR = {
    "FEW": "rares passages nuageux",
    "SCT": "ciel partiellement nuageux",
    "BKN": "ciel fragmenté",
    "OVC": "ciel couvert",
}

_TYPE_NUAGE_FR = {
    "CB": "cumulonimbus (risque orageux)",
    "TCU": "cumulus bourgeonnants (instabilité)",
}


# ---------------------------------------------------------------------------
# 2. Helpers session
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
# 3. Parsing METAR — extraction des champs significatifs
# ---------------------------------------------------------------------------

def _parser_metar(raw: str) -> dict:
    """Parse un METAR brut et retourne un dict structuré.

    Champs retournés :
        oaci, jour, heure_utc, auto (bool), vent_dir, vent_kt, vent_g,
        cavok, visibilite, temp, td, qnh, phenomenes (list),
        nuages (list de dict {couv, ft_alt, m_alt, type})
    """
    res = {
        "oaci": "",
        "jour": "", "heure_utc": "",
        "auto": False, "cor": False,
        "vent_dir": "", "vent_kt": "", "vent_g": "",
        "cavok": False,
        "visibilite_m": None, "visibilite_label": "",
        "temp": "", "td": "", "qnh": "",
        "phenomenes": [],
        "nuages": [],
    }
    if not raw:
        return res

    tokens = raw.split()
    if not tokens:
        return res

    # OACI
    if re.match(r"^[A-Z]{4}$", tokens[0]):
        res["oaci"] = tokens[0]

    # Jour + heure
    for t in tokens[:4]:
        m = re.match(r"^(\d{2})(\d{2})(\d{2})Z$", t)
        if m:
            res["jour"] = m.group(1)
            res["heure_utc"] = m.group(2) + m.group(3)
            break

    # AUTO / COR
    if "AUTO" in tokens:
        res["auto"] = True
    if "COR" in tokens:
        res["cor"] = True

    # Vent
    for t in tokens:
        m = re.match(r"^(\d{3}|VRB)(\d{2,3})(?:G(\d{2,3}))?KT$", t)
        if m:
            res["vent_dir"] = m.group(1)
            res["vent_kt"] = m.group(2)
            res["vent_g"] = m.group(3) or ""
            break

    # CAVOK
    if "CAVOK" in tokens:
        res["cavok"] = True

    # Visibilité (4 chiffres, hors heure)
    for i, t in enumerate(tokens):
        if i < 2:
            continue
        if t == "9999":
            res["visibilite_m"] = 10000
            res["visibilite_label"] = "supérieure à 10 km"
            break
        m = re.match(r"^(\d{4})$", t)
        if m:
            v = int(m.group(1))
            if 0 <= v <= 9000:
                res["visibilite_m"] = v
                res["visibilite_label"] = f"{v} m"
                break

    # Température / point de rosée
    for t in tokens:
        m = re.match(r"^(M?\d{2})/(M?\d{2})$", t)
        if m:
            t1 = m.group(1).replace("M", "-")
            t2 = m.group(2).replace("M", "-")
            res["temp"] = t1
            res["td"] = t2
            break

    # QNH
    for t in tokens:
        m = re.match(r"^Q(\d{4})$", t)
        if m:
            res["qnh"] = m.group(1)
            break

    # Couches nuageuses (avec ou sans /// pour codes AUTO)
    for t in tokens:
        m = re.match(r"^(FEW|SCT|BKN|OVC)(\d{3})(///|CB|TCU)?$", t)
        if m:
            couv, alt_str, suff = m.groups()
            ft = int(alt_str) * 100
            res["nuages"].append({
                "couv": couv,
                "ft_alt": ft,
                "m_alt": _ft_to_m(ft),
                "type": suff if suff in ("CB", "TCU") else "",
            })

    # Code "///CB" seul (METAR AUTO indiquant CB sans plafond mesurable)
    if "///CB" in tokens or any(t == "///CB" for t in tokens):
        if not any(n["type"] == "CB" for n in res["nuages"]):
            res["nuages"].append({
                "couv": "FEW", "ft_alt": 0, "m_alt": 0, "type": "CB",
                "auto_sans_alt": True,
            })

    # Phénomènes (codes 2-6 lettres)
    codes_phen = set(["RA", "SN", "DZ", "GR", "GS", "PL", "IC", "SG",
                      "BR", "FG", "FU", "HZ", "VA", "DU", "SA",
                      "TS", "SH", "FZ", "BL", "DR", "MI", "BC", "VC"])
    for t in tokens[2:]:
        m = re.match(r"^([+\-]|VC)?([A-Z]{2,6})$", t)
        if m:
            prefix, codes = m.groups()
            paires = [codes[i:i+2] for i in range(0, len(codes), 2)]
            if all(p in codes_phen for p in paires):
                p_str = "".join(paires)
                if prefix:
                    p_str = prefix + p_str
                res["phenomenes"].append(p_str)

    return res


# ---------------------------------------------------------------------------
# 4. Parsing TAF — extraction des groupes et plages temporelles
# ---------------------------------------------------------------------------

def _parser_taf(raw: str) -> dict:
    """Parse un TAF brut multi-lignes en groupes structurés.

    Retourne dict avec :
        oaci, emission_jour, emission_heure,
        periode_debut_jour, periode_debut_heure,
        periode_fin_jour, periode_fin_heure,
        groupe_base (dict similaire à _parser_metar),
        groupes_evolution (list de dict {type, proba, debut_jjhh, fin_jjhh,
                                          contenu_parsed})
    """
    res = {
        "oaci": "",
        "emission_jour": "", "emission_heure": "",
        "periode_debut_jour": "", "periode_debut_heure": "",
        "periode_fin_jour": "", "periode_fin_heure": "",
        "groupe_base": None,
        "groupes_evolution": [],
    }
    if not raw:
        return res

    # On normalise en assemblant tout sur une ligne, puis on resplit par
    # mots-clés de groupe. NB : PROB30 TEMPO et PROB30 BECMG sont des
    # paires qui doivent rester ensemble en un seul groupe. On utilise
    # un regex de split qui matche PROBxx (suivi optionnellement de TEMPO
    # ou BECMG) comme une SEULE unité.
    raw_clean = " ".join(raw.split())
    decoupage = re.sub(
        r"\s+(PROB\d{2}(?:\s+TEMPO|\s+BECMG)?|BECMG|TEMPO|FM\d{6})\b",
        r"\n\1",
        raw_clean
    )
    parts = [p.strip() for p in decoupage.split("\n") if p.strip()]
    if not parts:
        return res

    # 1re partie = en-tête + ligne de base
    base = parts[0]
    tokens = base.split()
    if tokens and re.match(r"^[A-Z]{4}$", tokens[0]):
        res["oaci"] = tokens[0]
    for t in tokens[:5]:
        m = re.match(r"^(\d{2})(\d{2})(\d{2})Z$", t)
        if m:
            res["emission_jour"] = m.group(1)
            res["emission_heure"] = m.group(2) + m.group(3)
            break
    for t in tokens:
        m = re.match(r"^(\d{2})(\d{2})/(\d{2})(\d{2})$", t)
        if m:
            res["periode_debut_jour"] = m.group(1)
            res["periode_debut_heure"] = m.group(2)
            res["periode_fin_jour"] = m.group(3)
            res["periode_fin_heure"] = m.group(4)
            break

    # Parse ligne de base avec _parser_metar (en lui faisant croire que
    # c'est un METAR — le format est très similaire). On retire le
    # groupe période DDHH/DDHH pour ne pas perturber le parsing visibilité.
    base_propre = re.sub(r"\d{2}\d{2}/\d{2}\d{2}", "", base)
    res["groupe_base"] = _parser_metar(base_propre)

    # Évolutions : parts[1:] sont alternativement [kw, contenu, kw, contenu, ...]
    # En fait après le split, chaque entrée de parts[1:] commence par un kw.
    for p in parts[1:]:
        g = _parser_groupe_evolution(p)
        if g:
            res["groupes_evolution"].append(g)

    return res


def _parser_groupe_evolution(s: str) -> Optional[dict]:
    """Parse une ligne 'BECMG 1510/1512 ...' ou 'PROB30 TEMPO 1512/1517 ...'."""
    tokens = s.split()
    if not tokens:
        return None

    g = {
        "type": "",
        "proba": None,
        "debut_jour": "", "debut_heure": "",
        "fin_jour": "", "fin_heure": "",
        "contenu": None,  # dict comme _parser_metar
    }

    i = 0
    if tokens[0].startswith("PROB"):
        m = re.match(r"^PROB(\d{2})$", tokens[0])
        if m:
            g["proba"] = int(m.group(1))
            i = 1
            # PROB suivi optionnellement de TEMPO/BECMG
            if i < len(tokens) and tokens[i] in ("TEMPO", "BECMG"):
                g["type"] = tokens[i]
                i += 1
            else:
                g["type"] = "PROB"
    elif tokens[0] in ("BECMG", "TEMPO"):
        g["type"] = tokens[0]
        i = 1
    elif tokens[0].startswith("FM"):
        g["type"] = "FM"
        m = re.match(r"^FM(\d{2})(\d{2})(\d{2})$", tokens[0])
        if m:
            g["debut_jour"] = m.group(1)
            g["debut_heure"] = m.group(2) + m.group(3)
        i = 1

    # Période DDHH/DDHH (si pas déjà extraite par FM)
    if i < len(tokens) and not g["debut_jour"]:
        m = re.match(r"^(\d{2})(\d{2})/(\d{2})(\d{2})$", tokens[i])
        if m:
            g["debut_jour"] = m.group(1)
            g["debut_heure"] = m.group(2)
            g["fin_jour"] = m.group(3)
            g["fin_heure"] = m.group(4)
            i += 1

    # Reste = contenu météo, parsable comme un sous-METAR
    reste = " ".join(tokens[i:])
    if reste:
        g["contenu"] = _parser_metar("XXXX 000000Z " + reste)

    return g


# ---------------------------------------------------------------------------
# 5. Rendu en phrases françaises rédactionnelles
# ---------------------------------------------------------------------------

def _phrase_vent(d: dict) -> str:
    """À partir d'un dict METAR-like, produit la phrase 'vent du nord à...'.

    Retourne chaîne vide si pas de vent.
    """
    if not d.get("vent_dir"):
        return ""
    direc = _direction_fr(d["vent_dir"])
    kt = d["vent_kt"]
    kmh = _kt_to_kmh(kt)
    if int(kt) == 0:
        return "vent calme"
    phrase = f"vent {direc} à {kt} kt ({kmh})"
    if d.get("vent_g"):
        phrase += f", avec rafales à {d['vent_g']} kt ({_kt_to_kmh(d['vent_g'])})"
    return phrase


def _phrase_visibilite(d: dict) -> str:
    if d.get("cavok"):
        return ("conditions CAVOK (visibilité ≥ 10 km, aucun nuage "
                "significatif sous 5000 ft, aucun phénomène)")
    label = d.get("visibilite_label", "")
    if not label:
        return ""
    vis_m = d.get("visibilite_m")
    if vis_m is None:
        return f"visibilité {label}"
    if vis_m >= 10000:
        return "visibilité supérieure à 10 km"
    km = vis_m / 1000
    if vis_m < 1000:
        return f"visibilité fortement réduite à {vis_m} mètres ({km:.1f} km)"
    if vis_m < 3000:
        return f"visibilité réduite à {vis_m} mètres ({km:.1f} km)"
    if vis_m < 5000:
        return f"visibilité limitée à {vis_m} mètres ({km:.1f} km)"
    return f"visibilité {vis_m} mètres ({km:.1f} km)"


def _phrase_nuages(nuages: List[dict]) -> str:
    """Convertit la liste des couches en phrase rédactionnelle."""
    if not nuages:
        return ""
    parties = []
    for n in nuages:
        couv = _COUV_FR.get(n["couv"], n["couv"].lower())
        if n.get("auto_sans_alt"):
            # METAR AUTO : ///CB = présence de CB détectée, altitude inconnue
            parties.append("cumulonimbus détectés (altitude non mesurée)")
            continue
        ft = n["ft_alt"]
        m = n["m_alt"]
        desc = f"{couv} à {ft} ft ({m} m)"
        if n["type"]:
            desc += f" avec {_TYPE_NUAGE_FR.get(n['type'], n['type'])}"
        parties.append(desc)
    return " ; ".join(parties)


def _phrase_phenomenes(codes: List[str]) -> str:
    """Convertit les codes phénomènes en français."""
    if not codes:
        return ""
    libelles = []
    for code in codes:
        c = code.lstrip("+-")
        intensite = ""
        if code.startswith("+"):
            intensite = "fortes "
        elif code.startswith("-"):
            intensite = "faibles "
        libelle = _PHENOMENES_FR.get(c)
        if not libelle:
            # Décompose en paires
            paires = [c[i:i+2] for i in range(0, len(c), 2)]
            morceaux = [_PHENOMENES_FR.get(p, p.lower()) for p in paires]
            libelle = " ".join(morceaux)
        if intensite:
            if "orage" in libelle:
                libelle = ("violents " + libelle if intensite == "fortes "
                           else "faibles " + libelle)
            else:
                libelle = intensite + libelle
        libelles.append(libelle)
    return ", ".join(libelles)


def _phrase_temp_qnh(d: dict) -> str:
    parties = []
    if d.get("temp"):
        parties.append(f"température de {d['temp']} °C")
    if d.get("qnh"):
        try:
            qnh = int(d["qnh"])
            tendance = ""
            if qnh < 1000:
                tendance = " (pression basse, perturbé)"
            elif qnh > 1020:
                tendance = " (pression haute, anticyclonique)"
            parties.append(f"pression QNH de {qnh} hPa{tendance}")
        except ValueError:
            parties.append(f"QNH {d['qnh']}")
    if not parties:
        return ""
    return " et ".join(parties)


# ---------------------------------------------------------------------------
# 6. Détection des risques opérationnels
# ---------------------------------------------------------------------------

def _detecter_risques(metar: dict, taf: dict) -> dict:
    """Retourne dict {nom_risque: [créneaux JJHH-JJHH]} pour chaque risque détecté.

    Risques détectés :
        orages, grele, brouillard, verglas, neige_forte,
        rafales_fortes (>25kt), visibilite_reduite (<5km)
    """
    risques: dict = {}

    def ajoute(nom: str, creneau: str = ""):
        if nom not in risques:
            risques[nom] = []
        if creneau and creneau not in risques[nom]:
            risques[nom].append(creneau)

    # === METAR (observation actuelle) ===
    if metar:
        for p in metar.get("phenomenes", []):
            c = p.lstrip("+-")
            if "TS" in c:
                ajoute("orages", "observé actuellement")
            if "GR" in c and "GS" not in c:
                ajoute("grele", "observée actuellement")
            if "FG" in c:
                ajoute("brouillard", "observé actuellement")
            if "FZ" in c:
                ajoute("verglas", "observé actuellement")
            if "SN" in c and p.startswith("+"):
                ajoute("neige_forte", "observée actuellement")

        # Rafales actuelles
        g = metar.get("vent_g", "")
        if g and g.isdigit() and int(g) > 25:
            ajoute("rafales_fortes", f"observées à {g} kt")

        # Visibilité réduite
        v = metar.get("visibilite_m")
        if v is not None and v < 5000 and not metar.get("cavok"):
            ajoute("visibilite_reduite", f"observée à {v} m")

    # === TAF (prévision) ===
    if taf:
        for g in taf.get("groupes_evolution", []):
            contenu = g.get("contenu") or {}
            creneau = _format_creneau(g)
            for p in contenu.get("phenomenes", []):
                c = p.lstrip("+-")
                if "TS" in c:
                    ajoute("orages", creneau)
                if "GR" in c and "GS" not in c:
                    ajoute("grele", creneau)
                if "FG" in c:
                    ajoute("brouillard", creneau)
                if "FZ" in c:
                    ajoute("verglas", creneau)
                if "SN" in c and p.startswith("+"):
                    ajoute("neige_forte", creneau)
            # CB seuls dans les nuages = risque orageux indirect
            for n in contenu.get("nuages", []):
                if n.get("type") == "CB":
                    ajoute("orages", creneau)
                    break
            # Rafales prévues
            g_kt = contenu.get("vent_g", "")
            if g_kt and g_kt.isdigit() and int(g_kt) > 25:
                ajoute("rafales_fortes",
                       f"{creneau} (jusqu'à {g_kt} kt)")
            # Visibilité réduite prévue
            v = contenu.get("visibilite_m")
            if v is not None and v < 5000 and not contenu.get("cavok"):
                ajoute("visibilite_reduite", f"{creneau} ({v} m)")

    return risques


def _format_creneau(g: dict) -> str:
    """'le 15 entre 12h et 17h UTC' ou similaire."""
    dj = g.get("debut_jour", "")
    dh = g.get("debut_heure", "")
    fj = g.get("fin_jour", "")
    fh = g.get("fin_heure", "")

    if not dj:
        return "période non précisée"

    if g.get("type") == "FM":
        return f"à partir du {dj} à {dh}h UTC"

    if not fj:
        return f"à partir du {dj} à {dh}h UTC"

    if dj == fj:
        return f"le {dj} entre {dh}h et {fh}h UTC"
    return f"du {dj} à {dh}h au {fj} à {fh}h UTC"


# ---------------------------------------------------------------------------
# 7. Composition du briefing complet (markdown)
# ---------------------------------------------------------------------------

def _composer_briefing(metar: dict, taf: dict,
                       metar_station: str, taf_station: str) -> Tuple[str, str]:
    """Compose le briefing complet. Retourne (markdown, texte_brut).

    v1.1.0 : Rendu compact — une ligne blanche UNIQUEMENT entre les grandes
    sections (titres ##), aucune entre titres et leur contenu.
    """
    md_lines: List[str] = []
    txt_lines: List[str] = []

    def add(line: str):
        md_lines.append(line)
        # Nettoie le markdown pour la version texte brute
        txt = re.sub(r"\*\*([^*]+)\*\*", r"\1", line)
        txt = re.sub(r"\*([^*]+)\*", r"\1", txt)
        txt = re.sub(r"^#{1,6}\s+", "", txt)
        txt_lines.append(txt)

    def sep():
        """Ligne blanche entre deux blocs."""
        md_lines.append("")
        txt_lines.append("")

    # === En-tête ===
    add("# 📋 BRIEFING MÉTÉO OPÉRATIONNEL ADRASEC")
    add(f"**Stations** : METAR {metar_station} — TAF {taf_station}")
    if metar.get("jour") and metar.get("heure_utc"):
        h = metar["heure_utc"]
        add(f"**Observation METAR** : jour {metar['jour']} à "
            f"{h[:2]}h{h[2:]} UTC")
    if taf.get("emission_jour") and taf.get("emission_heure"):
        h = taf["emission_heure"]
        add(f"**TAF émis** : jour {taf['emission_jour']} à "
            f"{h[:2]}h{h[2:]} UTC")
    if (metar_station and taf_station and metar_station != taf_station):
        add(f"ℹ️ *Le METAR concerne {metar_station} et le TAF concerne "
            f"{taf_station}. Prévision sur station voisine — utile si "
            f"{metar_station} ne publie pas de TAF, à interpréter avec "
            f"précaution.*")

    # === SECTION 1 : Situation actuelle ===
    sep()
    add("## 1. ☁️ SITUATION ACTUELLE (METAR)")
    phrases_metar = []
    if metar.get("jour"):
        h = metar["heure_utc"]
        phrases_metar.append(
            f"Conditions observées le {metar['jour']} à "
            f"{h[:2]}h{h[2:]} UTC."
        )
    if metar.get("auto"):
        phrases_metar.append("Station automatique sans observateur humain.")
    vent_phrase = _phrase_vent(metar)
    if vent_phrase:
        phrases_metar.append(_cap(vent_phrase) + ".")
    vis_phrase = _phrase_visibilite(metar)
    if vis_phrase:
        phrases_metar.append(_cap(vis_phrase) + ".")
    nuages_phrase = _phrase_nuages(metar.get("nuages", []))
    if nuages_phrase:
        phrases_metar.append(f"Couverture nuageuse : {nuages_phrase}.")
    phen_phrase = _phrase_phenomenes(metar.get("phenomenes", []))
    if phen_phrase:
        phrases_metar.append(f"Phénomènes en cours : {phen_phrase}.")
    temp_phrase = _phrase_temp_qnh(metar)
    if temp_phrase:
        phrases_metar.append(_cap(temp_phrase) + ".")
    if not phrases_metar:
        add("*Aucune donnée d'observation METAR disponible.*")
    else:
        # Une ligne par phrase pour la lisibilité, sans ligne blanche entre
        for p in phrases_metar:
            add(p)

    # === SECTION 2 : Prévision TAF ===
    sep()
    add("## 2. 🔮 PRÉVISION (TAF)")
    if not taf.get("periode_debut_jour"):
        add("*Aucune donnée de prévision TAF disponible.*")
    else:
        # Période + base + évolutions, sans ligne blanche entre sous-titres
        # et leur contenu. Une ligne blanche seulement entre sous-blocs.
        add("**Période de validité** : "
            f"du jour **{taf['periode_debut_jour']} à "
            f"{taf['periode_debut_heure']}h00 UTC** au jour "
            f"**{taf['periode_fin_jour']} à "
            f"{taf['periode_fin_heure']}h00 UTC**.")

        base = taf.get("groupe_base") or {}
        bp = []
        v = _phrase_vent(base)
        if v:
            bp.append(_cap(v))
        if base.get("cavok"):
            bp.append("conditions CAVOK initiales")
        else:
            vis = _phrase_visibilite(base)
            if vis:
                bp.append(vis)
            nuages = _phrase_nuages(base.get("nuages", []))
            if nuages:
                bp.append(nuages)
        if bp:
            add("**Conditions de base** : " + ", ".join(bp) + ".")
        evos = taf.get("groupes_evolution", [])
        if evos:
            add("**Évolutions notables** :")
            for g in evos:
                add(_phrase_evolution(g))
        else:
            add("*Pas d'évolution significative durant la période.*")

    # === SECTION 3 : Analyse comparée ===
    sep()
    add("## 3. ⚖️ ANALYSE COMPARÉE")
    for ligne in _construire_analyse(metar, taf):
        add(ligne)

    # === SECTION 4 : Points de vigilance ===
    sep()
    add("## 4. ⚠️ POINTS DE VIGILANCE")
    risques = _detecter_risques(metar, taf)
    if not risques:
        add("✅ Aucun phénomène significatif observé ni prévu — "
            "conditions favorables.")
    else:
        for nom, creneaux in risques.items():
            libelle = {
                "orages": "**Orages**",
                "grele": "**Grêle**",
                "brouillard": "**Brouillard**",
                "verglas": "**Verglas**",
                "neige_forte": "**Neige forte**",
                "rafales_fortes": "**Vent fort (rafales)**",
                "visibilite_reduite": "**Visibilité réduite (< 5 km)**",
            }.get(nom, f"**{nom}**")
            creneaux_str = " ; ".join(creneaux) if creneaux else "à surveiller"
            add(f"- {libelle} : {creneaux_str}.")

    # === SECTION 5 : Recommandations ADRASEC ===
    sep()
    add("## 5. 🎯 RECOMMANDATIONS ADRASEC")
    add("**Créneaux opérationnels** :")
    for ligne in _construire_creneaux(metar, taf, risques):
        add(ligne)
    add("**Équipement recommandé** :")
    for ligne in _construire_equipement(metar, taf, risques):
        add(ligne)

    # === Footer ===
    sep()
    add("---")
    add("*Briefing généré à partir du METAR et du TAF officiels Météo "
        "France (relayés par NOAA/NWS). Document à usage formation / "
        "exercice ADRASEC. Réf. F1GBD - FNRASEC.*")

    return "\n".join(md_lines), "\n".join(txt_lines)


def _phrase_evolution(g: dict) -> str:
    """Une ligne de l'item 'Évolutions notables'."""
    type_g = g.get("type", "")
    proba = g.get("proba")
    contenu = g.get("contenu") or {}

    # Préfixe temporel selon type
    creneau = _format_creneau(g)

    if type_g == "BECMG":
        intro = f"**{  _cap(creneau)} ({type_g})** : changement " \
                f"progressif vers"
    elif type_g == "TEMPO":
        intro = f"**{  _cap(creneau)} ({type_g})** : variations " \
                f"temporaires de"
    elif type_g == "FM":
        intro = f"**{  _cap(creneau)} (FM)** : changement rapide vers"
    elif type_g == "PROB":
        intro = f"**Probabilité {proba}%** ({creneau}) :"
    elif proba:
        intro = f"**{  _cap(creneau)} ({type_g}, probabilité " \
                f"{proba}%)** :"
    else:
        intro = f"**{  _cap(creneau)}** :"

    elements = []
    vent = _phrase_vent(contenu)
    if vent:
        elements.append(vent)
    vis = _phrase_visibilite(contenu)
    if vis:
        elements.append(vis)
    nuages = _phrase_nuages(contenu.get("nuages", []))
    if nuages:
        elements.append(nuages)
    phen = _phrase_phenomenes(contenu.get("phenomenes", []))
    if phen:
        elements.append(phen)

    if not elements:
        elements.append("changement non détaillé")

    return f"- {intro} {' ; '.join(elements)}."


def _construire_analyse(metar: dict, taf: dict) -> List[str]:
    """Produit 2-4 phrases d'analyse factuelle déterministe."""
    lignes = []

    phen_metar = bool(metar.get("phenomenes")) if metar else False
    cavok_metar = metar.get("cavok") if metar else False

    # Détecte si TAF prévoit phénomènes
    phen_taf = False
    for g in taf.get("groupes_evolution", []):
        if g.get("contenu", {}).get("phenomenes"):
            phen_taf = True
            break
        for n in g.get("contenu", {}).get("nuages", []):
            if n.get("type") in ("CB", "TCU"):
                phen_taf = True
                break

    # Cohérence METAR / début TAF
    base = taf.get("groupe_base") or {}
    if metar and base:
        if metar.get("cavok") and base.get("cavok"):
            lignes.append("Les conditions actuelles CAVOK sont cohérentes "
                          "avec les conditions de base prévues par le TAF.")
        elif phen_metar and not base.get("cavok"):
            lignes.append("Les conditions observées sont cohérentes avec "
                          "le début de la prévision TAF.")
        else:
            lignes.append("La situation actuelle correspond aux conditions "
                          "de base prévues par le TAF.")

    # Tendance
    if not phen_metar and phen_taf:
        lignes.append("**Tendance** : dégradation prévue avec apparition "
                      "de phénomènes significatifs durant la période.")
    elif phen_metar and not phen_taf:
        lignes.append("**Tendance** : amélioration prévue, les phénomènes "
                      "actuels devraient cesser.")
    elif phen_metar and phen_taf:
        lignes.append("**Tendance** : persistance des phénomènes "
                      "significatifs sur tout ou partie de la période.")
    elif not phen_metar and not phen_taf:
        lignes.append("**Tendance** : conditions stables prévues sur "
                      "toute la période, sans phénomène significatif.")

    # Premier basculement significatif
    premier_basculement = None
    for g in taf.get("groupes_evolution", []):
        contenu = g.get("contenu") or {}
        if contenu.get("phenomenes") or any(
                n.get("type") == "CB" for n in contenu.get("nuages", [])):
            premier_basculement = g
            break

    if premier_basculement:
        creneau = _format_creneau(premier_basculement)
        type_g = premier_basculement.get("type", "")
        proba = premier_basculement.get("proba")
        proba_str = f" (probabilité {proba}%)" if proba else ""
        lignes.append(f"**Premier basculement notable** : {creneau} "
                      f"avec apparition de phénomènes ({type_g}{proba_str}).")

    return lignes


def _construire_creneaux(metar: dict, taf: dict, risques: dict) -> List[str]:
    """Identifie créneaux favorable/dégradé/critique."""
    lignes = []

    if not risques and not taf.get("groupes_evolution"):
        lignes.append("- ✅ Conditions stables sur toute la période de "
                      "validité. Toutes plages favorables aux opérations.")
        return lignes

    # Créneaux critiques = quand orages OU rafales fortes OU grêle prévus
    creneaux_critiques = []
    for g in taf.get("groupes_evolution", []):
        contenu = g.get("contenu") or {}
        risque_groupe = False
        for p in contenu.get("phenomenes", []):
            c = p.lstrip("+-")
            if "TS" in c or "GR" in c or "FZ" in c:
                risque_groupe = True
                break
        if not risque_groupe:
            g_kt = contenu.get("vent_g", "")
            if g_kt and g_kt.isdigit() and int(g_kt) > 30:
                risque_groupe = True
        if risque_groupe:
            creneaux_critiques.append(_format_creneau(g))

    # Créneaux dégradés = pluie/neige/visi réduite hors critique
    creneaux_degrades = []
    for g in taf.get("groupes_evolution", []):
        contenu = g.get("contenu") or {}
        creneau = _format_creneau(g)
        if creneau in creneaux_critiques:
            continue
        if contenu.get("phenomenes"):
            creneaux_degrades.append(creneau)
            continue
        v = contenu.get("visibilite_m")
        if v is not None and v < 5000:
            creneaux_degrades.append(creneau)

    if creneaux_critiques:
        lignes.append(
            "- 🔴 **Créneau critique** : " +
            " ; ".join(creneaux_critiques) +
            " (phénomènes dangereux prévus, opérations extérieures "
            "à éviter)."
        )
    if creneaux_degrades:
        lignes.append(
            "- 🟠 **Créneau dégradé** : " +
            " ; ".join(creneaux_degrades) +
            " (prudence requise, précipitations ou visibilité réduite)."
        )

    # Créneau favorable = base TAF si conditions de base sont bonnes
    base = taf.get("groupe_base") or {}
    if base.get("cavok") or (not base.get("phenomenes")
                             and (base.get("visibilite_m") or 10000) >= 5000):
        dj = taf.get("periode_debut_jour", "")
        dh = taf.get("periode_debut_heure", "")
        fj = taf.get("periode_fin_jour", "")
        fh = taf.get("periode_fin_heure", "")
        if dj and fj:
            if creneaux_critiques or creneaux_degrades:
                lignes.append(
                    f"- 🟢 **Créneau favorable** : conditions de base "
                    f"bonnes du {dj} à {dh}h au {fj} à {fh}h UTC, en "
                    f"dehors des créneaux ci-dessus."
                )
            else:
                lignes.append(
                    f"- 🟢 **Créneau favorable** : toute la période du "
                    f"{dj} à {dh}h au {fj} à {fh}h UTC."
                )

    if not lignes:
        lignes.append("- Conditions à surveiller — pas de créneau clairement "
                      "identifiable depuis le TAF.")

    return lignes


def _construire_equipement(metar: dict, taf: dict, risques: dict) -> List[str]:
    """Recommandations d'équipement strictement basées sur la météo."""
    lignes = []

    # Température
    if metar.get("temp"):
        try:
            t = int(metar["temp"])
            if t < 5:
                lignes.append("- Vêtements chauds (température < 5 °C).")
            elif t < 10:
                lignes.append("- Vêtements adaptés au froid (température < "
                              "10 °C).")
            elif t > 30:
                lignes.append("- Protection chaleur, hydratation "
                              "(température > 30 °C).")
        except ValueError:
            pass

    # Pluie / averses
    pluie_prevue = ("orages" in risques or
                    any("RA" in p or "DZ" in p
                        for g in taf.get("groupes_evolution", [])
                        for p in (g.get("contenu") or {}).get("phenomenes", [])))
    if pluie_prevue:
        lignes.append("- Vêtements de pluie et protection des équipements "
                      "électroniques.")

    # Neige
    if "neige_forte" in risques or any(
            "SN" in p for g in taf.get("groupes_evolution", [])
            for p in (g.get("contenu") or {}).get("phenomenes", [])):
        lignes.append("- Tenue grand froid, antidérapants, déneigement "
                      "antennes au besoin.")

    # Vent fort
    if "rafales_fortes" in risques:
        lignes.append("- Antennes mobiles bien haubanées (vent fort prévu, "
                      "rafales > 25 kt).")

    # Verglas / brouillard
    if "verglas" in risques:
        lignes.append("- Prudence circulation (verglas annoncé), tenue "
                      "antidérapante.")
    if "brouillard" in risques:
        lignes.append("- Réflecteurs et lampes haute visibilité (brouillard).")

    # CAVOK = ensoleillé
    base = taf.get("groupe_base") or {}
    if base.get("cavok") and not risques:
        lignes.append("- Protection solaire (CAVOK prévu).")

    if not lignes:
        lignes.append("- Tenue opérationnelle standard suffisante.")

    return lignes


# ---------------------------------------------------------------------------
# 8. Action principale
# ---------------------------------------------------------------------------

def _action_briefing(session_vars: dict,
                     options: Any) -> Tuple[str, List[str]]:
    warnings: List[str] = []

    metar_raw = _get_var(session_vars, "METAR_RAW", "")
    metar_station = _get_var(session_vars, "METAR_STATION", "")
    taf_raw = _get_var(session_vars, "TAF_RAW", "")
    taf_station = _get_var(session_vars, "TAF_STATION", "")

    if not metar_raw and not taf_raw:
        return (
            "## ⚠️ Données météo absentes\n\n"
            "Aucun METAR ni TAF disponible en session. Procédure :\n\n"
            "1. Cliquez d'abord un bouton « METAR — LFXX » pour récupérer "
            "les conditions actuelles.\n"
            "2. Cliquez ensuite un bouton « TAF — LFXX » pour la prévision.\n"
            "3. Re-cliquez « BRIEFING MÉTÉO » : le briefing complet sera "
            "généré sans LLM (100% déterministe).",
            ["briefing_meteo : ni METAR_RAW ni TAF_RAW en session"]
        )

    if not metar_raw:
        warnings.append("METAR_RAW absent — briefing partiel (TAF uniquement)")
    if not taf_raw:
        warnings.append("TAF_RAW absent — briefing partiel (METAR uniquement)")

    metar = _parser_metar(metar_raw) if metar_raw else {}
    taf = _parser_taf(taf_raw) if taf_raw else {}

    # Station OACI : variable ou extraction depuis raw
    if not metar_station:
        metar_station = metar.get("oaci", "?")
    if not taf_station:
        taf_station = taf.get("oaci", "?")

    md, txt = _composer_briefing(metar, taf, metar_station, taf_station)

    # Stocker le briefing en clair pour réutilisation (SITREP, TTS, etc.)
    _set_session_var(options, "BRIEFING_METEO_RAW", txt)

    return md, warnings


# ---------------------------------------------------------------------------
# 9. Point d'entrée IAbrain
# ---------------------------------------------------------------------------

def is_action(action_id: str) -> bool:
    return (action_id or "").strip() in _ACTIONS


def list_actions() -> List[Tuple[str, str, str]]:
    return [
        (
            ACTION_BRIEFING,
            "BRIEFING MÉTÉO — Synthèse opérationnelle (déterministe)",
            "Produit un briefing météorologique complet en 5 sections "
            "(situation actuelle, prévision, analyse comparée, points de "
            "vigilance, recommandations ADRASEC) à partir des variables "
            "{METAR_RAW} et {TAF_RAW}. 100% déterministe (parsing Python "
            "pur, pas de LLM), garantit absence d'hallucination sur les "
            "unités, heures et altitudes. Pré-requis : avoir cliqué un "
            "bouton METAR et un bouton TAF auparavant. Le briefing est "
            "aussi stocké dans {BRIEFING_METEO_RAW} pour réutilisation."
        ),
    ]


def execute_action(action_id: str,
                   imported_files: Sequence[Tuple[str, str]] = (),
                   options: Any = None) -> Tuple[str, List[str]]:
    aid = (action_id or "").strip()
    session_vars = _get_session_vars(options)

    try:
        if aid == ACTION_BRIEFING:
            return _action_briefing(session_vars, options)
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        return (
            f"## ❌ Erreur interne du plugin BRIEFING\n\n"
            f"`{type(e).__name__}` : {e}\n\n"
            f"```\n{tb}\n```",
            [f"plugin briefing : exception {type(e).__name__}"],
        )

    return f"## ❌ Action inconnue : `{aid}`", []


# ---------------------------------------------------------------------------
# 10. Autotest
# ---------------------------------------------------------------------------

def _autotest() -> int:
    print(f"=== Autotest IAbrain_actions_briefing_meteo v{__version__} ===\n")
    erreurs = 0

    # Test 1 : contrat d'interface
    print("[1] Contrat d'interface")
    actions = list_actions()
    assert len(actions) == 1
    assert is_action(ACTION_BRIEFING)
    assert not is_action("metar_LFPM")
    assert not is_action("taf_LFPG")
    print(f"    OK ({len(actions)} action exposée)")

    # Test 2 : parsing METAR simple
    print("[2] Parsing METAR simple")
    metar = _parser_metar(
        "LFPM 151300Z AUTO 34015KT 9999 FEW038/// SCT046/// "
        "BKN058/// ///CB 12/05 Q1007"
    )
    assert metar["oaci"] == "LFPM"
    assert metar["jour"] == "15"
    assert metar["heure_utc"] == "1300"
    assert metar["auto"] is True
    assert metar["vent_dir"] == "340"
    assert metar["vent_kt"] == "15"
    assert metar["temp"] == "12"
    assert metar["qnh"] == "1007"
    assert len(metar["nuages"]) >= 3
    assert any(n["type"] == "CB" for n in metar["nuages"])
    print(f"    OK : OACI={metar['oaci']}, jour {metar['jour']} à "
          f"{metar['heure_utc']}, {len(metar['nuages'])} couches dont CB")

    # Test 3 : parsing TAF avec multiples PROB/TEMPO
    print("[3] Parsing TAF complexe (LFPO 15)")
    taf = _parser_taf(
        "LFPO 151100Z 1512/1618 32008KT 9999 BKN040 "
        "TEMPO 1512/1521 4000 -SHRA BKN030TCU "
        "PROB40 TEMPO 1512/1518 BKN025CB "
        "PROB30 TEMPO 1512/1517 32015G30KT 2000 -TSRA BKN030CB "
        "PROB30 TEMPO 1610/1617 4000 -SHRA BKN050TCU"
    )
    assert taf["oaci"] == "LFPO"
    assert taf["periode_debut_jour"] == "15"
    assert taf["periode_debut_heure"] == "12"
    assert taf["periode_fin_jour"] == "16"
    assert taf["periode_fin_heure"] == "18"
    assert taf["groupe_base"]["vent_dir"] == "320"
    assert taf["groupe_base"]["vent_kt"] == "08"
    assert len(taf["groupes_evolution"]) >= 4, \
        f"attendu 4+ groupes, obtenu {len(taf['groupes_evolution'])}"
    print(f"    OK : période {taf['periode_debut_jour']}/{taf['periode_debut_heure']} "
          f"-> {taf['periode_fin_jour']}/{taf['periode_fin_heure']}, "
          f"{len(taf['groupes_evolution'])} évolutions")

    # Test 4 : altitudes correctement converties
    print("[4] Altitudes BKN040 → 4000 ft (PAS 40 m, anti-hallucination LLM)")
    # Le groupe base a BKN040
    nuages_base = taf["groupe_base"]["nuages"]
    bkn040 = [n for n in nuages_base if n["couv"] == "BKN"]
    assert bkn040, "BKN040 absent du groupe base"
    assert bkn040[0]["ft_alt"] == 4000, f"BKN040 = {bkn040[0]['ft_alt']} ft (attendu 4000)"
    assert bkn040[0]["m_alt"] == 1219, f"BKN040 en mètres = {bkn040[0]['m_alt']} (attendu ~1219)"
    print(f"    OK : BKN040 = 4000 ft = 1219 m (PAS 40 mètres)")

    # Test 5 : heures correctement extraites (anti-hallucination LLM)
    print("[5] Heures TAF : 1512/1517 = jour 15 12h → jour 15 17h")
    g_critique = None
    for g in taf["groupes_evolution"]:
        contenu = g.get("contenu") or {}
        if g.get("proba") == 30 and any("TSRA" in p for p in contenu.get("phenomenes", [])):
            g_critique = g
            break
    assert g_critique is not None, "groupe PROB30 TSRA introuvable"
    assert g_critique["debut_jour"] == "15"
    assert g_critique["debut_heure"] == "12"
    assert g_critique["fin_jour"] == "15"
    assert g_critique["fin_heure"] == "17"
    creneau = _format_creneau(g_critique)
    assert "15 entre 12h et 17h" in creneau, f"créneau mal formaté : {creneau}"
    print(f"    OK : '{creneau}'")

    # Test 6 : direction du vent en français
    print("[6] Direction vent en français")
    assert _direction_fr("0") == "de nord", f"0° -> {_direction_fr('0')}"
    assert _direction_fr("90") == "d'est", f"90° -> {_direction_fr('90')}"
    assert _direction_fr("180") == "de sud"
    assert _direction_fr("270") == "d'ouest"
    assert _direction_fr("340") == "de nord-nord-ouest"
    assert _direction_fr("VRB") == "de secteur variable"
    print("    OK")

    # Test 7 : phénomènes en français
    print("[7] Phénomènes en français")
    assert _phrase_phenomenes(["TSRA"]) == "orages avec pluie"
    assert _phrase_phenomenes(["-SHRA"]) == "faibles averses de pluie"
    assert _phrase_phenomenes(["+TSRAGR"]) == "violents orages avec pluie et grêle"
    assert _phrase_phenomenes(["BR"]) == "brume"
    print("    OK")

    # Test 8 : détection de risques sur cas LFPO orageux
    print("[8] Détection de risques (cas LFPO orageux)")
    risques = _detecter_risques(metar, taf)
    assert "orages" in risques, f"orages non détectés : {risques}"
    assert "rafales_fortes" in risques, f"rafales non détectées : {risques}"
    assert "visibilite_reduite" in risques, f"visibilité non détectée"
    print(f"    OK : {len(risques)} risques détectés : {list(risques.keys())}")

    # Test 9 : briefing complet end-to-end (cas réel utilisateur)
    print("[9] Briefing complet end-to-end (cas LFPM+LFPO)")
    md, txt = _composer_briefing(metar, taf, "LFPM", "LFPO")
    assert "BRIEFING MÉTÉO OPÉRATIONNEL ADRASEC" in md
    assert "LFPM" in md and "LFPO" in md
    # Anti-régression : pas de date complète inventée
    assert "2023" not in md, "date 2023 hallucinée"
    assert "2024" not in md, "date 2024 hallucinée"
    assert "juin" not in md.lower(), "mois 'juin' halluciné"
    # Heures correctement formatées
    assert "13h00 UTC" in md or "13h00 UTC" in txt, "heure 1300 mal formatée"
    # Altitudes correctes
    assert "4000 ft" in md, "BKN040 non rendu en ft"
    assert "1219 m" in md, "BKN040 non converti en m"
    # Risques correctement listés
    assert "Orages" in md
    assert "Vent fort" in md or "rafales" in md.lower()
    print(f"    OK ({len(md)} chars markdown, {len(txt)} chars texte brut)")

    # Test 10 : message d'aide si données absentes
    print("[10] Action avec données absentes")
    md, ws = execute_action(ACTION_BRIEFING, options={"session_vars": {}})
    assert "absentes" in md.lower()
    assert "METAR" in md and "TAF" in md
    print("    OK")

    # Test 11 : action complète via execute_action
    print("[11] execute_action end-to-end")
    sv = {
        "METAR_STATION": "LFPM",
        "METAR_RAW": "LFPM 151300Z AUTO 34015KT 9999 FEW038/// SCT046/// "
                     "BKN058/// ///CB 12/05 Q1007",
        "TAF_STATION": "LFPO",
        "TAF_RAW": "LFPO 151100Z 1512/1618 32008KT 9999 BKN040 "
                   "TEMPO 1512/1521 4000 -SHRA BKN030TCU "
                   "PROB30 TEMPO 1512/1517 32015G30KT 2000 -TSRA BKN030CB",
    }
    md, ws = execute_action(ACTION_BRIEFING, options={"session_vars": sv})
    assert "BRIEFING MÉTÉO" in md
    assert "LFPM" in md and "LFPO" in md
    assert "station voisine" in md.lower(), "note LFPM≠LFPO absente"
    print(f"    OK ({len(md)} chars)")

    # Test 12 : stations identiques (pas de note voisine)
    print("[12] Stations identiques (pas de note 'voisine')")
    md, ws = execute_action(ACTION_BRIEFING, options={"session_vars": {
        "METAR_STATION": "LFBO",
        "METAR_RAW": "LFBO 151300Z 22018G30KT 3000 +TSRA BKN015CB 18/16 Q1008",
        "TAF_STATION": "LFBO",
        "TAF_RAW": "LFBO 151200Z 1512/1612 22015KT 9999 BKN040 "
                   "TEMPO 1515/1518 29025G45KT 2000 TSRAGR BKN025CB",
    }})
    assert "station voisine" not in md.lower(), \
        "note voisine présente alors que stations identiques"
    assert "grêle" in md.lower(), "grêle (TSRAGR) non détectée"
    assert "Créneau critique" in md or "critique" in md.lower()
    print("    OK")

    print(f"\n=== {'TOUS LES TESTS PASSENT' if not erreurs else f'{erreurs} ÉCHEC(S)'} ===")
    return 0 if not erreurs else 1


if __name__ == "__main__":
    import sys
    sys.exit(_autotest())
