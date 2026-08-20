# AERO-SPECTRIX — Composants tiers

AERO-SPECTRIX embarque des bibliothèques développées par des tiers. Elles
restent la propriété de leurs auteurs et sont régies par leurs propres
licences, qui **prévalent sur la licence d'AERO-SPECTRIX** pour ce qui les
concerne.

Le fichier `THIRD-PARTY-NOTICES.txt` livré dans l'archive contient le **texte
intégral** de chacune de ces licences, extrait des paquets réellement
embarqués au moment de la compilation.

---

## Qt et PySide6 — GNU LGPL version 3

> **AERO-SPECTRIX utilise la bibliothèque Qt, au travers de PySide6 (Qt for
> Python), sous licence GNU Lesser General Public License version 3.**
>
> Qt est un produit de The Qt Company Ltd et de ses contributeurs.
> AERO-SPECTRIX n'est ni édité, ni approuvé, ni soutenu par The Qt Company.

C'est le composant qui commande la forme de la distribution, et il mérite
d'être compris plutôt que subi.

### Ce que la LGPL v3 exige, et comment c'est satisfait ici

| Obligation | Comment elle est remplie |
|---|---|
| Signaler de façon visible l'usage d'une bibliothèque LGPL | Le présent fichier, la boîte *À propos* de l'application et la page de publication |
| Fournir le texte de la licence | LGPL v3 et GPL v3 reproduites dans `THIRD-PARTY-NOTICES.txt` |
| Permettre le remplacement de la bibliothèque | **L'application est distribuée en mode dossier** : les DLL de Qt sont des fichiers distincts, dans `_internal\`, remplaçables par une version modifiée |
| Fournir le code source correspondant | Publié par The Qt Company aux adresses ci-dessous, et fourni par l'Auteur sur simple demande |

Le mode **dossier** n'est pas un détail d'emballage. Un exécutable en fichier
unique scelle les DLL de Qt à l'intérieur du binaire : elles ne sont alors plus
remplaçables, et l'obligation de relink de la LGPL n'est plus satisfaite. C'est
la raison pour laquelle l'archive contient un dossier et non un seul `.exe`.

### Obtenir le code source de Qt et de PySide6

- Qt : <https://download.qt.io/archive/qt/>
- PySide6 (Qt for Python) : <https://download.qt.io/official_releases/QtForPython/>
- Dépôt PySide6 : <https://code.qt.io/cgit/pyside/pyside-setup.git/>

La version exacte embarquée est indiquée dans `THIRD-PARTY-NOTICES.txt`.

### Modules Qt effectivement utilisés

QtCore, QtGui, QtWidgets, QtMultimedia et QtNetwork. Les modules WebEngine,
Quick/QML, 3D, Charts, DataVisualization, SQL et autres extensions sont
explicitement exclus de la compilation.

---

## Les autres composants

Tous sont sous licence permissive de type BSD, MIT ou équivalente : elles
n'imposent que la conservation de la notice de copyright et du texte de la
licence, reproduits dans `THIRD-PARTY-NOTICES.txt`.

| Composant | Rôle dans AERO-SPECTRIX | Licence |
|---|---|---|
| **Python** | interpréteur embarqué | PSF License |
| **NumPy** | calcul numérique, FFT | BSD 3-Clause |
| **SciPy** | filtrage, traitement du signal | BSD 3-Clause |
| **Matplotlib** | scope, spectrogramme, figures | Matplotlib License (type PSF) |
| **Pillow** | repli GIF de l'enregistrement vidéo | MIT-CMU (HPND) |
| **sounddevice** | accès aux cartes son, mode Direct | MIT |
| **PortAudio** | couche audio native, variantes ASIO et non-ASIO | MIT |
| **pySerial** | liaison série avec la tête d'acquisition Teensy | BSD 3-Clause |
| **Tcl/Tk** | écran de démarrage natif | BSD-like (Tcl/Tk License) |
| **PyInstaller** | amorceur de l'exécutable | GPL v2 **avec exception** autorisant explicitement l'usage dans un logiciel propriétaire |

### Note sur ASIO

Les pilotes ASIO sont une technologie de Steinberg Media Technologies GmbH.
AERO-SPECTRIX ne redistribue pas le SDK ASIO : il utilise la bibliothèque
PortAudio compilée avec le support ASIO, livrée par le paquet `sounddevice`.
ASIO est une marque déposée de Steinberg Media Technologies GmbH.

---

## Régénérer ce fichier

Le texte intégral des licences est extrait des paquets installés, jamais
recopié à la main — une notice recopiée devient fausse dès la mise à jour d'une
dépendance :

```
.venv\Scripts\python.exe tools\collect_licences.py
```

Le fichier `THIRD-PARTY-NOTICES.txt` est écrit à la racine du projet, puis
copié dans le dossier de distribution. À relancer **avant chaque publication**.

---

*AERO-SPECTRIX par F1GBD — ADRASEC 77 / FNRASEC*
