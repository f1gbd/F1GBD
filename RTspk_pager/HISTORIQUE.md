# RTspk Pager — historique des versions

> Le détail de chaque version, de la plus récente à la plus ancienne.
> Pour découvrir l'application, commencez par le **[README](README.md)** ; pour
> le mode d'emploi de chaque fonction, voyez le **[guide détaillé](GUIDE.md)**.
>
> [⬅ README](README.md) · [📖 Guide détaillé](GUIDE.md) · [📜 Releases](https://github.com/f1gbd/F1GBD/releases)

---

## Versions

**1.0.60 — Couverture LoRa prévisionnelle et placement de relais RRLoRa.**
Un bouton **🗼 pylône** cherche **où poser un répéteur [RRLoRa](https://github.com/f1gbd/F1GBD/tree/master/RRLora)** pour relier deux
stations qui ne s'entendent pas : profil réel de la liaison directe, grille d'altitudes
sur le corridor, six meilleurs sites recalculés sur profils réels, et une **chaîne de deux
relais** quand un seul ne suffit pas. RRLoRa étant un **nœud Transport Reticulum**, la liaison
compte **deux bonds indépendants** : c'est le **maillon faible** qui est affiché. La position de
la station se choisit désormais entre **GPS et curseur**, et un appui sur l'encart de bilan
ouvre les réglages.

**1.0.60 — Couverture LoRa prévisionnelle.** Un bouton **📡 antenne**, sous les
réglages météo, trace la **portée radio de la station** en quatre couleurs sur la
**fréquence réellement configurée dans le RNode** (867,500 MHz par défaut), et
affiche le **bilan de liaison au point visé** : distance, azimut, affaiblissement,
puissance reçue, sensibilité, marge et dégagement de la zone de Fresnel. Le calcul
tient compte du **relief réel** (altitudes Open-Meteo, sans clé), de la **courbure
terrestre** et de la **diffraction sur arête** — une crête dégrade la liaison
progressivement au lieu de la couper net. À lire comme une prévision, jamais
comme une garantie : sur le terrain, seul un essai radio fait foi.

**1.0.53 — Tracé de zone utilisable sur téléphone.** La barre d'outils du tracé
tombait sous la **barre de navigation d'Android** : « ✓ Terminer » était
inatteignable. Elle remonte désormais au-dessus, la légende s'efface pendant le
tracé, et les messages de la carte passent devant les panneaux au lieu de rester
cachés dessous. Le bouton **Supprimer** des zones reste inactif tant qu'aucune
zone n'est sélectionnée, avec la consigne affichée — il ne semble plus « ne rien
faire ». Corrige aussi l'**envoi LXMF des zones**, qui ne partait pas : il
réclamait un lien LXMF établi, impossible sur liaison radio, et annonçait un
succès même quand rien n'était parti.

**1.0.52 — Réglages météo enfin accessibles.** L'appui long sur le bouton 🌦
n'ouvrait presque jamais les réglages : le panneau s'ouvrait bien, puis se
refermait aussitôt le doigt levé. Les zones à surveiller, qui ne s'atteignent
que par ce panneau, étaient de fait inaccessibles. Corrigé, et doublé d'un
**bouton ⚙ dédié** sous le bouton météo — un simple appui suffit désormais.

**1.0.51 — Correctif : pression du bulletin météo.** Le bulletin station
annonçait « Pression 0 hPa » : AROME France HD ne publie pas la pression au
niveau de la mer, et la valeur absente était affichée comme un zéro. La ligne
donne désormais la **pression au sol** quand la pression mer manque, et
disparaît si le modèle ne donne ni l'une ni l'autre. Même cause corrigée
ailleurs : une direction de vent absente dessinait une flèche **plein nord** au
lieu d'un simple cercle.

**1.0.50 — Couche météo AROME, règle des 3×30 et zones à surveiller.** Un bouton
🌦 **sous le bouton radar** allume une couche météo alimentée par le modèle
**AROME de Météo-France** via **Open-Meteo — gratuit et sans clé**. La carte se
couvre d'un **champ de vent** (une flèche par maille, pointe vers où souffle le
vent, couleur selon la vitesse), des **zones « règle des 3×30 »** (jaune =
2 critères sur 3, rouge = les 3 réunis, danger feux de forêt extrême), et d'un
**bulletin station** au point GPS de l'opérateur. On peut en plus **tracer des
zones à surveiller** au doigt : dès que les seuils y sont atteints, la zone
passe au rouge clignotant, un **bandeau d'alerte** barre le haut de la carte et
une **sirène montante** retentit. Les zones **s'échangent par LXMF** avec TCQ,
dans les deux sens. Réglages par appui long, aux **valeurs par défaut de TCQ** :
grille 6 × 5, flèches ×1,5, seuils 30 °C / 30 km/h / 30 %, rafraîchissement
15 min. Détails dans la section **Couche météo** plus bas.
✅ Interopérable **TCQ v12.68** — zones échangées et affichées dans les deux sens.

1.0.42 — Radar : case « Carte » et fond de carte sombre. Cochez Carte dans les réglages du radar : le scope se centre sur le centre de la carte au moment de l'ouverture au lieu du GPS — on cadre le secteur qui intéresse, on ouvre le radar, et on regarde le trafic là-bas. Seconde case, Fond de carte sombre : un disque de carte assombri se glisse sous le PPI, calé au pixel près sur le cercle de portée, à partir des tuiles déjà en cache (aucune requête supplémentaire).

<div align="center">
<img src="images/RATspeak_RADAR_display_carto.png" alt="RWLoRa" width="480">
<img src="images/RATspeak_RADAR_display_carto_setup.png" alt="RWLoRa" width="340">
</div>

**1.0.41 — Listes de diffusion modifiables.** Un bouton **Éditer** sous
**Envoyer** recharge une liste existante dans le formulaire : cochez pour
ajouter un opérateur, décochez pour le retirer. Le renommage ne crée plus de
doublon, et un membre dont le contact a disparu est conservé au lieu d'être
silencieusement perdu.

**1.0.40 — PING LXMF, photos compatibles TCQ, radar aéronefs.** Quatre ajouts
tournés vers l'opérationnel : un **PING LXMF** pour vérifier qu'une station
répond avant de compter dessus, l'**envoi de photos** (galerie ou prise de vue)
avec compression au format de TCQ, un transfert d'images **qui fonctionne dans
les deux sens** avec TCQ, et un **radar aéronefs** en balayage PPI accessible
depuis la carte. Détails dans les sections dédiées plus bas. Corrige aussi un
blocage de la liaison LXMF après un envoi d'image (un transfert enlisé gelait
la file d'attente jusqu'au redémarrage). ✅ Interopérable **TCQ v12.66**.

