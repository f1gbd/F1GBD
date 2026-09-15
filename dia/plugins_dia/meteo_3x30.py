# -*- coding: utf-8 -*-
"""
============================================================================
  meteo_3x30.py - Plugin ENTREE + ACTIONS pour d-IA v1.11+
============================================================================
  Auteur  : Jean-Louis (F1GBD) - ADRASEC 77 / FNRASEC
  Version : 2.7

Historique
----------
  2.1  le releve perime est rafraichi tout seul, en tache de fond.
  2.2  coordonnees des sites verifiees (geo.api.gouv.fr) ; un releve pris a
       l'ancien point d'un site est refuse au lieu d'etre publie.
  2.3  l'acquisition est AUTOMATIQUE meme quand il n'existe AUCUN releve -
       le cas de la premiere installation. Le plugin ne demande plus a
       l'operateur de lancer "python meteo_3x30_collecte.py" : il le fait.
       La commande manuelle ne subsiste qu'en dernier recours, quand
       l'acquisition automatique est impossible (reseau coupe).
  2.4  cette acquisition automatique ne prend plus le verrou devant une mesure
       explicitement demandee : elle repondait "acquisition deja en cours", et
       le site mesure n'etait pas celui demande. Elle appartient desormais au
       seul collect(), ou personne ne viendra chercher la donnee derriere.
       Et aucune variable publiee ne depasse plus 158 caracteres, la coupe se
       faisant sur un separateur plutot qu'en plein chiffre.
  2.5  l'acquisition automatique ecrivait dans meteo_releves_<defaut>.json
       tandis que la lecture sans site nomme regardait le fichier commun : le
       plugin ne pouvait rien trouver. Repli symetrique pose. Et "acquisition
       impossible" n'est plus annonce pendant qu'une acquisition est en cours
       ou vient d'avoir lieu - relance_auto dit desormais ce qui se passe.
  2.6  declare ACTIONS_LECTURE : ses deux actions sont des CONSULTATIONS, donc
       elles s'executent en mode "lecture" de d-IA v1.11.15 - un exercice
       cadre garde un scenario fictif et des mesures vraies.
  2.7  un lieu demande mais INCONNU n'est plus replie sur le site par defaut :
       le plugin refuse, ne publie aucune valeur, et rend la liste des sites.
       Se replier revenait a publier sous le nom du site demande une mesure
       faite ailleurs - la regle de lieu de la v1.5, contournee par la porte
       de service.
  2.8  la pre-lecture de execute_action n'annonce plus "aucun releve pour X
       pour le moment" juste avant de publier le releve de X. La note reste
       la ou elle est vraie (collect, lecture seule) ; elle disparait des que
       l'acquisition a eu lieu dans le meme appel.

Objet
-----
Injecte dans le dialogue les parametres meteorologiques reels issus du modele
AROME France HD de Meteo-France (~1,5 km), et l'etat de la REGLE DES 3 x 30 :

      temperature >= 30 C   ET   vent >= 30 km/h   ET   humidite <= 30 %

Les trois criteres reunis caracterisent un danger extreme de feu de vegetation.
C'est un critere de vigilance operationnelle, pas une prevision : il decrit la
situation au moment du releve.

Les seuils et le calcul sont ceux de meteo_lib.py, la bibliotheque meteo deja
utilisee par TCQ pour la couche meteo de la carte. Quand meteo_lib est
accessible, ce plugin l'IMPORTE et appelle sa fonction rule_3x30() : une seule
implementation de la regle pour TCQ et pour d-IA. Sinon, il applique une copie
locale strictement identique.

Actions exposees aux LLM
------------------------
    ACTION: mesure_meteo(lieu=melun)
    ACTION: releve_meteo_maintenant(lieu=melun)
    ATTENDRE: RELEVE_AGE_MIN < 2 delai=300
    ATTENDRE: REGLE_3X30 contient ATTEINTE delai=1800

REGLE DE LIEU (v1.5) - un releve appartient a UN site, et a un seul. Si l'on
demande mesure_meteo(lieu=melun) alors que le dernier releve concerne
Nangeville, le plugin ne rend PAS les valeurs de Nangeville : il lance une
acquisition sur Melun et le dit. Autrement le modele attribuerait a Melun des
mesures faites ailleurs - une erreur qui, sur une regle de danger de feu, n'est
pas acceptable.

Source des donnees
------------------
Le plugin NE VA JAMAIS SUR LE RESEAU : il lit un fichier local,
"meteo_releves.json", ecrit par le collecteur "meteo_3x30_collecte.py"
(livre a cote), qui interroge Open-Meteo en modele AROME France HD. C'est la
regle d'or du contrat d-IA : un plugin lit ce qui est deja la, il n'attend
jamais un service distant pendant un tour de dialogue (budget : 2 secondes).

  meteo_3x30_collecte.py  --->  meteo_releves.json  --->  meteo_3x30.py
  (tache planifiee, ou                (local)              (plugin d-IA)
   ACTION d'un LLM)

Variables produites
-------------------
  TEMPERATURE_C    temperature de l'air (degres Celsius)
  VENT_KMH         vent moyen a 10 m (km/h)
  RAFALES_KMH      rafales a 10 m (km/h)
  HUMIDITE_PCT     humidite relative (%)
  REGLE_3X30       etat de la regle : ATTEINTE (3/3) / 2 sur 3 / ...
  CRITERES_3X30    detail critere par critere
  LIEU_METEO       lieu du releve (nom, latitude, longitude)
  RELEVE_AGE_MIN   anciennete du releve, en minutes
============================================================================
"""

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import threading
import time
import unicodedata
from pathlib import Path

PLUGIN_NAME = "Meteo 3x30 (AROME France HD)"
PLUGIN_VERSION = "2.8"

# --- Seuils de la regle des 3 x 30 (identiques a meteo_lib.py de TCQ) ------
R3_TEMP = 30.0      # C    : temperature >= 30
R3_WIND = 30.0      # km/h : vent >= 30
R3_HUM = 30.0       # %    : humidite <= 30

# Les SEUILS sont publies avec les valeurs, jamais sous-entendus. Sans eux, le
# modele les invente : observe en seance, un mistral-nemo a conclu que la regle
# n'etait pas remplie parce que "l'humidite est inferieure a 80 %" - un seuil
# qui n'existe nulle part. Une valeur ne se juge pas sans son critere.
RAPPEL_REGLE = (f"T >= {R3_TEMP:g} C ET vent >= {R3_WIND:g} km/h "
                f"ET HR <= {R3_HUM:g} %")

