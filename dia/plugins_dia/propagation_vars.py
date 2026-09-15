# -*- coding: utf-8 -*-
"""
============================================================================
  propagation_vars.py - Plugin d'ENTREE pour d-IA v1.10+
============================================================================
  Auteur  : Jean-Louis (F1GBD) - ADRASEC 77 / FNRASEC
  Version : 1.0

Objet
-----
Injecte dans la simulation des VARIABLES DE SITUATION issues de releves
REELS (ou d'un fichier tenu a jour par le formateur) : indice geomagnetique,
etat de la fenetre NVIS, flux solaire, autonomie energetique du PCO.

Interet pedagogique : l'injecteur d'evenements et le COD cessent d'inventer
la propagation. Si le Kp du jour monte, la liaison HF NVIS se degrade DANS
l'exercice, et l'operateur doit basculer sur un moyen de secours. On
s'entraine sur la situation reelle, pas sur une fiction.

Source des donnees
------------------
Un fichier JSON, par defaut "propagation_releves.json" depose a cote de ce
plugin. GEOMAG-Observer (ou tout autre outil) peut le reecrire en continu :
le plugin le relit a chaque tour.

    {
      "kp": 4.3,
      "sfi": 142,
      "soc_pct": 61,
      "autonomie_h": 7.5,
      "commentaire": "orage magnetique en cours"
    }

Toutes les cles sont facultatives. Si le fichier est absent, un gabarit est
cree au premier appel et AUCUNE variable n'est injectee : le bloc
{variables} reste vide et le dialogue se deroule exactement comme en v1.9.
On n'invente jamais une valeur : pas de releve, pas de variable.

Variables produites
-------------------
  KP_LOCAL        indice Kp releve (0 a 9)
  NVIS_ETAT       ouverte / degradee / fermee, deduit du Kp
  SFI             flux solaire 10,7 cm
  AUTONOMIE_PCO   autonomie energetique restante du poste, en heures
  SOC_PCO         etat de charge de la power station, en %
  RELEVE_NOTE     commentaire libre du formateur
============================================================================
"""

import json
from pathlib import Path

PLUGIN_NAME = "Propagation / energie (releves)"
PLUGIN_VERSION = "1.0"

# Fichier de releves. Pointez-le vers la sortie de GEOMAG-Observer si vous
# voulez un couplage direct avec l'observatoire.
FICHIER_RELEVES = Path(__file__).with_name("propagation_releves.json")

GABARIT = {
    "_aide": ("Releves injectes dans d-IA. Mettez a jour ce fichier (ou faites-le "
              "ecrire par GEOMAG-Observer) : d-IA le relit a chaque tour."),
    "kp": None,
    "sfi": None,
    "soc_pct": None,
    "autonomie_h": None,
    "commentaire": "",
}


def list_variables():
    return [
        ("KP_LOCAL", "Indice geomagnetique Kp releve (0-9)"),
        ("NVIS_ETAT", "Etat de la fenetre NVIS deduit du Kp"),
        ("SFI", "Flux solaire 10,7 cm"),
        ("AUTONOMIE_PCO", "Autonomie energetique restante du poste (heures)"),
        ("SOC_PCO", "Etat de charge de la power station (%)"),
        ("RELEVE_NOTE", "Commentaire libre du formateur"),
    ]


def _ecrire_gabarit():
    """Cree le fichier de releves vide, pour que le formateur le trouve."""
    try:
        if not FICHIER_RELEVES.exists():
            FICHIER_RELEVES.write_text(
                json.dumps(GABARIT, ensure_ascii=False, indent=2),
                encoding="utf-8")
    except Exception:
        pass


def _etat_nvis(kp):
    """Traduit un Kp en etat de fenetre NVIS, en clair pour les modeles."""
    if kp is None:
        return None
    if kp <= 3:
        return "ouverte (propagation NVIS normale)"
    if kp <= 5:
        return "degradee (absorption, liaisons HF aleatoires)"
    return "fermee (NVIS inutilisable, basculer sur un moyen de secours)"


def collect(ctx):
    """Lit les releves et retourne les variables du tour. Jamais bloquant."""
    if not FICHIER_RELEVES.exists():
        _ecrire_gabarit()
        return {}
    try:
        data = json.loads(FICHIER_RELEVES.read_text(encoding="utf-8"))
    except Exception:
        # Fichier en cours d'ecriture ou malforme : on ne casse pas le tour.
        return {}
    if not isinstance(data, dict):
        return {}

    out = {}
    kp = data.get("kp")
    try:
        kp = float(kp) if kp is not None else None
    except (TypeError, ValueError):
        kp = None
    if kp is not None:
        out["KP_LOCAL"] = f"{kp:g}"
        etat = _etat_nvis(kp)
        if etat:
            out["NVIS_ETAT"] = etat
    if data.get("sfi") not in (None, ""):
        out["SFI"] = data["sfi"]
    if data.get("autonomie_h") not in (None, ""):
        out["AUTONOMIE_PCO"] = f"{data['autonomie_h']} h"
    if data.get("soc_pct") not in (None, ""):
        out["SOC_PCO"] = f"{data['soc_pct']} %"
    note = (data.get("commentaire") or "").strip()
    if note:
        out["RELEVE_NOTE"] = note
    return out
