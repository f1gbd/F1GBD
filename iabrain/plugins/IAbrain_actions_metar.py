# -*- coding: utf-8 -*-
"""IAbrain_actions_metar.py — Plugin de récupération et décodage METAR.

Récupère et décode en français clair les observations météorologiques
aéronautiques (METAR) depuis le serveur NOAA :
    https://tgftp.nws.noaa.gov/data/observations/metar/decoded/{OACI}.TXT

Le code OACI de la station est déterminé selon la priorité suivante :
    1. Variable de session {METAR_STATION} si définie (ex. "LFPM").
    2. Suffixe extrait de l'action_id (ex. "metar_LFPG" -> "LFPG").
    3. Variable {OACI} (alias historique) si présente.
    4. Par défaut : "LFPM" (Melun, ADRASEC 77).

Variables lues :
    METAR_STATION (optionnelle) : code OACI 4 lettres.
    OACI          (optionnelle) : alias de METAR_STATION.

Variables écrites :
    METAR_RAW     : ligne METAR brute (ob:) telle que reçue.
    METAR_STATION : code OACI effectivement utilisé.

F1GBD - ADRASEC 77 / FNRASEC — Usage formation
"""

from __future__ import annotations

import re
import urllib.request
import urllib.error
from typing import Any, List, Sequence, Tuple

__version__ = "1.0.0"

# ---------------------------------------------------------------------------
# 1. Identifiants des actions exposées
# ---------------------------------------------------------------------------

ACTION_METAR_FETCH = "metar_fetch"
_ACTIONS = {ACTION_METAR_FETCH}

# URL de base des METAR décodés NOAA
_METAR_URL = "https://tgftp.nws.noaa.gov/data/observations/metar/decoded/{}.TXT"
_HTTP_TIMEOUT = 8  # secondes
_USER_AGENT = "IAbrain-METAR-plugin/1.0 (ADRASEC 77 FNRASEC)"

# ---------------------------------------------------------------------------
# 2. Tables de traduction (codes METAR -> français)
# ---------------------------------------------------------------------------

# Direction cardinale anglaise -> française
_DIRECTIONS_FR = {
    "N": "Nord",        "NNE": "Nord-Nord-Est",   "NE": "Nord-Est",
    "ENE": "Est-Nord-Est", "E": "Est",            "ESE": "Est-Sud-Est",
    "SE": "Sud-Est",    "SSE": "Sud-Sud-Est",     "S": "Sud",
    "SSW": "Sud-Sud-Ouest", "SW": "Sud-Ouest",    "WSW": "Ouest-Sud-Ouest",
    "W": "Ouest",       "WNW": "Ouest-Nord-Ouest", "NW": "Nord-Ouest",
    "NNW": "Nord-Nord-Ouest",
}

# Phénomènes météorologiques significatifs (codes METAR groupe w'w')
_PHENOMENES = {
    # Intensité / proximité
    "-": "faible ", "+": "forte ", "VC": "à proximité ",
    # Descripteurs
    "MI": "mince ", "PR": "partiel ", "BC": "bancs de ",
    "DR": "chasse-",  "BL": "chasse-soufflée de ",
    "SH": "averse de ", "TS": "orage avec ", "FZ": "verglaçant ",
    # Précipitations
    "DZ": "bruine", "RA": "pluie", "SN": "neige", "SG": "neige en grains",
    "IC": "cristaux de glace", "PL": "granules de glace",
    "GR": "grêle", "GS": "petite grêle/neige roulée", "UP": "précipitation inconnue",
    # Obscurcissements
    "BR": "brume", "FG": "brouillard", "FU": "fumée", "VA": "cendres volcaniques",
    "DU": "poussière", "SA": "sable", "HZ": "brume sèche",
    "PY": "embruns",
    # Autres
    "PO": "tourbillons de poussière/sable", "SQ": "grain", "FC": "tornade/trombe",
    "SS": "tempête de sable", "DS": "tempête de poussière",
    "NSW": "fin du phénomène significatif",
}

