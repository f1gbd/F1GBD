#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================================
  meteo_3x30_collecte.py - Collecteur meteo pour le plugin d-IA meteo_3x30
============================================================================
  Auteur  : Jean-Louis (F1GBD) - ADRASEC 77 / FNRASEC
  Version : 1.2

Objet
-----
Interroge Open-Meteo en modele AROME France HD (Meteo-France, ~1,5 km) pour un
point donne et ecrit le releve dans "meteo_releves.json", a cote du plugin
d-IA "meteo_3x30.py" qui le lit.

Pourquoi un programme separe ? Parce qu'un plugin d-IA dispose de 2 secondes
par appel et doit fonctionner hors ligne : il ne va donc JAMAIS sur le reseau.
La separation est la meme que celle qui existe deja dans TCQ entre la couche
meteo (meteo_lib.py) et l'affichage.

    meteo_3x30_collecte.py  --->  meteo_releves.json  --->  meteo_3x30.py
      (ici : le reseau)                 (local)             (plugin d-IA)

Il reutilise meteo_lib.py (la bibliotheque meteo de TCQ) quand elle est
accessible ; sinon il embarque la meme requete, en bibliotheque standard
uniquement.

Usage
-----
    python meteo_3x30_collecte.py                        # point par defaut
    python meteo_3x30_collecte.py --lat 44.90 --lon 0.48 --lieu "Bergerac"
    python meteo_3x30_collecte.py --simuler 35,40,22     # T,vent,humidite
    python meteo_3x30_collecte.py --boucle 900           # releve toutes les 15 min
    python meteo_3x30_collecte.py --site melun          # site connu du plugin
    python meteo_3x30_collecte.py --site melun --boucle 900
    python meteo_3x30_collecte.py --sortie "C:\\ADRASEC\\meteo\\meteo_releves.json"

L'option --site reprend la table SITES de meteo_3x30.py (le plugin, a cote) :
elle fixe les coordonnees ET ecrit dans meteo_releves_<site>.json, le fichier
que le plugin lira pour ce site. C'est ce qu'il faut pour suivre plusieurs
communes en parallele sans qu'un releve ecrase l'autre.

Plusieurs installations de d-IA ? Chacune lit le releve dans SON dossier
plugins_dia\. Pour qu'elles partagent le meme, designez un emplacement commun
avec --sortie, avec la variable d'environnement DIA_METEO_RELEVES, ou avec la
constante CHEMIN_RELEVES_PARTAGE (renseignez alors la MEME valeur dans
meteo_3x30.py).

Mise en place recommandee : une tache planifiee Windows toutes les 15 minutes,
ou l'option --boucle dans une fenetre laissee ouverte pendant l'exercice.

En cas d'echec (reseau coupe, quota Open-Meteo epuise - HTTP 429), le fichier
PRECEDENT est conserve tel quel : on prefere un releve date et signale comme
ancien (le plugin affiche RELEVE_AGE_MIN) a une valeur fausse ou absente.
============================================================================
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

# --- Emplacement du releve -------------------------------------------------
# MEME resolution que le plugin meteo_3x30.py, pour qu'ils ne puissent pas
# diverger. Ordre de priorite :
#   1. l'option --sortie de la ligne de commande (ce que fait le plugin quand
#      c'est un LLM qui declenche l'acquisition) ;
#   2. la variable d'environnement DIA_METEO_RELEVES ;
#   3. la constante CHEMIN_RELEVES_PARTAGE ci-dessous ;
#   4. a defaut, meteo_releves.json a cote de ce script.
CHEMIN_RELEVES_PARTAGE = ""

VAR_ENV_RELEVES = "DIA_METEO_RELEVES"

# Point par defaut : Seine-et-Marne (meme point que test_meteo.py dans TCQ).
LAT_DEFAUT = 48.40
LON_DEFAUT = 2.70
LIEU_DEFAUT = "Seine-et-Marne"

OPENMETEO_URL = "https://api.open-meteo.com/v1/forecast"
MODELE = "meteofrance_arome_france_hd"      # AROME France HD ~1,5 km
CURRENT_VARS = [
    "temperature_2m", "relative_humidity_2m", "wind_speed_10m",
    "wind_direction_10m", "wind_gusts_10m", "pressure_msl", "precipitation",
]

