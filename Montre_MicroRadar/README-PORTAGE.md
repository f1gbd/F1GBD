# Micro Radar sur Waveshare Touch-AMOLED-2.06 (S3 et C6)

Portage du projet [micro-radar](https://github.com/AnthonySturdy/micro-radar)
(ESP32-C3 + écran rond GC9A01 240×240) vers les cartes Waveshare
**Touch-AMOLED-2.06** (dalle AMOLED CO5300 410×502 en QSPI).

Un seul jeu de sources, deux environnements PlatformIO :

| Environnement | Carte | SoC | PSRAM | Backbuffer |
|---|---|---|---|---|
| `esp32-s3-amoled-206` *(défaut)* | ESP32-**S3**-Touch-AMOLED-2.06 | LX7 double cœur 240 MHz | 8 Mo OPI | 16 bits, 412 Ko en PSRAM |
| `esp32-c6-amoled-206` | ESP32-**C6**-Touch-AMOLED-2.06 | RISC-V 160 MHz | aucune | palette 4 bits, 103 Ko en SRAM |

```bash
pio run                                    # compile les deux
pio run -e esp32-s3-amoled-206 -t upload   # flash la S3
pio run -e esp32-c6-amoled-206 -t upload   # flash la C6
pio device monitor
```

Les deux environnements ont été **compilés avec succès** (platform pioarduino
55.03.31 / arduino-esp32 3.3.0 / ESP-IDF 5.5).

---

## Les deux cartes

Même dalle, mêmes puces annexes, **brochage totalement différent** :

| Signal | **S3-Touch-AMOLED-2.06** | **C6-Touch-AMOLED-2.06** |
|---|---|---|
| LCD_SCLK | GPIO11 | GPIO0 |
| LCD_SDIO0 | GPIO4 | GPIO1 |
| LCD_SDIO1 | GPIO5 | GPIO2 |
| LCD_SDIO2 | GPIO6 | GPIO3 |
| LCD_SDIO3 | GPIO7 | GPIO4 |
| LCD_CS | GPIO12 | GPIO5 |
| LCD_RESET | GPIO8 | GPIO11 |
| I2C SDA | GPIO15 | GPIO8 |
| I2C SCL | GPIO14 | GPIO7 |
| TP_INT | GPIO38 | GPIO15 |
| TP_RESET | GPIO9 | GPIO10 |
| Bouton BOOT | GPIO0 | GPIO9 |
| Carte SD | GPIO1/2/3/17 | absente |

Communs : dalle **CO5300** 410×502 QSPI (offset colonne 22), tactile **FT3168**
(I2C 0x38) d'après les exemples Arduino officiels, IMU **QMI8658**, RTC
**PCF85063**, PMU **AXP2101**, 16 Mo de Flash.

Dépôts officiels :

* https://github.com/waveshareteam/ESP32-S3-Touch-AMOLED-2.06
* https://github.com/waveshareteam/ESP32-C6-Touch-AMOLED-2.06

---

## 1. Programmer la carte via l'USB-C

### Ce qu'il faut savoir sur le port USB-C

L'ESP32-S3 comme l'ESP32-C6 intègrent un contrôleur **USB Serial/JTAG natif**.
Le connecteur USB-C est câblé **directement** sur les broches USB du SoC.
Conséquences :

* **aucun pilote à installer** (pas de CH340, CP2102 ni FTDI sur ces cartes) ;
* Windows énumère un *USB JTAG/serial debug unit* + un port COM
  (VID:PID **303A:1001**) ;
* le port COM **disparaît et réapparaît** à chaque reset / flash — c'est normal ;
* `Serial` dans le code = le port USB, à condition de compiler avec
  `ARDUINO_USB_MODE=1` et `ARDUINO_USB_CDC_ON_BOOT=1` (fait dans le
  `platformio.ini`). Les exemples Waveshare, eux, instancient explicitement
  `HWCDC USBSerial;` — les deux approches marchent.

### Identifier le bon port

```powershell
pio device list
```

Cherche la ligne `USB VID:PID=303A:1001`. Les ports Bluetooth virtuels
(`BTHENUM\...`) ne sont pas des cartes ESP32.

> **Attention si tu as les deux cartes** : elles ont le même VID:PID, donc
> impossible de les distinguer par le nom du port. Débranche celle dont tu ne
> te sers pas. Si tu flashes le mauvais environnement, esptool refuse avec
> `This chip is ESP32-S3, not ESP32-C6` — c'est le signe que le port pointe sur
> l'autre carte.

### Méthode A — PlatformIO

Le paquet PlatformIO officiel `espressif32` **ne gère pas** Arduino sur C6 : le
`platformio.ini` utilise le fork **pioarduino** pour les deux cartes.

```bash
pio run -e esp32-s3-amoled-206 -t upload
pio device monitor
```

> **Ne jamais ajouter `lib_ldf_mode = deep+`** : avec arduino-esp32 3.x, ce
> mode casse la résolution des includes des bibliothèques intégrées au
> framework et produit
> `WiFiGeneric.h:44:10: fatal error: Network.h: No such file or directory`.
> Le mode par défaut (`chain+`) fonctionne.

### Méthode B — Arduino IDE 2.x

1. *Préférences → URL de gestionnaire de cartes* :
   `https://espressif.github.io/arduino-esp32/package_esp32_index.json`
2. Installer **esp32 by Espressif Systems ≥ 3.2.0**

| Paramètre | ESP32-S3-AMOLED-2.06 | ESP32-C6-AMOLED-2.06 |
|---|---|---|
| Board | **ESP32S3 Dev Module** | **ESP32C6 Dev Module** |
| USB CDC On Boot | Enabled | Enabled |
| USB Mode | **Hardware CDC and JTAG** | — |
| PSRAM | **OPI PSRAM** | Disabled |
| Flash Size | 16MB (128Mb) | 16MB (128Mb) |
| Partition Scheme | Huge APP (3MB No OTA) | Huge APP (3MB No OTA) |
| Upload Speed | 921600 | 921600 |

### Méthode C — ESP-IDF v5.5

```bash
idf.py set-target esp32s3     # ou esp32c6
idf.py -p COMxx flash monitor
```

### Méthode D — flasher un binaire tout prêt

Les dépôts Waveshare contiennent des firmwares d'usine dans `FirmWare/`, à
écrire à l'adresse **0x0** :

```bash
esptool --chip esp32s3 -p COMxx -b 921600 write_flash 0x0 firmware.bin
```

ou via le *Flash Download Tool* d'Espressif.

### Mode téléversement forcé (BOOT + RESET)

Normalement l'outil de flash bascule la carte tout seul en mode téléchargement
via les lignes DTR/RTS du CDC. Si ça échoue — typiquement après avoir flashé un
firmware qui plante avant l'init de l'USB :

1. maintenir **BOOT** enfoncé (**GPIO0** sur S3, **GPIO9** sur C6) ;
2. appuyer brièvement sur **RESET** (ou débrancher/rebrancher l'USB-C) ;
3. relâcher **BOOT**.

En dernier recours : `esptool --chip esp32s3 -p COMxx erase_flash`.

---

## 2. Le portage de Micro Radar

### Choix techniques

| Sujet | C3 d'origine | Touch-AMOLED-2.06 |
|---|---|---|
| Écran | GC9A01 240×240, SPI | CO5300 410×502, **QSPI** |
| Lib graphique | LovyanGFX | **LovyanGFX** (inchangée) |
| Backbuffer | sprite 240×240 8 bpp = 57 Ko | S3 : 16 bpp PSRAM · C6 : 4 bpp SRAM |
| Rétroéclairage | PWM sur GPIO3 | aucun — AMOLED, luminosité par registre `0x51` |

**LovyanGFX gère nativement cette dalle** depuis la version **1.2.26**
(`lgfx::Panel_CO5300` + bus QSPI `lgfx::Bus_SPI` avec `pin_io0..io3`), et
supporte aussi bien l'ESP32-S3 que l'ESP32-C6. Tout le code de dessin de
micro-radar (`LGFX_Sprite`, `drawCircle`, `fillTriangle`, `drawLine`…) est donc
réutilisé **tel quel**.

### Les trois pièges du portage

**1. La mémoire du backbuffer.** Un backbuffer plein écran 410×502 coûte :

| Profondeur | Taille | S3 (8 Mo PSRAM) | C6 (512 Ko SRAM, pas de PSRAM) |
|---|---|---|---|
| 16 bpp | 412 Ko | ✅ en PSRAM | impossible |
| 8 bpp | 206 Ko | ✅ | impossible avec WiFi + TLS |
| 4 bpp palette | 103 Ko | ✅ | ✅ |

Sur S3 on prend le 16 bits plein couleur en PSRAM. Sur C6 on tombe sur une
sprite en **palette 4 bits** (16 nuances de vert, ce qui suffit largement à
l'esthétique du radar). En mode palette, les fonctions de dessin de LovyanGFX
reçoivent un **numéro de palette**, pas une couleur RGB — d'où la fonction
`G(niveau)` de `include/DisplayConfig.h`, qui renvoie l'un ou l'autre selon la
cible. Le reste du code ne voit que `COL_RING`, `COL_BRIGHT`, etc.

Sur C6, la sprite est allouée **avant** le démarrage du WiFi : c'est le seul
moment où un bloc contigu de 103 Ko est disponible.

**2. Le CO5300 impose des fenêtres d'écriture alignées sur 2 pixels.** Le
driver `Panel_AMOLED` de LovyanGFX ignore *silencieusement* toute écriture dont
X ou la largeur est impair. Écrire du texte directement sur l'objet `tft` fait
donc disparaître des caractères au hasard. Solution retenue : **tout** passe par
la sprite plein écran, poussée en `(0, 0)` sur 410 px de large — X et largeur
pairs, contrainte toujours respectée. C'est pour ça que `WiFiManagerHelpers` et
les écrans de statut prennent un `LGFX_Sprite&` au lieu d'un `LGFX&`.

**3. `Panel_CO5300` de LovyanGFX est câblé pour la LilyGO T-Watch-Ultra**
(502×410, paysage). Sur les Waveshare, montées en portrait, il faut surcharger
`panel_width/height` et `memory_width/height` à 410×502 et poser
`offset_x = 22`. C'est fait dans `include/LGFX.h`.

### Géométrie à l'écran

Le radar est projeté dans un **carré** centré sur l'écran, paramétré par
`RADAR_SPAN` dans `include/DisplayConfig.h` :

* `RADAR_SPAN = SCREEN_H` (502, **défaut**) → radar plein écran, le cercle
  extérieur déborde à gauche et à droite ;
* `RADAR_SPAN = SCREEN_W` (410) → cercle entièrement visible, bandes noires de
  46 px en haut et en bas.

Les triangles d'avions, l'épaisseur du balayage et la taille du texte sont mis
à l'échelle via `UI_SCALE` (≈ 2,09).

### Fichiers modifiés / ajoutés

```
platformio.ini                 REECRIT   2 environnements S3 + C6 (pioarduino)
include/LGFX.h                 REECRIT   CO5300 QSPI + FT3168, brochage S3/C6
include/DisplayConfig.h        NOUVEAU   géométrie 410x502 + couleurs + alloc
include/DrawHelpers.h          MODIFIE   couleurs via G(), + ShowStatus()
include/WiFiManagerHelpers.h   MODIFIE   prend une LGFX_Sprite&
src/main.cpp                   MODIFIE   backbuffer plein écran, luminosité
src/AircraftManager.cpp        MODIFIE   projection + couleurs + échelle
src/AircraftManager.h          inchangé
src/ConfigurationWebServer.*   inchangé
src/HttpRequestManager.*       inchangé
src/OpenSkyAuthTokenHandler.*  inchangé
src/models/*                   inchangé
include/JsonParser.h           inchangé
```

### Empreinte mémoire mesurée

| Environnement | RAM statique | Flash |
|---|---|---|
| `esp32-s3-amoled-206` | 52 164 / 327 680 o (15,9 %) | 1 433 923 / 3 145 728 o (45,6 %) |
| `esp32-c6-amoled-206` | 49 348 / 327 680 o (15,1 %) | 1 445 500 / 3 145 728 o (46,0 %) |

`main.cpp` affiche le tas libre sur la console série après l'allocation du
backbuffer puis après la connexion WiFi — à surveiller au premier démarrage,
surtout sur C6 où il faut qu'il reste de quoi faire la poignée de main TLS vers
l'API OpenSky.

---

## 3. Mise en route

1. `pio run -e esp32-s3-amoled-206 -t upload`
2. Au premier boot, la carte crée un point d'accès **`MicroRadar-Setup`**
   (l'écran l'affiche). S'y connecter, choisir son réseau WiFi.
3. La carte redémarre. Ouvrir `http://<ip>/` (ou `http://microradar.local/`)
   pour saisir latitude, longitude, rayon et, optionnellement, les identifiants
   OpenSky.
4. Sans compte OpenSky : 400 requêtes/jour (≈ 1 rafraîchissement toutes les
   3,6 min). Avec un compte gratuit : 4000/jour (≈ 22 s).

### Réglages à ajuster éventuellement

| Fichier | Paramètre | Si… |
|---|---|---|
| `include/LGFX.h` | `cfg.freq_write = 40000000` | passer à `80000000` pour doubler la fluidité si l'affichage reste stable |
| `include/LGFX.h` | `MICRORADAR_USE_TOUCH` | mettre à `0` si le tactile perturbe le démarrage |
| `include/LGFX.h` | `cfg.offset_rotation` | image tournée ou en miroir → essayer 0…3 |
| `src/main.cpp` | `tft.setBrightness(200)` | 0…255, registre `0x51` du CO5300 |
| `include/DisplayConfig.h` | `RADAR_SPAN` | `SCREEN_W` pour un cercle entièrement visible |

### Pistes d'amélioration

* **Batterie** : l'AXP2101 n'est pas initialisé (inutile sur alimentation USB).
  Pour l'autonomie sur accu, ajouter `XPowersLib` et lire l'état de charge.
* **Tactile** : le FT3168 est configuré mais non exploité. `tft.getTouch(&x,&y)`
  permettrait de basculer l'affichage des textes ou de zoomer. Certaines
  révisions de la S3 embarquent un **CST9220** (adresse 0x5A) que LovyanGFX ne
  gère pas — dans ce cas le tactile reste simplement inactif.
* **IMU / RTC** : QMI8658 et PCF85063 sont sur le même bus I2C que le tactile —
  de quoi ajouter une rotation automatique ou une horloge.
* **Audio** : la S3 dispose d'un ES8311 + ES7210 et d'un lecteur SD, absents de
  la C6.
