# -*- coding: utf-8 -*-
"""
============================================================================
  chronogramme.py - Plugin d-IA v1.11+ : le DIRANIM qui deroule
============================================================================
  Auteur  : Jean-Louis (F1GBD) - ADRASEC 77 / FNRASEC
  Version : 1.0
  Doctrine : "Exercices de securite civile - Guide methodologique sur les
             exercices Cadre et Terrain", Direction de la Securite Civile,
             2011, section 3.1.3.3 (le chronogramme).

Objet
-----
Jusqu'ici, la cellule d'animation de d-IA (LLM3) tirait un evenement au sort
dans un repertoire, tous les K tours, sans lien avec un objectif. Le guide
fait l'inverse : il part de la REACTION ATTENDUE, choisit le joueur qui doit
la produire, puis l'animateur emetteur, puis seulement redige l'evenement,
et decide enfin du vecteur et du groupe horaire.

Ce plugin lit ce tableau - un CSV que le formateur ecrit avant la seance -
et le deroule. d-IA cesse d'improviser : il tient le role du DIRANIM.

Les quatre apports doctrinaux
-----------------------------
  1. UNE HORLOGE DE JEU. Les prises de parole sont converties en minutes de
     jeu (MINUTES_PAR_TOUR), et HEURE_JEU est publiee a chaque tour. Les
     joueurs cessent d'inventer leurs horodates : ils lisent l'heure de
     l'exercice. C'est la double colonne "groupe horaire (reel et H+X mn)"
     du guide.

  2. UN INJECT, UN DESTINATAIRE. Une ligne du chronogramme n'est publiee
     QU'AU tour du joueur designe en colonne "recepteur". L'autre partie ne
     l'a pas recue : elle l'apprendra si - et seulement si - l'information
     circule. C'est exactement ce que le guide cherche a tester.

  3. LA REACTION ATTENDUE N'EST JAMAIS PUBLIEE. Elle est lue par le plugin,
     journalisee dans la main courante de RETEX, et pointee automatiquement
     par les motifs de la colonne "detection". Les joueurs ne la voient
     jamais : c'est la regle "pas de divulgation" du paragraphe 3.1.1.

  4. PAS DE CONSTAT D'ECHEC. Si la reaction attendue n'est pas venue au bout
     de RELANCE_APRES_TOURS, le plugin injecte automatiquement le texte de
     la colonne "relance" - le meme evenement, par un autre vecteur. Le
     guide : "il est preferable de relancer l'evenement ou l'incident par un
     autre vecteur de communication pour faire prendre conscience aux joueurs
     qu'ils ont rate quelque chose mais qu'ils ont encore le temps de reagir
     comme dans la realite."

Le fichier de chronogramme
--------------------------
Un CSV UTF-8, separateur point-virgule (celui d'Excel en francais), depose a
cote de ce plugin. Par defaut "chronogramme.csv" ; la variable de session
CHRONOGRAMME = helios noir 26 fait lire "chronogramme_helios_noir_26.csv".

QUEL CHRONOGRAMME EST JOUE ? Dans cet ordre :
  1. celui que designe la variable de session CHRONOGRAMME ;
  2. "chronogramme.csv" s'il existe ;
  3. l'UNIQUE chronogramme_*.csv depose a cote du plugin.

Le troisieme cas est celui du formateur qui a depose son fichier sans penser a
la variable de session : deposer le fichier EST un acte explicite. Le plugin le
charge donc, et il le DIT dans le fil - il ne prend jamais la main en silence.
Avec PLUSIEURS fichiers, il ne choisit pas : il les nomme et rappelle comment
en designer un. Sans aucun fichier, il ne publie RIEN et ne le dit qu'une fois :
il peut donc rester installe a demeure dans plugins_dia\ sans perturber les
seances qui se jouent sans chronogramme.

Lignes de metadonnees, en tete, prefixees par # :

    #EXERCICE=HELIOS NOIR 26
    #SEQUENCE=7                 (v1.3) le chronogramme attend CETTE sequence
    #DEBEX=2026-07-11 14:00
    #MINUTES_PAR_TOUR=5

    Sans #SEQUENCE, le numero est deduit du libelle #EXERCICE s'il contient
    "sequence N" ; a defaut, le chronogramme demarre au premier tour, comme
    avant la v1.3. Avec une sequence declaree, il reste DORMANT tant que le
    dialogue ne l'a pas atteinte - sans quoi les injects du 11 juillet a
    14h00 tombent pendant la sequence du 26 juin, et le FINEX est prononce
    alors que la seance continue. (Defaut observe le 15/09.)

Colonnes, dans cet ordre :

    groupe_horaire ; vecteur ; emetteur ; recepteur ; evenement ;
    reaction_attendue ; detection ; relance

  groupe_horaire   H-15, H, H+5, H+120  (ou DEBEX, FINEX, RESERVE)
  vecteur          VARA FM, HF NVIS, telephone, radio phonie...
  emetteur         ANIBAS jouant l'EHPAD, ANIHAUT jouant le COZ, DIRANIM
  recepteur        LLM1, LLM2, TOUS, ou un libelle de role du preset
  evenement        le message, redige mot a mot, tel qu'il sera lu
  reaction_attendue  JAMAIS publiee - main courante et pointage seulement
  detection        motifs separes par des barres verticales, cherches dans
                   les messages des joueurs (sans accent, sans casse)
  relance          l'inject de rattrapage, par un autre vecteur

Une ligne dont le groupe horaire vaut RESERVE n'est jamais jouee d'elle-meme :
c'est un incident de reserve, que le formateur declenche a la main. Le guide :
"Vous pouvez ajouter a la fin du chronogramme une liste de quelques incidents
que vous injectez si necessaire."

Le texte de l'evenement peut contenir des variables entre accolades :
{TEMPERATURE_C}, {VENT_KMH}, {HUMIDITE_PCT}. Elles sont remplacees par les
valeurs publiees par les autres plugins. C'est ainsi que la mise en ambiance
du guide - "il fait 25 degres a l'ombre, le vent souffle a 5 km/h" - se
remplit toute seule avec les releves AROME du plugin meteo_3x30.

Le pupitre du DIRANIM
---------------------
Pendant la seance, le formateur pilote par "Plugins E/S -> Variables de
session...". Ces variables priment sur celles des plugins et sont prises en
compte immediatement :

    DIRANIM_PAUSE = oui        fige l'horloge de jeu (le temps ne passe plus)
    DIRANIM_AVANCE = 1         pousse le prochain inject sans attendre
    DIRANIM_RESERVE = 2        injecte l'incident de reserve numero 2
    DIRANIM_FINEX = oui        prononce le FINEX
    MINUTES_PAR_TOUR = 10      change la cadence a chaud
    CHRONOGRAMME = seq7        change de chronogramme a chaud

Aucune de ces commandes n'est une ACTION au sens de d-IA : le pupitre reste
donc entierement disponible quand le preset d'exercice impose, comme il le
doit, "plugins_actions_mode": "off". Un COD fictif ne pilote pas le
chronogramme de son propre exercice.

Sortie
------
Une main courante de RETEX : ..\\logs\\retex_chronogramme_AAAAMMJJ.csv
Une ligne par prise de parole, avec l'inject en cours, la reaction attendue
et son pointage. C'est le document du debriefing a froid.
============================================================================
"""

