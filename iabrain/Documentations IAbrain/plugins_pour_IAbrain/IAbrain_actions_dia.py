# -*- coding: utf-8 -*-
"""
============================================================================
  IAbrain_actions_dia.py - Plugin IAbrain pour d-IA v1.1
============================================================================
  Auteur     : Jean-Louis (F1GBD) - ADRASEC 77 / FNRASEC
  Version    : 1.0 (Mai 2026)
  IAbrain    : v1.40.7+ requis (systeme de plugins externes)
  d-IA       : v1.1+ requis (mode ADRASEC enrichi avec rag_adrasec.json)

Objet
-----
Plugin IAbrain qui convertit les fiches techniques produites par d-IA
(fichier rag_adrasec.json) en Markdown structure, directement affichable
dans le chat IAbrain ET prepare pour indexation /index.

Le plugin ne touche PAS aux bases RAG d'IAbrain : il se contente d'afficher
le Markdown converti dans le chat. L'utilisateur peut ensuite :
  1. Copier le contenu et l'enregistrer comme .md
  2. Utiliser la commande /index sur ce fichier pour l'indexer en base
     perso permanente
Cette approche "Mode 1" respecte le contrat d'interface documente du plugin
et evite tout couplage fragile avec les API internes d'IAbrain.

Actions exposees
----------------
- dia_lister      : Liste les fiches presentes dans le rag_adrasec.json
- dia_convertir   : Convertit toutes les fiches en Markdown pour copie/index
- dia_par_domaine : Convertit en filtrant par domaine (SATER, NVIS, etc.)
- dia_haute_conf  : Convertit seulement les fiches a haute confiance

Installation
------------
Copier ce fichier dans le dossier `plugins/` situe a cote de IAbrain.exe
(ou IAbrain.py en mode source). IAbrain le detecte automatiquement au
demarrage suivant.

Pas de dependances supplementaires : uniquement la librairie standard
Python.
============================================================================
"""

import json
import re
from datetime import datetime
from pathlib import Path


# ----------------------------------------------------------------------------
# Contrat d'interface IAbrain v1.40.7+
# ----------------------------------------------------------------------------
# Trois fonctions obligatoires :
#   - list_actions() -> list[tuple[str, str]]
#       Retourne la liste des actions exposees : (action_id, libelle)
#   - is_action(action_id: str) -> bool
#       True si ce plugin gere cette action
#   - execute_action(action_id, imported_files, options=None)
#         -> tuple[str, list[str]]
#       Execute l'action. Retourne (markdown_a_afficher, warnings)
# ----------------------------------------------------------------------------

ACTIONS = [
    ("dia_lister",
     "d-IA — Lister les fiches du rag_adrasec.json"),
    ("dia_convertir",
     "d-IA — Convertir TOUTES les fiches en Markdown (pour /index)"),
    ("dia_par_domaine",
     "d-IA — Convertir les fiches d'un domaine (SATER, NVIS, ...)"),
    ("dia_haute_conf",
     "d-IA — Convertir uniquement les fiches a haute confiance"),
]


def list_actions():
    """Liste les actions exposees par ce plugin.

    Affichee dans le dialogue de configuration des macros Action d'IAbrain.
    """
    return list(ACTIONS)


def is_action(action_id):
    """Indique si ce plugin gere l'action demandee."""
    return action_id in {aid for aid, _label in ACTIONS}


