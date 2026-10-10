# PAGER-RASEC v1.4.1 — pager RASEC-ALERT pour Quansheng UV-K1 / UV-K5 v3

Application overlay (`.app`) pour le firmware F4HWN édition Labs. Elle transforme
le portatif en **pager d'alerte ADRASEC** : elle écoute en permanence les trames
**AX.25 Packet 1200 bauds** envoyées par **TCQ** (onglet TNC Packet) et, à la
réception de la commande `#ra <code>`, **fait clignoter la lampe blanche frontale et l'écran et
déclenche une sirène** jusqu'à l'acquittement par l'opérateur.

**Nouveau en v1.4.1 : radiogrammes de TCQ.** Un radiogramme envoyé par TCQ
dans son format habituel (compressé) est toujours signalé « Radiogramme TCQ
(compresse): lire sur TCQ », même si une trame est perdue : la v1.4 affichait à
tort « incomplet: faire repeter ». Avec **TCQ v14.2** et sa case
**📟 Compatible pager UV-K1**, le radiogramme du PC de crise s'affiche en clair
sur le pager, comme ceux de RGRAM.

**v1.4 : radiogrammes RGRAM.** Un RADIOGRAMME ADRASEC émis par un
autre UV-K1 avec l'application **RGRAM v1.1** est reconstitué trame après trame
et affiché comme un message reçu : « ADRASEC 77 14:32 PRIORITE: INCENDIE ENTREPOT
ZONE NORD / 2 BLESSES LEGERS / ... » (voir Radiogrammes RGRAM).

**v1.3 : l'alerte fait clignoter la lampe blanche frontale** (la lampe
torche du UV-K1), bien plus visible que le petit voyant vert, en même temps que
l'écran. La lampe est éteinte à l'acquittement.

