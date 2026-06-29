<div align="center">

<img src="https://raw.githubusercontent.com/f1gbd/F1GBD/master/meshpacket/images/MeshPacket.png" alt="MeshPacket Pi" width="400">

# MeshPacket Pi

**Passerelle Packet pour MeshCore — édition Raspberry Pi 4B+/5 (64 bits) — ADRASEC 77 / FNRASEC**

MeshPacket Pi est le portage **Raspberry Pi (aarch64)** de MeshPacket. Il relie **deux réseaux radio MeshCore** (LoRa) à travers une **dorsale VHF Packet AX.25** : les messages d'un canal MeshCore d'un site sont encapsulés, transmis en VHF (1200 bauds AFSK via Direwolf, ou TNC KISS série/Bluetooth), puis réinjectés sur le réseau MeshCore du site distant — et inversement. C'est la même application que la version Windows, recompilée pour Raspberry Pi.

![Interface MeshPacket](https://raw.githubusercontent.com/f1gbd/F1GBD/master/meshpacket/images/MeshPacket_screen.png)

> Version courante : **v1.1.12** — Raspberry Pi OS 64 bits (Bookworm / Trixie), Pi 4B+ ou Pi 5.
### 📥 [**Télécharger la dernière version pour Raspberry Pi (aarch64)**](https://github.com/f1gbd/F1GBD/releases/download/meshpacket-pi-arm64-v1.1.12/MeshPacketPi-v1.1.12-aarch64.tar.gz)

*Archive autonome `.tar.gz` (PyInstaller, compilée sur le Pi) — aucune installation Python requise.*

</div>

---

## Principe

```
Réseau MeshCore A                                   Réseau MeshCore B
 (clients LoRa)                                       (clients LoRa)
      │                                                     │
   companion A ── USB ─────────┐                ┌────── USB ── companion B
                              │                │
                        ┌─────┴──────┐   ┌─────┴──────┐
                        │ MeshPacket │   │ MeshPacket │
                        │  Pi (A)    │   │  Pi (B)    │
                        └─────┬──────┘   └─────┬──────┘
                              │  VHF Packet AX.25 │
                          Direwolf / TNC ⇄ Direwolf / TNC
                              └───────  RF  ──────┘
```

Chaque passerelle est membre d'un **canal de routage MeshCore commun** (canal public ou canal privé dédié partagé, ex. `adrasec-xx`). Tout message posté sur ce canal est relayé vers l'autre réseau.

---

## Matériel requis

- **Raspberry Pi 4B+ ou Pi 5** sous **Raspberry Pi OS 64 bits**.
- Un **companion MeshCore** (nœud LoRa) connecté en **USB** (`/dev/ttyACM0` ou `/dev/ttyUSB0`).
- Selon le backend radio :
  - **Mode Direwolf** : une radio VHF + interface audio (carte son USB / câble data) + PTT, avec `direwolf` installé et un `direwolf.conf` valide ;
  - **Mode série / Bluetooth** : un **TNC KISS matériel** (ex. VGC VR-N76 en mode KISS-TNC, `/dev/rfcomm0` en Bluetooth ou `/dev/ttyUSB0` en série).

---

## Installation (depuis une release)

```bash
# 1. Extraction
tar xzf MeshPacketPi-v1.1.12-aarch64.tar.gz
cd MeshPacketPi-v1.1.12-aarch64

# 2. Configuration système (Direwolf, accès série, raccourci menu)
chmod +x install_pi.sh
./install_pi.sh
#   -> si vous avez été ajouté au groupe 'dialout', déconnectez/reconnectez la session.

# 3. Lancement
./meshpacket
```

L'archive est **autonome** : le binaire `meshpacket` et son dossier `_internal/` embarquent Python et Tkinter (aucune source, aucune dépendance Python à installer).

### Vérifier l'intégrité (SHA-256)

```bash
sha256sum -c MeshPacketPi-v1.1.12-aarch64.tar.gz.sha256
```

---

## Lancement et utilisation

- En ligne de commande : `./meshpacket` depuis le dossier extrait.
- Depuis le menu : raccourci **MeshPacket Pi** créé par `install_pi.sh` (catégorie *Ham Radio*).
- L'interface est identique à la version Windows : onglet **Connexion** (groupes *MeshCore (companion)*, *TNC / AX.25*, *Lien & fiabilité*) et onglet **Journal**. La configuration est enregistrée dans `meshpacket.json`, à côté du binaire.

Réglages de départ côté Pi :

- **MeshCore (companion)** : transport `serial`, port `/dev/ttyACM0`, débit `115200`, **Lecture active (get_msg)** cochée.
- **TNC / AX.25** : mode `direwolf` avec **Chemin Direwolf** = `direwolf` (binaire du PATH) et, si besoin, **Config Direwolf** = chemin de votre `direwolf.conf` ; ou mode `serial` avec **Port série / BT** = `/dev/rfcomm0` (ou `/dev/ttyUSB0`).
- **Lien & fiabilité** : **Indicatif local** = cette passerelle, **Indicatif pair** = celle d'en face ; **Accusé applicatif (ACK)** pour un lien à deux passerelles.

Pour le **paramétrage détaillé** et la **création d'un canal privé `adrasec-xx`** (synchronisation de clé par QR / import d'URL `meshcore://channel/add`), voir le **Manuel Utilisateur** commun (l'interface est identique à la version Windows).

---

## Dépannage (spécifique Pi)

- **`/dev/ttyACM0` : permission refusée** → vous n'êtes pas dans le groupe `dialout`. Lancez `./install_pi.sh` puis déconnectez/reconnectez la session (ou `sudo usermod -aG dialout $USER`).
- **Direwolf ne démarre pas** → installez-le (`sudo apt install direwolf`) ; vérifiez **Chemin Direwolf** = `direwolf` et renseignez **Config Direwolf** avec le chemin complet de votre `direwolf.conf`. En mode TNC série/BT, décochez **Lancer Direwolf**.
- **Companion non détecté** → vérifiez le port avec `ls /dev/ttyACM* /dev/ttyUSB*` et ajustez **Port**.
- **TNC Bluetooth** → appairez la radio puis liez le port : `sudo rfcomm bind /dev/rfcomm0 <MAC> 1`, et utilisez `/dev/rfcomm0`.

---

## Compiler soi-même sur le Pi

Le kit source (`MeshPacketPi-srckit-v1.1.12.tar.gz`) contient tout le nécessaire. Le script `build_pi.sh` crée un environnement virtuel, installe les dépendances et produit l'archive `MeshPacketPi-v<version>-aarch64.tar.gz` via PyInstaller.

```bash
tar xzf MeshPacketPi-srckit-v1.1.12.tar.gz
cd MeshPacketPi-srckit
chmod +x build_pi.sh && ./build_pi.sh
```

Détails dans **[README_PI4.md](README_PI4.md)**.

---

## 📄 Documentation associée

- 📘 **[Manuel utilisateur MeshPacket](https://github.com/f1gbd/F1GBD/blob/master/meshpacket/documentation/MEMO%20-%20MANUEL%20MeshPacket.pdf)** — Manuel Utilisateur et Paramétrage (interface commune Windows / Pi).
- 📋 **[Fiche de présentation MeshPacket](https://github.com/f1gbd/F1GBD/blob/master/meshpacket/documentation/MEMO%20-%20Fiche%20Technique%20MeshPacket.pdf)** — Fiche Technique.

---

<div align="center">

### 📡 Auteur

**Jean-Louis Naudin (F1GBD)**
*ADRASEC 77 — FNRASEC*

**MeshPacket Pi — Version 1.1.12 — Juin 2026**

---

*Pour toute question, contactez votre référent ADRASEC départemental.*

</div>
