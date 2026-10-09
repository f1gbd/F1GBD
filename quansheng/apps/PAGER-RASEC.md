# PAGER-RASEC v1.0 — pager RASEC-ALERT pour Quansheng UV-K1 / UV-K5 v3

Application overlay (`.app`) pour le firmware F4HWN édition Labs. Elle transforme
le portatif en **pager d'alerte ADRASEC** : elle écoute en permanence les trames
**AX.25 Packet 1200 bauds** envoyées par **TCQ** (onglet TNC Packet) et, à la
réception de la commande `#ra <code>`, **fait clignoter la LED et l'écran et
déclenche une sirène** jusqu'à l'acquittement par l'opérateur.

| | |
|---|---|
| Fréquence par défaut | **145.4375 MHz FM** (mode FIX) |
| Modulation | AFSK Bell 202 1200 bauds, trames UI AX.25 (PID F0) |
| Code d'activation par défaut | `ADRASEC77` (identique à TCQ) |
| Sirène | bi-ton 900 / 620 Hz, 350 ms chacun, comme TCQ |
| Taille | 4064 o de code (overlay 4 Kio) + 510 o de ressources |

## Installation

1. Ouvrir l'**[UV-K1 Apps Uploader](../index.html)** dans Chrome ou Edge.
2. Brancher la radio (USB-C), **Connecter la radio**, choisir le port série.
3. Sélectionner **Pager RASEC-ALERT**, garder l'emplacement proposé, **Installer**.
4. Sur la radio : menu **Apps** → **PAGER-RASEC**.

Une mise à jour de l'application conserve ses réglages (code, sirène, options).

## Commandes RASEC-ALERT (envoyées depuis TCQ)

Les commandes sont celles de TCQ (`_rasec_check_message`), tapées dans le chat
TNC Packet, n'importe quelle destination :

| Message | Effet sur le pager |
|---|---|
| `#ra ADRASEC77` | **ALERTE** : écran inversé clignotant « RASEC ALERT / ALERTE / de F1GBD », LED verte clignotante, sirène. **N'importe quelle touche acquitte.** |
| `#b 5` | Nombre de cycles de sirène, 0 à 20 ; `#b 0` = sirène continue jusqu'à l'acquittement |
| `#rapass ADRASEC77 NOUVEAU` | Change le code d'activation (1 à 12 caractères, sensible à la casse) |

- Le code n'est jamais affiché en clair : l'écran résume la commande
  (« ALERTE recue », « Code active modifie », « #ra refuse: code invalide »…).
- Une copie digipétée d'une alerte, reçue dans les 5 s suivant l'acquittement,
  ne relance pas l'alerte.
- Tout autre message reçu est affiché (indicatif + texte, 96 caractères) avec un
  double bip de notification.
- Le pager **n'émet pas d'accusé** en v1.0 (réception seule) : TCQ n'en attend pas.

## Écran et touches

```
 PAGER-RASEC  HP BIP        [batterie]
 F1GBD                              12   <- source, trames reçues
 Bonjour depuis TCQ, test packet         <- texte ou résumé de commande
 1200 bauds vers le pager
 - - - - - - - - - - - - - - - - - - - -
 145.437 50                         FIX  <- fréquence écoutée, mode
                                    Al:1 <- alertes
 Code:**** Sir:3 -87dBm
```

| Touche | Action |
|---|---|
| 1 | Haut-parleur (écoute du canal) marche / arrêt — mémorisé |
| 2 | Effacer le dernier message et les compteurs |
| 3 | **Test local de l'alerte** |
| 4 | Bip des messages ordinaires marche / arrêt (« BIP » dans la barre d'état) — mémorisé |
| 5 | Mode **FIX 145.4375** / **VFO** (écoute sur la fréquence du VFO) — mémorisé |
| MENU | Afficher / masquer le code d'activation |
| EXIT | Quitter (le pager n'écoute que lorsque l'application est ouverte) |

**Mode FIX** : l'application accorde 145.4375 MHz tant que le VFO est dans la
bande 2 m (136-174 MHz). Si le VFO est ailleurs (UHF, bande aviation…), l'écran
affiche `VFO!` et l'application écoute la fréquence du VFO : placez le VFO en
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
  `#b 5`, `#rapass`, `#ra` ancien code, `#ra` nouveau code, `#rapass` faux) : les
  8 trames sont traitées correctement, 145.4375 MHz accordé.
- Essai sur l'air à faire : TCQ + Direwolf → émetteur 145.4375 MHz → UV-K1.

ADRASEC 77 · F1GBD — 73
