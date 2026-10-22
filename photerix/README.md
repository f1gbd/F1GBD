<p align="center">
  <img src="images/PHOTERIX_logo.png" alt="PHOTERIX" width="300">
</p>

<h1 align="center">PHOTERIX</h1>
<p align="center"><b>Images sans frontières — des photos en Packet AX.25 VHF/UHF, du smartphone au portatif</b></p>

<p align="center">
  <a href="https://github.com/f1gbd/F1GBD/releases/download/photerix-v1.7.1/PHOTERIX-1.7.1.apk"><b>📥 Télécharger PHOTERIX v1.7.1 (APK Android)</b></a>
  &nbsp;·&nbsp;
  <a href="documentation/MANUEL_PHOTERIX.pdf"><b>📚 Manuel (PDF)</b></a>
</p>

---

## 📸 En bref

PHOTERIX est une application Android qui permet à des opérateurs de **s'échanger des photos prises avec leur smartphone par radio**, en **Packet AX.25 1200 bauds**, en VHF ou en UHF, sans réseau mobile ni Internet.

Le smartphone est relié par **câble de programmation + adaptateur OTG** à un portatif Quansheng qui sert de TNC :

| Portatif | Application TNC sur la radio |
|---|---|
| UV-K1 / UV-K5 v3 (firmware F4HWN) | **KISS-TNC** |
| UV-K5 v1 | **TACVYR** (mode KISS) |
| VR-N76, VR-N7600, UV-Pro, GA-5WB | TNC KISS intégré, **en Bluetooth** (aucun câble) — testé en réel sur VR-N76 et VR-N7600 |

Le protocole image est **celui de TCQ** : une station **TCQ** et un smartphone **PHOTERIX** s'envoient leurs photos dans les deux sens, accusés de réception compris. Un poste de commandement sous TCQ reçoit donc directement les photos du terrain.

<p align="center">
  <img src="images/PHOTERIX_viseur.jpg" alt="Le viseur de PHOTERIX" width="340">
</p>

## ✨ Fonctions

- **Viseur plein écran** façon appareil photo, avec déclencheur, lampe et **zoom** de la caméra principale (pincer le viseur, pastille 1× · 2× · 4×).
- **Photo de l'album** du téléphone, ou **selfie** avec la caméra frontale (bouton SELFIE).
- **CHAT Packet** pour se coordonner avec les équipes avant et après une photo : messages en clair, lus et envoyés aussi par le chat TNC Packet de TCQ, phrases courantes d'un toucher, alerte des messages adressés à la station.
- **Message court** (60 caractères) et **indicatif de la station** joints à la photo ; en option, ils sont **incrustés** sur l'image avec l'heure UTC.
- **Trois modes de compression de TCQ** et qualité JPEG réglable de 5 à 50, avec **aperçu de l'image telle qu'elle sera reçue**, sa taille, son nombre de trames et sa durée d'émission.
- **Réception en direct** : l'image apparaît pendant qu'elle arrive, trame après trame ; alerte sonore et vibreur, notification écran éteint.
- **Accusés de réception** au format TCQ, dans les deux sens.
- **Archives locales** de toutes les photos émises et reçues : revoir, zoomer, **renvoyer**, **relayer** vers une autre station, copier dans la galerie.
- **Liaison maintenue écran éteint** : le téléphone en poche reçoit et accuse les photos.
- **Journal radio** des trames, accusés, messages et radiogrammes TCQ reçus.
- **TACVYR** dans le CHAT : messages tactiques courts, sans phonie, choisis par code comme sur le UV-K1 (9 rubriques × 9 phrases : « EQUIPE BRAVO SUR ZONE »).
- **RGRAM** dans le CHAT : **radiogramme ADRASEC authentifié** (TOTP + CRC), au format de TCQ, lu par les stations TCQ et, en option, par les pagers UV-K1 ; radiogrammes reçus vérifiés (CRC) et accusés par leur destinataire.
- **EMAIL PAR RADIO (ICS-213)** (bouton enveloppe du CHAT) : formulaire ICS-213 de FLmsg envoyé en Packet comme TCQ ; une **passerelle SMTP** — station TCQ, ou **PHOTERIX relié à Internet** — le transmet aux adresses email du champ To (séparées par « ; ») et renvoie le compte rendu de l'envoi.
- **CARTE TACTIQUE** (bouton carte du CHAT) : carte OpenStreetMap **hors-ligne** (zone enregistrée ou cartes .mbtiles), stations APRS reçues avec leur indicatif, **points nommés** (Roméo 1…), et **touches MFD** qui composent ordres et comptes rendus en un toucher : Roméo 1 + GO → « Bravo 1, allez au point Roméo 1 ».
- **Position GPS en APRS** depuis le CHAT : TCQ place l'opérateur sur sa carte ; les positions reçues s'ouvrent sur une carte.
- **TNC Bluetooth** : VR-N76, VR-N7600, UV-Pro, GA-5WB (TNC KISS intégré, profil SPP), sans câble ; rythme d'envoi adapté et **reconnexion automatique** si la radio cesse de répondre, la file d'émission reprend d'elle-même.
- **Accusés de réception étalés** : plusieurs stations à l'écoute ne se brouillent plus (avec TCQ v14.3.3).