# --- Reutilisation de meteo_lib.py (TCQ) ----------------------------------
_CHEMINS_METEO_LIB = (
    Path(__file__).resolve().parent,
    Path(__file__).resolve().parent.parent,
    Path(r"H:\QITdevsrc\TCQ"),
)
meteo_lib = None
for _p in _CHEMINS_METEO_LIB:
    try:
        if (_p / "meteo_lib.py").is_file():
            if str(_p) not in sys.path:
                sys.path.insert(0, str(_p))
            import meteo_lib   # noqa: E402
            break
    except Exception:
        meteo_lib = None


def site_connu(nom):
    """Cherche un site dans la table SITES du plugin, a cote de ce script.

    Retourne (cle, (lat, lon, libelle)) ou (None, None). On importe le plugin
    au lieu de recopier la table : une seule liste de sites a tenir a jour.
    L'import n'a lieu qu'ici, donc jamais quand c'est le plugin qui nous
    importe.
    """
    try:
        import importlib.util
        chemin = Path(__file__).with_name("meteo_3x30.py")
        if not chemin.is_file():
            return None, None
        spec = importlib.util.spec_from_file_location("meteo_3x30_sites", chemin)
        if spec is None or spec.loader is None:
            return None, None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        cle = module._cle_site(nom)
        if cle in module.SITES:
            return cle, module.SITES[cle]
        print(f"site inconnu : {nom} - sites connus : "
              + ", ".join(sorted(module.SITES)))
    except Exception as e:
        print(f"table des sites illisible ({e}) - utilisez --lat/--lon")
    return None, None


