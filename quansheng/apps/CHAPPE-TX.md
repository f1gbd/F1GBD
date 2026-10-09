# CHAPPE-TX v1.1 — émetteur de messages CHAPPE26 pour Quansheng UV-K1 / UV-K5 v3

Application overlay (`.app`) pour le firmware F4HWN édition Labs. Elle permet de
**composer un message CHAPPE26 au clavier du portatif** et de l'**émettre en
AX.25 Packet 1200 bauds**, exactement comme le chat TNC Packet de **TCQ** :
une trame UI de `F1GBD-7` vers `CQ`, texte `!1000 !1024 !1380 !1990`.

**Nouveau en v1.1 : l'indicatif se saisit directement sur la radio** (F puis 0),
sans PC ni logiciel de programmation.

Le message est donc reçu et **affiché en clair** par :
- toute station **TCQ** (onglet TNC Packet, décodage CHAPPE26 automatique) ;
- tout autre UV-K1 / UV-K5 v3 sous **[PAGER-RASEC](PAGER-RASEC.md)** (v1.1 et suivantes) ;
- n'importe quel TNC / logiciel Packet (Direwolf, UZ7HO…), en codes bruts.

Manuel complet avec exemples de transmission : [PDF](../documentation/CHAPPE-TX_Manuel_v1.1.pdf)

| | |
|---|---|
| Modulation | AFSK Bell 202 1200 bauds, trame UI AX.25 (contrôle 03, PID F0), FCS CRC-16/X.25 |
| Adresses | source = indicatif saisi sur la radio (F 0), à défaut celui du message de démarrage, + SSID (7 par défaut) ; destination `CQ`, pas de digipeater |
| Fréquence | celle du **VFO d'émission** (ex. 145.4375 MHz FM, fréquence RASEC-ALERT de PAGER-RASEC) |
| Message | 1 à **15 codes** `!PPLL` (89 caractères, une seule trame : TCQ coupe au-delà de 92) |
| Aide à la saisie | domaine de la page et phrase en clair de chaque code, relecture du message complet (dictionnaire **CHAPPE26** requis) |
| Taille | 3852 o de code (overlay 4 Kio) + 1,3 ko de ressources |

## Installation

1. Ouvrir l'**[UV-K1 Apps Uploader](../index.html)** dans Chrome ou Edge.
2. Brancher la radio (USB-C), **Connecter la radio**, choisir le port série.
3. Sélectionner **Émetteur CHAPPE-TX**, garder l'emplacement proposé, **Installer**.
4. Si ce n'est pas déjà fait, installer aussi le **Dictionnaire CHAPPE26** : sans
   lui l'émission fonctionne, mais la radio n'affiche pas les phrases en clair.
5. Régler le **VFO** sur la fréquence de travail, puis menu **Apps** → **CHAPPE-TX**.
6. Saisir l'**indicatif** (ci-dessous) : au premier lancement, l'éditeur s'ouvre tout seul.

## Saisir l'indicatif sur la radio

**F puis 0** ouvre l'éditeur « Indicatif » : l'indicatif actuel, les cases libres en `_`,
le SSID à droite, un `^` sous le caractère en cours.

| Touche | Action |
|---|---|
| < / > | Lettre ou chiffre suivant / précédent sous le curseur : A … Z puis 0 … 9 (maintenu : rapide) |
| 0 à 9 | Taper un chiffre (le curseur avance seul) |
| * | Caractère suivant |
| F puis * | Effacer le caractère |
| MENU | Valider (mémorisé) |
| EXIT | Annuler |

Exemple, `F1GBD` depuis un éditeur vide : `>`×6 (F) `*` · `1` · `>`×7 (G) `*` · `>`×2 (B) `*` · `>`×4 (D) · `MENU`.

- 6 caractères au plus, lettres et chiffres. **Pas de SSID dans l'indicatif** : il se
  règle avec F 3 / F 9 (7 par défaut).
- Indicatif vide (tout effacer puis MENU) : CHAPPE-TX reprend l'indicatif de la ligne 1
  du message de démarrage de la radio (programmé avec CHIRP), comme APRS TX ; sans
  aucun indicatif, l'écran affiche « Pas d'indicatif: F puis 0 » et rien n'est émis.

## Composer et envoyer un message

Un code CHAPPE26 s'écrit sur 4 chiffres : **page** 10 à 19, **ligne** 00 à 99
(`1204` = page 12 Santé générale, ligne 04 = « Ambulance requise »).

