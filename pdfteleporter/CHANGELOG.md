# Historique des versions — PDF Teleporter

Toutes les archives `.psdi`, quelle que soit la version qui les a produites, restent
lisibles par toutes les autres versions **et par TCQ**. Le format n'a jamais changé depuis
la v1.0.0.

[← Retour au README](README.md)

| Version | Date | En bref |
|---|---|---|
| [v2.0.0](#v200) | août 2026 | Installeur Windows, association `.psdi`, interface PyQt6, 882 → 106 Mo |
| [v1.0.7](#v107) | juin 2026 | Binaire Linux x86_64 |
| [v1.0.6](#v106) | juin 2026 | Auto-bascule en rendu image pour les PDF scannés ou tournés |
| [v1.0.5](#v105) | mai 2026 | Accents LibreOffice, débordement des fontes ~4 pt d'Excel |
| [v1.0.4](#v104) | mai 2026 | Interligne des PDF à très petites fontes |
| [v1.0.3](#v103) | mai 2026 | Ligatures Unicode, marge interne de rendu |
| [v1.0.2](#v102) | mai 2026 | Débordement de texte dans les tableaux, familles de fontes |
| [v1.0.1](#v101) | mai 2026 | Correctif « fond noir » Microsoft Print To PDF / Word LTSC |
| [v1.0.0](#v100) | mars 2026 | Version initiale publique |

---

<a id="v200"></a>

## v2.0.0 — Août 2026

Version majeure. Le **moteur de compression ne change pas** : c'est celui de la v1.0.6,
à l'identique. Tout ce qui change est autour — l'installation, le poids et l'interface.

### 💿 Programme d'installation Windows

`PDFteleporter-2.0.0-setup.exe` (Inno Setup 6), 33,9 Mo :

- installation **avec ou sans droits administrateur**, au choix ;
- raccourcis Menu Démarrer et Bureau (optionnel) ;
- **association du type `.psdi`** — un double-clic sur une archive reçue ouvre
  PDF Teleporter avec le fichier chargé et son CRC déjà vérifié ;
- entrée **« Compacter avec PDF Teleporter »** dans le menu contextuel des PDF ;
- désinstalleur propre, clés de registre comprises ;
- assistant en français (anglais disponible) ;
- SHA-256 publié à côté de l'installeur.

L'archive 7z portable reste disponible pour les postes sur lesquels rien ne doit être
installé.

### 🪶 882 Mo → 106,5 Mo

|  | v1.0.6 | v2.0.0 | |
|---|---:|---:|---|
| Dossier installé | 882 Mo | **106,5 Mo** | ÷ 8,3 |
| Téléchargement (installeur) | 261 Mo | **33,9 Mo** | ÷ 7,7 |
| Téléchargement (archive 7z) | 261 Mo | **31,9 Mo** | ÷ 8,2 |

La v1.0.6 était compilée par PyInstaller **depuis l'environnement Python de développement
de TCQ**. Or PyInstaller embarque ce qu'il trouve dans l'environnement d'où on le lance :
il y prenait `numpy`, `scipy`, `matplotlib`, `pandas`, la pile Reticulum, `pyserial`,
`sounddevice`, `reportlab`, `lxml`, ainsi que `tcl/tk` pour Tkinter — dont l'application
n'utilise **aucun**.

Trois mesures dans la v2.0 :

| | |
|---|---|
| **Environnement de compilation dédié** | quatre paquets seulement : PyQt6, PyMuPDF, Pillow, PyInstaller |
| **Liste d'exclusions explicite** | ~50 modules Qt6 inutilisés et toute la pile scientifique et radio, en garde-fou |
| **Purge après compilation** | traductions Qt, DLL Qt6 non utilisées, `opengl32sw.dll`, `d3dcompiler_47.dll`, plugins superflus |

Ce n'est pas le code qui a maigri, c'est l'emballage. Le poids restant est
essentiellement `libmupdf` — le moteur PDF — et les trois DLL Qt6 réellement utilisées.

### 🖥 Interface réécrite en PyQt6

L'ergonomie ne bouge pas : deux panneaux, cinq niveaux de qualité, deux modes
d'extraction, bouton Winlink. Un opérateur formé sur la v1 n'a rien à réapprendre.
S'ajoutent :

- **rendu net en haute résolution** — fini le flou sur les portables récents et les
  postes à mise à l'échelle Windows ;
- **barre de progression réelle** pendant la compression et la recomposition ;
- **glisser-déposer** d'un `.pdf` ou d'un `.psdi` sur la fenêtre ;
- **ouverture par ligne de commande** (`PDFteleporter.exe fichier.psdi`), ce qui permet
  le double-clic sur une archive ;
- estimations différées : changer trois fois de qualité ne lance plus trois compressions
  complètes ;
- journal opérationnel coloré, fenêtre « À propos » indiquant les versions de
  l'interface, du moteur et du format d'archive.

### ⚙️ Moteur PSDI autonome

L'application utilise désormais sa propre copie du moteur (`psdi_lib.py`) au lieu du
`pdf_trans.py` de TCQ. **Aucune ligne d'algorithme n'a été modifiée** — mêmes signature
`PSDI`, versions d'archive, préréglages de qualité et auto-bascule pour les documents
scannés ou tournés.

**Compatibilité ascendante et descendante totale** : les `.psdi` produits par les
versions v1.0.0 à v1.0.6 et par TCQ se recomposent en v2.0, et ceux produits par la v2.0
se recomposent avec les versions antérieures et avec TCQ. Aucune coordination de mise à
jour n'est nécessaire au sein d'une section.

### 🐧 Linux

Inchangé : le binaire v1.0.7 reste valide, le moteur de compression étant identique.

---

<a id="v107"></a>

## v1.0.7 — Juin 2026 *(Linux)*

- 🐧 Binaire Linux x86_64 autonome, même format d'archive et mêmes correctifs que la
  v1.0.6 Windows. Voir **[linux/](linux/)**.

---

<a id="v106"></a>

## v1.0.6 — Juin 2026

- 🔄 **Auto-bascule en mode Rendu image pour les PDF scannés et tournés.** Les documents
  portant une rotation de page (`/Rotate != 0`) ou essentiellement scannés (texte
  extractible négligeable, forte couverture image) étaient recomposés **basculés de 90°
  sur fond noir** en mode Structuré. Deux causes cumulées : la rotation de page n'était
  pas propagée à la recomposition, et les images-masques — la couche d'encre quasi noire
  des scans, appliquée en transparence — étaient repeintes en opaque. La compression
  détecte désormais ces documents via `_detect_optimal_mode()` et route automatiquement
  vers le mode image, qui repose sur `get_pixmap()` : rotation respectée, masques
  composés correctement. Cas typique : l'arrêté préfectoral scanné puis transmis par
  radio.
- 🎯 **Détection ciblée, sans faux positifs** : seuls les documents tournés (raison
  `rotation`) ou scannés (raison `scan`) basculent. Les vrais PDF texte natifs non
  tournés conservent le mode Structuré, plus compact. Le mode `Sans image` et le mode
  image explicite ne sont jamais modifiés. La raison de la bascule est journalisée.
- 🔄 Compatibilité ascendante totale.

---

<a id="v105"></a>

## v1.0.5 — Mai 2026

- 🌍 **Correctif des caractères accentués LibreOffice.** Les mots contenant les ligatures
  `ti` ou `tt` — Situation, quitté, Éducation, nationale, routier, lutte, pollution —
  apparaissaient avec un caractère de remplacement `�` après recomposition. LibreOffice
  utilise des glyphes Unicode non standard (Ɵ U+019F, Ʃ U+01A9) dans ses CIDFonts, que
  PyMuPDF convertit en `U+FFFD`. La v1.0.5 décompose ces ligatures, ainsi que les
  ligatures classiques ﬀ ﬁ ﬂ ﬃ ﬄ ﬅ ﬆ, et restaure les mots français par une heuristique
  contextuelle.
- 🗹 **Correctif des cases à cocher perdues** sur les PDF formulaires (AcroForm). Les
  champs texte remplis survivaient déjà, mais la coche des cases et des boutons radio vit
  dans l'apparence `/AP /N` du widget, que ni `get_text` ni `get_drawings` n'extraient :
  elle disparaissait du PDF recomposé. Typique des SITREP ADRASEC remplis. La position
  des cases cochées est désormais relevée et une coche vectorielle y est redessinée.
- 📐 **Correctif du débordement Excel à très petites fontes** (~4 pt) : compensation de la
  marge interne du moteur HTML de PyMuPDF et auto-réduction modérée de la police plutôt
  que troncature.
- 🔄 Compatibilité ascendante totale — les archives antérieures bénéficient même
  automatiquement des correctifs côté recomposition.

---

<a id="v104"></a>

## v1.0.4 — Mai 2026

- 📏 **Correctif de l'interligne sur les PDF à fontes très petites.** La v1.0.3 utilisait
  un minimum absolu de 12 pt pour la hauteur du rectangle de rendu, ce qui faisait
  chevaucher les lignes successives des PDF Excel à fontes ~4 pt, dont l'espacement réel
  entre lignes de base est de ~5,7 pt. La hauteur est désormais proportionnelle à la
  taille réelle des polices de chaque ligne. Élimine l'empilement vertical des
  paragraphes dans les cadres « Commentaires » des SITREP produits sous Excel.
- 🔄 Compatibilité ascendante totale.

---

<a id="v103"></a>

## v1.0.3 — Mai 2026

- 🔤 **Décomposition des ligatures Unicode** (ﬀ ﬁ ﬂ ﬃ ﬄ ﬅ ﬆ) et heuristique de
  restauration des caractères `U+FFFD` produits par LibreOffice à la place des ligatures
  `ti` et `tt`.
- 📐 **Compensation de la marge interne du rendu HTML** pour éviter le débordement de
  texte sur les PDF Excel à fontes très petites, dont les bounding boxes sont optimisées
  au pixel près.
- 🔄 Compatibilité ascendante totale.

---

<a id="v102"></a>

## v1.0.2 — Mai 2026

- 📐 **Correctif du débordement de texte** dans la recomposition structurée. Les libellés
  des cellules de tableaux — Bilan humain, Moyens engagés, Activité de sécurité — ne
  sortent plus de leurs cellules colorées : le bounding box d'origine des lignes de texte
  est désormais strictement respecté au lieu d'être étiré jusqu'au bord de la page.
- 🔤 **Conservation de la famille de fonte d'origine** (sans-serif / serif / monospace)
  dans l'archive, pour un rendu plus fidèle. Surcoût négligeable, ~10 octets par span.
- 🔄 Compatibilité ascendante totale.

---

<a id="v101"></a>

## v1.0.1 — Mai 2026

- 🛡 **Correctif « fond noir »** sur la recomposition des PDF produits par Microsoft Print
  To PDF et Microsoft Word LTSC — soit une bonne part des documents des préfectures et
  des formulaires SIDPC/COD. L'extraction itère désormais sur les sous-items individuels
  des paths vectoriels au lieu d'utiliser leur bounding box global, ce qui produisait de
  gros rectangles noirs pleine page.
- 🛡 Garde-fou supplémentaire : tout rectangle quasi pleine page de luminance < 0,3 est
  ignoré. Un fond de page opérationnel ADRASEC n'est jamais noir plein.
- 📡 Correctif également propagé dans **TCQ v10.12.0**.
- 🐧 Linux : correctif d'ouverture du PDF recomposé via `xdg-open` (environnement
  `LD_LIBRARY_PATH` propre, nécessaire pour les binaires PyInstaller).
- 🔄 Compatibilité ascendante totale.

---

<a id="v100"></a>

## v1.0.0 — Mars 2026

- 🎉 Version initiale publique de PDF Teleporter.
- 5 niveaux de qualité, 2 modes d'extraction (Structuré / Rendu image), validation CRC,
  intégration Winlink Express et TCQ.

---

[← Retour au README](README.md)
