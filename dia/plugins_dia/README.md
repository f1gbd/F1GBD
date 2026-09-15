# Plugins d'entrées-sorties pour d-IA v1.11+

**Auteur** : Jean-Louis (F1GBD) — ADRASEC 77 / FNRASEC
**d-IA requis** : v1.10.0 (entrées-sorties) — v1.11.0 pour les actions, mesures et attentes
**Parenté** : même philosophie que les plugins IAbrain v1.40.7+ (voir la fiche
« Programmation de plugins Python et utilisation des macros dans IAbrain »)

---

## Ce que fait un plugin d-IA

Un plugin injecte des **variables de situation** dans la simulation et observe
ce qui s'y dit :

| Sens | Hook | Quand | À quoi ça sert |
|---|---|---|---|
| **Entrée** | `collect(ctx)` | avant chaque prise de parole | Le COD, l'opérateur et l'injecteur d'événements voient des données **réelles** : Kp du jour, état de la fenêtre NVIS, autonomie d'une power station, dernier message reçu par TCQ. |
| **Sortie** | `on_message(msg, ctx)` | après chaque prise de parole | Noter un SITREP, alimenter un CSV de RETEX, déclencher une action, alimenter une variable qui sera réinjectée au tour suivant. |

Les variables sont injectées dans le prompt des trois LLM sous la forme :

```
DONNEES DE SITUATION (releves reels transmis au poste, a prendre en compte dans ta reponse) :
KP_LOCAL = 4.5
NVIS_ETAT = degradee (absorption, liaisons HF aleatoires)
AUTONOMIE_PCO = 3 h
DEFAUT_RELEVE = message non horodate
```

**Aucune variable, aucun bloc** : le prompt redevient exactement celui de la
v1.9. C'est la même mécanique que le bloc `{sources_web}` de la recherche web.

---

## Installation

1. Déposer le fichier `.py` dans le dossier **`plugins_dia/`**, situé à côté de
   `d-IA.exe` (ou de `d-IA.py` en mode source). d-IA crée ce dossier au premier
   démarrage.
2. Relancer d-IA, ou **Plugins E/S ▼ → Recharger les plugins**.
3. Cocher **Plugins E/S ▼ → Activer les plugins et variables de situation**.
4. Vérifier avec **Plugins E/S ▼ → Diagnostic plugins…**

