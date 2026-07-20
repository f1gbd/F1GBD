<div align="center">
<img src="images/RatSpeak_Adrasec_Logo.png" alt="RWLoRa" width="320">
</div>

# RTspk Pager — Ratspeak édition RASEC-ALERT (F1GBD/ADRASEC 77)

**Récepteur d'alerte (pager) pour réseau Reticulum / LXMF**, basé sur
l'application [Ratspeak](https://github.com/ratspeak/Ratspeak) avec l'ajout de
la fonction **RASEC-ALERT** portée du MeshPager / de l'édition Saitama T-Deck.

Un message **LXMF** reçu contenant le code d'activation déclenche sur l'appareil :
un **écran plein écran clignotant « RASEC ALERT »** (avec compteur d'alertes),
une **sirène bitonale** synthétisée (aucun fichier son requis), et un **accusé
de réception automatique** renvoyé à l'expéditeur. Sur mobile, une **notification
native** est également émise.

**RTspk Pager** est compatible avec le logiciel **TCQ** (désactiver le mode quantique)

> Application Android — fonctionne sur téléphone/tablette et sur le LilyGO T-Deck
> (Android). Version desktop possible en compilant depuis les sources.

<div align="center">
<img src="images/RatSpeak_RASEC-ALERT.png" alt="RWLoRa" width="380">
</div>

---

## Téléchargement et installation (Android)

1. Télécharger l'APK (lien direct) : **[RTspk_pager-1.0.26.apk](https://github.com/f1gbd/F1GBD/releases/download/1.0.26/RTspk_pager-1.0.26.apk)**.
2. Sur le téléphone, autoriser l'installation depuis cette source (« sources
   inconnues » / « Installer des applications inconnues »).
3. Ouvrir le fichier APK et installer.
4. Au premier lancement, créer/importer une identité Reticulum et configurer au
   moins une interface (LoRa/RNode, TCP, WiFi/BLE…) dans *Settings*.

> **Nouveau en 1.0.26 — préréglage radio par défaut « France (868 MHz) ».**
> À la création d'une interface LoRa/RNode, les paramètres par défaut sont :
> **867,5 MHz · SF 8 · 125 kHz · CR 5 · TX 18 dBm**, avec limite d'airtime
> réglementaire (**1,5 % / heure**, **33 % / 15 s**). Tout reste modifiable dans
> *Settings → interface LoRa*.

---

## Utilisation de la fonction RASEC-ALERT

Depuis un autre nœud Reticulum/LXMF (autre RTspk Pager, Ratspeak, MeshChat…),
envoyer un **message** vers l'adresse LXMF de l'appareil :

| Commande | Effet |
|---|---|
| `#ra ADRASEC77` | Déclenche l'alerte (écran clignotant + sirène + ACK). |
| `#rapass <ancien> <nouveau>` | Change le code d'activation (persisté). |
| `#b <n>` | Règle le nombre de répétitions de la sirène. `#b 0` = alarme **continue** jusqu'à acquittement. Plage : 0–20. |

- Code d'activation par défaut : **`ADRASEC77`** (modifiable via `#rapass`).
- **Acquittement** : toucher/cliquer l'écran, ou Échap / Entrée / Espace.
- L'accusé renvoyé (« Pager OK - alerte bien recue ») ne contient jamais le code,
  pour éviter toute boucle d'auto-déclenchement.
- Le message déclencheur reste affiché normalement dans la conversation.

> **Audio (mobile).** Selon Android, le son peut ne démarrer qu'après une
> première interaction avec l'application (déverrouillage du contexte audio) ;
> l'écran d'alerte, lui, s'affiche toujours.

---

## Mise à jour

*Settings → (bas de page) → « Check for updates »* interroge les *Releases* de ce
dépôt. Installer manuellement la dernière version publiée ici : il n'y a pas de
mise à jour automatique (raisons de confidentialité).

---

## Licence et code source

RTspk Pager dérive de **Ratspeak**, distribué sous **GNU AGPL-3.0-or-later**.
Conformément à cette licence, le **code source correspondant** de cette version
modifiée est mis à disposition :

- Sources d'origine : https://github.com/ratspeak/Ratspeak (+ les bibliothèques
  frères rsReticulum / rsLXMF / rsLXST / lrgp-rs).
- Modifications RASEC-ALERT (méthode patch) : le fichier
  **`ratspeak-rasec-alert-f1gbd.patch`** fourni dans ce dossier s'applique sur une
  copie propre des sources Ratspeak (`git apply ratspeak-rasec-alert-f1gbd.patch`).
- Préréglage LoRa « France (868 MHz) » par défaut (1.0.26) : le fichier
  **`rtspk-france-preset-f1gbd.patch`** fourni dans ce dossier.
- Procédure de build de l'APK sous Windows : voir `BUILD-APK-WINDOWS.md`.

En reversant vos modifications, merci de respecter les termes de l'AGPL-3.0.

---

## Crédits

- Application **Ratspeak** — Ratspeak Contributors.
- Basé sur **Reticulum / LXMF**.
- Portage et build de l'option **RASEC-ALERT** : **F1GBD — ADRASEC 77 / FNRASEC**.

73 !