import csv
import datetime
import re
import unicodedata
from pathlib import Path

PLUGIN_NAME = "Chronogramme (DIRANIM)"
PLUGIN_VERSION = "1.3"

# --- Reglages -------------------------------------------------------------
FICHIER_DEFAUT = "chronogramme.csv"
MINUTES_PAR_TOUR = 5          # minutes de jeu par prise de parole
RELANCE_APRES_TOURS = 4       # sans reaction detectee, on relance
TOURS_DIFFUSION = 3           # un message a TOUS reste lisible ce nombre de tours
ATTENTE_MAX_TOURS = 6         # au-dela, un inject part meme sans son destinataire
SANS_ACCENT = True            # valeurs publiees sans accent (confort TTS)
JOURNAL = True                # main courante de RETEX en CSV
LONGUEUR_VALEUR = 158         # plafond d-IA : 160 caracteres par variable

# Un evenement plus long que 2 x LONGUEUR_VALEUR est tronque : la discipline
# radio du guide veut des messages courts, et une variable bavarde degrade
# l'imitation que les modeles en font.

# --------------------------------------------------------------------------
_LOGS = Path(__file__).resolve().parent.parent / "logs"
DOSSIER_SORTIE = _LOGS if _LOGS.is_dir() else Path(__file__).resolve().parent

RE_GROUPE = re.compile(r"^H\s*([+-])\s*(\d+)$", re.IGNORECASE)
RE_HEURE = re.compile(r"^(\d{1,2})\s*[h:]\s*(\d{2})$", re.IGNORECASE)
RE_ACCOLADE = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")

_CACHE = {"chemin": None, "mtime": None, "lignes": [], "meta": {}, "av": [],
          "av_dits": set()}

# Le suivi est indexe par le NUMERO DE LIGNE DANS LE FICHIER (champ "n"), et
# non par la position dans la liste triee : le formateur peut corriger une
# coquille en pleine seance sans que le deroule perde sa place.
_ETAT = {
    "livres": {},         # n -> {tour, detectee, relancee}
    "attente": None,      # n de la ligne due, en attente de son destinataire
    "attente_depuis": None,
    "diffusion": None,    # {"n": n, "restant": k} pour un message a TOUS
    "finex": False,
    "finex_force": False, # FINEX prononce par le DIRANIM : rien ne le defait
    "finex_annonce": False,
    "t0": None,           # tour de reference (premiere prise de parole vue)
    "gel": 0,             # minutes de jeu gelees par DIRANIM_PAUSE
    "dernier_tour": None,
    "reserve_faite": set(),
    "avance": 0,          # minutes offertes par DIRANIM_AVANCE
    "avance_vue": None,   # derniere valeur honoree de DIRANIM_AVANCE
    "arme": False,        # la sequence du chronogramme a ete atteinte (v1.3)
    "arme_annonce": False,
    "hors_sequence": False,   # on l'a quittee avant la fin
}


def _remise_a_zero():
    _ETAT.update({"livres": {}, "attente": None, "attente_depuis": None,
                  "diffusion": None, "finex": False, "finex_force": False,
                  "finex_annonce": False, "t0": None, "gel": 0,
                  "arme": False, "arme_annonce": False, "hors_sequence": False,
                  "dernier_tour": None, "reserve_faite": set(),
                  "avance": 0, "avance_vue": None})


def _par_n(lignes, n):
    for ligne in lignes:
        if ligne["n"] == n:
            return ligne
    return None


# ===========================================================================
#  Petits utilitaires
# ===========================================================================
def _sans_accent(texte):
    """NFD puis suppression des diacritiques. Rien d'autre n'est touche."""
    if not SANS_ACCENT:
        return texte
    decompose = unicodedata.normalize("NFD", texte)
    return "".join(c for c in decompose if unicodedata.category(c) != "Mn")


