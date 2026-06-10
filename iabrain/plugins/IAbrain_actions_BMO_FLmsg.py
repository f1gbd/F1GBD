# -*- coding: utf-8 -*-
"""IAbrain_actions_BMO_FLmsg.py — Plugin BRIEFING MÉTÉO OPÉRATIONNELLE → ICS-213.

Génère un message FLmsg ICS-213 (.213) contenant le briefing météo
opérationnel ADRASEC, puis ouvre l'application FLmsg pour finalisation
(expéditeur / destinataire) et envoi en AutoSend via TCQ.

═══════════════════════════════════════════════════════════════════════════
CHAÎNE OPÉRATIONNELLE
═══════════════════════════════════════════════════════════════════════════

    [ bouton METAR — LFXX ]      pose METAR_RAW / METAR_STATION
    [ bouton TAF   — LFXX ]      pose TAF_RAW   / TAF_STATION
    [ bouton BMO FLmsg     ]  →  ce plugin :
        1. (re)génère le briefing déterministe (moteur briefing_meteo)
        2. le formate en corps de message ICS-213
        3. écrit un fichier FLmsg « *.213 » prêt à l'emploi
        4. ouvre FLmsg sur ce fichier (To/From à compléter par l'opérateur)
        5. l'opérateur valide → AutoSend déclenché via TCQ

Le plugin N'ENVOIE JAMAIS le message lui-même : l'expéditeur, le
destinataire et le déclenchement de l'AutoSend restent sous le contrôle
de l'opérateur dans FLmsg / TCQ.

═══════════════════════════════════════════════════════════════════════════
FORMAT FLmsg ICS-213 (rétro-ingénierie du fichier exemple)
═══════════════════════════════════════════════════════════════════════════

Structure :

    <flmsg>4.0.24⏎
    :hdr_ed:21 ⏎
    F1GBD 20261006105655⏎
    <ics213>⏎
    :d1:8 10/06/26⏎
    :t1:5 1255L⏎
    :sb:38 BRIEFING MÉTÉO OPÉRATIONNEL ADRASEC⏎
    :mg:3094 <corps du briefing …>⏎

Règles décodées :
  • chaque champ = « :tag:LONGUEUR <valeur> » ;
  • LONGUEUR = nombre d'octets UTF-8 de la valeur, les sauts de ligne
    internes étant comptés comme un seul octet LF (\n) ;
  • le fichier sur disque utilise des fins de ligne CRLF (\r\n) : chaque
    \n logique devient \r\n à l'écriture, donc la longueur déclarée reste
    inférieure au nombre d'octets réellement écrits ;
  • encodage UTF-8 sans BOM ;
  • seuls les champs renseignés sont écrits ; les champs vides (To, From…)
    sont omis et apparaissent vierges dans FLmsg ;
  • le champ « hdr_ed » commence par un \n (artefact du « header editor »
    FLmsg) et contient « INDICATIF AAAAMMJJHHMMSS » ;
  • le sujet « :sb: » reprend le titre du briefing (sans l'émoji) ;
  • le corps « :mg: » reprend le briefing SANS la ligne de titre et SANS
    le pied de page, avec les puces « - » converties en « • ».

═══════════════════════════════════════════════════════════════════════════
CONFIGURATION : flmsg_path.json
═══════════════════════════════════════════════════════════════════════════

Fichier JSON recherché (premier trouvé) :
    1. chemin pointé par la variable d'environnement IABRAIN_FLMSG_CONF
    2. dans le dossier du présent plugin
    3. dans le dossier de plugins fourni par IAbrain (options["plugin_dir"])
    4. dans le répertoire courant

Forme complète (toutes les clés sauf flmsg_exe sont facultatives) :

    {
      "flmsg_exe":     "C:\\\\NBEMS\\\\flmsg-4.0.24\\\\flmsg.exe",
      "messages_dir":  "C:\\\\Users\\\\F1GBD\\\\NBEMS.files\\\\ICS\\\\messages",
      "callsign":      "F1GBD",
      "auto_open":     true,
      "flmsg_version": "4.0.24"
    }

Forme minimale acceptée (chaîne = chemin de l'exécutable) :

    "C:\\\\NBEMS\\\\flmsg-4.0.24\\\\flmsg.exe"

Si « messages_dir » est absent : on essaie ~/NBEMS.files/ICS/messages
(dossier FLmsg par défaut), sinon un dossier « BMO_messages » local.
Si « flmsg_exe » est absent / introuvable : le fichier .213 est écrit
mais FLmsg n'est pas ouvert (le chemin est indiqué à l'opérateur).

═══════════════════════════════════════════════════════════════════════════
ACTIONS EXPOSÉES (v1.0)
═══════════════════════════════════════════════════════════════════════════

  bmo_flmsg
      Génère le fichier ICS-213 ET ouvre FLmsg pour finalisation/AutoSend.

  bmo_flmsg_fichier
      Génère uniquement le fichier ICS-213 (n'ouvre pas FLmsg).

═══════════════════════════════════════════════════════════════════════════
VARIABLES DE SESSION
═══════════════════════════════════════════════════════════════════════════

Lues :
    METAR_RAW / METAR_STATION   posées par le plugin metar
    TAF_RAW   / TAF_STATION     posées par le plugin taf
    BRIEFING_METEO_RAW          briefing déjà calculé (repli si METAR/TAF
                                indisponibles en session)
    INDICATIF / CALLSIGN        indicatif station (repli pour hdr_ed)

Écrites :
    BMO_FLMSG_LAST_FILE         chemin du dernier .213 produit
    BMO_FLMSG_LAST_SUBJECT      sujet du dernier message produit

═══════════════════════════════════════════════════════════════════════════
F1GBD - ADRASEC 77 / FNRASEC — v1.0 juin 2026
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import time
from datetime import datetime
from typing import Any, List, Optional, Sequence, Tuple

__version__ = "1.1.0"

ACTION_BMO = "bmo_flmsg"
ACTION_BMO_FICHIER = "bmo_flmsg_fichier"
_ACTIONS = {ACTION_BMO, ACTION_BMO_FICHIER}

# Valeurs par défaut
_FLMSG_VERSION_DEFAUT = "4.0.24"
_INDICATIF_DEFAUT = "F1GBD"
_SUJET_DEFAUT = "BRIEFING MÉTÉO OPÉRATIONNEL ADRASEC"
_CONF_NOM = "flmsg_path.json"


# ===========================================================================
# 1. Accès au moteur de briefing déterministe (réutilisation, pas de copie)
# ===========================================================================

_ENGINE_CACHE: Any = None


def _engine() -> Any:
    """Importe (une seule fois) le moteur IAbrain_actions_briefing_meteo.

    Retourne le module, ou None s'il est introuvable. Dans ce dernier cas,
    le plugin se rabat sur la variable de session BRIEFING_METEO_RAW.
    """
    global _ENGINE_CACHE
    if _ENGINE_CACHE is not None:
        return _ENGINE_CACHE or None
    try:
        import IAbrain_actions_briefing_meteo as _bm  # type: ignore
        _ENGINE_CACHE = _bm
    except Exception:
        _ENGINE_CACHE = False
    return _ENGINE_CACHE or None


# ===========================================================================
# 2. Helpers session
# ===========================================================================

def _get_session_vars(options: Any) -> dict:
    if not options or not isinstance(options, dict):
        return {}
    sv = options.get("session_vars")
    return sv if isinstance(sv, dict) else {}


def _get_var(session_vars: dict, name: str, default: str = "") -> str:
    if not isinstance(session_vars, dict):
        return default
    v = session_vars.get(name)
    if v is None:
        return default
    s = str(v).strip()
    return s if s else default


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


# ===========================================================================
# 3. Configuration flmsg_path.json
# ===========================================================================

def _conf_candidats(options: Any) -> List[str]:
    cands: List[str] = []
    env = os.environ.get("IABRAIN_FLMSG_CONF")
    if env:
        cands.append(env)
    try:
        here = os.path.dirname(os.path.abspath(__file__))
    except Exception:
        here = os.getcwd()
    # 1. à côté du présent plugin (emplacement recommandé)
    cands.append(os.path.join(here, _CONF_NOM))
    # 2. dossiers fournis par IAbrain via options
    if isinstance(options, dict):
        for key in ("plugin_dir", "plugins_dir", "app_dir", "base_dir",
                    "work_dir", "working_dir", "config_dir", "data_dir"):
            d = options.get(key)
            if d:
                cands.append(os.path.join(str(d), _CONF_NOM))
    # 3. répertoire courant
    cands.append(os.path.join(os.getcwd(), _CONF_NOM))
    # 4. dossier personnel et configs usuelles
    home = os.path.expanduser("~")
    cands.append(os.path.join(home, _CONF_NOM))
    cands.append(os.path.join(home, ".iabrain", _CONF_NOM))
    cands.append(os.path.join(home, "IAbrain", _CONF_NOM))
    # Déduplication en préservant l'ordre
    vus = set()
    uniques: List[str] = []
    for c in cands:
        if c and c not in vus:
            vus.add(c)
            uniques.append(c)
    return uniques


def _normaliser_conf(data: Any, base_dir: str, source: Optional[str]) -> dict:
    conf = {
        "flmsg_exe": "",
        "messages_dir": "",
        "callsign": "",
        "auto_open": True,
        "flmsg_version": _FLMSG_VERSION_DEFAUT,
        "base_dir": base_dir,
        "source": source,
    }
    if isinstance(data, str):
        conf["flmsg_exe"] = data.strip()
        return conf
    if isinstance(data, dict):
        for k in ("flmsg_exe", "flmsg_path", "path", "exe", "flmsg"):
            if data.get(k):
                conf["flmsg_exe"] = str(data[k]).strip()
                break
        for k in ("messages_dir", "msg_dir", "output_dir",
                  "out_dir", "dossier_messages"):
            if data.get(k):
                conf["messages_dir"] = str(data[k]).strip()
                break
        if data.get("callsign"):
            conf["callsign"] = str(data["callsign"]).strip()
        if "auto_open" in data:
            conf["auto_open"] = bool(data["auto_open"])
        if data.get("flmsg_version"):
            conf["flmsg_version"] = str(data["flmsg_version"]).strip()
    return conf


def _doubler_antislashs_isoles(text: str) -> str:
    """Double les antislashs ISOLÉS, en préservant les paires « \\\\ » déjà
    correctes.

    Dans un fichier de chemins Windows, un « \\ » est toujours un séparateur,
    jamais une séquence d'échappement. Ce scan transforme un « \\ » solitaire
    en « \\\\ » (échappement JSON correct) et laisse les « \\\\ » existants
    intacts — il gère donc les fichiers MIXTES (certaines valeurs en
    antislashs simples, d'autres en doubles). Contrairement à une regex
    avec lookahead, il ne se laisse pas piéger par « \\f », « \\t », etc.
    """
    out: List[str] = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch == "\\":
            if i + 1 < n and text[i + 1] == "\\":
                out.append("\\\\")   # paire déjà correcte : on la conserve
                i += 2
            else:
                out.append("\\\\")   # antislash isolé : on le double
                i += 1
        else:
            out.append(ch)
            i += 1
    return "".join(out)


def _charger_json_tolerant(text: str) -> Tuple[Any, str]:
    """Parse un JSON, en réparant les antislashs Windows non échappés.

    Sous Windows, les chemins « C:\\Program Files\\flmsg.exe » écrits avec
    des antislashs SIMPLES produisent un JSON invalide. On tente d'abord un
    parsing strict (qui gère parfaitement « / » et « \\\\ ») ; en cas
    d'échec, on double les antislashs isolés puis on re-parse.

    Retourne (données | None, note) où note vaut :
        ""          parsing strict réussi
        "REPAIRED"  parsing réussi après réparation des antislashs
        "ERR:…"     échec définitif (données = None)
    """
    try:
        return json.loads(text), ""
    except json.JSONDecodeError:
        try:
            return json.loads(_doubler_antislashs_isoles(text)), "REPAIRED"
        except json.JSONDecodeError as e2:
            return None, f"ERR:{e2}"


def _charger_conf(options: Any) -> dict:
    try:
        here = os.path.dirname(os.path.abspath(__file__))
    except Exception:
        here = os.getcwd()

    diag = {"checked": [], "found": None, "parse_error": None,
            "repaired": False}

    for c in _conf_candidats(options):
        diag["checked"].append(c)
        if not (c and os.path.isfile(c)):
            continue
        try:
            with open(c, "r", encoding="utf-8-sig") as f:
                txt = f.read()
        except Exception as e:
            diag["parse_error"] = f"{c} : lecture impossible ({e})"
            continue
        data, note = _charger_json_tolerant(txt)
        if data is None:
            diag["parse_error"] = f"{c} : {note[4:]}"
            continue
        diag["found"] = c
        diag["repaired"] = (note == "REPAIRED")
        conf = _normaliser_conf(data, os.path.dirname(c), c)
        conf["_diag"] = diag
        return conf

    conf = _normaliser_conf({}, here, None)
    conf["_diag"] = diag
    return conf


def _resoudre_dossier_sortie(conf: dict) -> str:
    """Dossier d'écriture du .213 (créé si nécessaire)."""
    md = conf.get("messages_dir")
    if md:
        d = os.path.expanduser(os.path.expandvars(md))
        try:
            os.makedirs(d, exist_ok=True)
            return d
        except Exception:
            pass
    d = os.path.join(os.path.expanduser("~"), "NBEMS.files", "ICS", "messages")
    try:
        os.makedirs(d, exist_ok=True)
        return d
    except Exception:
        pass
    d = os.path.join(conf.get("base_dir") or os.getcwd(), "BMO_messages")
    os.makedirs(d, exist_ok=True)
    return d


def _resoudre_indicatif(conf: dict, session_vars: dict) -> str:
    for src in (
        conf.get("callsign"),
        _get_var(session_vars, "INDICATIF"),
        _get_var(session_vars, "CALLSIGN"),
    ):
        if src and str(src).strip():
            return str(src).strip().upper()
    return _INDICATIF_DEFAUT


def _prochain_serial(base_dir: str) -> str:
    """Compteur 2 chiffres (00→99) persistant dans bmo_serial.json."""
    p = os.path.join(base_dir or os.getcwd(), "bmo_serial.json")
    n = 0
    try:
        with open(p, "r", encoding="utf-8") as f:
            n = int(json.load(f).get("n", 0))
    except Exception:
        n = 0
    n = (n + 1) % 100
    try:
        with open(p, "w", encoding="utf-8") as f:
            json.dump({"n": n}, f)
    except Exception:
        n = int(time.time()) % 100
    return f"{n:02d}"


# ===========================================================================
# 4. Construction du fichier FLmsg ICS-213
# ===========================================================================

def _utf8_len(value: str) -> int:
    """Longueur en octets UTF-8, sauts de ligne comptés en LF (\\n)."""
    return len(value.encode("utf-8"))


def _flmsg_field(tag: str, value: str) -> str:
    """Sérialise un champ FLmsg « :tag:LONGUEUR <valeur> » (LF interne)."""
    return f":{tag}:{_utf8_len(value)} {value}"


def construire_ics213(callsign: str,
                      horodatage: str,
                      date_str: str,
                      time_str: str,
                      sujet: str,
                      corps: str,
                      flmsg_version: str = _FLMSG_VERSION_DEFAUT) -> str:
    """Assemble le document ICS-213 complet (fins de ligne LF).

    La conversion LF→CRLF est effectuée à l'écriture (voir ecrire_ics213).
    L'ordre et le jeu de champs reproduisent fidèlement le fichier exemple.
    """
    segs = [
        f"<flmsg>{flmsg_version}",
        _flmsg_field("hdr_ed", "\n" + f"{callsign} {horodatage}"),
        "<ics213>",
        _flmsg_field("d1", date_str),
        _flmsg_field("t1", time_str),
        _flmsg_field("sb", sujet),
        _flmsg_field("mg", corps),
    ]
    return "\n".join(segs) + "\n"


def ecrire_ics213(path: str, doc_lf: str) -> int:
    """Écrit le document en UTF-8 sans BOM avec fins de ligne CRLF.

    Retourne le nombre d'octets écrits.
    """
    data = doc_lf.replace("\r\n", "\n").replace("\n", "\r\n").encode("utf-8")
    with open(path, "wb") as f:
        f.write(data)
    return len(data)


# ===========================================================================
# 5. Transformation briefing → (sujet, corps ICS-213)
# ===========================================================================

def _extraire_sujet_corps(briefing_txt: str) -> Tuple[str, str]:
    """À partir du briefing en texte brut, retourne (sujet, corps_mg).

    • le sujet = ligne de titre, émoji/ponctuation de tête retirés ;
    • le corps = briefing sans la ligne de titre et sans le pied de page,
      puces « - » converties en « • », markdown résiduel nettoyé.
    """
    lignes = (briefing_txt or "").replace("\r\n", "\n").split("\n")

    # --- 1. Titre → sujet, retiré du corps -------------------------------
    sujet = _SUJET_DEFAUT
    reste: List[str] = []
    titre_trouve = False
    for ln in lignes:
        if (not titre_trouve) and ("BRIEFING MÉTÉO OPÉRATIONNEL" in ln.upper()):
            s = re.sub(r"^[^0-9A-Za-zÀ-ÿ]+", "", ln).strip()
            if s:
                sujet = s
            titre_trouve = True
            continue
        reste.append(ln)

    # --- 2. Suppression du pied de page (séparateur « --- » → fin) -------
    for i, ln in enumerate(reste):
        if ln.strip() == "---":
            reste = reste[:i]
            while reste and reste[-1].strip() == "":
                reste.pop()
            break

    # --- 3. Nettoyage markdown résiduel + puces « - » → « • » ------------
    nettoyees: List[str] = []
    for ln in reste:
        ln = re.sub(r"\*\*([^*]+)\*\*", r"\1", ln)
        ln = re.sub(r"\*([^*]+)\*", r"\1", ln)
        ln = re.sub(r"^#{1,6}\s+", "", ln)
        ln = re.sub(r"^(\s*)[-*]\s+", r"\1• ", ln)
        nettoyees.append(ln)

    # --- 4. Rognage des lignes vides de tête et de queue ----------------
    while nettoyees and nettoyees[0].strip() == "":
        nettoyees.pop(0)
    while nettoyees and nettoyees[-1].strip() == "":
        nettoyees.pop()

    return sujet, "\n".join(nettoyees)


def _obtenir_briefing(session_vars: dict) -> Tuple[Optional[str], List[str]]:
    """Retourne (briefing_txt, warnings) ou (None, warnings) si indisponible."""
    warnings: List[str] = []
    metar_raw = _get_var(session_vars, "METAR_RAW")
    taf_raw = _get_var(session_vars, "TAF_RAW")

    eng = _engine()
    if eng and (metar_raw or taf_raw):
        metar = eng._parser_metar(metar_raw) if metar_raw else {}
        taf = eng._parser_taf(taf_raw) if taf_raw else {}
        ms = _get_var(session_vars, "METAR_STATION") or (metar.get("oaci") or "?")
        ts = _get_var(session_vars, "TAF_STATION") or (taf.get("oaci") or "?")
        if not metar_raw:
            warnings.append("METAR_RAW absent — briefing partiel (TAF seul)")
        if not taf_raw:
            warnings.append("TAF_RAW absent — briefing partiel (METAR seul)")
        _md, txt = eng._composer_briefing(metar, taf, ms, ts)
        return txt, warnings

    brief = _get_var(session_vars, "BRIEFING_METEO_RAW")
    if brief:
        if not eng:
            warnings.append(
                "moteur briefing_meteo introuvable — réutilisation de "
                "BRIEFING_METEO_RAW (briefing déjà calculé)")
        else:
            warnings.append(
                "METAR_RAW/TAF_RAW absents — réutilisation de "
                "BRIEFING_METEO_RAW (briefing déjà calculé)")
        return brief, warnings

    return None, warnings


# ===========================================================================
# 6. Lancement de FLmsg
# ===========================================================================

def _lancer_flmsg(exe: str, fichier: str) -> Tuple[bool, str]:
    """Ouvre FLmsg sur le fichier .213 (processus détaché, non bloquant)."""
    if not exe:
        return False, "aucun chemin FLmsg configuré (flmsg_path.json)"
    if not os.path.isfile(exe):
        return False, f"exécutable FLmsg introuvable : {exe}"
    try:
        if os.name == "nt":
            flags = (getattr(subprocess, "DETACHED_PROCESS", 0)
                     | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0))
            subprocess.Popen([exe, fichier], close_fds=True,
                             creationflags=flags)
        else:
            subprocess.Popen([exe, fichier], close_fds=True,
                             start_new_session=True)
        return True, ""
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


