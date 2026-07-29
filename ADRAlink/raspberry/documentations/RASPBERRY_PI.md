# ADRAlink sur Raspberry Pi 4B+ (headless, derrière le GL.iNet)

Ce guide installe **ADRAlink en mode « boîtier serveur »** sur un Raspberry Pi 4B+
sans écran (*headless*) : le serveur ADRAlink, le portail de téléchargement + le
client web, et PAT (client Winlink) démarrent automatiquement au boot via
**systemd**. Le **mini-routeur GL.iNet reste le point d'accès WiFi** ; le Pi est
un simple hôte sur son réseau local.

Tout le cœur d'ADRAlink étant en **Python pur (bibliothèque standard)**, il tourne
tel quel sur Raspberry Pi OS. Le seul élément à part est **PAT** (binaire ARM
officiel) et, pour la radio, le modem **VARA via Wine** (voir §6).

---

## 1. Prérequis

- **Raspberry Pi 4B+** (2 Go suffisent ; 4 Go conseillé si VARA/Wine).
- **Raspberry Pi OS (64-bit)** — *Lite* suffit (pas besoin de bureau).
- Le Pi connecté au **réseau du GL.iNet** (Ethernet conseillé, ou WiFi).
- Une **IP fixe** pour le Pi (réservation DHCP sur le GL.iNet, ou IP statique) —
  c'est cette IP que `adralink.fr` pointera.
- Pour la radio : une **interface son** (SignaLink/Digirig…) + un TX/RX, et un
  **indicatif** + compte Winlink. Pour débuter, **Telnet (CMS)** ne demande rien.

---

## 2. Installation — une seule commande

Copiez le dossier **`raspberry`** sur le Pi (clé USB, `scp`, `git`…), puis :

```bash
cd raspberry
sudo bash install_adralink_pi.sh
```

L'installateur « one-click » fait **tout** et démarre le service :

- installe `python3`, `curl` et **PAT** (paquet `.deb` ARM `arm64`/`armhf`) ;
- crée l'utilisateur système **`adralink`** et **`/opt/adralink`**, y copie le code
  (et l'APK s'il est dans `app/`) ;
- **demande** l'indicatif (MyCall), le mot de passe Winlink et le transport,
  puis **configure PAT** (écrit `mycall` + mot de passe, sans éditeur) et écrit
  **`/etc/adralink/adralink.env`** ;
- installe, **active et démarre** les trois services systemd.

À la fin, ADRAlink est **déjà en service**. Il ne reste que le mappage
`adralink.fr` côté GL.iNet (§5).

> Placez votre `ADRAlink_client.apk` dans `raspberry/app/` **avant** de lancer le
> script pour qu'il soit proposé par le portail (sinon copiez-le ensuite dans
> `/opt/adralink/`).

### Variante non-interactive (une ligne, sans questions)

```bash
sudo MYCALL=F1GBD WINLINK_PASSWORD='motdepasse' CONNECT_URL=telnet \
     AUTO_CONNECT_FLAG=--auto-connect bash install_adralink_pi.sh
```

Variables disponibles : `MYCALL`, `WINLINK_PASSWORD`, `CONNECT_URL`
(`telnet`, `varafm:///RMS`, `varahf:///RMS`, `ardop:///RMS`), `AUTO_CONNECT_FLAG`
(`--auto-connect` ou vide), `SRV_PORT`, `PORTAL_PORT`, `POLL`, `RX_INTERVAL`.

---

## 3. Reconfigurer plus tard (optionnel)

Tout est déjà fait par l'installateur. Pour **changer** un réglage ensuite :

- **Paramètres de connexion** (comme le GUI Windows) — le plus simple, en SSH :

  ```bash
  sudo adralink-config
  ```

  Menu : **transport** (Telnet / VARA FM / VARA HF / VARA SAT / ARDOP),
  **indicatif de la passerelle RMS**, **digipeater** (ex. `F5ZYI-7`), fréquence,
  **sessions automatiques**. Il construit l'URL correcte
  (`varafm:///DIGI/RMS`, `varahf:///…` pour HF/SAT, `telnet`…), écrit la config
  et **redémarre le serveur**.
- **Autres réglages** (ports, cadences) : éditez `/etc/adralink/adralink.env`
  puis `sudo systemctl restart adralink-server adralink-portal`.
- **Indicatif / mot de passe Winlink** : relancez l'installateur, ou
  `sudo -u adralink HOME=/opt/adralink pat configure` puis
  `sudo systemctl restart pat`.

| Variable (`adralink.env`) | Rôle | Exemple |
|---|---|---|
| `SRV_PORT` | Port de l'API/serveur ADRAlink | `8080` |
| `PORTAL_PORT` | Port du portail + client web (80 = URL propre) | `80` |
| `CONNECT_URL` | `telnet`, `varafm:///RMS`, `varahf:///RMS`, `ardop:///RMS` | `telnet` |
| `POLL` / `RX_INTERVAL` | Relève / réception (s) | `20` / `120` |
| `AUTO_CONNECT_FLAG` | `--auto-connect` ou vide | `--auto-connect` |

---

## 4. Vérifier et superviser

```bash
systemctl status adralink-server --no-pager
journalctl -u adralink-server -f        # journal en direct
journalctl -u adralink-portal -f
journalctl -u pat -f
```