# --- Emplacement du releve -------------------------------------------------
# Par defaut, le releve est lu A COTE DE CE FICHIER. Chaque installation de
# d-IA a donc son propre dossier plugins_dia\ et son propre releve : c'est le
# comportement le plus previsible, et celui d'un poste unique.
#
# Pour PARTAGER un meme releve entre plusieurs installations (source, dossier
# dist, poste compile, autre machine sur un partage reseau), designez un
# emplacement commun. Ordre de priorite :
#   1. la variable d'environnement DIA_METEO_RELEVES  (la plus souple : elle
#      vaut pour le plugin ET pour le collecteur, sans modifier un fichier) ;
#   2. la constante CHEMIN_RELEVES_PARTAGE ci-dessous ;
#   3. a defaut, meteo_releves.json a cote de ce plugin.
#
# Exemples :
#   CHEMIN_RELEVES_PARTAGE = r"C:\ADRASEC\meteo\meteo_releves.json"
#   setx DIA_METEO_RELEVES "C:\ADRASEC\meteo\meteo_releves.json"
CHEMIN_RELEVES_PARTAGE = ""

VAR_ENV_RELEVES = "DIA_METEO_RELEVES"

# --- Sites connus ----------------------------------------------------------
# Un LLM ne connait pas les coordonnees d'une commune, et il ne doit pas les
# inventer. On lui donne donc une liste de sites NOMMES : il ecrit
#     ACTION: releve_meteo_maintenant(lieu=melun)
# et le plugin resout les coordonnees. La liste est publiee dans les DONNEES
# DE SITUATION (variable SITES_METEO), donc le modele sait ce qu'il peut
# demander. Ajoutez ici les sites de votre departement.
#     cle (sans accent, minuscules) : (latitude, longitude, libelle affiche)
# Coordonnees : centre de la commune, API Geo de l'Etat (geo.api.gouv.fr),
# verifiees le 14/09/2026. Le code INSEE permet de les recontroler.
#
# NANGEVILLE est une commune FICTIVE du scenario HELIOS NOIR 26. Elle n'a donc
# pas de meteo. Le releve est pris sur un point REEL, nomme dans le libelle :
# tout ce que le plugin publie doit pouvoir etre verifie. Pour deplacer le
# point de reference, une seule ligne a changer.
SITES = {
    # cle              lat       lon     libelle                        INSEE
    "nangeville": (48.5575, 3.0079,
                   "Nangeville (site fictif - mesure reelle a "
                   "Nangis 77)"),                                     # 77327
    "melun": (48.5421, 2.6552, "Melun (prefecture 77)"),              # 77288
    "fontainebleau": (48.4236, 2.6817, "Fontainebleau"),              # 77186
    "provins": (48.5629, 3.2845, "Provins"),                          # 77379
    "coulommiers": (48.8096, 3.0918, "Coulommiers"),                  # 77131
    "nemours": (48.2633, 2.7187, "Nemours"),                          # 77333
}


def controler_sites():
    """Deux sites au meme point rendraient la meme mesure sous deux noms.

    C'est le defaut le plus difficile a voir a la lecture d'un fil : les
    valeurs sont plausibles, elles sont seulement attribuees a un lieu qui
    n'a pas ete mesure. Le controle est fait au chargement, une fois.
    """
    vus, avertis = {}, []
    for cle, (lat, lon, _) in SITES.items():
        vus.setdefault((round(lat, 4), round(lon, 4)), []).append(cle)
    for (lat, lon), cles in sorted(vus.items()):
        if len(cles) > 1:
            avertis.append(
                "Plugin Meteo 3x30 : %s partagent le point (%.4f, %.4f) - "
                "un releve serait attribue a un site qui n'a pas ete mesure"
                % (" et ".join(sorted(cles)), lat, lon))
    return avertis


_AV_SITES = controler_sites()
_AV_SITES_DIT = False


def _avertis_sites():
    """Les anomalies de la table, dites UNE fois par seance."""
    global _AV_SITES_DIT
    if _AV_SITES_DIT or not _AV_SITES:
        return []
    _AV_SITES_DIT = True
    return list(_AV_SITES)
SITE_DEFAUT = "nangeville"


def _cle_site(texte):
    """Normalise un nom de lieu : sans accent, minuscules, sans ponctuation."""
    brut = unicodedata.normalize("NFD", str(texte or ""))
    brut = "".join(c for c in brut if unicodedata.category(c) != "Mn")
    return "".join(c for c in brut.lower() if c.isalnum())


def resoudre_site(params):
    """Determine le point a relever a partir des parametres d'une directive.

    Retourne (lat, lon, libelle, avertissements), ou (None, None, None, avertis)
    quand le lieu demande est INCONNU.

      1. lat= et lon= fournis explicitement ;
      2. lieu= correspondant a un site connu ;
      3. aucun lieu demande -> site par defaut ;
      4. lieu demande mais INCONNU -> on REFUSE (v2.7).

    Le cas 4 se repliait sur le site par defaut, en le disant. Ce n'etait pas
    suffisant. Seance du 15/09 a 12:30 : le COD demande chateau_d_eau, le
    plugin releve Nangeville et publie LIEU_DEMANDE = Nangeville. Le modele a
    donc recu, sous le nom du site qu'il avait demande, une mesure faite
    ailleurs - exactement ce que la REGLE DE LIEU (v1.5) existe pour empecher.
    Un avertissement dans le fil ne repare pas une variable fausse : le modele
    lit les variables, pas les avertissements.

    On refuse donc, et on rend la liste des sites connus. Le modele choisira.
    Mieux vaut une mesure absente qu'une mesure attribuee au mauvais lieu -
    sur une regle de danger de feu, la difference n'est pas academique.
    """
    avertis = []
    lat, lon = params.get("lat"), params.get("lon")
    lieu = (params.get("lieu") or params.get("site") or "").strip()
    if lat not in (None, "") and lon not in (None, ""):
        try:
            return (float(lat), float(lon),
                    lieu or f"point {float(lat):.2f}, {float(lon):.2f}", avertis)
        except (TypeError, ValueError):
            avertis.append(f"coordonnees illisibles ({lat}, {lon})")
    if lieu:
        cle = _cle_site(lieu)
        if cle in SITES:
            la, lo, libelle = SITES[cle]
            return la, lo, libelle, avertis
        # Seconde chance : le modele renvoie souvent le LIBELLE COMPLET, celui
        # que le plugin lui a lui-meme publie dans LIEU_METEO - "Melun
        # (prefecture 77)". Refuser ce qu'on vient de lui donner serait
        # absurde, et depuis la v2.7 le refus n'est plus anodin : il annule la
        # mesure. (Defaut trouve au banc en ecrivant le test du refus.)
        cle = _LIBELLE_VERS_CLE.get(lieu.strip()) or cle_du_libelle(lieu)
        if cle in SITES:
            la, lo, libelle = SITES[cle]
            return la, lo, libelle, avertis
        avertis.append(
            "site inconnu : %s - AUCUN releve n'est fait, pour ne pas "
            "attribuer a ce lieu une mesure prise ailleurs. Sites connus : %s"
            % (lieu, ", ".join(sorted(SITES))))
        return None, None, None, avertis
    la, lo, libelle = SITES[SITE_DEFAUT]
    return la, lo, libelle, avertis


