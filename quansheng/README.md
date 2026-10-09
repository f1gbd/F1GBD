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

## Applications

| Application | Version | Rôle |
|---|---|---|
| [PAGER-RASEC](apps/PAGER-RASEC.md) | 1.0 | Pager RASEC-ALERT : réception AX.25 Packet 1200 bauds depuis TCQ, LED + sirène sur `#ra <code>`, 145.4375 MHz FM |

## Ajouter une application

1. Construire le `.app` (`./compile-app.sh <app>` dans l'arborescence firmware).
2. Copier le `.app` et sa notice dans `apps/`.
3. Ajouter une entrée dans `apps/manifest.json` (`file`, `name`, `version`, `title`, `summary`, `doc`).

ADRASEC 77 · F1GBD — 73