# Codes nuages (couverture)
_NUAGES = {
    "SKC": "ciel clair", "CLR": "ciel clair (auto, < 12000 ft)",
    "NSC": "aucun nuage significatif", "NCD": "aucun nuage détecté (auto)",
    "FEW": "rares (1-2/8)", "SCT": "épars (3-4/8)",
    "BKN": "fragmentés (5-7/8)", "OVC": "couvert (8/8)",
    "VV":  "ciel invisible, visibilité verticale",
}

# Types de nuages (suffixes éventuels)
_TYPES_NUAGES = {
    "CB": "cumulonimbus (orageux)",
    "TCU": "cumulus bourgeonnants",
    "CI": "cirrus", "CS": "cirrostratus", "CC": "cirrocumulus",
    "AS": "altostratus", "AC": "altocumulus",
    "NS": "nimbostratus", "SC": "stratocumulus", "ST": "stratus", "CU": "cumulus",
}


# ---------------------------------------------------------------------------
# 3. Helpers session
# ---------------------------------------------------------------------------

def _get_session_vars(options: Any) -> dict:
    """Extrait le dict session_vars depuis options (snapshot dict)."""
    if not options or not isinstance(options, dict):
        return {}
    sv = options.get("session_vars")
    return sv if isinstance(sv, dict) else {}


def _get_var(session_vars: dict, name: str) -> str:
    """Lit une variable de session ; retourne '' si absente."""
    v = session_vars.get(name)
    return str(v).strip() if v is not None else ""


def _set_session_var(options: Any, name: str, value: str) -> bool:
    """Écrit une variable dans la session via le manager si exposé.

    Retourne True en cas de succès, False si le manager n'est pas exposé
    (versions IAbrain antérieures à v1.40.7) ou en cas d'erreur.
    """
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
# 4. Détermination du code OACI
# ---------------------------------------------------------------------------

_OACI_RE = re.compile(r"^[A-Z]{4}$")


def _extraire_oaci_depuis_action_id(action_id: str) -> str:
    """Cherche un suffixe OACI 4-lettres dans l'action_id.

    Exemples :
        "metar_LFPM"   -> "LFPM"
        "metar-LFPG"   -> "LFPG"
        "METAR_KJFK"   -> "KJFK"
        "metar_fetch"  -> ""   (pas un OACI)
    """
    if not action_id:
        return ""
    # On cherche un groupe terminal de 4 lettres après un séparateur
    m = re.search(r"[_\-]([A-Za-z]{4})$", action_id)
    if m:
        candidat = m.group(1).upper()
        if _OACI_RE.match(candidat) and candidat != "ETCH":  # exclut "metar_fetch"
            return candidat
    return ""


def _determiner_oaci(action_id: str, session_vars: dict) -> Tuple[str, str]:
    """Détermine le code OACI à interroger et la source de cette information.

    Priorité : METAR_STATION > suffixe action_id > OACI > défaut LFPM.

    Retourne (code_oaci, source_textuelle).
    """
    # Priorité 1 : variable explicite METAR_STATION
    s = _get_var(session_vars, "METAR_STATION").upper()
    if s and _OACI_RE.match(s):
        return s, "variable {METAR_STATION}"

    # Priorité 2 : suffixe de l'action_id (ex. metar_LFPM)
    s = _extraire_oaci_depuis_action_id(action_id)
    if s:
        return s, f"nom de l'action ({action_id})"

    # Priorité 3 : variable {OACI} (alias historique)
    s = _get_var(session_vars, "OACI").upper()
    if s and _OACI_RE.match(s):
        return s, "variable {OACI}"

    # Priorité 4 : défaut ADRASEC 77
    return "LFPM", "valeur par défaut (Melun, ADRASEC 77)"


# ---------------------------------------------------------------------------
# 5. Téléchargement du fichier METAR
# ---------------------------------------------------------------------------

