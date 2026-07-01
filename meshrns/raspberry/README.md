<div align="center">

<img src="https://raw.githubusercontent.com/f1gbd/F1GBD/master/meshrns/images/MeshRNS.png" alt="MeshRNS" width="400">

# MeshRNS — édition Linux

**Passerelle Reticulum / LXMF pour MeshCore — Raspberry Pi (aarch64) & PC/serveur Linux (x86-64)**

### *« Un pont, deux réseaux, aucune frontière. »*

*Là où le LoRa s'arrête, le maillage Reticulum prend le relais.*

</div>

MeshRNS relie un **réseau radio MeshCore** (LoRa) au **réseau maillé Reticulum** via **LXMF** (la même pile que TCQ), et ne dialogue **qu'avec les stations `TCQ-xxxx`** du réseau. Les messages d'un canal MeshCore sont transportés en LXMF vers les stations TCQ joignables par Reticulum (RF longue distance, LoRa, TCP/IP, I2P…), et les messages LXMF reçus des stations TCQ sont réinjectés sur le réseau MeshCore local. **C'est la même application que la version Windows, livrée en binaire natif pour Raspberry Pi et Linux x86-64** (interface, configuration et fichiers identiques).

<div align="center">
<img src="https://raw.githubusercontent.com/f1gbd/F1GBD/master/meshrns/images/MeshRNS_principle.png" alt="MeshRNS — du réseau MeshCore (LoRa, LXMF) au réseau Reticulum des stations TCQ" width="760">
</div>

> Version courante : **v2.1.2** — Raspberry Pi OS 64 bits (Bookworm/Trixie, Pi 4B+ ou Pi 5) **et** Linux x86-64 (Debian / Ubuntu 24.04…). **Nouveau :** routage de message vers email (commande `#m`, radiogramme authentifié).

> Contrairement à MeshPacket, MeshRNS n'utilise **ni Direwolf ni AX.25** : sa dorsale est **Reticulum/LXMF**.

---

## Matériel requis

- **Raspberry Pi 4B+ ou Pi 5** sous **Raspberry Pi OS 64 bits** (`uname -m` → `aarch64`), **ou** un **PC / serveur x86-64** sous **Debian / Ubuntu** (ex. Ubuntu 24.04 ; `uname -m` → `x86_64`).
- Un **companion MeshCore** (nœud LoRa) connecté en **USB** (apparaît en `/dev/ttyACM0` ou `/dev/ttyUSB0`) — ou en **TCP**, ou en **Bluetooth (BLE)**.
- Un **accès au réseau Reticulum** atteignant vos stations TCQ : au moins une **interface RNS** déclarée dans `~/.reticulum/config` (RNode LoRa, TCPClientInterface vers un nœud RNS, AutoInterface, I2P…).

---

## Installation (depuis une release)

Aucune source ni dépendance Python à installer : l'archive contient un **binaire autonome**.

### 📥 Télécharger la dernière version

`https://github.com/f1gbd/F1GBD/releases` → tag **`meshrns-v2.1.2`**, puis l'archive correspondant à votre machine :

| Plateforme | `uname -m` | Archive |
| --- | --- | --- |
| Raspberry Pi 4B+/5 (64 bits) | `aarch64` | **`MeshRNS-v2.1.2-linux-aarch64.tar.gz`** |
| PC / serveur Linux | `x86_64` | **`MeshRNS-v2.1.2-linux-x86_64.tar.gz`** |

```bash
# 1. Extraction (adaptez le nom d'archive à votre plateforme)
tar xzf MeshRNS-v2.1.2-linux-aarch64.tar.gz
cd MeshRNS

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
sha256sum -c MeshRNS-v2.1.2-linux-aarch64.tar.gz.sha256
```

---

## Configuration Reticulum (important)

MeshRNS lit la configuration RNS du poste, **`~/.reticulum/config`** :

- **1ᵉʳ lancement sur machine vierge** (dossier `~/.reticulum` absent) : MeshRNS y installe une **configuration par défaut**, **à adapter** à votre réseau ADRASEC.
- **Profil existant** : MeshRNS **n'y touche jamais**. Placez votre `~/.reticulum/config` (l'interface qui joint vos stations TCQ).
- État des interfaces : **`rnstatus`** (si le paquet `rns` est installé sur le système), ou la ligne **`Diagnostic Reticulum : … interfaces connectees=N/M …`** dans le **Journal** de MeshRNS au démarrage.

MeshRNS possède sa **propre identité LXMF** (dossier `~/.meshrns`), distincte de TCQ : son adresse LXMF est stable et propre à la passerelle.

> Tant qu'aucune annonce de station **TCQ** n'apparaît dans le Journal (sans le tag `[hors filtre TCQ]`), la passerelle n'est **pas** sur le même réseau Reticulum que vos stations.

---

## Démarrage rapide

