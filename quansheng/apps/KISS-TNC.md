# KISS-TNC v0.1 — le Quansheng UV-K1 / UV-K5 v3 en TNC KISS AX.25 1200 bauds pour TCQ

Application overlay (`.app`) pour le firmware F4HWN édition Labs. Elle fait du
portatif un **TNC Packet AX.25 1200 bauds** piloté en **KISS** par le simple
**câble de programmation** (prise K, celui de CHIRP ou UV Studio) : le PC de crise
sous **TCQ v14.3** (onglet TNC Packet, mode série) envoie ses radiogrammes, messages
et images par la radio, et reçoit ceux des autres stations — sans TNC matériel,
sans Direwolf, sans carte son.

<p align="center">
  <img src="../images/KISS-TNC_UV-K1_F1GBD.jpg" alt="UV-K1 sous KISS-TNC relié au PC par le câble de programmation" height="420">
  &nbsp;
  <img src="../images/KISS-TNC.jpg" alt="Écran de KISS-TNC après l'envoi d'une image de 21 trames" height="300">
</p>
<p align="center"><em>Le UV-K1 sous KISS-TNC sur la prise K ; l'écran après l'envoi d'une image de 21 trames par TCQ v14.3 (2 passages en émission, accusé de F8KSM-7 reçu)</em></p>

<p align="center">
  <img src="../images/KISS-TNC_chaine.png" alt="TCQ, câble de programmation, UV-K1 sous KISS-TNC, transpondeur, stations" width="760">
</p>

| | |
|---|---|
| Liaison PC | prise K, **38400 bauds** 8N1, protocole KISS (port 0) |
| Liaison radio | AX.25 1200 bauds AFSK, toutes trames (UI, accusés, trames connectées) |
| Fréquence | celle du **VFO** : puissance, décalage, **CTCSS / DCS conservés** |
| TXDELAY / persistance / slot time | ceux de TCQ (800 ms, 128, 30 ms par défaut) |
| Accès au canal | CSMA p-persistant : porteuse (RSSI) ou trame en cours = attente |
| Garde-fous | verrous d'émission du firmware, **jamais entre 405 et 407 MHz**, 15 s max par émission |
| Taille | 3 356 o de code (overlay 4 Kio) + 1 656 o de ressources (2 modules) |

Manuel complet : [PDF](../documentation/KISS-TNC_Manuel_v0.1.pdf).

## Installation

1. Ouvrir l'**[UV-K1 Apps Uploader](https://f1gbd.github.io/F1GBD/quansheng/)** dans Chrome ou Edge.
2. Brancher la radio (USB-C), **Connecter la radio**, choisir le port série.
3. Sélectionner **TNC KISS pour TCQ (KISS-TNC)**, garder l'emplacement proposé, **Installer**.

## Mise en route avec TCQ

1. Régler le **VFO** comme pour la phonie : fréquence, décalage et **CTCSS du
   transpondeur**, puissance.
2. Brancher le câble de programmation sur la **prise K** de la radio et sur le PC.
3. Radio : **Apps → KISS-TNC**.
4. TCQ **v14.3 ou plus**, onglet **TNC Packet** : mode **serial**, port COM du câble,
   **38400** bauds, TX Delay **800 ms**, Persistence 128, Slot Time 30 ms,
   Max Packet Len 255 ; **Connecter**. Les paramètres KISS s'affichent sur la radio.
5. Envoyer : la radio passe en émission (TX), puis revient en réception.
6. Pour finir : Déconnecter dans TCQ, puis **EXIT** sur la radio (la prise K est
   rendue au firmware : CHIRP, UV Studio et l'Apps Uploader fonctionnent de nouveau).

> Lancer KISS-TNC **avant** de connecter TCQ, pour qu'il reçoive les paramètres KISS.
> Avec une version de TCQ antérieure à **v14.3**, une image (21 trames envoyées en
> 11 s) fait déborder la mémoire de la radio (1,2 Ko) : « DEBORD », trames perdues.
> TCQ v14.3 envoie, en mode série, au rythme où la radio peut émettre.

## L'écran

| Ligne | Signification |
|---|---|
| `430.4375  RX` | fréquence ; **RX** canal libre, **OCC** occupé, **TX** émission |
| `PC>RF 21 PTT 2` | trames reçues de TCQ et émises ; passages en émission |
| `RF>PC 1 FILE 2` | trames reçues par radio et envoyées à TCQ ; trames en attente |
| `R F8KSM-7>F1GBD` / `E F1GBD>CQ` | dernière trame reçue / émise |
| `TXD800 P128 SL30` | TXDELAY, persistance, slot time en vigueur |
| `-85dB N62 HP E2` | signal reçu, niveau BF d'émission, haut-parleur, erreurs (HP et E seulement s'ils servent) |

Messages : `406 MHZ INTERDIT`, `EMISSION REFUSEE` (verrou du firmware, batterie,
VFO en AM), `DEBORD` (trop de données en attente) : les trames en attente sont
abandonnées.

## Touches

| Touche | Action |
|---|---|
| 1 | Haut-parleur marche / arrêt |
| HAUT / BAS | Niveau BF d'émission + / − (10 à 127, 66 par défaut, mémorisé) |
| \* | Remise à zéro des compteurs |
| EXIT | Quitter (prise K rendue au firmware) |

## Essai sur l'air du 11 octobre 2026

TCQ v14.3 (onglet TNC Packet, série COM10, 38400 bauds) → câble de programmation →
UV-K1 sous KISS-TNC sur 430,4375 MHz → transpondeur → station **F8KSM-7** :

- **RADIOGRAMME ADRASEC** de 12 trames (936 octets) : reçu, CRC valide, **ACK** de
  F8KSM-7 reçu par radio et affiché par TCQ ;
- **image** de 21 trames (3 463 octets) : reçue complète, **ACK** « Image reçu »
  7 s après la dernière trame.

<p align="center">
  <img src="../images/KISS-TNC_TCQ.png" alt="TCQ : radiogramme envoyé par le UV-K1, accusé de F8KSM-7 reçu" width="760">
</p>
<p align="center"><em>TCQ, onglet TNC Packet en série : radiogramme C79E envoyé par le UV-K1 sous KISS-TNC, accusé de F8KSM-7 reçu par radio</em></p>

<p align="center">
  <img src="../images/KISS-TNC_UV-K1.jpg" alt="Écran après le radiogramme" width="360">
</p>
<p align="center"><em>L'écran après le radiogramme : 12 trames en 9 passages, accusé de F8KSM-7 reçu</em></p>

## Validation

- Démodulateur et modulateur AFSK : APRS RX et APRS TX d'Armel F4HWN, déjà employés
  par PAGER-RASEC, CHAPPE-TX, RGRAM, TACVYR et EPIRBdecoder.
- Banc logiciel (l'App réelle exécutée instruction par instruction, flux KISS à
  38400 bauds, audio AFSK bruité, émissions décodées) : trames de TCQ émises à
  l'identique (FCS correct, TXDELAY 800 ms), plusieurs trames sous un même passage,
  trames reçues rendues à l'identique à l'hôte, émission retardée tant qu'une
  trame est reçue, image de 21 trames au rythme de TCQ v14.3 : 21 / 21 ; 406 MHz et
  verrou : aucune émission ; prise K rendue au firmware. Pile au pire 3 056 o.
- Essai sur l'air réussi le 11 octobre 2026 (radiogramme et image, accusés reçus).

ADRASEC 77 · F1GBD — 73
