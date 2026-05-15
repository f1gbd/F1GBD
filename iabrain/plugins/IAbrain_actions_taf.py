# -*- coding: utf-8 -*-
"""IAbrain_actions_taf.py — Plugin de récupération et décodage TAF.

Récupère et décode en français clair les prévisions météorologiques
aéronautiques (Terminal Aerodrome Forecast) depuis le serveur NOAA :
    https://tgftp.nws.noaa.gov/data/forecasts/taf/stations/{OACI}.TXT

═══════════════════════════════════════════════════════════════════════════
QU'EST-CE QU'UN TAF ?
═══════════════════════════════════════════════════════════════════════════

Le TAF est la PRÉVISION officielle émise par le service météo national
(Météo France pour la France) pour un aérodrome. Contrairement au METAR
qui décrit les conditions actuelles, le TAF prévoit l'évolution sur :
    - 9 heures (TAF court, aérodromes secondaires)
    - 24 ou 30 heures (TAF long, grands aérodromes)

Le TAF est émis toutes les 6 heures (00, 06, 12, 18 UTC) et amendé
en cas d'évolution significative imprévue.

Structure typique :
    TAF LFPG 150500Z 1506/1612 27010KT CAVOK
        BECMG 1512/1514 24015G25KT
        TEMPO 1518/1522 -SHRA BKN020TCU
        PROB30 1520/1523 TSRA BKN015CB

Lecture :
    - 1506/1612 : valide du 15 à 06h UTC au 16 à 12h UTC
    - Conditions de base : vent W 10 kt, CAVOK
    - BECMG : changement progressif entre 15h et 17h vers vent SW 15 G 25
    - TEMPO : conditions temporaires (< 1h) entre 18h et 22h
    - PROB30 : probabilité 30% d'orages avec pluie entre 20h et 23h

═══════════════════════════════════════════════════════════════════════════
ACTIONS EXPOSÉES (v1.0)
═══════════════════════════════════════════════════════════════════════════

  taf_fetch              Récupère le TAF de la station définie par
                         {TAF_STATION} ou {METAR_STATION} ou défaut LFPM.
  taf_LFXX (~110 entrées) Une action par aérodrome français diffusé NOAA.

═══════════════════════════════════════════════════════════════════════════
VARIABLES DE SESSION
═══════════════════════════════════════════════════════════════════════════

Lues :
    TAF_STATION       code OACI 4 lettres (priorité 1).
    METAR_STATION     fallback si TAF_STATION absent (cohérence avec le
                      plugin METAR : on prévoit pour la même station).

Écrites :
    TAF_RAW           prévision TAF brute multilignes.
    TAF_STATION       OACI effectivement utilisé.

═══════════════════════════════════════════════════════════════════════════
F1GBD - ADRASEC 77 / FNRASEC — Usage formation
"""

from __future__ import annotations

import re
import urllib.request
import urllib.error
from typing import Any, List, Optional, Sequence, Tuple

__version__ = "1.0.1"

# ---------------------------------------------------------------------------
# 1. Identifiants des actions exposées
# ---------------------------------------------------------------------------

ACTION_TAF_FETCH = "taf_fetch"
_ACTIONS_GENERIQUES = {ACTION_TAF_FETCH}

# Deux URLs : TAF long (24-30h, grands aérodromes) et TAF court (9h,
# aérodromes secondaires). On essaie le long d'abord, puis le court en
# fallback automatique avant de rendre un 404.
_TAF_URL_LONG = "https://tgftp.nws.noaa.gov/data/forecasts/taf/stations/{}.TXT"
_TAF_URL_SHORT = "https://tgftp.nws.noaa.gov/data/forecasts/shorttaf/stations/{}.TXT"
_TAF_URL = _TAF_URL_LONG  # alias historique pour les messages d'erreur
_HTTP_TIMEOUT = 8
_USER_AGENT = "IAbrain-TAF-plugin/1.0 (ADRASEC 77 FNRASEC)"

_OACI_RE = re.compile(r"^[A-Z]{4}$")

# ---------------------------------------------------------------------------
# 2. Table des aérodromes français (mêmes 110 stations que le plugin METAR)
# ---------------------------------------------------------------------------

