<div align="center">

<img src="doc/images/PDFteleporter_logo.png" alt="PDF Teleporter" width="180">

# PDF Teleporter

### Envoyer un document PDF par radio, et le retrouver intact à l'arrivée

*Pour les opérateurs ADRASEC / FNRASEC — TNC Packet, VARA HF/FM/SAT, Winlink Express*

[![Version](https://img.shields.io/badge/version-v2.0.0-blue)](https://github.com/f1gbd/F1GBD/releases/tag/pdfteleporter-v2.0.0)
[![Plateforme](https://img.shields.io/badge/Windows-10%20%2F%2011-lightgrey.svg)]()
[![Taille](https://img.shields.io/badge/installeur-34%20Mo-blueviolet.svg)]()
[![Licence](https://img.shields.io/badge/usage-ADRASEC%20%2F%20FNRASEC-green.svg)]()
[![Hors-ligne](https://img.shields.io/badge/100%25-hors--ligne-brightgreen.svg)]()

### 📥 Télécharger

**[⬇ Installeur Windows — PDFteleporter-2.0.0-setup.exe (34 Mo)](https://github.com/f1gbd/F1GBD/releases/download/pdfteleporter-v2.0.0/PDFteleporter-2.0.0-setup.exe)**

[Archive 7z portable (32 Mo)](https://github.com/f1gbd/F1GBD/releases/download/pdfteleporter-v2.0.0/PDFteleporter.7z) · [Version Linux](linux/) · [Toutes les versions](https://github.com/f1gbd/F1GBD/releases?q=pdfteleporter)

</div>

---

## À quoi ça sert

Un SITREP PDF de 48 Ko met **plus de 5 minutes** à passer en Packet 1200 baud. Compacté
par PDF Teleporter, il tient en **5 Ko** et passe en **38 secondes** — ou 19 secondes en
VARA HF. À l'arrivée, le destinataire clique une fois : il retrouve son PDF avec ses
tableaux, ses cases cochées et ses couleurs.

L'application fait deux choses, et rien d'autre :

| | |
|---|---|
| 📦 **Compacter** | Un PDF (SITREP, fiche réflexe, plan ORSEC, PSD, BSD, ordre d'opération) devient une archive `.psdi` de 5 à 25 % de sa taille. Texte, tableaux et images sont extraits puis compressés chacun avec l'algorithme qui lui convient. |
| 📬 **Recomposer** | Une archive `.psdi` reçue par radio redevient un PDF lisible, mise en forme d'origine restaurée. Aucune manipulation côté destinataire. |

Le `.psdi` se transmet par les modes radio de **TCQ** (TNC Packet, VARA HF/FM/SAT) ou en
pièce jointe **Winlink Express**. C'est la solution documentaire de l'ADRASEC quand le
réseau est isolé, dégradé ou inexistant.

---

## En images

<div align="center">

<img src="doc/images/PDFteleporter-working.png" alt="PDF Teleporter v2.0 en fonctionnement" width="960">

*Un SITREP ADRASEC de 49 161 octets compacté en 5 704 octets (11,6 %, 45 trames TNC),
puis recomposé à droite — cases à cocher et tableaux intacts.*

<img src="doc/images/winlink_dialog.png" alt="Préparation Winlink" width="700">

*Le bouton « Préparer pour Winlink » copie l'archive au bon endroit, vérifie la limite
de 120 Ko et affiche la procédure d'envoi pas à pas.*

</div>

---

## Installation

### Installeur Windows *(recommandé)*

1. Téléchargez **[PDFteleporter-2.0.0-setup.exe](https://github.com/f1gbd/F1GBD/releases/download/pdfteleporter-v2.0.0/PDFteleporter-2.0.0-setup.exe)**
2. Lancez-le et suivez l'assistant, en français. Il propose deux options utiles :
   le raccourci sur le Bureau, et **l'association des archives `.psdi`**.
3. Lancez l'application depuis le Menu Démarrer.

L'installation ne demande **pas de droits administrateur** si le poste est verrouillé.

> **Windows SmartScreen** peut afficher un avertissement au premier lancement :
> l'exécutable n'est pas signé par un certificat commercial. Cliquez sur
> *Informations complémentaires* → *Exécuter quand même*. Le SHA-256 est publié dans la
> release pour ceux qui veulent vérifier avant :
> `Get-FileHash -Algorithm SHA256 PDFteleporter-2.0.0-setup.exe`

### Archive portable

Pour une clé USB opérationnelle ou un poste sur lequel rien ne doit être installé :
téléchargez **[PDFteleporter.7z](https://github.com/f1gbd/F1GBD/releases/download/pdfteleporter-v2.0.0/PDFteleporter.7z)**,
décompressez-la où vous voulez, lancez `PDFteleporter\PDFteleporter.exe`. Aucun raccourci
ni association de fichier n'est créé dans ce mode.

### Mise à jour depuis une v1.0.x

Supprimez le dossier `C:\PDFteleporter\`, puis lancez l'installeur. Aucune configuration
n'est conservée ailleurs, et **toutes vos archives `.psdi` restent lisibles**.

### Vous utilisez déjà TCQ ?

PDF Teleporter est **intégré dans TCQ** : bouton **PDF** des modes **VARA Modem** et
**TNC Packet**. Rien à installer séparément. Les deux applications partagent le même
format d'archive et sont interopérables dans les deux sens.

### Configuration

| | Minimum | Recommandé |
|---|---|---|
| **OS** | Windows 10 (1909+) 64 bits | Windows 11 |
| **RAM** | 2 Go libres | 4 Go libres |
| **Disque** | 150 Mo | 250 Mo |
| **Écran** | 1024×768 | 1366×768 ou plus |

---

## 🆕 Nouveau en v2.0.0

> **Un vrai installeur, et huit fois plus léger.**
>
> 💿 **Programme d'installation Windows** — plus besoin de décompresser une archive dans
> `C:\`. Raccourcis, désinstalleur, assistant en français, installation possible sans
> droits administrateur.
>
> 📬 **Un `.psdi` reçu s'ouvre d'un double-clic** — l'archive arrive par VARA ou Winlink,
> vous double-cliquez, l'application s'ouvre avec le fichier chargé et son CRC déjà
> vérifié. Et un clic droit sur un PDF propose « Compacter avec PDF Teleporter ».
>
> 🪶 **882 Mo → 106 Mo installée, 261 Mo → 34 Mo à télécharger.** Le binaire de la v1.0.6
> embarquait tout l'environnement de développement de TCQ — bibliothèques de calcul
> scientifique, pile radio, générateurs de documents — dont l'application n'utilise rien.
> La v2.0 est compilée dans un environnement dédié réduit au strict nécessaire.
>
> 🖥 **Interface refondue (PyQt6)** — rendu net sur écrans haute résolution, barre de
> progression réelle, glisser-déposer d'un `.pdf` ou d'un `.psdi` sur la fenêtre.
>
> 🔄 **Le format `.psdi` ne change pas.** Les archives des versions v1.0.0 à v1.0.6 et
> celles de TCQ se recomposent telles quelles, et inversement. Aucune coordination de
> mise à jour n'est nécessaire au sein d'une section.

[Détail complet de la v2.0.0 →](CHANGELOG.md#v200)

---

## Fonctionnalités

| | | |
|:---:|---|---|
| ⚡ | **5 niveaux de qualité** | `Ultra Low` (~5 %, urgence Packet 1200), `Low` (~10 %), `Medium` (~20 %, VARA HF/FM), `High` (~25 %), `Sans image` (texte seul). Chacun est calibré pour un mode radio précis. |
| 🎨 | **2 modes d'extraction** | **Structuré** (texte + images repositionnées) ou **Rendu image** (pages aplaties en JPEG). Le mode image est choisi **automatiquement** pour les PDF scannés ou tournés. |
| ⏱ | **Estimation avant envoi** | Taille finale, nombre de trames TNC et temps d'envoi pour chaque mode radio — Packet 1200/9600, VARA HF/FM/SAT, ARDOP, LoRa. Plus de mauvaises surprises en exercice. |
| ✅ | **Validation CRC** | Signature, version et checksum sont vérifiés dès l'ouverture d'une archive. Un fichier corrompu en transfert est détecté avant toute tentative de recomposition. |
| 📧 | **Préparation Winlink** | Copie de l'archive dans `Documents\PDFteleporter\`, alerte au-delà de la limite de 120 Ko, procédure d'envoi affichée pas à pas. |
| 📐 | **Rendu fidèle** | Tableaux, couleurs de cellule, cases à cocher des formulaires AcroForm, accents des PDF LibreOffice, fontes ~4 pt d'Excel. Chaque cas a fait l'objet d'un correctif dédié. |
| 🖥 | **Interface PyQt6** | Thème sombre cohérent avec TCQ, rendu net en haute résolution, barre de progression, glisser-déposer, journal opérationnel horodaté. |
| 🔒 | **100 % local** | Aucune donnée ne quitte le poste, aucune connexion Internet, aucun compte. Adapté aux documents opérationnels sensibles et aux zones blanches. |

---

## Cas d'usage

**SITREP en exercice ou en mission** — l'opérateur de terrain compacte son SITREP en
qualité `Medium`, clique « Préparer pour Winlink », envoie la pièce jointe en VARA HF. La
cellule de coordination recompose en un clic.

**Diffusion de fiches réflexes** — le référent départemental compacte en `Low` et diffuse
sur le canal ADRASEC via TCQ-BBS. Toute la section reçoit et recompose localement.

**Urgence Packet 1200 sur batterie** — plan d'évacuation de 1,2 Mo, qualité `Ultra Low` :
~60 Ko, ~120 trames, sept minutes de transmission. Mise en forme préservée à l'arrivée.

---

## Le format `.psdi`

Archive binaire compacte et signée : signature `PSDI`, numéro de version (1 = structuré,
2 = rendu image), checksum CRC32, bloc texte compressé en LZMA, blocs images JPEG et
métadonnées de positionnement.

La signature détecte immédiatement un fichier corrompu ou étranger, et le CRC32 vérifie
l'intégrité après le transfert radio. Aucun format propriétaire, aucune dépendance
externe.

---

## Historique des versions

Le détail complet est dans le **[CHANGELOG](CHANGELOG.md)**.

| Version | Date | En bref | |
|---|---|---|:---:|
| **v2.0.0** | août 2026 | Installeur Windows, association `.psdi`, interface PyQt6, 882 → 106 Mo | [détails](CHANGELOG.md#v200) · [release](https://github.com/f1gbd/F1GBD/releases/tag/pdfteleporter-v2.0.0) |
| v1.0.7 | juin 2026 | Binaire Linux x86_64 | [détails](CHANGELOG.md#v107) · [linux/](linux/) |
| v1.0.6 | juin 2026 | Auto-bascule en rendu image pour les PDF scannés ou tournés | [détails](CHANGELOG.md#v106) |
| v1.0.5 | mai 2026 | Accents LibreOffice, cases à cocher AcroForm, fontes ~4 pt d'Excel | [détails](CHANGELOG.md#v105) |
| v1.0.4 | mai 2026 | Interligne des PDF à très petites fontes | [détails](CHANGELOG.md#v104) |
| v1.0.3 | mai 2026 | Ligatures Unicode, marge interne de rendu | [détails](CHANGELOG.md#v103) |
| v1.0.2 | mai 2026 | Débordement de texte dans les tableaux, familles de fontes | [détails](CHANGELOG.md#v102) |
| v1.0.1 | mai 2026 | Correctif « fond noir » Microsoft Print To PDF / Word LTSC | [détails](CHANGELOG.md#v101) |
| v1.0.0 | mars 2026 | Version initiale publique | [détails](CHANGELOG.md#v100) |

Toutes les archives `.psdi`, quelle que soit la version qui les a produites, restent
lisibles par toutes les autres — et par TCQ.

---

## Documentation

- 📘 **[Manuel utilisateur](doc/MEMO-PDFteleporter_MANUEL.pdf)** — guide pas-à-pas,
  niveaux de qualité, dépannage, intégration TCQ et Winlink
- 📋 **[Fiche de présentation](doc/PDFteleporter_FICHE_PRESENTATION.pdf)** — synthèse
  d'une page pour les briefings ADRASEC
- 🐧 **[Version Linux](linux/)** — binaire x86_64, même format d'archive
- 📄 **[SITREP de test](SITREP/)** — formulaires ADRASEC pour s'exercer

---

## Communauté

PDF Teleporter est un projet ouvert développé pour la communauté ADRASEC, proposé
librement aux ADRASEC départementales et à la FNRASEC. Il complète l'écosystème
**TCQ / IAbrain / SATER SIM** dans la chaîne d'outils de communications d'urgence.

Retours d'expérience, propositions et signalements sont bienvenus via les *Issues* du
dépôt.

---

<div align="center">

**Jean-Louis Naudin (F1GBD)**
*ADRASEC 77 — FNRASEC*

**Version 2.0.0 — Août 2026**

*Pour toute question, contactez votre référent ADRASEC départemental.*

📄 **PDF Teleporter** — *La téléportation radio des documents au service de la sécurité civile*

</div>
