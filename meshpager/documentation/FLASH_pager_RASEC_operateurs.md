# PAGER RASEC ALERT — Flashage du firmware (Heltec V3)

Firmware pr\u00eat \u00e0 flasher pour transformer une **Heltec WiFi LoRa 32 V3** en pager
d'alerte ADRASEC. Aucun outil de compilation n'est n\u00e9cessaire : un seul fichier
binaire \u00e0 \u00e9crire.

Fichier : `pager_rasec_heltecv3.bin` (binaire fusionn\u00e9, adresse `0x0`)

---

## M\u00e9thode 1 \u2014 Flasheur web (recommand\u00e9, sans installation)

Navigateur **Chrome** ou **Edge** (Web Serial requis ; Firefox/Safari non support\u00e9s).

1. Brancher la Heltec V3 en USB.
2. Ouvrir le flasheur Espressif : **https://espressif.github.io/esptool-js/**
3. Cliquer **Connect**, choisir le port s\u00e9rie de la carte (CP2102 / USB-Serial).
4. Dans la ligne de fichier : **Address** = `0x0`, **Choose File** = `pager_rasec_heltecv3.bin`.
5. Cliquer **Program**. Attendre la fin (\u00abProgramming\u2026\u00bb \u2192 100 %).
6. Appuyer sur **RST** sur la carte. Le pager d\u00e9marre.

> Si la connexion \u00e9choue : maintenir **BOOT**, appuyer/rel\u00e2cher **RST**, rel\u00e2cher **BOOT**, puis **Connect** \u00e0 nouveau.

## M\u00e9thode 2 \u2014 esptool en ligne de commande

Pr\u00e9requis : Python + `pip install esptool`.

```bash
esptool.py --chip esp32s3 --port COM3 --baud 921600 write_flash 0x0 pager_rasec_heltecv3.bin
```

(remplacer `COM3` par le port r\u00e9el ; sous Linux `/dev/ttyUSB0` ou `/dev/ttyACM0`.)

---

## V\u00e9rification apr\u00e8s flashage

Au d\u00e9marrage : logo MeshCore (~3 s) puis la page d'accueil pager. R\u00e9veiller
l'\u00e9cran avec le bouton **USER** si besoin. La 1re page affiche :

```
RASEC ALERT
by F1GBD
Alertes: 0
```

Appairage \u00e0 l'application MeshCore : code PIN affich\u00e9 \u00e0 l'\u00e9cran (ou d\u00e9fini au build).

---

## Pour le mainteneur \u2014 cr\u00e9er le binaire fusionn\u00e9

Depuis le dossier de build PlatformIO :

```bash
cd .pio/build/Heltec_v3_pager_adrasec

esptool.py --chip esp32s3 merge_bin -o pager_rasec_heltecv3.bin --flash_size 8MB \
  0x0     bootloader.bin \
  0x8000  partitions.bin \
  0xe000  boot_app0.bin \
  0x10000 firmware.bin
```

`boot_app0.bin` se trouve dans les paquets du framework, par ex. (Windows) :
`C:\Users\<user>\.platformio\packages\framework-arduinoespressif32\tools\partitions\boot_app0.bin`

Le fichier `pager_rasec_heltecv3.bin` obtenu est celui \u00e0 publier et \u00e0 flasher \u00e0 `0x0`.