## 🗺️ Carte tactique

Le bouton **carte** du CHAT ouvre une carte OpenStreetMap faite pour le terrain, **utilisable sans réseau**.

<p align="center">
  <img src="images/PHOETRIX_TACMAP.jpg" alt="PHOTERIX v1.5 : la carte tactique sur le terrain (forêt de Fontainebleau)" width="340">
</p>

> ✅ **Testé en réel** avec un VGC VR-N76 et un VR-N7600 (TNC KISS en Bluetooth), face à une station **TCQ v14.3.3** sur FT-817 + SCU-17 : carte tactique et ordres MFD validés.

- **Ma station** : la carte s'ouvre sur la position GPS. Sans GPS, un appui long → « Ma position ici » place la station à la main ; le bouton ◎ revient au GPS.
- **Stations distantes** : chaque position APRS reçue en AX.25 (PHOTERIX, TCQ, APRSdroid…) pose la station avec son indicatif et l'âge de sa position (vert : moins de 30 min). Un appui long lui donne un **nom d'équipe** (Bravo 1, Alpha 2…).
- **Points nommés** : appui long → « Point nommé ici » (Roméo 1, Roméo 2…). On peut les renommer, déplacer, supprimer, ou les **partager aux autres PHOTERIX** (objet APRS).
- **Hors-ligne** :
  - avec réseau, ⬇ « Enregistrer la zone affichée » avant la mission ;
  - sans réseau du tout, copier des cartes **.mbtiles** préparées sur PC (MOBAC, QGIS…) dans `Android/data/fr.f1gbd.photerix/files/cartes` ;
  - au-delà du zoom enregistré, la carte agrandit la tuile la plus proche.
- **Vision de nuit** (☾), émission de sa position APRS depuis la carte, dernier message reçu en bandeau.

### 🎛️ Les touches MFD : ordres et comptes rendus

| Groupe | Touches |
|---|---|
| **Navigation** (cyan, en haut) | GO · ETA · ARR · PASS · EXIT · HOLD · RTB |
| **Recherche** (ambre) | RAS · FIND · VICTIM · TRACE · SEARCH |
| **État** (vert) | OK · WAIT · DONE · BLOCK · LOST |
| **Assistance** (rouge) | HELP · MEDIC · REINF · EXTRACT |