_AERODROMES_FR: List[Tuple[str, str]] = [
    ("LFAC", "Calais Dunkerque (62)"),
    ("LFAQ", "Albert Picardie (80)"),
    ("LFAT", "Le Touquet Paris-Plage (62)"),
    ("LFBA", "Agen La Garenne (47)"),
    ("LFBC", "Cazaux (33, militaire)"),
    ("LFBD", "Bordeaux Mérignac (33)"),
    ("LFBE", "Bergerac Roumanière (24)"),
    ("LFBF", "Toulouse Francazal (31, militaire)"),
    ("LFBG", "Cognac Châteaubernard (16, militaire)"),
    ("LFBH", "La Rochelle Île-de-Ré (17)"),
    ("LFBI", "Poitiers Biard (86)"),
    ("LFBL", "Limoges Bellegarde (87)"),
    ("LFBM", "Mont-de-Marsan (40, militaire)"),
    ("LFBO", "Toulouse Blagnac (31)"),
    ("LFBP", "Pau Pyrénées (64)"),
    ("LFBS", "Biscarrosse Parentis (40)"),
    ("LFBT", "Tarbes Lourdes Pyrénées (65)"),
    ("LFBU", "Angoulême Cognac (16)"),
    ("LFBX", "Périgueux Bassillac (24)"),
    ("LFBY", "Dax Seyresse (40)"),
    ("LFBZ", "Biarritz Pays-Basque (64)"),
    ("LFCK", "Castres Mazamet (81)"),
    ("LFCR", "Rodez Marcillac (12)"),
    ("LFGA", "Colmar Houssen (68)"),
    ("LFGJ", "Dole Tavaux (39)"),
    ("LFHP", "Le Puy Loudes (43)"),
    ("LFJL", "Metz Nancy Lorraine (57)"),
    ("LFJR", "Angers Marcé (49)"),
    ("LFKB", "Bastia Poretta (2B)"),
    ("LFKC", "Calvi Sainte-Catherine (2B)"),
    ("LFKF", "Figari Sud-Corse (2A)"),
    ("LFKJ", "Ajaccio Napoléon Bonaparte (2A)"),
    ("LFKS", "Solenzara (2A, militaire)"),
    ("LFLB", "Chambéry Aix-les-Bains (73)"),
    ("LFLC", "Clermont-Ferrand Auvergne (63)"),
    ("LFLL", "Lyon Saint-Exupéry (69)"),
    ("LFLN", "Saint-Yan (71)"),
    ("LFLP", "Annecy Mont-Blanc (74)"),
    ("LFLS", "Grenoble Isère (38)"),
    ("LFLU", "Valence Chabeuil (26)"),
    ("LFLV", "Vichy Charmeil (03)"),
    ("LFLW", "Aurillac Tronquières (15)"),
    ("LFLX", "Châteauroux Déols (36)"),
    ("LFLY", "Lyon Bron (69)"),
    ("LFMC", "Le Luc Le Cannet (83, militaire)"),
    ("LFMD", "Cannes Mandelieu (06)"),
    ("LFMH", "Saint-Étienne Bouthéon (42)"),
    ("LFMI", "Istres Le Tubé (13, militaire)"),
    ("LFMK", "Carcassonne Salvaza (11)"),
    ("LFML", "Marseille Provence (13)"),
    ("LFMN", "Nice Côte d'Azur (06)"),
    ("LFMO", "Orange Caritat (84, militaire)"),
    ("LFMP", "Perpignan Rivesaltes (66)"),
    ("LFMT", "Montpellier Méditerranée (34)"),
    ("LFMU", "Béziers Vias (34)"),
    ("LFMV", "Avignon Caumont (84)"),
    ("LFMY", "Salon-de-Provence (13, militaire)"),
    ("LFOA", "Avord (18, militaire)"),
    ("LFOB", "Beauvais Tillé (60)"),
    ("LFOE", "Évreux Fauville (27, militaire)"),
    ("LFOH", "Le Havre Octeville (76)"),
    ("LFOJ", "Orléans Bricy (45, militaire)"),
    ("LFOK", "Châlons Vatry (51)"),
    ("LFOP", "Rouen Vallée de Seine (76)"),
    ("LFOT", "Tours Val de Loire (37)"),
    ("LFOV", "Laval Entrammes (53)"),
    ("LFOZ", "Orléans Saint-Denis-de-l'Hôtel (45)"),
    ("LFPB", "Paris Le Bourget (93)"),
    ("LFPG", "Paris Charles de Gaulle / Roissy (95)"),
    ("LFPM", "Melun Villaroche (77) ★ ADRASEC 77"),
    ("LFPN", "Toussus-le-Noble (78)"),
    ("LFPO", "Paris Orly (94)"),
    ("LFPT", "Pontoise Cormeilles-en-Vexin (95)"),
    ("LFPV", "Villacoublay Vélizy (78, militaire)"),
    ("LFQA", "Reims Prunay (51)"),
    ("LFQB", "Troyes Barberey (10)"),
    ("LFQG", "Nevers Fourchambault (58)"),
    ("LFQQ", "Lille Lesquin (59)"),
    ("LFRB", "Brest Bretagne (29)"),
    ("LFRC", "Cherbourg Maupertus (50)"),
    ("LFRD", "Dinard Pleurtuit Saint-Malo (35)"),
    ("LFRG", "Deauville Saint-Gatien (14)"),
    ("LFRH", "Lorient Lann Bihoué (56)"),
    ("LFRI", "La Roche-sur-Yon Les Ajoncs (85)"),
    ("LFRJ", "Landivisiau (29, militaire)"),
    ("LFRK", "Caen Carpiquet (14)"),
    ("LFRL", "Lanvéoc Poulmic (29, militaire)"),
    ("LFRM", "Le Mans Arnage (72)"),
    ("LFRN", "Rennes Saint-Jacques (35)"),
    ("LFRO", "Lannion Côte de Granit (22)"),
    ("LFRQ", "Quimper Pluguffan (29)"),
    ("LFRS", "Nantes Atlantique (44)"),
    ("LFRT", "Saint-Brieuc Armor (22)"),
    ("LFRU", "Morlaix Ploujean (29)"),
    ("LFRV", "Vannes Meucon (56)"),
    ("LFRZ", "Saint-Nazaire Montoir (44)"),
    ("LFSB", "Bâle Mulhouse Fribourg (68, EuroAirport)"),
    ("LFSD", "Dijon Longvic (21)"),
    ("LFSG", "Épinal Mirecourt (88)"),
    ("LFSI", "Saint-Dizier Robinson (52, militaire)"),
    ("LFSL", "Brive Souillac (19)"),
    ("LFSM", "Montbéliard Courcelles (25)"),
    ("LFSN", "Nancy Essey (54)"),
    ("LFSO", "Nancy Ochey (54, militaire)"),
    ("LFST", "Strasbourg Entzheim (67)"),
    ("LFSX", "Luxeuil Saint-Sauveur (70, militaire)"),
    ("LFTH", "Hyères Le Palyvestre (83)"),
    ("LFTW", "Nîmes Garons (30)"),
    ("LFVP", "Saint-Pierre Pointe-Blanche (Saint-Pierre-et-Miquelon)"),
    ("LFYR", "Romorantin Pruniers (41, militaire)"),
]