# ---------------------------------------------------------------------------
#  Acquisition
# ---------------------------------------------------------------------------
def _fetch_embarque(lat, lon, timeout=15):
    """Requete Open-Meteo en bibliotheque standard (repli sans meteo_lib).

    Reproduit exactement l'appel de meteo_lib.fetch_point().
    """
    import urllib.request
    import urllib.parse
    import urllib.error

    params = {
        "latitude": f"{lat:.4f}", "longitude": f"{lon:.4f}",
        "current": ",".join(CURRENT_VARS),
        "wind_speed_unit": "kmh",
        "timezone": "auto",
        "models": MODELE,
    }
    url = OPENMETEO_URL + "?" + urllib.parse.urlencode(params, safe=",")
    req = urllib.request.Request(
        url, headers={"User-Agent": "d-IA-ADRASEC/1.11"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        raison = ""
        try:
            corps = json.loads(e.read().decode("utf-8", "replace"))
            raison = corps.get("reason", "") if isinstance(corps, dict) else ""
        except Exception:
            pass
        raise RuntimeError(f"HTTP {e.code} - {raison or e.reason}")
    if isinstance(data, dict) and data.get("error"):
        raise RuntimeError(data.get("reason", "erreur Open-Meteo"))
    c = (data.get("current") or {}) if isinstance(data, dict) else {}
    return {
        "lat": data.get("latitude"), "lon": data.get("longitude"),
        "time": c.get("time"),
        "temp_c": c.get("temperature_2m"),
        "rh_pct": c.get("relative_humidity_2m"),
        "wind_kmh": c.get("wind_speed_10m"),
        "wind_dir": c.get("wind_direction_10m"),
        "gust_kmh": c.get("wind_gusts_10m"),
        "pressure": c.get("pressure_msl"),
        "precip": c.get("precipitation"),
    }


def relever(lat, lon):
    """Retourne le dict meteo normalise (via meteo_lib si disponible)."""
    if meteo_lib is not None and hasattr(meteo_lib, "fetch_point"):
        point = meteo_lib.fetch_point(lat, lon)
        if not point:
            raise RuntimeError("reponse vide d'Open-Meteo")
        return point
    return _fetch_embarque(lat, lon)


def resoudre_sortie(arg_sortie=None):
    """Chemin du releve a ecrire, selon l'ordre de priorite documente."""
    for candidat in (arg_sortie, os.environ.get(VAR_ENV_RELEVES, ""),
                     CHEMIN_RELEVES_PARTAGE):
        candidat = (candidat or "").strip().strip('"')
        if candidat:
            return Path(candidat).expanduser()
    return Path(__file__).with_name("meteo_releves.json")


def ecrire_releve(point, lieu, source, sortie=None):
    """Ecrit le releve JSON (ecriture atomique via fichier temporaire)."""
    releve = {
        "_type": "meteo_releves",
        "iso": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "lieu": lieu,
        "lat": point.get("lat"),
        "lon": point.get("lon"),
        "temperature_c": point.get("temp_c"),
        "humidite_pct": point.get("rh_pct"),
        "vent_kmh": point.get("wind_kmh"),
        "rafales_kmh": point.get("gust_kmh"),
        "direction_deg": point.get("wind_dir"),
        "pression_hpa": point.get("pressure"),
        "precip_mm": point.get("precip"),
        "heure_modele": point.get("time"),
        "source": source,
    }
    sortie = Path(sortie) if sortie else resoudre_sortie()
    try:
        sortie.parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    tmp = sortie.with_suffix(".tmp")
    tmp.write_text(json.dumps(releve, ensure_ascii=False, indent=2),
                   encoding="utf-8")
    tmp.replace(sortie)          # remplacement atomique : jamais de fichier
    return releve                # a moitie ecrit pour le plugin qui le lit


def _resume(releve):
    def v(x, unite="", nd=0):
        return f"{x:.{nd}f}{unite}" if isinstance(x, (int, float)) else "-"
    return (f"{releve.get('lieu')} : "
            f"T {v(releve.get('temperature_c'), ' C', 1)}, "
            f"vent {v(releve.get('vent_kmh'), ' km/h')} "
            f"(rafales {v(releve.get('rafales_kmh'), ' km/h')}), "
            f"HR {v(releve.get('humidite_pct'), ' %')}")


# ---------------------------------------------------------------------------
#  Programme principal
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(
        description="Collecteur meteo AROME France HD pour le plugin d-IA "
                    "meteo_3x30.")
    ap.add_argument("--lat", type=float, default=LAT_DEFAUT)
    ap.add_argument("--lon", type=float, default=LON_DEFAUT)
    ap.add_argument("--lieu", default=LIEU_DEFAUT)
    ap.add_argument("--simuler", metavar="T,VENT,HUM",
                    help="ecrit un releve de TEST sans reseau, "
                         "ex. --simuler 35,40,22")
    ap.add_argument("--boucle", type=int, metavar="SECONDES",
                    help="repete le releve toutes les N secondes "
                         "(900 = 15 min ; Ctrl+C pour arreter)")
    ap.add_argument("--sortie", metavar="CHEMIN",
                    help="fichier de releve a ecrire (defaut : meteo_releves.json "
                         "a cote de ce script ; voir DIA_METEO_RELEVES)")
    ap.add_argument("--site", metavar="CLE",
                    help="site connu du plugin (ex. melun) : fixe lat/lon ET "
                         "ecrit meteo_releves_<site>.json")
    args = ap.parse_args()
    sortie = resoudre_sortie(args.sortie)
    lat, lon, lieu = args.lat, args.lon, args.lieu
    if args.site:
        cle, coord = site_connu(args.site)
        if coord is None:
            return 2
        lat, lon, lieu = coord
        if not args.sortie:
            # Un fichier par site : c'est ce que le plugin ira relire.
            sortie = sortie.with_name(f"{sortie.stem}_{cle}{sortie.suffix}")

    if args.simuler:
        try:
            t, v, h = [float(x) for x in args.simuler.split(",")]
        except ValueError:
            print("--simuler attend trois nombres : T,VENT,HUM")
            return 2
        point = {"lat": lat, "lon": lon, "temp_c": t, "rh_pct": h,
                 "wind_kmh": v, "gust_kmh": v * 1.4, "wind_dir": 240,
                 "pressure": 1013, "precip": 0.0,
                 "time": time.strftime("%Y-%m-%dT%H:%M")}
        releve = ecrire_releve(point, lieu, "simulation (jeu de test)",
                               sortie)
        print("Releve SIMULE ecrit :", sortie)
        print("  ", _resume(releve))
        return 0

    periode = max(60, int(args.boucle)) if args.boucle else None
    while True:
        try:
            point = relever(lat, lon)
            releve = ecrire_releve(
                point, lieu,
                "Open-Meteo / AROME France HD (Meteo-France)", sortie)
            print(time.strftime("%H:%M:%S"), "releve ecrit :", _resume(releve),
                  "->", sortie)
        except RuntimeError as e:
            msg = str(e)
            print(time.strftime("%H:%M:%S"), "ECHEC Open-Meteo :", msg)
            if "429" in msg or "limit" in msg.lower():
                print("  -> quota journalier epuise (remise a zero a 00:00 UTC). "
                      "Espacez les releves.")
            print("  -> le releve precedent est conserve "
                  "(le plugin signalera son anciennete).")
        except Exception as e:
            print(time.strftime("%H:%M:%S"), "ECHEC reseau :", e)
            print("  -> le releve precedent est conserve.")
        if periode is None:
            return 0
        try:
            time.sleep(periode)
        except KeyboardInterrupt:
            print("\nArret demande.")
            return 0


if __name__ == "__main__":
    sys.exit(main())