**v1.2.1 :** correctif du défilement (< / > vidaient l'écran) et du dernier code
CHAPPE26 tronqué sur les longs messages.

**Nouveau en v1.2 : les 6 derniers messages sont conservés**, consultables et
effaçables (voir Écran et touches).

**Depuis la v1.1 : décodage CHAPPE26.** Un message `!1000 !1024 !1990` est
affiché en clair, comme dans TCQ : « Debut de transmission. Transmission
urgente. Fin transmission. » — avec l'application dictionnaire **CHAPPE26**.

Manuel complet : [PDF](../documentation/PAGER-RASEC_Manuel_v1.4.pdf)

| | |
|---|---|
| Fréquence par défaut | **145.4375 MHz FM** (mode FIX) |
| Modulation | AFSK Bell 202 1200 bauds, trames UI AX.25 (PID F0) |
| Code d'activation par défaut | `ADRASEC77` (identique à TCQ) |
| Sirène | bi-ton 900 / 620 Hz, 350 ms chacun, comme TCQ |
| CHAPPE26 | 1000 codes `!PPLL` décodés en clair (application CHAPPE26 requise) |
| Historique | 6 messages (commandes et alertes comprises), conservés tant que l'app tourne |
| Radiogrammes | format RGRAM v1.1 (`{QR:…}`), résumé de 96 caractères au plus |
| Taille | 4072 o de code (overlay 4 Kio) + 3312 o de ressources (3 modules) ; CHAPPE26 : 7,2 ko de dictionnaire |

<p align="center">
  <img src="../images/UV-K1_RASEC-ALERT.jpg" alt="Alerte RASEC reçue sur le UV-K1" height="320">
  &nbsp;&nbsp;
  <img src="../images/UV-K1_RASEC-ALERT_log.jpg" alt="Écran après acquittement" height="320">
</p>
<p align="center"><em>Essai sur l'air depuis TCQ : alerte reçue, puis écran après acquittement (v1.0)</em></p>

## Installation

1. Ouvrir l'**[UV-K1 Apps Uploader](../index.html)** dans Chrome ou Edge.
2. Brancher la radio (USB-C), **Connecter la radio**, choisir le port série.
3. Sélectionner **Pager RASEC-ALERT**, garder l'emplacement proposé, **Installer**.
4. Sélectionner **Dictionnaire CHAPPE26**, garder l'emplacement proposé, **Installer**
   (sans lui, les messages CHAPPE26 restent affichés en codes bruts).
5. Sur la radio : menu **Apps** → **PAGER-RASEC**. L'écran de veille indique
   « Dico CHAPPE26 : OK ».

Une mise à jour de l'application conserve ses réglages (code, sirène, options).

## Commandes RASEC-ALERT (envoyées depuis TCQ)

Les commandes sont celles de TCQ (`_rasec_check_message`), tapées dans le chat
TNC Packet, n'importe quelle destination :

| Message | Effet sur le pager |
|---|---|
| `#ra ADRASEC77` | **ALERTE** : écran inversé clignotant « RASEC ALERT / ALERTE / de F1GBD », lampe blanche frontale clignotante, sirène. **N'importe quelle touche acquitte.** |
| `#b 5` | Nombre de cycles de sirène, 0 à 20 ; `#b 0` = sirène continue jusqu'à l'acquittement |
| `#rapass ADRASEC77 NOUVEAU` | Change le code d'activation (1 à 12 caractères, sensible à la casse) |

- Le code n'est jamais affiché en clair : l'écran résume la commande
  (« ALERTE recue », « Code active modifie », « #ra refuse: code invalide »…).
- Une copie digipétée d'une alerte, reçue dans les 5 s suivant l'acquittement,
  ne relance pas l'alerte.
- Tout autre message reçu est affiché (indicatif + texte) avec un double bip de
  notification. Les 6 derniers messages sont conservés tant que l'application est
  ouverte (ils sont perdus à la sortie : l'application ne peut pas écrire en mémoire
  flash pendant qu'elle tourne).
- Le pager **n'émet pas d'accusé** en v1.0 (réception seule) : TCQ n'en attend pas.

## Messages CHAPPE26

Le code CHAPPE26 (répertoire de 1000 expressions, pages 10 à 19) se transmet
sous la forme `!PPLL` : `!1204` = page 12 (Santé générale), ligne 04 =
« Ambulance requise ». Règle de TCQ, reprise à l'identique :

| Message reçu | Affichage |
|---|---|
| `!1000 !1024 !1376 !1380 !1032 !1349 !1333 !1354 !1990` | Debut de transmission. Transmission urgente. Coupure electricite. Communication interrompue. Passez en mode secours. Equipement requis. Besoin renfort. Coordination requise. Fin transmission. |
| `!1204` (seul) | Ambulance requise. |
| `Rdv !1204 demain` (un seul code dans du texte) | affiché tel quel, pas de décodage |
| `!2500 !1990` | Code inconnu (2500). Fin transmission. |

Le texte en clair occupe jusqu'à 6 lignes de 32 caractères, coupées aux espaces ;
un `v` en bas à droite signale une suite (ou un message plus ancien), un `^` en
haut à droite un début caché (ou un message plus récent) : **< / >** pour faire
défiler, puis passer au message suivant.

## Radiogrammes RGRAM

L'application **RGRAM** (autre UV-K1), ou **TCQ v14.2** avec la case
**📟 Compatible pager UV-K1**, émet un radiogramme ADRASEC en 11 à 15 trames
`{QR:ID:NN/TT:…}` de 80 caractères, non compressé. Le pager les assemble au fil de la
réception, sans redessiner l'écran, puis affiche l'essentiel sur une ligne :

| Cas | Affichage |
|---|---|
| Radiogramme complet | `ADRASEC 77 14:32 PRIORITE: INCENDIE ENTREPOT ZONE NORD / 2 BLESSES LEGERS / EVACUATION EN COU...` |
| Une trame perdue | `Radiogramme incomplet: faire repeter` (RGRAM : PTT à nouveau ; TCQ : Envoyer à nouveau) |
| Radiogramme TCQ compressé (case décochée, ou TCQ avant v14.2), même incomplet | `Radiogramme TCQ (compresse): lire sur TCQ` — inutile de le faire répéter |

- Origine, heure, niveau d'alerte, puis les lignes de la description séparées par
  « / » ; au-delà de 96 caractères le texte finit par « ... ». Le texte complet et
  le code d'authentification se lisent sur TCQ.
- Le format compressé de TCQ (deflate, trames de 170 caractères) ne tient pas
  dans la radio : le pager le reconnaît à la longueur de ses trames et renvoie à
  TCQ. Pour l'afficher sur les pagers, cocher **📟 Compatible pager UV-K1** dans
  TCQ v14.2 (accents retirés, CRC toujours valide pour TCQ).
- Quand 6 messages sont conservés, le plus ancien est remplacé dès la première
  trame d'un radiogramme.

Manuel RGRAM : [PDF](../documentation/RGRAM_Manuel_v1.1.pdf).

## Écran et touches

```
 PAGER-RASEC  HP BIP        [batterie]
 F1GBD-3                           1/6   <- source, message affiché / conservés
 Debut de transmission.                  <- texte, traduction CHAPPE26
 Transmission urgente. Coupure              ou résumé de commande
 electricite. Communication                 (6 lignes, défilement haut/bas)
 interrompue. Passez en mode
 secours. Equipement requis.
 Besoin renfort. Coordination          v
 - - - - - - - - - - - - - - - - - - - -
 145.43750 FIX A1 S3 -87dBm              <- fréquence, mode, alertes, sirène, niveau
```

| Touche | Action |
|---|---|
| 1 | Haut-parleur (écoute du canal) marche / arrêt — mémorisé |
| 2 | **Effacer le message affiché** |
| 0 | **Effacer tous les messages** (et le compteur d'alertes) |
| 3 | **Test local de l'alerte** |
| 4 | Bip des messages ordinaires marche / arrêt (« BIP » dans la barre d'état) — mémorisé |
| 5 | Mode **FIX 145.4375** / **VFO** (écoute sur la fréquence du VFO) — mémorisé |
| < / > (haut / bas) | Faire défiler le message ; à la fin, passer au message plus ancien (>) ou plus récent (<) |
| MENU | Afficher le code d'activation sur la ligne du bas (à la place de la fréquence) |
| EXIT | Quitter (le pager n'écoute que lorsque l'application est ouverte) |

**Mode FIX** : l'application accorde 145.4375 MHz tant que le VFO est dans la
bande 2 m (136-174 MHz). Si le VFO est ailleurs (UHF, bande aviation…), l'écran
affiche `VFO!` sur la ligne du bas et l'application écoute la fréquence du VFO : placez le VFO en
VHF, ou directement sur 145.4375 MHz. À la sortie, la radio retrouve son VFO.

Le volume de la sirène suit le bouton de volume : réglez-le avant la veille.

## Réglages TCQ conseillés

- TNC Packet (Direwolf KISS TCP ou TNC série), 1200 bauds, émetteur sur 145.4375 MHz FM.
- Message court, une seule trame (TCQ découpe au-delà de 92 caractères ; le pager
  n'affiche que le dernier fragment).
- Même code dans TCQ (bouton « 🚨 RASEC-ALERT ») et sur le pager.

## Validation

- Démodulateur identique à l'application **APRS RX** de F4HWN (3 slicers, DPLL,
  HDLC, FCS), validé sur l'air.
- Banc logiciel : séquence TCQ synthétique (message texte, `#ra` faux code, `#ra`,
  `#b 5`, `#rapass`, `#ra` ancien code, `#ra` nouveau code, `#rapass` faux, puis
  4 messages CHAPPE26) : les 12 trames sont traitées correctement, avec et sans
  dictionnaire installé ; 145.4375 MHz accordé. Les 1000 codes du dictionnaire
  compressé sont vérifiés à chaque construction.
- **Essai sur l'air réussi** (9 octobre 2026, v1.0) : TCQ + Direwolf → émetteur →
  UV-K1, `#RA ADRASEC77` de F1GBD-3 reçu à −96 dBm, alerte et acquittement OK.
  Décodage CHAPPE26 (v1.1) : essai sur l'air à faire.
- Radiogrammes (v1.4) : 4 radiogrammes émis par l'émulation de l'application RGRAM
  réelle affichés correctement ; trame perdue, radiogramme TCQ compressé et
  description de 8 lignes (coupée) traités ; les 12 trames de la séquence TCQ
  toujours correctes après un radiogramme. Essai sur l'air : à faire.
- v1.4.1 : radiogrammes TCQ compressés complets, avec la 2e trame perdue et avec
  la 1re trame perdue : « Radiogramme TCQ (compresse) » dans les trois cas ;
  radiogrammes émis par la vraie fenêtre de TCQ v14.2 (format pager) affichés en
  clair. Pile au pire 3 400 o (émulation du vrai binaire).

ADRASEC 77 · F1GBD — 73
