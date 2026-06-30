<div align="center">

<img src="https://raw.githubusercontent.com/f1gbd/F1GBD/master/meshrns/images/MeshRNS.png" alt="MeshRNS Pi" width="400">

# MeshRNS Pi

**Passerelle Reticulum / LXMF pour MeshCore — édition Raspberry Pi 4B+/5 (aarch64)**

### *« Un pont, deux Univers Mesh, aucune frontière. »*

*Là où le LoRa s'arrête, le maillage Reticulum prend le relais.*

</div>

MeshRNS Pi est le portage **Raspberry Pi (aarch64)** de MeshRNS. Il relie un **réseau radio MeshCore** (LoRa) au **réseau maillé Reticulum** via **LXMF** (la même pile que TCQ), et ne dialogue **qu'avec les stations `TCQ-xxxx`** du réseau. Les messages d'un canal MeshCore sont transportés en LXMF vers les stations TCQ joignables par Reticulum (RF longue distance, LoRa, TCP/IP, I2P…), et les messages LXMF reçus des stations TCQ sont réinjectés sur le réseau MeshCore local. **C'est la même application que la version Windows, recompilée pour Raspberry Pi** (interface, configuration et fichiers identiques).

<div align="center">
<img src="https://raw.githubusercontent.com/f1gbd/F1GBD/master/meshrns/images/MeshRNS_principle.png" alt="MeshRNS — du réseau MeshCore (LoRa, LXMF) au réseau Reticulum des stations TCQ" width="760">
</div>

> Version courante : **v1.0.8** — Raspberry Pi OS 64 bits (Bookworm/Trixie), Pi 4B+ ou Pi 5.

> Contrairement à MeshPacket, MeshRNS n'utilise **ni Direwolf ni AX.25** : sa dorsale est **Reticulum/LXMF**.

---

## Matériel requis

- **Raspberry Pi 4B+ ou Pi 5** sous **Raspberry Pi OS 64 bits** (`uname -m` → `aarch64`).
- Un **companion MeshCore** (nœud LoRa) connecté en **USB** (apparaît en `/dev/ttyACM0` ou `/dev/ttyUSB0`) — ou en **TCP**, ou en **Bluetooth (BLE)**.
- Un **accès au réseau Reticulum** atteignant vos stations TCQ : au moins une **interface RNS** déclarée dans `~/.reticulum/config` (RNode LoRa, TCPClientInterface vers un nœud RNS, AutoInterface, I2P…).

---

## Installation (depuis une release)

### 📥 Télécharger la dernière version Raspberry Pi (aarch64)

`https://github.com/f1gbd/F1GBD/releases` → tag **`meshrns-pi-arm64-v1.0.8`**, fichier **`MeshRNSPi-v1.0.8-aarch64.tar.gz`**.

```bash
# 1. Extraction
tar xzf MeshRNSPi-v1.0.8-aarch64.tar.gz
cd MeshRNSPi-v1.0.8-aarch64

# 2. Configuration système (accès série, Bluetooth optionnel, raccourci menu)
chmod +x install_pi.sh
./install_pi.sh
#   -> si le script vous a ajouté au groupe 'dialout', déconnectez/reconnectez la session.

# 3. Lancement
./MeshRNS
```

L'archive est **autonome** : le binaire `MeshRNS` et son dossier `_internal/` embarquent Python, Tkinter et la pile **Reticulum/LXMF** (aucune source, aucune dépendance Python à installer). La configuration (`meshrns.json`) et l'annuaire (`annuaire.json`) sont créés/maintenus **à côté du binaire** — placez le dossier dans un emplacement **inscriptible** (votre home, pas un dossier système).

### Vérifier l'intégrité (SHA-256)

```bash
sha256sum -c MeshRNSPi-v1.0.8-aarch64.tar.gz.sha256
```

---

## Configuration Reticulum (important)

MeshRNS lit la configuration RNS du poste, **`~/.reticulum/config`** :

- **1ᵉʳ lancement sur machine vierge** (dossier `~/.reticulum` absent) : MeshRNS y installe une **configuration par défaut** (`reticulum_config/config`), **à adapter** à votre réseau ADRASEC.
- **Profil existant** : MeshRNS **n'y touche jamais**. Placez votre `~/.reticulum/config` (l'interface qui joint vos stations TCQ).
- État des interfaces : **`rnstatus`** (si le paquet `rns` est installé sur le système), ou la ligne **`Diagnostic Reticulum : … interfaces connectees=N/M …`** dans le **Journal** de MeshRNS au démarrage.

MeshRNS possède sa **propre identité LXMF** (dossier `~/.meshrns`), distincte de TCQ : son adresse LXMF est stable et propre à la passerelle.

> Tant qu'aucune annonce de station **TCQ** n'apparaît dans le Journal (sans le tag `[hors filtre TCQ]`), la passerelle n'est **pas** sur le même réseau Reticulum que vos stations.

---

## Démarrage rapide