Test rapide depuis un autre appareil du réseau (remplacez par l'IP du Pi) :

```
http://IP-DU-PI/               ->  portail (page + bouton client web)
http://IP-DU-PI/app            ->  client web (écrire / lire un message)
http://IP-DU-PI:8080/api/v1/health  ->  { "status": "ok", ... }
```

---

## 5. Accès pour le sinistré (nom `adralink.fr`)

Le Pi étant derrière le **GL.iNet**, c'est le **routeur** qui résout le nom.
Dans le DNS du GL.iNet (dnsmasq), faites pointer `adralink.fr` vers **l'IP du
Pi** :

```
uci add_list dhcp.@dnsmasq[0].address='/adralink.fr/IP-DU-PI'
uci commit dhcp; /etc/init.d/dnsmasq restart
```

Pour le **portail captif** (la page s'ouvre toute seule) et les réglages
smartphone (taper `http://`, désactiver le DNS privé Android), suivez
**`PORTAL_SETUP.md`** — tout s'applique à l'identique, en visant l'IP du Pi au
lieu de celle d'un PC.

Parcours utilisateur : WiFi ADRAlink → `http://adralink.fr` → télécharger l'app
Android **ou** « Utiliser dans le navigateur » (`/app`).

---

## 6. Radio : VARA (FM/HF/SAT) via Wine, ou ARDOP natif

### 6a. Telnet (CMS) — pour débuter

`CONNECT_URL=telnet` : aucun modem, les emails passent par les serveurs Winlink
(Internet de secours). Idéal pour valider toute la chaîne.

### 6b. VARA via Wine / Box86 (choix retenu)

VARA est un logiciel Windows ; sur Pi il s'exécute via **Wine + Box86/Box64**.
Des projets communautaires automatisent l'installation :

- **Winelink** (WheezyE) : scripts d'installation de VARA (et RMS Express) sur
  ARM — https://github.com/WheezyE/Winelink
- **Pi-Apps** : entrée « Install VARA HF on Linux ARM Device ».

Une fois VARA lancé (il écoute en TCP, ports **8300** commande / **8301**
données, comme sous Windows), configurez le bloc `varafm` (ou `varahf`) de PAT :

```bash
sudo -u adralink HOME=/opt/adralink pat configure
# bloc varafm : "addr": "localhost:8300", PTT via VOX ou Hamlib
```

puis mettez dans `/etc/adralink/adralink.env` :

```
CONNECT_URL=varafm:///INDICATIF_RMS      # ou varahf:///... pour HF / SAT
```

et `sudo systemctl restart adralink-server`.

**Démarrage automatique de VARA FM (headless).** Après avoir configuré VARA FM
**une fois** via écran/VNC (indicatif, carte son = interface USB en **ALSA**,
PTT, ports 8300/8301), activez le service fourni pour qu'il se lance seul au boot
via `xvfb-run` :

```bash
cd raspberry
sudo bash install_vara_service.sh          # detecte l'utilisateur + le chemin
# verifier :
systemctl status vara --no-pager
ss -ltnp | grep 8300                        # VARA en ecoute ?
```

Le script génère `/etc/systemd/system/vara.service` avec le bon utilisateur (celui
qui possède le préfixe `~/.wine`) et installe `xvfb`. VARA démarre alors **avant**
PAT et écoute sur 8300, headless.

> VARA/Wine est plus gourmand : sur un Pi 4, privilégiez une carte SD rapide (ou
> SSD USB) et surveillez la charge (`htop`). Réglez l'audio de Wine sur **ALSA**
> (pointant l'interface USB) plutôt que PulseAudio, plus fiable pour un service
> système. Pour VARA SAT, on utilise le schéma `varahf` avec le modem **VARA
> SAT**.

### 6c. ARDOP natif (alternative « tout Linux »)

Si vous préférez éviter Wine, **ARDOP** dispose d'un modem natif Linux/ARM
(`ardopcf`) qui tourne directement sur le Pi. Lancez-le, puis
`CONNECT_URL=ardop:///INDICATIF_RMS`.

---

## 7. Mise à jour / désinstallation

**Mettre à jour le code** (nouvelle version) :

```bash
sudo systemctl stop adralink-server adralink-portal
sudo install -m 0644 app/adralink_lib.py    /opt/adralink/adralink_lib.py
sudo install -m 0644 app/ADRAlink_portal.py /opt/adralink/ADRAlink_portal.py
sudo chown adralink:adralink /opt/adralink/*.py
sudo systemctl start adralink-server adralink-portal
```

**Désinstaller** :

```bash
sudo systemctl disable --now pat adralink-server adralink-portal
sudo rm -f /etc/systemd/system/{pat,adralink-server,adralink-portal}.service
sudo systemctl daemon-reload
sudo rm -rf /opt/adralink /etc/adralink
sudo userdel adralink
```

---

## 8. Dépannage

| Symptôme | Piste |
|---|---|
| `adralink-server` ne démarre pas | `journalctl -u adralink-server -e` ; vérifier `/etc/adralink/adralink.env`. |
| Le portail ne prend pas le port 80 | La capacité `CAP_NET_BIND_SERVICE` est posée par le service ; si un autre serveur web occupe le 80, mettez `PORTAL_PORT=8088`. |
| Client web injoignable | Vérifier que `adralink-server` tourne (le portail proxifie `/app` et `/api` vers lui). |
| `adralink.fr` ne résout pas | C'est le **DNS du GL.iNet** : voir §5 et `PORTAL_SETUP.md` (mapping, `/#/`, DNS privé Android). |
| PAT injoignable | `journalctl -u pat -e` ; refaire `pat configure` ; vérifier le port 8081. |
| Store « Identifiant inconnu » | Le store est `/opt/adralink/adralink_store.json` (persistant) ; ne pas mélanger avec un autre hôte. |

---

*ADRAlink v1.1.2 — F1GBD / ADRASEC 77 / FNRASEC — Licence GNU GPL v3.0*