def meme_site(libelle_canonique, lieu_demande, data):
    """Le releve lu concerne-t-il bien le site demande ?

    On compare des cles normalisees. Deux ecritures doivent concorder :
      - le libelle canonique du site ("Melun (prefecture 77)"), qui est celui
        que le plugin ecrit lui-meme quand il declenche une acquisition ;
      - le nom court tape par le modele ("melun"), en debut de cle, pour les
        relevs ecrits a la main avec --lieu.
    """
    cle_releve = _cle_site((data or {}).get("lieu"))
    if not cle_releve:
        return False
    concorde = cle_releve == _cle_site(libelle_canonique)
    if not concorde:
        cle_demande = _cle_site(lieu_demande)
        concorde = bool(cle_demande) and cle_releve.startswith(cle_demande)
    return concorde and _point_concorde(libelle_canonique, data)


# Un site peut CHANGER de coordonnees (correction d'une erreur de saisie,
# deplacement d'un point de reference). Le releve deja sur disque porte alors
# l'ancien point sous le bon nom : le nom concorde, la mesure non. On le
# refuse, et une acquisition neuve est declenchee.
TOLERANCE_DEG = 0.02          # ~2 km, au-dela de la maille AROME (~1,3 km)


def _point_concorde(libelle_canonique, data):
    """Le releve a-t-il ete pris la ou le site se trouve AUJOURD'HUI ?"""
    cle = _LIBELLE_VERS_CLE.get(libelle_canonique)
    if not cle or cle not in SITES:
        return True                      # site hors table : rien a comparer
    lat_site, lon_site, _ = SITES[cle]
    try:
        lat = float((data or {}).get("lat"))
        lon = float((data or {}).get("lon"))
    except (TypeError, ValueError):
        return True                      # releve ancien, sans coordonnees
    return (abs(lat - lat_site) <= TOLERANCE_DEG
            and abs(lon - lon_site) <= TOLERANCE_DEG)


def resoudre_fichier_releves():
    """Chemin du releve, selon l'ordre de priorite documente ci-dessus."""
    for candidat in (os.environ.get(VAR_ENV_RELEVES, ""),
                     CHEMIN_RELEVES_PARTAGE):
        candidat = (candidat or "").strip().strip('"')
        if candidat:
            return Path(candidat).expanduser()
    return Path(__file__).with_name("meteo_releves.json")


FICHIER_RELEVES = resoudre_fichier_releves()
COLLECTEUR = Path(__file__).with_name("meteo_3x30_collecte.py")

# Correspondance libelle -> cle courte, pour retrouver "melun" a partir de
# "Melun (prefecture 77)".
_LIBELLE_VERS_CLE = {libelle: cle for cle, (_, _, libelle) in SITES.items()}


def cle_du_libelle(libelle):
    """Cle courte d'un site a partir de son libelle affiche."""
    return _LIBELLE_VERS_CLE.get(libelle) or _cle_site(libelle)


def fichier_releves(cle=None):
    """Chemin du releve d'UN site (v2.0).

    Un releve appartient a un seul site : lui donner son propre fichier est la
    suite logique de la regle de lieu. Sans cle, on retombe sur le fichier
    commun, qui reste celui des installations existantes et des lancements
    manuels du collecteur sans --site.

        meteo_releves.json             site non precise / historique
        meteo_releves_melun.json       site "melun"
        meteo_releves_fontainebleau.json

    C'est ce qui rend la comparaison possible : deux mesures successives ne
    s'ecrasent plus l'une l'autre.
    """
    if not cle:
        return FICHIER_RELEVES
    return FICHIER_RELEVES.with_name(
        f"{FICHIER_RELEVES.stem}_{cle}{FICHIER_RELEVES.suffix}")


# Dernier site mesure pendant cette seance : c'est celui dont collect()
# publie le detail, les autres n'ayant droit qu'a une ligne de resume.
_DERNIER_SITE = None

# Les variables de fond de tableau passent en DERNIER : si d-IA tronque a
# PLUGIN_MAX_VARS, ce sont elles qui sautent, pas le resultat de la mesure.
_VARS_EN_QUEUE = ("SITES_METEO", "METEO_AUTRES_SITES")


# Plafond du contrat d-IA (PLUGIN_VAR_MAX_LEN). On coupe ICI, pas chez d-IA :
# lui tronque a l'aveugle, au milieu d'un nombre - et une valeur coupee en
# plein chiffre n'est pas une valeur incomplete, c'est une valeur FAUSSE.
LONGUEUR_VALEUR = 158


def _borner(valeur):
    """Ramene une valeur sous LONGUEUR_VALEUR, en coupant proprement (v2.4).

    On coupe de preference sur le dernier separateur d'enumeration : mieux
    vaut trois sites complets qu'un quatrieme ampute de sa temperature.
    """
    texte = str(valeur)
    if len(texte) <= LONGUEUR_VALEUR:
        return texte
    tronque = texte[:LONGUEUR_VALEUR - 1]
    for sep in (" ; ", ", "):
        i = tronque.rfind(sep)
        if i > LONGUEUR_VALEUR // 3:
            return tronque[:i] + "\u2026"
    return tronque.rstrip() + "\u2026"


def _ordonner(out):
    for cle in _VARS_EN_QUEUE:
        if cle in out:
            out[cle] = out.pop(cle)
    # Entonnoir unique de publication : rien ne sort d'ici hors gabarit.
    for cle in list(out):
        out[cle] = _borner(out[cle])
    return out

# Au-dela, le releve est signale comme perime (AROME est horaire).
AGE_MAX_MIN = 90

# En deca, un releve du bon site est rendu tel quel sans redeclencher une
# acquisition. Ce seuil est VOLONTAIREMENT bas, et c'est la lecon d'une seance
# perdue : avec un seuil de 20 min, un releve de Melun vieux de 16 min etait
# juge frais, aucune acquisition n'etait lancee - et le modele, qui avait ecrit
# ATTENDRE: RELEVE_AGE_MIN < 2, scrutait pendant 600 s un compteur qui ne
# pouvait que MONTER. Une attente doit toujours pouvoir aboutir : soit on
# rafraichit, soit on dit clairement qu'il n'y a rien a attendre.
AGE_FRAIS_MIN = 2

# --- Reutilisation de meteo_lib (TCQ) quand elle est accessible ------------
_CHEMINS_METEO_LIB = (
    Path(__file__).resolve().parent,
    Path(__file__).resolve().parent.parent,
    Path(r"H:\QITdevsrc\TCQ"),
)
_meteo_lib = None
for _p in _CHEMINS_METEO_LIB:
    try:
        if (_p / "meteo_lib.py").is_file():
            if str(_p) not in sys.path:
                sys.path.insert(0, str(_p))
            import meteo_lib as _meteo_lib   # noqa: E402
            break
    except Exception:
        _meteo_lib = None