_ACTION_PREFIX = "taf_"
_ACTIONS_OACI = {f"{_ACTION_PREFIX}{oaci}" for oaci, _ in _AERODROMES_FR}


# ---------------------------------------------------------------------------
# 3. Tables de traduction (reprises du plugin METAR)
# ---------------------------------------------------------------------------

_DIRECTIONS_DEG = [
    (0, "Nord"), (22.5, "Nord-Nord-Est"), (45, "Nord-Est"),
    (67.5, "Est-Nord-Est"), (90, "Est"), (112.5, "Est-Sud-Est"),
    (135, "Sud-Est"), (157.5, "Sud-Sud-Est"), (180, "Sud"),
    (202.5, "Sud-Sud-Ouest"), (225, "Sud-Ouest"), (247.5, "Ouest-Sud-Ouest"),
    (270, "Ouest"), (292.5, "Ouest-Nord-Ouest"), (315, "Nord-Ouest"),
    (337.5, "Nord-Nord-Ouest"),
]


def _direction_fr(degres: int) -> str:
    """Convertit un cap en lettres (Sud-Sud-Ouest etc.)."""
    d = degres % 360
    # On cherche la rose des vents la plus proche
    best = min(_DIRECTIONS_DEG + [(360, "Nord")],
               key=lambda x: abs(x[0] - d))
    return best[1]


_PHENOMENES = {
    "-": "faible ", "+": "forte ", "VC": "à proximité ",
    "MI": "mince ", "PR": "partiel ", "BC": "bancs de ",
    "DR": "chasse-",  "BL": "chasse-soufflée de ",
    "SH": "averse de ", "TS": "orage avec ", "FZ": "verglaçant ",
    "DZ": "bruine", "RA": "pluie", "SN": "neige", "SG": "neige en grains",
    "IC": "cristaux de glace", "PL": "granules de glace",
    "GR": "grêle", "GS": "petite grêle/neige roulée",
    "UP": "précipitation inconnue",
    "BR": "brume", "FG": "brouillard", "FU": "fumée",
    "VA": "cendres volcaniques",
    "DU": "poussière", "SA": "sable", "HZ": "brume sèche", "PY": "embruns",
    "PO": "tourbillons", "SQ": "grain", "FC": "tornade/trombe",
    "SS": "tempête de sable", "DS": "tempête de poussière",
    "NSW": "fin du phénomène significatif",
}

_NUAGES = {
    "SKC": "ciel clair", "CLR": "ciel clair",
    "NSC": "aucun nuage significatif", "NCD": "aucun nuage détecté",
    "FEW": "rares (1-2/8)", "SCT": "épars (3-4/8)",
    "BKN": "fragmentés (5-7/8)", "OVC": "couvert (8/8)",
    "VV":  "ciel invisible",
}

_TYPES_NUAGES = {
    "CB": "cumulonimbus (orageux)",
    "TCU": "cumulus bourgeonnants (instabilité)",
}

# Types de changement TAF
_CHANGE_TYPES = {
    "BECMG": ("BECMG — Changement progressif",
              "Évolution progressive et durable des conditions sur la "
              "période indiquée."),
    "TEMPO": ("TEMPO — Variation temporaire",
              "Variations temporaires de moins d'une heure, totalisant "
              "moins de la moitié de la période indiquée."),
    "FM":    ("FM — Changement rapide (From)",
              "Changement rapide et durable des conditions à l'heure "
              "indiquée."),
    "NOSIG": ("NOSIG — Pas de changement significatif",
              "Aucun changement météorologique significatif attendu dans "
              "les 2 prochaines heures."),
}


# ---------------------------------------------------------------------------
# 4. Helpers session
# ---------------------------------------------------------------------------

def _get_session_vars(options: Any) -> dict:
    if not options or not isinstance(options, dict):
        return {}
    sv = options.get("session_vars")
    return sv if isinstance(sv, dict) else {}


def _get_var(session_vars: dict, name: str) -> str:
    v = session_vars.get(name)
    return str(v).strip() if v is not None else ""


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
# 5. Détermination du code OACI
# ---------------------------------------------------------------------------

def _determiner_oaci(action_id: str, session_vars: dict) -> Tuple[str, str]:
    """Priorité : action native taf_LFXX > TAF_STATION > METAR_STATION > LFPM."""
    if action_id in _ACTIONS_OACI:
        return action_id[len(_ACTION_PREFIX):], f"action native {action_id}"

    # Pour taf_fetch générique : TAF_STATION > METAR_STATION (cohérence
    # avec le plugin METAR pour la même station) > défaut.
    s = _get_var(session_vars, "TAF_STATION").upper()
    if s and _OACI_RE.match(s):
        return s, "variable {TAF_STATION}"

    s = _get_var(session_vars, "METAR_STATION").upper()
    if s and _OACI_RE.match(s):
        return s, "variable {METAR_STATION} (héritée)"

    return "LFPM", "valeur par défaut (Melun, ADRASEC 77)"


# ---------------------------------------------------------------------------
# 6. Téléchargement du fichier TAF
# ---------------------------------------------------------------------------

def _telecharger_taf_url(url: str) -> Tuple[str, str]:
    """Tentative de téléchargement d'une URL TAF spécifique."""
    req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=_HTTP_TIMEOUT) as resp:
            data = resp.read()
        try:
            texte = data.decode("utf-8")
        except UnicodeDecodeError:
            texte = data.decode("latin-1", errors="replace")
        if not texte.strip():
            return "", "réponse vide du serveur NOAA"
        return texte, ""
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return "", "404"  # marqueur pour fallback
        return "", f"erreur HTTP {e.code} : {e.reason}"
    except urllib.error.URLError as e:
        return "", (f"impossible de joindre le serveur NOAA : {e.reason}. "
                    f"Vérifiez votre connexion Internet.")
    except Exception as e:
        return "", f"erreur inattendue : {type(e).__name__} — {e}"