<div align="center">
<img src="images/RATspeak_Ping_LXMF.png" alt="RWLoRa" width="380">
<img src="images/RATspeak_Photos.png" alt="RWLoRa" width="380">
</div>

**1.0.38 — Radar aéronefs et compresseur d'images.** Scope radar plein écran
façon Montre Micro Radar, et compression d'images aux réglages de TCQ.

<div align="center">
<img src="images/RATspeak_RADAR_btn_loc.png" alt="RWLoRa" width="250">
<img src="images/RATspeak_RADAR_display.png" alt="RWLoRa" width="250">
<img src="images/RATspeak_RADAR_display_setup.png" alt="RWLoRa" width="250">
</div>

**1.0.37 — Synchro NEM rapide par Internet.** Quand la liaison passe par
Internet plutôt que par la radio, la synchro NEM utilise des morceaux de
**4000 octets** au lieu de 50 et n'attend plus entre deux envois : une carte
complète part en quelques secondes au lieu de plusieurs minutes. La cadence
radio reste inchangée.

**1.0.36 — Synchro NEM ULTRA-COMPACTE (marqueurs en binaire).** Après le delta, RTspk compresse encore : les marqueurs voyagent en **binaire compact** (1 octet pour le symbole, position sur 3+3 octets) au lieu du JSON. Un marqueur tient en **~1 trame** ; **2 marqueurs = 3 morceaux** au lieu de 28 — transferts **~10× plus courts** sur VHF 1200 bauds. Repli JSON automatique (lignes/zones/marqueurs à options/versions antérieures), et **recentrage** de la carte sur les objets reçus. Ajoute aussi un bouton **« 🔄 Scanner »** dans « Ajouter un TNC » (rafraîchit les appareils appairés) et la demande d'autorisation **« Appareils à proximité »** au 1er lancement. ✅ Interopérable **TCQ v12.62**.