On touche une **station** (l'équipe), un **point**, puis une **touche** : le message se compose, on le relit, puis **▲ ÉMETTRE**.

| Touche | Message (équipe Bravo 1, point Roméo 1) |
|---|---|
| GO | « Bravo 1, allez au point Roméo 1 » |
| ARR | « Bravo 1, Roméo 1 atteint » |
| PASS | « Bravo 1, nous passons Roméo 1 » |
| RAS | « Bravo 1, RAS au point Roméo 1 » |
| HELP | « Bravo 1, assistance demandée à Roméo 1 » |
| VICTIM | « Bravo 1, victime localisée à Roméo 1 » |
| ETA | « Bravo 1, arrivée au point Roméo 1 dans 15 min » (délai au choix) |

- **Au PCO** : toucher la station Bravo 1 puis Roméo 1, puis GO. L'ordre part vers l'indicatif de Bravo 1.
- **Sur le terrain** : sans station choisie, le message part au nom de **sa propre équipe**, vers le PCO. Le nom d'équipe et le destinataire se règlent avec le bouton ⚙ de la carte.
- Les messages partent **en clair**, comme le CHAT : ils sont lus par TCQ, les UV-K1/K5 et les pagers.

## ✉️ Email par radio : ICS-213

Le bouton **enveloppe** du CHAT ouvre le formulaire **ICS-213 (General Message)** de FLmsg.

1. **To** : une ou plusieurs adresses email séparées par « ; » (`equipe@exemple.fr; pcc@exemple.org`), **Sub.** (objet), **Message**.
2. **Station TCQ** : l'indicatif de la station TCQ dont la **passerelle email (SMTP)** est en service.
3. **✉ TRANSMETTRE** : le fichier `.213`, identique à celui de FLmsg, part en Packet par la procédure FLmsg de TCQ (`FLMSG|nom|C|…` en trames `{QF:`). TCQ l'envoie par email à chaque adresse, le fichier .213 en pièce jointe, puis accuse réception.

Les adresses déjà utilisées sont proposées d'un toucher sous le champ To ; un **appui long** sur l'une d'elles la retire de la liste.

### 🌐 PHOTERIX passerelle email

Un smartphone PHOTERIX **relié à Internet** (4G, Wi-Fi) peut servir de passerelle aux équipes en **zone blanche**, comme une station TCQ :

1. ⚙ Réglages → **PASSERELLE EMAIL (SMTP)** : activer le routage, puis renseigner le serveur, le port, l'utilisateur, le mot de passe et l'expéditeur, avec **TLS (587)** ou **SSL (465)**. Ce sont les mêmes champs que dans TCQ. **🔌 TESTER** s'envoie un email de contrôle.
2. L'équipe en zone blanche met l'indicatif de cette station dans le champ **Passerelle** de son ICS-213.
3. La passerelle reçoit le message, l'envoie aux adresses du champ To (.213 en pièce jointe), puis répond par radio :
   - `[ACK] Email envoyé à equipe@exemple.fr, pcc@exemple.org le …`
   - `[ACK] Email NON envoyé : <raison> le …`

L'équipe voit ce compte rendu dans son CHAT (✓ ou ✕).

Si la passerelle ne route pas un message, elle dit pourquoi dans son CHAT : message adressé à une autre station, passerelle désactivée, aucune adresse dans To.

> ✅ **Testé en réel** le 21 octobre 2026 : PHOTERIX en zone blanche → PHOTERIX passerelle (Gmail, TLS 587) → email reçu, comptes rendus revenus par radio.

> 💡 Gmail : validation en deux étapes et **mot de passe d'application**.

## 🗜️ Les trois modes

| Mode | Résolution | Taille typique (Q20) | Trames | Durée ≈ |
|---|---|---|---|---|
| **ÉCLAIR** | 80 × 60 | ≈ 1 Ko | ≈ 9 | 15 s |
| **STANDARD** (défaut de TCQ) | 160 × 120 | ≈ 3 Ko | ≈ 23 | 35 s |
| **DÉTAIL** | 320 × 240 | ≈ 8 Ko | ≈ 65 | 1 min 40 |

Ce sont les résolutions de la fenêtre « Image Packet VHF » de TCQ. Une photo en portrait garde son sens (120 × 160 en STANDARD). Les durées comptent le TXDELAY de 800 ms et des trames enchaînées dans une seule émission.

## 🔌 Raccordement

<p align="center">
  <img src="images/schema_raccordement.png" alt="Raccordement : smartphone, OTG, câble de programmation, UV-K1/UV-K5" width="760">
</p>

1. Lancer **KISS-TNC** (UV-K1, UV-K5 v3) ou **TACVYR en mode KISS** (UV-K5 v1) sur le portatif, sur la fréquence Packet du réseau.
2. Brancher le **câble de programmation** sur la prise K du portatif et, par un **adaptateur OTG**, sur le téléphone.
3. Android propose d'ouvrir PHOTERIX : accepter (l'accès USB est alors accordé) — ou toucher la pastille **TNC** en haut de l'écran.

Câbles reconnus : CH340/CH341, CP210x, FTDI, PL2303 et CDC-ACM. Débit **38400 bauds** par défaut.

<p align="center">
  <img src="images/PHOTOTERIX_smartphone.jpg" alt="Le viseur de PHOTERIX" width="640">
</p>

<p align="center">
  <img src="images/PHOTERIX_VR-N76.jpg" alt="PHOTERIX et un VR-N76 en Bluetooth" width="640">
</p>

<p align="center">
  <img src="images/PHOTOTERIX_VR-N7600.jpg" alt="PHOTERIX et un VR-N7600 en Bluetooth" width="640">
</p>

## 📡 Compatibilité TCQ