def _telecharger_taf(oaci: str) -> Tuple[str, str, str]:
    """Télécharge le TAF en essayant successivement TAF long puis TAF court.

    Retourne (contenu, erreur, type_taf) où type_taf vaut 'long', 'court'
    ou '' en cas d'échec.
    """
    # 1) TAF long (24-30h, grands aérodromes)
    url_long = _TAF_URL_LONG.format(oaci.upper())
    contenu, erreur = _telecharger_taf_url(url_long)
    if contenu:
        return contenu, "", "long"
    if erreur and erreur != "404":
        # Erreur autre que 404 : on remonte sans tenter le fallback
        return "", erreur, ""

    # 2) Fallback TAF court (9h, aérodromes secondaires)
    url_short = _TAF_URL_SHORT.format(oaci.upper())
    contenu, erreur = _telecharger_taf_url(url_short)
    if contenu:
        return contenu, "", "court"
    if erreur == "404":
        return "", (f"TAF {oaci} introuvable sur le serveur NOAA (HTTP 404 "
                    f"sur le TAF long ET le TAF court). Cette station ne "
                    f"diffuse aucune prévision aérodrome — seuls les "
                    f"terrains avec service météo en publient. Pour la "
                    f"région parisienne, essayez LFPG, LFPO ou LFPB."), ""
    return "", erreur, ""


# ---------------------------------------------------------------------------
# 7. Parsing du TAF brut
# ---------------------------------------------------------------------------

def _nettoyer_taf(texte: str) -> Tuple[str, str]:
    """Sépare l'horodatage de réception (1re ligne) et le corps du TAF.

    Le serveur NOAA renvoie typiquement :
        2026/05/10 03:06
        TAF
              AMD LFBO 100303Z 1003/1106 14010KT CAVOK
              TEMPO 1003/1007 BKN011 ...

    On retourne (horodatage, taf_brut_normalise) où taf_brut_normalise
    est une chaîne unique avec les groupes de changement séparés par \\n.
    """
    lignes = texte.splitlines()
    if not lignes:
        return "", ""

    # 1re ligne : horodatage de réception (peut être absente sur certains feeds)
    horodatage = ""
    idx_debut = 0
    if re.match(r"^\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}", lignes[0]):
        horodatage = lignes[0].strip()
        idx_debut = 1

    # Le reste : on assemble tout, puis on resplit aux mots-clés de groupe
    corps = " ".join(l.strip() for l in lignes[idx_debut:] if l.strip())
    # Le serveur NOAA peut prefixer plusieurs fois "TAF " et/ou "AMD " avant
    # le code OACI (cas observé : "TAF  AMD TAF  AMD LFBO 100303Z ..."). On
    # boucle jusqu'à atteindre un code OACI ou un marqueur de groupe.
    while True:
        prev = corps
        corps = re.sub(r"^(TAF|AMD|COR)\s+", "", corps)
        if corps == prev:
            break

    # Insère un saut de ligne avant chaque mot-clé de groupe de changement,
    # pour faciliter le décodage. PROBxx peut être seul ou suivi de TEMPO.
    corps = re.sub(r"\s+(BECMG|TEMPO|FM|PROB\d{2})\b", r"\n\1", corps)

    return horodatage, corps.strip()


def _parser_periode_validite(s: str) -> Tuple[str, str]:
    """Parse 'DDHH/DDHH' (TAF long) ou 'DDHHHH' (TAF court).

    Retourne (debut, fin) au format 'le JJ à HHhUTC' (utilisable seul) ou
    'du JJ HHhUTC au JJ HHhUTC' via la fonction _formater_intervalle.
    """
    m = re.match(r"^(\d{2})(\d{2})/(\d{2})(\d{2})$", s)
    if m:
        return (f"le {m.group(1)} à {m.group(2)}h UTC",
                f"le {m.group(3)} à {m.group(4)}h UTC")
    return s, ""


def _formater_intervalle(debut: str, fin: str) -> str:
    """'le 10 à 03h UTC' + 'le 10 à 07h UTC' -> 'du 10 à 03h au 10 à 07h UTC'."""
    if not debut or not fin:
        return debut or fin
    # On retire "le " en début et "UTC" en fin de chacun pour reformer.
    deb_clean = debut.replace("le ", "", 1).replace(" UTC", "")
    fin_clean = fin.replace("le ", "", 1).replace(" UTC", "")
    return f"du {deb_clean} au {fin_clean} UTC"


def _parser_vent(token: str) -> str:
    """Parse un groupe vent METAR/TAF : DDDFFKT, DDDFFGggKT, VRBffKT."""
    # VRB05KT, VRB15G25KT
    m = re.match(r"^VRB(\d{2,3})(?:G(\d{2,3}))?KT$", token)
    if m:
        kt = int(m.group(1))
        kmh = round(kt * 1.852)
        out = f"vent **variable** à {kt} kt ({kmh} km/h)"
        if m.group(2):
            kt_g = int(m.group(2))
            kmh_g = round(kt_g * 1.852)
            out += f", **rafales** à {kt_g} kt ({kmh_g} km/h)"
        return out

    # 27010KT, 33010G25KT
    m = re.match(r"^(\d{3})(\d{2,3})(?:G(\d{2,3}))?KT$", token)
    if m:
        deg = int(m.group(1))
        kt = int(m.group(2))
        kmh = round(kt * 1.852)
        if kt == 0:
            return "vent **calme**"
        dir_fr = _direction_fr(deg)
        out = f"vent du **{dir_fr}** ({deg:03d}°) à {kt} kt ({kmh} km/h)"
        if m.group(3):
            kt_g = int(m.group(3))
            kmh_g = round(kt_g * 1.852)
            out += f", **rafales** à {kt_g} kt ({kmh_g} km/h)"
        return out

    return ""


