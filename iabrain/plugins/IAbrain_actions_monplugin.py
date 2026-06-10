# -*- coding: utf-8 -*-
"""IAbrain_actions_monplugin.py — Mon premier plugin IAbrain."""
 
from typing import Any, List, Sequence, Tuple
 
# Identifiants des actions exposées
_ACTIONS = {"hello_world", "compteur_mots"}
 
 
def is_action(action_id: str) -> bool:
    return (action_id or "").strip() in _ACTIONS
 
 
def list_actions() -> List[Tuple[str, str, str]]:
    return [
        ("hello_world", "Mon plugin — Bonjour",
         "Affiche un message de bienvenue personnalisé "
         "avec l'indicatif de l'opérateur."),
        ("compteur_mots", "Mon plugin — Compter les mots",
         "Compte les mots de la variable {TEXTE} et affiche "
         "le résultat avec quelques statistiques."),
    ]
 
 
def execute_action(action_id: str,
                   imported_files: Sequence[Tuple[str, str]] = (),
                   options: Any = None) -> Tuple[str, List[str]]:
    aid = (action_id or "").strip()
    sv = (options or {}).get("session_vars", {}) if options else {}
 
    if aid == "hello_world":
        indicatif = sv.get("INDICATIF") or "opérateur"
        md = f"## 👋 Bonjour {indicatif}\n\nBienvenue sur le plugin de démo."
        return md, []
 
    if aid == "compteur_mots":
        texte = sv.get("TEXTE", "")
        if not texte:
            return "## ❌ Variable {TEXTE} manquante", []
        mots = texte.split()
        md = (f"## 📊 Statistiques\n\n"
              f"- Mots : **{len(mots)}**\n"
              f"- Caractères : **{len(texte)}**\n"
              f"- Plus long mot : **{max(mots, key=len)}**")
        return md, []
 
    return f"## ❌ Action inconnue : {aid}", []