def _telecharger_metar(oaci: str) -> Tuple[str, str]:
    """Télécharge le METAR décodé NOAA pour la station donnée.

    Retourne (contenu, erreur). En cas de succès, erreur=''.
    En cas d'échec, contenu='' et erreur contient la cause.
    """
    url = _METAR_URL.format(oaci.upper())
    req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=_HTTP_TIMEOUT) as resp:
            data = resp.read()
        # Le fichier est en ASCII / UTF-8
        try:
            texte = data.decode("utf-8")
        except UnicodeDecodeError:
            texte = data.decode("latin-1", errors="replace")
        if not texte.strip():
            return "", "réponse vide du serveur NOAA"
        return texte, ""
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return "", (f"station {oaci} introuvable sur le serveur NOAA "
                        f"(HTTP 404). Vérifiez le code OACI.")
        return "", f"erreur HTTP {e.code} : {e.reason}"
    except urllib.error.URLError as e:
        return "", (f"impossible de joindre le serveur NOAA : {e.reason}. "
                    f"Vérifiez votre connexion Internet.")
    except Exception as e:
        return "", f"erreur inattendue : {type(e).__name__} — {e}"


# ---------------------------------------------------------------------------
# 6. Parsing et décodage français
# ---------------------------------------------------------------------------

def _parser_entete(texte: str) -> dict:
    """Extrait les champs textuels pré-décodés par le NOAA.

    Le format est une suite de lignes "Clé: valeur" + la ligne "ob:" finale
    contenant le METAR brut. Cette fonction ne fait que normaliser les
    valeurs ; la traduction française est faite par _decoder_metar_brut.
    """
    champs = {}
    lignes = [l.strip() for l in texte.splitlines() if l.strip()]
    if not lignes:
        return champs

    # Première ligne = nom de la station + coordonnées + altitude
    # Ex: "Melun, France (LFPM) 48-37N 002-41E 92M"
    champs["_station_line"] = lignes[0]
    m = re.match(
        r"^(.*?)\s*\(([A-Z]{4})\)\s+([0-9NSEW\-]+)\s+([0-9NSEW\-]+)\s+([0-9]+M)",
        lignes[0],
    )
    if m:
        champs["nom"] = m.group(1).strip()
        champs["oaci"] = m.group(2)
        champs["lat"] = m.group(3)
        champs["lon"] = m.group(4)
        champs["alt"] = m.group(5)

    # Deuxième ligne = date d'observation
    # Ex: "May 15, 2026 - 01:30 AM EDT / 2026.05.15 0530 UTC"
    if len(lignes) > 1:
        champs["date_obs"] = lignes[1]
        m = re.search(r"/\s*([0-9.]+)\s+([0-9]{4})\s+UTC", lignes[1])
        if m:
            champs["date_utc"] = m.group(1)
            champs["heure_utc"] = m.group(2)

    # Lignes "Clé: valeur"
    for ligne in lignes[2:]:
        m = re.match(r"^([A-Za-z][A-Za-z \(\)\.]*?)\s*:\s*(.*)$", ligne)
        if m:
            cle = m.group(1).strip().lower()
            val = m.group(2).strip()
            # Nettoyage des suffixes ":0" parasites du flux NOAA
            val = re.sub(r":0\s*$", "", val)
            champs[cle] = val

    return champs


def _traduire_vent(valeur: str) -> str:
    """Traduit une ligne 'Wind: from the NNW (330 degrees) at 5 MPH (4 KT)'."""
    if not valeur:
        return "non renseigné"
    if re.search(r"calm|variable\s+at\s+0", valeur, re.IGNORECASE):
        return "calme"

    # Direction cardinale
    m_dir = re.search(r"from the (\w+)\s*\((\d+)\s*degrees?\)", valeur, re.I)
    direction_fr = ""
    degres = ""
    if m_dir:
        card = m_dir.group(1).upper()
        degres = m_dir.group(2)
        direction_fr = _DIRECTIONS_FR.get(card, card)
    elif re.search(r"variable", valeur, re.I):
        direction_fr = "variable"

    # Vitesse
    m_v = re.search(r"at\s+([\d.]+)\s*MPH\s*\(\s*([\d.]+)\s*KT\)", valeur, re.I)
    vitesse_txt = ""
    if m_v:
        mph = float(m_v.group(1))
        kt = float(m_v.group(2))
        kmh = round(kt * 1.852, 1)
        vitesse_txt = f"{kt:.0f} kt ({kmh} km/h, {mph:.0f} mph)"

    # Rafales
    m_g = re.search(r"gusting to\s+([\d.]+)\s*MPH\s*\(\s*([\d.]+)\s*KT\)", valeur, re.I)
    rafales_txt = ""
    if m_g:
        kt_g = float(m_g.group(2))
        kmh_g = round(kt_g * 1.852, 1)
        rafales_txt = f", **rafales** à {kt_g:.0f} kt ({kmh_g} km/h)"

    parties = []
    if direction_fr and degres:
        parties.append(f"du **{direction_fr}** ({degres}°)")
    elif direction_fr:
        parties.append(f"**{direction_fr}**")
    if vitesse_txt:
        parties.append(f"à {vitesse_txt}")
    if rafales_txt:
        parties.append(rafales_txt.lstrip(", "))

    return ", ".join(parties) if parties else valeur