Pour désactiver un plugin sans le supprimer : le renommer en
`mon_plugin.py.disabled` (même convention qu'IAbrain).

---

## Contrat d'interface

Tout est optionnel, sauf qu'il faut au moins `collect` **ou** `on_message` —
sinon le fichier est signalé « ignoré » dans le rapport de chargement.

```python
PLUGIN_NAME    = "Nom lisible"      # str, défaut : nom du fichier
PLUGIN_VERSION = "1.0"              # str
PLUGIN_ENABLED = True               # mettre False pour neutraliser

def list_variables() -> list[tuple[str, str]]:
    """(nom, description) — documentaire, affiché dans le diagnostic."""

def collect(ctx) -> dict:
    """ENTRÉE. Retourne {NOM: valeur}."""

def on_message(msg, ctx) -> dict | None:
    """SORTIE. Retour optionnel fusionné dans les variables du tour suivant."""
```

### Le dictionnaire `ctx`

| Clé | Contenu |
|---|---|
| `tour` | numéro de la prise de parole en cours |
| `theme` | séquence active du scénario |
| `speaker` | `LLM1`, `LLM2` ou `LLM3` |
| `role` | libellé du rôle (ex. `COD Vaubourg`) |
| `sujet` | le scénario complet du preset |
| `mode_jdr` | `True` en simulation jouée |
| `labels` | `{label1, label2, label3}` du preset |
| `vars` / `session_vars` | photographie des variables courantes (les deux clés sont identiques ; `session_vars` est l'alias de compatibilité avec le contrat IAbrain) |
| `historique_court` | les 3 derniers messages, tronqués à 400 caractères |

### Le dictionnaire `msg`

`tour`, `speaker`, `role`, `texte`, `theme`, `ts` (horodate ISO), `humain`
(`True` quand c'est le stagiaire qui a tapé le message en mode CHAT).

### Valeurs de retour

Un `dict` simple, ou le couple `(dict, ["avertissement", …])` — même style que
`execute_action()` chez IAbrain. Les avertissements s'affichent dans le fil de
la conversation et dans le diagnostic, sans interrompre le tour.

Les valeurs sont **assainies** avant injection : converties en texte, une seule
ligne, sans markdown, tronquées à 160 caractères, 12 variables au maximum,
bloc plafonné à 800 caractères. Les noms sont normalisés en MAJUSCULES avec
des underscores (`consigne du jour` → `CONSIGNE_DU_JOUR`).

---

## Actions, mesures et attentes (v1.11)

Un plugin peut aussi exposer des **actions** que les LLM demandent eux-mêmes.

```python
def list_actions():
    # (action_id, libelle, description) - meme contrat que les plugins IAbrain
    return [("chauffage_on", "Allumer le chauffage", "Fait monter la temperature"),
            ("mesure_meteo", "Relever la meteo", "Lit le dernier releve")]

def execute_action(action_id, params, ctx):
    # Retourne {NOM: valeur}, ou (dict, ["avertissement"])
    ...
```

Le catalogue est injecté dans le prompt, et le modèle écrit une directive **seule sur sa ligne, en majuscules** :

```
ACTION: chauffage_on(zone=serre1)
MESURE: mesure_meteo()
ATTENDRE: TEMPERATURE_C >= 30 delai=600
```

| Directive | Effet |
|---|---|
| `ACTION:` / `MESURE:` | Appelle `execute_action()`. Le retour devient une variable, relue par les trois LLM au tour suivant. Budget : 10 s. |
| `ATTENDRE:` | Suspend le dialogue et scrute la condition (`collect()` toutes les 5 s) jusqu'à satisfaction ou expiration. Opérateurs : `>` `>=` `<` `<=` `=` `!=` `contient`. Issue dans `ATTENTE_RESULTAT`. |

Trois directives au maximum par message. Le délai d'attente est plafonné par `plugins_attente_max_s` (15 min par défaut), et l'attente reste interruptible par Pause et Arrêter.

**Trois modes d'exécution** — menu *Plugins E/S → Actions demandées par les LLM* :

| Mode | Comportement | Usage |
|---|---|---|
| `auto` (défaut) | Exécution directe | Banc de mesure, domotique, acquisition |
| `confirmer` | L'opérateur valide chaque action ; sans réponse en 120 s, c'est refusé | Matériel sensible |
| `off` | Directive journalisée, rien n'est exécuté, catalogue non proposé | **Exercice fictif** |

> Un preset d'exercice doit déclarer `"plugins_actions_mode": "off"`. Un COD fictif ne doit jamais allumer un vrai groupe électrogène.

**La règle d'or ne change pas** : `execute_action()` ne va pas sur le réseau et n'attend pas un équipement lent. Pour une acquisition distante, l'action *lance* un collecteur en arrière-plan (`subprocess.Popen`) et le LLM attend ensuite le résultat :

```
ACTION: releve_meteo_maintenant()
ATTENDRE: RELEVE_AGE_MIN < 2 delai=300
```

C'est exactement ce que fait le couple `meteo_3x30.py` / `meteo_3x30_collecte.py`.

---

## Variables de session (sans écrire de code)

**Plugins E/S ▼ → Variables de session…** ouvre un éditeur : une variable par
ligne, au format `NOM = valeur`. C'est l'équivalent d-IA de la commande `/set`
d'IAbrain.

Ces variables sont injectées exactement comme celles des plugins et **priment
sur elles** : en exercice, la valeur annoncée par le formateur fait foi. Elles
sont persistées dans `d-ia_setup.json` et prises en compte immédiatement, même
au milieu d'une séance — c'est le moyen le plus simple d'injecter une contrainte
à chaud (« SOC_PCO = 12 % ») sans toucher au scénario.

---

## Règles de sûreté (à lire avant d'écrire un plugin)

1. **Rendez la main vite.** Chaque appel est borné par un **timeout de 2 s** :
   au-delà, le résultat est ignoré, et au deuxième dépassement le plugin est
   désactivé pour la séance. Un plugin de dialogue n'est pas une macro : il est
   appelé à *chaque* tour. Lisez un fichier déjà écrit par un autre programme
   plutôt que d'interroger un service lent.
2. **N'inventez jamais une valeur.** Pas de relevé, pas de variable : mieux vaut
   un bloc vide qu'une donnée fictive présentée comme mesurée. Regardez
   `propagation_vars.py` : fichier absent → `{}`, JSON malformé → `{}`.
3. **Hors ligne d'abord.** Un exercice de black-out se joue sans réseau. Une
   exception est isolée et journalisée, mais elle reste une anomalie visible
   dans le fil.
4. **Valeurs courtes, sans accent, sans markdown.** Les modèles imitent ce
   qu'ils lisent : une valeur bavarde dégrade la discipline radio.
5. **Revue de code.** Un plugin s'exécute avec les droits de d-IA. Mêmes règles
   que pour IAbrain : sources fiables, lecture du `.py` avant installation,
   bibliothèque standard suffisante.

---

## Plugins livrés

| Fichier | Sens | Rôle |
|---|---|---|
| `exemple_minimal.py` | entrée + sortie | Squelette à copier (heure d'exercice, compteur de messages). |
| `propagation_vars.py` | entrée | Lit `propagation_releves.json` (Kp, SFI, SOC, autonomie) et en déduit l'état de la fenêtre NVIS. Peut être alimenté par GEOMAG-Observer. |
| `sitrep_scoring.py` | sortie | Note la forme de chaque message de l'opérateur sur 20 (indicatif, horodate, accusé, chiffres, brièveté, mention EXERCICE), écrit un CSV de RETEX et réinjecte le défaut constaté pour que le COD le réclame par radio. |
| `meteo_3x30.py` | entrée + actions | Température, vent, rafales, humidité du modèle **AROME France HD** et état de la **règle des 3 × 30** (T ≥ 30 °C, vent ≥ 30 km/h, HR ≤ 30 %). Réutilise `meteo_lib.py` de TCQ quand elle est accessible. **Acquisition automatique** : rien à lancer à la main, même à la première installation. Actions : `mesure_meteo`, `releve_meteo_maintenant`. |
| `meteo_3x30_collecte.py` | (hors d-IA) | Collecteur : interroge Open-Meteo en AROME France HD et écrit `meteo_releves.json`. **Le plugin l'appelle tout seul** ; le lancer à la main n'est utile que pour une tâche planifiée ou un dépannage. Options `--site CLE`, `--lat --lon --lieu`, `--simuler T,VENT,HUM`, `--boucle SECONDES`. |
| `chronogramme.py` | entrée + sortie | **Le DIRANIM.** Déroule un chronogramme d'exercice cadre écrit en CSV : horloge de jeu, inject adressé à un destinataire, pointage des réactions attendues, relance automatique, main courante de RETEX. Voir le chapitre ci-dessous. |
| `chronogramme_helios_noir_26.csv` | (données) | Le chronogramme de la séquence 7 d'HÉLIOS NOIR 26, au format de la doctrine. Neuf lignes datées et cinq incidents de réserve. |

---

## L'acquisition météo se fait toute seule (v2.3)

Un plugin dont la source de données est absente doit aller la chercher, pas
rédiger une consigne. Jusqu'en v2.2, une première installation affichait :

    [Plugin Meteo 3x30 - avertissement : releve absent ou illisible :
     C:\d-IA\plugins_dia\meteo_releves.json - lancer : python meteo_3x30_collecte.py]

C'était demander à l'opérateur de réparer une chose que le plugin sait faire —
et précisément au moment où il ne peut pas la deviner, avant même le premier
tour. Depuis la v2.3, le plugin lance lui-même l'acquisition et annonce :

    [Plugin Meteo 3x30 - avertissement : aucun releve pour le moment -
     acquisition relancee automatiquement sur Nangeville. Les valeurs
     arriveront dans quelques secondes.]

Trois garde-fous, inchangés depuis la v2.1 :

- **La règle des 2 secondes tient.** `collect()` ne va jamais sur le réseau :
  il *démarre* l'acquisition en tâche de fond et rend la main immédiatement.
- **Pas de martèlement.** Une relance automatique par site et par tranche de
  10 minutes au plus (`RELANCE_AUTO_MIN`), et jamais deux acquisitions
  simultanées sur le même site.
- **Hors ligne, on le dit.** Si l'acquisition est impossible — réseau coupé,
  aucun interpréteur Python pour le repli en sous-processus — le plugin ne
  boucle pas et n'invente aucune valeur : il l'annonce, et *là seulement*
  redonne la commande manuelle, en dernier recours.

Le site retenu est celui de la variable de session `LIEU_METEO` si elle existe,
sinon `SITE_DEFAUT` (`nangeville`, mesuré réellement à Nangis 77).

---

## Le chronogramme : d-IA en DIRANIM (plugin `chronogramme.py`)

Le guide méthodologique de la Direction de la Sécurité Civile sur les exercices
Cadre et Terrain (2011) décrit comment se monte un exercice : on part de la
**réaction attendue**, on choisit le joueur qui doit la produire, puis
l'animateur émetteur, puis seulement on rédige l'événement, et enfin on décide
du vecteur et du groupe horaire. Le tableau qui en résulte — le
**chronogramme** — se lit de la droite vers la gauche.

Jusqu'à ce plugin, LLM3 tirait un événement au sort dans un répertoire, tous
les K tours, sans lien avec un objectif. C'était de l'animation, pas du
déroulé. Le plugin `chronogramme.py` lit le tableau et le joue.

### Le fichier

Un CSV UTF-8, séparateur point-virgule, à côté du plugin. Par défaut
`chronogramme.csv` ; la variable de session `CHRONOGRAMME = helios noir 26`
fait lire `chronogramme_helios_noir_26.csv`.

**Quel chronogramme est joué ?** Dans cet ordre :

1. celui que désigne la variable de session `CHRONOGRAMME` ;
2. `chronogramme.csv` s'il existe ;
3. l'**unique** `chronogramme_*.csv` déposé à côté du plugin.

Le troisième cas est celui du formateur qui a déposé son fichier sans penser à
la variable de session. Déposer le fichier **est** un acte explicite : exiger en
plus une variable invisible transformait une préparation correcte en séance sans
chronogramme. Le plugin le charge donc — et il le **dit** dans le fil, car un
plugin qui prend la main ne doit jamais le faire en silence :

```
[Plugin Chronogramme : chronogramme_helios_noir_26.csv charge -
 HELIOS NOIR 26 - sequence 7 (seul chronogramme present dans le dossier),
 9 ligne(s) datee(s).]
```

Avec **plusieurs** fichiers, il ne choisit pas à votre place : il les nomme et
rappelle comment en désigner un. Sans **aucun** fichier, il ne publie rien et ne
le dit qu'une fois — il peut donc rester installé à demeure dans `plugins_dia\`
sans perturber les séances qui se jouent sans chronogramme, et les presets
HÉLIOS NOIR fonctionnent dans les deux cas : « quand `INJECT` est absent, tu
n'as rien reçu de nouveau ».

```
#EXERCICE=HELIOS NOIR 26 - sequence 7
#DEBEX=2026-07-11 14:00
#MINUTES_PAR_TOUR=5
groupe_horaire;vecteur;emetteur;recepteur;evenement;reaction_attendue;detection;relance
H+5;VARA FM;ANIBAS jouant l'EHPAD;LLM2;EXERCICE. Climatisation a l'arret depuis
11h, deux residents en hyperthermie.;SITREP formate et demande chiffree de
carburant;carburant|litres|evacuation;EXERCICE. La directrice rappelle, un
troisieme resident est en hyperthermie.
```

| Colonne | Rôle |
|---|---|
| `groupe_horaire` | `H-15`, `H`, `H+5`, `H+120` — ou `RESERVE` pour un incident hors chronologie |
| `vecteur` | VARA FM, HF NVIS, téléphone, radio phonie… |
| `emetteur` | ANIBAS jouant l'EHPAD, ANIHAUT jouant le COZ, DIRANIM |
| `recepteur` | `LLM1`, `LLM2`, `TOUS`, ou un libellé de rôle du preset |
| `evenement` | le message, rédigé mot à mot, tel qu'il sera lu |
| `reaction_attendue` | **jamais publiée** — main courante et pointage seulement |
| `detection` | motifs séparés par `\|`, cherchés dans les messages des joueurs |
| `relance` | l'inject de rattrapage, quand la réaction n'est pas venue |

Le texte de l'événement accepte des accolades : `{TEMPERATURE_C}`,
`{VENT_KMH}`, `{HUMIDITE_PCT}` sont remplacés par les valeurs publiées par les
autres plugins. La mise en ambiance type du guide — « il fait 25 degrés à
l'ombre, le vent souffle à 5 km/h » — se remplit donc toute seule avec les
relevés AROME de `meteo_3x30`.

### Ce que le plugin publie

| Variable | Contenu |
|---|---|
| `HEURE_JEU` | `11/07 14h20 (H+20)` — les joueurs cessent d'inventer leurs horodates |
| `PHASE_EXERCICE` | avant DEBEX, en cours, FINEX |
| `INJECT` | le message reçu **par le joueur qui parle** |
| `INJECT_SUITE` | sa fin, quand il dépasse une variable |
| `INJECT_DE` | qui émet : ANIBAS, ANIHAUT, DIRANIM, et le rôle joué |
| `INJECT_VECTEUR` | par quel moyen — et la mention `(relance par un autre vecteur)` le cas échéant |
| `CHRONO_AVANCEMENT` | position dans le chronogramme |

**Un inject, un destinataire.** Une ligne n'est publiée qu'au tour du joueur
désigné en colonne `recepteur`. L'autre partie ne l'a pas reçue : elle
l'apprendra si — et seulement si — l'information circule. C'est précisément ce
que le guide cherche à tester dans un centre opérationnel.

**La réaction attendue ne sort jamais.** Elle est lue, journalisée, pointée —
jamais publiée. C'est la règle « pas de divulgation » du § 3.1.1.

**Pas de constat d'échec.** Sans réaction détectée au bout de
`RELANCE_APRES_TOURS` (4 par défaut), le plugin envoie le texte de la colonne
`relance`, par un autre vecteur, pendant qu'il est encore temps de réagir.

### Le pupitre du DIRANIM

Par **Plugins E/S ▼ → Variables de session…**, en cours de séance :

| Variable | Effet |
|---|---|
| `DIRANIM_PAUSE = oui` | fige l'horloge de jeu |
| `DIRANIM_AVANCE = 1` | pousse l'inject suivant — **changez la valeur** (1, puis 2, puis 3) à chaque fois |
| `DIRANIM_RESERVE = 2` | injecte l'incident de réserve n° 2 |
| `DIRANIM_FINEX = oui` | prononce le FINEX |
| `MINUTES_PAR_TOUR = 10` | change la cadence |
| `CHRONOGRAMME = seq7` | change de chronogramme |

Aucune de ces commandes n'est une **action** au sens de d-IA : le pupitre reste
donc entièrement disponible quand le preset d'exercice impose, comme il le
doit, `"plugins_actions_mode": "off"`. Un COD fictif ne pilote pas le
chronogramme de son propre exercice — c'est pourquoi la seule action déclarée
par le plugin, `chronogramme_etat`, est en **lecture seule**.

### Câbler le chronogramme dans un preset

À ajouter à `persona1` **et** à `persona2` :

```
- Les DONNEES DE SITUATION portent HEURE_JEU, l'heure de l'exercice : tu
  horodates tes messages avec elle, jamais avec l'heure reelle.
- Quand INJECT est present, c'est un message que TU viens de recevoir, de la
  part de INJECT_DE, par INJECT_VECTEUR. Tu le traites comme du trafic
  entrant : tu en accuses reception et tu agis. INJECT_SUITE en est la fin.
- Quand INJECT est absent, tu n'as rien recu de nouveau : tu poursuis le
  trafic en cours, tu n'inventes pas d'evenement.
- Tu ne cites JAMAIS un nom de variable dans ton message : tu joues ce
  qu'elles disent.
- Quand PHASE_EXERCICE vaut FINEX, tu cesses le trafic et tu passes au bilan.
```

Et LLM3 : soit on le coupe (`"mod_conv_actif": false`) parce que le
chronogramme fait désormais l'animation, soit on lui laisse le rôle d'une
ANIBAS d'appoint, bornée aux **conséquences** des injects du chronogramme et
non à de nouveaux événements.

### La main courante de RETEX

Une ligne de CSV par événement dans `..\logs\retex_chronogramme_AAAAMMJJ.csv` :
horodate réelle, heure de jeu, tour, nature (inject, relance, réserve,
réaction), le groupe horaire, le vecteur, l'émetteur, le récepteur,
l'événement, **la réaction attendue**, son pointage, et l'extrait du message du
joueur qui l'a produite. Au FINEX, le plugin affiche le bilan dans le fil :
tant d'injects, tant de réactions obtenues sur tant de pointables, tant de
relances.

C'est le document du débriefing à froid, et c'est ce qui rend l'exercice
**évaluable** — ce qu'aucune séance ne permettait avant ce plugin.

---

## Différence avec un plugin IAbrain

|  | IAbrain | d-IA |
|---|---|---|
| Déclencheur | l'opérateur (macro, clic) | la boucle de dialogue, à chaque tour |
| Contrat | `is_action` / `list_actions` / `execute_action` | `list_variables` / `collect` / `on_message`, plus `list_actions` / `execute_action` depuis la v1.11 |
| Retour | Markdown affiché dans le chat | variables injectées dans le prompt |
| Contrainte de temps | aucune | **timeout de 2 s** |
| Dossier | `plugins/` | `plugins_dia/` |
| Désactivation | renommer en `.disabled` | renommer en `.disabled` |

---

*ADRASEC 77 — F1GBD — usage pédagogique interne.*
