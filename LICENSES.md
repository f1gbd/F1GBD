# Licences du dépôt F1GBD

Ce dépôt regroupe plusieurs projets, chacun sous **sa propre licence**. Le fichier
`LICENSE` présent dans le dossier d'un projet est celui qui fait foi. À défaut, c'est
la **GNU GPL v3** du fichier [`LICENSE.txt`](LICENSE.txt) à la racine qui s'applique.

## PolyForm Noncommercial 1.0.0 — gratuit, usage commercial interdit

Usage libre et gratuit à titre personnel ou radioamateur, et par les associations
(ADRASEC, FNRASEC…), les organismes de sécurité civile et les services publics.
Texte : <https://polyformproject.org/licenses/noncommercial/1.0.0>

`tcq` · `tcqws` · `pdfteleporter` · `photerix` · `winkiss-tnc` · `meshrns` · `meshvara` · `meshpacket` · `homer` · `dia` · `aero-spectrix` · `ADRAlink` · `meshfederator` · `geovor` · `gslorasat` · `iabrain` · `xerulith` · `epirb` (suite Windows : EPIRBdecoder et EPIRB-generator) · `epirb/linux` · `epirb/raspberry` · `epirb/android`

TCQ, TCQws, GeoVOR et la suite EPIRB Windows livrent à part, dans un dossier `sdr-gpl\`, des outils SDR tiers (rtl-sdr, HackRF) qui restent sous leurs propres licences (GPL v2, LGPL 2.1, BSD) ; les éditions Linux et Raspberry Pi d'EPIRB utilisent le `rtl_tcp` du paquet système `rtl-sdr`. TCQ livre aussi à part, dans `ffmpeg-lgpl\`, le programme FFmpeg (LGPL v3).

ADRAlink, MeshFederator, GeoVOR, GSLoRaSat et XERULITH livrent à part, dans un dossier `esptool-gpl\`, l'outil officiel `esptool.exe` d'Espressif (GPL v2), lancé comme programme séparé. Les firmwares tiers écrits dans les cartes restent sous leur licence : Meshtastic (GPL v3), RNode (GPL v3), rsDeck (AGPL v3), et le **TinyGS modifié** de GSLoRaSat et GeoVOR (GPL v3), dont le correctif source est publié dans [`gslorasat/firmware/`](gslorasat/firmware/) et joint aux releases. XERULITH livre à part les simulateurs ArduPilot SITL (GPL v3) ; **Mission Planner OFF-GRID** (GPL v3) est publié dans sa propre release avec son correctif source.

Chaque dossier concerné contient un fichier `THIRD-PARTY-NOTICES.txt` qui détaille ces composants.

## GNU GPL v3 (fichier `LICENSE.txt` à la racine, ou `LICENSE` du dossier)

`epirb/saterfinder` · `TML`

Également sous GPL v3 par défaut : `satersim` et tout autre dossier sans fichier `LICENSE` propre.

## Licence de l'œuvre d'origine

| Projet | Licence | Œuvre d'origine |
|---|---|---|
| `RTspk_pager`, `RTspk_pager/T-Deck` | GNU AGPL-3.0 | Ratspeak / rsDeck |
| `RRLora`, `RWLora`, `quansheng/uv-k5_v1` | Apache 2.0 | microReticulum, firmware F4HWN |
| `Montre_MicroRadar`, `meshpager/android` | MIT | micro-radar, MeshCore Open |
| `meshpager` | MIT | MeshCore |
| `meshpager/tdeck` | GNU GPL-3.0-or-later | Saitama |
| `geomag-observer` | MIT (voir son dossier) | — |

Les versions publiées avant octobre 2026 restent régies par la licence qui les
accompagnait lors de leur publication.

© 2026 Jean-Louis NAUDIN (F1GBD / F4JHW) — ADRASEC 77 / FNRASEC
