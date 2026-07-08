# MeshPager — PAGER RASEC ALERT (MeshCore / Heltec V3)

Transforme un module **Heltec WiFi LoRa 32 V3** (firmware companion BLE MeshCore v1.16)
en **pager d'alerte** pour la chaîne ADRASEC. À réception d'une commande d'activation
envoyée en chat (depuis TCQ ou une application cliente MeshCore), le pager signale
l'alerte de façon **visuelle et sonore** et confirme la bonne réception à l'émetteur.

> Projet **ADRASEC 77 / FNRASEC** — F1GBD / F4JHW. Usage exercices et opérations SATER / ORSEC.

<p align="center">
  <img src="images/Rasec-Alert_logo.jpg" width="560" alt="RASEC ALERT"/>
</p>

<p align="center">
  <img src="images/Meshcore_Pager.png" width="560" alt="RASEC ALERT"/>
</p>


---

## Fonctionnement

À réception de la commande **`#ra <code>`** (message direct ou canal) :

- **Écran OLED** : affichage plein écran « RASEC ALERT ».
- **LED blanche** : clignotement rapide par **séries de 3 impulsions**.
- **Buzzer piezo** (sur **GPIO 4**) : **3 bips** par défaut (réglable par `#b <n>`).
- **Alarme continue** possible (`#b 0`) : bips en boucle jusqu'à **acquittement** par la touche **USER**.
- **Accusé de réception** : renvoyé automatiquement à l'émetteur (message direct).
- **Écran d'accueil** dédié : titre, signature et **compteur d'alertes reçues**.
- **Émission CHAPPE 26** *(v5.0)* : le pager peut aussi **émettre** un code Chappe à 4 chiffres sur le canal privé — voir [Émettre un code Chappe](#émettre-un-code-chappe-chappe-26).

<p align="center">
  <img src="images/rasec_pager.gif" width="440" alt="Pager recevant l'alerte RASEC en direct"/>
</p>
<p align="center">
  <img src="images/raserc_pager.jpeg" width="440" alt="Pager Heltec V3 affichant RASEC ALERT"/>
</p>

<p align="center"><em>Réception d'une alerte « RASEC ALERT » sur un pager Heltec V3.</em></p>

---

## Paramètres radio (France)

Le firmware est compilé avec les paramètres LoRa ADRASEC pour la France :

| Fréquence | Bande passante | Spreading Factor | Coding Rate |
|---|---|---|---|
| **869.618 MHz** | **62.5 kHz** | **8** | **8** |

Ces valeurs sont figées au build (flags `LORA_FREQ / LORA_BW / LORA_SF / LORA_CR`).

> ⚠️ **Effacer la mémoire au flashage.** MeshCore enregistre les paramètres radio :
> les valeurs figées ne s'appliquent qu'à l'initialisation. Lors du flashage, choisir
> **« Erase device / Effacer »** pour qu'elles prennent effet — sinon les réglages
> précédemment enregistrés persistent. Vérification : bouton **USER** → page radio,
> lire `FQ 869.618 · BW 62.50 · SF 8 · CR 8`.

Tous les nœuds du réseau doivent partager **exactement** ces paramètres pour communiquer.

---

## Matériel

- **Heltec WiFi LoRa 32 V3** (ESP32-S3, écran OLED 0,96", LED blanche, bouton USER).
- Câble USB-C.
- **Buzzer piezo passif** sur **GPIO 4** (borne + sur GPIO 4, borne − sur GND).
- (Optionnel) module relais pour une variante TOR.

---

## Buzzer (GPIO 4)

Le firmware active un **buzzer piezo passif** sur **GPIO 4** : à chaque `#ra <code>`
reçu, le pager émet **3 bips** (et un court jingle au démarrage). Câblage direct :

```
GPIO 4  ──►│─── borne +  (piezo passif)
GND     ────── borne −
```

> Piezo **passif** requis (pas un buzzer actif auto-oscillant). Pour un buzzer plus
> puissant, l'interposer via un transistor (voir fiche technique).

---

## Flashage (opérateurs)

### ⚡ Méthode 1 — Bouton « Install » en un clic (recommandé)

➡️ **[Installer le firmware Pager](https://f1gbd.github.io/F1GBD/meshpager/)**  (Chrome ou Edge)

Brancher la Heltec V3 en USB, cliquer **Installer le firmware Pager**, **choisir
« Erase device / Effacer »** (pour appliquer les paramètres radio France), laisser
flasher, puis **RST**. Le binaire est servi par GitHub Pages (même origine), donc le
flashage web fonctionne directement.

> Connexion impossible ? Maintenir **BOOT**, appuyer/relâcher **RST**, relâcher **BOOT**, puis réessayer.

### Méthode 2 — Télécharger le binaire et flasher

1. Télécharger **[`pager_rasec_heltecv3.bin`](https://github.com/f1gbd/F1GBD/releases/latest/download/pager_rasec_heltecv3.bin)** (dernière release).
2. Ouvrir **https://espressif.github.io/esptool-js/** (Chrome/Edge), **Connect**, effacer la flash, fichier à l'adresse `0x0`, **Program**.

### Méthode 3 — esptool (ligne de commande)

```bash
pip install esptool
esptool --chip esp32s3 --port COM3 --baud 921600 erase_flash
esptool --chip esp32s3 --port COM3 --baud 921600 write_flash 0x0 pager_rasec_heltecv3.bin
```

---

## Appairage Bluetooth (BLE)

Pour configurer le pager depuis l'application MeshCore, l'appairage BLE demande un
**code PIN**. Ce PIN s'affiche **au démarrage**, sur l'écran de logo (splash), sous la
date :

```
Pin BLE: 772677
```

- Le PIN est **fixe** (`772677`) grâce au flag `-D BLE_PIN_CODE=772677`. Sans ce flag,
  il est **aléatoire** et régénéré à chaque démarrage (à relire au splash).
- Dans l'appli MeshCore : lancer l'appairage, puis saisir ce code.

> ℹ️ Après un flashage **Erase**, l'identité du nœud change : il faut **re-ajouter le
> pager comme contact** dans TCQ / l'application (il ré-émet une annonce au démarrage)
> avant de pouvoir lui envoyer un message direct.

---

## Utilisation

Depuis TCQ ou une application cliente MeshCore, envoyer au pager (message direct
recommandé, ou canal commun) :

```
#ra ADRASEC77
```

- Le préfixe `#ra` doit être en début de message, suivi d'un espace puis du **code exact** (casse respectée).
- Un code erroné ne déclenche rien.
- En message direct, l'émetteur reçoit l'accusé « Pager OK - alerte bien recue ».

Le code d'activation par défaut est `ADRASEC77` ; il se personnalise au build
(`-D PAGER_ACTIVATION_CODE`). Il peut aussi être **changé à distance**, uniquement en
**message direct** (jamais sur un canal) :
```
#rapass <ancien_code> <nouveau_code>
```
Le pager répond « Code RASEC mis a jour » ; le nouveau code est persistant (survit au redémarrage).

### Nombre de bips et alarme continue

Le nombre de bips de l'alarme se règle **uniquement en message direct** (jamais sur un canal),
valeur **persistante** :
```
#b <n>
```
- `#b 5` → l'alarme sonnera **5 bips** (défaut : **3**). Réponse : « Bips d'alarme regles sur 5 ».
- `#b 0` → **alarme continue** : séquences de 3 bips espacées d'~1 s, **indéfiniment**, jusqu'à ce qu'un opérateur **acquitte** en appuyant sur la touche **USER** (bouton du haut du Heltec V3). Le pager affiche alors « Alerte acquittee ».

> La touche **USER** acquitte / coupe toute alerte en cours (même une alerte normale de quelques secondes). En mode continu, une **borne de sécurité de 30 min** coupe l'alarme si personne n'acquitte.

> ⚠️ **Important — commandes de configuration en message direct uniquement.** Les commandes
> `#b` et `#rapass` ne sont traitées que sur le chemin **message direct** : envoyées sur un
> **canal**, elles sont **ignorées**. Règle d'usage : **on configure en DM** (`#b`, `#rapass`),
> **on alerte via le canal** (`#ra`).

---
### Émettre un code Chappe (CHAPPE 26)
---

Depuis la **v5.0**, le pager peut **émettre** un code Chappe à 4 chiffres directement depuis
le terrain, **sans téléphone ni application et sans besoin d'Internet**. Cette méthode est **à utiliser uniquement en situation extrême et en cas d'urgence**.

<p align="center">
  <img src="images/MeshPager_FOMEC_Chappe26.png" width="560" alt="RASEC ALERT"/>
</p>

Un message de type Chappe26 est **préfixé par `!`** (ex. `!2104`) sur le **canal privé** ADRASEC, où il est lisible par
tous les opérateurs abonnés au canal.
> Format du code : 1er chiffre = **Domaine**, 2e = **Sous-catégorie**, 3e et 4e = **Expression**

- (Pour plus de détails consulter le *[Livret Chappe26](https://github.com/f1gbd/F1GBD/blob/master/meshpager/documentation/Chappe26_Livret_B5.pdf)*.

**Saisie à la touche USER :**

1. Depuis l'accueil, aller sur la **page 2 « Recent Advert »** (appuis courts pour naviguer), puis **appui LONG** → entrée en mode **CHAPPE 26**.
2. **Appui COURT** : fait défiler le chiffre courant (`0 → 9`).
3. **Appui LONG** : valide le chiffre et passe au suivant.
4. Après les 4 chiffres, un **5ᵉ chiffre de confirmation** : `1` = **envoi**, `0` = **annulation**.

L'écran affiche « CHAPPE 26 », le code en cours (chiffre courant entre crochets) et le rappel
des touches. À l'émission, le pager affiche « Chappe: envoye ». **30 s** d'inactivité annulent
la saisie.

Le code est émis sur le canal d'index `CHAPPE_CHANNEL_IDX` (**= 1** par défaut, le **même** que
celui du RASEC ALERT collectif) : les nœuds inscrits reçoivent « `<Nom> : !2104` ».

> Sans conflit avec le buzzer : la bascule buzzer reste sur l'**appui long de la page 1**
> « RASEC ALERT » ; l'entrée CHAPPE 26 est réservée à l'**appui long de la page 2** « Recent Advert ».
- 📘 **Livret Code Chappe26** : [`Chappe26_Livret_B5.pdf`](https://github.com/f1gbd/F1GBD/blob/master/meshpager/documentation/Chappe26_Livret_B5.pdf)
- 📘 **Fiche Exemple Chappe26 Blackout** : [`Fiche_Exemple_Blackout.pdf`](https://github.com/f1gbd/F1GBD/blob/master/meshpager/documentation/Chappe26_Fiche_BlackOut.pdf)
- 📘 **Fiche Exemple Chappe26 Incendie** : [`Fiche_Exemple_Incendie.pdf`](https://github.com/f1gbd/F1GBD/blob/master/meshpager/documentation/Chappe26_Fiche_Incendie.pdf)
---
MeshPager est disponible sur LILYGO T-Deck
---
<p align="center">
  <img src="tdeck/images/rasec-alert-demo.gif" width="300" alt="Pager recevant l'alerte RASEC en direct"/>
</p>
Voir : https://github.com/f1gbd/F1GBD/tree/master/meshpager/tdeck/

---
## Documentation

- 📄 **Fiche réflexe** (envoyer / tester l'alerte) : [`Fiche_reflexe_RASEC_ALERT.pdf`](https://github.com/f1gbd/F1GBD/blob/master/meshpager/documentation/Fiche_reflexe_RASEC_ALERT.pdf)
- 📘 **Fiche technique** (mise en œuvre complète) : [`Fiche_PAGER_RASEC_ALERT_ADRASEC.pdf`](https://github.com/f1gbd/F1GBD/blob/master/meshpager/documentation/Fiche_PAGER_RASEC_ALERT_ADRASEC.pdf)
- 📘 **Livret Code Chappe26** : [`Chappe26_Livret_B5.pdf`](https://github.com/f1gbd/F1GBD/blob/master/meshpager/documentation/Chappe26_Livret_B5.pdf)
- 📘 **Fiche Exemple Chappe26 Blackout** : [`Fiche_Exemple_Blackout.pdf`](https://github.com/f1gbd/F1GBD/blob/master/meshpager/documentation/Chappe26_Fiche_BlackOut.pdf)
- 📘 **Fiche Exemple Chappe26 Incendie** : [`Fiche_Exemple_Incendie.pdf`](https://github.com/f1gbd/F1GBD/blob/master/meshpager/documentation/Chappe26_Fiche_Incendie.pdf)

---

Options (buzzer, textes, durées) : voir la fiche technique.


## Auteur & licence

**Jean-Louis — F1GBD**, ADRASEC 77.
Basé sur MeshCore (voir la licence du projet MeshCore pour le firmware de base).

73 !