1. **Taper les 4 chiffres** du code. Dès le 2e chiffre la radio affiche le
   **domaine** de la page, au 4e la **phrase** en clair.
   Ou **parcourir le répertoire** : `<` / `>` code précédent / suivant
   (maintenu : défilement rapide), **F** puis `<` / `>` page précédente / suivante.
2. **MENU** ajoute le code au message (affiché sous la ligne pointillée, 5 codes par ligne).
3. Recommencer pour les codes suivants. `*` retire le dernier code.
4. **F puis MENU** : **relecture** du message en clair, un code par ligne
   (`<` / `>` pour défiler, PTT pour émettre, une autre touche pour revenir).
5. **PTT** : émission (≈ 0,6 à 1 s). « TRANSMIT » s'affiche dans la barre d'état,
   le compteur `env` augmente. Le message reste en mémoire : PTT à nouveau pour le répéter.
6. **F puis `*`** vide le message.

Exemple « Début de transmission. Transmission urgente. Communication
interrompue. Fin transmission. » : `1000 MENU 1024 MENU 1380 MENU 1990 MENU PTT`.

## Écran et touches

```
 CHAPPE-TX                  [batterie]
 Code 1380                        4/15   <- code en cours / codes dans le message
 Communication interrompue               <- phrase en clair (dictionnaire)
 Securite civile                         <- domaine de la page
 - - - - - - - - - - - - - - - - - - - -
 !1000 !1024 !1380 !1990                 <- le message (3 lignes de 5 codes)

 F1GBD-7>CQ                              <- adresses (ou état : TX refusee...)
 145.43750 L66 T0 env 1                  <- VFO TX, niveau, twist, trames émises
```

| Touche | Action |
|---|---|
| 0 à 9 | Saisie du code (4 chiffres ; un 5e chiffre recommence un nouveau code) |
| < / > | Code précédent / suivant (maintenu : répétition) |
| F puis < / > | Page précédente / suivante (±100) |
| MENU | **Ajouter** le code au message (15 maximum : « Message plein ») |
| * | Retirer le dernier code |
| F puis * | Vider le message |
| F puis MENU | **Relecture** du message en clair |
| PTT | **Émettre** le message |
| F puis 1 / F puis 7 | Niveau BF (déviation) + / − (10 à 127, défaut 66) |
| F puis 2 / F puis 8 | Twist + / − (gain du 2200 Hz, −4 à +8 soit −6 à +6 dB) |
| F puis 3 / F puis 9 | SSID + / − (0 à 15, défaut 7) |
| F puis 0 | **Éditeur d'indicatif** |
| EXIT | Quitter |

Indicatif, SSID, niveau et twist sont mémorisés (et conservés lors d'une mise à jour). Le message est conservé tant que
l'application est ouverte (l'application ne peut pas écrire en mémoire flash
pendant qu'elle tourne).

Les codes hors répertoire (`2500`…) sont signalés « Hors repertoire 1000-1999 » et
ne peuvent pas être ajoutés.

## Réglages conseillés

- Même fréquence que la station TCQ ou les pagers (145.4375 MHz FM pour RASEC-ALERT).
- Puissance et squelch selon la liaison ; le CTCSS/DCS du VFO est supprimé pendant l'émission.
- Si TCQ / Direwolf décode mal : ajuster le niveau (F 1 / F 7) ou le twist (F 2 / F 8)
  — même réglage que l'application APRS TX de F4HWN, dont l'émetteur AFSK est repris.

## Validation

- Émetteur AFSK identique à **APRS TX** de F4HWN (générateur de tonalité du BK4829,
  NRZI, bit stuffing, 40 drapeaux de préambule), validé sur l'air.
- Banc logiciel : exécution instruction par instruction de l'application réelle
  (émulateur Cortex-M0+) ; l'AFSK émis est reconstitué à partir des écritures du
  BK4829, décodé (FCS correcte, `F1GBD-7>CQ`, `!1000 !1024 !1380 !1990`), puis
  rejoué dans l'émulateur de **PAGER-RASEC**, qui affiche « Debut de transmission.
  Transmission urgente. Communication interrompue. Fin transmission. ». Les 1000
  phrases affichées par CHAPPE-TX sont identiques au répertoire de TCQ.
- Éditeur d'indicatif (v1.1) vérifié en émulation : saisie sans message de démarrage,
  trame émise avec la source saisie, indicatif mémorisé, retour au message de démarrage
  si l'indicatif est effacé, réglages d'une v1.0 conservés.
- Essai sur l'air : à faire.

ADRASEC 77 · F1GBD — 73