# ---------------------------------------------------------------------------
#  Acquisition en arriere-plan
# ---------------------------------------------------------------------------
# ATTENTION AU MODE COMPILE : dans un exe PyInstaller, sys.executable vaut
# d-IA.exe et NON python.exe. Lancer le collecteur par subprocess avec
# sys.executable echoue donc ([WinError 50] sous Windows).
#
# On procede dans cet ordre :
#   1. on IMPORTE le collecteur (c'est du Python pur, bibliotheque standard)
#      et on le fait tourner dans un THREAD DEMON : cela fonctionne en source
#      comme en compile, sans fenetre console, et l'action rend la main tout
#      de suite ;
#   2. a defaut seulement, on retombe sur un sous-processus, avec un vrai
#      interpreteur Python cherche dans le PATH (jamais sys.executable si
#      l'application est gelee).
#
# Le resultat de l'acquisition n'est pas attendu : le LLM le constate ensuite
# avec ATTENDRE: RELEVE_AGE_MIN < 2.

_ACQ = {"en_cours": False, "erreur": "", "depuis": 0.0}
_ACQ_VERROU = threading.Lock()


def _charger_collecteur():
    """Importe meteo_3x30_collecte.py comme un module. None si impossible."""
    try:
        if not COLLECTEUR.is_file():
            return None
        spec = importlib.util.spec_from_file_location(
            "meteo_3x30_collecte", COLLECTEUR)
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception:
        return None


def _interpreteur_python():
    """Chemin d'un vrai interpreteur Python, ou None.

    En mode compile, sys.executable est l'exe de l'application : on ne
    l'utilise donc QUE si l'application tourne depuis les sources.
    """
    if not getattr(sys, "frozen", False):
        return sys.executable
    for nom in ("python", "python3", "py"):
        chemin = shutil.which(nom)
        if chemin:
            return chemin
    return None


def _acquisition_thread(module, lat, lon, libelle, cible=None):
    """Corps du thread d'acquisition (reseau). Ne leve jamais."""
    try:
        point = module.relever(lat, lon)
        module.ecrire_releve(
            point, libelle,
            "Open-Meteo / AROME France HD (Meteo-France)",
            cible or FICHIER_RELEVES)
        with _ACQ_VERROU:
            _ACQ["erreur"] = ""
    except Exception as e:
        with _ACQ_VERROU:
            _ACQ["erreur"] = f"acquisition AROME echouee : {e}"
    finally:
        with _ACQ_VERROU:
            _ACQ["en_cours"] = False


