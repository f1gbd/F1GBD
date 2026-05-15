# -*- coding: utf-8 -*-
"""IAbrain_actions_metar.py — Plugin de récupération et décodage METAR.

v1.2 — Exposition d'une action native par aérodrome français (LF*).

Permet à l'opérateur ADRASEC de sélectionner directement l'aérodrome
souhaité dans le dropdown du dialog d'édition de macro, sans passer
par la variable {METAR_STATION}.

═══════════════════════════════════════════════════════════════════════════
ACTIONS EXPOSÉES (v1.2)
═══════════════════════════════════════════════════════════════════════════

  metar_fetch                Récupère le METAR selon {METAR_STATION} ou
                             défaut LFPM (Melun).
  metar_vocal                Récupère le METAR depuis une demande vocale
                             transcrite par Vosk (alphabet OTAN / ville).
  metar_LFXX  (~110 entrées) Une action native par aérodrome français
                             effectivement diffusé sur le serveur NOAA,
                             directement sélectionnable dans le dropdown.

═══════════════════════════════════════════════════════════════════════════
F1GBD - ADRASEC 77 / FNRASEC — Usage formation
"""

from __future__ import annotations

import re
import unicodedata
import urllib.request
import urllib.error
from typing import Any, List, Optional, Sequence, Tuple

__version__ = "1.2.0"

# ---------------------------------------------------------------------------
# 1. Identifiants des actions exposées
# ---------------------------------------------------------------------------

ACTION_METAR_FETCH = "metar_fetch"
ACTION_METAR_VOCAL = "metar_vocal"
_ACTIONS_GENERIQUES = {ACTION_METAR_FETCH, ACTION_METAR_VOCAL}

# URL de base des METAR décodés NOAA
_METAR_URL = "https://tgftp.nws.noaa.gov/data/observations/metar/decoded/{}.TXT"
_HTTP_TIMEOUT = 8
_USER_AGENT = "IAbrain-METAR-plugin/1.2 (ADRASEC 77 FNRASEC)"

# Regex code OACI (4 lettres majuscules)
_OACI_RE = re.compile(r"^[A-Z]{4}$")

# ---------------------------------------------------------------------------
# 2. Table des aérodromes français diffusés NOAA (v1.2)
# ---------------------------------------------------------------------------
#
# Liste des 110 stations LF* effectivement diffusées sur tgftp.nws.noaa.gov
# (état au 15 mai 2026). Les stations obsolètes (dernière MAJ > 2 ans) sont
# exclues. Format : (OACI, "Aérodrome — Ville (dept)").
#
# Note ADRASEC 77 : LFPM (Melun) est la station de référence par défaut.
# ---------------------------------------------------------------------------

_AERODROMES_FR: List[Tuple[str, str]] = [
    # ── A : Nord & Picardie ──
    ("LFAC", "Calais Dunkerque (62)"),
    ("LFAQ", "Albert Picardie (80)"),
    ("LFAT", "Le Touquet Paris-Plage (62)"),

    # ── B : Sud-Ouest (Aquitaine, Midi-Pyrénées, Limousin) ──
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

    # ── C : Sud (Toulouse Lasbordes, Rodez...) ──
    ("LFCK", "Castres Mazamet (81)"),
    ("LFCR", "Rodez Marcillac (12)"),

    # ── G : Alsace, Bourgogne, Jura ──
    ("LFGA", "Colmar Houssen (68)"),
    ("LFGJ", "Dole Tavaux (39)"),

    # ── H : Auvergne (Le Puy) ──
    ("LFHP", "Le Puy Loudes (43)"),

    # ── J : Lorraine, Jura ──
    ("LFJL", "Metz Nancy Lorraine (57)"),
    ("LFJR", "Angers Marcé (49)"),

    # ── K : Corse ──
    ("LFKB", "Bastia Poretta (2B)"),
    ("LFKC", "Calvi Sainte-Catherine (2B)"),
    ("LFKF", "Figari Sud-Corse (2A)"),
    ("LFKJ", "Ajaccio Napoléon Bonaparte (2A)"),
    ("LFKS", "Solenzara (2A, militaire)"),

    # ── L : Rhône-Alpes, Auvergne ──
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

    # ── M : Provence-Alpes-Côte d'Azur, Languedoc ──
    ("LFMC", "Le Luc Le Cannet (83, militaire)"),
    ("LFMD", "Cannes Mandelieu (06)"),
    ("LFMH", "Saint-Étienne Bouthéon (42)"),
    ("LFMI", "Istres Le Tubé (13, militaire)"),
    ("LFMK", "Carcassonne Salvaza (11)"),
    ("LFML", "Marseille Provence (13)"),
    ("LFMO", "Orange Caritat (84, militaire)"),
    ("LFMP", "Perpignan Rivesaltes (66)"),
    ("LFMT", "Montpellier Méditerranée (34)"),
    ("LFMU", "Béziers Vias (34)"),
    ("LFMV", "Avignon Caumont (84)"),
    ("LFMY", "Salon-de-Provence (13, militaire)"),
    ("LFMN", "Nice Côte d'Azur (06)"),

    # ── O : Centre, Normandie, Bourgogne ──
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

    # ── P : Région parisienne (LFP*) — zone ADRASEC 77 ★ ──
    ("LFPB", "Paris Le Bourget (93)"),
    ("LFPG", "Paris Charles de Gaulle / Roissy (95)"),
    ("LFPM", "Melun Villaroche (77) ★ ADRASEC 77"),
    ("LFPN", "Toussus-le-Noble (78)"),
    ("LFPO", "Paris Orly (94)"),
    ("LFPT", "Pontoise Cormeilles-en-Vexin (95)"),
    ("LFPV", "Villacoublay Vélizy (78, militaire)"),

    # ── Q : Champagne-Ardenne, Nord-Pas-de-Calais ──
    ("LFQA", "Reims Prunay (51)"),
    ("LFQB", "Troyes Barberey (10)"),
    ("LFQG", "Nevers Fourchambault (58)"),
    ("LFQQ", "Lille Lesquin (59)"),

    # ── R : Bretagne, Pays de la Loire ──
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

    # ── S : Alsace-Lorraine, Franche-Comté ──
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

    # ── T : Côte d'Azur, Languedoc-Roussillon ──
    ("LFTH", "Hyères Le Palyvestre (83)"),
    ("LFTW", "Nîmes Garons (30)"),

    # ── V : Saint-Pierre-et-Miquelon ──
    ("LFVP", "Saint-Pierre Pointe-Blanche (Saint-Pierre-et-Miquelon)"),

    # ── Y : autres ──
    ("LFYR", "Romorantin Pruniers (41, militaire)"),
]