<div align="center">
<img src="https://github.com/f1gbd/F1GBD/blob/master/meshrns/raspberry/images/MeshRNSpi_mainscreen.png" alt="Interface MeshRNS v2.1.2 — onglet Connexion avec le groupe Routage email" width="900">
</div>

1. **Préparez `~/.reticulum/config`** (interface RNode LoRa / TCP qui joint le réseau TCQ).
2. Lancez `./MeshRNS` (ou le raccourci **MeshRNS** du menu). L'onglet **Connexion** présente **quatre groupes** : *MeshCore*, *LXMF / Reticulum* et *Routage email* à gauche, *Lien & filtrage TCQ* à droite.
3. **MeshCore (companion)** : **Transport** `serial`, **Port** `/dev/ttyACM0` (ou `/dev/ttyUSB0`), **Baudrate** `115200`, **Lecture active (get_msg)** cochée.
4. **LXMF / Reticulum** : **Station LXMF** = un indicatif **`TCQ-*`** (ex. `TCQ-F1GBD/77`). **Config RNS** vide (= `~/.reticulum/config`).
5. **Lien & filtrage TCQ** : **Indicatif local**, **Mode d'émission** (`broadcast` ou `direct`), **Canal de service** `tcq`, **Filtrer entrant (TCQ seul)** coché.
6. Au besoin, **Canaux…** pour créer le canal `tcq` sur le companion (même **clé** que les stations du réseau).
7. **▶ Démarrer** → voyant **● En service**. Suivez l'onglet **Journal** et **Annuaire…**.

> **Port série sous Linux** : réglez le **Port** du companion sur `/dev/ttyACM0` (USB-CDC) ou `/dev/ttyUSB0` (adaptateur série). Si le `meshrns.json` fourni contient un port **Windows** (`COMx`), remplacez-le. Idéalement, utilisez le chemin **stable** `/dev/serial/by-id/…` (immunisé aux renumérotations). Repérez-le avec `ls -l /dev/serial/by-id/`.

---

## Routage de message vers email (`#m`) *(v2.1)*

Depuis un **nœud MeshCore (LoRa)**, un opérateur peut faire **router un message vers un ou plusieurs destinataires courriel** — sans Internet côté terrain, c'est la passerelle qui relaie. Le corps est encapsulé dans un **radiogramme ADRASEC authentifié TOTP+CRC** (mêmes algorithmes que TCQ, donc **re-validable par n'importe quelle station TCQ**) puis expédié par SMTP.

Sur le canal de service `tcq` :

```
#m dest1@exemple.com; dest2@wanadoo.fr; corps du message … 73
```

Les adresses de tête (séparées par `;`) sont les destinataires ; le reste est le corps (les `;` internes sont conservés). Sans adresse, les **destinataires par défaut** sont utilisés. Une confirmation **`[#m] OK`** (code AUTH + expiration) revient sur le canal. La commande est **purement locale** (jamais relayée vers LXMF ni miroitée).

**Configuration** (onglet **Connexion**, groupe **Routage email**, sous *LXMF / Reticulum*) : renseignez **Serveur/Port SMTP**, **Utilisateur/Mot de passe SMTP**, **Email expéditeur** et **Destinataires défaut**, puis cochez **Routage email actif**. Le mot de passe est **masqué** (case **Afficher**). Pour un compte **Gmail**, utilisez un **mot de passe d'application dédié** (révocable) — procédure détaillée au **§13 du Manuel utilisateur**. Ces réglages sont enregistrés dans `meshrns.json` (passerelle autonome, sans TCQ).

> Dans la version publiée, les champs SMTP sont **vierges** : à renseigner par le sysop de la passerelle.

---

## Fonctionnalités (rappel)

L'édition Linux est **fonctionnellement identique** à la version Windows :