def execute_action(action_id, imported_files, options=None):
    """Execute l'action demandee.

    Parametres
    ----------
    action_id : str
        Identifiant de l'action ('dia_lister', 'dia_convertir', etc.)
    imported_files : list[tuple[str, str]]
        Liste des fichiers importes dans IAbrain (nom, contenu).
        Si l'utilisateur a importe son rag_adrasec.json dans IAbrain via
        "Importer un fichier", on l'utilise. Sinon, on cherche aux endroits
        standards (cf. _trouver_rag_adrasec).
    options : dict, optionnel
        Options additionnelles. Cles potentielles :
        - "log"                  : callback log(msg) pour progression
        - "session_vars"         : dict des variables de session
        - "session_vars_manager" : manager pour ecrire des variables

    Retour
    ------
    (md, warnings) : tuple
        md : str
            Markdown a afficher dans le chat IAbrain.
        warnings : list[str]
            Messages d'avertissement non bloquants.
    """
    options = options or {}
    log = options.get("log") or (lambda _msg: None)
    warnings = []

    # --- 1. Recuperer le fichier rag_adrasec.json ---
    log("[d-IA] Recherche du fichier rag_adrasec.json...")
    rag_path, source_desc = _trouver_rag_adrasec(imported_files)
    if rag_path is None:
        return _aide_introuvable(), []

    log(f"[d-IA] Source : {source_desc}")

    # --- 2. Charger les fiches ---
    try:
        if isinstance(rag_path, Path):
            data = json.loads(rag_path.read_text(encoding="utf-8"))
        else:
            # rag_path est en realite le contenu textuel (fichier importe)
            data = json.loads(rag_path)
    except Exception as e:
        return (
            f"# Erreur\n\n"
            f"Impossible de lire le fichier rag_adrasec.json : `{e}`\n\n"
            f"Verifier que le fichier est un JSON valide produit par "
            f"d-IA v1.1 ou superieur.",
            [str(e)],
        )

    fiches = data.get("fiches", [])
    if not fiches:
        return (
            "# Aucune fiche trouvee\n\n"
            "Le fichier rag_adrasec.json existe mais ne contient aucune "
            "fiche.\n\n"
            "Verifier dans d-IA :\n"
            "- Mode ADRASEC enrichi active (Parametres IA > Mode ADRASEC)\n"
            "- LLM3 Moderateur correctement configure et teste\n"
            "- Au moins 8 messages echanges dans un dialogue (= 4 echanges)\n"
            "\n"
            "Lancer un dialogue, attendre les meta-messages "
            "« [Moderateur] N fiche(s) ajoutee(s) », puis reessayer.",
            [],
        )

    log(f"[d-IA] {len(fiches)} fiche(s) chargee(s)")

    # --- 3. Dispatcher selon l'action ---
    if action_id == "dia_lister":
        return _action_lister(fiches, data, source_desc), warnings

    if action_id == "dia_convertir":
        return _action_convertir(fiches, source_desc, log), warnings

    if action_id == "dia_par_domaine":
        domaine = _demander_domaine(fiches, options)
        if domaine is None:
            return _action_lister(fiches, data, source_desc), warnings
        return (
            _action_convertir_filtre(
                fiches, source_desc, log,
                filtre=lambda f: f.get("domaine", "").upper() == domaine,
                description=f"domaine = {domaine}",
            ),
            warnings,
        )

    if action_id == "dia_haute_conf":
        return (
            _action_convertir_filtre(
                fiches, source_desc, log,
                filtre=lambda f: f.get("confiance", "").lower() == "haute",
                description="confiance = haute",
            ),
            warnings,
        )

    return f"# Action inconnue\n\nAction `{action_id}` non geree.", warnings


# ============================================================================
#  Localisation du fichier rag_adrasec.json
# ============================================================================

def _trouver_rag_adrasec(imported_files):
    """Cherche le fichier rag_adrasec.json a divers endroits.

    Ordre de recherche :
      1. Dans les fichiers importes dans IAbrain (drag-drop ou bouton)
      2. Emplacements standards d-IA sur le disque

    Retourne (source, description) ou (None, None) si rien trouve.
    Si trouve via import : source = str (contenu du fichier)
    Si trouve sur disque : source = Path
    """
    # 1. Fichier importe dans IAbrain
    for nom, contenu in (imported_files or []):
        if Path(nom).name.lower() == "rag_adrasec.json":
            return contenu, f"fichier importe « {nom} »"

    # 2. Emplacements standards (par ordre de probabilite)
    candidates = [
        Path("C:/QITdevsrc/d-IA/rag_adrasec.json"),
        Path("C:/d-IA/rag_adrasec.json"),
        Path.home() / "Documents" / "d-IA" / "rag_adrasec.json",
        Path.home() / "d-IA" / "rag_adrasec.json",
        # Cas binaire compile : a cote de l'exe (variable)
        Path.cwd() / "rag_adrasec.json",
    ]

    for cand in candidates:
        try:
            if cand.exists() and cand.is_file():
                return cand, f"fichier disque « {cand} »"
        except (OSError, PermissionError):
            continue

    return None, None