| | PHOTERIX → TCQ | TCQ → PHOTERIX |
|---|---|---|
| Trames | UI AX.25, PID F0, `{QI:ID:NN/TT:…` de 170 caractères | idem |
| En-tête | `IMG\|<message ou nom>\|<LxH>\|<JPEG en Base64>` | `IMG\|<fichier>\|<LxH>\|…` |
| Accusé | `[ACK] Image reçu le …` renvoyé par TCQ | renvoyé par PHOTERIX |
| CHAT | message en clair dans une trame UI, lu dans le chat TNC Packet de TCQ | idem |
| TACVYR | message tactique en clair (1 ou 2 phrases codées), vers CQ | idem, depuis un UV-K1/K5 |
| Radiogramme | `{QR:ID:NN/TT:…`, zlib + Base64, AUTH TOTP/CRC de TCQ (80 caractères en format pager UV-K1) | lu dans le CHAT, CRC vérifié |
| Position | balise APRS `=DDMM.mmN/DDDMM.mmE[…` vers APZPHX, sur la carte de TCQ | bulle 📍 dans le CHAT |
| ICS-213 | `FLMSG\|nom\|C\|base64(zlib)` en trames `{QF:…`, fichier FLmsg 4.0.24 ; routé par email par TCQ | reçu, affiché dans le CHAT ; routé par email si PHOTERIX est passerelle |
| Compte rendu email | `[ACK] Email envoyé à … le …` / `[ACK] Email NON envoyé : … le …` (passerelle PHOTERIX) | affiché dans le CHAT |
| Ordres MFD | message en clair (« Bravo 1, allez au point Roméo 1 »), lu dans le chat de TCQ | idem |
| Point nommé | objet APRS `;Romeo 1  *…` vers APZPHX : entre PHOTERIX (TCQ l'affiche en texte) | |
| Accusés | 3 à 14 s après la dernière trame, créneau au hasard, canal libre (TCQ v14.3.3) | idem |
| Paramètres KISS | TXDELAY 800 ms, Persistence 128, Slot Time 30 ms (TCQ v14.3.2) | |

Le message de l'opérateur voyage dans le champ « nom » de l'en-tête : TCQ l'affiche à la réception (« IMAGE reçue de F4JHW : Pont coupé RD12 »). Côté PHOTERIX, l'émission respecte la mémoire du TNC (900 octets au plus en attente, comme TCQ v14.3 en mode série).

Compatibilité vérifiée **au bit près** avec le code Packet de TCQ v14.3.2, dans les deux sens.

## ⚙️ Réglages

- **Station** : indicatif et SSID (7 par défaut, portatif).
- **Liaison TNC** : câble, débit, DTR/RTS, connexion automatique au branchement.
- **Paramètres KISS** : TXDELAY, Persistence, Slot Time (bouton « Valeurs de TCQ »).
- **Transmission** : destination par défaut, digipeaters, mode par défaut, incrustation, original pleine définition gardé, accusés automatiques.
- **Passerelle email (SMTP)** : routage des ICS-213 reçus, serveur, port, identifiants, TLS/SSL, bouton de test.
- **Alertes** : son, vibreur, écran toujours allumé sur le viseur.

## 🗂️ Archives

Les photos sont rangées dans `Android/data/fr.f1gbd.photerix/files/Pictures/PHOTERIX` — lisible depuis un PC par le câble USB — avec le journal radio (`journal_radio.log`). Le fichier gardé est exactement le JPEG passé sur l'air ; pour une photo émise, l'original pleine définition peut être conservé à côté.

## 📚 Documentation

- **[Manuel d'utilisation et de paramétrage (PDF)](documentation/MANUEL_PHOTERIX.pdf)** — raccordement du portatif, réglages, émission, réception, CHAT, TACVYR, radiogramme, ICS-213 (email) et passerelle email, carte tactique, archives, trafic avec TCQ, dépannage.

## 📱 Configuration requise

- Android 7.0 ou plus récent, avec **USB OTG** (ou Bluetooth pour les VR-N76 / VR-N7600) ; GPS pour la carte tactique.
- Un portatif Quansheng sous KISS-TNC ou TACVYR, et son câble de programmation.

---

*Jean-Louis (F1GBD / F4JHW) — ADRASEC 77 — FNRASEC*

---

## Licence

**Licence** : [PolyForm Noncommercial 1.0.0](LICENSE) — utilisation gratuite pour un usage personnel ou radioamateur, et par les associations (ADRASEC, FNRASEC…), les organismes de sécurité civile et les services publics ; **tout usage commercial est interdit**. Les versions publiées avant octobre 2026 restent régies par la licence qui les accompagnait.

