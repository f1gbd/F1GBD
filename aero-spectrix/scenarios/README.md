# Scénarios de détection longue distance — ASPX v1.4

Cinq configurations prêtes à charger, conçues pour **démontrer le mode
adaptatif** : chacune place la cible dans la bande où la trame seule décroche
et où la fenêtre longue tient encore. Plus près, les deux réglages détectent
tout et la différence ne se voit pas ; plus loin, aucun des deux ne détecte
rien.

## Charger un scénario

*Fichier → Charger une configuration…* puis le `.json` voulu, et
*Lancer la simulation*.

Chaque fichier est livré **réglé sur le mode adaptatif** (`jusqu'à ×4`, case
« Raccourcir la fenêtre quand la raie dérive » cochée).

## Refaire la comparaison vous-même

Onglet *Traitement*, ligne **Fenêtre de détection** :

| pour obtenir | réglage |
|---|---|
| la colonne « trame seule » | `trame seule` |
| la colonne « adaptative » | `jusqu'à ×4` + case cochée |

Rien d'autre ne doit être touché entre les deux passes. La graine aléatoire
est fixée (`seed = 20260821`) : le bruit et la trajectoire sont identiques
d'une passe à l'autre, la seule variable est la longueur de fenêtre.

## Conditions communes

Ce sont les conditions **par défaut** d'ASPX, celles du tableau de portée du
README principal — pas des conditions choisies pour flatter le résultat :

* bruit ambiant 32 dB(A), vent 2 m/s, 18 °C, 60 % HR, 101,325 kPa ;
* antenne tétraédrique 70 cm, 1,6 m au-dessus du sol, réflexion sol activée ;
* peigne 90–520 Hz, échantillonnage 48 kHz.

## Les cinq scénarios, mesurés

Toutes les valeurs ci-dessous sont **mesurées** sur la simulation, pas
prédites par le bilan de liaison. « 1ʳᵉ détection » est la distance à la
première salve de trois trames détectées consécutives.

| # | fichier | cible | 1ʳᵉ détection | préavis gagné | trames détectées | trames pistées | erreur médiane |
|---|---|---|---|---|---|---|---|
| 1 | `01_quadricoptere_moyen_400m.json` | quadricoptère type Phantom, approche depuis 440 m à 8 m/s | 343 → **414 m** | **+8,9 s** | 45,9 → 55,9 % | 44,1 → 44,4 % | 0,31 → 0,29° |
| 2 | `02_hexacoptere_lourd_480m.json` | gros hexacoptère, passage latéral à 480 m, 9 m/s | 542 m (dès l'entrée) | — | 50,4 → **80,7 %** | 70,5 → **94,6 %** | 1,33 → 1,13° |
| 3 | `03_aile_electrique_900m.json` | aile électrique, approche depuis 960 m à 20 m/s | 605 → **723 m** | **+5,7 s** | 49,6 → 52,2 % | 25,2 % | 0,60° |
| 4 | `04_avion_thermique_2400m.json` | avion thermique 2 temps 4 cyl., approche depuis 2,4 km à 45 m/s | 2042 → **2406 m** | **+7,0 s** | 63,6 → 76,0 % | 24,7 % | 0,75° |
| 5 | `05_shahed136_3km.json` | Shahed-136 / Geran-2, approche de front depuis 3,15 km à 51,4 m/s | 2267 → **3164 m** | **+20,2 s** | 56,8 → 73,9 % | 36,2 % | 0,60° |

*Format des colonnes : `trame seule` → `adaptative`.*

L'erreur angulaire est mesurée contre la **position d'émission**, non contre
la position courante : à 3 km le son met neuf secondes à parvenir à
l'antenne, et le Shahed a parcouru 460 m pendant ce temps. Comparer à la
position courante attribuerait au capteur une erreur de près de 5° qui n'est
que le temps de vol du son.

## Ce que chaque scénario montre — et ne montre pas

**1 — Quadricoptère.** Le cas le plus net. 414 m contre 343 m : la fenêtre
longue recule le seuil de 21 %, et sur une cible lente cela vaut neuf
secondes de préavis. Les deux seuils sont **réellement atteints** ici, la
trajectoire débutant à 458 m. Le bilan de liaison annonçait 415 m en
adaptatif — mesuré 414 — et 258 m en trame seule, où il se montre pessimiste
de 33 %. La piste s'établit vers 270 m dans les deux réglages, à 0,3° près.

**2 — Hexacoptère latéral.** La distance ne varie presque pas le long de la
trajectoire : ici la fenêtre longue ne recule pas un seuil, elle **fiabilise
une détection déjà marginale**. Une trame sur deux devient quatre sur cinq,
et la piste passe de 70 % à 95 % du temps. C'est le scénario à montrer quand
la question est « la piste tient-elle ? » plutôt que « jusqu'où voit-on ? ».

**3 — Aile électrique.** Gain réel mais modeste : +118 m sur le seuil, et
aucun effet sur la piste. À noter, la détection s'établit à 723 m là où le
bilan de liaison en annonçait 931 : sur ce profil de source, **la prédiction
est optimiste de 22 %**. Le scénario est conservé tel quel pour cette
raison — il documente une limite du modèle plutôt que de la masquer.

**4 — Avion thermique.** 2406 m de première détection alors que la
trajectoire entre en scène à 2425 m : la cible est acquise presque dès son
apparition, le seuil réel n'est donc **pas atteint** dans ce scénario. Le
chiffre à retenir est le préavis, +7,0 s, et le taux de détection, 63,6 →
76,0 %. Pour mesurer le vrai seuil il faudrait faire débuter la trajectoire
au-delà de 2,6 km.

**5 — Shahed-136.** Même remarque, en plus marqué : détecté dès la première
salve de trames, à 3164 m, soit le début même de la trajectoire. La trame
seule ne l'accroche qu'à 2267 m, vingt secondes plus tard — à 185 km/h,
vingt secondes valent un kilomètre. Le bilan de liaison annonce 3472 m en
adaptatif ; ce scénario ne l'infirme ni ne le confirme, il montre seulement
que 3,15 km est tenu.

## Réserves

Ces chiffres sortent d'une **simulation**, avec un modèle de source, un modèle
d'absorption atmosphérique et un bruit de fond synthétiques. Ils décrivent le
comportement du traitement, pas une garantie de portée sur le terrain, où le
vent, les obstacles, le bruit de circulation et le régime réel du moteur
pèsent bien davantage.

Les taux de piste des scénarios 3, 4 et 5 sont identiques dans les deux
réglages : la fenêtre adaptative agit sur le **détecteur**, la goniométrie
GCC-PHAT travaillant toujours sur la trame courte, elle n'en profite pas.
C'est le comportement attendu, et il est ici mesuré plutôt que supposé.

---

*Jean-Louis (F1GBD) — ADRASEC 77 / FNRASEC — AERO-SPECTRIX (ASPX) v1.4*