def _aide_introuvable():
    """Retourne un message d'aide quand le fichier n'a pas ete trouve."""
    return (
        "# Fichier rag_adrasec.json introuvable\n\n"
        "Le plugin d-IA n'a pas trouve de fichier `rag_adrasec.json` "
        "exploitable.\n\n"
        "## Solutions\n\n"
        "**Option 1 — Importer le fichier dans IAbrain :**\n\n"
        "1. Ouvrir le menu **Importer** d'IAbrain (ou glisser-deposer)\n"
        "2. Selectionner votre `rag_adrasec.json` (typiquement dans "
        "`C:\\d-IA\\` ou `C:\\QITdevsrc\\d-IA\\`)\n"
        "3. Relancer cette action\n\n"
        "**Option 2 — Verifier les chemins standards :**\n\n"
        "Le plugin cherche automatiquement aux emplacements suivants :\n"
        "- `C:\\QITdevsrc\\d-IA\\rag_adrasec.json`\n"
        "- `C:\\d-IA\\rag_adrasec.json`\n"
        "- `<Documents>\\d-IA\\rag_adrasec.json`\n"
        "- `<Home>\\d-IA\\rag_adrasec.json`\n"
        "- Dossier courant\n\n"
        "Si votre fichier est ailleurs, deplacez-le ou utilisez l'Option 1.\n\n"
        "## Verification\n\n"
        "Si vous n'avez aucun fichier `rag_adrasec.json`, c'est qu'aucune "
        "fiche n'a encore ete extraite par d-IA. Verifier que :\n\n"
        "- d-IA v1.1 (ou superieur) est installe\n"
        "- Le mode ADRASEC enrichi est actif dans Parametres IA\n"
        "- Le LLM3 Moderateur est configure (onglet IA 3 - Moderateur)\n"
        "- Vous avez deja mene au moins un dialogue avec 8+ messages"
    )


# ============================================================================
#  Action : lister les fiches
# ============================================================================

def _action_lister(fiches, data, source_desc):
    """Affiche un tableau recapitulatif des fiches presentes dans le RAG."""
    lignes = []
    lignes.append("# Fiches d-IA disponibles")
    lignes.append("")
    lignes.append(f"**Source** : {source_desc}")
    lignes.append(f"**Total** : {len(fiches)} fiche(s)")
    if data.get("_total_dialogues"):
        lignes.append(f"**Dialogues capitalises** : {data['_total_dialogues']}")
    if data.get("_last_modified"):
        lignes.append(f"**Derniere mise a jour** : {data['_last_modified']}")
    lignes.append("")

    # Statistiques par domaine
    par_dom = {}
    par_conf = {"haute": 0, "moyenne": 0, "basse": 0, "?": 0}
    for f in fiches:
        dom = f.get("domaine", "?")
        par_dom[dom] = par_dom.get(dom, 0) + 1
        conf = f.get("confiance", "?").lower()
        par_conf[conf if conf in par_conf else "?"] += 1

    lignes.append("## Repartition par domaine")
    lignes.append("")
    lignes.append("| Domaine | Nombre |")
    lignes.append("|---|---|")
    for dom, n in sorted(par_dom.items(), key=lambda kv: -kv[1]):
        lignes.append(f"| {dom} | {n} |")
    lignes.append("")

    lignes.append("## Repartition par confiance")
    lignes.append("")
    lignes.append("| Niveau | Nombre |")
    lignes.append("|---|---|")
    for niveau in ("haute", "moyenne", "basse", "?"):
        if par_conf[niveau] > 0:
            lignes.append(f"| {niveau} | {par_conf[niveau]} |")
    lignes.append("")

    # Liste detaillee
    lignes.append("## Liste des fiches")
    lignes.append("")
    lignes.append("| # | Domaine | Titre | Confiance | Tags |")
    lignes.append("|---|---|---|---|---|")
    for i, f in enumerate(fiches, 1):
        titre = f.get("titre", "?")[:60]
        dom = f.get("domaine", "?")
        conf = f.get("confiance", "?")
        tags = ", ".join(f.get("tags", [])[:3])
        if len(f.get("tags", [])) > 3:
            tags += "..."
        lignes.append(f"| {i} | {dom} | {titre} | {conf} | {tags} |")

    lignes.append("")
    lignes.append("---")
    lignes.append("")
    lignes.append("**Pour convertir ces fiches en Markdown indexable :**")
    lignes.append("Lancer la macro Action « d-IA — Convertir TOUTES les fiches "
                  "en Markdown »")
    lignes.append("")

    return "\n".join(lignes)


