# MeshFederator — CHANGELOG

## v1.0.1 — Octobre 2026

Prise en charge du **Heltec WiFi LoRa 32 V3** (8 Mo de flash, USB CP2102), au même titre que le V4.

- **MeshFederator** : libellés V3/V4, assistant Ports série (CP2102 = V3). La passerelle elle-même est indépendante du modèle.
- **MeshFederator Setup** : variante « Heltec V3 », téléchargement Meshtastic `heltec-v3` et MeshCore `Heltec_v3_companion_radio_usb`, reconnaissance des fichiers V3 dans la bibliothèque, alerte si la variante choisie ne correspond pas au module branché, sauvegarde de la flash à la taille réelle (8 Mo V3 / 16 Mo V4).
- **Programme d'installation Windows** (Inno Setup 6) : `MeshFederator-<version>-setup.exe`, installation par utilisateur sans droits administrateur, page de licence GNU GPL, raccourcis (passerelle, Setup, flasheur web, bibliothèque de firmwares), configuration et sauvegardes conservées à la mise à jour comme à la désinstallation. Script `Build-MeshFederator.ps1 -Archive -Installeur`.
- **Bibliothèque de firmwares Heltec V3 et V4 incluse** (Meshtastic 2.7.26 Beta + MeshCore companion USB 1.17.1) dans l'installeur et l'archive.
- **À propos → Vérifier les mises à jour** dans les deux applications : releases GitHub `meshfederator-v*` (API puis flux Atom), téléchargement de l'installeur avec **contrôle SHA-256**, lancement puis fermeture de l'application.
- **Publication** : l'archive .7z et l'installeur sont publiés ensemble, avec leurs deux empreintes SHA-256.
- **Flasheur web** : variante V3 ; adresses OTA/LittleFS Meshtastic propres à chaque variante (V3 `0x340000`/`0x670000`, V4 `0x650000`/`0xC90000`) ou lues dans le manifeste `.mt.json` (fichier local ou archive) ; refus d'un fichier d'une autre variante.

## v1.0.0 — Octobre 2026

Version initiale.

### MeshFederator (passerelle)
- Pont bidirectionnel **Meshtastic ⇄ MeshCore** sur deux Heltec LoRa V4 (firmwares officiels).
- Routes de canaux par index ou par nom, bidirectionnelles ou à sens unique (`0<>0`, `1>2`, `3<1`).
- Étiquettes `[MT]` / `[MC]` / `[FED]` et refus de re-fédérer un message étiqueté (anti-boucle multi-passerelles).
- Anti-écho local, déduplication des réceptions, exclusion du trafic Meshtastic via MQTT.
- Relais DM `@nom texte` d'un réseau à l'autre ; réponse sans `@` vers le dernier correspondant.
- Commandes `#h` `#v` `#s` `#n` `#p`.
- Découpage `[i/n]` selon la charge utile de chaque réseau.
- Cadencement d'émission par réseau, plafond de messages par minute, file bornée.
- Reconnexion automatique des deux radios.
- Interface Tkinter : Connexion, Trafic, Nœuds, Journal ; assistant Ports série ; vérification des mises à jour.
- Mode console (`--nogui`), `--list-ports`, `--gen-config`, `--selftest`.

### MeshFederator Setup
- Bibliothèque de firmwares hors ligne (Meshtastic factory + OTA + LittleFS, MeshCore companion USB).
- Téléchargement des dernières versions officielles (extraction sélective HTTP Range pour Meshtastic).
- Flashage esptool embarqué, effacement, sauvegarde de la flash, identification de la puce.
- Paramétrage Meshtastic (propriétaire, région, preset, puissance, rôle, canaux, URL).
- Paramétrage MeshCore (nom, radio, puissance, canaux, URL de partage, annonce).
- Export `firmware/index.json` pour le flasheur web.

### Flasheur web
- Page Web Serial (esptool-js) : firmware hébergé ou fichier local (y compris archive `firmware-esp32s3-*.zip`).
