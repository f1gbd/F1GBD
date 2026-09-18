<div align="center">

<img src="images/TCQws_logo.png" alt="TCQws" width="300">

# TCQws

### Weak Signal Emergency Messaging — le FT4 / FT8 des opérateurs ADRASEC

*Une application Windows autonome, sans WSJT-X : QSO FT4/FT8 et log ADIF · radiogrammes ADRASEC avec accusé de réception · alerte FLASH sonore et lumineuse · code civil CHAPPE-26 décodé en clair · trafic satellite et activations · décodeur FT4 cohérent avec empilement des répétitions.*

[![Plateforme](https://img.shields.io/badge/plateforme-Windows%2010%2F11-lightgrey.svg)]()
[![Architecture](https://img.shields.io/badge/arch-x86__64-orange.svg)]()
[![Modes](https://img.shields.io/badge/modes-FT4%20%7C%20FT8-blueviolet.svg)]()
[![Compatibilité](https://img.shields.io/badge/compatible-WSJT--X%20(ADIF%2C%20ALL.TXT)-teal.svg)]()
[![Licence](https://img.shields.io/badge/usage-ADRASEC%2FFNRASEC-green.svg)](https://github.com/f1gbd/F1GBD/blob/master/LICENSE.txt)
[![Code civil](https://img.shields.io/badge/code%20civil-CHAPPE--26-b01818.svg)](doc/Chappe26_Livret_B5.pdf)
[![Version TCQws](https://img.shields.io/badge/version-tcqws--v0.2.7-blue)](HISTORIQUE.md)

## 📥 Télécharger TCQws v0.2.7 pour Windows

### **[⬇ TCQws-0.2.7-setup.exe](https://github.com/f1gbd/F1GBD/releases/download/tcqws-v0.2.7/TCQws-0.2.7-setup.exe)** — double-clic, et c'est installé

*Aucun droit administrateur, aucune installation Python, aucune interférence avec TCQ. Raccourcis Bureau et menu Démarrer, manuel inclus, et une désinstallation qui conserve vos réglages, votre log ADIF, votre journal et vos radiogrammes.*

**[⬇ TCQws.7z](https://github.com/f1gbd/F1GBD/releases/download/tcqws-v0.2.7/TCQws.7z)** — l'archive, pour installer à la main ou mettre à jour par-dessus l'existant.

[📜 Historique des versions](HISTORIQUE.md) · [📖 Manuel PDF](doc/MANUEL_TCQws.pdf) · [🚨 Alerte FLASH](#2-lalerte-flash--32-caractères-tout-de-suite) · [🗼 CHAPPE-26](#3-chappe-26--une-phrase-en-quatre-chiffres) · [🛰 Satellite](#4-satellite-et-activations) · [📨 Radiogrammes](#1-les-radiogrammes-adrasec--le-message-pas-seulement-le-qso)

</div>

---

## En une phrase

TCQws est une application de trafic **FT4 et FT8 autonome** : elle ne pilote pas WSJT-X, elle ne l'imite pas non plus. Elle ajoute au protocole FT4/FT8 ce dont une équipe de sécurité civile a besoin sur le terrain : **transmettre un message formaté, déclencher une alerte, et décoder des signaux plus faibles que d'habitude** — tout en restant parfaitement compatible avec les stations WSJT-X.

Pour un QSO ordinaire, WSJT-X reste la référence. TCQws existe pour tout ce qu'il y a **autour** du QSO.

![Trafic FT8 avec TCQws](images/TCQws_main2.png)

---

## La valeur ajoutée, en bref

| | WSJT-X | **TCQws** |
|---|---|---|
| QSO FT4 / FT8, log ADIF | ✔ | ✔ (log `wsjtx_log.adi` au même format) |
| Modes proposés | ~15 (FT8, FT4, JT65, Q65, WSPR, MSK144…) | FT4 et FT8 seulement |
| **Messages libres longs** | 13 caractères par émission | **jusqu'à ~1 500 caractères**, comprimés et protégés (radiogramme ADRASEC) |
| **Accusé de réception** | non | **oui** : trames manquantes redemandées, complétées, puis acquit |
| **Alerte d'urgence** | non | **alerte FLASH** : 32 caractères, écran rouge + alarme sonore chez tous les destinataires |
| **Code civil CHAPPE-26** | non | **1000 codes** : une phrase en 4 chiffres, décodée en clair à l'arrivée |
| **Décodage FT4** | décodeur WSJT-X | **décodeur cohérent** : ≈ 0,4 dB de mieux, et **empilement** des répétitions jusqu'à ≈ −24 dB |
| Tolérance d'horloge en FT4 | environ ±1 s | **−2 à +2 s** (deux PC désynchronisés continuent de se lire) |
| Vérification de l'heure | externe | **NTP intégré** + calage **GPS NMEA** (utile sans Internet) |
| PTT et CAT | un port, un réglage | **deux ports COM distincts** (PTT par RTS/DTR, CAT fréquence à part, 1200 bauds et 2 bits de stop possibles) |
| Diagnostic audio | limité | **WAV de chaque émission et de chaque réception**, compteurs de périodes perdues, alerte de DT anormal |
| Répondeur automatique | Auto-Seq + Call 1st | **AUTO QSO** : répond seul aux CQ, enchaîne, logue, et reprend l'écoute |
| Pays et distance à l'écran | via JTAlert (externe) | **intégré** : pays et km depuis votre locator |
| Filtre d'indicatifs | non | **exclusion par préfixe(s)**, séparés par des virgules (affichage et réponse auto) |
| **Trafic satellite** | fréquence unique | **deux fréquences** (montée / descente), log ADIF `prop_mode` / `sat_name` / `sat_mode` |
| **Activations** (LLOTA…) | non | champ dédié → `MY_SIG` / `MY_SIG_INFO` dans le log |
| Thème d'écran | clair | **clair ou sombre**, au choix — plein jour sous la tente ou vidéoprojection |
| Mise à jour | manuelle | **vérifiée depuis l'application** (bouton dans « À propos ») |

> TCQws est une réalisation indépendante : **aucun code de WSJT-X n'y est repris**. Seuls les protocoles FT4 et FT8 (K1JT, K9AN, G4WJS) sont implémentés, à partir de la bibliothèque libre `ft8_lib` (Kārlis Goba, YL3JG, licence MIT) complétée d'un décodeur cohérent écrit pour TCQ.

---

## 1. Les radiogrammes ADRASEC — le message, pas seulement le QSO

En exercice ou en opération, un réseau d'urgence ne transmet pas des rapports de signal : il transmet des **messages formatés**. TCQws transporte le radiogramme ADRASEC (le même que le module Packet de TCQ, avec son code d'authentification AUTH TOTP/CRC) **directement en FT4/FT8**, sans interface ni logiciel tiers.

![Onglet Radiogramme](images/TCQws_radiogramme.png)

- **Compression** par codeur arithmétique à contexte (≈ 3,5 bits par caractère en français), bien plus efficace que ZIP sur des messages courts.
- **Code d'effacement MDS** : n'importe quelles *k* trames parmi les *k + m* envoyées suffisent à reconstituer le message. Une trame perdue ne demande pas de tout retransmettre.
- **Mode dirigé** : le destinataire acquitte, ou indique combien de trames lui manquent ; l'expéditeur envoie alors des trames **nouvelles**, jamais des répétitions.
- **Mode diffusion** (destinataire CQ), avec option rafale (une trame par période, durée divisée par deux).
- **AUTH vérifié à l'arrivée** (CRC et TOTP ±30 min), message enregistré en `.txt` relisible par **RADIOGRAMME_VALIDATOR** de TCQ.
- Les trames sont des messages FT4/FT8 **standards** de type télémétrie : WSJT-X les affiche en hexadécimal, sans être perturbé.

**Durées indicatives en FT4** : ≈ 4,5 min pour 60 caractères en envoi dirigé, ≈ 9 min pour 600 caractères en diffusion rafale. En FT8, le double, avec une sensibilité un peu meilleure.

---

## 2. L'alerte FLASH — 32 caractères, tout de suite

![Alerte FLASH](images/TCQws_FLASH.png)

Un radiogramme complet prend plusieurs minutes. Pour l'urgence immédiate, TCQws ajoute un format dédié :

- **32 caractères au plus**, diffusés à toutes les stations, **sur chaque période** : environ 75 s en FT4.
- 4 à 10 trames dont **n'importe lesquelles 1 à 6 suffisent** (même code correcteur que les radiogrammes), suivies de l'identification en clair.
- À la réception, sur chaque poste TCQws à l'écoute : **fenêtre rouge clignotante au premier plan**, message en très gros caractères, expéditeur, heure et fréquence, et **alarme sonore jusqu'à l'acquittement**.
- L'alerte est journalisée et enregistrée dans `radiogrammes\FLASH_*.txt`. Une alerte répétée n'est signalée qu'une fois par demi-heure.

C'est la fonction qui n'a aucun équivalent dans WSJT-X : elle transforme une station d'écoute en **poste d'alerte**, y compris sans opérateur devant l'écran.

---

## 3. CHAPPE-26 — une phrase en quatre chiffres

[![Livret CHAPPE-26](https://img.shields.io/badge/livret-1000%20codes-1f4e79.svg)](doc/Chappe26_Livret_B5.pdf)
[![Fiche BLACK-OUT](https://img.shields.io/badge/fiche-BLACK--OUT-b01818.svg)](doc/TCQws-Chappe26_Fiche_BlackOut.pdf)

Trente-deux caractères, c'est peu pour dire une situation. Le **livre de code civil CHAPPE-26** de l'ADRASEC résout le problème à la façon du télégraphe Chappe : **un nombre de quatre chiffres vaut une phrase entière**, lue dans un livret de poche que l'opérateur a sur lui.

    1204 = Santé · Urgence · Ambulance requise
    1376 = Sécurité civile · Coupure électricité
    1990 = Fin de transmission

Une alerte FLASH qui commence par **`!`** est reconnue comme du CHAPPE-26. Un seul `!` pour tout le message, et non un devant chaque code : chaque caractère gagné est un code de plus, et les 32 caractères portent ainsi **sept codes**, soit sept phrases.

**À l'émission**, TCQws traduit les codes au fur et à mesure de la frappe et signale avant l'envoi un groupe incomplet, un code absent du livret ou l'oubli du `1990` final — une alerte part pour plus d'une minute, mieux vaut corriger avant.

**À la réception**, l'alarme se déclenche comme pour toute alerte FLASH, et le message s'affiche **en clair, en très gros caractères** ; les codes reçus restent rappelés en dessous, pour contrôle sur le livret papier. Le fichier `radiogrammes\FLASH_*.txt` conserve les deux.

![Alerte FLASH CHAPPE-26 décodée en clair](images/TCQws_CHAPPE26.png)

Exemple complet — demande de moyens radio pendant un black-out, 29 caractères sur 32 :

```
!1000102413761380134913331990
```

> Début de transmission · Transmission urgente · Coupure électricité · Communication interrompue · Équipement requis · Besoin renfort · Fin transmission

Le tout se relit à la main avec le seul livret, sans TCQws et sans électricité : retirer le `!`, découper en groupes de quatre, chercher chaque code. Le chiffrement Page/Ligne du livret (clé du jour) se fait avant la frappe et se défait après la réception — **TCQws ne détient aucune clé** et transporte le message tel qu'il est saisi.

📄 **[Fiche d'exemple BLACK-OUT](doc/TCQws-Chappe26_Fiche_BlackOut.pdf)** · 📘 **[Livret des 1000 codes](doc/Chappe26_Livret_B5.pdf)**

---

## 4. Satellite et activations

**La bande SAT sait que monter et descendre ne sont pas la même fréquence.** Le cadre *Fréquences spéciales* de la configuration porte les deux : **SAT Rx**, la descente — c'est elle que la radio affiche et que vous écoutez — et **SAT Tx**, la montée. Sur QO-100 : 10 489,540 et 2 400,040 MHz.

Le QSO est alors logué **sur la montée**, offset audio compris, parce que c'est la convention ADIF d'un contact satellite : la bande d'un QSO QO-100 est le 13 cm, pas le 3 cm de la descente.

```
<band:4>13cm <freq:11>2400.040935 <prop_mode:3>SAT <sat_name:6>QO-100 <sat_mode:2>SX
```

TCQws ne pilote qu'un VFO, celui de la réception : la conversion vers la fréquence rayonnée reste l'affaire de votre transverter ou de votre SDR. Le nom et le mode du satellite se règlent, donc rien n'est figé sur QO-100.

**Les activations vont dans le log, pas sur l'air.** Le champ **LLOTA**, à droite de la fréquence, reçoit une référence comme `LLFR-0087` ; chaque QSO logué porte alors :

```
<operator:5>F1GBD <my_sig:5>LLOTA <my_sig_info:9>LLFR-0087
```

Le protocole FT4/FT8 limite le modificateur d'appel à quatre lettres — « LLOTA » n'y tient pas — d'où un champ séparé de celui des CQ POTA/SOTA/WWFF. Champ vide, aucun de ces champs n'est écrit.

Un champ **Commentaire** complète l'ensemble : vide, TCQws écrit son commentaire habituel ; rempli, votre texte part tel quel dans `<comment>`.

---

## 5. Décoder plus bas que le seuil habituel

TCQws embarque **deux décodeurs** : celui de `ft8_lib` (FT8) et un **décodeur cohérent FT4** écrit pour TCQ, avec OSD.

Mesures sur bruit blanc, fichiers identiques donnés à TCQws et à `jt9 -d 3` de WSJT-X 2.7.0, 100 essais par point :

| S/B (FT4) | ft8_lib seul | **TCQws (cohérent)** | WSJT-X |
|---|---|---|---|
| −18 dB | 0 % | **32 %** | 23 % |
| −17 dB | 0 % | **87 %** | 72 % |
| −16 dB | 4 % | **96 %** | 91 % |
| **Seuil à 50 %** | ≈ −14,3 dB | **≈ −17,7 dB** | ≈ −17,3 dB |

Et surtout, l'**empilement** (« stacking ») : en réseau d'urgence, une station en difficulté répète son message. TCQws additionne **de façon cohérente** les périodes successives reçues sur la même fréquence :

| Périodes empilées | 1 | 2 | 4 | 8 | 16 |
|---|---|---|---|---|---|
| Seuil à 50 % | ≈ −17,8 dB | ≈ −18,5 dB | ≈ −20,6 dB | ≈ −22,2 dB | **≈ −24,2 dB** |

Avec 16 répétitions (2 à 4 minutes), un message passe **sous le seuil du FT8**, dans la zone de Q65-30 — sans changer de mode ni de matériel. Aucune fausse détection n'est apparue sur 4 000 essais d'empilement de bruit pur, ni sur 600 périodes de bruit en décodage normal.

**En FT8**, le décodeur reste celui de `ft8_lib` : seuil à 50 % d'environ −18,7 dB, contre −20,6 dB pour WSJT-X. C'est le point où WSJT-X garde l'avantage.

---

## 6. Tenir sur le terrain

![Configuration](images/TCQws_setup.png)

- **Heure** : vérification **NTP** au démarrage et sur demande, correction proposée en un clic, et **calage GPS NMEA** pour le mode blackout (sans Internet). Le journal signale toute station reçue avec un DT anormal, et dit s'il faut corriger une horloge ou une latence.
- **Tolérance d'horloge** : en FT4, TCQws décode de **−2 à +2 s** de DT, là où WSJT-X s'arrête vers ±1 s. Deux postes mal synchronisés continuent de se lire — le temps de corriger.
- **PTT et CAT séparés** : PTT par RTS, DTR, CAT, rigctld ou VOX sur un port, **fréquence par CAT sur un autre port** (vitesse et bits de stop propres). Les transceivers anciens, comme l'IC-737 (CI-V sans commande d'émission, 1200 bauds, 2 bits de stop), fonctionnent tels quels.
- **Boutons de bande** SAT, 80 → 10 m : la radio se règle par CAT, la fréquence suit le mode FT4/FT8, chaque bouton se modifie au clic droit.
- **Audio maîtrisé** : sortie 48 kHz 16 bits stéréo comme WSJT-X, latences réglables, et **enregistrement WAV de chaque émission et de chaque réception** pour diagnostiquer une chaîne audio douteuse au lieu de la deviner.
- **Thème clair ou sombre**, d'un bouton : le thème clair pour un écran en plein jour, sous une tente ou en vidéoprojection, le sombre pour la veille de nuit. La chute d'eau reste sur fond noir dans les deux cas.
- **Mise à jour vérifiée depuis l'application** : le bouton « ⭯ Vérifier la mise à jour » de la fenêtre « À propos » compare la version installée à la dernière publiée et propose le téléchargement. Sans Internet, il le dit et n'insiste pas.
- **Un seul exécutable**, sans installation ni service, et un mode **`--demo`** avec bande simulée pour se former sans radio.

---

## 7. Le trafic de tous les jours

![QSO et log](images/TCQws_main.png)

- **AUTO QSO** : TCQws répond seul aux CQ reçus (la station la plus forte, pas encore contactée sur la bande et le mode), mène le QSO, l'enregistre, puis se remet à l'écoute. Les CQ dirigés vers une zone sont ignorés, les CQ d'activité (POTA, SOTA, WWFF…) non.
- **Log ADIF** `wsjtx_log.adi` au format de WSJT-X : importable dans Log4OM, JTAlert, TQSL/LoTW, Club Log, QRZ… ou ajouté directement au log existant de WSJT-X.
- **Indicatifs spéciaux et portables** (`TM50SC`, `F1GBD/P`) gérés comme dans WSJT-X, y compris le cas où WSJT-X ne peut pas transmettre de rapport.
- **CQ POTA / SOTA / IOTA / WWFF…** par un champ dédié.
- **Pays et distance** affichés directement dans l'activité de bande (calculés depuis votre locator), et **filtre d'exclusion par préfixe** pour écarter d'un coup une zone qui sature la bande — à l'affichage comme en réponse automatique.
- **Journal `ALL.TXT`** au format WSJT-X, et double-clic qui passe en émission comme dans WSJT-X.

---

## Ce que WSJT-X fait mieux

Par honnêteté, et parce que les deux logiciels sont complémentaires :

- **Beaucoup plus de modes** : JT65, Q65, WSPR, MSK144, FST4, EME… TCQws ne fait que FT4 et FT8.
- **Décodage FT8 plus sensible** (≈ 2 dB), grâce à des techniques de décodage multi-passes et *a priori* que TCQws n'implémente pas.
- **Écosystème** : PSK Reporter, JTAlert, cartes, concours, traductions, multi-plateforme, et une communauté considérable.
- **Maturité** : des années d'essais sur l'air, sur toutes les bandes et tous les continents.

TCQws n'a pas vocation à remplacer WSJT-X sur une station de trafic. Il est fait pour le poste ADRASEC, en exercice ou en opération — et rien n'empêche d'avoir les deux sur le même PC.

---

## Installation et premiers pas

### Programme d'installation (le plus simple)

Télécharger **`TCQws-x.y.z-setup.exe`** dans la dernière [release `tcqws-v…`](https://github.com/f1gbd/F1GBD/releases?q=tcqws) et le lancer. Aucun droit administrateur n'est demandé : l'installation se fait dans votre profil, avec les raccourcis (dont un raccourci **démonstration**) et le manuel. La désinstallation retire le programme et **conserve** vos réglages, votre log ADIF, votre journal et vos radiogrammes.

### Installation automatique par script

Pour déployer ou mettre à jour plusieurs postes sans cliquer, une commande PowerShell **en administrateur** :

```powershell
iwr https://github.com/f1gbd/F1GBD/raw/master/tcqws/Install-TCQws.ps1 -OutFile $env:TEMP\Install-TCQws.ps1
& $env:TEMP\Install-TCQws.ps1
```

Le script prend la dernière release **TCQws** (tag `tcqws-v…`), vérifie le SHA-256, installe dans `C:\TCQws` et crée un raccourci. Lors d'une mise à jour, il **conserve** les réglages (`ft4_config.json`), le log ADIF, le journal `ft4_ALL.TXT` et le dossier `radiogrammes\`. Une installation de **TCQ** existante n'est pas touchée : les deux applications cohabitent.

### Installation manuelle

1. Télécharger `TCQws.7z` dans la dernière [release `tcqws-v…`](https://github.com/f1gbd/F1GBD/releases?q=tcqws), décompresser dans un dossier où l'on peut écrire (par exemple `C:\TCQws`).
2. Lancer **`TCQws.exe`**.
3. Essayer d'abord **sans radio** : `TCQws.exe --demo` (bande simulée, stations automatiques, radiogramme et alerte FLASH d'exercice).
4. Régler l'audio, le PTT, le CAT et l'heure dans l'onglet ⚙ Configuration, puis **💾 Enregistrer** et **✔ Appliquer**.

**Options :** `--demo`, `--sans-accueil`, `--config fichier.json`.

**Fichiers créés à côté de l'exécutable :** `ft4_config.json` (réglages), `ft4_ALL.TXT` (journal), `wsjtx_log.adi` (log ADIF), `radiogrammes\` (messages reçus), `diag_tx\` (WAV de diagnostic).

### Documentation

| Document | Contenu |
|---|---|
| [📖 Manuel de l'utilisateur](doc/MANUEL_TCQws.pdf) | Le mode d'emploi complet, avec exemples d'alerte FLASH et de radiogramme |
| [📘 Livret CHAPPE-26](doc/Chappe26_Livret_B5.pdf) | Les 1000 codes du livre de code civil, format B5 à imprimer en recto/verso |
| [📄 Fiche BLACK-OUT](doc/TCQws-Chappe26_Fiche_BlackOut.pdf) | Un message CHAPPE-26 de bout en bout, de la frappe à la réception |
| [📊 Fiche topo — performances](doc/FICHE_TOPO_TCQws_performances.pdf) | Seuils de décodage mesurés et positionnement face aux autres modes |
| [📜 Historique des versions](HISTORIQUE.md) | Les nouveautés de chaque version, de la plus récente à la plus ancienne |

Le mode d'emploi est aussi livré avec l'application, dans **`README_TCQws.md`**.

Windows 10/11 64 bits. Ce dépôt publie les **exécutables** ; les sources ne sont pas distribuées.

---

## Licences et crédits

- **TCQws** © 2026 F1GBD — ADRASEC 77 / FNRASEC. Licence : voir `LICENSE`.
- **Protocoles FT4 et FT8** : Joe Taylor K1JT, Steve Franke K9AN, Bill Somerville G4WJS et l'équipe WSJT-X. TCQws est une réalisation indépendante, **non affiliée au projet WSJT-X**, et ne reprend aucun de ses codes.
- **ft8_lib** : Kārlis Goba, YL3JG — licence MIT.
- **Composants tiers** : Python, Tk, NumPy, SciPy, PortAudio / sounddevice, pySerial, Pillow, chacun sous sa propre licence.

*L'utilisation de TCQws se fait dans le respect des conditions de la licence radioamateur de l'opérateur. Les fonctions d'urgence (radiogrammes, alerte FLASH) sont destinées aux exercices et aux opérations de sécurité civile encadrées par la FNRASEC.*

<p align="center"><i>73 de F1GBD — ADRASEC 77</i></p>
