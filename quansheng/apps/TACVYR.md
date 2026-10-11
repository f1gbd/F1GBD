# TACVYR v1.0 — messages tactiques courts en AX.25 Packet pour Quansheng UV-K1 / UV-K5 v3

Application overlay (`.app`) pour le firmware F4HWN édition Labs. Elle permet
d'**échanger des messages tactiques courts sans parler** : là où la phonie est
impossible ou indésirable (salle de COD, approche discrète, zone très bruyante),
l'opérateur compose le message au clavier avec un **code à 2 chiffres** et l'émet
par **PTT** en **AX.25 Packet 1200 bauds**. Entre deux saisies, la radio écoute en
permanence et affiche les messages reçus.

<p align="center">
  <img src="../images/TACVYR_rubrique.png" alt="TACVYR : la rubrique POSITION après la touche 2" width="300">
  &nbsp;
  <img src="../images/TACVYR_message.png" alt="TACVYR : message prêt à partir" width="300">
</p>
<p align="center"><em>Touche 2 : la rubrique POSITION ; 1 2 puis 2 1 : « EQUIPE BRAVO SUR ZONE » prêt à partir (maquettes d'écran)</em></p>

| | |
|---|---|
| Messages | 81 phrases en 9 rubriques, code à 2 chiffres ; 1 ou 2 phrases par message, ou texte libre (48 caractères) |
| Format sur l'air | une trame UI AX.25 `<indicatif>-<SSID>` → `CQ`, PID F0, **texte en clair** : TCQ, PAGER-RASEC et tout TNC l'affichent tel quel |
| Fréquence | celle du **VFO** (réception et émission) |
| Réception | démodulateur d'APRS RX (comme PAGER-RASEC), 6 derniers messages gardés (envoyés compris), double bip et voyant vert |
| Émission | 0,5 à 1,1 s selon le message et le TXDELAY (300, 500 ou 800 ms) |
| Taille | 3 940 o de code (overlay 4 Kio) + 3 797 o de ressources (dont 2 modules) |

Manuel complet : [PDF](../documentation/TACVYR_Manuel_v1.0.pdf) — carte opérateur A4 avec les
81 codes, à imprimer et plastifier : [PDF](../documentation/TACVYR_Carte_Operateur.pdf).

<p align="center">
  <img src="../images/TACVYR-TCQ.jpg" alt="Message TACVYR reçu en clair par TCQ" width="760">
</p>
<p align="center"><em>Essai sur l'air du 11 octobre 2026 : « EQUIPE ALPHA SUR ZONE » (codes 11 et 21) émis par le UV-K1 F1GBD-7, reçu en clair par TCQ v14.2.1</em></p>

## Installation

1. Ouvrir l'**[UV-K1 Apps Uploader](../index.html)** dans Chrome ou Edge.
2. Brancher la radio (USB-C), **Connecter la radio**, choisir le port série.
3. Sélectionner **Messages tactiques TACVYR**, garder l'emplacement proposé, **Installer**.
4. Régler le **VFO** sur la fréquence tactique (FM), puis menu **Apps** → **TACVYR**.

## Envoyer un message

1. **1re touche (1 à 9)** : la rubrique s'affiche avec ses 9 phrases.
2. **2e touche (1 à 9)** : la phrase est ajoutée au message.
3. Éventuellement une **2e phrase** de la même façon (2 phrases au plus).
4. **PTT** : le message part. Il rejoint la liste des messages, marqué « envoye ».

Exemples :

| Touches | Message émis | Durée (TXDELAY 500 ms) |
|---|---|---|
| `1 2  2 1  PTT` | EQUIPE BRAVO SUR ZONE | 0,81 s |
| `7 1  PTT` | RECU | 0,69 s |
| `3 5  2 2  PTT` | DEMANDE POUR ACTION AU POINT ROMEO UN | 0,91 s |
| `1 7  6 4  PTT` | COD BESOIN RENFORT | 0,79 s |
| `5 1  2 3  PTT` | BALISE TROUVEE AU POINT ROMEO DEUX | 0,89 s |

**Texte libre** : **MENU** ouvre l'éditeur sur le message en cours (vide, ou avec les
phrases déjà choisies, pour le compléter : « AU POINT ROMEO UN » + « N4 »). Saisie
multi-tap comme sur un téléphone : 2 = ABC, 3 = DEF… 9 = WXYZ, 1 = ponctuation,
0 = espace ; pour deux lettres de la même touche, attendre une seconde ; **F puis
une touche** donne le chiffre ; **\*** efface ; **MENU** valide, **EXIT** annule.

## Les messages pré-définis

Le code est **rubrique puis phrase** : 12 = EQUIPE BRAVO, 21 = SUR ZONE, 71 = RECU.