# ===========================================================================
# 7. Action principale
# ===========================================================================

def _action_bmo(session_vars: dict,
                options: Any,
                ouvrir_flmsg: bool) -> Tuple[str, List[str]]:
    # 7.1 Récupérer / générer le briefing -------------------------------
    briefing_txt, warnings = _obtenir_briefing(session_vars)
    if briefing_txt is None:
        return (
            "## ⚠️ Données météo absentes\n\n"
            "Impossible de produire le briefing ICS-213 : aucune source "
            "disponible en session. Procédure :\n\n"
            "1. Cliquez un bouton « METAR — LFXX » (conditions actuelles).\n"
            "2. Cliquez un bouton « TAF — LFXX » (prévision).\n"
            "3. (facultatif) « BRIEFING MÉTÉO » pour prévisualiser.\n"
            "4. Re-cliquez « BMO FLmsg » : le fichier ICS-213 sera généré.",
            warnings + ["bmo_flmsg : ni METAR/TAF ni BRIEFING_METEO_RAW"],
        )

    sujet, corps = _extraire_sujet_corps(briefing_txt)

    # 7.2 Configuration --------------------------------------------------
    conf = _charger_conf(options)
    callsign = _resoudre_indicatif(conf, session_vars)
    now = datetime.now()
    horodatage = now.strftime("%Y%m%d%H%M%S")
    date_str = now.strftime("%d/%m/%y")
    time_str = now.strftime("%H%M") + "L"

    # 7.3 Construction + écriture du fichier .213 ------------------------
    doc = construire_ics213(callsign, horodatage, date_str, time_str,
                            sujet, corps, conf["flmsg_version"])
    out_dir = _resoudre_dossier_sortie(conf)
    serial = _prochain_serial(conf.get("base_dir") or out_dir)
    fname = f"{callsign}-BMO-{now:%Y%m%d}-{now:%H%M%S}L-{serial}.213"
    path = os.path.join(out_dir, fname)
    try:
        octets = ecrire_ics213(path, doc)
    except Exception as e:
        return (
            f"## ❌ Échec d'écriture du fichier ICS-213\n\n"
            f"Dossier : `{out_dir}`\n\n`{type(e).__name__}` : {e}",
            warnings + [f"bmo_flmsg : écriture impossible ({e})"],
        )

    _set_session_var(options, "BMO_FLMSG_LAST_FILE", path)
    _set_session_var(options, "BMO_FLMSG_LAST_SUBJECT", sujet)

    # 7.4 Ouverture FLmsg (si demandée) ---------------------------------
    ligne_flmsg = ""
    if ouvrir_flmsg and conf.get("auto_open", True):
        ok, err = _lancer_flmsg(conf.get("flmsg_exe", ""), path)
        if ok:
            ligne_flmsg = ("✅ **FLmsg ouvert** sur le message — complétez "
                           "l'expéditeur et le destinataire, puis lancez "
                           "l'**AutoSend** (via TCQ).")
        else:
            ligne_flmsg = (f"⚠️ **FLmsg non ouvert** ({err}). Ouvrez "
                           f"manuellement le fichier ci-dessous.")
            warnings.append(f"bmo_flmsg : FLmsg non lancé — {err}")
    elif ouvrir_flmsg and not conf.get("auto_open", True):
        ligne_flmsg = ("ℹ️ Ouverture automatique désactivée "
                       "(`auto_open: false`). Ouvrez le fichier manuellement.")
    else:
        ligne_flmsg = ("ℹ️ Fichier généré sans ouverture de FLmsg "
                       "(action « fichier seul »).")

    # 7.5 Compte rendu Markdown -----------------------------------------
    nb_lignes_corps = corps.count("\n") + 1 if corps else 0
    diag = conf.get("_diag") or {}
    exe = conf.get("flmsg_exe", "")

    # Bloc d'état de la configuration (clair et actionnable)
    if diag.get("found"):
        rep = " — antislashs Windows réparés auto" if diag.get("repaired") else ""
        conf_lignes = [f"flmsg_path.json : `{diag['found']}`{rep}"]
        if exe:
            existe = os.path.isfile(exe)
            etat = "trouvé" if existe else "⚠️ INTROUVABLE sur le disque"
            conf_lignes.append(f"flmsg_exe : `{exe}` ({etat})")
        else:
            conf_lignes.append("⚠️ clé `flmsg_exe` absente ou vide")
    elif diag.get("parse_error"):
        conf_lignes = [
            f"⚠️ **flmsg_path.json trouvé mais ILLISIBLE** : {diag['parse_error']}",
            "→ JSON invalide. Utilisez des `/` (ex. "
            "`\"C:/Program Files (x86)/flmsg-4.0.24/flmsg.exe\"`) "
            "ou doublez les antislashs (`\\\\`).",
        ]
    else:
        checked = diag.get("checked") or []
        liste = "\n".join(f"  • `{c}`" for c in checked) or "  (aucun)"
        conf_lignes = [
            f"⚠️ **aucun {_CONF_NOM} trouvé**. Chemins testés :\n{liste}",
            f"→ Placez `{_CONF_NOM}` à côté du plugin, ou définissez la "
            "variable d'environnement `IABRAIN_FLMSG_CONF`.",
        ]
    conf_bloc = "\n".join(conf_lignes)

    md = (
        "## 📡 Message ICS-213 généré (Briefing Météo Opérationnelle)\n\n"
        f"**Sujet** : {sujet}\n\n"
        f"**Fichier** : `{path}`\n"
        f"({octets} octets écrits, corps de {nb_lignes_corps} lignes "
        f"/ {_utf8_len(corps)} octets)\n\n"
        f"**En-tête** : {callsign} — {date_str} {time_str}\n\n"
        f"{ligne_flmsg}\n\n"
        "---\n"
        "### ▶️ Étapes restantes dans FLmsg\n"
        "1. Renseigner **De (expéditeur)** et **À (destinataire)**.\n"
        "2. Vérifier le corps du message (déjà rempli).\n"
        "3. Déclencher l'**AutoSend** — l'acheminement radio est pris en "
        "charge par **TCQ**.\n\n"
        "---\n"
        f"### ⚙️ Configuration\n{conf_bloc}"
    )
    return md, warnings