def _cle(texte):
    """Forme de comparaison : minuscules, sans accent, espaces normalises."""
    decompose = unicodedata.normalize("NFD", (texte or "").lower())
    plat = "".join(c for c in decompose if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", plat).strip()


def _decouper(texte, n=LONGUEUR_VALEUR):
    """Coupe un evenement en deux valeurs au plus, sur une frontiere de mot.

    d-IA tronque toute variable a 160 caracteres. Plutot que de laisser la
    phrase s'arreter au milieu d'un mot, on coupe proprement et on publie la
    suite dans une seconde variable.
    """
    texte = re.sub(r"\s+", " ", (texte or "").strip())
    if len(texte) <= n:
        return [texte] if texte else []
    coupe = texte.rfind(" ", 0, n)
    if coupe < n // 2:
        coupe = n
    premier, reste = texte[:coupe].strip(), texte[coupe:].strip()
    if len(reste) <= n:
        return [premier, reste]
    coupe2 = reste.rfind(" ", 0, n - 1)
    if coupe2 < n // 2:
        coupe2 = n - 1
    return [premier, reste[:coupe2].strip() + "…"]


def _minutes(groupe):
    """Convertit un groupe horaire en minutes relatives au DEBEX.

    Accepte H, H+5, H-15, DEBEX, FINEX, ou une heure absolue 14h20 (qui est
    alors rendue par rapport au DEBEX lu dans les metadonnees).
    Retourne None pour RESERVE et pour tout ce qui n'est pas reconnu.
    """
    g = (groupe or "").strip().upper().replace(" ", "")
    if g in ("", "RESERVE", "RESERVES"):
        return None
    if g in ("H", "DEBEX", "H+0", "H-0"):
        return 0
    m = RE_GROUPE.match(g)
    if m:
        val = int(m.group(2))
        return -val if m.group(1) == "-" else val
    m = RE_HEURE.match(g)
    if m:
        return ("abs", int(m.group(1)) * 60 + int(m.group(2)))
    if g == "FINEX":
        return "FINEX"
    return None


# ===========================================================================
#  Lecture du chronogramme
# ===========================================================================
def _slug(nom):
    """Nom de session -> morceau de nom de fichier. "" si rien d'exploitable."""
    return re.sub(r"[^A-Za-z0-9_-]+", "_", _cle(nom)).strip("_")


def fichier_chronogramme(nom=None):
    """Chemin du CSV : chronogramme.csv, ou chronogramme_<nom>.csv."""
    plat = _slug(nom) if nom else ""
    if plat:
        return Path(__file__).with_name("chronogramme_%s.csv" % plat)
    return Path(__file__).with_name(FICHIER_DEFAUT)


def chronogrammes_presents():
    """Les chronogrammes nommes trouves a cote du plugin, tries."""
    dossier = Path(__file__).resolve().parent
    try:
        fichiers = sorted(dossier.glob("chronogramme_*.csv"))
    except OSError:
        return []
    return [f for f in fichiers if f.is_file()]


def nom_depuis_fichier(chemin):
    """chronogramme_helios_noir_26.csv -> 'helios noir 26'."""
    return Path(chemin).stem[len("chronogramme_"):].replace("_", " ")


def resoudre_chronogramme(nom=None):
    """Quel chronogramme jouer ? Retourne (chemin, origine, avertissements).

    Trois cas, dans cet ordre :
      "variable" - la variable de session CHRONOGRAMME le designe ;
      "defaut"   - chronogramme.csv est present ;
      "unique"   - un SEUL chronogramme nomme est depose a cote du plugin.

    Le troisieme cas est celui du formateur qui a depose son fichier et n'a pas
    pense a la variable de session. Deposer le fichier EST un acte explicite :
    exiger en plus une variable invisible transformait une preparation correcte
    en seance sans chronogramme. On le charge donc, mais on le DIT dans le fil -
    un plugin qui prend la main ne doit jamais le faire en silence.

    Avec plusieurs fichiers, on ne choisit pas a la place du formateur : on les
    nomme et on rappelle comment en designer un.
    """
    # Une variable CHRONOGRAMME vide, ou qui ne contient que de la ponctuation,
    # ne designe rien : elle vaut absence de variable. Sans cette precaution, on
    # retombait sur chronogramme.csv en pretendant qu'il avait ete demande, et
    # le fil annoncait un "fichier absent" que personne n'avait reclame.
    if nom and _slug(nom):
        vise = fichier_chronogramme(nom)
        if vise.exists():
            return vise, "variable", []
        # Le fichier demande n'existe pas : on le dit, et on dit ce qu'il y a.
        presents = chronogrammes_presents()
        dispo = (", ".join(nom_depuis_fichier(f) for f in presents) if presents
                 else "aucun")
        return vise, None, [
            "Plugin Chronogramme : CHRONOGRAMME = %r ne correspond a aucun "
            "fichier (%s attendu). Disponible(s) dans ce dossier : %s."
            % (str(nom).strip(), vise.name, dispo)]
    defaut = fichier_chronogramme()
    if defaut.exists():
        return defaut, "defaut", []
    presents = chronogrammes_presents()
    if len(presents) == 1:
        return presents[0], "unique", []
    if not presents:
        return defaut, None, [
            "Plugin Chronogramme : aucun chronogramme. %s est absent, et ce "
            "dossier n'en contient aucun autre. Sans chronogramme, le plugin "
            "ne publie rien." % defaut]
    dispo = ", ".join(nom_depuis_fichier(f) for f in presents)
    return defaut, None, [
        "Plugin Chronogramme : %d chronogrammes disponibles (%s) - aucun n'est "
        "charge. Choisissez-en un : Plugins E/S > Variables de session > "
        "CHRONOGRAMME = %s" % (len(presents), dispo,
                               nom_depuis_fichier(presents[0]))]


def _lire_csv(chemin):
    """Retourne (lignes, meta, avertissements). Ne leve jamais."""
    lignes, meta, av = [], {}, []
    try:
        brut = chemin.read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        return [], {}, ["Plugin Chronogramme : fichier absent - %s" % chemin]
    except OSError as exc:
        return [], {}, ["Plugin Chronogramme : lecture impossible - %s" % exc]

    utiles = []
    for ligne in brut.splitlines():
        nu = ligne.strip()
        if not nu:
            continue
        if nu.startswith("#"):
            if "=" in nu:
                cle, _, val = nu[1:].partition("=")
                meta[cle.strip().upper()] = val.strip()
            continue
        utiles.append(ligne)

    if not utiles:
        return [], meta, ["Plugin Chronogramme : %s ne contient aucune ligne" % chemin.name]

    # Separateur : point-virgule (Excel FR) ou virgule, selon la premiere ligne.
    sep = ";" if utiles[0].count(";") >= utiles[0].count(",") else ","
    entete = [_cle(c) for c in next(csv.reader([utiles[0]], delimiter=sep))]
    connues = ("groupe_horaire", "vecteur", "emetteur", "recepteur",
               "evenement", "reaction_attendue", "detection", "relance")
    avec_entete = any(c.replace(" ", "_") in connues for c in entete)
    corps = utiles[1:] if avec_entete else utiles

    for num, ligne in enumerate(csv.reader(corps, delimiter=sep), start=1):
        champs = [(c or "").strip() for c in ligne]
        champs += [""] * (8 - len(champs))
        (groupe, vecteur, emetteur, recepteur, evenement,
         reaction, detection, relance) = champs[:8]
        if not evenement:
            continue
        minutes = _minutes(groupe)
        if minutes is None and (groupe or "").strip().upper() not in ("RESERVE", "RESERVES", ""):
            av.append("Plugin Chronogramme : groupe horaire illisible ligne %d (%s)"
                      % (num, groupe))
        lignes.append({
            "n": num,
            "groupe": (groupe or "").strip() or "RESERVE",
            "minutes": minutes,
            "vecteur": vecteur or "radio",
            "emetteur": emetteur or "ANIMATION",
            "recepteur": recepteur or "TOUS",
            "evenement": evenement,
            "reaction": reaction,
            "detection": [d for d in (detection or "").split("|") if d.strip()],
            "relance": relance,
        })

    # Les lignes datees sont jouees dans l'ordre du temps, pas du fichier :
    # le formateur peut ajouter un inject sans renumeroter tout son tableau.
    datees = [l for l in lignes if isinstance(l["minutes"], int)]
    datees.sort(key=lambda l: (l["minutes"], l["n"]))
    autres = [l for l in lignes if not isinstance(l["minutes"], int)]
    return datees + autres, meta, av


def charger(nom=None):
    """Lecture avec cache sur la date de modification (regle des 2 s)."""
    chemin, origine, av_resol = resoudre_chronogramme(nom)
    try:
        mtime = chemin.stat().st_mtime
    except OSError:
        mtime = None
    if _CACHE["chemin"] == chemin and _CACHE["mtime"] == mtime:
        return _CACHE["lignes"], _CACHE["meta"], []
    change_de_fichier = _CACHE["chemin"] is not None and _CACHE["chemin"] != chemin
    lignes, meta, av = _lire_csv(chemin) if origine else ([], {}, [])
    av = list(av_resol) + list(av)
    # Le formateur doit toujours savoir CE QUI est joue, et pourquoi. Le cas
    # "unique" surtout : le plugin a choisi, il le dit.
    if origine and lignes:
        exercice = (meta.get("EXERCICE") or chemin.name).strip()
        precision = {
            "variable": "designe par la variable CHRONOGRAMME",
            "defaut": "fichier par defaut",
            "unique": "seul chronogramme present dans le dossier",
        }[origine]
        av.append("Plugin Chronogramme : %s charge - %s (%s), %d ligne(s) datee(s)."
                  % (chemin.name, exercice, precision,
                     len([l for l in lignes if isinstance(l["minutes"], int)])))
    # Un plugin sans chronogramme doit se taire : il est installe a demeure,
    # mais la plupart des seances n'en chargent pas. L'avertissement est donc
    # dit UNE fois par fichier, pas a chaque prise de parole.
    av = [a for a in av if a not in _CACHE["av_dits"]]
    _CACHE["av_dits"].update(av)
    _CACHE.update({"chemin": chemin, "mtime": mtime, "lignes": lignes,
                   "meta": meta, "av": av})
    # Changer de CHRONOGRAMME remet le deroule a zero ; corriger une coquille
    # dans le fichier courant ne le fait pas, puisque le suivi est indexe par
    # numero de ligne.
    if change_de_fichier:
        _remise_a_zero()
    return lignes, meta, av


# ===========================================================================
#  Horloge de jeu
# ===========================================================================
def _cadence(ctx):
    val = _var(ctx, "MINUTES_PAR_TOUR")
    try:
        n = float(str(val).replace(",", "."))
        if 0 < n <= 240:
            return n
    except (TypeError, ValueError):
        pass
    return MINUTES_PAR_TOUR


def _var(ctx, nom):
    """Lit une variable de situation (variables de session comprises)."""
    vars_ = (ctx or {}).get("vars") or (ctx or {}).get("session_vars") or {}
    if not isinstance(vars_, dict):
        return None
    for cle, val in vars_.items():
        if str(cle).strip().upper() == nom:
            return val
    return None


def _oui(valeur):
    return _cle(valeur) in ("oui", "1", "vrai", "true", "on", "o", "y", "yes")


def _origine(lignes):
    """Minute de jeu du premier evenement : l'horloge demarre la."""
    datees = [l["minutes"] for l in lignes if isinstance(l["minutes"], int)]
    return min(datees) if datees else 0


def sequence_declaree(meta):
    """Numero de sequence que ce chronogramme decrit, ou None (v1.3).

    Deux sources, dans l'ordre :
      #SEQUENCE=7                        explicite
      #EXERCICE=... sequence 7 - ...     deduite du libelle

    None signifie "ce chronogramme vaut pour tout l'exercice" : il demarre au
    premier tour, comme avant la v1.3. On ne rend donc pas dormant un
    chronogramme ecrit pour l'ensemble d'une seance.
    """
    brut = (meta or {}).get("SEQUENCE", "").strip()
    m = re.search(r"\d+", brut)
    if m:
        return int(m.group(0))
    m = re.search(r"s[eé]quence\s*(\d+)",
                  _sans_accent((meta or {}).get("EXERCICE", "")), re.I)
    return int(m.group(1)) if m else None


def sequence_du_theme(ctx):
    """Numero de sequence du theme actuellement joue, ou None.

    Le libelle d'un theme commence par "Sequence N (...)" dans les presets
    HELIOS NOIR 26. On ne lit que ce numero : le reste du libelle change d'un
    exercice a l'autre, le numero non.
    """
    theme = _sans_accent(str((ctx or {}).get("theme") or ""))
    m = re.search(r"s[eé]quence\s*(\d+)", theme, re.I)
    return int(m.group(1)) if m else None


def minutes_de_jeu(ctx, lignes):
    """Minutes ecoulees depuis le premier groupe horaire du chronogramme."""
    tour = int((ctx or {}).get("tour") or 1)
    if _ETAT["t0"] is None:
        _ETAT["t0"] = tour
    ecoules = max(0, tour - _ETAT["t0"])
    return _origine(lignes) + ecoules * _cadence(ctx) - _ETAT["gel"] + _ETAT["avance"]


def _debex(meta):
    """Horodate absolue du DEBEX, si les metadonnees en donnent une."""
    brut = (meta or {}).get("DEBEX", "").strip()
    for forme in ("%Y-%m-%d %H:%M", "%d/%m/%Y %H:%M", "%d/%m %H:%M", "%H:%M"):
        try:
            d = datetime.datetime.strptime(brut, forme)
            if forme == "%H:%M":
                auj = datetime.date.today()
                d = d.replace(year=auj.year, month=auj.month, day=auj.day)
            elif forme == "%d/%m %H:%M":
                d = d.replace(year=datetime.date.today().year)
            return d
        except ValueError:
            continue
    return None


def heure_de_jeu(meta, minutes):
    """Chaine lisible : '11/07 14h20', ou 'H+20' faute de DEBEX declare."""
    base = _debex(meta)
    signe = "+" if minutes >= 0 else "-"
    relatif = "H%s%d" % (signe, abs(int(round(minutes))))
    if not base:
        return relatif
    d = base + datetime.timedelta(minutes=minutes)
    return "%s %02dh%02d (%s)" % (d.strftime("%d/%m"), d.hour, d.minute, relatif)


# ===========================================================================
#  Destinataire
# ===========================================================================
def destinataire_est(ligne, ctx):
    """Le joueur qui parle est-il le recepteur de cet inject ?

    La colonne recepteur accepte LLM1 / LLM2 / LLM3, TOUS, ou un libelle de
    role du preset (COD Vaubourg, Operateur PCO Nangeville...). La comparaison
    se fait sans accent et sans casse, et tolere qu'un libelle en contienne
    un autre - "Operateur PCO Nangeville (VOUS)" repond bien a "PCO".
    """
    cible = _cle(ligne.get("recepteur"))
    if cible in ("", "tous", "toutes stations", "tout le monde", "all"):
        return True
    speaker = _cle((ctx or {}).get("speaker"))
    if cible == speaker:
        return True
    role = _cle((ctx or {}).get("role"))
    if role and (cible in role or role in cible):
        return True
    labels = (ctx or {}).get("labels") or {}
    if isinstance(labels, dict):
        for nom, libelle in labels.items():
            lib = _cle(libelle)
            if lib and (cible in lib or lib in cible):
                # label1 -> LLM1, label2 -> LLM2, label3 -> LLM3
                chiffre = re.sub(r"\D", "", str(nom))
                if chiffre and speaker == "llm%s" % chiffre:
                    return True
    return False


def _substituer(texte, ctx):
    """Remplace {VARIABLE} par la valeur publiee par les autres plugins."""
    def _remplacer(m):
        val = _var(ctx, m.group(1).upper())
        return str(val) if val not in (None, "") else m.group(0)
    return RE_ACCOLADE.sub(_remplacer, texte or "")


# ===========================================================================
#  Deroule
# ===========================================================================
def _datees(lignes):
    return [l for l in lignes if isinstance(l["minutes"], int)]


def _prochaine(lignes):
    """Prochaine ligne datee non encore livree, dans l'ordre du temps."""
    for ligne in _datees(lignes):
        if ligne["n"] not in _ETAT["livres"]:
            return ligne
    return None


def _ligne_due(lignes, minutes):
    """Premiere ligne datee non encore livree dont l'heure est venue."""
    ligne = _prochaine(lignes)
    return ligne if ligne and ligne["minutes"] <= minutes else None


def _relance_due(lignes, tour):
    """Une reaction attendue manque-t-elle depuis trop longtemps ?

    C'est la regle "pas de constat d'echec" du paragraphe 3.1.1 : on ne note
    pas l'absence de reaction pour le debriefing, on relance l'evenement par
    un autre vecteur pendant qu'il est encore temps de reagir.
    """
    for n, suivi in _ETAT["livres"].items():
        if suivi.get("detectee") or suivi.get("relancee"):
            continue
        ligne = _par_n(lignes, n)
        if not ligne or not ligne.get("relance") or not ligne.get("detection"):
            continue
        if tour - suivi.get("tour", tour) >= RELANCE_APRES_TOURS:
            return ligne
    return None


def _relance_en_vue(lignes, tour):
    """Une relance reste-t-elle possible ? Alors le FINEX peut attendre."""
    for n, suivi in _ETAT["livres"].items():
        if suivi.get("detectee") or suivi.get("relancee"):
            continue
        ligne = _par_n(lignes, n)
        if ligne and ligne.get("relance") and ligne.get("detection"):
            return True
    return False


def _publier(ligne, ctx, texte=None, mention=""):
    """Construit les variables d'un inject."""
    corps = _substituer(texte if texte is not None else ligne["evenement"], ctx)
    morceaux = _decouper(_sans_accent(corps))
    out = {}
    if morceaux:
        out["INJECT"] = morceaux[0]
    if len(morceaux) > 1:
        out["INJECT_SUITE"] = morceaux[1]
    out["INJECT_DE"] = _sans_accent(ligne["emetteur"])[:LONGUEUR_VALEUR]
    out["INJECT_VECTEUR"] = _sans_accent(ligne["vecteur"] + (" " + mention if mention else ""))[:LONGUEUR_VALEUR]
    return out


# ===========================================================================
#  Contrat d-IA
# ===========================================================================
def list_variables():
    return [
        ("HEURE_JEU", "Heure de l'exercice - les joueurs horodatent avec elle"),
        ("PHASE_EXERCICE", "avant DEBEX, en cours, ou FINEX"),
        ("INJECT", "Message d'animation adresse au joueur qui parle"),
        ("INJECT_SUITE", "Fin du message quand il depasse une variable"),
        ("INJECT_DE", "Qui emet : ANIBAS, ANIHAUT, DIRANIM, et le role joue"),
        ("INJECT_VECTEUR", "Par quel moyen le message arrive"),
        ("CHRONO_AVANCEMENT", "Position dans le chronogramme"),
    ]


def list_actions():
    """Une seule action, et elle ne fait que LIRE.

    Avancer le chronogramme, tirer un incident de reserve ou prononcer le
    FINEX sont des prerogatives du DIRANIM : elles passent par les variables
    de session, jamais par une directive. Un joueur ne doit pas pouvoir
    piloter le deroule de son propre exercice - et le preset d'exercice
    impose de toute facon "plugins_actions_mode": "off".
    """
    return [("chronogramme_etat",
             "Etat du chronogramme (lecture seule)",
             "Rend l'heure de jeu, la phase et l'avancement. N'injecte rien.")]


def execute_action(action_id, params, ctx):
    if action_id != "chronogramme_etat":
        return {}
    lignes, meta, av = charger(_var(ctx, "CHRONOGRAMME"))
    minutes = minutes_de_jeu(ctx, lignes)
    datees = [l for l in lignes if isinstance(l["minutes"], int)]
    return ({
        "HEURE_JEU": _sans_accent(heure_de_jeu(meta, minutes)),
        "PHASE_EXERCICE": "FINEX" if _ETAT["finex"] else "en cours",
        "CHRONO_AVANCEMENT": "%d inject(s) sur %d" % (len(_ETAT["livres"]), len(datees)),
    }, av)


def collect(ctx):
    """ENTREE : appele avant chaque prise de parole."""
    avertis = []
    lignes, meta, av = charger(_var(ctx, "CHRONOGRAMME"))
    avertis.extend(av)
    if not lignes:
        return {}, avertis

    tour = int((ctx or {}).get("tour") or 1)

    # --- La sequence du chronogramme est-elle atteinte ? (v1.3) ------------
    # Tant qu'elle ne l'est pas, on ne fait RIEN : pas d'inject, pas
    # d'horloge, pas de FINEX. Deux horloges tournaient cote a cote sans se
    # parler - celle du chronogramme, cadencee au tour, et celle des themes.
    # C'est le THEME qui commande : c'est lui que les joueurs voient.
    voulue = sequence_declaree(meta)
    if voulue is not None and not _ETAT["finex"]:
        jouee = sequence_du_theme(ctx)
        if jouee is not None and jouee != voulue:
            if _ETAT["arme"]:
                # On a quitte la sequence avant la fin du chronogramme. On
                # gele plutot que de derouler dans le vide : le formateur
                # decide s'il revient, ou s'il prononce le FINEX.
                if not _ETAT["hors_sequence"]:
                    _ETAT["hors_sequence"] = True
                    avertis.append(
                        "chronogramme GELE : le dialogue a quitte la sequence "
                        "%d pour la sequence %d, et %d inject(s) n'ont pas ete "
                        "joues. Revenez a la sequence %d, ou prononcez le FINEX "
                        "par la variable de session DIRANIM_FINEX."
                        % (voulue, jouee, len(_datees(lignes)) - len(_ETAT["livres"]),
                           voulue))
                return ({"PHASE_EXERCICE": "chronogramme en attente de la "
                                           "sequence %d" % voulue}, avertis)
            if not _ETAT["arme_annonce"]:
                _ETAT["arme_annonce"] = True
                avertis.append(
                    "chronogramme EN ATTENTE : il decrit la sequence %d, or le "
                    "dialogue joue la sequence %d. Aucun inject ne sera emis "
                    "avant que la sequence %d ne soit atteinte."
                    % (voulue, jouee, voulue))
            return ({"PHASE_EXERCICE": "avant la sequence %d" % voulue}, avertis)
        if jouee == voulue and not _ETAT["arme"]:
            _ETAT["arme"] = True
            _ETAT["hors_sequence"] = False
            _ETAT["t0"] = tour          # l'horloge part MAINTENANT
            avertis.append(
                "sequence %d atteinte au tour %d : le chronogramme est arme, "
                "l'horloge de jeu demarre." % (voulue, tour))

    # Pupitre du DIRANIM ----------------------------------------------------
    if _oui(_var(ctx, "DIRANIM_PAUSE")):
        if _ETAT["dernier_tour"] is not None and tour > _ETAT["dernier_tour"]:
            _ETAT["gel"] += _cadence(ctx) * (tour - _ETAT["dernier_tour"])
    _ETAT["dernier_tour"] = tour

    if _oui(_var(ctx, "DIRANIM_FINEX")):
        _ETAT["finex"] = True
        _ETAT["finex_force"] = True

    # Avance demandee par le formateur : chaque NOUVELLE valeur de
    # DIRANIM_AVANCE pousse un inject (1, puis 2, puis 3...). Sans cette
    # regle, une variable oubliee dans le pupitre deroulerait tout l'exercice.
    avance = _var(ctx, "DIRANIM_AVANCE")
    if avance not in (None, "") and str(avance) != str(_ETAT["avance_vue"]):
        _ETAT["avance_vue"] = str(avance)
        suivante = _prochaine(lignes)
        if suivante is not None:
            manque = suivante["minutes"] - minutes_de_jeu(ctx, lignes)
            if manque > 0:
                _ETAT["avance"] += manque
        # Le formateur veut la suite : on ne lui repasse pas le message
        # precedent parce qu'il etait encore en diffusion.
        _ETAT["diffusion"] = None

    minutes = minutes_de_jeu(ctx, lignes)
    out = {"HEURE_JEU": _sans_accent(heure_de_jeu(meta, minutes))}
    datees = _datees(lignes)
    out["CHRONO_AVANCEMENT"] = "%d/%d" % (len(_ETAT["livres"]), len(datees))

    # Ordre de priorite : FINEX prononce par le DIRANIM, puis incident de
    # reserve, puis FINEX automatique. Un incident de reserve reste jouable
    # apres la derniere ligne datee - c'est meme la son usage le plus
    # frequent, quand le jeu est alle plus vite que le chronogramme.
    if _ETAT["finex_force"]:
        return _finir(out, avertis)

    reserve = _var(ctx, "DIRANIM_RESERVE")
    if reserve not in (None, ""):
        libres = [l for l in lignes if not isinstance(l["minutes"], int)]
        rang = int(re.sub(r"\D", "", str(reserve)) or 0)
        if 1 <= rang <= len(libres) and rang not in _ETAT["reserve_faite"]:
            ligne = libres[rang - 1]
            if destinataire_est(ligne, ctx):
                _ETAT["reserve_faite"].add(rang)
                _ETAT["livres"].setdefault(ligne["n"], {
                    "tour": tour, "detectee": False, "relancee": False})
                _ETAT["finex"] = False       # l'exercice reprend
                _journaliser(ctx, meta, minutes, ligne, "reserve")
                out["PHASE_EXERCICE"] = "en cours"
                return _remettre(out, ligne, ctx, mention="(reserve)"), avertis
        elif rang > len(libres):
            avertis.append("Plugin Chronogramme : aucun incident de reserve n%d "
                           "(%d disponible(s))" % (rang, len(libres)))

    # FINEX automatique : tout est livre ET aucune relance ne reste possible.
    diffusion_en_cours = bool(_ETAT["diffusion"] and _ETAT["diffusion"]["restant"] > 0)
    if not _ETAT["finex"] and datees and _ETAT["attente"] is None \
            and not diffusion_en_cours \
            and len(_ETAT["livres"]) >= len(datees) \
            and not _relance_en_vue(lignes, tour):
        _ETAT["finex"] = True
    if _ETAT["finex"]:
        return _finir(out, avertis)

    out["PHASE_EXERCICE"] = "en cours" if minutes >= 0 else "avant DEBEX"

    # Un message adresse a TOUS reste lisible quelques tours, le temps que
    # chaque station l'ait sous les yeux.
    diff = _ETAT["diffusion"]
    if diff and diff["restant"] > 0:
        ligne = _par_n(lignes, diff["n"])
        if ligne is not None:
            diff["restant"] -= 1
            out.update(_publier(ligne, ctx, texte=diff.get("texte"),
                                mention=diff.get("mention", "")))
            return _borner(out), avertis
        _ETAT["diffusion"] = None

    # Relance : la reaction attendue n'est pas venue -------------------------
    if _ETAT["attente"] is None:
        ligne = _relance_due(lignes, tour)
        if ligne is not None and destinataire_est(ligne, ctx):
            _ETAT["livres"][ligne["n"]]["relancee"] = True
            _ETAT["livres"][ligne["n"]]["tour"] = tour
            _journaliser(ctx, meta, minutes, ligne, "relance")
            return _remettre(out, ligne, ctx, texte=ligne["relance"],
                             mention="(relance par un autre vecteur)"), avertis

    # Inject du chronogramme ------------------------------------------------
    ligne = _par_n(lignes, _ETAT["attente"]) if _ETAT["attente"] is not None else None
    if ligne is None:
        ligne = _ligne_due(lignes, minutes)
    if ligne is None:
        return _borner(out), avertis

    if not destinataire_est(ligne, ctx):
        # L'heure est venue, mais ce n'est pas le tour du destinataire. On
        # patiente : dans la doctrine, un message s'adresse a QUELQU'UN, et
        # c'est la circulation de l'information au sein du CO que l'on teste.
        if _ETAT["attente"] != ligne["n"]:
            _ETAT["attente"] = ligne["n"]
            _ETAT["attente_depuis"] = tour
        elif tour - (_ETAT["attente_depuis"] or tour) >= ATTENTE_MAX_TOURS:
            # Le destinataire ne prend jamais la parole : plutot que de bloquer
            # le chronogramme, on remet le message a qui parle, et on le dit.
            avertis.append(
                "Plugin Chronogramme : recepteur \"%s\" jamais entendu depuis "
                "%d tours - inject remis a %s" % (ligne["recepteur"],
                                                  ATTENTE_MAX_TOURS,
                                                  (ctx or {}).get("speaker", "?")))
            _ETAT["attente"] = None
            _ETAT["livres"][ligne["n"]] = {"tour": tour, "detectee": False,
                                           "relancee": False}
            _journaliser(ctx, meta, minutes, ligne, "inject (hors destinataire)")
            return _remettre(out, ligne, ctx), avertis
        return _borner(out), avertis

    _ETAT["attente"] = None
    _ETAT["attente_depuis"] = None
    _ETAT["livres"][ligne["n"]] = {"tour": tour, "detectee": False, "relancee": False}
    _journaliser(ctx, meta, minutes, ligne, "inject")
    return _remettre(out, ligne, ctx), avertis


def _finir(out, avertis):
    """FINEX : prononce une fois, avec le bilan de pointage pour le RETEX."""
    out["PHASE_EXERCICE"] = "FINEX"
    if not _ETAT["finex_annonce"]:
        _ETAT["finex_annonce"] = True
        _ETAT["diffusion"] = None
        b = bilan()
        out["INJECT"] = ("EXERCICE TERMINE - EXERCICE TERMINE. Fin du trafic, "
                         "cloture de la main courante, passage au RETEX a chaud.")
        out["INJECT_DE"] = "DIRANIM"
        out["INJECT_VECTEUR"] = "toutes stations"
        avertis.append(
            "Plugin Chronogramme : FINEX - %d inject(s), %d reaction(s) attendue(s) "
            "obtenue(s) sur %d pointable(s), %d relance(s). Main courante : %s"
            % (b["injects"], b["reactions_obtenues"], b["reactions_pointables"],
               b["relances"], DOSSIER_SORTIE))
    return _borner(out), avertis


def _remettre(out, ligne, ctx, texte=None, mention=""):
    """Publie l'inject et arme sa diffusion si le recepteur est TOUS."""
    out.update(_publier(ligne, ctx, texte=texte, mention=mention))
    if _cle(ligne.get("recepteur")) in ("", "tous", "toutes stations",
                                        "tout le monde", "all"):
        _ETAT["diffusion"] = {"n": ligne["n"], "restant": TOURS_DIFFUSION - 1,
                              "texte": texte, "mention": mention}
    else:
        _ETAT["diffusion"] = None
    return _borner(out)


def on_message(msg, ctx):
    """SORTIE : pointe les reactions attendues et tient la main courante."""
    lignes, meta, _ = charger(_var(ctx, "CHRONOGRAMME"))
    if not lignes:
        return None
    texte = _cle((msg or {}).get("texte"))
    if not texte:
        return None

    # Une reaction attendue ne peut etre produite que par un JOUEUR : un
    # inject de l'animation qui contiendrait le motif ne vaut pas reaction.
    if _cle((msg or {}).get("speaker")) == "llm3":
        return None

    for n, suivi in _ETAT["livres"].items():
        if suivi.get("detectee"):
            continue
        ligne = _par_n(lignes, n)
        if ligne is None:
            continue
        motifs = ligne.get("detection") or []
        if any(_cle(m) and _cle(m) in texte for m in motifs):
            suivi["detectee"] = True
            _journaliser(ctx, meta, None, ligne, "reaction",
                         msg=msg, tour_msg=(msg or {}).get("tour"))
    return None


def _borner(out):
    """Ceinture et bretelles : d-IA plafonne deja, on ne lui envoie pas plus."""
    return {k: str(v)[:LONGUEUR_VALEUR] for k, v in out.items() if v not in (None, "")}


# ===========================================================================
#  Main courante de RETEX
# ===========================================================================
def _journaliser(ctx, meta, minutes, ligne, nature, msg=None, tour_msg=None):
    """Une ligne de CSV par evenement. Le document du debriefing a froid."""
    if not JOURNAL:
        return
    try:
        jour = datetime.datetime.now().strftime("%Y%m%d")
        chemin = DOSSIER_SORTIE / ("retex_chronogramme_%s.csv" % jour)
        neuf = not chemin.exists()
        with chemin.open("a", encoding="utf-8", newline="") as f:
            w = csv.writer(f, delimiter=";")
            if neuf:
                w.writerow(["horodate_reel", "heure_jeu", "tour", "nature",
                            "groupe_horaire", "vecteur", "emetteur", "recepteur",
                            "evenement", "reaction_attendue", "pointee",
                            "extrait_joueur"])
            suivi = _ETAT["livres"].get(ligne.get("n"))
            extrait = ""
            if msg:
                extrait = re.sub(r"\s+", " ", str(msg.get("texte") or ""))[:300]
            w.writerow([
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                heure_de_jeu(meta, minutes) if minutes is not None else "",
                tour_msg if tour_msg is not None else (ctx or {}).get("tour", ""),
                nature, ligne.get("groupe", ""), ligne.get("vecteur", ""),
                ligne.get("emetteur", ""), ligne.get("recepteur", ""),
                re.sub(r"\s+", " ", ligne.get("evenement", ""))[:400],
                re.sub(r"\s+", " ", ligne.get("reaction", ""))[:400],
                "oui" if (suivi or {}).get("detectee") else "non",
                extrait,
            ])
    except OSError:
        # Une main courante qui ne s'ecrit pas ne doit pas arreter l'exercice.
        pass


def bilan():
    """Bilan de pointage, pour le RETEX a chaud. Utilisable hors d-IA."""
    lignes = _CACHE["lignes"]
    total = len(_ETAT["livres"])
    pointables = sum(1 for n in _ETAT["livres"]
                     if (_par_n(lignes, n) or {}).get("detection"))
    obtenues = sum(1 for s in _ETAT["livres"].values() if s.get("detectee"))
    relances = sum(1 for s in _ETAT["livres"].values() if s.get("relancee"))
    return {"injects": total, "reactions_pointables": pointables,
            "reactions_obtenues": obtenues, "relances": relances}


# ===========================================================================
#  Autotest : ecrit un chronogramme d'exemple et le deroule a vide
# ===========================================================================
if __name__ == "__main__":
    exemple = fichier_chronogramme("autotest")
    exemple.write_text(
        "#EXERCICE=AUTOTEST\n"
        "#DEBEX=2026-07-11 14:00\n"
        "#MINUTES_PAR_TOUR=5\n"
        "groupe_horaire;vecteur;emetteur;recepteur;evenement;reaction_attendue;detection;relance\n"
        "H-15;radio;DIRANIM;TOUS;EXERCICE. Mise en ambiance : il fait {TEMPERATURE_C} C, "
        "vent {VENT_KMH} km/h. Reseaux publics hors service.;Accuse de reception des deux stations;recu|accuse;\n"
        "H;VARA FM;ANIHAUT jouant le COZ;LLM1;EXERCICE. Le COD demande un point de situation "
        "complet de Nangeville pour 14h30.;Le COD relaie la demande au PCO;point de situation;"
        "EXERCICE. Le COZ s'etonne de ne pas avoir recu le point de situation annonce.\n"
        "H+5;VARA FM;ANIBAS jouant l'EHPAD;LLM2;EXERCICE. Climatisation a l'arret depuis 11h, "
        "deux residents en hyperthermie, groupe electrogene a 4 h d'autonomie.;SITREP formate et "
        "demande chiffree;carburant|evacuation;\n"
        "RESERVE;telephone;ANIBAS jouant le maire;LLM1;EXERCICE. Le maire de Nangeville demande "
        "la conduite a tenir.;Allocation explicite;;\n",
        encoding="utf-8")
    print("Chronogramme d'exemple :", exemple)

    vars_ = {"CHRONOGRAMME": "autotest", "TEMPERATURE_C": "31.4", "VENT_KMH": "34.0"}
    for tour in range(1, 9):
        for speaker, role in (("LLM1", "COD Vaubourg"), ("LLM2", "Operateur PCO Nangeville")):
            ctx = {"tour": tour * 2 + (0 if speaker == "LLM1" else 1),
                   "speaker": speaker, "role": role, "vars": vars_,
                   "labels": {"label1": "COD Vaubourg", "label2": "Operateur PCO Nangeville"}}
            out, av = collect(ctx)
            if "INJECT" in out:
                print("  [%s] %s -> %s : %s" % (out["HEURE_JEU"], out.get("INJECT_DE"),
                                                speaker, out["INJECT"]))
            for a in av:
                print("  !", a)
    print("Bilan :", bilan())