# Préfixe utilisé pour l'identifiant d'action « par OACI »
_ACTION_PREFIX = "metar_"

# Ensemble des identifiants valides « metar_LFXX » exposés en v1.2
_ACTIONS_OACI = {f"{_ACTION_PREFIX}{oaci}" for oaci, _ in _AERODROMES_FR}


# ---------------------------------------------------------------------------
# 3. Tables de traduction METAR (codes -> français)
# ---------------------------------------------------------------------------

_DIRECTIONS_FR = {
    "N": "Nord",        "NNE": "Nord-Nord-Est",   "NE": "Nord-Est",
    "ENE": "Est-Nord-Est", "E": "Est",            "ESE": "Est-Sud-Est",
    "SE": "Sud-Est",    "SSE": "Sud-Sud-Est",     "S": "Sud",
    "SSW": "Sud-Sud-Ouest", "SW": "Sud-Ouest",    "WSW": "Ouest-Sud-Ouest",
    "W": "Ouest",       "WNW": "Ouest-Nord-Ouest", "NW": "Nord-Ouest",
    "NNW": "Nord-Nord-Ouest",
}

_PHENOMENES = {
    "-": "faible ", "+": "forte ", "VC": "à proximité ",
    "MI": "mince ", "PR": "partiel ", "BC": "bancs de ",
    "DR": "chasse-",  "BL": "chasse-soufflée de ",
    "SH": "averse de ", "TS": "orage avec ", "FZ": "verglaçant ",
    "DZ": "bruine", "RA": "pluie", "SN": "neige", "SG": "neige en grains",
    "IC": "cristaux de glace", "PL": "granules de glace",
    "GR": "grêle", "GS": "petite grêle/neige roulée", "UP": "précipitation inconnue",
    "BR": "brume", "FG": "brouillard", "FU": "fumée", "VA": "cendres volcaniques",
    "DU": "poussière", "SA": "sable", "HZ": "brume sèche",
    "PY": "embruns",
    "PO": "tourbillons de poussière/sable", "SQ": "grain", "FC": "tornade/trombe",
    "SS": "tempête de sable", "DS": "tempête de poussière",
    "NSW": "fin du phénomène significatif",
}

_NUAGES = {
    "SKC": "ciel clair", "CLR": "ciel clair (auto, < 12000 ft)",
    "NSC": "aucun nuage significatif", "NCD": "aucun nuage détecté (auto)",
    "FEW": "rares (1-2/8)", "SCT": "épars (3-4/8)",
    "BKN": "fragmentés (5-7/8)", "OVC": "couvert (8/8)",
    "VV":  "ciel invisible, visibilité verticale",
}

_TYPES_NUAGES = {
    "CB": "cumulonimbus (orageux)",
    "TCU": "cumulus bourgeonnants",
    "CI": "cirrus", "CS": "cirrostratus", "CC": "cirrocumulus",
    "AS": "altostratus", "AC": "altocumulus",
    "NS": "nimbostratus", "SC": "stratocumulus", "ST": "stratus", "CU": "cumulus",
}


# ---------------------------------------------------------------------------
# 4. Module d'extraction phonétique OTAN (v1.1, inchangé)
# ---------------------------------------------------------------------------

