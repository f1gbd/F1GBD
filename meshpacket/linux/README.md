<div align="center">

<img src="https://raw.githubusercontent.com/f1gbd/F1GBD/master/meshpacket/images/MeshPacket.png" alt="MeshPacket Linux" width="400">

# MeshPacket Linux

**Passerelle Packet pour MeshCore — édition Linux (Ubuntu 24.04, x86_64) — ADRASEC 77 / FNRASEC**

MeshPacket Linux est l'édition **Linux 64 bits (x86_64)** de MeshPacket. Elle relie **deux réseaux radio MeshCore** (LoRa) à travers une **dorsale VHF Packet AX.25** : les messages d'un canal MeshCore d'un site sont encapsulés, transmis en VHF (1200 bauds AFSK via Direwolf, ou TNC KISS série/Bluetooth), puis réinjectés sur le réseau MeshCore du site distant — et inversement. C'est la même application que la version Windows, recompilée pour Linux.

![Interface MeshPacket](https://raw.githubusercontent.com/f1gbd/F1GBD/master/meshpacket/images/MeshPacket_screen.png)

> Version courante : **v1.1.12** — Ubuntu 24.04 LTS (x86_64).
### 📥 [**Télécharger la dernière version pour Linux (Ubuntu 24.04, x86_64)**](https://github.com/f1gbd/F1GBD/releases/download/meshpacket-linux-v1.1.12/MeshPacketLinux-1.1.12-linux-x86_64.tar.gz)

*Archive autonome `.tar.gz` (PyInstaller) — aucune installation Python requise.*

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
                        │ Linux (A)  │   │ Linux (B)  │
                        └─────┬──────┘   └─────┬──────┘
                              │  VHF Packet AX.25 │
                          Direwolf / TNC ⇄ Direwolf / TNC
                              └───────  RF  ──────┘
```

Chaque passerelle est membre d'un **canal de routage MeshCore commun** (canal public ou canal privé dédié partagé, ex. `adrasec-xx`). Tout message posté sur ce canal est relayé vers l'autre réseau.

---

## Matériel requis

- Un PC **Ubuntu 24.04 LTS (x86_64)**.
- Un **companion MeshCore** (nœud LoRa) connecté en **USB** (`/dev/ttyACM0` ou `/dev/ttyUSB0`).
- Selon le backend radio :
  - **Mode Direwolf** : une radio VHF + interface audio (carte son USB / câble data) + PTT, avec `direwolf` installé et un `direwolf.conf` valide ;
  - **Mode série / Bluetooth** : un **TNC KISS matériel** (ex. VGC VR-N76 en mode KISS-TNC, `/dev/rfcomm0` en Bluetooth ou `/dev/ttyUSB0` en série).

---

## Installation (depuis une release)

```bash
# Téléchargement de l'archive et de sa somme de contrôle
wget https://github.com/f1gbd/F1GBD/releases/download/meshpacket-linux-v1.1.12/MeshPacketLinux-1.1.12-linux-x86_64.tar.gz
wget https://github.com/f1gbd/F1GBD/releases/download/meshpacket-linux-v1.1.12/MeshPacketLinux-1.1.12-linux-x86_64.tar.gz.sha256

# Vérification de l'intégrité (recommandée)
sha256sum -c MeshPacketLinux-1.1.12-linux-x86_64.tar.gz.sha256
# Doit afficher : MeshPacketLinux-1.1.12-linux-x86_64.tar.gz.sha256: OK

# 1. Extraction
tar xzf MeshPacketLinux-1.1.12-linux-x86_64.tar.gz
cd MeshPacketLinux-1.1.12-linux-x86_64

# 2. Configuration système (Direwolf, accès série, raccourci menu)
chmod +x install_linux.sh
./install_linux.sh
#   -> si vous avez été ajouté au groupe 'dialout', déconnectez/reconnectez la session.

# 3. Lancement
./meshpacket
```

L'archive est **autonome** : le binaire `meshpacket` et son dossier `_internal/` embarquent Python et Tkinter (aucune source applicative, aucune dépendance Python à installer).

### Vérifier l'intégrité (SHA-256)

```bash
sha256sum -c MeshPacketLinux-1.1.12-linux-x86_64.tar.gz.sha256
```

---

## Configuration de Direwolf (audio + PTT)

Sur Linux, Direwolf a besoin d'un `direwolf.conf` pointant la bonne carte son. Un modèle est fourni (`direwolf.conf.sample`).

```bash
# repérer la carte son USB (souvent PAS la carte 0)
aplay -l ; arecord -l

# créer la config (adapter le numéro de carte, ex. card 3 -> plughw:3,0)
cp direwolf.conf.sample ~/direwolf.conf
nano ~/direwolf.conf      # ADEVICE, MYCALL, PTT

# tester Direwolf seul : on doit voir « Ready to accept KISS client … on port 8001 »
direwolf -c ~/direwolf.conf
```

Dans MeshPacket : **TNC / AX.25 → Config Direwolf** = `/home/<vous>/direwolf.conf`. Au démarrage, MeshPacket lance Direwolf automatiquement et journalise sa sortie dans `~/direwolf-meshpacket.log`.

---

## Lancement et utilisation

- En ligne de commande : `./meshpacket` depuis le dossier extrait.
- Depuis le menu : raccourci **MeshPacket Linux** créé par `install_linux.sh`.
- L'interface est identique à la version Windows : onglet **Connexion** (groupes *MeshCore (companion)*, *TNC / AX.25*, *Lien & fiabilité*) et onglet **Journal**. La configuration est enregistrée dans `meshpacket.json`, à côté du binaire.

Pour le **paramétrage détaillé** et la **création d'un canal privé `adrasec-xx`** (synchronisation de clé par QR / import d'URL `meshcore://channel/add`), voir le **Manuel Utilisateur** commun (interface identique).

---

## Dépannage

- **`/dev/ttyACM0` : permission refusée** → groupe `dialout` manquant : `./install_linux.sh` puis reconnexion (ou `sudo usermod -aG dialout $USER`).
- **`Connect call failed ('127.0.0.1', 8001)`** → Direwolf n'a pas ouvert KISS : mauvais `ADEVICE`. Lancez `direwolf -c ~/direwolf.conf` et corrigez la carte son (`aplay -l`).
- **Direwolf introuvable** → `sudo apt install direwolf`.
- **Companion non détecté** → `ls /dev/ttyACM* /dev/ttyUSB*` puis ajustez **Port**.

---

## Licence & auteur

**MeshPacket Linux** — *a Packet Gateway for MeshCore* — par **F1GBD** (c) 2026 — **ADRASEC 77 / FNRASEC**.
