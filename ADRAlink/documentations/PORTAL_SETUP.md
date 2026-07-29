# ADRAlink — Portail de téléchargement en zone blanche

Objectif : le sinistré se connecte au **WiFi ADRAlink** (mini-routeur GL.iNet,
sans Internet) et arrive sur une page où il **télécharge l'application Android**.
Deux confforts d'accès sont prévus : une **adresse simple** (`http://adralink.fr`)
et un **portail captif** (la page s'ouvre toute seule à la connexion).

Le portail est servi par `ADRAlink_portal.py` **sur le PC de l'opérateur**
(celui qui fait déjà tourner `ADRAlink_serveur`). C'est la solution recommandée :
rien à installer sur le routeur. Une variante « hébergé sur le routeur » est
décrite en fin de document.

---

## 1. Lancer le portail sur le PC

1. Placez le fichier **`ADRAlink_client.apk`** (l'APK que vous avez compilé) **à
   côté de `ADRAlink_portal.py`** — ou indiquez son chemin avec `--apk`.
2. Lancez le portail. Le port 80 permet l'URL propre `http://adralink.fr` (sans
   `:port`) et le portail captif ; sous Windows il demande souvent les droits
   **administrateur** :

   ```
   python ADRAlink_portal.py                 # port 80 (recommandé)
   python ADRAlink_portal.py --port 8088     # repli si le port 80 est pris
   python ADRAlink_portal.py --apk "C:\chemin\ADRAlink_client.apk"
   ```

3. **Pare-feu Windows** : autorisez le port du portail (comme pour ADRAlink) :

   ```
   netsh advfirewall firewall add rule name="ADRAlink Portail 80" dir=in action=allow protocol=TCP localport=80 profile=any
   ```

Test rapide depuis le PC : ouvrez `http://127.0.0.1/` (ou `:8088`). Depuis un
téléphone connecté au WiFi : `http://IP-DU-PC/`.

> Astuce : donnez au PC une **IP fixe** sur le réseau du routeur (ou une
> réservation DHCP), pour que l'adresse `adralink.fr` pointe toujours au bon
> endroit. Dans les exemples ci-dessous, le PC est en `192.168.8.100`
> (adaptez à votre `ipconfig`).

---

## 2. Adresse simple `http://adralink.fr` (DNS du routeur)

On fait résoudre le nom `adralink.fr` vers l'IP du PC, côté GL.iNet (dnsmasq).

### Via l'interface (LuCI / OpenWrt)

Interface avancée du GL.iNet → **Network → DHCP and DNS → General → Addresses**
(champ « Address ») → ajoutez :

```
/adralink.fr/192.168.8.100
```

### Via SSH (uci)

```
ssh root@192.168.8.1
uci add_list dhcp.@dnsmasq[0].address='/adralink.fr/192.168.8.100'
uci commit dhcp
/etc/init.d/dnsmasq restart
```

> **Protection anti-rebind DNS.** OpenWrt bloque par défaut la résolution d'un
> **nom public** (`.fr`) vers une **IP privée** (`192.168.x`). Si `adralink.fr`
> ne répond pas, autorisez-le :
> ```
> uci add_list dhcp.@dnsmasq[0].rebind_domain='adralink.fr'
> uci commit dhcp; /etc/init.d/dnsmasq restart
> ```
> (ou décochez « Rebind protection » dans LuCI). Autre option : utiliser un nom
> **sans point** comme `adralink` ou un domaine `.lan` (`adralink.lan`), non
> concerné par cette protection.

Le port 80 étant le port web par défaut, l'utilisateur tape juste
**`adralink.fr`** (ou `adralink.fr:8088` si vous êtes sur le port de repli).

---

## 3. Portail captif (la page s'ouvre toute seule)

Quand un smartphone rejoint un WiFi, il teste l'accès Internet en appelant des
**domaines de détection** (Android, Apple, Windows). S'ils ne répondent pas
« normalement », le téléphone ouvre automatiquement une fenêtre de connexion.
Il suffit de faire pointer ces tests vers le portail.

Comme le dispositif est **isolé (aucun Internet)**, le plus simple et le plus
fiable est de **rediriger TOUS les domaines vers le PC** : chaque test de
connectivité tombe alors sur le portail, et n'importe quelle adresse tapée y
mène aussi.

### Via SSH (uci) — redirection totale

```
ssh root@192.168.8.1
uci add_list dhcp.@dnsmasq[0].address='/#/192.168.8.100'
uci commit dhcp
/etc/init.d/dnsmasq restart
```

`/#/` = « tous les domaines ». Le portail répond aux sondes captives
(`/generate_204`, `/hotspot-detect.html`, `/ncsi.txt`, …) par une redirection
vers la page : la fenêtre de téléchargement s'ouvre donc automatiquement.

> Cela n'empêche pas l'application ADRAlink de fonctionner : le client parle au
> serveur par **adresse IP** (et la découverte automatique reste par IP), pas par
> nom de domaine.

### Variante ciblée (si vous ne voulez pas le « tout rediriger »)

Rediriger uniquement les domaines de détection vers le PC :

```
uci add_list dhcp.@dnsmasq[0].address='/connectivitycheck.gstatic.com/192.168.8.100'
uci add_list dhcp.@dnsmasq[0].address='/clients3.google.com/192.168.8.100'
uci add_list dhcp.@dnsmasq[0].address='/captive.apple.com/192.168.8.100'
uci add_list dhcp.@dnsmasq[0].address='/www.msftconnecttest.com/192.168.8.100'
uci add_list dhcp.@dnsmasq[0].address='/www.msftncsi.com/192.168.8.100'
uci commit dhcp; /etc/init.d/dnsmasq restart
```

---

## 4. Récapitulatif de l'expérience utilisateur

1. Le sinistré se connecte au **WiFi ADRAlink** (pas d'Internet).
2. Son téléphone **ouvre automatiquement** la page de téléchargement (portail
   captif) — ou il tape **`adralink.fr`** dans son navigateur.
3. Il touche **« Télécharger l'application Android »**, autorise l'installation,
   installe **ADRAlink**.
4. Il ouvre l'app : le **serveur est détecté automatiquement**, il envoie son
   message.

Sur **PC / tablette / iPhone**, il choisit plutôt **« Utiliser dans le
navigateur »** et écrit/lit son message sans rien installer.

---

## 4bis. Client web (sans installation)

Le **serveur ADRAlink** sert lui-même un **client web** (page unique) à sa
racine, à la même origine que l'API — donc sans problème de CORS. Le portail
ajoute un bouton **« Utiliser dans le navigateur »**.

Pour éviter d'avoir à saisir le port `:8080`, le portail **relaie** (proxy) le
client web et l'API sur son propre port :

- l'utilisateur ouvre simplement **`http://adralink.fr/app`** ;
- le portail transmet `/app` et `/api/…` au serveur ADRAlink local
  (`127.0.0.1:8080`) ; aucune configuration supplémentaire.

Le client web est aussi accessible **directement** sur le serveur
(`http://IP-du-PC:8080/`). Dans tous les cas, il faut que le **serveur ADRAlink
soit démarré** (bouton « Démarrer le serveur »). Le port de l'API est transmis
automatiquement au portail par la console ; en lancement manuel, utilisez
`--api-port` si le serveur n'est pas sur 8080.

---

## 5. Variante : héberger le portail sur le routeur GL.iNet

Avantage : fonctionne **même PC éteint**, et le portail captif est natif.
Inconvénient : configuration OpenWrt manuelle.

Principe (serveur web `uhttpd` déjà présent sur OpenWrt) :

```
ssh root@192.168.8.1
mkdir -p /www/adralink
# copiez la page et l'APK dans /www/adralink/ (index.html + ADRAlink_client.apk)
# servez-les via uhttpd (port 80 déjà utilisé par LuCI : utilisez un autre port
# ou un instance uhttpd dédiée), et ajoutez le bon type MIME pour l'APK :
echo "static.apk=application/vnd.android.package-archive" >> /etc/httpd.conf
```

Puis pointez `adralink.fr` (ou la redirection captive) vers **l'IP du routeur**
(`192.168.8.1`) au lieu de celle du PC. Les mêmes réglages DNS qu'aux sections 2
et 3 s'appliquent, en remplaçant `192.168.8.100` par `192.168.8.1`.

> Pour générer la page seule (à copier dans le routeur), lancez le portail sur le
> PC et enregistrez `http://127.0.0.1/` depuis un navigateur, ou demandez le
> fichier `index.html` à l'équipe ADRAlink.

---

*ADRAlink v1.1.1 — F1GBD / ADRASEC 77 / FNRASEC — Licence GNU GPL v3.0*