def _parser_visibilite(token: str) -> str:
    """Parse visibilité TAF : 9999, 5000, CAVOK."""
    if token == "CAVOK":
        return ("**CAVOK** (visibilité ≥ 10 km, aucun nuage sous 5000 ft, "
                "aucun phénomène significatif — conditions excellentes)")
    if token == "9999":
        return "visibilité ≥ **10 km**"
    m = re.match(r"^(\d{4})$", token)
    if m:
        v = int(m.group(1))
        if 0 <= v <= 9000:
            km = v / 1000
            return f"visibilité **{v} m** ({km:.1f} km)"
    return ""


def _parser_nuages(token: str) -> str:
    """Parse couche nuageuse : FEW030, BKN040CB, VV001."""
    m = re.match(r"^(FEW|SCT|BKN|OVC|VV)(\d{3})(CB|TCU)?$", token)
    if not m:
        return ""
    type_n, alt_cent, suff = m.groups()
    alt_ft = int(alt_cent) * 100
    alt_m = round(alt_ft * 0.3048)
    libelle = _NUAGES.get(type_n, type_n)
    out = f"{libelle} à {alt_ft} ft (~{alt_m} m)"
    if suff:
        out += f" — **{_TYPES_NUAGES.get(suff, suff)}**"
    return out


def _parser_phenomene(token: str) -> str:
    """Parse un groupe météo significative : -SHRA, +TSRAGR, BR, VCSH..."""
    if token in ("NSW", "NSC", "CAVOK"):
        return ""
    t = token
    parts = []
    prefix = ""  # intensité/proximité (espace de fin déjà inclus)

    if t.startswith("-"):
        prefix = _PHENOMENES["-"]; t = t[1:]
    elif t.startswith("+"):
        prefix = _PHENOMENES["+"]; t = t[1:]
    elif t.startswith("VC"):
        prefix = _PHENOMENES["VC"]; t = t[2:]

    elements = re.findall(r"[A-Z]{2}", t)
    if not elements or any(e not in _PHENOMENES for e in elements):
        return ""

    # Séparation des codes en : descripteurs (qui se collent au suivant)
    # et phénomènes (qui se chaînent avec ' et '). Ex. TSRAGR =
    # TS (descripteur "orage avec ") + RA (pluie) + GR (grêle)
    # -> "orage avec pluie et grêle".
    descripteurs = {"MI", "PR", "BC", "DR", "BL", "SH", "TS", "FZ"}
    phen_decodes = []
    desc_courant = ""
    for e in elements:
        if e in descripteurs:
            desc_courant += _PHENOMENES[e]
        else:
            phen_decodes.append(desc_courant + _PHENOMENES[e])
            desc_courant = ""
    if desc_courant:
        # Descripteur sans phénomène (rare : ex. SH seul, ignoré)
        phen_decodes.append(desc_courant.strip())

    return (prefix + " et ".join(phen_decodes)).strip()


def _decoder_groupe(groupe: str) -> dict:
    """Décode un groupe TAF (ligne de base ou de changement).

    Retourne un dict avec les clés trouvées : type, periode, vent, visi,
    phenomenes (list), nuages (list), tokens_bruts.
    """
    tokens = groupe.split()
    res = {
        "type": "BASE",
        "periode_debut": "",
        "periode_fin": "",
        "proba": None,
        "vent": "",
        "visi": "",
        "phenomenes": [],
        "nuages": [],
        "tokens_bruts": list(tokens),
        "oaci": "",
        "emission": "",
    }
    if not tokens:
        return res

    i = 0

    # Type de groupe + probabilité éventuelle
    if tokens[0] in ("BECMG", "TEMPO", "FM", "NOSIG"):
        res["type"] = tokens[0]
        i = 1
    elif tokens[0].startswith("PROB"):
        m = re.match(r"^PROB(\d{2})$", tokens[0])
        if m:
            res["proba"] = int(m.group(1))
            i = 1
            # PROB suivi parfois de TEMPO/BECMG
            if i < len(tokens) and tokens[i] in ("TEMPO", "BECMG"):
                res["type"] = tokens[i]
                i += 1
            else:
                res["type"] = "PROB"
    elif _OACI_RE.match(tokens[0]):
        # 1re ligne : "LFBO 100303Z 1003/1106 ..."
        res["oaci"] = tokens[0]
        i = 1
        if i < len(tokens) and re.match(r"^\d{6}Z$", tokens[i]):
            jj, hh, mm = tokens[i][0:2], tokens[i][2:4], tokens[i][4:6]
            res["emission"] = f"émis le {jj} à {hh}h{mm} UTC"
            i += 1

    # Période de validité (DDHH/DDHH) ou heure FM (DDHHMM)
    if i < len(tokens):
        if re.match(r"^\d{4}/\d{4}$", tokens[i]):
            res["periode_debut"], res["periode_fin"] = \
                _parser_periode_validite(tokens[i])
            i += 1
        elif res["type"] == "FM" and re.match(r"^\d{6}$", tokens[i]):
            jj, hh, mm = tokens[i][0:2], tokens[i][2:4], tokens[i][4:6]
            res["periode_debut"] = f"à partir du {jj} à {hh}h{mm} UTC"
            i += 1

    # Tokens suivants : vent, visibilité, phénomènes, nuages
    while i < len(tokens):
        t = tokens[i]

        # Vent
        vent = _parser_vent(t)
        if vent:
            res["vent"] = vent
            i += 1
            continue

        # Visibilité / CAVOK
        visi = _parser_visibilite(t)
        if visi:
            res["visi"] = visi
            i += 1
            continue

        # Nuages
        nuage = _parser_nuages(t)
        if nuage:
            res["nuages"].append(nuage)
            i += 1
            continue

        # Phénomène (météo significative)
        phen = _parser_phenomene(t)
        if phen:
            res["phenomenes"].append(phen)
            i += 1
            continue

        # NSC / NSW / SKC / NCD / CLR : indicateurs ciel propre
        if t in ("NSC", "SKC", "NCD", "CLR"):
            res["nuages"].append(_NUAGES.get(t, t))
            i += 1
            continue
        if t == "NSW":
            res["phenomenes"].append(_PHENOMENES["NSW"])
            i += 1
            continue

        # Token inconnu : ignoré
        i += 1

    return res