# ============================================================================
#  Action : conversion des fiches en Markdown
# ============================================================================

def _action_convertir(fiches, source_desc, log):
    """Convertit toutes les fiches en Markdown affichable."""
    return _action_convertir_filtre(
        fiches, source_desc, log,
        filtre=None,
        description="toutes les fiches",
    )


def _action_convertir_filtre(fiches, source_desc, log, filtre, description):
    """Convertit les fiches qui passent le filtre en Markdown."""
    if filtre is None:
        fiches_select = fiches
    else:
        fiches_select = [f for f in fiches if filtre(f)]

    log(f"[d-IA] Conversion : {len(fiches_select)} fiche(s) selectionnee(s) "
        f"({description})")

    if not fiches_select:
        return (
            f"# Aucune fiche correspondante\n\n"
            f"Aucune fiche ne correspond au critere : **{description}**.\n\n"
            f"Source utilisee : {source_desc}\n"
            f"Total dans la base : {len(fiches)} fiche(s)\n"
        )

    # En-tete du document Markdown produit
    lignes = []
    lignes.append("# Fiches d-IA converties en Markdown")
    lignes.append("")
    lignes.append(
        f"**Selection** : {description} — "
        f"{len(fiches_select)}/{len(fiches)} fiche(s)"
    )
    lignes.append(f"**Source** : {source_desc}")
    lignes.append(
        f"**Genere le** : "
        f"{datetime.now().isoformat(timespec='seconds')}"
    )
    lignes.append("")
    lignes.append(
        "> **Pour indexer dans IAbrain :** copier le contenu ci-dessous "
        "dans un fichier `.md`, puis utiliser la commande `/index` ou le "
        "menu **Connaissances > Indexer un fichier (base perso)**. "
        "Choisir le mode **Permanent** pour conserver les fiches entre "
        "sessions."
    )
    lignes.append("")
    lignes.append("---")
    lignes.append("")

    # Conversion fiche par fiche
    for idx, fiche in enumerate(fiches_select, 1):
        lignes.append(_fiche_to_markdown(fiche, numero=idx))
        lignes.append("")
        lignes.append("---")
        lignes.append("")

    log(f"[d-IA] Conversion terminee ({len(fiches_select)} fiche(s))")

    return "\n".join(lignes)


