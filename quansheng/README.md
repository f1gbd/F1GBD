# Quansheng UV-K1 / UV-K5 v3 — applications Sécurité Civile

Applications overlay (`.app`) pour le firmware F4HWN édition Labs, développées
pour les missions ADRASEC / FNRASEC, et leur outil d'installation.

### ▶ [Ouvrir l'UV-K1 Apps Uploader](https://f1gbd.github.io/F1GBD/quansheng/)

<p align="center">
  <img src="images/UV-K1.jpg" alt="Quansheng UV-K1(8) v3" height="420">
  &nbsp;&nbsp;
  <img src="images/UV-K1_display.jpg" alt="Écran du UV-K1 sous firmware F4HWN" height="420">
</p>
<p align="center"><em>Quansheng UV-K1(8) v3 et son écran sous firmware F4HWN</em></p>

## UV-K1 Apps Uploader

Page web d'installation par **Web Serial** (Chrome / Edge, ordinateur) :
**https://f1gbd.github.io/F1GBD/quansheng/** — elle ne demande aucun logiciel :
brancher la radio, choisir l'application, installer.

> Le lien `github.com/.../blob/master/quansheng/index.html` n'affiche que le code
> source de la page : utilisez l'adresse GitHub Pages ci-dessus.

<p align="center"><img src="images/uploader.png" alt="UV-K1 Apps Uploader" width="720"></p>

- Lecture de la version du firmware et des 16 emplacements Apps de la radio.
- Catalogue des applications de ce dépôt (`apps/manifest.json`) ou fichier `.app` local.
- Contrôle du fichier avant envoi : signature FAP1, ABI, tailles, CRC-32 du code et des ressources.
- Installation : effacement, ressources, code, en-tête en dernier, vérification.
  Une mise à jour garde les réglages de l'application.
- Effacement d'un emplacement.

Le protocole (commandes 0x0514, 0x0730 à 0x0737) est celui du firmware d'Armel
F4HWN, également utilisé par UV Studio ; il est implémenté dans [`uvproto.js`](uvproto.js).

## Essai sur l'air

Premier essai réussi le 9 octobre 2026 : TCQ (TNC Packet, Direwolf) envoie
`#RA ADRASEC77` depuis F1GBD-3, le UV-K1 sous PAGER-RASEC déclenche l'alerte
(écran, LED, sirène) puis affiche « ALERTE recue » après acquittement.

<p align="center">
  <img src="images/UV-K1_RASEC-ALERT.jpg" alt="Alerte RASEC reçue sur le UV-K1" height="380">
  &nbsp;&nbsp;
  <img src="images/UV-K1_RASEC-ALERT_log.jpg" alt="Écran après acquittement" height="380">
</p>
<p align="center"><em>À gauche : l'alerte reçue de F1GBD-3. À droite : l'écran de veille après acquittement
(PAGER-RASEC v1.0, VFO sur 430.4375 MHz, signal −96 dBm, 2 alertes).</em></p>

## Documentation

| Document | Formats |
|---|---|
| PAGER-RASEC v1.1 — Manuel d'installation et d'utilisation | [PDF](documentation/PAGER-RASEC_Manuel_v1.1.pdf) · [Word](documentation/PAGER-RASEC_Manuel_v1.1.docx) |

## Applications

| Application | Version | Rôle |
|---|---|---|
| [PAGER-RASEC](apps/PAGER-RASEC.md) ([manuel PDF](documentation/PAGER-RASEC_Manuel_v1.1.pdf)) | 1.1 | Pager RASEC-ALERT : réception AX.25 Packet 1200 bauds depuis TCQ, LED + sirène sur `#ra <code>`, messages CHAPPE26 en clair, 145.4375 MHz FM |
| CHAPPE26 | 1.0 | Dictionnaire CHAPPE26 (1000 codes) pour PAGER-RASEC — à installer avec lui |

## Ajouter une application

1. Construire le `.app` (`./compile-app.sh <app>` dans l'arborescence firmware).
2. Copier le `.app` et sa notice dans `apps/`.
3. Ajouter une entrée dans `apps/manifest.json` (`file`, `name`, `version`, `title`, `summary`, `doc`).

ADRASEC 77 · F1GBD — 73
