# -*- coding: utf-8 -*-
"""
============================================================================
  exemple_minimal.py - Squelette de plugin d-IA v1.10+
============================================================================
  Auteur  : ADRASEC 77 - F1GBD
  Version : 1.0

Le plus petit plugin utile : une variable d'ENTREE (l'heure d'exercice) et un
hook de SORTIE (compteur de messages). Copiez ce fichier, renommez-le, et
remplacez le contenu des deux fonctions.

Pour desactiver un plugin sans le supprimer : renommez-le en
"exemple_minimal.py.disabled" (meme convention que les plugins IAbrain).
============================================================================
"""

import datetime

PLUGIN_NAME = "Exemple minimal"
PLUGIN_VERSION = "1.0"

_COMPTEUR = {"messages": 0}


def list_variables():
    """Documentaire : alimente la fenetre Diagnostic plugins."""
    return [
        ("HEURE_EXERCICE", "Heure locale, pour horodater le trafic"),
        ("MESSAGES_ECHANGES", "Nombre de prises de parole depuis le debut"),
    ]


def collect(ctx):
    """ENTREE : appele avant chaque prise de parole.

    ctx contient tour, theme, speaker, role, sujet, mode_jdr, labels,
    vars / session_vars (snapshot des variables) et historique_court.
    Retournez un dict {NOM: valeur}, ou {} pour n'injecter rien du tout.
    """
    return {"HEURE_EXERCICE": datetime.datetime.now().strftime("%Hh%M")}


def on_message(msg, ctx):
    """SORTIE : appele apres chaque prise de parole.

    msg contient tour, speaker, role, texte, theme, ts, humain.
    Retour possible : un dict (fusionne dans les variables du tour suivant),
    ou le couple (dict, ["avertissement", ...]) comme chez IAbrain, ou None.
    """
    _COMPTEUR["messages"] += 1
    return {"MESSAGES_ECHANGES": _COMPTEUR["messages"]}