def _fiche_to_markdown(fiche, numero=None):
    """Convertit une fiche en bloc Markdown structure.

    Le format est concu pour le chunking semantique d'IAbrain :
    chaque section porte son contexte (titre, tags, domaine) en
    en-tete, afin que le retrieval reste pertinent meme si le
    chunker coupe au milieu.
    """
    lignes = []

    titre = fiche.get("titre", "Sans titre")
    if numero is not None:
        lignes.append(f"## Fiche {numero} — {titre}")
    else:
        lignes.append(f"## {titre}")
    lignes.append("")

    # Bandeau metadonnees
    domaine = fiche.get("domaine", "GENERAL")
    tags = fiche.get("tags", [])
    confiance = fiche.get("confiance", "moyenne")
    date_str = fiche.get("date", "")[:10] if fiche.get("date") else "?"

    lignes.append(
        f"**Domaine** : {domaine} | "
        f"**Tags** : {', '.join(tags) if tags else '-'} | "
        f"**Confiance** : {confiance} | "
        f"**Date** : {date_str}"
    )
    lignes.append("")

    # Tracabilite source
    src = fiche.get("source_dialogue") or {}
    if src:
        sujet = src.get("sujet", "")
        theme = src.get("theme", "")
        modele = src.get("moderateur_modele", "?")
        if sujet or theme:
            lignes.append(
                f"*Source : Dialogue d-IA — Sujet « {sujet} » — "
                f"Theme « {theme} » — Moderateur {modele}*"
            )
            lignes.append("")

    # Resume
    resume = (fiche.get("resume") or "").strip()
    if resume:
        lignes.append("### Resume")
        lignes.append("")
        lignes.append(resume)
        lignes.append("")

    # Faits techniques
    faits = fiche.get("faits", []) or fiche.get("faits_techniques", [])
    if faits:
        lignes.append("### Faits techniques")
        lignes.append("")
        for f in faits:
            lignes.append(f"- {f}")
        lignes.append("")

    # Procedures
    procs = fiche.get("procedures", [])
    if procs:
        lignes.append("### Procedures operationnelles")
        lignes.append("")
        for i, proc in enumerate(procs, 1):
            lignes.append(f"**Etape {i} :** {proc}")
            lignes.append("")

    # Sources citees
    sources = fiche.get("sources_citees", []) or fiche.get("references", [])
    if sources:
        lignes.append("### Sources citees dans le dialogue")
        lignes.append("")
        for s in sources:
            lignes.append(f"- {s}")
        lignes.append("")

    # Disclaimer
    lignes.append(
        "*Fiche extraite automatiquement par d-IA v1.1. A relire et "
        "corriger avant exploitation operationnelle.*"
    )

    return "\n".join(lignes)


# ============================================================================
#  Helpers : selection du domaine via variables de session
# ============================================================================

def _demander_domaine(fiches, options):
    """Detecte le domaine cible via une variable de session DIA_DOMAINE.

    L'utilisateur peut definir cette variable dans IAbrain via /set :
        /set DIA_DOMAINE=SATER
    Puis lancer la macro Action "d-IA - Convertir les fiches d'un domaine".

    Si DIA_DOMAINE n'est pas defini, on retourne None et l'appelant
    affichera le panneau de listing avec les domaines disponibles.
    """
    session_vars = options.get("session_vars") or {}
    dom = session_vars.get("DIA_DOMAINE", "").strip().upper()
    if not dom:
        return None
    # Verifier que le domaine existe vraiment dans les fiches
    domaines_dispo = {f.get("domaine", "").upper() for f in fiches}
    if dom not in domaines_dispo:
        return None
    return dom


# ============================================================================
#  Auto-test (si execute directement, pas via IAbrain)
# ============================================================================

if __name__ == "__main__":
    print("=== Plugin IAbrain d-IA — Auto-test ===\n")
    print(f"Actions exposees : {len(ACTIONS)}")
    for aid, label in ACTIONS:
        print(f"  - {aid:20s} : {label}")
    print()
    print("Pour tester en conditions reelles :")
    print("  1. Copier ce fichier dans le dossier `plugins/` d'IAbrain")
    print("  2. Demarrer IAbrain")
    print("  3. Verifier dans le menu Aide > Diagnostic plugins")
    print("     que IAbrain_actions_dia.py est charge")
    print("  4. Creer une macro de type Action et selectionner")
    print("     l'une des actions ci-dessus.")