def _traduire_visibilite(valeur: str) -> str:
    """Traduit 'Visibility: 4 mile(s)' ou 'Visibility: greater than 7 mile(s)'."""
    if not valeur:
        return "non renseignée"
    plus = "supérieure à " if re.search(r"greater than", valeur, re.I) else ""
    m = re.search(r"([\d./]+)\s*mile", valeur, re.I)
    if m:
        miles_str = m.group(1)
        # Gestion des fractions style "1/4"
        if "/" in miles_str:
            num, den = miles_str.split("/")
            try:
                miles = float(num) / float(den)
            except ValueError:
                miles = 0
        else:
            try:
                miles = float(miles_str)
            except ValueError:
                miles = 0
        km = round(miles * 1.609, 1)
        return f"{plus}{miles_str} mile(s) — soit environ **{km} km**"
    return valeur


def _f_to_c(f_str: str) -> str:
    """Convertit '41 F' -> '5 °C' avec arrondi entier."""
    m = re.search(r"(-?[\d.]+)\s*F", f_str, re.I)
    if not m:
        return f_str
    f = float(m.group(1))
    c = (f - 32) * 5 / 9
    # Si la chaîne contient déjà la valeur Celsius en parenthèses, on la garde
    m_c = re.search(r"\(\s*(-?[\d.]+)\s*C\s*\)", f_str)
    if m_c:
        return f"**{m_c.group(1)} °C** ({f:.0f} °F)"
    return f"**{c:.0f} °C** ({f:.0f} °F)"


def _traduire_pression(valeur: str) -> str:
    """Traduit '29.65 in. Hg (1004 hPa)' -> '1004 hPa (29.65 inHg)'."""
    m_hpa = re.search(r"\(\s*([\d.]+)\s*hPa\s*\)", valeur)
    m_in = re.search(r"([\d.]+)\s*in\.?\s*Hg", valeur, re.I)
    if m_hpa and m_in:
        hpa = float(m_hpa.group(1))
        tendance = ""
        if hpa < 1000:
            tendance = " (basse, perturbé)"
        elif hpa > 1020:
            tendance = " (haute, anticyclonique)"
        else:
            tendance = " (standard)"
        return f"**{hpa:.0f} hPa**{tendance} — {m_in.group(1)} inHg"
    return valeur


# ---------- Décodage du METAR brut (ligne "ob:") ----------