| | **1x** EQUIPES | **2x** POSITION | **3x** ACTION | **4x** ETAT | **5x** RECHERCHE |
|---|---|---|---|---|---|
| **x1** | EQUIPE ALPHA | SUR ZONE | DEPLOIEMENT | EN ATTENTE | BALISE TROUVEE |
| **x2** | EQUIPE BRAVO | AU POINT ROMEO UN | EXTRACTION | PRET | SIGNAL FORT |
| **x3** | EQUIPE CHARLIE | AU POINT ROMEO DEUX | EVAC | OCCUPE | SIGNAL FAIBLE |
| **x4** | EQUIPE DELTA | AU POINT ROMEO TROIS | RECHERCHE EN COURS | RAS | PAS DE SIGNAL |
| **x5** | EQUIPE ECHO | EN ROUTE | DEMANDE POUR ACTION | TERMINE | RELEVEMENT EN COURS |
| **x6** | PC | ARRIVE | RELEVE | EN PAUSE | EPAVE TROUVEE |
| **x7** | COD | AU PC | REPLI | BATTERIE FAIBLE | VICTIME TROUVEE |
| **x8** | TOUTES EQUIPES | RETOUR BASE | STOP | PROBLEME RADIO | ZONE FOUILLEE |
| **x9** | ICI | POSITION ? | FIN DE MISSION | HORS ZONE | BALISE ETEINTE |

| | **6x** SECOURS | **7x** TRANSMISSION | **8x** DELAI | **9x** MOYENS |
|---|---|---|---|---|
| **x1** | BLESSE | RECU | IMMEDIAT | VEHICULE |
| **x2** | BLESSE GRAVE | REPETEZ | DANS 5 MIN | GROUPE ELECTROGENE |
| **x3** | BESOIN MEDICAL | COMPRIS | DANS 15 MIN | RELAIS RADIO |
| **x4** | BESOIN RENFORT | NEGATIF | DANS 30 MIN | ANTENNE |
| **x5** | BESOIN EAU | AFFIRMATIF | DANS 1 H | BATTERIES |
| **x6** | BESOIN CARBURANT | ATTENDEZ | MAINTENANT | VIVRES |
| **x7** | BESOIN TRANSPORT | CHANGEZ FREQUENCE | PLUS TARD | ECLAIRAGE |
| **x8** | URGENCE | RAPPELEZ | ANNULE | PHOTO |
| **x9** | DANGER | PAS COMPRIS | A CONFIRMER | POINT DE SITUATION |

La liste se modifie dans `gen_assets.py` (24 caractères au plus par phrase) avant
de reconstruire l'application.

## Recevoir

TACVYR écoute le VFO tant qu'il est ouvert, y compris pendant la saisie. Un message
reçu fait un double bip (sauf si coupé, F 4) et allume le voyant vert jusqu'à la
touche suivante. En cours de saisie, la ligne du bas indique « Recu de F1GBD-3 » :
**< / >** affichent les messages sans perdre le message en cours, **EXIT** y revient.

## Touches

| Touche | Écran principal |
|---|---|
| 1 à 9 | Rubrique (puis 1 à 9 : la phrase) |
| MENU | Texte libre / modifier le message |
| PTT | Émettre le message |
| \* | Effacer le message en cours |
| < / > | Messages reçus et envoyés (le plus récent en premier) |
| EXIT | Revenir au message / l'effacer / quitter |
| F puis MENU | **Indicatif** (6 caractères ; vide = celui du message de démarrage) |
| F puis 1 / 7 | Niveau BF + / − |
| F puis 2 / 8 | Twist + / − |
| F puis 3 / 9 | SSID + / − (7 par défaut) |
| F puis 4 | Bip de réception marche / arrêt |
| F puis 5 | Haut-parleur (écoute du canal) marche / arrêt |
| F puis 6 | TXDELAY 300 → 500 → 800 ms (800 ms pour passer par un relais) |
| F puis 0 | Effacer les messages |
| F puis EXIT | Quitter |

Indicatif, SSID, niveau, twist, TXDELAY, bip et haut-parleur sont mémorisés en
quittant par EXIT. La ligne du bas rappelle la fréquence, l'indicatif utilisé et le
TXDELAY : `430.50000 F1GBD-7 TXD5`.

## Compatibilité

- **TCQ** (onglet TNC Packet) et **PAGER-RASEC** affichent les messages TACVYR en clair.
- TACVYR affiche tout message Packet reçu : TCQ, CHAPPE-TX, un autre TACVYR
  (les 56 premiers caractères).

## Validation

- Émetteur AFSK identique à APRS TX de F4HWN, CHAPPE-TX et RGRAM ; démodulateur
  identique à APRS RX et PAGER-RASEC (essais sur l'air réussis).
- Banc logiciel : exécution instruction par instruction de l'application réelle,
  audio Packet en entrée, touches simulées : messages reçus et affichés, saisie
  par codes (1 et 2 phrases, refus d'une 3e), texte libre multi-tap, éditeur
  d'indicatif, SSID, TXDELAY 300 / 500 / 800 ms ; chaque émission reconstituée et
  décodée (FCS correcte, `F4JHW-8>CQ`, texte exact) ; réglages mémorisés et
  relus. Pile au pire 3 400 o.
- **Essai sur l'air réussi** (11 octobre 2026) : « EQUIPE ALPHA SUR ZONE » émis par le
  UV-K1 F1GBD-7 et reçu en clair par TCQ v14.2.1 (Direwolf, onglet TNC Packet).

ADRASEC 77 · F1GBD — 73
