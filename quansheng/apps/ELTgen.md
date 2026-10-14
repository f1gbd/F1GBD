# ELTgen v1.0 — balise ELT d'entraînement pour Quansheng UV-K1 / UV-K5 v3

Application overlay (`.app`) pour le firmware F4HWN édition Labs. Elle transforme
le portatif en **balise ELT d'entraînement** : sur le VFO d'émission, elle module
la porteuse avec le **« whoop » caractéristique des balises de détresse ELT** — une
tonalité **balayée en glissando descendant ~1550 → 640 Hz**, répétée **~2,3 fois/s**,
reproduite fidèlement à partir d'un vrai signal ELT (`elt.wav`). Elle **identifie en
CW** (indicatif de la radio) périodiquement.

Objectif : **tester HOMER en conditions réelles sur le terrain** avec une antenne
Yagi (homing au niveau reçu + whoop audible), sans mobiliser une vraie balise.

> ⚠️ **ELTgen émet réellement — usage réservé aux radioamateurs licenciés.**
> **Bande 2 m uniquement** (p. ex. **144.610 MHz FM**, usage SATER/ADRASEC).
> **JAMAIS 121,5 MHz** (bande aéronautique, interdit et dangereux) : hors bande, le
> firmware refuse d'émettre et ELTgen affiche **TX OFF**.

| | |
|---|---|
| Fréquence | celle du **VFO** d'émission (144.610 MHz FM conseillée ; 2 m amateur) |
| Modulation | FM, tonalité **balayée 1550 → 640 Hz, ~2,3 balayages/s** (profil `elt.wav`) |
| Identification | **CW** (indicatif de la radio), 1000 Hz, intervalle **60 / 120 / 300 s** |
| Modes | **Continu** (comme une vraie balise) / **Intermittent** (4 s / 4 s) |
| Garde-fou | émission seulement si le firmware l'autorise — **hors bande → TX OFF** |
| Taille | 3 938 o de code (overlay 4 Kio) |

Manuel complet : [PDF](../documentation/ELTgen_Manuel_v1.0.pdf).

## Installation

1. Ouvrir l'**[UV-K1 Apps Uploader](https://f1gbd.github.io/F1GBD/quansheng/)** dans Chrome ou Edge.
2. Brancher la radio (USB-C), **Connecter la radio**, choisir le port série.
3. Sélectionner **Balise ELT d'entraînement (ELTgen)**, garder l'emplacement proposé, **Installer**.

## Mise en route

1. Régler le **VFO en émission** sur **144.610 MHz FM** (ou une autre fréquence 2 m), puissance voulue.
2. Radio : **Apps → ELTgen** — l'app s'ouvre en **VEILLE** (« PRÊT », **aucune émission**).
3. Régler les paramètres : **indicatif** (touche `3`), **mode** (`1`), **intervalle d'ID** (`2`).
4. **`MENU`** : **démarre l'émission** — la porteuse monte, le whoop ELT est émis, l'indicatif part en CW.
5. Lancer la recherche avec **[HOMER](https://github.com/f1gbd/F1GBD/tree/master/homer)** (clé RTL-SDR ou source UV-Kx) et l'antenne Yagi.
6. **`EXIT`** : **arrête l'émission** (retour en VEILLE) ; **`EXIT`** en veille **quitte** l'app.

## Commandes

| Touche | Fonction |
|---|---|
| `1` | Mode **CONT** (continu) / **INTER** (intermittent 4 s / 4 s) |
| `2` | Intervalle de l'**ID CW** : 60 / 120 / 300 s |
| **`3`** | **Saisir l'indicatif** (ID CW) — voir ci-dessous |
| `MENU` | **En veille : démarre l'émission** · en émission : ré-arme le compte à rebours de l'ID |
| `EXIT` | **En émission : arrête** (retour veille) · **en veille : quitte** l'app |
| `F` (appui long) | Verrouillage du clavier |

L'app démarre en **VEILLE** : on règle tous les paramètres (dont l'indicatif) **avant**
de lancer l'émission par `MENU`. L'écran d'émission affiche l'état (**ELT** / **ID** /
**PAUSE**), le compte à rebours avant la prochaine identification, le mode, l'intervalle
d'ID, la fréquence d'émission et l'**indicatif courant** (`ID:…`).

## Saisir l'indicatif (touche 3)

Comme les autres apps, l'indicatif de l'ID CW se saisit **sur la radio**, dans l'app :

1. Appuyer sur la touche **`3`** → l'éditeur d'indicatif s'ouvre (en émission, elle est coupée pendant la saisie).
2. **▲/▼** change le caractère sous le curseur (**A-Z / 0-9 / `/`**) ; les **touches chiffres** tapent directement un chiffre (et avancent).
3. **`F`** passe au caractère suivant ; **`*`** efface (recule).
4. **`MENU`** enregistre, **`EXIT`** annule.

L'indicatif est **mémorisé** dans l'app. S'il est laissé vide, ELTgen reprend la
**1ʳᵉ ligne du message d'accueil** de la radio (API `boot_callsign`). Sans indicatif,
aucune ID CW n'est émise.

## Notes techniques

- Le balayage ne réécrit que le **registre de tonalité du BK4819** (REG_71) pas à
  pas, pour un **glissando continu** (pas de son « en escalier »). La table de pitch
  est extraite du contour réel de `elt.wav`.
- Pour la radiogoniométrie, HOMER se cale sur le **niveau reçu (RSSI)**, indépendant
  de la modulation : une vraie ELT 121,5 est en AM, ici l'émission est en **FM 2 m**,
  ce qui est **équivalent pour la gonio au Yagi** (le whoop sert au repérage à l'oreille).

---

**Jean-Louis — F1GBD / F4JHW** · ADRASEC 77 · FNRASEC. © 2026 F1GBD. **73**