def _decoder_metar_brut(ob: str) -> List[str]:
    """Décode la ligne METAR brute en éléments français supplémentaires.

    Retourne une liste de chaînes Markdown (lignes de bullet). Cette fonction
    complète les champs déjà fournis par le NOAA en exposant les éléments
    manquants : QFE, code AUTO, nuages détaillés, météo significative, RVR.
    """
    extras: List[str] = []
    if not ob:
        return extras

    tokens = ob.split()
    if len(tokens) < 2:
        return extras

    # tokens[0] = OACI, tokens[1] = ddhhmmZ (date-heure d'observation)
    m_dh = re.match(r"^(\d{2})(\d{2})(\d{2})Z$", tokens[1])
    if m_dh:
        jour, hh, mm = m_dh.groups()
        extras.append(
            f"- **Heure d'observation** : le {jour} du mois à "
            f"{hh}h{mm} UTC"
        )

    # AUTO / COR
    if "AUTO" in tokens:
        extras.append(
            "- **Source** : observation **automatique** (station sans observateur)"
        )
    if "COR" in tokens:
        extras.append("- **Correction** appliquée à un message précédent (COR)")

    # CAVOK
    if "CAVOK" in tokens:
        extras.append(
            "- **CAVOK** : visibilité ≥ 10 km, aucun nuage sous 5000 ft (ou MSA), "
            "aucun phénomène significatif → **conditions excellentes**"
        )

    # Météo significative (groupe w'w')
    phenomenes_trouves = []
    for t in tokens[2:]:
        if t in ("CAVOK", "NSC", "NCD", "SKC", "CLR"):
            continue
        # On ne traite ici que les groupes courts faits exclusivement de
        # préfixes / codes phénomènes (ex: -RA, +TSRA, VCSH, BR, FG).
        if re.match(r"^[+\-]?(VC)?[A-Z]{2,8}$", t) and 2 <= len(t.replace("+", "").replace("-", "")) <= 8:
            decode = _decoder_token_phenomene(t)
            if decode:
                phenomenes_trouves.append(decode)
    if phenomenes_trouves:
        extras.append(
            "- **Phénomènes significatifs** : "
            + ", ".join(f"*{p}*" for p in phenomenes_trouves)
        )

    # Nuages (couches FEW/SCT/BKN/OVC + altitude en centaines de ft)
    couches = []
    for t in tokens:
        m = re.match(r"^(FEW|SCT|BKN|OVC|VV)(\d{3})(CB|TCU)?$", t)
        if m:
            type_n, alt_cent, suff = m.groups()
            alt_ft = int(alt_cent) * 100
            alt_m = round(alt_ft * 0.3048)
            libelle = _NUAGES.get(type_n, type_n)
            ligne = f"{libelle} à {alt_ft} ft (~{alt_m} m)"
            if suff:
                ligne += f" — {_TYPES_NUAGES.get(suff, suff)}"
            couches.append(ligne)
    if couches:
        extras.append("- **Couches nuageuses** :")
        for c in couches:
            extras.append(f"    - {c}")

    # QNH brut (Q ou A) — utile si le décodage NOAA est incomplet
    for t in tokens:
        if re.match(r"^Q\d{4}$", t):
            extras.append(f"- **QNH** : {t[1:]} hPa (référence pression mer)")
            break
        if re.match(r"^A\d{4}$", t):
            inhg = int(t[1:]) / 100
            hpa = round(inhg * 33.8639)
            extras.append(f"- **QNH** : {inhg:.2f} inHg ≈ {hpa} hPa")
            break

    # Visibilité en mètres (groupe à 4 chiffres après le vent)
    for i, t in enumerate(tokens):
        if re.match(r"^\d{4}$", t) and i >= 2 and not re.match(r"^\d{6}Z?$", t):
            # On évite de prendre la date par erreur (déjà filtrée par le Z)
            try:
                m_vis = int(t)
                if m_vis == 9999:
                    extras.append("- **Visibilité (brute METAR)** : ≥ 10 km")
                elif 0 <= m_vis <= 9000:
                    extras.append(f"- **Visibilité (brute METAR)** : {m_vis} m")
                break
            except ValueError:
                pass

    return extras


def _decoder_token_phenomene(token: str) -> str:
    """Décode un groupe w'w' du METAR, ex: '-RA', '+TSRA', 'VCSH', 'BR'."""
    t = token
    parts = []

    # Intensité ou proximité
    if t.startswith("-"):
        parts.append(_PHENOMENES["-"]); t = t[1:]
    elif t.startswith("+"):
        parts.append(_PHENOMENES["+"]); t = t[1:]
    elif t.startswith("VC"):
        parts.append(_PHENOMENES["VC"]); t = t[2:]

    # Découpage par paires de lettres (codes 2 lettres)
    elements = re.findall(r"[A-Z]{2}", t)
    if not elements or any(e not in _PHENOMENES for e in elements):
        # Pas un groupe météo connu : on ignore silencieusement
        return ""

    for e in elements:
        parts.append(_PHENOMENES[e])

    return "".join(parts).strip()