_NATO_PHONETIC = {
    "alpha": "A", "alfa": "A", "alfaa": "A",
    "bravo": "B", "bravos": "B",
    "charlie": "C", "charly": "C", "charles": "C", "charli": "C",
    "delta": "D",
    "echo": "E", "écho": "E", "eko": "E", "echos": "E",
    "foxtrot": "F", "fox-trot": "F", "fox trot": "F",
    "fox trotte": "F", "fox trotter": "F", "fox trottez": "F",
    "fox-trotte": "F", "foxtrotte": "F",
    "phoque trot": "F", "phoque trotte": "F",
    "golf": "G", "gholf": "G", "goal": "G", "gulf": "G",
    "hotel": "H", "hôtel": "H", "otel": "H", "hôtels": "H",
    "india": "I", "indien": "I", "indra": "I",
    "juliet": "J", "juliett": "J", "juliette": "J", "juliettes": "J",
    "kilo": "K", "kilos": "K",
    "lima": "L", "limas": "L", "lima bean": "L",
    "mike": "M", "maïque": "M", "maique": "M", "mick": "M", "mike s": "M",
    "november": "N", "novembre": "N", "novembres": "N",
    "oscar": "O", "oskar": "O", "oscars": "O",
    "papa": "P", "papas": "P",
    "quebec": "Q", "québec": "Q", "kebek": "Q", "kebeck": "Q",
    "romeo": "R", "roméo": "R", "roméos": "R",
    "sierra": "S", "siera": "S", "sierras": "S",
    "tango": "T", "tangos": "T",
    "uniform": "U", "uniforme": "U", "uniformes": "U",
    "victor": "V", "viktor": "V", "victors": "V",
    "whiskey": "W", "whisky": "W", "wiski": "W", "wisky": "W", "ouisky": "W",
    "xray": "X", "x-ray": "X", "ixre": "X", "iks ray": "X", "x ray": "X",
    "yankee": "Y", "yanki": "Y", "yankees": "Y", "yanké": "Y",
    "zulu": "Z", "zoulou": "Z", "zoulous": "Z",
}

# Villes/aéroports pour extraction vocale (v1.1). Sous-ensemble lisible
# côté Vosk ; complète la table _AERODROMES_FR plus haut.
_VILLES_OACI = {
    "melun": "LFPM", "melun villaroche": "LFPM",
    "roissy": "LFPG", "roissy charles de gaulle": "LFPG",
    "charles de gaulle": "LFPG", "cdg": "LFPG",
    "orly": "LFPO", "paris orly": "LFPO",
    "le bourget": "LFPB", "bourget": "LFPB",
    "toussus": "LFPN", "toussus le noble": "LFPN",
    "pontoise": "LFPT", "cormeilles": "LFPT",
    "villacoublay": "LFPV",
    "marseille": "LFML", "marseille provence": "LFML",
    "lyon saint exupery": "LFLL", "lyon": "LFLL",
    "lyon bron": "LFLY",
    "nice": "LFMN", "nice cote d azur": "LFMN",
    "toulouse blagnac": "LFBO", "toulouse": "LFBO",
    "bordeaux merignac": "LFBD", "bordeaux": "LFBD",
    "nantes atlantique": "LFRS", "nantes": "LFRS",
    "strasbourg entzheim": "LFST", "strasbourg": "LFST",
    "lille lesquin": "LFQQ", "lille": "LFQQ",
    "rennes saint jacques": "LFRN", "rennes": "LFRN",
    "brest bretagne": "LFRB", "brest": "LFRB",
    "montpellier": "LFMT",
    "biarritz": "LFBZ",
    "pau": "LFBP",
    "clermont ferrand": "LFLC", "clermont": "LFLC",
    "grenoble isere": "LFLS", "grenoble": "LFLS",
    "ajaccio": "LFKJ",
    "bastia": "LFKB",
    "calvi": "LFKC",
    "figari": "LFKF",
    "tours": "LFOT",
    "poitiers": "LFBI",
    "limoges": "LFBL",
    "perpignan": "LFMP",
    "metz nancy": "LFJL", "metz": "LFJL",
    "dijon": "LFSD",
    "reims": "LFQA",
    "rouen": "LFOP",
    "caen carpiquet": "LFRK", "caen": "LFRK",
    "cherbourg": "LFRC",
    "deauville": "LFRG",
    "annecy meythet": "LFLP", "annecy": "LFLP",
    "annecy mont blanc": "LFLP",
    "chambery aix les bains": "LFLB", "chambery": "LFLB",
    "valence": "LFLU",
    "avignon": "LFMV",
    "nimes": "LFTW",
    "beziers": "LFMU",
    "carcassonne": "LFMK",
    "tarbes lourdes": "LFBT", "lourdes": "LFBT",
    "le havre": "LFOH",
    "vatry": "LFOK",
    "bale mulhouse": "LFSB", "mulhouse": "LFSB", "euroairport": "LFSB",
    "colmar": "LFGA",
    "saint pierre miquelon": "LFVP", "saint pierre": "LFVP",
}

_MOTS_FR_4L = {
    "donc", "mais", "avec", "pour", "dans", "sans", "sous", "vers",
    "plus", "tres", "bien", "tout", "tous", "rien", "deja",
    "elle", "nous", "vous", "leur",
    "etre", "fait", "fais", "fera", "faut", "veut", "peut",
    "doit", "voit", "vois", "sait", "sais",
    "beau", "belle", "ciel", "vent", "froid", "chaud",
    "ville", "code", "nord", "midi", "ouest",
    "merci", "salut",
    "meteo", "metar", "noaa", "oaci",
    "donne", "voir", "dire", "lire",
    "site", "page",
    "vosk", "aero",
    "hier", "matin", "soir", "jour", "nuit",
    "exer", "info", "data",
    "stop", "next", "ainsi",
    "moi", "toi", "soi", "lui",
    "trop", "peu",
}

_TRIGGERS_METEO = {
    "metar", "meteo", "meteorologie", "meteorologique",
    "aero", "aeronautique",
    "temps", "observation", "noaa", "station",
    "vent", "visibilite", "pression", "qnh",
    "atis", "taf",
}

