<div align="center">

<img src="images/MeshRNS.png" alt="MeshRNS" width="400">


**Passerelle Reticulum / LXMF pour MeshCore — ADRASEC 77 / FNRASEC**

### *« Un pont, deux Univers Mesh, aucune frontière. »*

*Là où le LoRa s'arrête, le maillage Reticulum prend le relais.*

MeshRNS relie un **réseau radio MeshCore** (LoRa) au **réseau maillé Reticulum** via **LXMF** (la même pile que TCQ), et ne dialogue **qu'avec les stations `TCQ-xxxx`** du réseau. Les messages d'un canal MeshCore sont transportés en LXMF vers les stations TCQ joignables par Reticulum (RF longue distance, LoRa, TCP/IP, I2P…), et les messages LXMF reçus des stations TCQ sont réinjectés sur le réseau MeshCore local. C'est l'équivalent d'une passerelle AirLink, mais avec **Reticulum/LXMF** comme dorsale au lieu de VARA — ce qui apporte l'**adressage de bout en bout**, le **chiffrement natif** et le **routage multi-saut** propres à Reticulum.

![Interface MeshRNS](https://raw.githubusercontent.com/f1gbd/F1GBD/master/meshrns/images/MeshRNS_screen.png)

> Version courante : **v1.0.8** — Windows (interface graphique).
### 📥 [**Télécharger la dernière version pour Windows 11 (x64)**](https://github.com/f1gbd/F1GBD/releases/download/meshrns-v1.0.8/MeshRNS-v1.0.8-win64.7z)

*Archive **7-Zip** (.7z) — Windows 11 l'extrait nativement ; sinon installez [7-Zip](https://www.7-zip.org).*

</div>

---

## Principe

<div align="center">
<img src="images/MeshRNS_principle.png" alt="MeshRNS — un pont, deux réseaux, aucune frontière : du réseau MeshCore (LoRa, LXMF) au réseau Reticulum des stations TCQ" width="760">
</div>

```
        Réseau MeshCore (LoRa)                       Réseau Reticulum (maillé)
            clients LoRa                            stations TCQ-xxxx en LXMF
                 │                                  (TCQ / MeshChat / Sideband)
           canal « tcq »                                       │
                 │                                             │
      companion ── USB/série/TCP/BLE ──┐                       │
                                       │                       │
                                 ┌─────┴───────┐               │
                                 │   MeshRNS   │ ═══ LXMF ═════╪═══ Reticulum
                                 │ (passerelle)│    (RNS)      │   RF / LoRa /
                                 └─────────────┘               │   TCP-IP / I2P…
                                                               │
                                                    TCQ-F1GBD · TCQ-56/HF · TCQ-BBS…
```

La passerelle s'**annonce sur LXMF** sous un indicatif de station **`TCQ-*`** et écoute les annonces du réseau : seules les stations dont le nom commence par **`TCQ`** sont retenues (**filtrage**) et inscrites dans un **annuaire**. Tout message posté sur le **canal MeshCore de service `tcq`** est relayé en LXMF vers ces stations ; tout message LXMF reçu d'une station TCQ est réinjecté sur MeshCore.

La **connexion à Reticulum est automatique** : MeshRNS lit la configuration RNS du poste (`~/.reticulum/config`), **préparée dans TCQ-config** — il n'y a **aucun réglage d'interface RNS dans MeshRNS**.

---

## Fonctionnalités

- **Dorsale Reticulum / LXMF** — transport applicatif **LXMF** (Lightweight Extensible Message Format), exactement la pile utilisée par TCQ, par-dessus le réseau maillé **Reticulum** (RF, LoRa RNode, TCP/IP, I2P…). Adressage de bout en bout et chiffrement assurés par Reticulum.
- **Connexion automatique à Reticulum** — la pile RNS lit `~/.reticulum/config` (interfaces, transport) **configuré via TCQ-config**. Rien à régler ici.
- **Filtrage `TCQ-*`** — la passerelle ne retient (annonces, annuaire) et n'accepte (messages entrants) **que les stations TCQ**. Les autres trafics LXMF du réseau sont ignorés.
- **Annuaire LXMF** — constitué automatiquement à partir des annonces des stations TCQ, persistant dans `annuaire.json` (**format identique à TCQ** : `{hash: {name, last_seen}}`), avec visualiseur intégré (copier l'adresse, définir comme station directe, case **« Sans filtre TCQ »** pour afficher *toutes* les stations LXMF vues, et bouton **« Importer annuaire TCQ… »** pour fusionner un `annuaire.json` complet généré par TCQ).
- **Annuaire consultable depuis le canal MeshCore `tcq`** — un client MeshCore envoie une commande (`ANNUAIRE`, `DIR`, `LIST`, `?`…) sur le canal de service et la passerelle **répond la liste des stations TCQ** sur ce même canal, avec filtre optionnel (`ANNUAIRE BBS`).
- **Deux modes d'émission** MeshCore → LXMF (champ *Mode d'émission*) :
  - **`broadcast`** (défaut) — multi-unicast vers **toutes les stations TCQ vues récemment** (fenêtre `broadcast_max_age_days`). C'est le mode qui reproduit le comportement réseau de TCQ ;
  - **`direct`** — message adressé à **une seule station** par défaut (`peer_station`, nom TCQ ou hash).
  - **Surcharge ad hoc** — un message commençant par **`@<nom|hash> texte`** est envoyé uniquement à cette station, quel que soit le mode. Le **préfixe d'expéditeur** que MeshCore ajoute aux messages de canal (`F1GBD/P: @TCQ-…`) est **toléré** : le `@cible` est détecté même précédé du nom de l'émetteur.
- **Signature des messages** — les messages relayés vers LXMF sont **signés** en fin de message avec l'**indicatif local** (ou une signature personnalisée), sans double signature (`sign_outbound` / `signature`).
- **Réinjection LXMF → MeshCore** — messages des stations TCQ réinjectés sur un canal configurable, préfixés `[TCQ-xx]`, avec **déduplication** et **anti-boucle (anti-écho)**.
- **Lecture active des messages MeshCore** (`get_msg`) — interroge directement le companion plutôt que de dépendre de l'auto-fetch d'événements, qui ne remonte pas toujours les messages de canal selon le firmware.
- **Fragmentation** — découpage automatique des listes/messages dépassant la taille utile MeshCore (`mc_max_chars`, défaut 140).
- **Gestion des canaux du companion** — bouton *Canaux…* : lister, créer/configurer le canal `tcq` (clé incluse), **QR de partage** au format de l'app MeshCore, et **import** d'une URL de canal copiée depuis l'app.
- **Arrêt fiable** — le bouton **Arrêter** ferme proprement la liaison MeshCore de façon **bornée** (le port série est libéré, au besoin de force, même si la pile tarde) et stoppe LXMF sans détruire Reticulum : l'état repasse à **Arrêté** et un **redémarrage immédiat** est possible.
- **Configuration Reticulum par défaut embarquée** — au tout premier lancement, si `~/.reticulum/config` est absent, MeshRNS y copie automatiquement la config fournie dans `reticulum_config/config` (une config existante n'est **jamais écrasée**).
- **Configuration persistante** (`meshrns.json`, rechargée au démarrage) + chargement/enregistrement de profils nommés.
- **Interface graphique** Tkinter (onglet *Connexion* défilable + onglet *Journal* temps réel), écran d'accueil, fenêtre *À propos*.
- **Modes console** — exécution sans interface (`--nogui`), auto-test (`--selftest`), génération de configuration (`--gen-config`).

---

## Prérequis

- Un **companion MeshCore** (nœud LoRa) connecté en USB/série (ou TCP / BLE), avec le **canal de service `tcq`** créé (même **nom** *et* même **clé** que les stations du réseau TCQ).
- La pile **Reticulum (`rns`)** et **LXMF** opérationnelle sur le poste, **avec la connexion RNS configurée dans TCQ-config** (éditeur de configuration Reticulum). MeshRNS réutilise cette configuration `~/.reticulum/config` ; il ne la modifie pas.
- Au moins une **interface Reticulum** active (RNode LoRa, TCPClientInterface vers un nœud RNS, AutoInterface…) pour joindre les stations TCQ.

> La pile RNS/LXMF n'est **pas** un service externe à lancer manuellement : MeshRNS l'initialise au démarrage. En revanche, **la configuration des interfaces Reticulum se fait dans TCQ-config**, pas dans MeshRNS.

---

## Installation
### 📥 [**Télécharger la dernière version pour Windows 11 (x64)**](https://github.com/f1gbd/F1GBD/releases/download/meshrns-v1.0.8/MeshRNS-v1.0.8-win64.7z)

*Archive **7-Zip** (.7z). Décompressez-la (Windows 11 nativement, ou [7-Zip](https://www.7-zip.org)), puis lancez `MeshRNS.exe`. Conservez `MeshRNS.png`, `MeshRNS.ico`, `meshrns.json` **et le dossier `reticulum_config/`** à côté de l'exécutable. L'annuaire `annuaire.json` est créé/maintenu au même endroit. Au premier lancement, si `~/.reticulum/config` n'existe pas, la configuration par défaut `reticulum_config/config` y est copiée automatiquement.*

---

## Démarrage rapide

1. **Préparez Reticulum dans TCQ-config** : vérifiez/créez la connexion RNS (interfaces, transport). MeshRNS s'y connectera automatiquement.
2. Lancez MeshRNS. L'onglet **Connexion** présente trois groupes de réglages.
3. **MeshCore (companion)** : choisissez le **Transport** (`serial`/`tcp`/`ble`), le **Port** (ex. `COM4`) et le **Baudrate**. Laissez **Lecture active (get_msg)** cochée.
4. **LXMF / Reticulum** : indiquez la **Station LXMF** de cette passerelle (un indicatif **`TCQ-*`**, ex. `TCQ-F1GBD`). Laissez **Config RNS** vide (= configuration de TCQ-config). Réglez au besoin l'**intervalle d'annonce** et le **préfixe de filtre** (`TCQ`).
5. **Lien & filtrage TCQ** : **Indicatif local**, **Mode d'émission** (`broadcast` ou `direct`), et — en mode direct — la **Station par défaut** (`peer_station`). Vérifiez le **Canal de service** (`tcq`). Laissez **Filtrer entrant (TCQ seul)** coché.
6. Au besoin, ouvrez **Canaux…** pour créer le canal `tcq` sur le companion (voir plus bas).
7. Cliquez **▶ Démarrer**. Le voyant passe à **● En service**. Suivez les échanges dans l'onglet **Journal** et l'annuaire via **Annuaire…**.

La configuration affichée est enregistrée automatiquement dans `meshrns.json` au démarrage et à la fermeture, puis rechargée au lancement suivant.

---

## Configuration (`meshrns.json`)

Exemple (passerelle **TCQ-F1GBD**, mode `broadcast`, canal de service `tcq`) :

```json
{
  "meshcore": {
    "transport": "serial", "port": "COM4", "baudrate": 115200,
    "tcp_port": 5000, "ble_address": "", "ble_pin": "",
    "manual_poll": true, "poll_interval": 1.0
  },
  "lxmf": {
    "station_name": "TCQ-F1GBD",
    "storage_path": "~/.meshrns",
    "reticulum_config": "",
    "auto_announce": true, "announce_interval": 600,
    "tcq_prefix": "TCQ", "path_timeout": 60
  },
  "local_call": "F1GBD",
  "link_mode": "broadcast",
  "peer_station": "TCQ-BBS-F1GBD",
  "broadcast_max_age_days": 7.0,
  "channels": [1], "channel_map": {}, "inject_channel": -1,
  "tcq_channel_name": "tcq", "service_channel": -1,
  "tunnel_direct_to_channel": -1,
  "tcq_filter_inbound": true,
  "sign_outbound": true, "signature": "",
  "antiloop_ttl": 30.0, "mc_max_chars": 140, "rx_dedup_ttl": 120.0,
  "annuaire_file": "annuaire.json", "rns_loglevel": 0, "log_file": ""
}
```

| Champ | Rôle |
| --- | --- |
| `lxmf.station_name` | Indicatif **LXMF** de la passerelle, doit commencer par **`TCQ`**. |
| `lxmf.storage_path` | Stockage de l'**identité LXMF** propre à la passerelle (adresse RNS stable). |
| `lxmf.reticulum_config` | Dossier de config RNS. **Vide = `~/.reticulum`** (configuré par TCQ-config). |
| `lxmf.auto_announce` / `announce_interval` | Annonce LXMF au démarrage puis périodiquement. |
| `lxmf.tcq_prefix` | Préfixe de filtrage des stations (défaut `TCQ`). |
| `lxmf.path_timeout` | Délai de recherche de chemin RNS avant émission (s). |
| `link_mode` | `broadcast` (toutes les stations TCQ fraîches) ou `direct` (une station). |
| `peer_station` | En mode `direct` : station TCQ cible par défaut (nom ou hash). |
| `broadcast_max_age_days` | En `broadcast` : ne viser que les stations vues depuis moins de N jours (`0` = toutes). |
| `channels` | Index des canaux MeshCore relayés vers LXMF (`[]` = tous). |
| `inject_channel` | Canal MeshCore de réinjection des messages LXMF (`-1` = canal de service). |
| `tcq_channel_name` | **Nom** du canal MeshCore de service (annuaire + relais), défaut `tcq`. |
| `service_channel` | Index explicite du canal de service (`-1` = résolu par nom). |
| `tcq_filter_inbound` | N'injecter sur MeshCore **que** les messages venant de stations TCQ. |
| `sign_outbound` / `signature` | Signer les messages relayés vers LXMF (en fin de message). Signature vide = **indicatif local**. |
| `tunnel_direct_to_channel` | Router les **DM** MeshCore vers un canal (`-1` = non routé). |
| `mc_max_chars` | Taille utile d'un message MeshCore / découpage (défaut 140). |
| `rx_dedup_ttl` / `antiloop_ttl` | Anti-doublon LXMF entrant / anti-écho du companion (s). |
| `rns_loglevel` | Verbosité de la pile RNS (`0` = silencieux, mute le spam d'interfaces ; `0..7`). |
| `annuaire_file` | Fichier de l'annuaire TCQ (défaut `annuaire.json`, à côté de l'exe). |

---

## L'annuaire TCQ et le canal de service `tcq`

L'annuaire est l'ensemble des stations **`TCQ-*`** découvertes via leurs **annonces LXMF** (mêmes données et même fichier `annuaire.json` que TCQ). Il sert à deux choses : savoir **vers qui** émettre (mode `broadcast`) et permettre la **consultation depuis le réseau MeshCore**.

Sur le **canal `tcq`**, un client MeshCore peut interroger l'annuaire en envoyant l'une de ces commandes (insensibles à la casse) :

| Commande | Effet |
| --- | --- |
| `ANNUAIRE` · `ANNU` · `DIR` · `LIST` · `?` · `TCQ?` · `QTC?` | Liste **toutes** les stations TCQ connues. |
| `ANNUAIRE <filtre>` (ex. `DIR BBS`) | Liste les stations dont le **nom** contient le filtre. |

La passerelle répond **sur le même canal**, sous la forme :

```
Annuaire TCQ (3):
1.TCQ-F1GBD     5436706f 2026-06-26 19:49
2.TCQ-F1ABC/HF  9672a8ca 2026-06-26 18:12
3.TCQ-F1XYZ     a1b2c3d4 2026-06-25 21:07
```

Les réponses trop longues sont **automatiquement découpées** à `mc_max_chars`. Côté GUI, le bouton **Annuaire…** affiche la même liste (nom, adresse LXMF, dernier contact) et permet de copier une adresse ou de la définir comme station directe.

Le bouton **« Importer annuaire TCQ… »** (fenêtre Annuaire) charge un `annuaire.json` complet (par ex. généré par TCQ) et le **fusionne** dans l'annuaire de MeshRNS : les stations **TCQ** sont ajoutées/mises à jour (le **contact le plus récent** est conservé), les entrées non-TCQ sont ignorées. Pratique pour **pré-charger** la passerelle sans attendre que toutes les stations s'annoncent. La fusion s'applique à l'annuaire en service (puis sauvegarde) ou directement au fichier si la passerelle est arrêtée.

---

## Modes d'émission MeshCore → LXMF

LXMF est un protocole **adressé** (pas de diffusion native), contrairement à VARA. MeshRNS propose donc :

- **`broadcast`** — chaque message du canal `tcq` est envoyé (multi-unicast) à **toutes les stations TCQ fraîches** de l'annuaire (`last_seen` < `broadcast_max_age_days`). Comportement « réseau » proche de TCQ.
- **`direct`** — chaque message est envoyé à la **station par défaut** (`peer_station`), équivalent d'une liaison point-à-point.
- **`@<station> texte`** — surcharge ponctuelle : le message n'est envoyé qu'à la station indiquée (par **nom** TCQ ou **hash** LXMF de 32 caractères), quel que soit le mode. Exemple : `@TCQ-56/HF SITREP recu, QSL.`

> **Préfixe d'expéditeur MeshCore.** Sur un canal, le firmware MeshCore ajoute le nom de l'émetteur en tête du message (`F1GBD/P: @TCQ-F1ABC/HF …`). Depuis la **v1.0.6**, MeshRNS détecte le `@cible` **même précédé de ce préfixe** ; le Journal le confirme par une ligne `Ciblage @TCQ-56/HF -> …`. Les messages relayés sont par ailleurs **signés** en fin de message avec l'indicatif (`sign_outbound`).

Pour chaque cible, MeshRNS effectue une **recherche de chemin RNS** (`request_path`, délai `path_timeout`) avant l'envoi.

---

## Filtrage TCQ (entrant)

Avec **`tcq_filter_inbound`** activé (défaut), seuls les messages LXMF provenant d'une **station TCQ connue/nommée** sont réinjectés sur MeshCore ; les autres sont ignorés et journalisés (`source non TCQ`). C'est l'équivalent du filtrage opéré par TCQ : le réseau MeshCore local ne voit que le trafic **`TCQ-*`**.

---

## Configurer le canal `tcq` depuis MeshRNS (bouton « Canaux… »)

Un companion ne **reçoit** les messages d'un canal que s'il a ce canal configuré localement (même **index** *et* surtout même **clé**). Le canal public (0) est connu de tous ; un canal privé inconnu du companion voit ses messages reçus mais non déchiffrables, donc ignorés en silence.

Le bouton **Canaux…** (barre du bas) ouvre une fenêtre qui :

- **liste les canaux réellement présents** sur le companion (index, nom, empreinte de clé) ;
- permet d'en **créer / configurer un** (par ex. `tcq`) : index (0-7), nom, et clé optionnelle (32 hexa). Si la clé est laissée vide, elle est **dérivée du nom** (`SHA-256(nom)`) : il suffit alors d'employer le **même nom de canal** sur toutes les extrémités pour obtenir la même clé.
- **« Lire le canal »** récupère le nom et la **clé** réels d'un index donné (pour comparer/copier la clé entre nœuds — c'est la clé, pas le nom, qui doit être identique partout).
- **« QR de partage… »** affiche un QR code au **format de l'app MeshCore** (`meshcore://channel/add?name=…&psk=<clé base64>`, clé incluse) : scanné depuis l'app (Canaux → Ajouter → Scanner un QR code), il ajoute le canal prêt à l'emploi.
- **« Importer »** fait l'inverse : collez l'URL d'un canal **copiée depuis l'app**, les champs Nom + Clé sont remplis, puis **Configurer ce canal** pose sur le companion **exactement la même clé** que le téléphone.

La fenêtre fonctionne que la passerelle soit démarrée (connexion active) ou arrêtée (connexion temporaire au companion). Au démarrage, MeshRNS journalise aussi la liste des canaux configurés et indique l'**index résolu** du canal de service `tcq`.

---

## Connexion Reticulum (via TCQ-config)

MeshRNS **ne configure pas** Reticulum : il réutilise la configuration RNS du poste, gérée par l'**éditeur de configuration Reticulum de TCQ-config** (`~/.reticulum/config`). Pour relier votre passerelle au reste du réseau TCQ, déclarez-y au moins une **interface** :

- une **TCPClientInterface** vers un nœud RNS de transport (réseau ADRASEC ou nœud public),
- et/ou une interface **RNode LoRa** / **AutoInterface** selon votre infrastructure.

MeshRNS possède sa **propre identité LXMF** (dossier `lxmf.storage_path`, défaut `~/.meshrns`), distincte de celle de TCQ : son adresse LXMF est donc stable et propre à la passerelle.

> **Configuration par défaut.** Au premier lancement, si aucun `~/.reticulum/config` n'existe, MeshRNS installe la configuration par défaut embarquée (`reticulum_config/config` : AutoInterface + nœuds de transport). Vous l'ajustez ensuite dans TCQ-config. Une configuration existante n'est jamais remplacée.

---

## Dépannage

- **Aucune ligne `MeshCore RX` à la réception d'un message de canal** → la lecture active (`get_msg`) doit être cochée ; certains firmwares ne déclenchent pas l'auto-fetch d'événements de canal.
- **`MeshCore RX` apparaît mais rien ne part en LXMF** → message filtré (vérifiez **Canaux relayés**) ou anti-écho (voir le Journal), ou **annuaire vide** en mode broadcast (aucune station TCQ encore annoncée).
- **`LXMF non démarré` / pas de connexion Reticulum** → la pile `rns`+`lxmf` n'est pas détectée, ou aucune interface RNS n'est configurée : vérifiez la connexion dans **TCQ-config**.
- **`source non TCQ` en réception** → message LXMF d'une station hors filtre `TCQ` : comportement normal (désactivable via `tcq_filter_inbound`).
- **Émission broadcast sans effet** → toutes les stations TCQ de l'annuaire sont trop anciennes (au-delà de `broadcast_max_age_days`) ou aucun **chemin RNS** n'a pu être trouvé (`path_timeout`).
- **`@station introuvable`** → la station n'est pas (ou plus) dans l'annuaire : laissez-la s'annoncer, ou utilisez son **hash** LXMF complet.
- **Canal `tcq` refusé sur le companion** → le canal n'existe pas avec la **même clé** : (re)configurez-le via **Canaux…** (QR de partage / Importer pour synchroniser la clé).
- **La passerelle ne s'arrête pas / impossible de redémarrer** → corrigé en **v1.0.8** (arrêt borné, port libéré au besoin de force). Mettez à jour si vous observez ce comportement sur une version antérieure.

---

## Licence & auteur

**MeshRNS** — *a Reticulum/LXMF Gateway for MeshCore* — par **F1GBD** (c) 2026 — **ADRASEC 77 / FNRASEC**.

## 📄 Documentation associée

- 📘 **[Manuel utilisateur MeshRNS](https://github.com/f1gbd/F1GBD/blob/master/meshrns/documentation/MEMO%20-%20MANUEL%20MeshRNS.pdf)** — Manuel Utilisateur et Paramétrage de MeshRNS
- 📋 **[Fiche technique MeshRNS](https://github.com/f1gbd/F1GBD/blob/master/meshrns/documentation/MEMO%20-%20Fiche%20Technique%20MeshRNS.pdf)** — Fiche Technique MeshRNS

---

<div align="center">

### 📡 Auteur

**Jean-Louis Naudin (F1GBD)**
*ADRASEC 77 — FNRASEC*

**Version 1.0.8 — Juin 2026**

---

*Pour toute question, contactez votre référent ADRASEC départemental.*

</div>
