# Historique des versions — TCQws

Les nouveautés de chaque version, de la plus récente à la plus ancienne.
Chaque version est aussi publiée comme [release GitHub](https://github.com/f1gbd/F1GBD/releases?q=tcqws),
avec son programme d'installation, son archive et son empreinte SHA-256.

[← Retour au README](README.md)

---


## v0.4.0 — Écouter avec une clé SDR

*19 septembre 2026*

### 📡 Une clé RTL-SDR comme récepteur

TCQws sait recevoir directement sur une **clé RTL-SDR**, sans transceiver, sans carte son et sans câblage audio. C'est pour les **SWL** — l'écouteur en formation, le poste d'écoute d'un exercice, le PC qui surveille un segment dans un coin de la salle radio — et, pour une station équipée, un deuxième récepteur qui tourne pendant que le transceiver fait autre chose.

Onglet **Configuration**, cadre Audio : **Source de réception** propose *Carte son (transceiver)* ou *Clé SDR RTL-SDR (réception seule — SWL)*. Le second ouvre le cadre **📡 Clé SDR** — bouton **🔄 Chercher** pour lister les clés branchées, mode d'échantillonnage, gain, correction ppm, entrée transverter. Les boutons de bande de l'onglet Trafic réaccordent la clé comme ils commandent un transceiver en CAT.

### 🔒 Réception seule, annoncée

Une clé reçoit et ne transmet pas. TCQws verrouille donc l'émission tant que la source est une clé : **Tx1 à Tx6** et **PING** grisés, **AUTO QSO** et **PONG** décochés, file d'émission affichant *« Écoute seule (clé SDR) : émission désactivée »*. Le décodage reste complet : activité, carte, journal, radiogrammes reçus, alerte FLASH.

### ⚙ Les deux réglages qui décident de tout

- **Échantillonnage direct, branche Q.** Le tuner d'une clé ne descend pas sous 24 MHz : sans lui, rien n'est décodé en onde courte alors que la clé a l'air de fonctionner. C'est le mode par défaut, celui des **RTL-SDR Blog V3**. En VHF/UHF ou par transverter, choisir *Normal*.
- **La clé n'est jamais calée sur le segment écouté.** Son centre porte une raie continue et du bruit en 1/f qui tomberaient en plein milieu du FT8 : TCQws l'accorde **50 kHz au-dessus** et redescend en numérique.

Le reste suit sans qu'on y pense : 240 kHz d'échantillonnage, démodulation BLU supérieure, décimation vers les 12 kHz du décodeur, et continuité d'un bloc au suivant — sans quoi le signal serait haché quatre fois par seconde.

### 🖥 L'onglet Configuration sur un petit écran

Chaque cadre se plie d'un clic sur son titre (▾ / ▸), et **⇕ Replier tout** fait les sept d'un coup : une fois le poste câblé, PTT et CAT ne changent plus de l'année et rendent leur place. L'onglet passe de 765 à 112 pixels de haut tout replié, et l'état est retenu d'un lancement à l'autre — sans jamais partir dans un profil, puisqu'il décrit cet écran-là et pas la station.

La page est aussi passée à **deux colonnes partout** — les *Fréquences spéciales* et le *Log des QSO* occupaient chacune toute la largeur — avec les explications en gris les plus longues raccourcies : **1548 → 1163 pixels de large**, de quoi tenir sur un 1366, et sur un 1024 avec un cadre ou deux repliés. Comme le bouton 🔍, **⇕ Replier tout** est placé pour être le dernier à disparaître si la barre du bas déborde.

### 🔧 Pilote

Le bouton **🔄 Chercher** reste utilisable même quand la carte son est la source : on vérifie que la clé est vue avant de basculer dessus. S'il ne trouve rien, TCQws distingue les trois pannes qui donnent le même écran vide — module Python absent, DLL absentes, et pilote Windows qui n'est pas **WinUSB** (Zadig) — et donne pour chacune la marche à suivre.

Le message nomme **l'interpréteur qui fait tourner TCQws** et donne la commande `<cet interpréteur> -m pip install …` toute prête : sous Windows, `pip` et `python` désignent très souvent deux Python différents, et `pip install` réussit alors ailleurs pendant que TCQws continue de ne rien voir. TCQws dit aussi ce que `pyrtlsdrlib` livre réellement ici — ce paquet est propre à la plateforme, et une roue d'une autre plateforme s'installe sans broncher sans contenir la moindre DLL Windows.

Deux corrections de fond : quand la DLL manque, pyrtlsdr lève un `ImportError`, que TCQws prenait pour un module absent (c'est `find_spec` qui tranche désormais) ; et depuis Python 3.8 le PATH ne suffit plus à faire trouver `libusb-1.0.dll` à `rtlsdr.dll`, d'où le passage par `os.add_dll_directory`. L'exécutable publié embarque le nécessaire ; pour qui compile lui-même, `pyrtlsdr` reste facultatif.

Dans l'exécutable compilé, `pip install` n'a aucun effet : un programme figé porte les modules choisis à la compilation. Le message le dit maintenant — recompiler, ou lancer depuis les sources. Et la compilation elle-même a été corrigée : `rtlsdr` était à la fois embarqué sous condition et **exclu** (un vestige), or PyInstaller fait gagner l'exclusion sans rien signaler ; les bibliothèques de `pyrtlsdrlib`, cherchées par `importlib.resources` **dans le paquet `pyrtlsdrlib.lib`**, n'étaient ni ramassées ni posées au bon endroit — les mettre à la racine du bundle ne sert à rien, et le fichier livré s'appelle `librtlsdr_w64_static.dll`, pas `rtlsdr.dll`. Un garde-fou fait désormais **échouer le build** si un module est à la fois embarqué et exclu, et le build affiche quel Python et quelles versions il utilise.

Plus largement, quand la station ne démarre pas faute d'un module (`sounddevice`, par exemple), TCQws donne le nom du module, le chemin de l'interpréteur et la commande qui vise le bon.

### 🔊 Audio : deux pièges de terrain

Le bouton **⏱ Corriger** pouvait descendre la latence d'entrée jusqu'à −1 seconde. Une latence négative n'existe pas : PortAudio refuse alors d'ouvrir le flux et la station ne démarre plus. Désormais, si la correction devait passer sous zéro, c'est la preuve que l'écart vient de l'**horloge** et non de la carte son — TCQws le dit et corrige l'horloge. Les valeurs négatives héritées sont ignorées.

L'API audio passe **en tête** du nom du périphérique (`33: [WDM-KS] Input (…)`) : en suffixe, la liste déroulante la coupait, et on pouvait choisir une entrée Bluetooth sans le voir. Enfin, `Unanticipated host error [PaErrorCode -9999]` ne s'affiche plus seul : TCQws nomme les trois causes habituelles — périphérique inadapté, latences, périphérique déjà pris.

Une clé conçue pour la VHF/UHF (Nooelec NESDR SMArt, clé DVB-T ordinaire) accepte l'échantillonnage direct mais coupe l'onde courte à l'entrée : lui donner un convertisseur (Ham It Up) et choisir le mode **Transverter**.

---


## v0.3.2 — Gros caractères et configurations nommées

*19 septembre 2026*

### 🔍 Taille des caractères

Un bouton **🔍** dans la barre du haut fait le tour de **100 %**, **125 %** et **150 %** : tout le texte suit d'un coup, carte et chute d'eau comprises, et le réglage est retenu. C'est fait pour la tablette sous la tente et la lecture debout.

- Le gros texte est amorti de moitié au-delà de 12 points : l'horloge est déjà lisible, la grossir ferait seulement déborder la barre du haut.
- Le champ Commentaire passe à la ligne en gros caractères, sans quoi la case PONG deviendrait inatteignable.
- Le bouton est à l'extrême droite de la barre, donc le dernier à disparaître si elle déborde, et **Ctrl + +**, **Ctrl + −**, **Ctrl + 0** doublent la commande : on ne reste pas coincé en 150 %.

### 💾 Configurations nommées

Deux boutons en bas de l'onglet **Configuration** : **📤 Sauvegarder…** et **📥 Charger…**. Un profil « exercice départemental », un profil « QO-100 », un profil « portable », et on passe de l'un à l'autre en deux clics. Les profils vivent dans `profils\` à côté de `ft4_config.json` — ou sur une clé USB, pour les donner à une autre station.

**Le matériel ne voyage pas par défaut.** Une configuration mélange ce qui décrit l'opérateur (indicatif, locator, bandes, LLOTA, satellite, filtres, thème) et ce qui décrit la machine (carte son, ports COM du PTT et du CAT, latences, correction d'horloge). Sur un autre poste, « COM3 » ne désigne pas la même interface : reprendre ce réglage à l'aveugle, c'est mettre le PTT sur un autre port, et au pire laisser une radio en émission. Le chargement garde donc les réglages matériels du poste ; si le profil vient d'ailleurs, TCQws le signale et propose de reprendre le matériel aussi, à ne faire que si les deux postes sont câblés à l'identique. Venant du poste lui-même, tout est repris sans question.

- Le chargement annonce combien de réglages changent, et prévient si le profil est identique plutôt que de ne rien faire en silence.
- Un ancien `ft4_config.json` se charge directement ; un JSON quelconque est refusé avec la raison.
- La géométrie de la fenêtre ne part jamais dans un profil et n'est jamais imposée.

---


## v0.3.1 — La carte dit la bande, et sait faire la carte des QSO

*19 septembre 2026*

### 🎨 Reconnaître la bande d'un coup d'œil

Sur une carte, deux marqueurs quelconques peuvent se toucher : au-delà de **trois** teintes, aucune palette ne garantit qu'un œil — surtout daltonien — les distingue à coup sûr. Douze bandes ne tiennent donc pas sur la couleur seule. TCQws en donne trois lectures, qui se complètent :

- la **couleur** du marqueur, pour saisir la répartition d'un regard : les huit bandes les plus courues en FT8/FT4 ont chacune leur teinte (choisie séparément pour le thème sombre et pour le clair) ; 160 m, 60 m, VHF, UHF et satellite partagent un gris ;
- la **bande écrite à côté de l'indicatif** — « F4JHW 20m » — qui lève toute ambiguïté, gris compris ;
- la **liste Bande** de la barre d'outils, qui n'en affiche qu'une à la fois et ne propose que les bandes réellement présentes. La ligne d'état en donne le compte.

Un sélecteur **Couleur : bande / rapport** garde l'ancienne échelle des rapports disponible.

### 📒 Carte des QSO

Le bouton **📒 Carte des QSO** relit le log ADIF et place un marqueur par contact enregistré : la carte de ce que vous avez **travaillé**, et non de ce que vous avez entendu.

- L'import **efface les stations seulement entendues** : la carte ne répond plus qu'à une question.
- L'ancienneté passe d'office sur « tout » — les QSO du journal ont souvent plusieurs jours, la carte s'afficherait vide sans cela.
- Les QSO **sans locator** ne peuvent pas être placés : ils sont comptés et signalés, plutôt que perdus en silence.
- Une station contactée **et** vue au PING garde son triangle.
- Les stations contactées portent un **anneau clair** : quand de nouveaux décodages arrivent après l'import, le contacté se distingue de l'entendu sur la même carte. Un QSO logué en cours de trafic marque la station aussitôt.

---


## v0.3.0 — PING/PONG, carte des stations, éditeur de journal

*19 septembre 2026*

### 📡 PING / PONG — qui est là ?

Un bouton **📡 PING** dans le cadre Émission, une case **PONG** cochée par défaut : on clique, et en deux périodes on sait qui est sur la bande, où, et avec quel rapport, sans engager de QSO.

- PING = `CQ PING F1GBD JN18`, PONG = `CQ PONG F4JHW JN19` : des messages FT4/FT8 **standards** (un CQ avec modificateur, comme `CQ POTA`), donc **décodés normalement par WSJT-X**. Le PONG porte l'indicatif ET le locator.
- Les réponses sont **étalées** : chaque répondant tire sa fréquence audio entre 500 et 2400 Hz à partir de son indicatif, et les réponses se répartissent sur deux périodes. Sans quoi vingt stations répondant ensemble seraient toutes perdues.
- PING et PONG s'affichent en **bleu sur fond orange** dans l'activité de bande et en **triangles** sur la carte.
- Un indicatif non standard (TM50SC) ne peut pas porter de modificateur de CQ : TCQws l'explique au lieu de refuser sans raison.

### 🗺 Onglet Carte

- Carte du monde des stations entendues, **entièrement hors ligne** : les contours sont embarqués (Natural Earth 110 m, domaine public), aucune tuile n'est téléchargée.
- Rond coloré selon le rapport pour les stations reçues, triangle pour les stations TCQws vues au PING, croix pour la vôtre. Info-bulle au survol : pays, locator, distance, azimut, rapport, bande, ancienneté.
- Zoom molette / ＋ − / double-clic, déplacement à la souris, raccourcis 🌍 Monde, 🎯 Ajuster, 🏠 Chez moi. Filtres par ancienneté et « TCQws seulement ».
- **Grille des locators** : champs sur 2 lettres en vue générale, carrés de 4 caractères en zoomant. La projection équirectangulaire est choisie pour cela — les carrés Maidenhead y sont des rectangles réguliers.

### 📒 Onglet Logbook

- `wsjtx_log.adi` en tableau : **corriger** un QSO champ par champ, **supprimer** un doublon, **ajouter** un contact fait ailleurs. Tri par colonne, filtre, QSO satellite en cyan et activations en vert.
- Trois précautions : rien n'est écrit avant le clic sur 💾 Enregistrer ; l'écriture passe par un fichier temporaire et garde la version précédente en `.bak` ; les QSO logués par TCQws **pendant** l'édition sont conservés au lieu d'être écrasés.

### 🌍 Exclure par nom de pays

Le champ **Exclure** prend « Russie, Bielorussie » plutôt que la liste des préfixes. Accents et casse ignorés, déclinaisons incluses (« Russie » couvre la Russie d'Asie ; Kaliningrad se nomme à part). Les préfixes bruts restent acceptés.

---


## v0.2.7 — CAT des Yaesu : lignes DTR et RTS

*18 septembre 2026*

Sur un **FTX-1**, la radio ne changeait pas de fréquence alors que la vitesse (38400 bauds), le modèle et la commande étaient bons. En cause, les lignes de contrôle du port série, que ces postes exigent au niveau haut avant d'accepter le moindre dialogue CAT : le menu *CAT RTS* de la radio arme un contrôle de flux matériel.

- **Deux cases « Lignes du port CAT » — DTR et RTS —** dans le cadre *CAT* de la Configuration. Ces lignes sont tenues au niveau haut pendant tout le dialogue CAT.
  - **Yaesu FTX-1, FT-991 et apparentés** : cocher **DTR**, et **RTS** en plus si le menu *CAT RTS* de la radio est sur **ON**.
  - **Icom, Kenwood, Elecraft sur port USB natif** : laisser les deux décochées, comme avant.
  - **Interface CAT ancienne alimentée par le port série** (CT-17, montage maison) : cocher les deux.
- **La ligne qui porte le PTT n'est jamais montée**, quel que soit le réglage : elle mettrait la radio en émission permanente dès l'ouverture du port.
- Jusqu'ici, la case « RTS/DTR actifs en CAT » n'agissait **que si le PTT était lui-même en mode CAT** : elle était sans effet sur le réglage de fréquence, ce qui explique que le problème résistait à tous les réglages.
- Le **manuel** décrit les deux cases au § 3.3, avec un exemple de réglage complet pour un FTX-1 à 38400 bauds.

---


## v0.2.6 — Trafic satellite, activation LLOTA, commentaire du log

*18 septembre 2026*

### Trafic satellite (QO-100 et autres)

- **Cadre « 🛰 Fréquences spéciales »** dans la Configuration, au-dessus du Log des QSO : **SAT Rx** (la descente, celle que la radio affiche et que l'on écoute) et **SAT Tx** (la montée), plus le nom et le mode du satellite.
- Sur la **bande SAT**, TCQws règle la radio sur la descente et **logue la montée** : c'est la convention ADIF pour un QSO satellite. Sur QO-100 avec SAT Tx = 2400,040 MHz et un TX audio à 935 Hz, le log porte `<band:4>13cm <freq:11>2400.040935`.
- Le QSO est marqué **`<prop_mode:3>SAT <sat_name:6>QO-100 <sat_mode:2>SX`**, le nom et le mode venant du cadre de configuration.
- Le bouton **SAT** affiche les deux fréquences (`RX ↓ • TX ↑`) ; un clic droit ouvre directement le cadre de configuration.

### Activation LLOTA

- **Champ « LLOTA »** de 10 caractères sur la première ligne du cadre Émission, à droite de la fréquence. Rempli d'une référence comme `LLFR-0087`, il ajoute au log **`<operator:5>F1GBD <my_sig:5>LLOTA <my_sig_info:9>LLFR-0087`** — `operator` étant repris du champ **Opérateur** de la configuration.
- Vide, aucun de ces champs n'apparaît : les QSO ordinaires ne changent pas.

### Commentaire du log

- **Champ « Commentaire »** à droite d'AUTO QSO, dans le cadre Émission. Vide, TCQws garde son commentaire habituel (`FT8  Sent: … Rcvd: …`) ; rempli, c'est son contenu qui part dans `<comment>` — par exemple `Thanks for this digital QSO via QO-100`.

### Log ADIF

- L'ordre des champs suit la ligne de référence : `operator` passe juste après `station_callsign`, suivi de `my_sig` / `my_sig_info`, et les champs satellite ferment l'enregistrement.
- La fenêtre « Loguer le QSO » montre et laisse corriger les nouveaux champs (activation, référence, propagation, satellite, mode satellite).
- Bandes **13 cm** et **3 cm** reconnues (elles l'étaient déjà) : `2400.040935` → `13cm`, `10489.540` → `3cm`.


## v0.2.5 — Code civil CHAPPE-26, thème clair, installeur Windows

*18 septembre 2026*

### Urgence ADRASEC — le code civil CHAPPE-26

- **Les alertes FLASH parlent CHAPPE-26.** Un message qui commence par **`!`** suivi de codes de 4 chiffres est reconnu comme du [livre de code civil CHAPPE-26](https://github.com/f1gbd/F1GBD/blob/master/tcqws/doc/Chappe26_Livret_B5.pdf) : à la réception, l'alarme se déclenche comme d'habitude, mais le message s'affiche **en clair, une ligne par code, en très gros caractères**. Les codes reçus restent rappelés en dessous, pour contrôle sur le livret papier.
- **Un seul `!` pour tout le message**, et non un devant chaque code comme sur MeshPager : à 32 caractères, chaque caractère gagné est un code de plus. Une alerte porte ainsi **sept codes**, soit sept phrases.

  ```
  !1000102413761380134913331990
  ```
  > Début de transmission · Transmission urgente · Coupure électricité · Communication interrompue · Équipement requis · Besoin renfort · Fin transmission

- **Relecture avant diffusion** : pendant la frappe, TCQws traduit les codes sous le champ de saisie et signale un groupe incomplet, un code absent du livret ou l'oubli du `1990` final. Une alerte part pour plus d'une minute, autant corriger avant.
- Le fichier `radiogrammes\FLASH_*.txt` conserve les codes **et** leur traduction : il se relit avec ou sans le livret.
- Le chiffrement Page/Ligne du livret (clé du jour) se fait à la main, avant la frappe : TCQws transporte le message tel qu'il est saisi et ne détient aucune clé.
- Voir la [fiche d'exemple BLACK-OUT](https://github.com/f1gbd/F1GBD/blob/master/tcqws/doc/TCQws-Chappe26_Fiche_BlackOut.pdf), un message de bout en bout.

### Confort d'utilisation

- **Thème clair / sombre** : un bouton en haut à droite (`☀ Clair` / `🌙 Sombre`) bascule toute l'interface. Le thème clair est fait pour les écrans en plein jour, sous une tente ou en vidéoprojection ; le thème choisi est mémorisé. La chute d'eau reste sur fond sombre dans les deux cas, pour garder la lisibilité des traces.
- **Filtre d'exclusion multi-préfixes** : le champ « Exclure » accepte maintenant plusieurs préfixes séparés par une virgule — par exemple `R, UA, K`. Les stations correspondantes ne sont ni affichées dans l'activité de bande, ni appelées par l'AUTO QSO.

### Mises à jour

- **Bouton « ⭯ Vérifier la mise à jour »** dans la fenêtre « À propos » : TCQws interroge GitHub, compare avec la version installée et propose d'ouvrir le téléchargement si une version plus récente est publiée. La vérification se fait en arrière-plan et ne bloque jamais le trafic en cours.

### Installation

- **Programme d'installation Windows** (`TCQws-0.2.5-setup.exe`) : installation par utilisateur, sans droits administrateur, avec licence, raccourcis (dont un raccourci « démonstration »), lien vers le manuel PDF et désinstallation qui **conserve vos réglages, votre log ADIF, votre journal et vos radiogrammes**.

### Corrections

- La vérification de mise à jour n'accède plus à l'interface depuis un fil secondaire (fermeture de la fenêtre pendant la vérification).
- Le changement de thème respecte le rôle de chaque couleur : les champs de saisie gardent un fond clair et une encre sombre dans les deux thèmes.


## v0.2.4 — Alerte FLASH, AUTO QSO, PTT et CAT séparés

*17 septembre 2026*

### Urgence ADRASEC

- **Alerte FLASH** : message de 32 caractères diffusé à toutes les stations (≈ 75 s en FT4). À la réception : fenêtre rouge clignotante au premier plan, message en très gros caractères et alarme sonore jusqu'à l'acquittement. L'alerte est journalisée et enregistrée dans `radiogrammes\FLASH_*.txt`.
- **Radiogrammes** : réception en arrière-plan quel que soit l'onglet affiché, bascule automatique vers l'onglet Radiogramme.

### Décodage et horloge

- **Fenêtre de DT du FT4 portée à −2 .. +2 s** : deux postes dont les horloges diffèrent de plus d'une seconde continuent de se décoder (WSJT-X s'arrête vers ±1 s).
- **Vérification de l'heure par NTP** au démarrage et sur demande, avec correction proposée en un clic ; calage GPS NMEA toujours disponible pour le mode blackout.
- Le journal signale toute station reçue avec un DT anormal et indique quoi corriger.

### Trafic

- **AUTO QSO** répond maintenant automatiquement aux CQ reçus (station la plus forte, pas encore contactée sur la bande et le mode), mène le QSO, l'enregistre, puis se remet à l'écoute.
- **Double-clic** sur un décodage : passage en émission immédiat, comme dans WSJT-X.
- **Boutons de bande** SAT, 80 → 10 m : la radio se règle par CAT, la fréquence suit le mode, clic droit pour modifier un bouton.
- **Champ CQ** (POTA, SOTA, IOTA, WWFF…) pour les appels d'activité.
- **Pays et distance** affichés dans l'activité de bande, et **filtre d'exclusion par préfixe** d'indicatif (affichage et réponse automatique).
- Boutons 🗑 Effacer sur les listes de décodages ; les listes occupent désormais plus de place que la chute d'eau, la séparation se déplace à la souris.

### Radio et diagnostic

- **PTT et CAT sur deux ports COM distincts** : PTT par RTS/DTR/CAT/rigctld/VOX d'un côté, fréquence par CAT de l'autre (vitesse et bits de stop propres). Les transceivers anciens comme l'IC-737 (CI-V 1200 bauds, 2 bits de stop, sans commande d'émission) fonctionnent tels quels.
- **Enregistrement WAV des réceptions** en plus des émissions, compteur de périodes non décodées dans la barre d'état.
- Page de configuration **adaptée aux petits écrans** (défilement, boutons Enregistrer et Appliquer toujours visibles).


---

## Avant la v0.2.4

Étapes de développement, sans release publiée : modem FT4/FT8 et décodeur cohérent
(v0.1.x), planificateur temps réel et interface (v0.2.0 à v0.2.2), radiogrammes
ADRASEC et log ADIF (v0.2.3).

---

*Jean-Louis (F1GBD / F4JHW) — ADRASEC 77 — FNRASEC*
