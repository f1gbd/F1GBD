# MC-RMRPconfigurator

**Configurateur 100 % OFF-GRID pour Room Server & Répéteur MeshCore**
sur module **Heltec WiFi LoRa 32 V3** (ESP32-S3).

> _par **F1GBD** — ADRASEC 77 — FNRASEC — Juillet 2026 — **v1.2**_

Inspiré du configurateur web <https://meshcore.co.uk/configurator/>, mais conçu pour
fonctionner **sans aucune connexion Internet**, sur le terrain, en situation de crise
ou d'exercice.

---

## Pourquoi « Off-Grid » ?

Le configurateur web officiel nécessite un navigateur et l'accès au site
`meshcore.co.uk`. **MC-RMRPconfigurator ne dépend de rien de tout cela** :

- ⚡ **Zéro Internet, zéro cloud, zéro serveur.** Toute la configuration se fait en
  local, par câble **USB**, via la **console série (CLI)** intégrée au firmware MeshCore.
- 🔌 **Flashage du firmware hors-ligne** : les fichiers `.bin` sont pris sur le disque
  local (préalablement téléchargés), le flash passe par `esptool` en local — aucune
  connexion pendant l'opération.
- 🎒 **Utilisable sur une machine isolée** : PC de terrain, poste ADRASEC/FNRASEC sans
  réseau, ordinateur volontairement déconnecté. Idéal pour déployer un réseau maillé
  **autonome** (secours, événementiel, zone blanche).
- 🔒 **Aucune donnée ne sort du poste.** Pas de télémétrie, pas de compte, pas de dépendance
  externe.

C'est l'outil de configuration pensé pour un usage **de secours et d'autonomie radio**.

---

## Fonctionnalités

- **Connexion série** avec détection automatique des ports (115200 bauds par défaut, réglable).
- **Lecture / écriture globale** de la configuration du nœud.
- **Onglet Radio** : fréquence, bande passante, SF, CR, puissance TX, RX boosted gain,
  et **préréglages régionaux** (EU 868/433, US 915, ANZ 915, UK, IN).
- **Onglet Système** : nom, latitude/longitude, info propriétaire, rôle, clé publique,
  mot de passe admin, économie d'énergie.
- **Onglet Routage** : repeat, duty cycle, délais de retransmission, détection de boucle,
  intervalles d'advert, nombre de hops max, multi-acks…
- **Onglet Room Server** : mot de passe invité, mode lecture seule, gestion de l'**ACL**
  (`setperm`).
- **Onglet Région** : édition de l'arborescence des régions (`region load` / `region save`),
  régions *home* et *default*.
- **Bouton 📢 Advertise** : émet une annonce du Room Server / répéteur (**flood** ou **zero-hop**).
- **Onglet Firmware** : **flashage offline** du Heltec V3 (fichier fusionné ou 4 fichiers
  séparés, effacement de flash, log en temps réel).
- **Onglet Catalogue firmwares** : firmwares Heltec V3 pré-enregistrés (**Repeater**,
  **Room Server**, **MeshPager RASEC ALERT v5.0**) — téléchargement (une fois, machine
  connectée) vers un dossier local puis **flash 100 % hors-ligne en un clic**.
- **Onglet Console** : terminal CLI brut + commandes rapides (`ver`, `advert`, `reboot`,
  `erase`…).
- **Profils JSON** : sauvegarde / rechargement de la configuration pour déployer
  plusieurs nœuds identiques.
- Interface sombre « pro » (PySide6 / Qt).

---

## Installation

### Option A — Exécutable Windows (recommandé, aucune dépendance)