1. **Préparez `~/.reticulum/config`** (interface RNode LoRa / TCP qui joint le réseau TCQ).
2. Lancez `./MeshRNS` (ou le raccourci **MeshRNS Pi** du menu). L'onglet **Connexion** présente trois groupes.
3. **MeshCore (companion)** : **Transport** `serial`, **Port** `/dev/ttyACM0`, **Baudrate** `115200`, **Lecture active (get_msg)** cochée.
4. **LXMF / Reticulum** : **Station LXMF** = un indicatif **`TCQ-*`** (ex. `TCQ-F1GBD/77`). **Config RNS** vide (= `~/.reticulum/config`).
5. **Lien & filtrage TCQ** : **Indicatif local**, **Mode d'émission** (`broadcast` ou `direct`), **Canal de service** `tcq`, **Filtrer entrant (TCQ seul)** coché.
6. Au besoin, **Canaux…** pour créer le canal `tcq` sur le companion (même **clé** que les stations du réseau).
7. **▶ Démarrer** → voyant **● En service**. Suivez l'onglet **Journal** et **Annuaire…**.

> Le port companion par défaut est déjà **`/dev/ttyACM0`** sur Raspberry Pi (et `COM4` sur Windows) : un `meshrns.json` neuf démarre directement sur le bon port.

---

## Fonctionnalités (rappel)

L'édition Pi est **fonctionnellement identique** à la version Windows :

- **Dorsale Reticulum / LXMF** — transport applicatif LXMF par-dessus Reticulum (RF, LoRa RNode, TCP/IP, I2P…), adressage de bout en bout et chiffrement natif.
- **Filtrage `TCQ-*`** et **annuaire** persistant (`annuaire.json`, format TCQ), avec **import d'annuaire** et consultation depuis le canal MeshCore `tcq` (`ANNUAIRE`, `DIR`, `LIST`, `?`…).
- **Deux modes d'émission** : `broadcast` (toutes les stations TCQ fraîches) et `direct` (une station), plus la **surcharge `@<nom|hash> texte`** (ciblage exact ; un nom qualifié comme `@TCQ-F8KSM/77` n'est jamais détourné vers une variante plus longue).
- **Signature** des messages relayés, **réinjection LXMF → MeshCore** avec déduplication et anti-écho, **confirmation de livraison** journalisée (`Livraison LXMF confirmee`).
- **Gestion des canaux** du companion (création/clé, **QR de partage**, import d'URL `meshcore://channel/add`).
- **Arrêt fiable** (port libéré au besoin de force) et **config Reticulum par défaut** installée au 1ᵉʳ lancement si absente.

> Pour le détail exhaustif (tableau `meshrns.json`, canal `tcq`, dépannage complet), voir le **[README principal MeshRNS](https://github.com/f1gbd/F1GBD/tree/master/meshrns)** et les fiches PDF — identiques, l'interface étant la même.

---

## Dépannage (spécifique Pi)

- **`/dev/ttyACM0` : permission refusée** → vous n'êtes pas dans le groupe `dialout`. Lancez `./install_pi.sh` puis déconnectez/reconnectez la session (ou `sudo usermod -aG dialout $USER`).
- **Companion non détecté** → `ls /dev/ttyACM* /dev/ttyUSB*` et ajustez **Port**.
- **`interfaces connectees=0`** (Journal) → la config Reticulum ne joint pas votre réseau : éditez `~/.reticulum/config` (RNode LoRa / TCP). Diagnostiquez avec `rnstatus`.
- **`Pas de chemin RNS vers …`** → la station cible n'est pas joignable sur le réseau Reticulum actuel (hors ligne, ou autre réseau). La ligne `Livraison LXMF confirmee` atteste d'une remise effective.
- **Companion Bluetooth (BLE)** → `./install_pi.sh` installe `bluez` ; appairez le companion, choisissez transport `ble`. *(Le binaire doit avoir été compilé avec le support BLE : bloc `bleak` décommenté dans `MeshRNS.spec`.)*
- **Annuaire vide après redémarrage** → placez le dossier de l'appli dans un emplacement **inscriptible** (home), pour que `annuaire.json` persiste.

---

## 📄 Documentation associée

- 📘 **[Manuel utilisateur MeshRNS](https://github.com/f1gbd/F1GBD/blob/master/meshrns/documentation/MEMO%20-%20MANUEL%20MeshRNS.pdf)**
- 📋 **[Fiche technique MeshRNS](https://github.com/f1gbd/F1GBD/blob/master/meshrns/documentation/MEMO%20-%20Fiche%20Technique%20MeshRNS.pdf)**

---

## Licence & auteur

**MeshRNS Pi** — *a Reticulum/LXMF Gateway for MeshCore* — par **F1GBD** (c) 2026 — **ADRASEC 77 / FNRASEC**.

<div align="center">

### 📡 Auteur

**Jean-Louis Naudin (F1GBD)**
*ADRASEC 77 — FNRASEC*

**MeshRNS Pi — Version 1.0.8 — Juin 2026**

</div>
