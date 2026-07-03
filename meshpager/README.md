# MeshPager — PAGER RASEC ALERT (MeshCore / Heltec V3)

Transforme un module **Heltec WiFi LoRa 32 V3** (firmware companion BLE MeshCore v1.16)
en **pager d'alerte** pour la chaîne ADRASEC. À réception d'une commande d'activation
envoyée en chat (depuis TCQ ou une application cliente MeshCore), le pager signale
l'alerte de façon **visuelle et sonore** et confirme la bonne réception à l'émetteur.

> Projet **ADRASEC 77 / FNRASEC** — F1GBD / F4JHW. Usage exercices et opérations SATER / ORSEC.

<p align="center">
  <img src="images/Rasec-Alert_logo.jpg" width="560" alt="RASEC ALERT"/>
</p>

---

## Fonctionnement

À réception de la commande **`#ra <code>`** (message direct ou canal) :

- **Écran OLED** : affichage plein écran « RASEC ALERT ».
- **LED blanche** : clignotement rapide par **séries de 3 impulsions**.
- **Buzzer** (optionnel, si câblé) : 3 bips.
- **Accusé de réception** : renvoyé automatiquement à l'émetteur (message direct).
- **Écran d'accueil** dédié : titre, signature et **compteur d'alertes reçues**.

<p align="center">
  <img src="images/rasec_pager.gif" width="440" alt="Pager recevant l'alerte RASEC en direct"/>
</p>
<p align="center">
  <img src="images/raserc_pager.jpeg" width="440" alt="Pager Heltec V3 affichant RASEC ALERT"/>
</p>

<p align="center"><em>Réception d'une alerte « RASEC ALERT » sur un pager Heltec V3.</em></p>

---

## Matériel

- **Heltec WiFi LoRa 32 V3** (ESP32-S3, écran OLED 0,96", LED blanche, bouton USER).
- Câble USB-C.
- (Optionnel) buzzer + module relais pour les variantes sonore / TOR.

---

## Flashage (opérateurs)

### ⚡ Méthode 1 — Bouton « Install » en un clic (recommandé)

➡️ **[Installer le firmware Pager](https://f1gbd.github.io/F1GBD/meshpager/)**  (Chrome ou Edge)

Brancher la Heltec V3 en USB, cliquer **Installer le firmware Pager**, choisir le
port série, laisser flasher, puis **RST**. Le binaire est servi par GitHub Pages
(même origine), donc le flashage web fonctionne directement.

> Connexion impossible ? Maintenir **BOOT**, appuyer/relâcher **RST**, relâcher **BOOT**, puis réessayer.

### Méthode 2 — Télécharger le binaire et flasher

1. Télécharger **[`pager_rasec_heltecv3.bin`](https://github.com/f1gbd/F1GBD/releases/latest/download/pager_rasec_heltecv3.bin)** (dernière release).
2. Ouvrir **https://espressif.github.io/esptool-js/** (Chrome/Edge), **Connect**, fichier à l'adresse `0x0`, **Program**.

### Méthode 3 — esptool (ligne de commande)

```bash
pip install esptool
esptool.py --chip esp32s3 --port COM3 --baud 921600 write_flash 0x0 pager_rasec_heltecv3.bin
```

Détails et création du binaire fusionné : voir [`FLASH_pager_RASEC_operateurs.md`](FLASH_pager_RASEC_operateurs.md).

---

## Utilisation

Depuis TCQ ou une application cliente MeshCore, envoyer au pager (message direct
recommandé, ou canal commun) :

```
#ra ADRASEC77
```

- Le préfixe `#ra` doit être en début de message, suivi d'un espace puis du **code exact** (casse respectée).
- Un code erroné ne déclenche rien.
- En message direct, l'émetteur reçoit l'accusé « Pager OK - alerte bien recue ».

Le code d'activation par défaut est `ADRASEC77` ; il se personnalise au build
(`-D PAGER_ACTIVATION_CODE`).

---

## Documentation

- 📄 **Fiche réflexe** (envoyer / tester l'alerte) : [`Fiche_reflexe_RASEC_ALERT.docx`](https://github.com/f1gbd/F1GBD/blob/master/meshpager/documentation/Fiche_reflexe_RASEC_ALERT.pdf)
- 📘 **Fiche technique** (mise en œuvre complète) : [`Fiche_PAGER_RASEC_ALERT_ADRASEC.docx`](https://github.com/f1gbd/F1GBD/blob/master/meshpager/documentation/Fiche_PAGER_RASEC_ALERT_ADRASEC.pdf)

---

Options (buzzer, textes, durées) : voir la fiche technique.

### Principaux paramètres (`build_flags`)

| Flag | Défaut | Rôle |
|---|---|---|
| `PAGER_ACTIVATION_CODE` | `ADRASEC77` | Code attendu après `#ra` |
| `PAGER_ALERT_MS` | `6000` | Durée de l'alerte (écran + LED), ms |
| `PAGER_HOME` | (non défini) | Active l'écran d'accueil pager |
| `PIN_BUZZER` | (non défini) | Broche du buzzer (active le bip) |
| `PAGER_ALSO_MATCH_TEXT` | (non défini) | Accepte aussi le texte brut « RASEC ALERT » |

---

## Auteur & licence

**Jean-Louis — F1GBD**, ADRASEC 77.
Basé sur MeshCore (voir la licence du projet MeshCore pour le firmware de base).

73 !