# ---------------------------------------------------------------------------
# 7. Action principale
# ---------------------------------------------------------------------------

def _action_metar_fetch(action_id: str, session_vars: dict, options: Any
                        ) -> Tuple[str, List[str]]:
    """Récupère et décode le METAR pour la station déterminée."""
    warnings: List[str] = []

    oaci, source = _determiner_oaci(action_id, session_vars)

    # Téléchargement
    contenu, erreur = _telecharger_metar(oaci)
    if erreur:
        md = (
            f"## ❌ Erreur récupération METAR — {oaci}\n\n"
            f"**Station demandée** : `{oaci}` *(source : {source})*\n\n"
            f"**Cause** : {erreur}\n\n"
            f"---\n\n"
            f"**Pour réessayer :**\n"
            f"- Vérifiez le code OACI 4 lettres (ex. LFPM, LFPG, EGLL, KJFK).\n"
            f"- Définissez `/set METAR_STATION=XXXX` pour forcer une autre station.\n"
            f"- URL interrogée : {_METAR_URL.format(oaci)}"
        )
        warnings.append(f"METAR {oaci} : {erreur}")
        return md, warnings

    # Parsing
    champs = _parser_entete(contenu)
    if not champs:
        warnings.append(f"contenu METAR {oaci} vide ou non parsable")
        return f"## ⚠️ METAR {oaci} reçu mais illisible\n\n```\n{contenu}\n```", warnings

    # Extraction ligne ob: (METAR brut)
    m_ob = re.search(r"^ob:\s*(.+)$", contenu, re.MULTILINE)
    metar_brut = m_ob.group(1).strip() if m_ob else ""

    # Stockage en session
    if metar_brut:
        if _set_session_var(options, "METAR_RAW", metar_brut):
            stockage_md = "✅ Variable `{METAR_RAW}` stockée en session."
        else:
            stockage_md = (
                "ℹ️ Pour mémoriser le METAR brut, copiez :\n"
                f"`/set METAR_RAW={metar_brut}`"
            )
    else:
        stockage_md = ""

    _set_session_var(options, "METAR_STATION", oaci)

    # ---- Construction du rendu Markdown ----
    nom = champs.get("nom", "station inconnue")
    lat = champs.get("lat", "?")
    lon = champs.get("lon", "?")
    alt = champs.get("alt", "?")
    date_obs = champs.get("date_obs", "")

    lignes_md = [
        f"## 🛩️ METAR {oaci} — {nom}",
        "",
        f"**Source** : station {source}.",
        f"**Position** : {lat} / {lon} — altitude {alt}.",
        f"**Observation** : {date_obs}.",
        "",
        "### 🌬️ Conditions météorologiques",
        "",
    ]

    if "wind" in champs:
        lignes_md.append(f"- **Vent** : {_traduire_vent(champs['wind'])}.")
    if "visibility" in champs:
        lignes_md.append(f"- **Visibilité** : {_traduire_visibilite(champs['visibility'])}.")
    if "temperature" in champs:
        lignes_md.append(f"- **Température** : {_f_to_c(champs['temperature'])}.")
    if "dew point" in champs:
        lignes_md.append(f"- **Point de rosée** : {_f_to_c(champs['dew point'])}.")
    if "relative humidity" in champs:
        lignes_md.append(f"- **Humidité relative** : **{champs['relative humidity']}**.")
    if "pressure (altimeter)" in champs:
        lignes_md.append(
            f"- **Pression QNH** : {_traduire_pression(champs['pressure (altimeter)'])}."
        )
    elif "pressure" in champs:
        lignes_md.append(f"- **Pression** : {_traduire_pression(champs['pressure'])}.")

    # Sky conditions / weather (texte brut NOAA si présent)
    if "sky conditions" in champs:
        lignes_md.append(f"- **Ciel (NOAA)** : {champs['sky conditions']}.")
    if "weather" in champs:
        lignes_md.append(f"- **Temps présent (NOAA)** : {champs['weather']}.")

    # Décodage complémentaire de la ligne brute
    extras = _decoder_metar_brut(metar_brut)
    if extras:
        lignes_md.append("")
        lignes_md.append("### 🔍 Décodage complémentaire (METAR brut)")
        lignes_md.append("")
        lignes_md.extend(extras)

    # METAR brut + métadonnées
    lignes_md.append("")
    lignes_md.append("### 📡 METAR brut (transmission OACI)")
    lignes_md.append("")
    lignes_md.append("```")
    lignes_md.append(metar_brut if metar_brut else "(non disponible)")
    lignes_md.append("```")

    if stockage_md:
        lignes_md.append("")
        lignes_md.append(stockage_md)

    lignes_md.append("")
    lignes_md.append(
        f"*Source : NOAA / NWS — {_METAR_URL.format(oaci)}*"
    )

    return "\n".join(lignes_md), warnings