def _parser_taf_complet(corps: str) -> List[dict]:
    """Découpe le TAF en groupes et décode chacun."""
    groupes = []
    for ligne in corps.split("\n"):
        ligne = ligne.strip()
        if ligne:
            groupes.append(_decoder_groupe(ligne))
    return groupes


# ---------------------------------------------------------------------------
# 8. Rendu Markdown
# ---------------------------------------------------------------------------

def _rendre_groupe(g: dict, est_premier: bool) -> List[str]:
    """Produit les lignes Markdown pour un groupe décodé."""
    out: List[str] = []
    type_g = g["type"]

    # En-tête de groupe
    if est_premier:
        titre = "### 🛫 Conditions de base prévues"
        if g.get("emission"):
            titre += f" *(prévision {g['emission']})*"
        out.append(titre)
        if g["periode_debut"] and g["periode_fin"]:
            intervalle = _formater_intervalle(g["periode_debut"],
                                              g["periode_fin"])
            out.append(f"**Période de validité** : {intervalle}.")
        out.append("")
    else:
        label, definition = _CHANGE_TYPES.get(
            type_g, (type_g, "Groupe de changement.")
        )
        proba_txt = ""
        if g.get("proba"):
            proba_txt = f" — probabilité **{g['proba']}%**"
        out.append(f"#### 🔀 {label}{proba_txt}")
        if g["periode_debut"]:
            if g["periode_fin"]:
                intervalle = _formater_intervalle(g["periode_debut"],
                                                  g["periode_fin"])
                out.append(f"*{intervalle}.*")
            else:
                out.append(f"*{g['periode_debut']}.*")
        out.append(f"*{definition}*")
        out.append("")

    # Contenu météo du groupe
    if g["vent"]:
        out.append(f"- **Vent** : {g['vent']}.")
    if g["visi"]:
        out.append(f"- **Visibilité** : {g['visi']}.")
    if g["phenomenes"]:
        out.append("- **Phénomènes** : " +
                   ", ".join(f"*{p}*" for p in g["phenomenes"]) + ".")
    if g["nuages"]:
        out.append("- **Nuages** :")
        for n in g["nuages"]:
            out.append(f"    - {n}")

    out.append("")
    return out


def _rendre_taf(oaci: str, source: str, contenu_brut: str,
                type_taf: str, options: Any) -> Tuple[str, List[str]]:
    """Parse + rend le TAF. Retourne (markdown, warnings).

    type_taf : 'long' (24-30h) ou 'court' (9h).
    """
    warnings: List[str] = []

    horodatage, corps = _nettoyer_taf(contenu_brut)
    if not corps:
        warnings.append(f"TAF {oaci} vide ou non parsable")
        return (f"## ⚠️ TAF {oaci} reçu mais illisible\n\n"
                f"```\n{contenu_brut}\n```", warnings)

    # Récupération du nom de la station depuis la table interne
    nom_station = "station inconnue"
    for code, nom in _AERODROMES_FR:
        if code == oaci:
            nom_station = nom
            break

    # Stockage TAF brut en session (multilignes -> espace pour /set compat)
    taf_brut_oneline = corps.replace("\n", " ")
    if _set_session_var(options, "TAF_RAW", taf_brut_oneline):
        stockage_md = "✅ Variable `{TAF_RAW}` stockée en session."
    else:
        stockage_md = (f"ℹ️ Pour mémoriser le TAF brut, copiez :\n"
                       f"`/set TAF_RAW={taf_brut_oneline}`")
    _set_session_var(options, "TAF_STATION", oaci)
    _set_session_var(options, "TAF_TYPE", type_taf)

    # Décodage des groupes
    groupes = _parser_taf_complet(corps)
    if not groupes:
        warnings.append("aucun groupe TAF identifié")
        return (f"## ⚠️ TAF {oaci} non décodable\n\n```\n{corps}\n```",
                warnings)

    # Libellé du type de TAF
    type_libelle = {
        "long":  "TAF long (validité 24 à 30 heures)",
        "court": "TAF court (validité 9 heures) — *fallback automatique, "
                 "le TAF long n'est pas disponible pour cette station*",
    }.get(type_taf, f"TAF type={type_taf}")

    # Construction du Markdown
    md_lignes = [
        f"## 🌤️ TAF {oaci} — {nom_station}",
        "",
        f"**Source** : {source}.",
        f"**Type** : {type_libelle}.",
    ]
    if horodatage:
        md_lignes.append(f"**Réception** : {horodatage} UTC.")
    md_lignes.append("")
    md_lignes.append(
        "> 📘 Le **TAF** (*Terminal Aerodrome Forecast*) est la prévision "
        "officielle Météo France émise pour cet aérodrome."
    )
    md_lignes.append("")

    for idx, g in enumerate(groupes):
        md_lignes.extend(_rendre_groupe(g, est_premier=(idx == 0)))

    # Bloc TAF brut
    md_lignes.append("### 📡 TAF brut (transmission OACI)")
    md_lignes.append("")
    md_lignes.append("```")
    md_lignes.append(corps)
    md_lignes.append("```")
    md_lignes.append("")
    md_lignes.append(stockage_md)
    md_lignes.append("")
    url_used = _TAF_URL_SHORT if type_taf == "court" else _TAF_URL_LONG
    md_lignes.append(f"*Source : NOAA / NWS — {url_used.format(oaci)}*")

    return "\n".join(md_lignes), warnings


