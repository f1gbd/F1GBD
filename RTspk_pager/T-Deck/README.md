# rsDeck T-Deck — édition RASEC-ALERT + MAIL ADRAlink + CHAPPE26 + Carte OSM (F1GBD / ADRASEC 77)

<p align="center">
  <img src="images/RatSpeak_Adrasec_Logo.png" alt="RatSpeak — ADRASEC" width="200">
</p>

<p align="center">
  <img src="images/RATspeak_T-Deck_v300.jpg" alt="rsDeck T-Deck — écran d'accueil v3.0.0" width="380"><br>
  <em>Écran d'accueil <strong>v3.0.0</strong> : LoRa + WiFi + GPS, pairs entendus, boutons <strong>GPS</strong> et <strong>MAIL ADRALINK</strong>.</em>
</p>

Firmware **RASEC-ALERT** pour **LilyGo T-Deck Plus** (ESP32-S3, LoRa SX1262,
écran ST7789, GPS UBlox), dérivé de [rsDeck](https://github.com/ratspeak/rsDeck) —
un messager Reticulum / **LXMF** — et enrichi de l'**option Pager RASEC-ALERT**
portée depuis le MeshPager.

Version : **3.0.0-rasec-f1gbd**

Un message **LXMF** reçu déclenche un **écran plein écran clignotant
« RASEC ALERT »** (avec compteur d'alertes), une **sirène bitonale synthétisée**
et un **accusé de réception automatique**. Aucune carte SD ni fichier `.mp3` :
la sirène est générée en I2S dans le firmware.

Le firmware embarque aussi l'option **MAIL ADRAlink** : depuis l'écran d'accueil,
le bouton **MAIL ADRALINK** ouvre un formulaire pour envoyer un court **email
d'urgence** à un proche via une passerelle **ADRAlink** (routage Winlink / ADRASEC)
et **relire les réponses** — le tout par radio, sans Internet.

Le **décodeur CHAPPE26** est intégré : à la réception d'un message LXMF contenant
des codes CHAPPE26 au format transmission (`!1000 !1204 !1990 …`), le firmware
**décode automatiquement** et affiche la **traduction en clair** juste sous le
message, à partir du **répertoire complet ADRASEC/FNRASEC** (10 domaines × 100
lignes = **1000 codes** ; ex. `1204` = *Santé · Ambulance requise*). Un décodeur de
test est accessible via **Settings → « Decodeur CHAPPE26 »**.

voir le LIVRET du **Code CHAPPE-26** (https://github.com/f1gbd/F1GBD/blob/master/TML/documentation/Chappe26_Livret_B5.pdf)

---

## 🆕 Nouveau en 3.0.0 — Carte OSM live + off-grid, dialogue GPS, filtre TCQ

**Carte OSM centrée sur la position GPS (live + hors-réseau).** Un nouveau bouton
**GPS** sur l'écran d'accueil ouvre un **dialogue d'état GPS** (statut, coordonnées
Lat/Lon, satellites, HDOP, altitude). Dès que la position est verrouillée, le bouton
**CARTE** ouvre une **carte OpenStreetMap** centrée sur le T-Deck, avec **marqueur de
position** en temps réel.

- **Off-grid (sans réseau)** — les tuiles sont lues depuis la micro-SD dans
  `maps/osm/{z}/{x}/{y}.png` (arborescence *slippy map* standard). Idéal terrain,
  comme TCQ.
- **Live (WiFi)** — les tuiles manquantes sont **téléchargées** depuis
  OpenStreetMap **puis mises en cache sur la SD** automatiquement. Une zone parcourue
  en ligne devient donc réutilisable **hors-réseau** ensuite.
- **Navigation** — **glisser** le doigt pour déplacer la carte, boutons à l'écran
  **`+` / `−`** (zoom) et **`O`** (recentrer GPS). Au clavier : `+`/`-`, flèches,
  `c` (recentrer), Retour (revenir).

> **Préparer l'off-grid.** Avant une mission, connecter le T-Deck en WiFi et balayer
> la zone d'intérêt **à chaque niveau de zoom** utile : les tuiles se rangent sur la
> SD au fur et à mesure et restent disponibles hors-réseau (le cache est **par niveau
> de zoom**). On peut aussi pré-copier un dossier `maps/osm/` à la racine de la SD.

<p align="center">
  <img src="images/RATspeak_T-Deck_map.jpg" alt="Carte OSM sur le T-Deck (terrain)" width="330">
  &nbsp;&nbsp;
  <img src="images/Carto_v300.jpg" alt="Carte OSM plein écran — Melun" width="400"><br>
  <em>Carte OSM centrée sur la position GPS : sur le terrain (à gauche) et en plein
  écran (à droite). Glisser pour déplacer, boutons <code>+</code> / <code>−</code>
  (zoom) et <code>O</code> (recentrer GPS) ; marqueur rouge = position.</em>
</p>

**Filtre TCQ dans « Peers ».** Une case **TCQ** en haut de la liste des pairs filtre
l'affichage pour ne garder que les annonces dont le nom commence par `TCQ`.

<p align="center">
  <img src="images/Filtage_TCQ.jpg" alt="Filtre TCQ dans l'écran Peers" width="400"><br>
  <em>Filtre <strong>TCQ</strong> actif dans « Peers » : seules les annonces
  commençant par <code>TCQ</code> sont affichées.</em>
</p>

<p align="center">
  <img src="images/t-deck_ratspeak-Chappe26.png" alt="rsDeck T-Deck — décodage Chappe26" width="580"><br>
  <em>Décodage de message <strong>Chappe26</strong> intégré.</em>
</p>

---

## ⚡ Flash en un clic (recommandé)

Le plus simple : flasher directement depuis le navigateur, sans rien installer.

**➡️ https://f1gbd.github.io/F1GBD/RTspk_pager/T-Deck/**

1. Ouvrez la page depuis **Chrome** ou **Edge** sur ordinateur (Web Serial requis
   — ne fonctionne pas sur iOS/Safari).
2. Branchez le T-Deck en USB-C, interrupteur sur **ON**, cliquez **Installer**,
   choisissez le port.
3. Laissez l'installation se terminer, puis appuyez sur **reset**.

Si le bouton n'arrive pas à se connecter (fréquent sur ESP32-S3 à USB natif),
mettez d'abord le T-Deck en **mode download** — maintenir la trackball, appuyer
sur reset (côté gauche), relâcher — puis recliquez sur **Installer**.

> **Région radio.** rsDeck démarre par défaut sur *Americas (915 MHz)*. Pour la
> France, choisir **Europe (868 MHz)** dans *Settings → Radio* après le 1ᵉʳ boot.
> Il y a deux possibilités de réglages LoRa :
> - France Std 868 (Fréq : 867.5 MHz BW125/SF8/CR5)
> - France HD 868 (Fréq : 867.5 MHz BW500/SF7/CR5)

<p align="center">
  <img src="images/Preset.png" alt="Accueil rsDeck en LoRa pur 868 MHz" width="580"><br>
  <em>Accueil en <strong>LoRa pur</strong> (868 MHz, TCP/WiFi coupés) — configuration terrain ADRASEC.</em>
</p>

---

## Option Pager RASEC-ALERT — utilisation

Depuis un autre nœud Reticulum/LXMF, en **message direct** vers l'adresse LXMF
du T-Deck :

- `#ra ADRASEC77` — déclenche l'alerte (écran clignotant + sirène + ACK). Le code
  `ADRASEC77` est modifiable.
- `#rapass <ancien> <nouveau>` — change le code d'activation à distance (persisté
  en flash NVS).
- `#b <n>` — règle le nombre de répétitions de la sirène. `#b 0` = alarme continue
  jusqu'à acquittement (plage 0–20).

**Acquittement :** toucher l'écran, appuyer sur une touche, ou appui long.

L'accusé renvoyé ne contient jamais le code (anti-boucle). La sirène suit le
volume et l'interrupteur haut-parleur des réglages.

<p align="center">
  <img src="images/t-deck_ratspeak-alert.png" alt="Écran d'alerte RASEC ALERT" width="300"><br>
  <em>Écran d'alerte plein écran clignotant, compteur d'alertes et invite d'acquittement.</em>
</p>

---

## Carte SD — tuiles OSM (off-grid)

Pour la carte hors-réseau, placer les tuiles sur la micro-SD du T-Deck dans
l'arborescence *slippy map* standard :

```
/maps/osm/{zoom}/{x}/{y}.png        ex. /maps/osm/15/16600/11269.png
```

Les tuiles téléchargées en mode WiFi (« live ») sont **automatiquement** rangées
dans cette même arborescence, ce qui alimente le cache off-grid au fil de la
navigation.

---

## Contenu de ce dossier

| Fichier | Rôle |
|---|---|
| `index.html` | Page de flash web (ESP Web Tools). |
| `manifest.json` | Manifest ESP Web Tools (ESP32-S3, image à l'offset `0x0`). |
| `rsdeck-mail-adralink-3.0.0.bin` | **Image firmware fusionnée** (à flasher à l'offset `0x0`). |
| `CHANGELOG.md` | Historique des versions. |
| `images/` | Photos et captures d'écran du T-Deck. |
| `README.md` | Ce fichier. |

> ⚠️ Le web-flasher ne fonctionne que si le binaire référencé par `manifest.json`
> (`rsdeck-mail-adralink-3.0.0.bin`) est présent dans ce dossier et poussé sur
> GitHub. C'est le fichier à régénérer — et à renommer avec le numéro de version —
> à chaque nouvelle version du firmware.

---

## Licence & crédits

- Firmware dérivé de [rsDeck](https://github.com/ratspeak/rsDeck) — voir la
  licence du dépôt d'origine.
- Basé sur [Reticulum](https://github.com/markqvist/Reticulum) /
  [microReticulum](https://github.com/attermann/microReticulum).
- Cartographie : tuiles [OpenStreetMap](https://www.openstreetmap.org/copyright)
  (© les contributeurs OpenStreetMap).
- Flash web : [ESP Web Tools](https://github.com/esphome/esp-web-tools).
- Portage T-Deck et option RASEC-ALERT : **F1GBD — ADRASEC 77**.