# ---------------------------------------------------------------------------
# 8. Point d'entrée IAbrain (contrat d'interface)
# ---------------------------------------------------------------------------

def is_action(action_id: str) -> bool:
    """Retourne True si action_id est géré par ce plugin.

    Accepte :
        - "metar_fetch" (id canonique)
        - "metar_XXXX" où XXXX est un code OACI 4 lettres
          (permet de nommer le bouton avec le code de la station)
    """
    aid = (action_id or "").strip()
    if aid in _ACTIONS:
        return True
    if _extraire_oaci_depuis_action_id(aid):
        return True
    return False


def list_actions() -> List[Tuple[str, str, str]]:
    """Déclare les actions exposées par le plugin (format strict à 3 éléments)."""
    return [
        (
            ACTION_METAR_FETCH,
            "METAR — Récupérer et décoder",
            "Télécharge et décode en français clair l'observation "
            "météorologique aéronautique (METAR) d'une station OACI "
            "depuis le serveur NOAA. La station est déterminée par la "
            "variable {METAR_STATION} ou par le suffixe du nom du bouton "
            "(ex. bouton 'metar_LFPM' → station LFPM). Défaut : LFPM "
            "(Melun, ADRASEC 77). Stocke le METAR brut dans {METAR_RAW}."
        ),
    ]


def execute_action(action_id: str,
                   imported_files: Sequence[Tuple[str, str]] = (),
                   options: Any = None) -> Tuple[str, List[str]]:
    """Point d'entrée appelé par IAbrain au clic sur la macro Action."""
    aid = (action_id or "").strip()
    session_vars = _get_session_vars(options)

    if aid in _ACTIONS or _extraire_oaci_depuis_action_id(aid):
        try:
            return _action_metar_fetch(aid, session_vars, options)
        except Exception as e:
            return (
                f"## ❌ Erreur interne du plugin METAR\n\n"
                f"`{type(e).__name__}` : {e}\n\n"
                f"Action : `{aid}`",
                [f"plugin METAR : exception {type(e).__name__}"],
            )

    return f"## ❌ Action inconnue : `{aid}`", []


# ---------------------------------------------------------------------------
# 9. Autotest local
# ---------------------------------------------------------------------------