# ---------------------------------------------------------------------------
# 9. Action principale
# ---------------------------------------------------------------------------

def _action_taf_fetch(action_id: str, session_vars: dict,
                      options: Any) -> Tuple[str, List[str]]:
    warnings: List[str] = []
    oaci, source = _determiner_oaci(action_id, session_vars)

    contenu, erreur, type_taf = _telecharger_taf(oaci)
    if erreur:
        md = (
            f"## ❌ Erreur récupération TAF — {oaci}\n\n"
            f"**Station demandée** : `{oaci}` *(source : {source})*\n\n"
            f"**Cause** : {erreur}\n\n"
            f"---\n\n"
            f"**À noter** : tous les aérodromes ne diffusent pas de TAF. "
            f"Seuls les terrains avec service météo (généralement avec "
            f"contrôle aérien) en publient. Les petits aérodromes "
            f"n'auront que des METAR.\n\n"
            f"URLs interrogées :\n"
            f"- TAF long : {_TAF_URL_LONG.format(oaci)}\n"
            f"- TAF court : {_TAF_URL_SHORT.format(oaci)}"
        )
        warnings.append(f"TAF {oaci} : {erreur}")
        return md, warnings

    md, w = _rendre_taf(oaci, source, contenu, type_taf, options)
    warnings.extend(w)
    return md, warnings


# ---------------------------------------------------------------------------
# 10. Point d'entrée IAbrain (contrat d'interface)
# ---------------------------------------------------------------------------

def is_action(action_id: str) -> bool:
    aid = (action_id or "").strip()
    return aid in _ACTIONS_GENERIQUES or aid in _ACTIONS_OACI


def list_actions() -> List[Tuple[str, str, str]]:
    """Déclare 1 action générique + 1 par aérodrome français."""
    actions: List[Tuple[str, str, str]] = [
        (
            ACTION_TAF_FETCH,
            "TAF — Récupérer la prévision (variable {TAF_STATION})",
            "Télécharge et décode en français clair la prévision "
            "aéronautique TAF (Terminal Aerodrome Forecast) de la station "
            "définie par {TAF_STATION}, à défaut {METAR_STATION}, à défaut "
            "LFPM (Melun). Le TAF est la prévision OFFICIELLE Météo France "
            "valable 9 à 30 heures. Stocke le TAF brut dans {TAF_RAW}."
        ),
    ]
    for oaci, nom in _AERODROMES_FR:
        actions.append((
            f"{_ACTION_PREFIX}{oaci}",
            f"TAF — {oaci} ({nom})",
            f"Télécharge la prévision TAF officielle pour la station "
            f"{oaci} ({nom}) directement, sans variable de session. "
            f"Source : NOAA / NWS. Note : tous les aérodromes ne diffusent "
            f"pas de TAF — seuls ceux avec service météo (généralement "
            f"contrôlés). En cas de 404, basculer sur le METAR."
        ))
    return actions


def execute_action(action_id: str,
                   imported_files: Sequence[Tuple[str, str]] = (),
                   options: Any = None) -> Tuple[str, List[str]]:
    aid = (action_id or "").strip()
    session_vars = _get_session_vars(options)

    try:
        if aid in _ACTIONS_GENERIQUES or aid in _ACTIONS_OACI:
            return _action_taf_fetch(aid, session_vars, options)
    except Exception as e:
        return (
            f"## ❌ Erreur interne du plugin TAF\n\n"
            f"`{type(e).__name__}` : {e}\n\n"
            f"Action : `{aid}`",
            [f"plugin TAF : exception {type(e).__name__}"],
        )

    return f"## ❌ Action inconnue : `{aid}`", []


# ---------------------------------------------------------------------------
# 11. Autotest local
# ---------------------------------------------------------------------------

