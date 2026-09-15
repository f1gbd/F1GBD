# -*- coding: utf-8 -*-
"""
============================================================================
  sitrep_scoring.py - Plugin de SORTIE pour d-IA v1.10+
============================================================================
  Auteur  : Jean-Louis (F1GBD) - ADRASEC 77 / FNRASEC
  Version : 1.0

Objet
-----
Evalue automatiquement chaque message de l'operateur (LLM2, ou le stagiaire
en mode CHAT) selon la grille de forme du tutoriel de formation, et ecrit une
ligne de RETEX dans un CSV. La notation devient un sous-produit de la seance
au lieu d'un travail de relecture.

Criteres controles (forme uniquement - le fond reste l'affaire du formateur)
  - indicatif present                            2 pts
  - horodate presente                            3 pts
  - accuse de reception ou demande d'accuse      3 pts
  - demande chiffree (litres, personnes, delai)  4 pts
  - brievete (<= 6 lignes, <= 800 caracteres)    4 pts
  - mention EXERCICE                             4 pts
                                                ------
                                                20 pts

Sortie
------
  1. Un CSV par jour dans ..\\logs\\retex_sitrep_AAAAMMJJ.csv
  2. Une variable DEFAUT_RELEVE reinjectee dans la simulation : le COD la
     voit et peut reclamer par radio l'element manquant. C'est la boucle
     sortie -> entree, et c'est beaucoup plus formateur qu'une remarque du
     formateur en fin de seance.

Reglages (a ajuster en tete de fichier)
---------------------------------------
  INJECTER_DEFAUT  True  : le defaut constate est injecte dans le prompt
  INJECTER_SCORE   False : le score chiffre n'est PAS injecte (il casserait
                           l'immersion ; il reste dans le CSV)
============================================================================
"""

import csv
import datetime
import re
from pathlib import Path

PLUGIN_NAME = "Notation SITREP (RETEX)"
PLUGIN_VERSION = "1.0"

INJECTER_DEFAUT = True
INJECTER_SCORE = False

# Le CSV va dans le dossier logs/ de d-IA s'il existe, sinon a cote du plugin.
_LOGS = Path(__file__).resolve().parent.parent / "logs"
DOSSIER_SORTIE = _LOGS if _LOGS.is_dir() else Path(__file__).resolve().parent

RE_INDICATIF = re.compile(r"\b[A-Z]{1,2}\d[A-Z]{1,4}\b")
RE_HORODATE = re.compile(r"\b\d{1,2}\s?[hH:]\s?\d{2}\b|\b\d{6}Z\b")
RE_ACCUSE = re.compile(r"accus|recu|reçu|\bAR\b|bien re", re.IGNORECASE)
RE_CHIFFRE = re.compile(
    r"\b\d+\s*(l\b|litres?|m3|palettes?|pers\b|personnes?|residents?|"
    r"heures?|\bh\b|min\b|kw|kva|%)", re.IGNORECASE)
RE_EXERCICE = re.compile(r"exercice", re.IGNORECASE)

_ETAT = {"nb": 0, "total": 0}


def list_variables():
    return [
        ("DEFAUT_RELEVE", "Element manquant dans le dernier message de l'operateur"),
        ("SITREP_TRANSMIS", "Nombre de messages de l'operateur evalues"),
        ("SCORE_SITREP", "Note de forme du dernier message (sur 20, si injecte)"),
    ]


def _noter(texte):
    """Retourne (score, defauts) pour un message d'operateur."""
    lignes = [l for l in (texte or "").splitlines() if l.strip()]
    score = 0
    defauts = []
    if RE_INDICATIF.search(texte or ""):
        score += 2
    else:
        defauts.append("indicatif non annonce")
    if RE_HORODATE.search(texte or ""):
        score += 3
    else:
        defauts.append("message non horodate")
    if RE_ACCUSE.search(texte or ""):
        score += 3
    else:
        defauts.append("pas d'accuse de reception")
    if RE_CHIFFRE.search(texte or ""):
        score += 4
    else:
        defauts.append("demande non chiffree")
    if len(lignes) <= 6 and len(texte or "") <= 800:
        score += 4
    else:
        defauts.append("message trop long")
    if RE_EXERCICE.search(texte or ""):
        score += 4
    else:
        defauts.append("mention EXERCICE absente")
    return score, defauts


def _ecrire_csv(ligne):
    """Ajoute une ligne au CSV du jour (cree l'entete au besoin)."""
    jour = datetime.datetime.now().strftime("%Y%m%d")
    chemin = DOSSIER_SORTIE / f"retex_sitrep_{jour}.csv"
    neuf = not chemin.exists()
    with open(chemin, "a", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        if neuf:
            w.writerow(["horodate", "tour", "sequence", "auteur", "humain",
                        "score_sur_20", "defauts", "message"])
        w.writerow(ligne)
    return chemin


def on_message(msg, ctx):
    """Note les messages de l'operateur (LLM2). Ignore le COD et l'animation."""
    if msg.get("speaker") != "LLM2":
        return None
    texte = (msg.get("texte") or "").strip()
    if len(texte) < 15:
        return None

    score, defauts = _noter(texte)
    _ETAT["nb"] += 1
    _ETAT["total"] += score

    try:
        _ecrire_csv([
            msg.get("ts", ""),
            msg.get("tour", ""),
            (msg.get("theme", "") or "")[:60],
            msg.get("role", "") or msg.get("speaker", ""),
            "oui" if msg.get("humain") else "non",
            score,
            " / ".join(defauts) if defauts else "RAS",
            texte.replace("\n", " ")[:500],
        ])
    except Exception:
        # Disque plein, fichier ouvert dans Excel... on ne casse pas la seance.
        pass

    out = {"SITREP_TRANSMIS": _ETAT["nb"]}
    if INJECTER_DEFAUT:
        out["DEFAUT_RELEVE"] = (defauts[0] if defauts
                                else "message conforme (forme complete)")
    if INJECTER_SCORE:
        out["SCORE_SITREP"] = f"{score}/20"
    return out