_CORRECTIONS_METAR = [
    (re.compile(r"(?i)\b(le|du)\s+tard\b"),       r"\1 metar"),
    (re.compile(r"(?i)\bmes\s+tard\b"),           "metar"),
    (re.compile(r"(?i)\bmé\s*tard\b"),            "metar"),
    (re.compile(r"(?i)\bmétard\b"),               "metar"),
    (re.compile(r"(?i)\bmaitard\b"),              "metar"),
    (re.compile(r"(?i)\bmet\s+art\b"),            "metar"),
    (re.compile(r"(?i)\bmétéo\s+aéro\b"),         "meteo aero"),
    (re.compile(r"(?i)\baéro\s+nautique\b"),      "aeronautique"),
    (re.compile(r"(?i)\bho\s+aci\b"),             "oaci"),
    (re.compile(r"(?i)\boh\s+hassi\b"),           "oaci"),
]

_CONTEXTE_METAR_PRESENT = re.compile(
    r"(?i)\b(metar|meteo|météo|aéro|aero|aeronaut|station|noaa|"
    r"vent|qnh|qfe|tour|piste|pilote|avion|aérodrome|aerodrome|"
    r"lima|foxtrot|kilo|papa|mike|hotel|tango|charlie|delta|bravo|"
    r"juliet|juliette|alpha|oscar|sierra|whiskey|romeo|yankee|"
    r"zulu|november|india|golf|echo|écho|victor|uniform|quebec|"
    r"x-?ray)\b"
)


