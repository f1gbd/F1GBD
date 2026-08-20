<div align="center">

<img src="images/AERO-SPECTRIX.png" alt="AERO-SPECTRIX" width="200">

# AERO-SPECTRIX

**Radar acoustique de détection, de localisation et de poursuite d'aéronefs sans pilote**

![version](https://img.shields.io/badge/version-1.3.0-0B3B57)
![plateforme](https://img.shields.io/badge/plateforme-Windows%2010%20%2F%2011%20x64-0B3B57)
![tests](https://img.shields.io/badge/tests-42%2F42-1B7F4F)
![licence](https://img.shields.io/badge/licence-gratuite%20%E2%80%94%20usage%20libre-D2600F)

*par F1GBD — ADRASEC 77 / FNRASEC*

</div>

---

Quatre microphones disposés en tétraèdre, et un écran de type radar.
AERO-SPECTRIX détecte, localise et suit un drone ou un avion léger **à son
seul bruit** : ni radio, ni radar, ni caméra. Un aéronef silencieux du point
de vue radio, sans télémétrie et de nuit, reste parfaitement audible.

Le principe tient en une phrase : le son n'arrive pas exactement au même
instant sur les quatre microphones, et ces quelques microsecondes d'écart
suffisent à retrouver la direction de la source. Avec une antenne de 70 cm
d'arête, l'écart maximal entre deux microphones vaut 2 047 µs, soit
98 échantillons à 48 kHz — largement mesurable.

<div align="center">
<img src="images/D%C3%A9tection_ALERTE.png" alt="Poursuite en cours, alarme déclenchée" width="900">
<br><em>Poursuite en cours. Le bandeau rouge signale une signature acoustique confirmée : azimut 360°, élévation 19°, BPF 213 Hz, score 4,9 dB.</em>
</div>

---

## Sommaire

- [Ce que le système fait](#ce-que-le-système-fait)
- [Ce qu'il ne fait pas](#ce-quil-ne-fait-pas)
- [Performances](#performances)
- [Installation](#installation)
- [Prise en main en cinq minutes](#prise-en-main-en-cinq-minutes)
- [Fonctionnalités](#fonctionnalités)
- [Lire le scope](#lire-le-scope)
- [Le matériel](#le-matériel)
- [Version d'évaluation à bas coût](#version-dévaluation-à-bas-coût)
- [Documentation](#documentation)
- [Validation](#validation)
- [Nouveautés de la version 1.3.0](#nouveautés-de-la-version-130)
- [Architecture](#architecture)
- [Licence](#licence)

---

## Ce que le système fait

Une seule application, deux modes, **la même chaîne de traitement dans les
deux** — ce que vous validez en simulation est littéralement le code qui
tournera sur le matériel.

| Mode | Ce qu'il fait | À quoi il sert |
|---|---|---|
| **Simulation** | Reconstitue une scène acoustique complète — signature de l'aéronef, propagation dans l'atmosphère, bruits d'ambiance et de vent — et fait tourner la chaîne de traitement dessus | Préparer une mission, dimensionner l'antenne, se former, évaluer une portée avant de sortir le matériel |
| **Direct** | Applique la même chaîne au flux réel d'une carte son quatre voies | Exploitation sur le terrain |

La chaîne de traitement est classique et documentée : détection par peigne
harmonique, corrélations croisées **GCC-PHAT** interpolées, carte
**SRP-PHAT** sur l'hémisphère céleste, résolution de la direction par
moindres carrés avec rejet d'aberrants, puis **filtre de Kalman** avec
initiation de piste M-de-N.

<div align="center">
<img src="images/D%C3%A9tection_acoustique.jpg" alt="Vue d'ensemble d'un passage au zénith" width="900">
<br><em>Un passage au zénith, vu de bout en bout : carte SRP-PHAT, spectrogramme
avec les harmoniques suivies, azimut et élévation pistés contre la vérité, et
score de peigne au regard du seuil de détection.</em>
</div>

## Ce qu'il ne fait pas

Trois limites à connaître avant de s'en servir. Aucune ne relève d'un défaut
du logiciel : elles tiennent à la physique de la mesure acoustique passive.

- **Pas de distance.** Une antenne unique mesure une **direction**, jamais une
  position. Obtenir la distance suppose une seconde antenne distante de 50 à
  200 m, ou une hypothèse d'altitude connue.
- **Le vent est l'ennemi n° 1.** Le pseudo-bruit de vent sur les capsules croît
  d'environ **+17 dB par doublement de la vitesse**. Au-delà de 4 à 5 m/s, la
  portée s'effondre quelles que soient les bonnettes.
- **Latence physique incompressible.** À 300 m, le son met 0,88 s à parvenir aux
  microphones. Le scope montre donc où l'aéronef **était**, pas où il est.

## Performances

Portées de détection prévues par le bilan de liaison, en campagne de jour
(bruit de fond 34 dB(A), vent 2,5 m/s, antenne de 70 cm) :

| Aéronef | Niveau à 1 m | Fréquence suivie | Portée |
|---|---:|---:|---:|
| Mini quadricoptère (DJI Mini) | 68 dB(A) | 273 Hz | 128 m |
| Quadricoptère moyen (Phantom) | 76 dB(A) | 207 Hz | 258 m |
| Gros hexacoptère | 84 dB(A) | 140 Hz | 400 m |
| Aile / hélice unique électrique | 79 dB(A) | 233 Hz | 615 m |
| Avion thermique 4 temps, 4 cyl. | 90 dB(A) | 167 Hz | 1 071 m |
| Avion thermique 2 temps, 2 cyl. | 92 dB(A) | 233 Hz | 1 391 m |
| Avion thermique 2 temps, 4 cyl. | 95 dB(A) | 400 Hz | 1 974 m |

**Précision angulaire** : 0,14° dans les meilleures configurations, 0,70° dans
les plus défavorables, avec une arête de 70 cm. Erreur médiane mesurée sur le
scénario de référence : **0,27°**.

<div align="center">
<img src="images/Calculs_temps_r%C3%A9el.png" alt="Onglet Performances" width="900">
<br><em>L'onglet <strong>Performances</strong> : azimut et élévation contre la
vérité, erreur de pointage en échelle logarithmique, score de peigne et résidu
des moindres carrés, effet Doppler sur la fréquence de passage de pale, erreur
en fonction de la distance.</em>
</div>

> **Le facteur qui domine tout n'est pas le matériel, c'est le site.** À
> matériel constant, la portée passe de 22 m en environnement urbain à 655 m
> sur un site de campagne très calme. Gagner 10 dB sur le bruit de fond —
> s'éloigner d'une route, se placer derrière un talus, opérer de nuit —
> multiplie la portée par trois. Aucun réglage n'a cet effet.

## Installation

Téléchargez **`aero-spectrix.7z`** (environ 119 Mio): https://github.com/f1gbd/F1GBD/releases/download/v1.30/AERO-SPECTRIX.7z puis décompressez-la
où vous voulez — [7-Zip](https://www.7-zip.org/) ou tout autre outil sachant
lire ce format. Vous obtenez un dossier `AERO-SPECTRIX\` contenant :

| Élément | |
|---|---|
| `AERO-SPECTRIX.exe` | l'application — c'est le fichier à lancer |
| `_internal\` | les bibliothèques dont elle a besoin |
| `AERO-SPECTRIX_fiche_technique.pdf` | la fiche technique |
| `LICENSE` | la licence d'utilisation |
| `THIRD-PARTY-NOTICES.txt` | les licences des composants tiers |

**Distribuez et déplacez le dossier entier**, jamais le seul `.exe` : les
bibliothèques posées à côté de lui sont indispensables. Rien à installer, rien
à désinstaller : pour supprimer l'application, supprimez le dossier.

| Élément | Détail |
|---|---|
| Système | Windows 10 ou 11, 64 bits |
| Mémoire vive | 4 Go minimum, 8 Go recommandés |
| Espace disque | environ 400 Mo, dossier décompressé |
| Écran | 1 366 × 768 minimum |
| Droits | aucun droit d'administrateur nécessaire |
| Réseau | aucun — l'application ne communique avec rien |
| Carte son | uniquement pour le mode Direct |

Comptez **2 à 4 secondes** avant l'affichage de la fenêtre ; un écran de
démarrage couvre l'attente.

<details>
<summary><strong>Si Windows affiche un avertissement SmartScreen</strong></summary>

L'exécutable n'est pas signé par un certificat commercial. Windows affiche
alors « Windows a protégé votre ordinateur ». Cliquez sur *Informations
complémentaires* puis *Exécuter quand même*. Le message ne signale pas un
problème détecté : il signale que l'éditeur n'a pas payé de certificat de
signature de code. Le SHA-256 publié avec chaque release est là pour vous
permettre de vérifier vous-même que le fichier téléchargé est bien celui qui a
été publié :

```powershell
Get-FileHash -Algorithm SHA256 aero-spectrix.7z
```
</details>

## Prise en main en cinq minutes

1. Lancez l'application et **ne touchez à rien**. Le scénario par défaut est un
   quadricoptère qui passe au-dessus de l'antenne.
2. Regardez le **bilan de liaison** en bas à droite : il annonce déjà une portée
   d'environ 258 m, avant tout calcul.
3. Cochez **ALARME**, cliquez sur **Test** : le bandeau doit clignoter et la
   sirène retentir. À faire une fois par séance.
4. Cliquez sur **▶ Lancer la simulation** (ou `F5`). Comptez cinq à huit fois la
   durée simulée en temps de calcul. **Le scope reste vide pendant ce temps —
   c'est normal**, la piste n'apparaît qu'à la fin.
5. La relecture démarre toute seule. Cochez **Écouter le son** : vous entendez le
   bourdonnement du quadricoptère.

Le rond ○ est la piste estimée, la croix × orange la position vraie. L'écart
entre les deux est l'erreur réelle, affichée en chiffres.

## Fonctionnalités

<table>
<tr><td width="50%" valign="top">

**Détection et poursuite**
- Peigne harmonique auto-adaptatif, 90–520 Hz
- GCC-PHAT interpolé ×16 + raffinement parabolique
- Carte SRP-PHAT sur l'hémisphère
- Moindres carrés sur 6 paires, rejet d'aberrants
- Initiation de piste M-de-N avec cohérence angulaire
- Filtre de Kalman à vitesse angulaire constante

</td><td width="50%" valign="top">

**Simulation acoustique**
- Multirotors et moteurs à pistons 2 et 4 temps
- Propagation à retard variable — le Doppler émerge du calcul
- Absorption atmosphérique ISO 9613-1
- Réflexion par le sol (source image)
- Bruits d'ambiance, de vent et de microphone
- Pondération A selon CEI 61672

</td></tr>
<tr><td valign="top">

**Alarme**
- Déclenchement sur **conjonction de quatre critères indépendants**
- Sirène en boucle, bandeau clignotant, flash de la barre des tâches
- Alarme à verrou, acquittement par bouton, `Ctrl+A` ou double-clic
- Bouton **Test** pour vérifier que le son sort réellement

</td><td valign="top">

**Sorties**
- Export WAV 4 voies calibrées (1.0 = 1 pascal)
- Enregistrement continu du flux réel, sans limite de durée
- Vidéo du scope en MP4 ou GIF animé
- Piste CSV, figures de performance, configuration JSON

</td></tr>
</table>

<div align="center">
<img src="images/Spectrogramme.png" alt="Onglet Spectrogramme" width="900">
<br><em>L'onglet <strong>Spectrogramme</strong> : moyenne des quatre voies, avec
les harmoniques de la fréquence de passage de pale suivies trame par trame
(points clairs). À droite, le bilan de liaison annonce la portée avant tout
calcul.</em>
</div>

### L'alarme, en détail

Déclencher sur un simple dépassement de seuil serait inutilisable : un coup de
vent, une portière, un oiseau franchissent ce seuil plusieurs fois par minute,
et une alarme qui crie pour rien est désarmée au bout d'un quart d'heure.
AERO-SPECTRIX exige donc **quatre conditions simultanées**, chacune éliminant
une famille différente de fausses alarmes :

| Critère | Ce qu'il vérifie | Ce qu'il élimine |
|---|---|---|
| Score de peigne | Une famille d'harmoniques régulièrement espacées | Bruits large bande : vent, circulation, feuillage |
| Résidu TDOA | Les six temps d'arrivée désignent **une** direction | Champ diffus, échos, réverbération |
| Piste confirmée | M mesures sur N trames, cohérentes en direction | Bruits impulsionnels |
| Persistance | La conjonction tient N trames consécutives | Coïncidences fortuites |

<div align="center">
<img src="images/Donn%C3%A9es.png" alt="Onglet Données" width="900">
<br><em>L'onglet <strong>Données</strong> donne le détail trame par trame —
score, fréquence de passage de pale, direction brute, direction pistée, résidu,
erreur — et s'exporte en CSV.</em>
</div>

## Lire le scope

<div align="center">
<img src="images/Scope.jpg" alt="Le scope dôme céleste" width="520">
</div>

Une antenne unique mesure une direction, pas une distance. L'écran est donc un
**dôme céleste** et non un PPI en mètres :

- l'**angle autour du cercle** est l'azimut — 0° au Nord, sens horaire ;
- le **rayon** est l'angle zénithal — le centre correspond à un aéronef à la
  verticale, le bord à l'horizon ;
- le **fond vert** est la carte SRP-PHAT, l'énergie reçue de chaque direction.
  Les arcs ne sont pas un artefact : ce sont les surfaces de temps d'arrivée
  constant d'une antenne à quatre éléments.

Ce choix est une question d'honnêteté d'affichage : présenter des mètres
reviendrait à afficher une information dont l'instrument ne dispose pas.

> **L'indicateur le plus utile est le résidu TDOA.** Quatre microphones forment
> six paires pour trois inconnues : il reste trois mesures redondantes. Le
> résidu mesure leur désaccord, et c'est le seul indicateur capable de dire
> qu'une direction affichée est fausse. Sous 20 µs, faites confiance ; au-delà
> de 60 µs, la mesure est rejetée automatiquement.

## Le matériel

<div align="center">
<img src="images/Antenne_acoustique.png" alt="Géométrie du tétraèdre et cotes de montage" width="900">
<br><em>Le schéma de câblage est généré depuis la configuration courante : les
cotes affichées sont celles de votre antenne, pas celles d'un exemple.</em>
</div>

L'antenne est un **tétraèdre régulier** : les quatre microphones occupent les
sommets alternés d'un cube, donc toutes les paires ont exactement la même
longueur de base et la précision angulaire est isotrope. En pratique, cela se
ramène à **deux barres identiques croisées à 90° et décalées en hauteur** —
pour une arête de 70 cm : deux barres de 70,0 cm, décalage de 49,5 cm.

> **Tolérance de construction : ± 2 mm.** Une erreur de 5 mm sur une barre de
> 70 cm introduit 0,4° de biais **systématique** — il ne se moyenne pas avec le
> temps et aucun filtrage ne l'élimine.

### La contrainte qui commande tout

> [!IMPORTANT]
> **Un seul périphérique audio pour les quatre voies.** Deux interfaces stéréo
> séparées ne conviennent pas, même de modèle identique : leurs horloges
> dérivent de quelques dizaines de ppm, soit des dizaines de microsecondes par
> seconde. Mesuré sur scène simulée, avec deux quartz écartés de 5 ppm : le
> résidu TDOA passe de 10 à 106 µs en une minute, franchit le seuil de rejet, et
> la chaîne cesse de déclarer une piste.

Ce qu'il faut donc chercher, dans l'ordre : **quatre entrées microphone sur un
seul boîtier**, une **alimentation fantôme** si les capsules en réclament, un
**pilote ASIO du constructeur** sous Windows, et la possibilité de **désactiver
les traitements** — coupe-bas, limiteur, compresseur, réduction de bruit. Ces
derniers sont souvent actifs par défaut sur les enregistreurs de podcast et
déforment la phase entre les voies, c'est-à-dire exactement la grandeur que le
système mesure.

Sous **Windows**, le pilote de classe n'expose que deux voies quelle que soit
l'interface : les quatre n'apparaissent qu'avec le pilote **ASIO** du
constructeur. Sous **Linux**, ce problème n'existe pas — une interface conforme
à la classe audio 2 fonctionne avec le pilote générique du noyau.

### Les microphones

| Type | Sensibilité | Bruit propre | Verdict |
|---|---:|---:|---|
| Électret de mesure (Primo EM272) | 40 mV/Pa | 14 dB(A) | la référence |
| MEMS numérique I²S (ICS-43434) | 25 mV/Pa | 29 dB(A) | bon, si les horloges sont partagées |
| MEMS numérique I²S (INMP441) | 25 mV/Pa | 33 dB(A) | correct et bon marché |
| Dynamique de chant cardioïde | 2 mV/Pa | 26 dB(A) | **à éviter** |

**Omnidirectionnel obligatoire.** Une cardioïde introduit un déphasage variable
en fréquence qui dégrade directement la corrélation croisée, et laisse des
trous de couverture dans le ciel.

**Bonnettes mousse + fourrure sur chaque capsule, sans exception.** Une capsule
nue dans un montage de quatre suffit à ruiner la mesure.

## Version d'évaluation à bas coût

Le montage de référence revient à 320–650 €. Pour répondre à la seule question
qui se pose au départ — *est-ce que ça marche, chez moi, sur ce que je veux
détecter ?* — deux montages d'évaluation suffisent.

| Montage | Coût | Mise au point | Verdict |
|---|---:|---|---|
| **A** — Teensy 4 + 4 capsules MEMS I²S | 69–94 € | flasher un croquis | le moins cher |
| **B** — PC ou Pi + interface USB classe audio 2 | 510–820 € | aucune | fonctionne tel quel |
| **C** — Raspberry Pi + I²S natif | — | — | **à écarter** : 2 voies seulement |

`AudioInputI2SQuad` lit quatre voies sur **un seul** périphérique SAI : la
synchronisation découle du **câblage**, pas d'un réglage qu'on pourrait rater.
C'est ce qui rend un montage à 70 € valable pour de la mesure de temps
d'arrivée, alors que bien des solutions plus chères ne le sont pas.

Le document *Version d'évaluation à bas coût* détaille les deux montages :
schémas de câblage, nomenclatures chiffrées, croquis Teensy quatre voies, pont
série vers le PC et procédure de mesure des écarts résiduels entre voies.

> **En campagne de jour, le montage à 70 € perd 6 % de portée** face à la chaîne
> de mesure à 500 €. Le facteur limitant n'est pas le microphone, c'est le site :
> à 34 dB(A) de bruit ambiant, un plancher de capsule à 33 dB(A) disparaît
> dedans. L'écart ne se creuse qu'en site très calme (−35 %).

## Documentation

| Document | Contenu |
|---|---|
| **Manuel de l'utilisateur** | 35 pages : prise en main, exploitation, référence des paramètres, diagnostic |
| [**Fiche technique**](documents/AERO-SPECTRIX_fiche_technique.pdf) | Les fonctionnalités de l'application |
| **Version d'évaluation à bas coût** | 18 pages : montages Teensy et électret, schémas, nomenclatures |
| **Étude de coûts** | 18 pages : sept paliers chiffrés, du simulateur au poste opérationnel |
| **Schéma de câblage** | Page HTML autonome, cotes calculées depuis la configuration |

## Validation

Chaque version est soumise à **42 tests de non-régression** avant publication,
comparés à des références **indépendantes** du logiciel — un simulateur vérifié
contre lui-même ne prouve rien :

- absorption atmosphérique **ISO 9613-2**, quatre couples température / humidité ;
- pondération A **CEI 61672**, neuf fréquences ;
- borne théorique de précision angulaire ;
- 41 retards fractionnaires connus ;
- effet Doppler émergeant du calcul de propagation, à 0,02 Hz près ;
- raies d'un moteur à pistons : allumage = rotation × cylindres × 2/temps ;
- logique d'alarme : cinq tests vérifient qu'elle **refuse** de partir sur un
  signal fort mais incohérent ;
- intégrité des WAV écrits au fil de l'eau, comparaison bit à bit.

```
==========================================================================
  42/42 tests réussis
==========================================================================
```

## Nouveautés de la version 1.3.0

- **Alarme sonore et visuelle** sur confirmation de signature acoustique —
  quatre critères indépendants, sirène de synthèse, bandeau clignotant,
  alarme à verrou et acquittement.
- **Export du son en WAV** : trois fichiers en simulation (calibré, écoute,
  voie boostée) et **enregistrement au fil de l'eau** en mode Direct, sans
  limite de durée.
- **Enregistrement vidéo du scope** en MP4 ou GIF, dans un fil séparé, avec
  progression et annulation.
- **Fenêtre adaptative** : dimensionnement sur la zone réellement disponible de
  l'écran, mode compact, `Ctrl+0` pour réajuster, `F11` plein écran.
- **Version d'évaluation à bas coût** documentée : croquis Teensy 4 voies, pont
  série vérifié, schémas MEMS et électret, calibration des écarts entre voies.
- **Correction** du bruit propre des préréglages MEMS, aligné sur les fiches
  constructeur (29 et 33 dB(A) au lieu de 20 et 24).
- 28 → **42 tests** de non-régression.

## Architecture

Le programme s'articule autour de modules aux responsabilités séparées :
synthèse de la scène acoustique, propagation, détection, localisation,
poursuite, décision d'alarme, affichage, bilan de liaison, acquisition.

Le point clé tient en une phrase : **une seule** implémentation de l'algorithme
de localisation, utilisée à la fois par la simulation hors ligne et par
l'acquisition temps réel. C'est ce qui donne son sens au mode Simulation — ce
que vous y validez est littéralement ce qui tournera sur le matériel, et non un
modèle approchant.

## Licence

AERO-SPECTRIX est un **logiciel gratuit mais non libre**. Texte complet dans
[`LICENSE`](LICENSE).

**Vous pouvez** l'utiliser sans limite de durée et sur autant de postes que vous
voulez, à titre personnel, associatif, pédagogique, professionnel ou
opérationnel ; et le redistribuer gratuitement, à condition que l'archive reste
complète et non modifiée.

**Vous ne pouvez pas**, sans accord écrit, le vendre ou l'inclure dans une offre
payante, le modifier, ni le redistribuer sous un autre nom.

Le code source n'est pas publié. Le logiciel est fourni **sans aucune
garantie** ; il ne constitue pas un équipement de sûreté certifié et ne se
substitue pas aux moyens réglementaires de surveillance de l'espace aérien.

### Composants tiers

AERO-SPECTRIX embarque des bibliothèques développées par des tiers, listées
dans [`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md), dont le texte intégral
des licences accompagne l'archive.

> [!NOTE]
> **AERO-SPECTRIX utilise la bibliothèque Qt, au travers de PySide6, sous
> licence GNU LGPL version 3.** C'est la raison pour laquelle l'application est
> distribuée en dossier et non en fichier unique : les bibliothèques Qt y
> restent des fichiers distincts, que vous pouvez remplacer par une version
> modifiée, comme cette licence l'exige. Le code source correspondant est
> publié par The Qt Company, et fourni sur simple demande.

---

<div align="center">

**AERO-SPECTRIX 1.3.0** par **F1GBD** — ADRASEC 77 / FNRASEC

*Destiné à l'étude, à la formation et aux opérations de sécurité civile.
L'emploi de moyens de détection est soumis à la réglementation en vigueur.*

</div>