# ===========================================================================
# 8. Point d'entrée IAbrain
# ===========================================================================

def is_action(action_id: str) -> bool:
    return (action_id or "").strip() in _ACTIONS


def list_actions() -> List[Tuple[str, str, str]]:
    return [
        (
            ACTION_BMO,
            "BMO FLmsg — Briefing météo → ICS-213 + ouverture FLmsg",
            "Génère un message FLmsg ICS-213 (.213) contenant le briefing "
            "météo opérationnel ADRASEC (à partir de METAR_RAW/TAF_RAW ou de "
            "BRIEFING_METEO_RAW), puis ouvre FLmsg pour saisie de "
            "l'expéditeur/destinataire et envoi en AutoSend via TCQ. Le "
            "chemin de l'exécutable FLmsg est lu dans flmsg_path.json. "
            "Pré-requis : avoir cliqué METAR puis TAF (ou BRIEFING MÉTÉO).",
        ),
        (
            ACTION_BMO_FICHIER,
            "BMO FLmsg — Générer le fichier ICS-213 seul",
            "Identique à « BMO FLmsg » mais n'ouvre PAS FLmsg : produit "
            "uniquement le fichier .213 et indique son chemin. Utile pour "
            "préparer un message hors ligne ou en lot.",
        ),
    ]