def _normaliser_texte(s: str) -> str:
    if not s:
        return ""
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.lower()
    s = re.sub(r"[\-_'`.,;:!?]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _pre_corriger_metar(phrase: str) -> str:
    if not phrase:
        return phrase
    if not _CONTEXTE_METAR_PRESENT.search(phrase):
        return phrase
    out = phrase
    for pattern, repl in _CORRECTIONS_METAR:
        out = pattern.sub(repl, out)
    return out


def _detecter_oaci_direct(texte_norm: str) -> str:
    for m in re.finditer(r"\b([a-z]{4})\b", texte_norm):
        candidat = m.group(1)
        if candidat in _MOTS_FR_4L:
            continue
        if candidat[0] in "abcdefghiklmnoprstuvwyz":
            oaci = candidat.upper()
            if _OACI_RE.match(oaci):
                return oaci
    return ""


def _detecter_oaci_phonetique(texte_norm: str) -> Tuple[str, int]:
    mots = texte_norm.split()
    n = len(mots)
    for start in range(n):
        lettres = []
        i = start
        bruits = 0
        while i < n and len(lettres) < 4:
            mot = mots[i]
            consume = 1
            lettre = _NATO_PHONETIC.get(mot)
            if lettre is None and i + 1 < n:
                compose = mot + " " + mots[i + 1]
                if compose in _NATO_PHONETIC:
                    lettre = _NATO_PHONETIC[compose]
                    consume = 2
            if lettre is not None:
                lettres.append(lettre)
                bruits = 0
                i += consume
            else:
                bruits += 1
                if bruits > 2:
                    break
                i += 1
        if len(lettres) == 4:
            oaci = "".join(lettres)
            if _OACI_RE.match(oaci):
                return oaci, i - start
    return "", 0


def _detecter_oaci_ville(texte_norm: str) -> Tuple[str, str]:
    cles_triees = sorted(_VILLES_OACI.keys(), key=len, reverse=True)
    for cle in cles_triees:
        pattern = r"\b" + re.escape(cle) + r"\b"
        if re.search(pattern, texte_norm):
            return _VILLES_OACI[cle], cle
    return "", ""


def extraire_oaci_depuis_phrase(phrase: str) -> Tuple[str, str]:
    """Extrait un code OACI 4 lettres depuis une phrase en français.

    Stratégie en cascade : phonétique OTAN > ville > code direct.
    Retourne (oaci, methode). Fonction publique réutilisable.
    """
    if not phrase:
        return "", ""

    phrase = _pre_corriger_metar(phrase)
    texte_norm = _normaliser_texte(phrase)
    if not texte_norm:
        return "", ""

    oaci, _ = _detecter_oaci_phonetique(texte_norm)
    if oaci:
        return oaci, "phonetique"

    oaci, _ville = _detecter_oaci_ville(texte_norm)
    if oaci:
        return oaci, "ville"

    mots = set(texte_norm.split())
    if mots & _TRIGGERS_METEO:
        oaci = _detecter_oaci_direct(texte_norm)
        if oaci:
            return oaci, "direct"

    return "", ""


# ---------------------------------------------------------------------------
# 5. Helpers session
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
# 6. Détermination du code OACI
# ---------------------------------------------------------------------------

def _extraire_oaci_depuis_action_id(action_id: str) -> str:
    """Cherche un OACI dans l'action_id en respectant la priorité v1.2 :
    si l'action_id est exactement 'metar_LFXX' (action native exposée),
    on extrait LFXX. Sinon match terminal classique.
    """
    if not action_id:
        return ""
    # Priorité v1.2 : action exposée directement
    if action_id in _ACTIONS_OACI:
        return action_id[len(_ACTION_PREFIX):]
    # Match terminal (cas v1.0 : suffixe arbitraire)
    m = re.search(r"[_\-]([A-Za-z]{4})$", action_id)
    if m:
        candidat = m.group(1).upper()
        if _OACI_RE.match(candidat) and candidat not in ("ETCH", "OCAL"):
            return candidat
    return ""


def _determiner_oaci(action_id: str, session_vars: dict) -> Tuple[str, str]:
    """Mode standard : priorité action_id LFXX > METAR_STATION > OACI > LFPM."""
    # v1.2 : si l'action_id est une action native par OACI, elle est
    # PRIORITAIRE sur la variable {METAR_STATION}. Cela résout le bug
    # observé en v1.0 où un bouton 'metar_LFPG' restait coincé sur la
    # valeur précédente de METAR_STATION.
    if action_id in _ACTIONS_OACI:
        oaci = action_id[len(_ACTION_PREFIX):]
        return oaci, f"action native {action_id}"

    # Pour les actions génériques (metar_fetch), on suit l'ancienne logique :
    s = _get_var(session_vars, "METAR_STATION").upper()
    if s and _OACI_RE.match(s):
        return s, "variable {METAR_STATION}"

    s = _extraire_oaci_depuis_action_id(action_id)
    if s:
        return s, f"nom de l'action ({action_id})"

    s = _get_var(session_vars, "OACI").upper()
    if s and _OACI_RE.match(s):
        return s, "variable {OACI}"

    return "LFPM", "valeur par défaut (Melun, ADRASEC 77)"


def _determiner_oaci_vocal(session_vars: dict
                           ) -> Tuple[str, str, Optional[str]]:
    """Mode vocal : extrait l'OACI depuis une phrase transcrite par Vosk."""
    candidats = [
        ("{DEMANDE_VOCALE}", _get_var(session_vars, "DEMANDE_VOCALE")),
        ("{LASTMSG}",        _get_var(session_vars, "LASTMSG")),
        ("{VOICE_INPUT}",    _get_var(session_vars, "VOICE_INPUT")),
    ]
    phrase = ""
    src_phrase = ""
    for nom, val in candidats:
        if val:
            phrase = val
            src_phrase = nom
            break

    if not phrase:
        return "", "aucune phrase vocale disponible", None

    oaci, methode = extraire_oaci_depuis_phrase(phrase)
    if oaci:
        libelle = {
            "phonetique": "alphabet OTAN reconnu",
            "ville":      "nom de ville/aéroport reconnu",
            "direct":     "code OACI prononcé tel quel",
        }.get(methode, methode)
        return oaci, f"extraction vocale depuis {src_phrase} ({libelle})", phrase

    return "", f"aucun code OACI extractible depuis {src_phrase}", phrase


# ---------------------------------------------------------------------------
# 7. Téléchargement du fichier METAR
# ---------------------------------------------------------------------------

def _telecharger_metar(oaci: str) -> Tuple[str, str]:
    url = _METAR_URL.format(oaci.upper())
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
            return "", (f"station {oaci} introuvable sur le serveur NOAA "
                        f"(HTTP 404). Vérifiez le code OACI.")
        return "", f"erreur HTTP {e.code} : {e.reason}"
    except urllib.error.URLError as e:
        return "", (f"impossible de joindre le serveur NOAA : {e.reason}. "
                    f"Vérifiez votre connexion Internet.")
    except Exception as e:
        return "", f"erreur inattendue : {type(e).__name__} — {e}"


# ---------------------------------------------------------------------------
# 8. Parsing et décodage français
# ---------------------------------------------------------------------------

def _parser_entete(texte: str) -> dict:
    champs = {}
    lignes = [l.strip() for l in texte.splitlines() if l.strip()]
    if not lignes:
        return champs

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

    if len(lignes) > 1:
        champs["date_obs"] = lignes[1]
        m = re.search(r"/\s*([0-9.]+)\s+([0-9]{4})\s+UTC", lignes[1])
        if m:
            champs["date_utc"] = m.group(1)
            champs["heure_utc"] = m.group(2)

    for ligne in lignes[2:]:
        m = re.match(r"^([A-Za-z][A-Za-z \(\)\.]*?)\s*:\s*(.*)$", ligne)
        if m:
            cle = m.group(1).strip().lower()
            val = m.group(2).strip()
            val = re.sub(r":0\s*$", "", val)
            champs[cle] = val

    return champs


def _traduire_vent(valeur: str) -> str:
    if not valeur:
        return "non renseigné"
    if re.search(r"calm|variable\s+at\s+0", valeur, re.IGNORECASE):
        return "calme"

    m_dir = re.search(r"from the (\w+)\s*\((\d+)\s*degrees?\)", valeur, re.I)
    direction_fr = ""
    degres = ""
    if m_dir:
        card = m_dir.group(1).upper()
        degres = m_dir.group(2)
        direction_fr = _DIRECTIONS_FR.get(card, card)
    elif re.search(r"variable", valeur, re.I):
        direction_fr = "variable"

    m_v = re.search(r"at\s+([\d.]+)\s*MPH\s*\(\s*([\d.]+)\s*KT\)", valeur, re.I)
    vitesse_txt = ""
    if m_v:
        mph = float(m_v.group(1))
        kt = float(m_v.group(2))
        kmh = round(kt * 1.852, 1)
        vitesse_txt = f"{kt:.0f} kt ({kmh} km/h, {mph:.0f} mph)"

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
    if not valeur:
        return "non renseignée"
    plus = "supérieure à " if re.search(r"greater than", valeur, re.I) else ""
    m = re.search(r"([\d./]+)\s*mile", valeur, re.I)
    if m:
        miles_str = m.group(1)
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
    m = re.search(r"(-?[\d.]+)\s*F", f_str, re.I)
    if not m:
        return f_str
    f = float(m.group(1))
    c = (f - 32) * 5 / 9
    m_c = re.search(r"\(\s*(-?[\d.]+)\s*C\s*\)", f_str)
    if m_c:
        return f"**{m_c.group(1)} °C** ({f:.0f} °F)"
    return f"**{c:.0f} °C** ({f:.0f} °F)"


def _traduire_pression(valeur: str) -> str:
    m_hpa = re.search(r"\(\s*([\d.]+)\s*hPa\s*\)", valeur)
    m_in = re.search(r"([\d.]+)\s*in\.?\s*Hg", valeur, re.I)
    if m_hpa and m_in:
        hpa = float(m_hpa.group(1))
        if hpa < 1000:
            tendance = " (basse, perturbé)"
        elif hpa > 1020:
            tendance = " (haute, anticyclonique)"
        else:
            tendance = " (standard)"
        return f"**{hpa:.0f} hPa**{tendance} — {m_in.group(1)} inHg"
    return valeur


def _decoder_metar_brut(ob: str) -> List[str]:
    extras: List[str] = []
    if not ob:
        return extras

    tokens = ob.split()
    if len(tokens) < 2:
        return extras

    m_dh = re.match(r"^(\d{2})(\d{2})(\d{2})Z$", tokens[1])
    if m_dh:
        jour, hh, mm = m_dh.groups()
        extras.append(
            f"- **Heure d'observation** : le {jour} du mois à "
            f"{hh}h{mm} UTC"
        )

    if "AUTO" in tokens:
        extras.append(
            "- **Source** : observation **automatique** (station sans observateur)"
        )
    if "COR" in tokens:
        extras.append("- **Correction** appliquée à un message précédent (COR)")

    if "CAVOK" in tokens:
        extras.append(
            "- **CAVOK** : visibilité ≥ 10 km, aucun nuage sous 5000 ft (ou MSA), "
            "aucun phénomène significatif → **conditions excellentes**"
        )

    phenomenes_trouves = []
    for t in tokens[2:]:
        if t in ("CAVOK", "NSC", "NCD", "SKC", "CLR"):
            continue
        if re.match(r"^[+\-]?(VC)?[A-Z]{2,8}$", t) and \
           2 <= len(t.replace("+", "").replace("-", "")) <= 8:
            decode = _decoder_token_phenomene(t)
            if decode:
                phenomenes_trouves.append(decode)
    if phenomenes_trouves:
        extras.append(
            "- **Phénomènes significatifs** : "
            + ", ".join(f"*{p}*" for p in phenomenes_trouves)
        )

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

    for t in tokens:
        if re.match(r"^Q\d{4}$", t):
            extras.append(f"- **QNH** : {t[1:]} hPa (référence pression mer)")
            break
        if re.match(r"^A\d{4}$", t):
            inhg = int(t[1:]) / 100
            hpa = round(inhg * 33.8639)
            extras.append(f"- **QNH** : {inhg:.2f} inHg ≈ {hpa} hPa")
            break

    for i, t in enumerate(tokens):
        if re.match(r"^\d{4}$", t) and i >= 2 and not re.match(r"^\d{6}Z?$", t):
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
    t = token
    parts = []

    if t.startswith("-"):
        parts.append(_PHENOMENES["-"]); t = t[1:]
    elif t.startswith("+"):
        parts.append(_PHENOMENES["+"]); t = t[1:]
    elif t.startswith("VC"):
        parts.append(_PHENOMENES["VC"]); t = t[2:]

    elements = re.findall(r"[A-Z]{2}", t)
    if not elements or any(e not in _PHENOMENES for e in elements):
        return ""

    for e in elements:
        parts.append(_PHENOMENES[e])

    return "".join(parts).strip()


# ---------------------------------------------------------------------------
# 9. Rendu Markdown commun
# ---------------------------------------------------------------------------

def _rendre_metar(oaci: str, source: str, contenu: str,
                  options: Any) -> Tuple[str, List[str], Optional[str]]:
    warnings: List[str] = []

    champs = _parser_entete(contenu)
    if not champs:
        warnings.append(f"contenu METAR {oaci} vide ou non parsable")
        return (f"## ⚠️ METAR {oaci} reçu mais illisible\n\n```\n{contenu}\n```",
                warnings, None)

    m_ob = re.search(r"^ob:\s*(.+)$", contenu, re.MULTILINE)
    metar_brut = m_ob.group(1).strip() if m_ob else ""

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

    if "sky conditions" in champs:
        lignes_md.append(f"- **Ciel (NOAA)** : {champs['sky conditions']}.")
    if "weather" in champs:
        lignes_md.append(f"- **Temps présent (NOAA)** : {champs['weather']}.")

    extras = _decoder_metar_brut(metar_brut)
    if extras:
        lignes_md.append("")
        lignes_md.append("### 🔍 Décodage complémentaire (METAR brut)")
        lignes_md.append("")
        lignes_md.extend(extras)

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
    lignes_md.append(f"*Source : NOAA / NWS — {_METAR_URL.format(oaci)}*")

    return "\n".join(lignes_md), warnings, metar_brut


# ---------------------------------------------------------------------------
# 10. Actions
# ---------------------------------------------------------------------------

def _action_metar_fetch(action_id: str, session_vars: dict, options: Any
                        ) -> Tuple[str, List[str]]:
    warnings: List[str] = []
    oaci, source = _determiner_oaci(action_id, session_vars)
    _set_session_var(options, "METAR_OACI_SRC", "standard")

    contenu, erreur = _telecharger_metar(oaci)
    if erreur:
        md = (
            f"## ❌ Erreur récupération METAR — {oaci}\n\n"
            f"**Station demandée** : `{oaci}` *(source : {source})*\n\n"
            f"**Cause** : {erreur}\n\n"
            f"---\n\n"
            f"**Pour réessayer :**\n"
            f"- Vérifiez le code OACI 4 lettres (ex. LFPM, LFPG, EGLL).\n"
            f"- Définissez `/set METAR_STATION=XXXX` pour forcer une autre station.\n"
            f"- URL interrogée : {_METAR_URL.format(oaci)}"
        )
        warnings.append(f"METAR {oaci} : {erreur}")
        return md, warnings

    md, w, _ = _rendre_metar(oaci, source, contenu, options)
    warnings.extend(w)
    return md, warnings


def _action_metar_vocal(session_vars: dict, options: Any
                        ) -> Tuple[str, List[str]]:
    warnings: List[str] = []

    oaci, source, phrase = _determiner_oaci_vocal(session_vars)
    _set_session_var(options, "METAR_OACI_SRC", "vocal")

    if not oaci:
        md = (
            f"## 🎙️ METAR vocal — extraction impossible\n\n"
            f"**Cause** : {source}.\n\n"
        )
        if phrase:
            md += f"**Phrase analysée** : « *{phrase}* »\n\n"
        md += (
            "**Façons de demander un METAR à la voix :**\n\n"
            "- Par alphabet OTAN : « *METAR Lima Foxtrot Papa Mike* »\n"
            "- Par ville : « *METAR de Melun* », « *météo aéro de Roissy* »\n"
            "- Par code direct : « *METAR de LFPG* »\n\n"
            "Sinon, définissez la variable :\n"
            "`/set METAR_STATION=LFPM` puis cliquez le bouton METAR."
        )
        warnings.append(f"METAR vocal : {source}")
        return md, warnings

    contenu, erreur = _telecharger_metar(oaci)
    if erreur:
        md = (
            f"## ❌ Erreur récupération METAR vocal — {oaci}\n\n"
            f"**Station extraite** : `{oaci}`\n"
            f"**Source** : {source}\n"
            f"**Phrase analysée** : « *{phrase}* »\n\n"
            f"**Cause** : {erreur}"
        )
        warnings.append(f"METAR vocal {oaci} : {erreur}")
        return md, warnings

    md, w, _ = _rendre_metar(oaci, source, contenu, options)
    warnings.extend(w)

    prefixe_vocal = (
        f"## 🎙️ Station reconnue : **{oaci}**\n\n"
        f"*Phrase : « {phrase} » — {source}.*\n\n"
        f"---\n\n"
    )
    return prefixe_vocal + md, warnings


# ---------------------------------------------------------------------------
# 11. Point d'entrée IAbrain (contrat d'interface)
# ---------------------------------------------------------------------------

def is_action(action_id: str) -> bool:
    aid = (action_id or "").strip()
    if aid in _ACTIONS_GENERIQUES:
        return True
    if aid in _ACTIONS_OACI:
        return True
    if _extraire_oaci_depuis_action_id(aid):
        return True
    return False


def list_actions() -> List[Tuple[str, str, str]]:
    """Déclare 2 actions génériques + 1 par aérodrome français (v1.2).

    Total : 2 + len(_AERODROMES_FR) entrées dans le dropdown.
    """
    actions: List[Tuple[str, str, str]] = [
        (
            ACTION_METAR_FETCH,
            "METAR — Récupérer (variable {METAR_STATION})",
            "Télécharge et décode en français clair l'observation "
            "météorologique aéronautique (METAR) de la station définie "
            "par la variable de session {METAR_STATION}. À défaut, "
            "utilise LFPM (Melun, ADRASEC 77). Stocke le METAR brut dans "
            "{METAR_RAW}. Pour sélectionner une station fixe sans variable, "
            "préférez une action « METAR — LFXX » spécifique."
        ),
        (
            ACTION_METAR_VOCAL,
            "METAR — Vocal (extraction phonétique OTAN)",
            "Récupère le METAR à partir d'une demande vocale transcrite "
            "par Vosk. Extrait le code OACI depuis {DEMANDE_VOCALE} en "
            "reconnaissant l'alphabet OTAN, les noms de villes françaises "
            "ou un code OACI prononcé tel quel. Usage mains libres."
        ),
    ]

    # Une action native par aérodrome (110 entrées)
    for oaci, nom in _AERODROMES_FR:
        actions.append((
            f"{_ACTION_PREFIX}{oaci}",
            f"METAR — {oaci} ({nom})",
            f"Télécharge et décode le METAR de la station {oaci} "
            f"({nom}) directement, sans variable de session. "
            f"Source : NOAA / NWS."
        ))

    return actions


def execute_action(action_id: str,
                   imported_files: Sequence[Tuple[str, str]] = (),
                   options: Any = None) -> Tuple[str, List[str]]:
    aid = (action_id or "").strip()
    session_vars = _get_session_vars(options)

    try:
        if aid == ACTION_METAR_VOCAL:
            return _action_metar_vocal(session_vars, options)
        if aid == ACTION_METAR_FETCH or aid in _ACTIONS_OACI \
                or _extraire_oaci_depuis_action_id(aid):
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
# 12. Autotest local
# ---------------------------------------------------------------------------

def _autotest() -> int:
    print(f"=== Autotest IAbrain_actions_metar v{__version__} ===\n")
    erreurs = 0

    # Test 1 : contrat d'interface + nombre d'actions
    print("[1] Contrat d'interface")
    actions = list_actions()
    print(f"    Nombre d'actions exposées : {len(actions)}")
    print(f"    Dont {len(_AERODROMES_FR)} aérodromes français + 2 génériques")
    assert len(actions) == 2 + len(_AERODROMES_FR), \
        f"attendu {2 + len(_AERODROMES_FR)}, obtenu {len(actions)}"
    for a in actions:
        assert len(a) == 3, f"action mal formée : {a!r}"
    assert is_action("metar_fetch")
    assert is_action("metar_vocal")
    assert is_action("metar_LFPM")
    assert is_action("metar_LFPG")
    assert is_action("metar_LFBO")
    assert not is_action("hello_world")
    print("    OK")

    # Test 2 : pas de doublons d'OACI dans la table
    print("[2] Pas de doublons dans la table _AERODROMES_FR")
    oacis = [o for o, _ in _AERODROMES_FR]
    doublons = [c for c in oacis if oacis.count(c) > 1]
    if doublons:
        print(f"    ÉCHEC : doublons trouvés : {set(doublons)}")
        erreurs += 1
    else:
        print(f"    OK ({len(set(oacis))} OACI uniques)")

    # Test 3 : tous les codes sont au format OACI valide
    print("[3] Format OACI valide pour toutes les stations")
    invalides = [o for o, _ in _AERODROMES_FR if not _OACI_RE.match(o)]
    if invalides:
        print(f"    ÉCHEC : {invalides}")
        erreurs += 1
    else:
        print(f"    OK")

    # Test 4 : action_id 'metar_LFPG' déclenche bien LFPG (le bug v1.1)
    print("[4] Résolution OACI pour metar_LFPG (régression bug v1.1)")
    oaci, src = _determiner_oaci("metar_LFPG", {})
    if oaci != "LFPG":
        print(f"    ÉCHEC : oaci={oaci} (attendu LFPG)")
        erreurs += 1
    else:
        print(f"    OK   : metar_LFPG -> {oaci} ({src})")

    # Test 5 : action_id 'metar_LFPG' PRIORITAIRE sur METAR_STATION résiduel
    print("[5] Action native PRIORITAIRE sur {METAR_STATION} (bug rapporté)")
    sv = {"METAR_STATION": "LFPM"}  # variable polluée
    oaci, src = _determiner_oaci("metar_LFPG", sv)
    if oaci != "LFPG":
        print(f"    ÉCHEC : oaci={oaci} (LFPG attendu, METAR_STATION ne doit pas primer)")
        erreurs += 1
    else:
        print(f"    OK   : LFPG l'emporte sur METAR_STATION=LFPM résiduel")

    # Test 6 : metar_fetch générique respecte toujours METAR_STATION
    print("[6] metar_fetch (générique) respecte {METAR_STATION}")
    sv = {"METAR_STATION": "LFBO"}
    oaci, src = _determiner_oaci("metar_fetch", sv)
    if oaci != "LFBO":
        print(f"    ÉCHEC : oaci={oaci} (attendu LFBO)")
        erreurs += 1
    else:
        print(f"    OK   : {oaci} ({src})")

    # Test 7 : extraction phonétique OTAN (régression v1.1)
    print("[7] Extraction phonétique OTAN")
    cas = [
        ("Lima Foxtrot Papa Mike", "LFPM"),
        ("donnez-moi le tard de lima fox trotte papa mike", "LFPM"),
        ("Kilo Juliet Foxtrot Kilo", "KJFK"),
    ]
    err7 = 0
    for phrase, attendu in cas:
        obtenu, _ = extraire_oaci_depuis_phrase(phrase)
        if obtenu != attendu:
            print(f"    ÉCHEC : '{phrase[:50]}' -> '{obtenu}' (attendu '{attendu}')")
            err7 += 1
    if err7 == 0:
        print(f"    OK")
    erreurs += err7

    # Test 8 : présence des stations IDF / ADRASEC 77 critiques
    print("[8] Stations ADRASEC 77 / IDF présentes")
    critiques = ["LFPM", "LFPG", "LFPO", "LFPB", "LFPN", "LFPT", "LFPV"]
    manquantes = [c for c in critiques if f"metar_{c}" not in _ACTIONS_OACI]
    if manquantes:
        print(f"    ÉCHEC : stations IDF manquantes : {manquantes}")
        erreurs += 1
    else:
        print(f"    OK ({len(critiques)} stations IDF présentes)")

    # Test 9 : régression parsing METAR
    print("[9] Régression parsing v1.0 (échantillon LFPM)")
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
    )
    champs = _parser_entete(echantillon)
    if champs.get("oaci") != "LFPM" or "Nord-Nord-Ouest" not in _traduire_vent(champs["wind"]):
        print("    ÉCHEC parsing")
        erreurs += 1
    else:
        print("    OK")

    # Test 10 : libellés des actions présents
    print("[10] Libellés des actions LF*")
    quelques = [a for a in actions if a[0].startswith("metar_LF")][:5]
    for aid, label, desc in quelques:
        print(f"    {aid:14s} → \"{label}\"")
    print("    OK")

    print(f"\n=== {'TOUS LES TESTS PASSENT' if not erreurs else f'{erreurs} ÉCHEC(S)'} ===")
    return 0 if not erreurs else 1


if __name__ == "__main__":
    import sys
    sys.exit(_autotest())
