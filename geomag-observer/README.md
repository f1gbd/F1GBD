<div align="center">

<img src="images/geomag_observer_logo.png" alt="GEOMAG-Observer" width="300">

# GEOMAG-Observer

**Observatoire magnétique amateur et détecteur de perturbation géomagnétique locale**

Version 1.1.0 — F1GBD / F4JHW — ADRASEC 77

### [**Télécharger la dernière version**](https://github.com/f1gbd/F1GBD/releases/download/geomag-observer-v1.1.0/GEOMAG-Observer.7z)

`GEOMAG-Observer.7z` — v1.1.0 — 38 Mo — Windows 10/11 64 bits
[Notes de version](https://github.com/f1gbd/F1GBD/releases/tag/geomag-observer-v1.1.0)

</div>

---

## Ce que c'est

Un poste de surveillance géomagnétique complet bâti autour d'un **PNI RM3100** à 31 €. Il mesure les variations du champ magnétique terrestre, en tire un **indice K local**, détecte les orages géomagnétiques, et vous dit ce que ça change pour la propagation HF.

En scénario de crise avec coupure Internet, vous n'avez plus accès au Kp planétaire du NOAA. Votre station devient alors **votre seule source de conditions géomagnétiques** — et donc le seul moyen de savoir que vos liaisons HF sont en train de tomber avant qu'elles ne tombent.

![Tableau de bord temps réel](images/geomag-observer_main.png)

## Ce que ça mesure — et ce que ça ne mesure pas

**Ça mesure des VARIATIONS.** L'indice K ne dépend que des plages de variation sur des blocs de 3 heures, jamais du niveau absolu. Une station amateur sans ligne de base le calcule donc parfaitement, et c'est ce qui rend ce projet réaliste.

**Ça ne mesure pas le champ absolu.** Pas de théodolite DI, pas de ligne de base : aucune contribution INTERMAGNET possible, et une dérive lente sur des mois que rien ne rattrape. Sans la moindre importance pour l'usage visé.

## Trois usages

| Usage | À quoi ça sert |
|---|---|
| **Détection d'orage** | Indice K local, commencements brusques (SSC), surveillance de dB/dt, alarme à seuil |
| **Correction diurne** | Export IAGA-2002 relu directement par un logiciel de levé magnétique — une station à 0 km vaut mieux qu'un observatoire à 60 km |
| **Surveillance de site** | Mesure du bruit magnétique culturel d'un terrain avant d'y installer quoi que ce soit |

## Fonctions

### Tableau de bord temps réel

- **Cadran gradué en indice K**, pas en nanoteslas. L'échelle K est quasi géométrique (5, 10, 20, 40, 70, 120, 200, 330, 500 nT) : une graduation linéaire écraserait toute la partie utile contre le zéro. Chaque niveau reçoit un secteur angulaire égal.
- **Oscillogramme à deux tracés** — perturbation et dB/dt, chacun avec sa ligne de seuil. Deux grandeurs de nature différente ne se superposent pas sur une seule échelle.
- **Alarme visuelle et sonore** à seuils paramétrables, avec délai de confirmation et mémorisation jusqu'à acquittement.

### Analyse

| Onglet | Contenu |
|---|---|
| **Magnétogramme** | H, E, Z et température sur 24 h, avec la courbe Sq ajustée et les SSC marqués |
| **Radar** | Azimut du vecteur de perturbation sur 360°, rose des relèvements, amplitude en couleur |
| **Indice K** | Les huit blocs de 3 h, l'échelle de la station, la lecture opérationnelle HF |
| **Santé** | Spectre, couplage thermique, plancher de bruit, journal de traitement |
| **Rapport** | Synthèse texte exportable |
| **Firmware** | Flash des cartes Heltec, sans PlatformIO |

<div align="center">

| | |
|:---:|:---:|
| ![Magnétogramme](images/geomag-observer_magnetogramme.png) | ![Radar](images/geomag-observer_radar.png) |
| **Magnétogramme** — SSC, phase principale, baies de sous-orage | **Radar** — azimut du vecteur de perturbation |
| ![Indice K](images/geomag-observer_indiceK.png) | ![Santé](images/geomag-observer_sante.png) |
| **Indice K** — huit blocs de 3 h et lecture HF | **Santé** — spectre, thermique, bruit |

</div>

### Confort

- Thèmes **sombre et clair**, bascule instantanée
- Réglages en **JSON**, chargés et enregistrés automatiquement
- **Écran d'accueil** et fenêtre À propos
- **Simulateur géomagnétique complet** : tout fonctionne sans matériel

## Matériel

### Le capteur

**PNI RM3100**, magnéto-inductif trois axes. Gain = `0,3671 × CC + 1,5` LSB/µT.

| Cycle count | Résolution | Cadence max |
|---|---|---|
| 200 (défaut usine) | 13,3 nT/LSB | 150 Hz |
| **800 (recommandé)** | **3,39 nT/LSB** | 37 Hz |

Moyenné à la minute, on atteint **±3 nT** — largement sous le seuil K1 de 5 nT. L'instrument résout donc toute l'échelle K utile.

### Cinq montages

| Montage | Liaison | Pour qui |
|---|---|---|
| **Heltec LoRa 868** *(recommandé)* | LoRa vers une passerelle USB | Poste ADRASEC. Aucun câble à tirer, tête autonome sur batterie et solaire |
| **Heltec WiFi** | UDP sur le réseau local | Terrasse ou jardin, **avec le secteur à portée**. Une carte au lieu de deux, une trame par seconde au lieu d'une par minute |
| **Tête Teensy 4.1** | USB série, Ethernet UDP, carte SD | Station fixe câblée. L'Ethernet franchit 100 m — le SPI, lui, ne passe pas 30 m |
| **Raspberry Pi direct** | SPI ou I2C local | Capteur à moins d'un mètre du calculateur |
| **Simulateur** | aucune | Mise au point, formation, démonstration |

## La chaîne LoRa — le montage de référence

Deux **Heltec WiFi LoRa 32 V4**, la même carte que RWLoRa et RRLoRa : mêmes outils de flash, mêmes réflexes de mise en service, et rien à tirer entre le capteur et la maison.

| | |
|---|---|
| **CAPTEUR** | Heltec V4 + RM3100, dans le tube. Batterie 3000 mAh, panneau 5 W sur l'entrée solaire dédiée du V4. ~12 mA moyens, donc autonome. |
| **STATION** | Heltec V4 ou V3 en passerelle USB sur le PC. Elle reçoit les trames et les rend au format série que le programme parle déjà. |

![Câblage RM3100 vers Heltec V4 (pinout identique pour le V3)](images/cablage_rm3100_heltec.png)

Quatre fils de signal et deux d'alimentation, sur **J3-14 à J3-17** — quatre GPIO contigus sur le connecteur *et* dans l'ordre des broches du module : la nappe part droite, sans un seul croisement. DRDY n'est pas câblé : à 10 Hz, interroger le registre d'état ne fait rien perdre.

> **Le piège du V4.** `GPIO2`, `GPIO7` et `GPIO46` pilotent l'étage RF haute puissance ; `GPIO33` à `GPIO37` sont consommés par la PSRAM octale d'un ESP32-S3R8. Les utiliser donne une carte qui démarre, compile et fonctionne — jusqu'à la première émission. `GPIO7` est J3-18, juste à côté de la nappe.

### Pourquoi la minute, et pourquoi ça ne coûte rien

La sous-bande g1 (868,0–868,6 MHz) est limitée à **1 % de rapport cyclique**. Une trame par seconde demanderait 6 % au SF7 : illégal d'un facteur six. On groupe donc la minute.

Et la physique aide : **l'indice K est une statistique de plage.** En transmettant la moyenne minute exacte plus le min et le max de chaque axe, K est calculé *sans aucune perte* — identique au bit près à une liaison filaire. On ne perd que la finesse de l'oscillogramme (4 s au lieu de 1 s) et une minute de latence.

| Trame | octets | SF7 | SF8 | SF9 |
|---|---|---|---|---|
| COMPACT / ALARME | 42 | 0,15 % | 0,26 % | 0,48 % |
| FULL 15 éch. | 132 | **0,37 %** | 0,65 % | 1,16 % ✗ |

Le nœud interroge la pile radio sur le temps d'antenne réel de ses paramètres et **choisit son type de trame tout seul**. Au SF9 la forme d'onde saute, la statistique minute passe. L'opérateur ne *peut pas* composer une configuration illégale, et une comptabilité d'antenne glissante sur l'heure refuse d'émettre au-delà du budget plutôt que de tricher.

### Le blanking d'émission

Le SX1262 tire ~60 mA pendant ~100 ms à l'émission, soit quelques nT à 10 cm. Mais contrairement à une liaison Ethernet qui émet en permanence, **le microcontrôleur sait quand il émet** : les échantillons de la fenêtre sont jetés, 0,4 % du temps au SF7, et le problème disparaît. C'est l'avantage décisif du LoRa sur l'Ethernet pour une tête magnétique.

L'acier statique — blindage USB-C, ressorts IPEX — n'est pas un problème : un objet magnétique immobile à distance fixe produit un **offset constant**, et l'indice K ne voit pas les offsets. Seule règle : tout rigidement fixé, rien d'amovible.

### L'implantation

![Montage sur tube PVC](images/montage3d_tete_lora.png)

Le capteur va au **fond d'un puits en PVC 40 mm**, à 70 cm, où l'amplitude thermique quotidienne tombe sous 0,1 °C. Le tube de 20 mm est un **fourreau de câble**, pas un mât porteur : le module RM3100 (25 mm) n'y entre pas, et un mât de 20 mm fléchit au soleil de **2218 nT à 1,50 m** — 1′ d'arc, soit 0,3 mm de flexion, vaut déjà 12 nT.

Sur terrasse, quand on ne peut pas creuser : 24 cm hors socle **maximum**, socle lourd posé et jamais fixé au mur, abri blanc ombrant le capteur *et la totalité du mât*. Le détail chiffré est dans `documentations/FICHE_CABLAGE_RM3100_Heltec-V4.docx`.

### [Vue 3D interactive du montage de la tête](https://f1gbd.github.io/F1GBD/geomag-observer/Capteur_3D_GEOMAG.html)

Le circuit RM3100 de 16 × 15 mm, debout dans un manchon PVC de 20, son plan dans le méridien magnétique — avec les trois axes de mesure, le vecteur champ à 64°, le berceau et le cordon Cat6. Pivotable, zoomable, et chiffrée : ce que coûte une erreur de cap, ce que la mise en service corrige, et ce qu'elle ne corrigera jamais.

## La variante WiFi — quand le secteur est à portée

Même carte, même capteur, même câblage. Ce qui change est le transport, et ce que ce transport permet.

**Ce que le WiFi apporte.** Il n'y a plus de rapport cyclique à respecter : la tête émet **une trame par seconde** au lieu d'une par minute. Le dB/dt y gagne — 3,00 nT/min sur une rampe de référence à 3 nT/min, contre 3,43 à la minute — et l'onglet Santé reçoit enfin un flux continu sur lequel calculer un spectre. Et il n'y a plus de passerelle : la tête parle directement au PC, une carte au lieu de deux. Le V3 convient aussi bien que le V4, puisque l'entrée solaire ne sert plus.

**Ce que le WiFi coûte**, et qu'il ne faut pas se cacher :

| | LoRa | WiFi |
|---|---|---|
| Autonomie sur 3000 mAh | 5,6 j (une trame/min) | **1,5 j** |
| Courant moyen | ~18 mA | ~65 mA |
| Cadence | 1 trame/min | 1 trame/s |
| Fenêtrage d'émission | complet, à la microseconde | **partiel** |
| Déport minimum | 30 cm | **41 cm** |
| Cartes nécessaires | 2 (tête + passerelle) | 1 |

Deux points méritent d'être compris plutôt que subis.

*Le fenêtrage n'est plus complet.* La tête LoRa sait à la microseconde près quand elle émet et jette les échantillons concernés. Une station WiFi associée, elle, reçoit les balises de son point d'accès, les ARP et les retransmissions **sur l'horloge du point d'accès** — 1 à 3 % du temps, imprévisible. On fenêtre ce qu'on maîtrise, sa propre émission, et on ne prétend pas fenêtrer le reste.

*Ce n'est pas grave si le déport suffit.* Le WiFi tire ~350 mA en crête contre ~135 mA pour le SX1262 : facteur 2,6 en courant, donc **1,37 en distance**, le champ d'une boucle décroissant en 1/r³. Les 30 cm minimum de la tête LoRa deviennent 41 cm ici ; les 50 cm recommandés conviennent aux deux.

**Une coupure réseau est un trou dans la donnée.** Rien n'est mis en réserve pour être réémis : rejouer des minutes anciennes en vrac désordonnerait la série pour rattraper des points que l'opérateur aurait de toute façon vus manquer. Le journal de la tête compte les trames perdues.

### La règle de choix

Ce sont deux usages, pas deux camps.

- Capteur sur terrasse ou en jardin, **secteur à portée** → WiFi, 1 Hz, déport 50 cm.
- Capteur éloigné, **sur accu ou solaire** → LoRa.

### Configurer la tête WiFi

La tête doit connaître le réseau. Cela s'écrit par le port USB, depuis l'onglet **Firmware**, panneau *Configuration WiFi du capteur* : SSID, mot de passe, hôte, port — puis *Écrire et sauvegarder* et *Redémarrer la tête*.

Le dialogue est **celui de la console RWLoRa**, trait pour trait : trame KISS sur le port série, charge utile MsgPack, namespace 101 « réseau ». Un opérateur qui a configuré une passerelle RWLoRa retrouve les mêmes champs et les mêmes messages.

> **Hôte vide : la tête diffuse sur le sous-réseau.** C'est le réglage à laisser tant que tout va bien — l'adresse du PC change au gré du bail DHCP, la diffusion non. Si rien n'arrive, certains points d'accès filtrent la diffusion entre clients WiFi : saisir alors l'adresse du PC.

> **Le mot de passe ne se relit jamais.** Il part vers la tête, jamais l'inverse. Une console capable de le relire serait un moyen d'extraire la clé WiFi de toute tête à laquelle on a un accès physique — et une tête magnétique passe sa vie dehors, sur un mât. Le champ revient donc vide à chaque lecture, et n'est écrit que si vous en saisissez un.

Côté application, choisir le capteur **Heltec WiFi (UDP)** et le port de l'onglet *Capteur*. La tête émet la même trame de 36 octets que le firmware Teensy : le décodeur, son CRC et son autotest servent tels quels.

## L'orientation de la tête, et la mise en service

Un magnétomètre vectoriel est d'abord un instrument mécanique. Trois questions se posent au montage, et elles n'ont pas le même poids.

**L'aplomb est presque gratuit.** L'onglet **Capteur** porte un bouton *Mesurer 8 s* : le programme lit huit secondes, en tire la rotation capteur → HEZ et la range dans `geomag_observer.json`. Un basculement dans le plan méridien est alors corrigé **exactement**, même de 15°. Un degré au niveau à bulle suffit donc — ce qui compte est qu'il ne *change* plus, une minute d'arc valant 12,3 nT.

**Le cap, lui, se paie.** Aligner un vecteur sur un autre ne fixe que deux des trois degrés de liberté d'une rotation : celle autour du champ reste indéterminée, et c'est presque exactement un azimut. Aucun calcul ne peut le retrouver. La fuite d'une variation de H vers la voie E a une forme close — `sin²(I) × ε`, soit 0,81 ε sous nos latitudes : dix degrés d'erreur mettent 14 % de H dans E après mise en service, 17 % sans. **±5° à la boussole, sur le nord magnétique**, et le repère marqué au feutre sur le manchon.

**L'indice K, lui, ne bouge pas.** Sur un orage synthétique de 3 h, ni 30° de cap ni 15° de basculement ne le changent d'un cran : K est une statistique de plage sur le vecteur horizontal, et une rotation le redistribue entre les voies sans en changer la longueur. Ce sont les relèvements du **Radar** et la **déclinaison** qui paient, pas l'alarme.

La mise en service rend deux contrôles, tous deux indépendants de l'orientation : l'écart entre le `|F|` mesuré et celui de l'IGRF — qui attrape un cycle count faux ou une masse ferromagnétique proche — et la dispersion de E, qui mesure le bruit du câblage.

## L'onglet Firmware

Un opérateur n'a pas à installer PlatformIO pour poser une station. L'onglet **Firmware** écrit les images livrées dans `firmware\` directement sur la carte.

Rôle (**STATION** / **CAPTEUR LoRa** / **CAPTEUR WiFi**) × carte (**V4** / **V3**) → port → *Détecter la carte* → *FLASHER*, avec journal et barre d'avancement.

- Une carte qui n'est **pas un ESP32-S3** est refusée avant écriture.
- Le V3 et le V4 portent **tous deux** un ESP32-S3 : aucune lecture ne les distingue. L'interface le dit franchement — c'est votre déclaration qui fait foi.
- Une seule image de passerelle sert le V3 **et** le V4 : pour ce rôle les deux cartes sont électriquement équivalentes.
- Pas d'image **CAPTEUR LoRa** pour le V3 : cette tête s'appuie sur l'entrée solaire dédiée du V4.
- La **CAPTEUR WiFi**, elle, sert le V3 **et** le V4 avec une seule image : elle tourne sur secteur, l'entrée solaire ne lui sert pas — c'est précisément ce qui rend le V3 utilisable ici.
- Refus argumentés si l'acquisition occupe déjà le port, si l'image est absente, tronquée, ou de nom non conforme.

### Propreté magnétique — à lire avant de câbler

Le calculateur est lui-même une source magnétique. Un Heltec V4 ou un Teensy 4.1 consomme quelques dizaines à une centaine de milliampères ; la boucle de courant correspondante produit environ :

| Distance capteur ↔ calculateur | Champ parasite |
|---|---|
| 10 cm | ~6 nT |
| 20 cm | ~0,8 nT |
| **30 cm** | **~0,2 nT** |
| 50 cm | ~0,05 nT |

Le plancher de bruit visé étant de 1 à 3 nT : **30 cm minimum, 50 cm de préférence**, et sous-cadencer le processeur (80 MHz sur l'ESP32-S3, `CLK=150` sur le Teensy). Sur la variante filaire, le magjack RJ45 contient des transformateurs à noyau ferrite — objet magnétiquement perméable, à placer aussi loin et à fixer rigidement.

## Installation

Télécharger [**GEOMAG-Observer.7z**](https://github.com/f1gbd/F1GBD/releases/download/geomag-observer-v1.1.0/GEOMAG-Observer.7z) (v1.1.0, 38 Mo), décompresser dans un dossier accessible en écriture, lancer `GEOMAG-Observer.exe`.

Aucune installation, aucune dépendance, aucun droit administrateur. Windows 10 ou 11, 64 bits.

Le fichier de réglages `geomag_observer.json` se crée tout seul au premier lancement, à côté de l'exécutable. Le supprimer suffit à revenir aux valeurs d'usine.

> Ne pas placer le dossier dans `C:\Program Files` : le programme écrit ses réglages et ses exports à côté de l'exécutable. Un dossier de documents, un disque de données ou une clé USB conviennent — le programme est entièrement portable, il ne touche ni à la base de registre ni au profil utilisateur.

### Contenu de l'archive

| Élément | Rôle |
|---|---|
| `GEOMAG-Observer.exe` | L'application |
| `_internal\` | Bibliothèques et données embarquées — ne rien y modifier |
| `documentations\` | Fiche technique et manuel |
| `firmware\` | Images à flasher sur les cartes Heltec |
| `teensy\` | Source du firmware de la tête filaire Teensy |
| `LICENSE` | Conditions de diffusion (MIT) |

### Les firmwares

Le sous-dossier [`osjt_maghead_lora/`](osjt_maghead_lora/) contient le projet PlatformIO des trois rôles — un seul arbre de sources, trois environnements :

```powershell
pio run -e heltec_v4_gateway     # passerelle LoRa
pio run -e heltec_v4_node        # tête LoRa
pio run -e heltec_v4_node_wifi   # tête WiFi
```

Les images produites sont livrées dans `firmware\`, prêtes à flasher depuis l'onglet Firmware. `osjt_lora_frame.h` définit la trame radio, `osjt_teensy_frame.h` celle de 36 octets qui arrive au PC — une seule définition chacune, partagée par les trois rôles.


### Le firmware de la tête Teensy

Le sous-dossier [`teensy/`](teensy/) contient `osjt_maghead.ino`, le source complet de la tête magnétique. Il n'est utile que si vous construisez la tête décrite plus bas : l'application fonctionne sans, en simulateur ou avec un capteur câblé directement.

Ouvrir dans l'IDE Arduino équipé de **Teensyduino**, choisir la carte *Teensy 4.1* à 600 MHz, téléverser. La tête répond ensuite aux commandes série listées en tête du fichier (`?`, `STAT`, `CC=`, `TMRC=`, `SAVE`).

> Deux réglages à ne pas oublier au premier démarrage : `CC=800` puis `SAVE` — le cycle count sort d'usine à 200, soit 13,3 nT/LSB, trop grossier pour le bas de l'échelle K. Et `CLK=150` : lire un capteur à 40 Hz ne demande aucune puissance de calcul, et la signature magnétique du Teensy chute avec sa consommation.

## Prise en main

1. Lancer le programme. Backend **Simulateur** par défaut : rien à brancher.
2. **Démarrer l'acquisition**. Le cadran bouge, l'oscillogramme se remplit.
3. Onglet **Alarme** : régler le seuil. 40 nT correspond à K4 pour un K9 de 500 nT.
4. Au bout d'un quart d'heure, les onglets d'analyse se remplissent tout seuls.

Pour passer au matériel : onglet **Firmware**, flasher les deux cartes, puis choisir le backend **Teensy (série)** et saisir le port de la passerelle — elle rend les trames au format que ce backend parle déjà, il n'y a rien d'autre à changer.

## L'échelle K

Les seuils sont des fractions de K9 selon l'échelle de Bartels. Pour K9 = 500 nT, valeur usuelle aux latitudes moyennes :

| K | 1 | 2 | 3 | **4** | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|
| **Plage sur 3 h (nT)** | 5 | 10 | 20 | **40** | 70 | 120 | 200 | 330 | 500 |
| **Activité** | calme | calme | actif | **perturbé** | orage mineur | orage modéré | orage fort | orage sévère | orage sévère |

Lecture opérationnelle HF :

- **K ≤ 2** — propagation nominale
- **K 3-4** — MUF en baisse, absorption accrue, surveiller les liaisons de plus de 1500 km
- **K 5** — MUF effondrée aux hautes latitudes, absorption aurorale, prévoir un repli
- **K 6-7** — liaisons HF longue distance peu fiables, basculer vers un chemin alternatif
- **K ≥ 8** — panne HF généralisée, risque de courants induits sur les longues lignes conductrices

## Trois pièges, et comment ils sont traités

Ces trois défauts ont été trouvés et corrigés pendant le développement. Ils sont documentés parce qu'ils guettent tout projet équivalent.

**1. dB/dt sur des échantillons à 1 seconde.** Dériver d'un échantillon à l'autre et rapporter à la minute multiplie le bruit par 60 : mesuré sur du bruit blanc de 1 nT, on obtient des pointes à **276 nT/min**, et l'alarme part toute seule. GEOMAG-Observer compare deux moyennes de 15 s séparées d'une minute — sur le même bruit, le maximum tombe à **1,2 nT/min**, et une rampe réelle de 12,0 nT/min se lit 12,17.

**2. Le déparasitage qui efface les commencements brusques.** Un SSC est une excursion courte : un filtre anti-impulsion naïf le supprime, c'est-à-dire exactement l'événement que la station existe pour détecter. Le filtre distingue **impulsion** (le niveau revient) et **marche** (le niveau reste déplacé) en comparant les moyennes de part et d'autre.

**3. La régression thermique qui mange la variation diurne.** La courbe Sq et la température sont toutes deux pilotées par le Soleil : une régression directe attribue la Sq entière à la température et efface le signal. L'ajustement ne se fait que sur la bande 10-60 min, et le programme refuse d'estimer quand la corrélation est insuffisante — ce qui est le comportement normal d'un capteur bien enterré.

## Formats de fichiers

| Fichier | Contenu |
|---|---|
| `<code><AAAAMMJJ>min.min` | IAGA-2002, données minute, relisible par tout logiciel d'observatoire |
| `<code><AAAAMMJJ>.csv` | Données minute brutes : `t_unix, H, E, Z, F, T` |
| `geomag_observer.json` | Réglages, fusionnés avec les défauts à la lecture |

## Ligne de commande

`GEOMAG-Observer.exe` accepte les options suivantes :

```
--headless              analyse une journée simulée et écrit les figures
--daemon                acquisition continue sans interface
--teensy PORT           tête Teensy sur port série
--teensy-udp [PORT]     tête Teensy en UDP (défaut 10077)
--spi / --i2c           capteur direct sur Raspberry Pi
--selftest              vérifie le protocole de trame de la tête
--theme dark|light      thème de démarrage
--logo [FICHIER]        extrait le logo embarqué
--quiet-day             journée calme simulée
--dirty-site            site pollué simulé — montre ce que produit une mauvaise implantation
```

## Documentation

- [`documentations/FICHE_TECHNIQUE_GEOMAG-Observer.pdf`](documentations/) — fiche technique
- [`documentations/MANUEL_GEOMAG-Observer.pdf`](documentations/) — manuel professionnel
- [`documentations/FICHE_CABLAGE_RM3100_Heltec-V4.pdf`](documentations/) — câblage, montage mécanique et budget thermique
- [`documentations/FICHE_CABLAGE_RJ45_Cat6.pdf`](documentations/) — la liaison capteur ↔ carte par cordon Cat6 de 50 cm, V4 et V3

Chaque fiche existe en `.docx` et en `.pdf`.

- [**Vue 3D interactive du montage de la tête**](https://f1gbd.github.io/F1GBD/geomag-observer/Capteur_3D_GEOMAG.html) — orientation, berceau, axes de mesure et vecteur champ

## Sources et références

- **HamSCI** — Personal Space Weather Station, projet magnétomètre RM3100
- **NASA STEN** — *Arduino Magnetometer for Space Weather Studies*
- **PNI Sensor Corporation** — manuel RM3100
- **ArduPilot / PX4** — carte des registres RM3100 (REVID 0x22, 75 LSB/µT à CC=200)
- **IAGA** — échelle K de Bartels, méthode FMI
- **ppigrf** — champ de référence IGRF-14

## Licence

**MIT** — voir le fichier [`LICENSE`](LICENSE), qui précise aussi les licences des bibliothèques embarquées dans l'exécutable et les limites d'usage de l'instrument.

---

<div align="center">

**GEOMAG-Observer** — projet OSJT · F1GBD / F4JHW · ADRASEC 77 · 2026

</div>
