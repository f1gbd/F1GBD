<p align="center">
  <img src="../images/ADRAlink_logo.png" alt="ADRAlink" width="150">
</p>

# ADRAlink — édition Raspberry Pi 4B+

Boîtier serveur **ADRAlink autonome** sur Raspberry Pi 4B+ : le serveur, le
**portail de téléchargement**, le **client web** et **PAT** (client Winlink)
démarrent automatiquement au boot (services systemd). Un **tableau de bord** est
affiché sur l'écran du Pi. Livré en **binaires (sans code source)**, comme les
exécutables Windows.

Le mini-routeur WiFi (GL.iNet ou autre) reste le point d'accès ; le Pi est un
hôte de son réseau local.

> Publié en Open Source ([licence GNU v3.0](https://github.com/f1gbd/F1GBD/blob/master/LICENSE.txt))
> pour un usage personnel uniquement, non professionnel et non commercial.

---

## Téléchargement

Depuis la [dernière release](https://github.com/f1gbd/F1GBD/releases) :

- 📦 **Paquet Debian (recommandé)** — `adralink_1.1.2_arm64.deb`
  ([télécharger](https://github.com/f1gbd/F1GBD/releases/download/adralink-v1.1.2/adralink_1.1.2_arm64.deb))

Prérequis : **Raspberry Pi 4B+**, **Raspberry Pi OS 64-bit** (Lite suffit), Pi
connecté au réseau du mini-routeur (IP fixe conseillée).

---

## Installation (opérateur de terrain)

### Méthode — paquet `.deb` (la plus simple)

```bash
sudo apt install ./adralink_1.1.2_arm64.deb
```

Tout est installé, activé et démarré. Aucune question posée.

```

### Configuration (une seule fois, après l'installation)

```bash
sudo -u adralink HOME=/opt/adralink pat configure   # indicatif + mot de passe Winlink
sudo adralink-config                                # transport / RMS / digipeater
```

`adralink-config` propose Telnet / VARA FM / VARA HF / VARA SAT / ARDOP, l'indicatif
de la passerelle RMS et le **digipeater** (ex. F5ZYI-7), puis redémarre le serveur.

### Radio VARA FM (optionnel)

VARA FM (sous Wine) doit être installé et configuré une fois, puis activé en
service :

```bash
sudo bash /opt/adralink/install_vara_service.sh
```

Détails (Wine/Box86, ARDOP natif, écran/VNC) : voir
[RASPBERRY_PI.md](documentations/RASPBERRY_PI.md) §6.

---

## Utilisation

- **Écran du Pi** : tableau de bord (indicatif, IP, `adralink.fr`, transport,
  état des services, compteurs de messages) au-dessus du journal en direct.
- **Sinistré** (sur le WiFi ADRAlink) : `http://adralink.fr/` → télécharger
  l'app Android **ou** « Utiliser dans le navigateur » (`/app`).
- **Adresse `adralink.fr`** : à faire pointer vers l'IP du Pi dans le DNS du
  routeur (voir [../documentations/PORTAL_SETUP.md](../documentations/PORTAL_SETUP.md)).

Au **redémarrage**, tout se relance automatiquement.

---

## Documentation

- 🧭 **[Fiche exploitation terrain](documentations/FICHE_TERRAIN.md)** — 1 page : allumer,
  vérifier, changer de transport/digi, éteindre.
- 📘 **[Guide complet RASPBERRY_PI.md](documentations/RASPBERRY_PI.md)** — installation, PAT,
  VARA/Wine, réseau, supervision, dépannage.
- 🌐 **[Portail & DNS routeur](../documentations/PORTAL_SETUP.md)** —
  `adralink.fr`, portail captif.

---

## Compilation (mainteneur, pour produire les binaires)

Les binaires ARM sont fabriqués **une fois sur un Pi** (kit de build, non publié
avec les sources). Voir le kit `raspberry/build/` du dépôt de développement :
`build_pi_release.sh` (→ `.tar.gz`) et `build_pi_deb.sh` (→ `.deb`).

---

*ADRAlink v1.1.2 — © 2026 F1GBD / ADRASEC 77 / FNRASEC. Licence GNU GPL v3.0.*
