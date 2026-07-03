# MeshPager — PAGER RASEC ALERT (MeshCore / Heltec V3)

Transforme un module **Heltec WiFi LoRa 32 V3** (firmware companion BLE MeshCore v1.16)
en **pager d'alerte** pour la chaîne ADRASEC. À réception d'une commande d'activation
envoyée en chat (depuis TCQ ou une application cliente MeshCore), le pager signale
l'alerte de façon **visuelle et sonore** et confirme la bonne réception à l'émetteur.

> Projet **ADRASEC 77 / FNRASEC** — F1GBD / F4JHW. Usage exercices et opérations SATER / ORSEC.

---

## Fonctionnement

À réception de la commande **`#ra <code>`** (message direct ou canal) :

- **Écran OLED** : affichage plein écran « RASEC ALERT ».
- **LED blanche** : clignotement rapide par **séries de 3 impulsions**.
- **Buzzer** (optionnel, si câblé) : 3 bips.
- **Accusé de réception** : renvoyé automatiquement à l'émetteur (message direct).
- **Écran d'accueil** dédié : titre, signature et **compteur d'alertes reçues**.

<p align="center">
  <img src="oled_pager.png" width="360" alt="Écran d'accueil du pager"/>
  &nbsp;&nbsp;
  <img src="oled_alert.png" width="360" alt="Alerte RASEC affichée"/>
</p>

---

## Matériel

- **Heltec WiFi LoRa 32 V3** (ESP32-S3, écran OLED 0,96", LED blanche, bouton USER).
- Câble USB-C.
- (Optionnel) buzzer + module relais pour les variantes sonore / TOR.

---

## Flashage (opérateurs)

Fichier à flasher : **`pager_rasec_heltecv3.bin`** (binaire fusionné, adresse `0x0`).

### ⚡ Flashage en un clic (le plus simple)

➡️ **[Installer le firmware Pager](https://f1gbd.github.io/F1GBD/meshpager/)** (Chrome ou Edge)

Un bouton « Installer le firmware Pager » détecte la carte et flashe automatiquement.
(Nécessite l'activation de GitHub Pages sur le dépôt.)

### Méthode 1 — Flasheur web générique (sans installation)

Navigateur **Chrome** ou **Edge** (Web Serial requis).

1. Brancher la Heltec V3 en USB.
2. Ouvrir **https://espressif.github.io/esptool-js/**
3. **Connect** → choisir le port série de la carte.
4. Adresse `0x0`, fichier `pager_rasec_heltecv3.bin`, puis **Program**.
5. Appuyer sur **RST**. Le pager démarre.

> Connexion impossible ? Maintenir **BOOT**, appuyer/relâcher **RST**, relâcher **BOOT**, puis reconnecter.

### Méthode 2 — esptool (ligne de commande)

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

- 📄 **Fiche réflexe** (envoyer / tester l'alerte) : [`Fiche_reflexe_RASEC_ALERT.docx`](Fiche_reflexe_RASEC_ALERT.docx)
- 📘 **Fiche technique** (mise en œuvre complète) : [`Fiche_PAGER_RASEC_ALERT_ADRASEC.docx`](Fiche_PAGER_RASEC_ALERT_ADRASEC.docx)
- 🔧 **Procédure de flashage** : [`FLASH_pager_RASEC_operateurs.md`](FLASH_pager_RASEC_operateurs.md)

---

## Compiler depuis les sources

Le firmware est le **companion BLE** de [MeshCore](https://github.com/meshcore-dev/MeshCore)
v1.16, modifié par un patch (écran + LED + buzzer + accusé + écran d'accueil + activation `#ra`).

1. Cloner MeshCore, appliquer le patch depuis la racine :
   ```bash
   git apply meshcore-companion-pager-rasec-f1gbd-v3.1.patch
   ```
2. Ajouter un environnement dérivé dans `platformio.local.ini` :
   ```ini
   [env:Heltec_v3_pager_adrasec]
   extends = env:Heltec_v3_companion_radio_ble
   build_flags =
     ${env:Heltec_v3_companion_radio_ble.build_flags}
     -D PAGER_HOME=1
     -D PAGER_ACTIVATION_CODE='"ADRASEC77"'
   ```
3. Compiler / flasher :
   ```bash
   pio run -e Heltec_v3_pager_adrasec -t upload
   ```

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

**Jean-Louis Naudin — F1GBD / F4JHW**, ADRASEC 77.
Basé sur MeshCore (voir la licence du projet MeshCore pour le firmware de base).

73 !