def execute_action(action_id: str,
                   imported_files: Sequence[Tuple[str, str]] = (),
                   options: Any = None) -> Tuple[str, List[str]]:
    aid = (action_id or "").strip()
    session_vars = _get_session_vars(options)
    try:
        if aid == ACTION_BMO:
            return _action_bmo(session_vars, options, ouvrir_flmsg=True)
        if aid == ACTION_BMO_FICHIER:
            return _action_bmo(session_vars, options, ouvrir_flmsg=False)
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        return (
            f"## ❌ Erreur interne du plugin BMO_FLmsg\n\n"
            f"`{type(e).__name__}` : {e}\n\n```\n{tb}\n```",
            [f"plugin BMO_FLmsg : exception {type(e).__name__}"],
        )
    return f"## ❌ Action inconnue : `{aid}`", []


# ===========================================================================
# 9. Autotest
# ===========================================================================

def _autotest() -> int:
    print(f"=== Autotest IAbrain_actions_BMO_FLmsg v{__version__} ===\n")
    erreurs = 0

    # ----- Test 1 : contrat d'interface --------------------------------
    print("[1] Contrat d'interface")
    actions = list_actions()
    assert len(actions) == 2
    assert is_action(ACTION_BMO)
    assert is_action(ACTION_BMO_FICHIER)
    assert not is_action("briefing_meteo")
    print(f"    OK ({len(actions)} actions exposées)")

    # ----- Test 2 : encodage de champ FLmsg (longueurs octets UTF-8) ---
    print("[2] Encodage de champ — longueur octets UTF-8")
    assert _flmsg_field("d1", "10/06/26") == ":d1:8 10/06/26"
    assert _flmsg_field("t1", "1255L") == ":t1:5 1255L"
    # « BRIEFING MÉTÉO OPÉRATIONNEL ADRASEC » : 35 caractères, 3 « É »
    # multi-octets → 38 octets.
    assert _flmsg_field("sb", _SUJET_DEFAUT) == \
        ":sb:38 BRIEFING MÉTÉO OPÉRATIONNEL ADRASEC", \
        _flmsg_field("sb", _SUJET_DEFAUT)
    # hdr_ed avec \n de tête : 1 + 20 = 21
    assert _flmsg_field("hdr_ed", "\nF1GBD 20261006105655") == \
        ":hdr_ed:21 \nF1GBD 20261006105655"
    print("    OK (d1=8, t1=5, sb=38, hdr_ed=21)")

    # ----- Test 3 : en-tête byte-identique au fichier exemple ----------
    print("[3] En-tête reproduit byte-à-byte (vs exemple)")
    here = os.path.dirname(os.path.abspath(__file__))
    ex_path = os.path.join(here, "exemple.213")
    if os.path.isfile(ex_path):
        exemple = open(ex_path, "rb").read()
        # Reconstruire le préfixe jusqu'à (inclus) « :sb:… » avec les
        # valeurs exactes de l'exemple.
        doc = construire_ics213(
            callsign="F1GBD",
            horodatage="20261006105655",
            date_str="10/06/26",
            time_str="1255L",
            sujet="BRIEFING MÉTÉO OPÉRATIONNEL ADRASEC",
            corps="X",  # corps factice, on ne compare que l'en-tête
            flmsg_version="4.0.24",
        )
        genere = doc.replace("\n", "\r\n").encode("utf-8")
        # Comparer jusqu'à la fin du champ :sb: (juste avant :mg:)
        coupe = exemple.find(b":mg:")
        assert genere[:coupe] == exemple[:coupe], (
            "divergence en-tête:\n"
            f"  généré : {genere[:coupe]!r}\n"
            f"  exemple: {exemple[:coupe]!r}"
        )
        print(f"    OK ({coupe} octets d'en-tête identiques)")
    else:
        print("    (exemple.213 absent — test ignoré)")

    # ----- Test 4 : round-trip — relire les longueurs déclarées --------
    print("[4] Round-trip : longueurs déclarées == octets réels (LF)")
    corps_test = ("Ligne 1\n• puce A\n• puce B\nLigne finale avec accents "
                  "é à ù ç.")
    doc = construire_ics213("F4JHW", "20260610130000", "10/06/26",
                            "1300L", _SUJET_DEFAUT, corps_test)
    disque = doc.replace("\n", "\r\n").encode("utf-8")
    # Reparser chaque champ
    for tag in (b"hdr_ed", b"d1", b"t1", b"sb", b"mg"):
        i = disque.find(b":" + tag + b":")
        assert i >= 0, f"champ {tag!r} absent"
        m = re.match(rb":" + tag + rb":(\d+) ", disque[i:])
        assert m, f"champ {tag!r} mal formé"
        decl = int(m.group(1))
        deb = i + m.end()
        # valeur = decl octets en comptage LF → relire en convertissant CRLF
        # On extrait jusqu'à la fin puis on convertit pour mesurer.
        val_lf = disque[deb:].replace(b"\r\n", b"\n")[:decl]
        assert len(val_lf) == decl, \
            f"{tag!r}: longueur {len(val_lf)} != déclarée {decl}"
    print("    OK (hdr_ed, d1, t1, sb, mg)")

    # ----- Test 5 : extraction sujet + corps (titre/pied retirés) ------
    print("[5] Transformation briefing → (sujet, corps)")
    briefing = (
        "📋 BRIEFING MÉTÉO OPÉRATIONNEL ADRASEC\n"
        "Stations : METAR LFPM — TAF LFPO\n"
        "\n"
        "1. ☁️ SITUATION ACTUELLE (METAR)\n"
        "Vent d'ouest à 09 kt.\n"
        "\n"
        "2. 🔮 PRÉVISION (TAF)\n"
        "Évolutions notables :\n"
        "- Le 10 entre 07h et 10h UTC (TEMPO) : faibles averses.\n"
        "\n"
        "---\n"
        "Briefing généré à partir du METAR et du TAF. Réf. F1GBD - FNRASEC."
    )
    sujet, corps = _extraire_sujet_corps(briefing)
    assert sujet == "BRIEFING MÉTÉO OPÉRATIONNEL ADRASEC", sujet
    assert "📋" not in corps, "émoji titre présent dans le corps"
    assert "BRIEFING MÉTÉO OPÉRATIONNEL ADRASEC" not in corps, \
        "titre dupliqué dans le corps"
    assert "---" not in corps, "séparateur de pied présent"
    assert "Briefing généré" not in corps, "pied de page présent"
    assert "• Le 10 entre 07h" in corps, "puce non convertie"
    assert "- Le 10 entre 07h" not in corps, "puce markdown résiduelle"
    assert corps.startswith("Stations : METAR LFPM"), corps[:40]
    print("    OK (titre→sujet, pied retiré, « - »→« • »)")

    # ----- Test 6 : nettoyage markdown gras résiduel -------------------
    print("[6] Nettoyage markdown résiduel (**gras**)")
    s, c = _extraire_sujet_corps(
        "BRIEFING MÉTÉO OPÉRATIONNEL ADRASEC\n"
        "**Période de validité** : du 10 au 11.\n"
        "- **Vent fort** : rafales > 25 kt."
    )
    assert "**" not in c, "gras non nettoyé"
    assert "Période de validité : du 10" in c
    assert "• Vent fort : rafales" in c
    print("    OK")

    # ----- Test 7 : génération end-to-end via moteur (si dispo) --------
    print("[7] Génération end-to-end (METAR + TAF en session)")
    eng = _engine()
    if eng:
        import tempfile
        tmp = tempfile.mkdtemp(prefix="bmo_")
        conf_path = os.path.join(tmp, _CONF_NOM)
        with open(conf_path, "w", encoding="utf-8") as f:
            json.dump({"messages_dir": tmp, "callsign": "F1GBD",
                       "auto_open": False}, f)
        os.environ["IABRAIN_FLMSG_CONF"] = conf_path
        sv = {
            "METAR_STATION": "LFPM",
            "METAR_RAW": "LFPM 101030Z AUTO 29009KT 9999 FEW048 BKN068 "
                         "BKN084 17/09 Q1020",
            "TAF_STATION": "LFPO",
            "TAF_RAW": "LFPO 100500Z 1006/1112 27006KT 9999 FEW015 BKN050 "
                       "TEMPO 1007/1010 FEW025TCU -SHRA "
                       "PROB30 TEMPO 1015/1017 27015G30KT 4000 SCT030TCU -SHRA",
        }
        md, ws = execute_action(ACTION_BMO_FICHIER,
                                options={"session_vars": sv})
        assert "Message ICS-213 généré" in md, md[:200]
        # Retrouver le fichier créé
        fics = [x for x in os.listdir(tmp) if x.endswith(".213")]
        assert fics, "aucun .213 produit"
        produit = open(os.path.join(tmp, fics[0]), "rb").read()
        assert produit.startswith(b"<flmsg>4.0.24\r\n"), "en-tête FLmsg KO"
        assert b"<ics213>\r\n" in produit
        assert b":mg:" in produit and b":sb:" in produit
        assert b"BKN068" not in produit, "METAR brut fuite dans le message"
        # Anti-régression hallucination : pas d'année inventée
        texte = produit.decode("utf-8")
        assert "2023" not in texte and "2024" not in texte
        assert "station voisine" in texte.lower(), "note LFPM≠LFPO absente"
        # Le nom de fichier suit le motif attendu
        assert re.match(r"F1GBD-BMO-\d{8}-\d{6}L-\d{2}\.213$", fics[0]), fics[0]
        os.environ.pop("IABRAIN_FLMSG_CONF", None)
        print(f"    OK (fichier {fics[0]}, {len(produit)} octets)")
    else:
        print("    (moteur briefing_meteo absent — test ignoré)")

    # ----- Test 8 : repli sur BRIEFING_METEO_RAW ----------------------
    print("[8] Repli sur BRIEFING_METEO_RAW (sans METAR/TAF)")
    import tempfile
    tmp2 = tempfile.mkdtemp(prefix="bmo2_")
    conf_path2 = os.path.join(tmp2, _CONF_NOM)
    with open(conf_path2, "w", encoding="utf-8") as f:
        json.dump({"messages_dir": tmp2, "auto_open": False}, f)
    os.environ["IABRAIN_FLMSG_CONF"] = conf_path2
    sv2 = {"BRIEFING_METEO_RAW":
           "📋 BRIEFING MÉTÉO OPÉRATIONNEL ADRASEC\n"
           "Stations : METAR LFBO — TAF LFBO\n"
           "1. ☁️ SITUATION ACTUELLE (METAR)\n"
           "Vent calme.\n"}
    md, ws = execute_action(ACTION_BMO_FICHIER, options={"session_vars": sv2})
    assert "Message ICS-213 généré" in md
    fics2 = [x for x in os.listdir(tmp2) if x.endswith(".213")]
    assert fics2, "aucun .213 produit en repli"
    os.environ.pop("IABRAIN_FLMSG_CONF", None)
    print(f"    OK (fichier {fics2[0]})")

    # ----- Test 9 : message d'erreur si rien en session ---------------
    print("[9] Aucune donnée en session → message d'aide")
    md, ws = execute_action(ACTION_BMO, options={"session_vars": {}})
    assert "absentes" in md.lower()
    assert "METAR" in md and "TAF" in md
    print("    OK")

    # ----- Test 10 : conf chaîne simple (chemin exe) ------------------
    print("[10] flmsg_path.json sous forme de chaîne simple")
    conf = _normaliser_conf("C:\\NBEMS\\flmsg.exe", "C:\\x", None)
    assert conf["flmsg_exe"] == "C:\\NBEMS\\flmsg.exe"
    assert conf["auto_open"] is True
    conf = _normaliser_conf({"path": "/usr/bin/flmsg", "auto_open": False},
                            "/x", None)
    assert conf["flmsg_exe"] == "/usr/bin/flmsg"
    assert conf["auto_open"] is False
    print("    OK")

    # ----- Test 11 : chargeur JSON tolérant aux antislashs Windows -----
    print("[11] JSON tolérant : fichier mixte simples/doubles réparé")
    bs = chr(92)  # un antislash, sans ambiguïté d'échappement
    # Reproduit EXACTEMENT le cas réel : flmsg_exe en antislashs SIMPLES
    # (dont un segment « \flmsg » piégeux), messages_dir en DOUBLES.
    txt_ko = (
        '{' + chr(10)
        + '  "flmsg_exe": "C:' + bs + 'Program Files (x86)' + bs
        + 'flmsg-4.0.24' + bs + 'flmsg.exe",' + chr(10)
        + '  "messages_dir": "C:' + bs + bs + 'Users' + bs + bs
        + 'F1GBD' + bs + bs + 'NBEMS.files",' + chr(10)
        + '  "auto_open": true' + chr(10) + '}'
    )
    # parsing strict doit échouer (antislashs simples non échappés)
    strict_ok = True
    try:
        json.loads(txt_ko)
    except json.JSONDecodeError:
        strict_ok = False
    assert not strict_ok, "le cas de test devrait être strictement invalide"
    data, note = _charger_json_tolerant(txt_ko)
    assert data is not None, "réparation échouée"
    assert note == "REPAIRED", note
    # CRUCIAL : le « \flmsg » ne doit PAS être interprété comme saut de page
    attendu_exe = ("C:" + bs + "Program Files (x86)" + bs + "flmsg-4.0.24"
                   + bs + "flmsg.exe")
    assert data["flmsg_exe"] == attendu_exe, repr(data["flmsg_exe"])
    assert chr(12) not in data["flmsg_exe"], "saut de page (\\f) injecté !"
    # messages_dir en doubles doit rester correct (pas de séparateurs en trop)
    attendu_dir = "C:" + bs + "Users" + bs + "F1GBD" + bs + "NBEMS.files"
    assert data["messages_dir"] == attendu_dir, repr(data["messages_dir"])
    assert data["auto_open"] is True
    # JSON déjà valide → aucune réparation
    data2, note2 = _charger_json_tolerant('{"flmsg_exe":"/usr/bin/flmsg"}')
    assert note2 == "" and data2["flmsg_exe"] == "/usr/bin/flmsg"
    print("    OK (simples doublés, doubles préservés, \\flmsg intact)")

    print(f"\n=== {'TOUS LES TESTS PASSENT' if not erreurs else f'{erreurs} ÉCHEC(S)'} ===")
    return 0 if not erreurs else 1


if __name__ == "__main__":
    import sys
    sys.exit(_autotest())