def _autotest() -> int:
    print(f"=== Autotest IAbrain_actions_taf v{__version__} ===\n")
    erreurs = 0

    # Test 1 : contrat d'interface
    print("[1] Contrat d'interface")
    actions = list_actions()
    print(f"    Actions exposées : {len(actions)} "
          f"(1 générique + {len(_AERODROMES_FR)} aérodromes)")
    assert len(actions) == 1 + len(_AERODROMES_FR)
    for a in actions:
        assert len(a) == 3
    assert is_action("taf_fetch")
    assert is_action("taf_LFPG")
    assert is_action("taf_LFPM")
    assert not is_action("metar_LFPG")
    print("    OK")

    # Test 2 : résolution OACI depuis action native
    print("[2] Résolution OACI — action native prioritaire")
    oaci, src = _determiner_oaci("taf_LFPG", {"TAF_STATION": "LFPM"})
    assert oaci == "LFPG", f"action native doit primer, obtenu {oaci}"
    print(f"    OK : taf_LFPG -> {oaci} ({src})")

    # Test 3 : fallback sur METAR_STATION
    print("[3] Fallback METAR_STATION quand TAF_STATION absent")
    oaci, src = _determiner_oaci("taf_fetch", {"METAR_STATION": "LFBO"})
    assert oaci == "LFBO", f"fallback METAR_STATION attendu, obtenu {oaci}"
    print(f"    OK : taf_fetch + METAR_STATION=LFBO -> {oaci} ({src})")

    # Test 4 : nettoyage du flux NOAA (échantillon réel LFBO)
    print("[4] Nettoyage flux NOAA")
    echantillon = (
        "2026/05/10 03:06\n"
        "TAF \n"
        "      AMD TAF \n"
        "      AMD LFBO 100303Z 1003/1106 14010KT CAVOK \n"
        "      TEMPO 1003/1007 BKN011 PROB30 \n"
        "      TEMPO 1003/1006 BKN009 \n"
        "      BECMG 1010/1012 VRB03KT \n"
        "      TEMPO 1013/1020 33010KT -SHRA SCT035TCU BKN050 PROB40 \n"
        "      TEMPO 1014/1019 VRB15G25KT 4000 TSRA SCT040CB PROB30 \n"
        "      TEMPO 1015/1018 29025G45KT 2000 TSRAGR BKN025CB PROB30 \n"
        "      TEMPO 1100/1106 4000 BR\n"
    )
    horo, corps = _nettoyer_taf(echantillon)
    assert horo.startswith("2026/05/10"), f"horodatage : {horo}"
    assert corps.startswith("LFBO 100303Z"), f"corps mal nettoyé : {corps[:50]}"
    lignes = corps.split("\n")
    print(f"    OK : horodatage={horo}, {len(lignes)} groupes identifiés")

    # Test 5 : décodage de la ligne de base
    print("[5] Décodage ligne de base LFBO")
    g_base = _decoder_groupe(lignes[0])
    assert g_base["oaci"] == "LFBO"
    assert "14010KT" in g_base["tokens_bruts"]
    assert "Sud-Est" in g_base["vent"], f"vent mal décodé : {g_base['vent']}"
    assert "CAVOK" in g_base["visi"], f"CAVOK manqué : {g_base['visi']}"
    print(f"    OK : OACI={g_base['oaci']}, vent='{g_base['vent']}'")

    # Test 6 : décodage groupe TEMPO avec phénomène complexe (TSRAGR)
    print("[6] Décodage groupe TEMPO avec TSRAGR + CB")
    # On cherche la ligne avec "TSRAGR"
    ligne_grele = [l for l in lignes if "TSRAGR" in l][0]
    g = _decoder_groupe(ligne_grele)
    assert g["type"] == "TEMPO", f"type={g['type']}"
    txt_phen = " ".join(g["phenomenes"])
    assert "orage" in txt_phen and "grêle" in txt_phen, f"phen : {txt_phen}"
    txt_nuages = " ".join(g["nuages"])
    assert "cumulonimbus" in txt_nuages.lower(), f"nuages : {txt_nuages}"
    print(f"    OK : TEMPO avec TSRAGR -> '{txt_phen}'")

    # Test 7 : décodage groupe PROB suivi de TEMPO/BECMG
    print("[7] Décodage groupe PROB")
    g_prob = _decoder_groupe("PROB30 TEMPO 1518/1522 -SHRA")
    assert g_prob["proba"] == 30
    assert g_prob["type"] == "TEMPO"
    print(f"    OK : PROB30 TEMPO -> proba={g_prob['proba']}")

    # Test 8 : vent variable VRB15G25KT
    print("[8] Vent variable avec rafales")
    v = _parser_vent("VRB15G25KT")
    assert "variable" in v and "rafales" in v
    print(f"    OK : VRB15G25KT -> '{v}'")

    # Test 9 : direction du vent (rose des vents)
    print("[9] Rose des vents")
    cas = [(0, "Nord"), (90, "Est"), (180, "Sud"), (270, "Ouest"),
           (45, "Nord-Est"), (225, "Sud-Ouest"), (340, "Nord-Nord-Ouest")]
    for deg, attendu in cas:
        obtenu = _direction_fr(deg)
        assert obtenu == attendu, f"{deg}° -> {obtenu} (attendu {attendu})"
    print("    OK")

    # Test 10 : période de validité
    print("[10] Période de validité")
    deb, fin = _parser_periode_validite("1506/1612")
    assert "15" in deb and "06h" in deb
    assert "16" in fin and "12h" in fin
    print(f"    OK : 1506/1612 -> {deb} → {fin}")

    # Test 11 : rendu complet du TAF échantillon
    print("[11] Rendu complet TAF LFBO échantillon")
    md, w = _rendre_taf("LFBO", "test", echantillon, "long", options={})
    assert "TAF LFBO" in md
    assert "Toulouse Blagnac" in md, "nom de station absent"
    assert "TEMPO" in md and "BECMG" in md
    assert "orage" in md.lower()
    assert "cumulonimbus" in md.lower()
    print(f"    OK ({len(md)} caractères, {md.count(chr(10))} lignes)")

    # Test 12 : robustesse — station qui ne diffuse pas de TAF (mock 404)
    print("[12] Action sur station inexistante (gestion d'erreur)")
    # On simule un OACI bidon
    md, w = execute_action("taf_LFXX", options={"session_vars": {}})
    # taf_LFXX n'est pas dans _ACTIONS_OACI, donc "Action inconnue"
    assert "inconnue" in md.lower()
    print("    OK : action inconnue gérée proprement")

    print(f"\n=== {'TOUS LES TESTS PASSENT' if not erreurs else f'{erreurs} ÉCHEC(S)'} ===")
    return 0 if not erreurs else 1


if __name__ == "__main__":
    import sys
    sys.exit(_autotest())
