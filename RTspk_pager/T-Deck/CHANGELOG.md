# Changelog — rsDeck T-Deck (édition RASEC-ALERT / F1GBD · ADRASEC 77)

Toutes les versions sont au format `x.y.z-rasec-f1gbd`, image fusionnée à flasher
à l'offset `0x0` (web-flasher ESP Web Tools).

## 3.0.0 — 2026-08-08

### Ajouté
- **Carte OSM** centrée sur la position GPS, ouverte depuis le bouton **CARTE** du
  dialogue GPS de l'accueil.
  - **Off-grid** : tuiles lues depuis la micro-SD (`/maps/osm/{z}/{x}/{y}.png`).
  - **Live (WiFi)** : téléchargement des tuiles manquantes depuis OpenStreetMap
    puis **mise en cache automatique sur la SD** pour réutilisation hors-réseau.
  - Marqueur de position GPS temps réel, HUD zoom + coordonnées.
  - Navigation **tactile** : glisser = pan, boutons `+` / `−` (zoom) et `O`
    (recentrer GPS). Clavier : `+`/`-`, flèches, `c`, Retour.
  - Décodeur **PNG** LVGL (lodepng) activé + cache image agrandi.
- **Bouton GPS** sur l'écran d'accueil → **dialogue d'état GPS** (statut,
  coordonnées Lat/Lon, satellites, HDOP, altitude) ; bouton **CARTE** actif au fix.
- **Filtre TCQ** dans l'écran « Peers » : n'afficher que les annonces dont le nom
  commence par `TCQ`.

### Corrigé / robustesse
- Parsing de la **position GPS activé en permanence** au démarrage du GPS (la
  localisation survit désormais au redémarrage).
- Formatage des coordonnées via `snprintf` (le `printf` interne de LVGL ne gère
  pas `%f`).
- Alignement des tuiles calé sur une **origine entière unique** (plus de couture).
- **Purge du cache image** LVGL avant libération d'un descripteur (fin des tuiles
  fantômes / recopies au pan/zoom).
- **Garde anti-boucle** sur les téléchargements de tuiles ratés (une seule
  tentative par tuile, throttle) — évite le blocage de l'UI.

## 2.0.4 — 2026-08

### Ajouté
- **Décodeur CHAPPE26** intégré : auto-décodage des messages LXMF contenant des
  codes `!DDDD` (répertoire complet 1000 codes) + écran de test dans Settings.
- **Rétro-éclairage clavier** temporisé (5 s à la frappe).
- Deux presets **LoRa France** (Standard 868 et Haut Débit 868).
- Bandeau d'accueil « Ratspeak - Adrasec » + version.

## 2.0.3

### Ajouté / amélioré
- **MAIL ADRAlink** : champ identifiant **modifiable** (relire un ancien message),
  **journal effaçable**, retour visuel clair à l'envoi et à la réception.

## Antérieur

- Option **Pager RASEC-ALERT** portée depuis le MeshPager : message LXMF `#ra`
  → écran plein écran clignotant + sirène I2S synthétisée + accusé de réception ;
  `#rapass` (changement de code), `#b` (répétitions sirène).
- Base : firmware **rsDeck** (Reticulum / microReticulum / LXMF) pour LilyGo
  T-Deck Plus.