- **Dorsale Reticulum / LXMF** — transport applicatif LXMF par-dessus Reticulum (RF, LoRa RNode, TCP/IP, I2P…), adressage de bout en bout et chiffrement natif.
- **Routage de message vers email** *(v2.1)* — commande **`#m`** depuis un canal MeshCore vers un ou plusieurs courriels, avec **radiogramme authentifié TOTP+CRC** (re-validable par TCQ). Voir la section dédiée ci-dessus.
- **Filtrage `TCQ-*`** et **annuaire** persistant (`annuaire.json`, format TCQ), avec **import d'annuaire** et consultation depuis le canal MeshCore `tcq` (`ANNUAIRE`, `DIR`, `LIST`, `?`…).
- **Deux modes d'émission** : `broadcast` (toutes les stations TCQ fraîches) et `direct` (une station), plus la **surcharge `@<nom|hash> texte`** (ciblage exact ; un nom qualifié comme `@TCQ-F8KSM/77` n'est jamais détourné vers une variante plus longue).
- **Signature** des messages relayés, **réinjection LXMF → MeshCore** avec déduplication et anti-écho, **confirmation de livraison** journalisée (`Livraison LXMF confirmee`).
- **Gestion des canaux** du companion (création/clé, **QR de partage**, import d'URL `meshcore://channel/add`).
- **Arrêt fiable** (port libéré au besoin de force) et **config Reticulum par défaut** installée au 1ᵉʳ lancement si absente.
- **Interconnexion inter-îlots** *(v2.0)* — relie plusieurs îlots LoRa MeshCore **éloignés** en miroitant le canal de service via LXMF (mode **réflecteur / peering**), avec anti-écho par identifiant de message et liste blanche de pairs. Idéale pour un **réflecteur ADRASEC** en fonctionnement autonome (voir l'autostart ci-dessous).

> Pour le détail exhaustif (tableau `meshrns.json`, canal `tcq`, **paramétrage de l'interconnexion** avec schémas, **routage email #m** et **procédure app-password**, dépannage complet), voir le **[README principal MeshRNS](https://github.com/f1gbd/F1GBD/tree/master/meshrns)** et les fiches PDF — identiques, l'interface étant la même.

---

## Lancement automatique au démarrage

Pour qu'une passerelle ADRASEC démarre **MeshRNS automatiquement** à l'allumage (poste avec bureau, Raspberry Pi ou PC Linux) — et **désactiver** le démarrage automatique de MeshPacket Pi sur le même poste :

```bash
chmod +x autostart_pi.sh
./autostart_pi.sh
sudo reboot
```

Le script `autostart_pi.sh` :

- **active** MeshRNS au démarrage via l'**autostart XDG** `~/.config/autostart/meshrns-pi.desktop` (honoré par les sessions Raspberry Pi OS en **X11** comme en **Wayland** — labwc / wayfire), avec une petite temporisation au boot ;
- **désactive** MeshPacket Pi au démarrage sur tous les mécanismes courants : autostart XDG (`meshpacket*.desktop` → `.disabled`), services **systemd** (utilisateur et système), et fichiers `labwc` / `lxsession`.

Pour **revenir en arrière** (retirer MeshRNS du démarrage et réactiver MeshPacket) :

```bash
./autostart_pi.sh --undo
sudo reboot
```

> L'autostart ouvre l'**interface** MeshRNS ; cliquez sur **Démarrer** pour lancer la passerelle. Pour un fonctionnement totalement sans surveillance, demandez l'ajout d'une option de démarrage automatique de la passerelle.

---

## Dépannage

- **`could not open port COM3` / port Windows** → le `meshrns.json` contient un port Windows ; réglez le **Port** sur `/dev/ttyACM0` ou `/dev/ttyUSB0` (voir Démarrage rapide).
- **`/dev/ttyACM0` : permission refusée** → vous n'êtes pas dans le groupe `dialout`. Lancez `./install_pi.sh` puis déconnectez/reconnectez la session (ou `sudo usermod -aG dialout $USER`).
- **Companion non détecté** → `ls /dev/ttyACM* /dev/ttyUSB*` et ajustez **Port**.
- **`interfaces connectees=0`** (Journal) → la config Reticulum ne joint pas votre réseau : éditez `~/.reticulum/config` (RNode LoRa / TCP). Diagnostiquez avec `rnstatus`.
- **`Pas de chemin RNS vers …`** → la station cible n'est pas joignable sur le réseau Reticulum actuel (hors ligne, ou autre réseau). La ligne `Livraison LXMF confirmee` atteste d'une remise effective.
- **Routage email `#m` sans effet** → vérifiez que **Routage email actif** est coché et les champs SMTP renseignés (Gmail : mot de passe d'application, Manuel §13). Le Journal indique l'envoi ou l'erreur SMTP.
- **Companion Bluetooth (BLE)** → `./install_pi.sh` installe `bluez` ; appairez le companion, puis choisissez le transport `ble`.
- **Annuaire vide après redémarrage** → placez le dossier de l'appli dans un emplacement **inscriptible** (home), pour que `annuaire.json` persiste.

---

## 📄 Documentation associée

- 📘 **[Manuel utilisateur MeshRNS](https://github.com/f1gbd/F1GBD/blob/master/meshrns/documentation/MEMO%20-%20MANUEL%20MeshRNS.pdf)**
- 📋 **[Fiche technique MeshRNS](https://github.com/f1gbd/F1GBD/blob/master/meshrns/documentation/MEMO%20-%20Fiche%20Technique%20MeshRNS.pdf)**

---

## Licence & auteur

**MeshRNS** — *a Reticulum/LXMF Gateway for MeshCore* — par **F1GBD** (c) 2026 — **ADRASEC 77 / FNRASEC**.

<div align="center">

### 📡 Auteur

**Jean-Louis (F1GBD)**
*ADRASEC 77 — FNRASEC*

**MeshRNS — Version 2.1.2 — Juillet 2026**

</div>