**1.0.35 — Synchro NEM DELTA (n'échange que la différence).** La synchro NEM ne retélécharge plus toute la carte : RTspk compare les deux cartes et ne transmet **que ce qui a changé**. Cartes déjà identiques → simple accusé de **~20 octets** (jusqu'à **~97 % de données en moins** sur VHF 1200 bauds). Un objet déplacé **glisse à sa nouvelle position au lieu de se dupliquer** (même nom + même symbole = même objet ; la modif la plus récente gagne). **Repli automatique** en synchro complète si le correspondant est en version antérieure. ✅ Delta de bout en bout avec **TCQ v12.61** ; compatible en repli avec les versions plus anciennes.

**1.0.34 — Balise de position & synchro NEM fiabilisée.** Appui long sur le bouton de recentrage GPS (◎) : pose ton symbole **SATER:TEAM** à ta position, avec ton indicatif en label. Synchro NEM stabilisée et **bidirectionnelle** (émission + réception fiables sur VHF packet).

**1.0.33 — Messages FLASH sur la carte.** Bouton **⚡** pour envoyer un message
court (**90 car.**) à un ou plusieurs contacts (ou une liste de diffusion), préfixé
`&`. À la réception d'un `&`, un dialogue s'ouvre par-dessus la carte pour lire et
répondre ; `$GPS` dans la réponse insère la position. Voir « Cartographie & synchro
NEM ».
<div align="center">
<img src="images/RATspeak_repFLASH.png" alt="RWLoRa" width="320">

  <em><strong>"RTspk FLASH</strong> — message éclair, carte en direct."</em>
</div>


**1.0.32 — Carte tactique et synchro NEM.** Cartographie OpenStreetMap
embarquée **Live et Off-grid** (cache des tuiles hors réseau), **symbologie
SDIS / NEB** de TCQ (118 symboles), enregistrement/chargement au **format JSON
compatible TCQ**, et **synchro NEM** : partage de toute la situation par radio
(LXMF), interopérable avec TCQ. Voir la section « Cartographie & synchro NEM ».

<div align="center">
<img src="images/RATspeak_Carto_Nem_FTBL.jpg" alt="RWLoRa" width="640">

  <em><strong>Carte Tactique partagée en équipe **"synchro NEM"**</strong> en Mission Opérationnelle sur le terrain.</em>

</div>


<div align="center">
<img src="images/RATspeak_Carto_Nem.jpg" alt="RWLoRa" width="320">

  <em><strong>**Symbologie
SDIS / NEB**</strong> de TCQ (118 symboles) .</em>
</div>

**1.0.31 — Veille alerte et bouton MAIL.** Deux ajouts majeurs pour l'usage
en pager d'astreinte : une **veille alerte** qui continue de recevoir en LoRa
application fermée, et un bouton **MAIL** qui envoie un email par radio via une
passerelle ADRAlink. Voir les deux sections dédiées plus bas.


**1.0.27 — Listes de diffusion.** Envoi d'un message ou d'une alerte RASEC à
plusieurs opérateurs ADRASEC en une fois (voir plus bas).

**1.0.26 — Préréglage radio par défaut « France (868 MHz) ».** À la création
d'une interface LoRa/RNode, les paramètres par défaut sont : **867,5 MHz · SF 8 ·
125 kHz · CR 5 · TX 18 dBm**, avec limite d'airtime réglementaire (**1,5 % /
heure**, **33 % / 15 s**). Tout reste modifiable dans *Settings → interface LoRa*.

Un **écran de démarrage** (splash) aux couleurs RATSPEAK ADRASEC s'affiche au
lancement.

---