def _autotest() -> int:
    """Vérifie le contrat d'interface et le parsing sur un échantillon."""
    print(f"=== Autotest IAbrain_actions_metar v{__version__} ===\n")
    erreurs = 0

    # Test 1 : contrat d'interface
    print("[1] Contrat d'interface")
    actions = list_actions()
    assert isinstance(actions, list) and len(actions) >= 1, "list_actions vide"
    for a in actions:
        assert len(a) == 3, f"action mal formée : {a!r}"
    assert is_action("metar_fetch"), "is_action('metar_fetch') doit être True"
    assert is_action("metar_LFPM"), "is_action('metar_LFPM') doit être True"
    assert is_action("METAR_LFPG"), "is_action('METAR_LFPG') doit être True"
    assert not is_action("hello_world"), "is_action('hello_world') doit être False"
    assert not is_action(""), "is_action('') doit être False"
    print("    OK")

    # Test 2 : extraction OACI depuis action_id
    print("[2] Extraction OACI depuis action_id")
    cas = [
        ("metar_LFPM", "LFPM"),
        ("metar-LFPG", "LFPG"),
        ("METAR_KJFK", "KJFK"),
        ("metar_fetch", ""),
        ("hello", ""),
        ("metar_XX", ""),  # trop court
    ]
    for entree, attendu in cas:
        obtenu = _extraire_oaci_depuis_action_id(entree)
        if obtenu != attendu:
            print(f"    ÉCHEC : '{entree}' -> '{obtenu}' (attendu '{attendu}')")
            erreurs += 1
    if not erreurs:
        print("    OK")

    # Test 3 : parsing du fichier NOAA (échantillon réel LFPM)
    print("[3] Parsing échantillon LFPM")
    echantillon = (
        "Melun, France (LFPM) 48-37N 002-41E 92M\n"
        "May 15, 2026 - 01:30 AM EDT / 2026.05.15 0530 UTC\n"
        "Wind: from the NNW (330 degrees) at 5 MPH (4 KT):0\n"
        "Visibility: 4 mile(s):0\n"
        "Temperature: 41 F (5 C)\n"
        "Dew Point: 41 F (5 C)\n"
        "Relative Humidity: 100%\n"
        "Pressure (altimeter): 29.65 in. Hg (1004 hPa)\n"
        "ob: LFPM 150530Z AUTO 33004KT 7000 NSC 05/05 Q1004\n"
        "cycle: 5\n"
    )
    champs = _parser_entete(echantillon)
    assert champs.get("oaci") == "LFPM", f"OACI mal parsé : {champs.get('oaci')}"
    assert champs.get("nom") == "Melun, France", f"nom mal parsé : {champs.get('nom')}"
    assert "wind" in champs, "champ 'wind' manquant"
    assert "temperature" in champs, "champ 'temperature' manquant"
    print("    OK")

    # Test 4 : traduction vent
    print("[4] Traduction vent")
    vent = _traduire_vent("from the NNW (330 degrees) at 5 MPH (4 KT)")
    assert "Nord-Nord-Ouest" in vent, f"vent mal traduit : {vent}"
    assert "330°" in vent, f"degrés absents : {vent}"
    assert "km/h" in vent, f"conversion km/h absente : {vent}"
    print(f"    {vent}")
    print("    OK")

    # Test 5 : conversion température
    print("[5] Conversion température")
    t = _f_to_c("41 F (5 C)")
    assert "5 °C" in t and "41 °F" in t, f"température mal convertie : {t}"
    print(f"    {t}")
    print("    OK")

    # Test 6 : décodage METAR brut
    print("[6] Décodage METAR brut")
    extras = _decoder_metar_brut("LFPM 150530Z AUTO 33004KT 7000 NSC 05/05 Q1004")
    txt = "\n".join(extras)
    assert "automatique" in txt, f"AUTO non détecté : {txt}"
    assert "QNH" in txt and "1004" in txt, f"QNH non détecté : {txt}"
    print("    OK")

    # Test 7 : décodage phénomène
    print("[7] Décodage phénomènes")
    assert _decoder_token_phenomene("-RA") == "faible pluie"
    assert _decoder_token_phenomene("+TSRA") == "forte orage avec pluie"
    assert _decoder_token_phenomene("BR") == "brume"
    assert _decoder_token_phenomene("VCSH") == "à proximité averse de"
    print("    OK")

    # Test 8 : robustesse (action inconnue)
    print("[8] Robustesse action inconnue")
    md, w = execute_action("inconnue", options={"session_vars": {}})
    assert "Action inconnue" in md, "message d'erreur attendu"
    print("    OK")

    print(f"\n=== {'TOUS LES TESTS PASSENT' if not erreurs else f'{erreurs} ÉCHEC(S)'} ===")
    return 0 if not erreurs else 1


if __name__ == "__main__":
    import sys
    sys.exit(_autotest())