Téléchargez la dernière archive `MC-RMRPconfigurator-vX.Y.Z-win64.7z` depuis la page
[Releases](https://github.com/f1gbd/F1GBD/releases), décompressez-la (Windows 11 gère le
`.7z` nativement, sinon [7-Zip](https://www.7-zip.org)), puis lancez
`MC-RMRPconfigurator.exe`.

### Option B — Depuis les sources (Python 3.9+)

```bash
pip install pyside6 pyserial esptool
python mc_rmrp_configurator.py
```

> Astuce : installez les dépendances **une fois** sur une machine connectée, l'application
> tourne ensuite **totalement hors-ligne**.

---

## Prise en main rapide

1. Branchez le Heltec V3 (déjà flashé MeshCore en rôle **Repeater** ou **Room Server**) en USB.
2. Cliquez sur `⟳`, choisissez le port, laissez `115200`, puis **Connecter**.
3. **Lire toute la config** pour rapatrier les réglages actuels.
4. Modifiez les champs, **Appliquer toute la config**, puis **Redémarrer le nœud**
   (la fréquence et les paramètres radio ne prennent effet qu'après reboot).
5. Utilisez **📢 Advertise** pour annoncer le nœud sur le réseau.

📄 Une **[Fiche Technique](FICHE_TECHNIQUE.md)** détaille pas-à-pas la configuration d'un
Room Server et d'un Répéteur.

---

## Flashage firmware (offline)

Le Heltec V3 est un **ESP32-S3**. L'onglet *Firmware* appelle `esptool` en local.

| Fichier | Offset (ESP32-S3) |
|---|---|
| bootloader | `0x0` |
| partitions | `0x8000` |
| boot_app0 | `0xe000` |
| application | `0x10000` |

Un mode « fichier unique fusionné » (`merged` @ `0x0`) est également disponible.
Les firmwares MeshCore se récupèrent au préalable (sur une machine connectée) depuis
<https://flasher.meshcore.co.uk/> ou les *releases* GitHub `meshcore-dev/MeshCore`, puis
se copient sur le poste hors-ligne.

---

## Catalogue de firmwares (Repeater / Room Server / MeshPager)

L'onglet **Catalogue firmwares** regroupe des firmwares Heltec V3 prêts à flasher :

| Firmware | Version | Mode de flash | Source |
|---|---|---|---|
| **Repeater** | MeshCore v1.16.0 | fusionné @ `0x0` + erase | releases `meshcore-dev/MeshCore` |
| **Room Server** | MeshCore v1.16.0 | fusionné @ `0x0` + erase | releases `meshcore-dev/MeshCore` |
| **MeshPager RASEC ALERT** | F1GBD **v5.0** | 4 fichiers (`0x0`/`0x8000`/`0xe000`/`0x10000`) + erase | [f1gbd.github.io/F1GBD/meshpager](https://f1gbd.github.io/F1GBD/meshpager/) |

Principe **off-grid** : un bouton **Télécharger** récupère les fichiers (sur une machine
connectée) dans un dossier local `firmware/`, puis le bouton **Flasher (offline)** les
envoie au module **sans aucune connexion**. Sur un poste totalement isolé, il suffit de
copier les `.bin` à la main dans ce dossier.

> ℹ️ Le **MeshPager** est un nœud **companion** : sa radio est **figée au build**
> (869.618 MHz / 62.5 kHz / SF8 / CR8) et il se configure par **commandes de chat**
> (`#ra`, `#b`, `#rapass`, code Chappe 26) ou **appairage BLE** (PIN `772677`), et **non**
> par les onglets de configuration série. Voir le projet
> [MeshPager](https://github.com/f1gbd/F1GBD/tree/master/meshpager).

---

## Avertissement réglementaire

Respectez la réglementation radioélectrique de votre pays (fréquence, puissance, duty
cycle). En Europe, la bande 868 MHz impose des limites de duty cycle : configurez
`dutycycle` en conséquence.

---

## Crédits

Développé pour un usage **OFF-GRID** par **F1GBD** — **ADRASEC 77** / **FNRASEC**.
Basé sur le firmware et la CLI [MeshCore](https://meshcore.co.uk/).

Références CLI :
- <https://docs.meshcore.io/cli_commands/>
- <https://github.com/meshcore-dev/MeshCore/wiki/Repeater-&-Room-Server-CLI-Reference>

## Licence

MIT.
