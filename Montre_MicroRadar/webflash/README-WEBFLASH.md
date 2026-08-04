# Publier le flashage web sur https://github.com/f1gbd/F1GBD

Page cible une fois publiée :

**https://f1gbd.github.io/F1GBD/Montre_MicroRadar/webflash/**

---

## 1. D'où vient le `.bin` ?

Un firmware ESP32 est normalement écrit en **quatre morceaux** à des adresses
différentes. ESP Web Tools sait le faire, mais il est bien plus simple de
publier **un seul fichier flashable à l'offset 0x0** :

| Offset | Contenu |
|---|---|
| `0x0` | `bootloader.bin` (bootloader de 2e étage) |
| `0x8000` | `partitions.bin` (table de partitions) |
| `0xe000` | `boot_app0.bin` (sélecteur OTA) |
| `0x10000` | `firmware.bin` (l'application) |

Le script `tools/merge_bin.py` fait la fusion **automatiquement après chaque
compilation** (activé par `extra_scripts = post:tools/merge_bin.py` dans
`platformio.ini`) :

```powershell
pio run -e esp32-s3-amoled-206 -e esp32-c6-amoled-206
```

produit :

```
.pio\build\esp32-s3-amoled-206\esp32-s3-amoled-206-merged.bin   (~1,5 Mo)
.pio\build\esp32-c6-amoled-206\esp32-c6-amoled-206-merged.bin   (~1,6 Mo)
```

À copier dans `webflash\` sous les noms attendus par le manifeste :

```powershell
copy .pio\build\esp32-s3-amoled-206\esp32-s3-amoled-206-merged.bin webflash\micro-radar-s3.bin
copy .pio\build\esp32-c6-amoled-206\esp32-c6-amoled-206-merged.bin webflash\micro-radar-c6.bin
```

L'équivalent à la main, si besoin :

```bash
esptool --chip esp32s3 merge-bin -o merged.bin \
  --flash-mode dio --flash-freq 80m --flash-size 16MB \
  0x0     bootloader.bin \
  0x8000  partitions.bin \
  0xe000  boot_app0.bin \
  0x10000 firmware.bin
```

## 2. Ce qu'il faut mettre dans le dépôt

```
F1GBD/
├── .nojekyll                        <- a la RACINE du depot (important)
└── Montre_MicroRadar/
    ├── platformio.ini
    ├── src/  include/  tools/
    └── webflash/
        ├── index.html               <- page de flashage
        ├── manifest.json            <- declare les 2 cartes
        ├── micro-radar-s3.bin
        └── micro-radar-c6.bin
```

Le `.nojekyll` à la racine désactive le moteur Jekyll : sans lui, GitHub Pages
ignore les fichiers et dossiers commençant par `_` et peut se mêler du contenu.

Le `manifest.json` déclare **les deux cartes dans un seul fichier** :
ESP Web Tools interroge la puce connectée et sert automatiquement le bon
binaire. Un seul bouton pour les deux cartes.

## 3. Activer GitHub Pages

Dans **Settings → Pages** du dépôt `F1GBD` :

* **Source :** `Deploy from a branch`
* **Branch :** `master` — **Folder :** `/ (root)`

C'est volontairement le mode « branche » et non « GitHub Actions » : avec
Actions, l'artefact publié **remplace tout le site**, ce qui interdirait
d'héberger un jour un autre projet de ce dépôt. En mode branche, chaque projet
vit dans son sous-dossier et garde son URL.

Compter 1 à 2 minutes après le premier push pour que la page soit servie.

## 4. Contraintes à connaître

* **HTTPS obligatoire.** L'API Web Serial n'existe qu'en contexte sécurisé.
  GitHub Pages est en HTTPS, donc c'est réglé — mais un test en `file://`
  échouera.
* **Chrome ou Edge sur ordinateur uniquement.** Firefox et Safari
  n'implémentent pas Web Serial, aucun navigateur mobile non plus. La page
  affiche un message explicite dans ces cas.
* **Pas de CORS à gérer** tant que les `.bin` sont servis depuis la même
  origine que le `manifest.json` — c'est le cas ici, même dossier.
* **`new_install_prompt_erase: true`** propose d'effacer toute la flash à la
  première installation : cela supprime les identifiants Wi-Fi et la
  configuration NVS d'un firmware précédent (les cartes sont livrées avec un
  firmware « XiaoZhi » d'usine).
* **Poids dans git :** ~3 Mo par mise à jour des deux binaires. Sur quelques
  versions ce n'est rien ; si tu publies souvent, préfère joindre les `.bin` à
  une *release* GitHub et pointer le `manifest.json` vers ces URL.

## 5. Tester avant de pousser

```powershell
python -m http.server 8000 --directory webflash
```

Puis ouvrir `http://localhost:8000/` dans Chrome — `localhost` est considéré
comme un contexte sécurisé, donc Web Serial fonctionne malgré le `http://`.

## 6. Automatiser plus tard (optionnel)

`.github/workflows/firmware.yml` compile les deux cartes à chaque push sur
`master`. Tel qu'il est fourni il publie via GitHub Actions ; si tu restes en
mode « branche » (recommandé ci-dessus), remplace l'étape de publication par un
simple commit des `.bin` dans `Montre_MicroRadar/webflash/`. Tant que tu
publies à la main, ce fichier peut rester de côté.