def lancer_acquisition(lat, lon, libelle, cible=None):
    """Demarre une acquisition. Retourne (ok, message, avertissements)."""
    cible = cible or FICHIER_RELEVES
    with _ACQ_VERROU:
        if _ACQ["en_cours"] and (time.time() - _ACQ["depuis"]) < 120:
            return True, "acquisition deja en cours", []
        _ACQ["en_cours"] = True
        _ACQ["depuis"] = time.time()
        _ACQ["erreur"] = ""

    module = _charger_collecteur()
    if module is not None and hasattr(module, "relever"):
        threading.Thread(
            target=_acquisition_thread,
            args=(module, lat, lon, libelle, cible),
            daemon=True, name="meteo3x30-acquisition").start()
        return True, f"acquisition AROME lancee sur {libelle}", []

    # Repli : sous-processus, avec un interpreteur Python reel.
    python = _interpreteur_python()
    if not python:
        with _ACQ_VERROU:
            _ACQ["en_cours"] = False
        return (False, "aucun moyen de lancer l'acquisition",
                ["collecteur non importable et aucun interpreteur Python "
                 "trouve : lancez meteo_3x30_collecte.py a la main, ou par une "
                 "tache planifiee"])
    cmd = [python, str(COLLECTEUR), "--sortie", str(cible),
           "--lat", str(lat), "--lon", str(lon), "--lieu", libelle]
    kwargs = {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
    if sys.platform == "win32":
        # Pas de fenetre console qui surgit devant l'operateur en pleine seance.
        kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    try:
        subprocess.Popen(cmd, **kwargs)
    except Exception as e:
        with _ACQ_VERROU:
            _ACQ["en_cours"] = False
        return False, "echec du lancement de l'acquisition", [str(e)]
    finally:
        with _ACQ_VERROU:
            _ACQ["en_cours"] = False      # le sous-processus vit sa vie
    return True, f"acquisition AROME lancee sur {libelle} (sous-processus)", []


# Duree que l'ACTION s'autorise a attendre l'acquisition. d-IA accorde 10 s a
# une action (PLUGIN_ACTION_TIMEOUT_S) et seulement 2 s a un collect() : rien
# n'obligeait donc l'action a rendre la main tout de suite. Une requete
# Open-Meteo aboutit en general en moins d'une seconde ; on l'attend, et le
# modele repart avec la mesure dans le meme tour au lieu d'enchainer une
# attente. Si le reseau traine, le thread continue en fond et on retombe sur
# l'ancien comportement.
ACQ_SYNC_TIMEOUT_S = 6.0


def _court(texte, n=90):
    texte = str(texte or "").replace("\n", " ").strip()
    return texte if len(texte) <= n else texte[:n - 3].rstrip() + "..."


def acquerir(lat, lon, libelle, attente_s=ACQ_SYNC_TIMEOUT_S, cible=None):
    """Acquisition avec attente bornee.

    Retourne (etat, message, avertissements), etat parmi :
      "faite"    - le releve est ecrit, il n'y a plus qu'a le relire ;
      "en_cours" - trop long, le thread poursuit : le modele devra attendre ;
      "echouee"  - le reseau ou l'API a refuse, et on DIT pourquoi.
    """
    module = _charger_collecteur()
    if module is None or not hasattr(module, "relever"):
        ok, message, avertis = lancer_acquisition(lat, lon, libelle, cible)
        return ("en_cours" if ok else "echouee"), message, avertis

    with _ACQ_VERROU:
        if _ACQ["en_cours"] and (time.time() - _ACQ["depuis"]) < 120:
            return "en_cours", "acquisition deja en cours", []
        _ACQ["en_cours"] = True
        _ACQ["depuis"] = time.time()
        _ACQ["erreur"] = ""

    fil = threading.Thread(target=_acquisition_thread,
                           args=(module, lat, lon, libelle, cible),
                           daemon=True, name="meteo3x30-acquisition")
    fil.start()
    fil.join(max(0.5, float(attente_s)))
    if fil.is_alive():
        return "en_cours", f"acquisition AROME en cours sur {libelle}", []
    with _ACQ_VERROU:
        erreur = _ACQ["erreur"]
    if erreur:
        return "echouee", _court(erreur), [erreur]
    return "faite", f"releve {libelle} obtenu a l'instant", []


# ---------------------------------------------------------------------------
#  Rafraichissement automatique (v2.1)
# ---------------------------------------------------------------------------
# Un releve perime le restait jusqu'a ce qu'un humain pense a relancer le
# collecteur - ou jusqu'a ce qu'un LLM y pense, ce qu'il ne fait pas : il lit
# "releve vieux de 90 min" comme une information, pas comme une consigne.
# Attendre d'un modele qu'il joue le role d'une tache planifiee n'est pas
# raisonnable ; c'est au plugin de tenir ses donnees a jour.
#
# La regle des 2 secondes n'est pas enfreinte : collect() ne va toujours PAS
# sur le reseau. Il DEMARRE une acquisition en tache de fond et rend la main
# immediatement - la meme mecanique que celle d'une action, sans l'attente.
RELANCE_AUTO_MIN = 10.0        # jamais plus d'une relance auto par site et par
                               # tranche de 10 min, pour ne pas marteler l'API
_DERNIERE_RELANCE_AUTO = {}


def relance_auto(cle, data=None):
    """Acquiert un site en arriere-plan. Non bloquant, throttlee.

    Sert dans deux cas :
      - le releve est PERIME (trop vieux, ou pris a l'ancien point du site) ;
      - il n'y en a AUCUN, ce qui est le cas de toute premiere installation.

    Le second cas etait traite en disant a l'operateur de lancer le collecteur
    a la main. C'etait lui demander de reparer une chose que le plugin sait
    faire seul - et precisement au moment ou il ne peut pas le deviner. Un
    plugin dont la source de donnees est absente doit aller la chercher, pas
    rediger une consigne.

    Retourne le texte a joindre a l'avertissement - y compris quand rien n'a
    ete lance PARCE QU'une acquisition est deja en route. C'est la correction
    de la v2.5 : rendre None dans ce cas faisait annoncer "acquisition
    impossible (reseau coupe)" trente-huit secondes apres en avoir lance une,
    et envoyait l'operateur chercher une panne qui n'existait pas. None est
    reserve au seul cas ou il n'y a vraiment plus rien a attendre.
    """
    with _ACQ_VERROU:
        if _ACQ["en_cours"]:
            depuis = time.time() - (_ACQ.get("depuis") or time.time())
            return ("acquisition deja en cours depuis %d s" % int(depuis))
    reference = cle or ""
    ecoule = time.time() - _DERNIERE_RELANCE_AUTO.get(reference, 0.0)
    if ecoule < RELANCE_AUTO_MIN * 60:
        # Garde-fou anti-martelement : on ne relance pas, mais une acquisition
        # a bien eu lieu recemment - ce n'est pas une panne.
        return ("acquisition lancee il y a %d s ; prochaine relance possible "
                "dans %d min" % (int(ecoule), int(RELANCE_AUTO_MIN - ecoule / 60)))

    if cle in SITES:
        lat, lon, libelle = SITES[cle]
    else:
        # Pas de site nomme : on reprend le point du releve lui-meme, faute de
        # quoi on relancerait sur des coordonnees arbitraires.
        lat, lon = (data or {}).get("lat"), (data or {}).get("lon")
        libelle = str((data or {}).get("lieu") or "").strip() or "point du releve"
        if lat is None or lon is None:
            return None

    _DERNIERE_RELANCE_AUTO[reference] = time.time()
    ok, _message, _avertis = lancer_acquisition(lat, lon, libelle,
                                                fichier_releves(cle))
    if not ok:
        return None
    return f"acquisition relancee automatiquement sur {libelle}"


def list_variables():
    return [
        ("TEMPERATURE_C", "Temperature de l'air (degres Celsius)"),
        ("VENT_KMH", "Vent moyen a 10 m (km/h)"),
        ("RAFALES_KMH", "Rafales a 10 m (km/h)"),
        ("HUMIDITE_PCT", "Humidite relative (%)"),
        ("REGLE_3X30", "Etat de la regle des 3 x 30 (danger de feu)"),
        ("CRITERES_3X30", "Detail critere par critere"),
        ("LIEU_METEO", "Lieu du releve (nom, latitude, longitude)"),
        ("LIEU_DEMANDE", "Site demande par la derniere action de mesure"),
        ("RELEVE_AGE_MIN", "Anciennete du releve, en minutes"),
        ("SITES_METEO", "Sites que l'on peut demander a relever"),
        ("METEO_AUTRES_SITES", "Resume des autres sites deja releves"),
    ]


# Actions de CONSULTATION (contrat d-IA v1.11.15). En mode "lecture", d-IA
# n'execute que celles-ci : le scenario peut etre fictif, la mesure reste
# vraie. Les deux actions de ce plugin INTERROGENT Open-Meteo et ecrivent un
# fichier de releve ; aucune ne commande quoi que ce soit. Un plugin qui
# piloterait un relais, un emetteur ou un groupe electrogene ne declarerait
# evidemment rien ici.
ACTIONS_LECTURE = ("mesure_meteo", "releve_meteo_maintenant")


def list_actions():
    """Contrat identique aux plugins IAbrain : 3 elements par tuple."""
    return [
        ("mesure_meteo",
         "Mesurer la meteo d'un site : mesure_meteo(lieu=<site connu>) - "
         "unique action de mesure : temperature, vent, humidite ET regle 3x30 "
         "sont fournis ensemble",
         "Mesure le site demande et rend les valeurs DANS LA MEME REPONSE : "
         "en general il n'y a rien a attendre. LIRE MESURE_RESULTAT : s'il "
         "annonce une acquisition en cours, ecrire alors "
         "ATTENDRE: RELEVE_AGE_MIN < 2 delai=300 ; s'il annonce un echec, le "
         "dire sans inventer de valeurs. Ne rend jamais le releve d'un autre "
         "site."),
        ("releve_meteo_maintenant",
         "Declencher une acquisition AROME sur un site : "
         "releve_meteo_maintenant(lieu=<site connu>)",
         "Lance le collecteur en arriere-plan (Open-Meteo / AROME). Le resultat "
         "n'est pas immediat : attendre ensuite avec "
         "ATTENDRE: RELEVE_AGE_MIN < 2 delai=300."),
    ]


# ---------------------------------------------------------------------------
#  Logique metier (testable sans d-IA)
# ---------------------------------------------------------------------------
def regle_3x30(temp_c, vent_kmh, hum_pct):
    """Evalue la regle des trois 30. Delegue a meteo_lib quand disponible.

    Retourne le meme dict que meteo_lib.rule_3x30 :
    {"temp": bool, "wind": bool, "hum": bool, "count": int, "ok": bool}
    """
    if _meteo_lib is not None and hasattr(_meteo_lib, "rule_3x30"):
        try:
            return _meteo_lib.rule_3x30(temp_c, vent_kmh, hum_pct)
        except Exception:
            pass
    t = temp_c is not None and temp_c >= R3_TEMP
    w = vent_kmh is not None and vent_kmh >= R3_WIND
    h = hum_pct is not None and hum_pct <= R3_HUM
    return {"temp": bool(t), "wind": bool(w), "hum": bool(h),
            "count": int(t) + int(w) + int(h), "ok": bool(t and w and h)}


def formuler_3x30(r3, temp_c, vent_kmh, hum_pct):
    """Traduit le dict de la regle en deux valeurs lisibles par un LLM."""
    if r3.get("ok"):
        etat = "ATTEINTE (3/3) - danger extreme de feu de vegetation"
    else:
        etat = f"{r3.get('count', 0)} critere(s) sur 3"
        if r3.get("count") == 2:
            etat += " - vigilance elevee"
    etat += f" [regle : {RAPPEL_REGLE}]"

    def _c(libelle, valeur, ok, unite, seuil):
        if valeur is None:
            return f"{libelle} inconnu"
        return (f"{libelle} {valeur:g}{unite} (seuil {seuil}) "
                f"{'OUI' if ok else 'non'}")

    detail = " / ".join([
        _c("temperature", temp_c, r3.get("temp"), " C", f">= {R3_TEMP:g}"),
        _c("vent", vent_kmh, r3.get("wind"), " km/h", f">= {R3_WIND:g}"),
        _c("humidite", hum_pct, r3.get("hum"), " %", f"<= {R3_HUM:g}"),
    ])
    return etat, detail


def _nombre(valeur):
    try:
        return float(valeur)
    except (TypeError, ValueError):
        return None


def _lire_releve(chemin=None):
    """Lit un fichier de releve. Retourne (dict|None, age_minutes|None)."""
    chemin = Path(chemin) if chemin else FICHIER_RELEVES
    if not chemin.exists():
        return None, None
    try:
        data = json.loads(chemin.read_text(encoding="utf-8"))
    except Exception:
        return None, None
    if not isinstance(data, dict):
        return None, None
    age_min = None
    try:
        age_min = max(0.0, (time.time() - chemin.stat().st_mtime) / 60.0)
    except Exception:
        pass
    return data, age_min


def _resume_site(cle, data, age_min):
    """Une ligne compacte pour un site que l'on ne detaille pas."""
    t = _nombre(data.get("temperature_c"))
    v = _nombre(data.get("vent_kmh"))
    h = _nombre(data.get("humidite_pct"))
    r3 = regle_3x30(t, v, h)
    def _n(x, u):
        return f"{x:g}{u}" if x is not None else "?"
    age = f"{age_min:.0f} min" if age_min is not None else "age inconnu"
    return (f"{cle} T {_n(t, ' C')} vent {_n(v, ' km/h')} HR {_n(h, ' %')} "
            f"3x30 {r3.get('count', 0)}/3 ({age})")


def resumes_autres_sites(cle_courante, limite=3):
    """Resume des AUTRES sites deja releves, du plus recent au plus ancien.

    C'est ce qui permet une comparaison : apres avoir mesure Melun puis
    Fontainebleau, le modele voit le detail du second ET une ligne pour le
    premier, au lieu de voir le premier ecrase par le second.
    """
    trouves = []
    for cle in SITES:
        if cle == cle_courante:
            continue
        data, age_min = _lire_releve(fichier_releves(cle))
        if data is None:
            continue
        trouves.append((age_min if age_min is not None else 1e9, cle,
                        _resume_site(cle, data, age_min)))
    trouves.sort()
    return [r for _, _, r in trouves[:max(0, int(limite))]]


NOTE_ABSENCE = "aucun releve pour "     # prefixe des notes provisoires


def _sans_note_absence(avertis):
    """Retire les notes d'absence qu'une acquisition vient de dementir (v2.8).

    _variables_depuis_releve() signale qu'il n'y a pas encore de releve. C'est
    utile la ou personne ne va combler l'absence : collect(), ou une lecture
    qui s'arrete la. Ce n'est plus vrai quand l'appelant enchaine sur une
    acquisition : le fil affichait alors "aucun releve pour coulommiers pour
    le moment" une ligne avant la valeur de Coulommiers. Une absence annoncee
    et resolue dans le meme tour n'informe pas, elle egare. (Seance du 15/09.)
    """
    return [a for a in avertis if not str(a).startswith(NOTE_ABSENCE)]


def _variables_depuis_releve(cle=None, acquerir_si_absent=False):
    """Construit (variables, avertissements) pour UN site.

    cle = None : le fichier commun (comportement d'avant la v2.0).

    acquerir_si_absent (v2.4) : lancer une acquisition quand il n'y a rien a
    publier. RESERVE a collect(), ou personne ne viendra chercher la donnee
    derriere nous. Les actions, elles, acquierent ELLES-MEMES juste apres :
    si cette lecture prenait le verrou, la mesure explicitement demandee se
    verrait repondre "acquisition deja en cours" et le LLM recevrait les
    valeurs d'un autre site que celui qu'il a demande. Un automatisme de
    confort ne passe jamais devant une demande explicite.
    """
    chemin = fichier_releves(cle)
    data, age_min = _lire_releve(chemin)
    if data is None and not cle and SITE_DEFAUT in SITES:
        # v2.5 : sans site nomme, on lit le fichier COMMUN - mais
        # l'acquisition automatique, elle, se rabat sur SITE_DEFAUT et ecrit
        # donc dans meteo_releves_<defaut>.json. Le plugin acquerait dans un
        # fichier et regardait dans un autre : il ne pouvait rien trouver.
        # Le repli symetrique (site -> fichier commun) existait deja pour les
        # installations d'avant la v2.0 ; celui-ci manquait.
        chemin_defaut = fichier_releves(SITE_DEFAUT)
        data_d, age_d = _lire_releve(chemin_defaut)
        if data_d is not None:
            data, age_min, chemin, cle = data_d, age_d, chemin_defaut, SITE_DEFAUT
    if data is None and cle:
        # Repli sur le fichier commun, mais SEULEMENT s'il concerne ce site :
        # c'est ce qui permet a une installation d'avant la v2.0 de continuer
        # a fonctionner sans rien deplacer.
        data_c, age_c = _lire_releve(FICHIER_RELEVES)
        if data_c is not None and meme_site(
                SITES.get(cle, (0, 0, cle))[2], cle, data_c):
            data, age_min, chemin = data_c, age_c, FICHIER_RELEVES
    ecarte = None
    if data is not None and cle and not _point_concorde(
            SITES.get(cle, (0, 0, cle))[2], data):
        # Le fichier porte le bon nom, mais la mesure a ete prise ailleurs :
        # les coordonnees du site ont change depuis. On ne publie rien, et on
        # dit pourquoi - une acquisition neuve remettra les choses en ordre.
        lat_s, lon_s, _ = SITES[cle]
        ecarte = ("releve de %s pris a (%s, %s) alors que le site est a "
                  "(%.4f, %.4f) - releve perime, ignore"
                  % (cle, data.get("lat"), data.get("lon"), lat_s, lon_s))
        data = None

    if data is None:
        # On nomme le chemin ATTENDU : c'est la question que tout le monde se
        # pose la premiere fois (d-IA lit le fichier a cote du plugin, donc a
        # cote de l'exe en version compilee, et non dans le dossier source).
        manque = {"SITES_METEO": ", ".join(sorted(SITES))}
        autres = resumes_autres_sites(cle, limite=3)
        if autres:
            manque["METEO_AUTRES_SITES"] = " ; ".join(autres)
        # Aucune donnee publiable : on va la chercher. Sans site nomme, on
        # prend SITE_DEFAUT - c'est celui de la commune-pilote de l'exercice,
        # et il se change en une ligne en tete de fichier.
        vise = cle if cle in SITES else (SITE_DEFAUT if SITE_DEFAUT in SITES else None)
        note = relance_auto(vise) if (vise and acquerir_si_absent) else None
        if ecarte:
            suite = ("acquisition relancee automatiquement" if note
                     else "relancer le collecteur")
            return _ordonner(manque), ["%s - %s" % (ecarte, suite)]
        if note:
            return _ordonner(manque), [
                "aucun releve pour %s pour le moment - %s. Les valeurs "
                "arriveront dans le fil des que le collecteur aura ecrit."
                % (vise or "ce site", note)]
        if not acquerir_si_absent:
            # Lecture seule : l'appelant va acquerir lui-meme. On ne parle pas
            # d'un echec qui n'a pas eu lieu.
            return _ordonner(manque), [
                "aucun releve pour %s pour le moment" % (vise or "ce site")]
        # Ici, et ici seulement, il n'y a vraiment plus rien a attendre :
        # relance_auto a rendu None, donc ni acquisition en cours, ni relance
        # recente, ni coordonnees exploitables.
        return _ordonner(manque), [
            f"releve absent : {chemin}. L'acquisition automatique n'a pas pu "
            f"demarrer (reseau coupe, ou collecteur introuvable). "
            f"A defaut : python meteo_3x30_collecte.py --site {vise or SITE_DEFAUT}"]

    avertis = []
    t = _nombre(data.get("temperature_c"))
    v = _nombre(data.get("vent_kmh"))
    h = _nombre(data.get("humidite_pct"))
    r = _nombre(data.get("rafales_kmh"))

    r3 = regle_3x30(t, v, h)
    etat, detail = formuler_3x30(r3, t, v, h)
    out = {"REGLE_3X30": etat, "CRITERES_3X30": detail}
    if t is not None:
        out["TEMPERATURE_C"] = f"{t:.1f}"
    # Une decimale pour le vent et les rafales, comme pour la temperature :
    # AROME les donne avec une decimale, et arrondir a l'entier laissait le
    # modele "completer" de lui-meme (VENT_KMH = 20 restitue en "20,1 km/h").
    # Une valeur publiee doit etre exactement celle de la source.
    if v is not None:
        out["VENT_KMH"] = f"{v:.1f}"
    if r is not None:
        out["RAFALES_KMH"] = f"{r:.1f}"
    if h is not None:
        out["HUMIDITE_PCT"] = f"{h:.0f}"

    lieu = str(data.get("lieu") or "").strip()
    lat, lon = data.get("lat"), data.get("lon")
    if lieu or lat is not None:
        coord = f" ({lat}, {lon})" if lat is not None and lon is not None else ""
        out["LIEU_METEO"] = (lieu or "point") + coord

    if age_min is not None:
        out["RELEVE_AGE_MIN"] = f"{age_min:.0f}"
        if age_min > AGE_MAX_MIN:
            # On ne se contente plus de le signaler : on relance.
            note = relance_auto(cle, data)
            avertis.append(f"releve meteo vieux de {age_min:.0f} min - "
                           + (note or "relancer le collecteur"))
    if str(data.get("source", "")).lower().startswith("simul"):
        avertis.append("releve SIMULE (jeu de test, pas une mesure AROME)")
    # Le modele doit savoir quels lieux il peut demander : sans cette liste,
    # il inventerait des noms ou des coordonnees.
    out["SITES_METEO"] = ", ".join(sorted(SITES))
    # Les autres sites deja releves, en une ligne : de quoi comparer.
    autres = resumes_autres_sites(cle, limite=3)
    if autres:
        out["METEO_AUTRES_SITES"] = " ; ".join(autres)
    # Etat de l'acquisition : le modele doit savoir si une mesure est en route,
    # et l'operateur doit voir un echec reseau au lieu d'un silence.
    with _ACQ_VERROU:
        en_cours, erreur = _ACQ["en_cours"], _ACQ["erreur"]
    if en_cours:
        out["ACQUISITION"] = "en cours"
    if erreur:
        avertis.append(erreur)
    return _ordonner(out), avertis


# ---------------------------------------------------------------------------
#  Contrat d-IA
# ---------------------------------------------------------------------------
def collect(ctx):
    # On detaille le dernier site mesure : c'est celui dont on parle.
    # Seul collect() acquiert d'office : personne ne viendra chercher la
    # donnee derriere lui. Les actions acquierent elles-memes (v2.4).
    out, avertis = _variables_depuis_releve(_DERNIER_SITE, acquerir_si_absent=True)
    return out, _avertis_sites() + list(avertis)


def execute_action(action_id, params, ctx):
    """Actions demandees par un LLM (directives ACTION: / MESURE:)."""
    global _DERNIER_SITE
    if action_id == "mesure_meteo":
        variables, avertis = _variables_depuis_releve(_DERNIER_SITE)
        demande = (params.get("lieu") or params.get("site") or "").strip()
        if not demande and not params.get("lat"):
            # Pas de lieu precise : on rend ce que l'on a, LIEU_METEO dit ou.
            if not variables:
                return {"MESURE_RESULTAT": "aucun releve disponible"}, avertis
            return variables, avertis

        lat, lon, libelle, avertis_site = resoudre_site(params)
        # Un lieu est nomme : la pre-lecture portait sur le site precedent, et
        # ce qu'elle disait de son absence ne concerne pas cette demande.
        avertis = _sans_note_absence(avertis) + avertis_site
        if libelle is None:
            # Lieu demande mais inconnu : on ne publie AUCUNE valeur, et on
            # dit au modele quoi demander. Une mesure absente se voit ; une
            # mesure attribuee au mauvais lieu ne se voit pas.
            return _ordonner({
                "SITES_METEO": ", ".join(sorted(SITES)),
                "LIEU_DEMANDE": demande,
                "MESURE_RESULTAT": (
                    "site %s inconnu - aucune mesure faite. Redemande avec "
                    "l'un des sites connus : %s"
                    % (demande, ", ".join(sorted(SITES)))),
            }), avertis
        cle = cle_du_libelle(libelle)
        cible = fichier_releves(cle)
        _DERNIER_SITE = cle
        variables, av0 = _variables_depuis_releve(cle)
        avertis = avertis + av0
        data, age_min = _lire_releve(cible)
        if data is None:
            data, age_min = _lire_releve(FICHIER_RELEVES)
        concorde = data is not None and meme_site(libelle, demande, data)
        frais = age_min is not None and age_min <= AGE_FRAIS_MIN

        if concorde and frais:
            # On le DIT : sans cette phrase, le modele enchaine par un
            # ATTENDRE: RELEVE_AGE_MIN < 2 que rien ne viendra satisfaire.
            variables["LIEU_DEMANDE"] = libelle
            variables["MESURE_RESULTAT"] = (
                f"valeurs de {libelle} deja a jour ({age_min:.0f} min) - "
                f"repondre maintenant, ne pas attendre")
            return _ordonner(variables), avertis

        # On MESURE maintenant, et on attend le resultat le temps que le
        # budget de l'action le permet. C'est la difference avec un collect() :
        # ici, aller sur le reseau est legitime.
        etat, message, avertis_acq = acquerir(lat, lon, libelle, cible=cible)
        # A partir d'ici l'absence est soit comblee ("faite"), soit remplacee
        # par un message plus precis ("echouee", "en cours"). Dans les trois
        # cas, la note de la pre-lecture a cesse d'etre vraie. (v2.8)
        avertis = _sans_note_absence(avertis) + avertis_acq

        if etat == "faite":
            # Le fichier vient d'etre reecrit : on le relit pour publier les
            # valeurs fraiches dans CETTE reponse. Aucune attente necessaire.
            variables, avertis_relecture = _variables_depuis_releve(cle)
            variables["LIEU_DEMANDE"] = libelle
            variables["MESURE_RESULTAT"] = f"{message} - repondre maintenant"
            return _ordonner(variables), avertis + avertis_relecture

        if etat == "echouee":
            # Un echec doit se voir tout de suite, et non au bout d'un delai
            # d'attente expire. On ne publie que ce que l'on peut justifier.
            if concorde:
                variables["LIEU_DEMANDE"] = libelle
                variables["ACQUISITION"] = "echouee"
                variables["MESURE_RESULTAT"] = _court(
                    f"acquisition impossible ({message}) - valeurs de "
                    f"{libelle} datant de {age_min:.0f} min", 160)
                return _ordonner(variables), avertis
            return ({"MESURE_RESULTAT": _court(
                        f"acquisition impossible : {message} - aucune valeur "
                        f"disponible pour {libelle}", 160),
                     "LIEU_DEMANDE": libelle,
                     "ACQUISITION": "echouee"}, avertis)

        # etat == "en_cours" : le reseau traine, on repasse au mode differe.
        if concorde:
            variables["LIEU_DEMANDE"] = libelle
            variables["ACQUISITION"] = "en cours"
            variables["MESURE_RESULTAT"] = (
                f"valeurs de {libelle} datant de {age_min:.0f} min - "
                f"acquisition en cours, attendre RELEVE_AGE_MIN < 2")
            return _ordonner(variables), avertis

        # Site different : on ne publie SURTOUT pas les valeurs de l'autre
        # site, sinon le modele les attribuerait au lieu demande.
        if data is not None:
            avertis.append(
                f"le releve disponible concerne {data.get('lieu')} et non "
                f"{libelle} : ses valeurs ne valent pas pour {libelle}")
        return ({"MESURE_RESULTAT": f"{message} - ATTENDRE: RELEVE_AGE_MIN < 2 "
                                    f"delai=300",
                 "LIEU_DEMANDE": libelle,
                 "ACQUISITION": "en cours"}, avertis)

    if action_id == "releve_meteo_maintenant":
        if not COLLECTEUR.exists():
            return ({"MESURE_RESULTAT": "collecteur absent"},
                    ["meteo_3x30_collecte.py introuvable"])
        # On impose au collecteur le fichier que CE plugin va relire : peu
        # importe la copie du collecteur lancee, elle ecrira au bon endroit.
        lat, lon, libelle, avertis_site = resoudre_site(params)
        cle = cle_du_libelle(libelle)
        _DERNIER_SITE = cle
        etat, message, avertis = acquerir(lat, lon, libelle,
                                          cible=fichier_releves(cle))
        avertis = avertis + avertis_site
        if etat == "faite":
            variables, avertis_relecture = _variables_depuis_releve(cle)
            variables["LIEU_DEMANDE"] = libelle
            variables["MESURE_RESULTAT"] = f"{message} - repondre maintenant"
            return _ordonner(variables), avertis + avertis_relecture
        if etat == "echouee":
            return ({"MESURE_RESULTAT": _court(
                        f"acquisition impossible : {message}", 160),
                     "LIEU_DEMANDE": libelle,
                     "ACQUISITION": "echouee"}, avertis)
        return ({"MESURE_RESULTAT": f"{message} - attendre RELEVE_AGE_MIN < 2",
                 "LIEU_DEMANDE": libelle,
                 "ACQUISITION": "en cours"}, avertis)

    return {"MESURE_RESULTAT": f"action inconnue : {action_id}"}


if __name__ == "__main__":
    ctx = {"tour": 1, "speaker": "LLM1", "vars": {}}
    print("fichier de releve   :", FICHIER_RELEVES)
    print("  pour melun        :", fichier_releves("melun"))
    print("  pour provins      :", fichier_releves("provins"))
    print("sites connus        :", ", ".join(sorted(SITES)))
    print("collecteur importe  :", _charger_collecteur() is not None)
    print("interpreteur Python :", _interpreteur_python())
    for essai in ({"lieu": "Melun"}, {"lieu": "MELUN"}, {"lieu": "Nemours"},
                  {"lieu": "Toulouse"}, {"lat": "44.90", "lon": "0.48",
                                         "lieu": "Bergerac"}, {}):
        print("  resoudre_site", essai, "->", resoudre_site(essai))
    print("meteo_lib importee :", _meteo_lib is not None)
    print("collect            :", collect(ctx))
    print("mesure_meteo       :", execute_action("mesure_meteo", {}, ctx))
    print("mesure_meteo melun :",
          execute_action("mesure_meteo", {"lieu": "melun"}, ctx))
    for a, b in (("Melun (prefecture 77)", "melun"),
                 ("Nangeville", "melun"),
                 ("Nangeville", "nangeville")):
        print(f"  meme_site({b!r}, releve={a!r}) ->",
              meme_site(SITES[_cle_site(b)][2] if _cle_site(b) in SITES else b,
                        b, {"lieu": a}))
    for essai in ((35.0, 40.0, 22.0), (30.0, 30.0, 30.0), (28.0, 40.0, 22.0),
                  (35.0, None, 22.0)):
        r3 = regle_3x30(*essai)
        print(f"3x30 {str(essai):24s} -> count={r3['count']} ok={r3['ok']}")
