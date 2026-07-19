# Ratspeak (RASEC-ALERT) — produire un APK Android prêt à installer (Windows)

Objectif : obtenir `app-universal-release.apk` **signé**, installable sur un
téléphone / T-Deck Android. Le patch RASEC-ALERT doit déjà être appliqué (voir
`RASEC-ALERT.md`).

> Un APK de *release non signé* ne s'installe pas. Deux voies possibles :
> **A. Release signé** (distribuable, recommandé) — étapes 4→7 ci-dessous.
> **B. Debug auto-signé** (test rapide) — voir le raccourci en fin de document.

---

## 1. Prérequis (à installer une seule fois)

1. **Rust** via https://rustup.rs + « Desktop development with C++ » (MSVC Build
   Tools, proposé par l'installeur Visual Studio).
2. **Tauri CLI 2** :
   ```powershell
   cargo install tauri-cli --version "^2.0"
   ```
3. **JDK 17** (Temurin/Adoptium : https://adoptium.net).
4. **Android Studio** (https://developer.android.com/studio) puis, via
   *More Actions → SDK Manager* :
   - onglet *SDK Platforms* : **Android 14 (API 34)** et **Android (API 36)**,
   - onglet *SDK Tools* : cocher **NDK (Side by side)**, **Android SDK
     Command-line Tools**, **Android SDK Build-Tools**, **Android SDK Platform-Tools**
     (fournit `adb`).
5. **Git for Windows** (fournit **Git Bash**, nécessaire pour `build-css.sh`).

### Variables d'environnement

Dans PowerShell (adapter les chemins et la version de NDK réellement installée,
p. ex. `27.1.12297006`) :
```powershell
setx JAVA_HOME "C:\Program Files\Eclipse Adoptium\jdk-17.0.12+7"
setx ANDROID_HOME "$env:LOCALAPPDATA\Android\Sdk"
setx NDK_HOME "$env:LOCALAPPDATA\Android\Sdk\ndk\27.1.12297006"
```
**Fermer puis rouvrir le terminal** après `setx`. Vérifier :
```powershell
java -version
cargo tauri --version
dir $env:ANDROID_HOME\ndk
```

### Cibles Rust Android
```powershell
rustup target add aarch64-linux-android armv7-linux-androideabi i686-linux-android x86_64-linux-android
```

---

## 2. Disposition des dépôts (checkouts frères)

Ratspeak référence ses bibliothèques par chemins relatifs `../...`. Il faut donc
les dépôts frères **à côté** de Ratspeak :

```powershell
mkdir C:\QITdevsrc\ratspeak-src
cd C:\QITdevsrc\ratspeak-src
git clone https://github.com/ratspeak/rsReticulum
git clone https://github.com/ratspeak/rsLXMF
git clone https://github.com/ratspeak/lrgp-rs
git clone https://github.com/ratspeak/rsLXST
```

Puis placer **ta copie patchée** de Ratspeak dans le même dossier, sous le nom
`Ratspeak` :
```
C:\QITdevsrc\ratspeak-src\
    rsReticulum\
    rsLXMF\
    rsLXST\
    lrgp-rs\
    Ratspeak\          <-  sources patchées RASEC-ALERT
```

> Le plus simple : renommer/copier `C:\QITdevsrc\Ratspeak-Adrasec` (déjà patché)
> en `C:\QITdevsrc\ratspeak-src\Ratspeak`. Les noms des dépôts frères doivent
> être **exactement** ceux ci-dessus.

---

## 3. Construire le CSS du frontend

Dans **Git Bash** (pas PowerShell) :
```bash
cd /c/QITdevsrc/ratspeak-src/Ratspeak
bash dashboard/build-css.sh
```
Génère `dashboard/static/style.css`. (Étape standard Ratspeak. L'overlay RASEC
injecte son propre style, mais le reste de l'UI a besoin de ce fichier.)

---

## 4. Créer la clé de signature (une seule fois)

Depuis PowerShell, dans le dossier du projet Android :
```powershell
cd C:\QITdevsrc\ratspeak-src\Ratspeak\src-tauri\gen\android
& "$env:JAVA_HOME\bin\keytool.exe" -genkeypair -v `
    -keystore ratspeak-release.keystore `
    -alias ratspeak -keyalg RSA -keysize 2048 -validity 10000
```
Répondre aux questions (mot de passe + identité). **Conserver précieusement ce
fichier et le mot de passe** : toute mise à jour de l'app devra être signée avec
la même clé.

---

## 5. Déclarer la clé pour Gradle

Créer le fichier **`C:\QITdevsrc\ratspeak-src\Ratspeak\src-tauri\gen\android\keystore.properties`**
avec ce contenu (remplacer les mots de passe) :
```properties
storeFile=ratspeak-release.keystore
storePassword=TON_MOT_DE_PASSE_STORE
keyAlias=ratspeak
keyPassword=TON_MOT_DE_PASSE_CLE
```
`storeFile` est relatif à `gen/android/`. Dès que ce fichier existe et contient
`storeFile`, le build de release est **signé automatiquement**.

---

## 6. Construire l'APK de release signé

```powershell
cd C:\QITdevsrc\ratspeak-src\Ratspeak\src-tauri
cargo tauri android build --apk
```

Variantes utiles :
- **Sans la voix expérimentale** (évite d'avoir à compiler `rsLXST`) :
  ```powershell
  cargo tauri android build --apk --no-default-features
  ```
- **Une seule architecture** (build plus rapide, téléphones ARM64 modernes) :
  ```powershell
  cargo tauri android build --apk --target aarch64
  ```

> Si la toute première commande dit que le projet Android n'est pas initialisé,
> lancer une fois `cargo tauri android init` puis relancer le build. Le dépôt
> fournit déjà `gen/android`, donc en principe ce n'est pas nécessaire.

---

## 7. Récupérer et installer l'APK

L'APK signé se trouve sous (Tauri affiche aussi le chemin exact en fin de
build) :
```
src-tauri\gen\android\app\build\outputs\apk\universal\release\app-universal-release.apk
```
(en mode `--target aarch64` : sous-dossier de l'architecture correspondante).

Installer sur un appareil branché en USB (débogage USB activé) :
```powershell
adb install -r "C:\QITdevsrc\ratspeak-src\Ratspeak\src-tauri\gen\android\app\build\outputs\apk\universal\release\app-universal-release.apk"
```
Ou copier l'`.apk` sur le téléphone et l'ouvrir (autoriser « sources inconnues »).

---

## Raccourci B — APK debug (test rapide, sans keystore)

Pour un simple essai terrain, sans créer de clé (APK auto-signé debug,
directement installable) :
```powershell
cd C:\QITdevsrc\ratspeak-src\Ratspeak\src-tauri
cargo tauri android build --apk --debug
adb install -r ..\src-tauri\gen\android\app\build\outputs\apk\universal\debug\app-universal-debug.apk
```

---

## Dépannage

- **`Failed to find NDK` / erreur de linker Android** : `NDK_HOME` mal défini →
  vérifier `dir $env:ANDROID_HOME\ndk` et pointer sur la version installée.
- **`SDK location not found`** : créer
  `src-tauri\gen\android\local.properties` contenant
  `sdk.dir=C\:\\Users\\<toi>\\AppData\\Local\\Android\\Sdk`
  (double antislash, échapper le `:`).
- **Erreur de chemin sur les dépôts frères** (`path ../rsReticulum not found`) :
  la disposition de l'étape 2 n'est pas respectée (noms/emplacements exacts).
- **Build très long la première fois** : normal (compilation Rust de toute la
  pile Reticulum pour 4 architectures). `--target aarch64` accélère nettement.
- **APK non signé refusé à l'installation** : `keystore.properties` absent ou
  sans `storeFile` → le release n'est pas signé. Refaire l'étape 5.

---

Crédits portage RASEC-ALERT : **F1GBD — ADRASEC 77**.
