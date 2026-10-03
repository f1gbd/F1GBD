# Historique des versions — TCQws

Les nouveautés de chaque version, de la plus récente à la plus ancienne.
Chaque version est aussi publiée comme [release GitHub](https://github.com/f1gbd/F1GBD/releases?q=tcqws),
avec son programme d'installation, son archive et son empreinte SHA-256.

[← Retour au README](README.md)

---


## v0.7.7 — TUNE, et des boutons qui portent leur nom

*3 octobre 2026*

### 📶 Un bouton TUNE dans l'onglet JTTY/RTTY

À droite de **📒 LOG QSO**, en bleu, le même qu'en FT4/FT8 : régler un coupleur ou lire un ROS demande une porteuse stable, pas un message. La station JTTY savait la sortir depuis la v0.6.0 — il n'y avait simplement pas de quoi la lui demander depuis cet onglet.

Elle s'arrête au second clic, au **⛔ Stop TX**, à l'arrêt de la station, dès qu'un message part, et de toute façon au bout de **deux minutes** : une porteuse oubliée chauffe l'étage final et tient la fréquence occupée. En RTTY elle sort sur la **fréquence centrale** du signal, pas sur le bord bas que donne l'onglet — c'est là que l'antenne doit être accordée.

### ✏️ Les boutons du PROTOCOLE QSO se renomment

Le clic droit sur **CQ, RST, 73, RBN, MSG1 à MSG4** ouvre la même fenêtre à deux cases que les touches F1 à F8 : le nom affiché sur le bouton, et le message émis.

C'est sur cette rangée que le besoin était le plus criant. Quatre de ces boutons s'appellent « MSG1 » à « MSG4 », ce qui ne dit rien de ce qu'ils émettent : celui qui porte l'appel ADRASEC peut enfin s'appeler **QAP**. Les quatre autres se renomment aussi — un réseau départemental n'appelle pas « CQ ».

Les noms sont rangés dans une clé à part (`jtty_msg_noms`), si bien que les messages personnalisés ne bougent pas. Une case laissée vide revient au défaut, et une valeur égale au défaut ne s'enregistre pas du tout.

### 🗣 Deux messages du protocole changent de défaut

| | avant | maintenant |
|---|---|---|
| **CQ** | `CQ CQ DE {mycall} {mycall} K` | `CQ DE {mycall} {mycall} {locator} K` |
| **73** | `{remote} DE {mycall} TU FER QSO 73 73 SK` | `{remote} DE {mycall} R TU FER QSO 73 SK` |

L'appel porte désormais le **locator** : depuis la v0.7.6 le correspondant a une case GRID à remplir, et le lui donner d'emblée lui épargne de le demander. La clôture commence par un **`R`** — l'accusé de réception de l'opérateur RTTY, qui dit ce que le second `73` ne disait pas : *j'ai bien reçu*. Le message **RST** ne change pas, et les versions personnalisées sont conservées.

---

## v0.7.6 — Le carré du correspondant, et le log à la main

*3 octobre 2026*

### 🗺 Un champ GRID à côté de DEST

La grammaire WSJT-X met le locator dans l'appel — `CQ EA1MU EA1MU IN70` — et **rien ne l'affichait** : il fallait le relire dans la fenêtre de réception pour orienter une antenne. Il a maintenant sa case. Trois sources, par ordre de confiance décroissante, et la couleur dit laquelle : **le locator donné sur l'air** (vert), **un QSO précédent du log ADIF** (cyan), **le carré du pays déduit du préfixe** (orange, libellé `GRID≈`).

TCQws connaît le centre des 240 entités DXCC de sa table de préfixes, affiné par le chiffre d'appel là où le pays est trop vaste pour qu'un centre veuille dire quelque chose — W1 tombe en FN43, W6 en DM06, quatre mille kilomètres les séparent. Mais un carré déduit reste une estimation : la France entière vaut JN16, et une station de Brest est en IN78. **Il s'affiche donc, et ne part pas au log** — un carré faux dans un ADIF voyage, se recroise, et plus personne ne sait d'où il sort. Pour le loguer, il faut le retaper : la case passe au vert, c'est devenu un fait vérifié par l'opérateur. Dès que la station donne son vrai carré, l'estimation cède la place toute seule.

### 📒 Un bouton LOG QSO

Sur la rangée des touches F1 à F8, parce que c'est là qu'on vient de taper son 73. Il enregistre au log le QSO en cours — la station de DEST, à défaut celle de DX. Trois situations l'exigent, toutes relevées sur l'air : le 73 du correspondant est passé sous le bruit, le QSO s'est mené avec des tournures que TCQws ne reconnaît pas comme une clôture, ou l'opérateur a simplement bavardé sans jamais écrire « 73 ». **Le QSO a bien eu lieu ; il faut pouvoir le dire.**

Une fois le QSO logué, **DEST, GRID et DX se vident ensemble** — mais seulement s'ils portaient bien cette station : on a souvent déjà appelé la suivante quand le 73 du précédent arrive enfin.

### ✏️ Renommer un bouton Macro

Le clic droit sur une touche F1 à F8 ouvre maintenant **deux cases** : le nom affiché sur le bouton, et le message émis. Qui change le contenu d'une touche change presque toujours sa raison d'être — la touche « Report » qui émet désormais un appel de détresse ADRASEC doit le dire sur le bouton. Chaque mode garde son jeu, et les réglages d'avant la v0.7.6 se relisent tels quels.

Au passage : la configuration rétablissait le mode **après** les touches, si bien qu'en rouvrant TCQws fermé en RTTY on retrouvait les touches du JTTY.

---

## v0.7.5 — Le RTTY

*2 octobre 2026*

### 📻 Le titre de l'onglet est devenu un bouton

Un clic sur **📻 JTTY** et il devient **📻 RTTY** : TCQws trafique en **Baudot — 45,45 bauds, shift de 170 Hz**, celui que tout le monde pratique depuis soixante ans.

Le JTTY entend onze décibels plus bas, mais il ne parle qu'au JTTY. Le RTTY se décode sur n'importe quoi, y compris du matériel des années 1970. **Un réseau d'urgence qui ne peut parler qu'à lui-même ne sert à rien** : c'est la seule raison d'être de ce mode.

| | JTTY | RTTY |
|---|---|---|
| Modem | 4-GFSK, 31,25 bauds, 127 Hz | 2-FSK Baudot, 45,45 bauds, shift 170 Hz |
| Fréquence 20 m | 14,090 MHz | 14,085 MHz |
| Longueur d'un message | 16 trames **et** 80 caractères | aucune limite |
| Touches F1 à F8 | grammaire WSJT-X | tournures RTTY |
| Seuil mesuré | − 16 dB | − 4 dB |

**Ce qui ne change pas** : le PROTOCOLE QSO, le radiogramme ACP 127, le métalangage MTL, le log ADIF, AUTO CQ et AUTO QSO, la file d'appel, les pays exclus, le dégagement ADRASEC. Rien de tout cela ne sait de quel modem il vient.

### 🎯 L'accrochage automatique

Un signal JTTY se cherche tout seul ; un signal RTTY, il faut se poser dessus. Le bouton 🎯 trouve les deux raies et s'y pose à deux ou trois hertz près — **un décalage de quinze hertz fait passer le taux d'erreur de 0 % à 31 %**. Le gabarit de la chute d'eau a par ailleurs la largeur du mode : il affichait 127 Hz devant un signal RTTY de 170, et on croyait être posé dessus.

### 🔧 Trois correctifs venus du trafic réel

**Un QSO mené à la main se logue.** Les touches du PROTOCOLE QSO émettaient sans jamais ouvrir ni clore le QSO : le 73 partait, et rien n'arrivait au Logbook. Un message qui s'adresse à une station l'ouvre désormais, un message qui porte un `73` ou finit par `SK` le clôt et l'enregistre.

**Une réponse sans indicatif ne bloque plus le QSO.** Relevé du 2 octobre : `F1GBD 599 KM18 F1GBD` — l'indicatif de l'expéditeur manquait. Le message est maintenant attribué à la station en cours, à trois conditions : un QSO engagé, la bonne fréquence à 60 Hz près, et aucun autre indicatif dans le message.

**Clic droit sur les boutons de bande JTTY.** Il manquait, alors que l'onglet Trafic l'avait. Chaque mode garde son propre jeu de fréquences.

---

## v0.7.4 — Le dégagement ADRASEC

*2 octobre 2026*

Le bandeau « expérimental » de l'onglet JTTY laisse la place à un **bouton ADRASEC**, orange sur bleu foncé. Un clic, et la radio passe sur **7,080 MHz (40 m)** : le point de ralliement du réseau quand la fréquence de travail devient inutilisable. Pas de confirmation — un bouton de dégagement sert au moment où la question serait de trop. La fréquence quittée est retenue : le bouton devient **↩ RETOUR**.

La bande ADRASEC de l'onglet Trafic passe de 7,084 à **7,080 MHz en FT4**, et son bouton prend la même couleur. Le FT8 garde 7,084.

Un bouton **🧹** dans le coin de la fenêtre de réception la vide — l'affichage seulement : journal, log, QSO en cours et file d'appel sont intacts.

---

## v0.7.3 — Le radiogramme en présence de trafic

*2 octobre 2026*

### 📨 Un radiogramme par station, plus un pour toute la bande

Relevé du 2 octobre, 09h12-09h21 : avec PA3AGN, IW0EFI et OE6VIE sur la même tranche, F4JHW a passé **quatre** radiogrammes. TCQws en a affiché **deux**, farcis du trafic des voisins — *« MESSAGE DE PA3AGN 599 001 M NR 4 … »* — et les deux autres n'ont jamais été vus. Le détecteur tenait **un seul accumulateur pour toute la bande** : il ouvrait sur `RGRAM` et avalait tout jusqu'au `<SK>`.

Chaque radiogramme suit désormais **sa propre piste**, repérée par son numéro et par la fréquence audio de l'émetteur, à 50 Hz près — une trame JTTY en occupe 127. Le même relevé rejoué rend les quatre, sans un mot étranger ; c'est devenu un essai permanent.

### 🔢 Des morceaux numérotés, donc renvoyables un par un

Chaque morceau porte son rang : `RGRAM RGRAM DE F1GBD R12.1/4 A F4JHW NR 12 P`, puis `R12.2 …`. Un morceau du voisin n'a pas le bon numéro et n'entre pas ; un morceau perdu est **nommé** — *« morceau 2 manquant sur 4 »* — et se redemande **seul** : 9 trames au lieu des 25 à 56 d'un renvoi complet. Le dernier morceau annonce qu'il est le dernier, donc un `<SK>` perdu n'empêche plus la remise.

### 📨 L'accusé de réception part tout seul

`F4JHW DE F1GBD QSL NR 9 <SK>` quand tout est là, `RPT NR 9 2 4 <SK>` sinon — et **sur la fréquence du radiogramme**, pas sur celle du QSO en cours. L'accusé attend un blanc pour ne pas couvrir le morceau qu'il réclame, et s'arrête après deux demandes. À l'autre bout, les morceaux réclamés repartent seuls et se remettent à leur place.

### 📉 Des morceaux plus courts, et l'identification en tête

Second relevé, 09h56 : d'un premier morceau de **14 trames**, quatre sont arrivées — et comme l'ACP 127 place les indicatifs après l'heure de dépôt, tout ce qui identifiait le message était dans les trames perdues. Formulaire vide, et pas même de quoi adresser une demande. Les morceaux sont donc plafonnés à **10 trames**, et l'expéditeur est nommé dès la **quatrième**. Un formulaire ne s'ouvre plus jamais vide : faute de texte lisible, il montre les trames reçues telles quelles.

La case *Morceaux numérotés* se décoche pour un correspondant qui relève au casque en morse : la forme émise redevient mot pour mot celle de la Station CW, vérifié contre son analyseur réel.

---

## v0.7.2 — On n'envoie pas son pedigree à qui ne nous a pas entendus

*2 octobre 2026*

Relevé sur l'air : TCQws répondait au CQ d'EA8ATE par le message RST complet — 23 secondes — et l'a répété trois fois à une station qui ne l'avait pas entendu, soit **1 min 08 s** de fréquence en pure perte. On répond maintenant comme en RTTY réelle : **son seul indicatif, 9 secondes**, et le report, le nom et le QTH partent à l'étape suivante. Trois appels sans réponse coûtent **28 secondes au lieu de 68**.

Les **`<BT>` et les crochets des prosignes disparaissent** des messages de QSO : un `<BT>` coûte deux trames et ne sépare rien que l'œil ne voie déjà. Le message RST passe de 12 trames à 9, la clôture de 12 à 7. Seul le radiogramme ACP 127 les garde — là, ils délimitent le corps et ferment la détection.

Le champ **Prénom** du bouton *ℹ Station* a enfin sa propre case : il écrivait dans `operateur`, qui est le champ ADIF de l'**indicatif** de l'opérateur, et annonçait `NAME F1GBD` sur l'air.

---

## v0.7.1 — Le radiogramme compact, et le style RTTY

*2 octobre 2026*

### 📨 Un tiers de trames en moins pour le radiogramme

L'ACP 127 en morse double les indicatifs et redit le compte de groupes parce qu'un opérateur CW lit à l'oreille, sans filet. En JTTY chaque trame porte un CRC-12 : elle arrive juste ou elle n'arrive pas, et répéter ne protège plus rien. **38 trames → 25**, **1 min 12 s → 47 s**. Seul l'en-tête `RGRAM` reste doublé : il tombe sur deux trames différentes, et un radiogramme non *détecté* ne déclenche pas l'alarme.

### 🗣 Répondre à chacun dans sa langue

Deux styles s'ajoutent : **RTTY**, qui mène le QSO automatique avec les messages du protocole QSO — un clic droit sur RST change donc ce que l'AUTO QSO raconte, nom et QTH compris — et **Auto (RTTY ⇄ WSJT-X)**, qui tranche au vu du CQ reçu. Un `DE` entre deux indicatifs, ou un prosigne de fin, et c'est de la RTTY ; sinon c'est du WSJT-X. Le style est retenu pour toute la durée du QSO.

### 🚫 Un message trop long ne part plus amputé

Un message JTTY tient dans 16 trames **et** 80 caractères. La seconde limite ne levait rien : le texte était coupé en silence, et le correspondant attendait une clôture qui n'arrivait jamais. Il est désormais refusé, avec son compte de caractères, et l'aperçu le signale en rouge avant la touche Entrée.

---

## v0.7.0 — Les trois outils de la Station CW, portés au JTTY

*2 octobre 2026*

Le mode JTTY reçoit les trois fonctions de la **Station CW de TCQ**, avec les mêmes formats et les mêmes variables : un opérateur passe de l'une à l'autre sans rien réapprendre.

- **📨 Radiogramme ACP 127 OTAN** : priorité (R, P, O, Z), destinataire, numéro, DTG en UTC, texte et compte des groupes. L'en-tête `RGRAM` déclenche la détection chez le destinataire, l'alarme sonne, et le formulaire s'ouvre noir sur blanc — un document qui s'imprime. Un radiogramme émis en CW se lit en JTTY, et réciproquement, vérifié contre l'analyseur de la Station CW lui-même.
- **🎛 Protocole QSO** : huit boutons sous les touches F1 à F8 — CQ, RST, 73, RBN, MSG1 à MSG4 — avec un champ DEST et un bouton REPLY, et les variables de la CW. Clic droit pour modifier un message.
- **📜 Script QSO Auto** : le métalangage **MTL** et ses sept commandes, avec un éditeur qui vérifie le script en direct. Un script fautif ne démarre pas.

Un **journal des radiogrammes** tient la main courante des messages reçus et émis, et le formulaire reçu permet d'y répondre, d'accuser réception ou de demander une répétition.

📄 **[Fiche technique FT-201 — MTL et radiogramme ACP 127](doc/FICHE_TECHNIQUE_TCQws_MTL_ACP127.pdf)**

---

## v0.6.1 — Le FT-847, et le JTTY après ses premières heures

*1er octobre 2026*

### 📻 Yaesu FT-847 — fréquence et PTT

Il suffit de le choisir dans *Radio*. Le poste parle le CAT binaire de Yaesu — cinq octets, l'opcode en dernier — avec trois particularités qui sont aussi les trois façons de se tromper avec lui : sa liaison série est à **deux bits de stop** (4800, 9600 ou 57600 bauds selon le menu 37 de la radio), TCQws les impose même si la configuration en demande un seul ; la radio **ignore tout en silence** tant qu'elle n'a pas reçu `CAT ON` (`00 00 00 00 00`), que TCQws envoie à l'ouverture du port ; le PTT est `00 00 00 00 08` / `00 00 00 01 88`, et la fréquence quatre octets BCD par dizaines de hertz suivis de l'opcode `01` — 14,090 MHz donne `01 40 90 00 01`. Les octets sont ceux du pilote Hamlib du poste, et les encodages de fréquence tombent sur les exemples publiés (439,70 MHz du manuel Yaesu, 28,150 MHz de la fiche VK4SN).

### 📻 Le JTTY après ses premières heures sur l'air

TCQws **n'écoute plus sa propre émission** : ce que la carte son réentend pendant qu'on émet est effacé de la fenêtre avant décodage, comme le fait WSJT-X, et le plancher de bruit de la chute d'eau est gelé pendant l'émission. Si un fantôme de votre message apparaît sous 200 Hz, c'est votre chaîne audio qui sature : ces raies sont les battements entre les quatre tons, espacés de 31,25 Hz.

Un **message mal rempli ne part plus** : une substitution restée en place — `%H` sans indicatif DX, ou une faute de frappe — est refusée à l'émission. Le bouton **⟲ Touches** rend aux huit touches leur contenu d'origine. Enfin, le rapport signal/bruit n'affiche plus `−99 dB` pour une trame qui touche le bord de la fenêtre d'analyse.

---

## v0.6.0 — TUNE, et le mode JTTY

*1er octobre 2026*

### 📶 Un bouton TUNE

Régler un coupleur ou lire un ROS demande une porteuse stable, pas un message. Le bouton **📶 TUNE** de la barre d'émission ferme le PTT et sort une porteuse pure sur la fréquence d'émission, au niveau réglé ; un second appui la coupe. Comme le *Tune* de WSJT-X : rampes de 20 ms au départ et à l'arrêt (une coupure franche claque dans toute la bande), émission normale suspendue tant qu'elle dure, et **arrêt de sécurité au bout de deux minutes** — une porteuse oubliée chauffe l'étage final et tient la fréquence occupée.

### 📻 Le mode JTTY, dans un onglet à part

**JTTY** est le mode asynchrone de WSJT-X 3.2 : ni période de 15 s, ni parité, ni message à cases. On tape une ligne, Entrée l'envoie, ce qui arrive se déroule au-dessus — c'est de la RTTY, et cela n'a rien à voir avec la fenêtre du FT8. D'où un **onglet 📻 JTTY** séparé. Le mode est **expérimental** : le modem est vérifié contre les sources de WSJT-X 3.2.0-rc1, mais le trafic réel reste à faire, et FT4/FT8 et JTTY ne tournent pas en même temps (une seule carte son).

Quatre tons espacés de 31,25 Hz, lissage gaussien BT = 2, 31,25 bauds, trame de 59 symboles en 1,888 s, 127 Hz occupés. Chaque trame porte 34 bits protégés par un CRC-12 et un code convolutif *tail-biting* de contrainte 10, décodés par Viterbi circulaire à liste (WAVA) avec addition cohérente par blocs de 2 et 4 symboles : **sensibilité mesurée à −16 dB** dans 2 500 Hz, pour une limite théorique de −17 dB.

La réception tourne en continu sur une fenêtre glissante : le message s'affiche trame après trame, et une trame perdue au milieu laisse un trou marqué `…` au lieu de couper la phrase en deux. L'émission part tout de suite, avec une file d'attente pour taper la suite pendant que le message précédent sort.

Toute la grammaire de WSJT-X est reprise — indicatifs, séries, zones CQ et ITU, états et provinces, sections ARRL/RAC, préfixes, locators, classes Field Day, heure, phrases de service, texte libre — et le message est découpé dans **le plus petit nombre de trames possible**, selon trois profils d'échange : courant, Field Day, RTTY Roundup (où `599 05` devient `599 005`). L'onglet reprend les habitudes de la RTTY : touches **F1 à F8** modifiables, file d'appel alimentée toute seule, double-clic sur un indicatif reçu pour le prendre comme DX, chute d'eau cliquable, et boutons de bande 160 m à 2 m aux fréquences JTTY avec envoi CAT.

### 🔎 Au passage

Le décodeur JTTY écarte les trames dont la synchronisation ne tombe pas juste. Un CRC de douze bits laisse passer une charge utile fausse sur quatre mille : à côté d'un signal fort, cela donnait quelques lignes vides par minute. Le contrôle les supprime et, comme il intervient avant le Viterbi, il divise par deux le temps de décodage.

---

## v0.5.2 — La bonne distance

*23 septembre 2026*

### 📏 « RR73 » n'est plus pris pour un locator

`RR73` a la forme d'un carré Maidenhead, et ce carré existe, au nord du détroit de Béring. Une station des Pays-Bas qui répondait `F1GBD PH1M RR73` était annoncée **à 5 338 km**, plein nord, et posée sur la carte au milieu de l'Arctique, alors que son CQ donnait 478 km. La distance et la carte ne retiennent maintenant que les vrais locators. Le log ADIF n'était pas touché : il écartait déjà `RR73` du champ `GRIDSQUARE`.

### 📍 La distance reste affichée pendant le QSO

Les messages d'un QSO ne portent pas de locator. La distance disparaissait donc dès le premier échange, y compris sur les lignes rouges qui vous sont adressées. TCQws garde maintenant le locator entendu dans le CQ de la station : les 478 km restent affichés jusqu'au 73. Sans CQ entendu, seul le pays s'affiche — rien n'est inventé.

### 📻 La bande active sur chaque trait de période

Annoncé en v0.5.1, absent du binaire publié : le trait qui sépare deux périodes dans *Activité de bande* porte bien, depuis cette version, la bande et la fréquence (`── ADRASEC ──  7.084 MHz`).

---

## v0.5.1 — Le réseau a son bouton

*21 septembre 2026*

### 📻 Un bouton ADRASEC dans la barre des bandes

Un réseau départemental se donne rendez-vous sur **sa propre fréquence**, à l'écart du segment encombré de 7,074 MHz. Le bouton **ADRASEC**, en tête de la barre *Bande*, y porte la radio d'un clic : **7,084 MHz** par défaut en FT8 comme en FT4, et un **clic droit** pour la changer — un autre département, un exercice sur 80 m. Le log garde la vraie bande, déduite de la fréquence (`40m` sur 7,084) : ADIF ne connaît que les bandes radio.

### 📏 La bande active sur chaque trait de période

Le trait qui sépare deux périodes dans *Activité de bande* porte la bande et la fréquence (`── ADRASEC ──  7.084 MHz`). Après un changement de bande, on sait d'un coup d'œil où chaque station a été entendue. Une fréquence retapée à la main prend le nom de sa bande radio : le trait n'annonce jamais « ADRASEC » sur 14,074.

*Les v0.4.0 et v0.5.0 n'ayant pas été publiées séparément, la v0.5.1 apporte aussi tout leur contenu, décrit ci-dessous.*

---

## v0.5.0 — Le satellite commute tout seul

*20 septembre 2026*

### 🌍 Le filtre d'exclusion prend tout le QSO

Écarter un pays ne marchait que tant qu'il appelait **CQ**. Dès qu'une station exclue engageait un contact, son correspondant la nommait — `UA3ABC G6LTT -17` est émis par G6LTT, qui n'est pas exclu — et **la moitié de l'échange revenait** dans *Activité de bande* comme dans *Fréquence RX*.

Un décodage est maintenant écarté dès qu'**un seul** de ses indicatifs relève d'un pays exclu : absent des deux tableaux, absent de la carte, et ignoré par la séquence automatique comme par AUTO QSO. **Y compris un appel qui vous est adressé** : exclure un pays, c'est refuser de l'entendre *et* de le travailler, et un appel direct est précisément le seul message que vous risqueriez de prendre pour un QSO.

### 📏 Deux colonnes qui respirent

Un message FT8 fait au plus 22 caractères. Lui donner toute la place disponible laissait un grand vide à droite du texte pendant que `Pays-Bas • 5338 km` se faisait couper. Les colonnes **Message** et **Pays • km** s'étirent désormais ensemble, dans les deux tableaux.

### 🛰 Split automatique Rx / Tx en bande SAT

Une station satellite n'émet pas là où elle écoute. Deux champs dans *Fréquences spéciales*, **Radio Rx** et **Radio Tx**, portent ce que le transceiver affiche vraiment — 28,540 et 28,040 MHz sur un montage QO-100 — et TCQws **porte le VFO sur Radio Tx avant chaque message émis, puis le ramène sur Radio Rx**. Rien n'est calculé : ni case à cocher, ni écart imposé. Un transpondeur n'est pas forcément inverseur, et un relais V/U écoute en 2 m pour émettre en 70 cm. L'écart est seulement rappelé sous le champ, où une faute de frappe se voit.

**Les fréquences réglées sont celles de la radio** : avec un downconverter QO-100 (10 489,540 → 28,540), c'est la sortie du convertisseur. Plus de conversion à faire de tête.

**Le log ne suit pas la radio** : quelle que soit la fréquence affichée, le QSO reste enregistré sur la montée réelle — 2400,040 MHz, bande **13 cm**, `prop_mode SAT`.

L'ordre compte et il est vérifié sur l'éther simulé : commutation **avant** le PTT (0,3 s, de quoi laisser passer une commande CI-V à 1200 bauds), retour en réception **après** son relâchement, jamais pendant l'émission — sur un port CAT séparé, changer de VFO pendant l'émission est refusé ; sur un port partagé, cela couperait la porteuse. Deux fréquences identiques : le VFO ne commute pas, et le journal le dit. Une configuration réglée sous l'ancienne case à cocher est reprise automatiquement.

**Le retour en réception est envoyé, puis confirmé** — une commande 0,25 s après le PTT, une seconde au début de la période suivante. Une radio restée sur la fréquence d'émission est sourde et rien ne le signale ; or une commande CI-V se perd, et une radio qui n'a pas fini de quitter l'émission en ignore une sans le dire. TCQws renvoie donc l'ordre même quand il croit la fréquence déjà bonne. Une fin de QSO, le bouton *Arrêter TX* ou un arrêt de station ramènent aussi le VFO au milieu d'une émission ; à l'arrêt, un échec est écrit en clair. Un CAT en échec n'empêche pas d'émettre — la radio reste en réception, ce qui s'entend.

### 🔌 Aucun port COM ouvert en écoute SDR

Une clé n'est pas un transceiver : les cadres **PTT** et **CAT** sont entièrement grisés tant que la source est une clé, et les boutons de test expliquent pourquoi. Sans cela, TCQws ouvrait un port COM inexistant et échouait au démarrage sur `could not open port 'COM1'`.

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
