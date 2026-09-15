# Changelog — d-IA

Toutes les évolutions notables de **d-IA** (dialogue autonome entre deux IA, arbitré par un troisième).
Format inspiré de [Keep a Changelog](https://keepachangelog.com/fr/) et versionnage [SemVer](https://semver.org/lang/fr/).

Légende : ➕ ajout · 🛠️ correctif / amélioration · ⚙️ technique · ⚠️ changement de comportement · 🛡️ sécurité / garde-fou

---

## [plugin chronogramme 1.3] — 2026-09 — Le chronogramme attend SA séquence

### Corrigé

- 🛠️ **Deux horloges tournaient côte à côte sans se parler.** Séance du 15/09 : le chronogramme d'HÉLIOS NOIR 26 décrit la **séquence 7** — « 11 juillet, 14h00, focus Nangeville ». Il s'est déroulé intégralement entre les tours 0 et 16, pendant que le dialogue jouait les séquences 1 à 3, et a prononcé FINEX à 12:49 alors que la séance a continué jusqu'à 13:03 :

  ```
  [12:49:01] FINEX - 9 inject(s), 7 reaction(s) attendue(s) obtenue(s)
  [12:50:34] Passage au theme : Sequence 4 ...
  ```

  La cause : `_ETAT["t0"]`, le tour de référence de l'horloge de jeu, se fixait à la **première prise de parole vue**, quelle que soit la séquence en cours. Le chronogramme démarrait donc au tour 0 et injectait les événements du 11 juillet à 14h00 dans une séquence du 26 juin. L'horloge du chronogramme était cadencée au tour ; celle des thèmes, à `tours_par_theme`. Une seule doit commander, et **c'est le thème — c'est lui que les joueurs voient.**

### Ajouté

- ➕ **Le chronogramme déclare sa séquence et reste dormant jusqu'à elle.**

  ```
  #SEQUENCE=7                        explicite, prioritaire
  #EXERCICE=... sequence 7 - ...     à défaut, déduite du libellé
  ```

  Tant que le dialogue ne l'a pas atteinte : aucun inject, aucune horloge, aucun FINEX. L'attente est annoncée **une seule fois**, en nommant la séquence attendue et celle qui est jouée. Quand elle arrive, le chronogramme s'arme et l'horloge de jeu démarre **à ce tour-là**.

- 🛡️ **Quitter la séquence avant la fin gèle, plutôt que de dérouler dans le vide** : *« chronogramme GELÉ : le dialogue a quitté la séquence 7 pour la séquence 8, et 8 injects n'ont pas été joués. Revenez à la séquence 7, ou prononcez le FINEX par la variable de session DIRANIM_FINEX. »* Les deux issues sont données ; c'est le DIRANIM qui tranche, pas le plugin.

- ⚙️ **Compatibilité entière** : sans séquence déclarée — ni `#SEQUENCE`, ni « séquence N » dans `#EXERCICE` — le chronogramme démarre au premier tour comme avant la v1.3. Un chronogramme écrit pour l'ensemble d'un exercice continue de fonctionner sans modification. `chronogramme_helios_noir_26.csv` porte désormais `#SEQUENCE=7`.

---

## [1.11.23] — 2026-09 — Ne pas relancer un modèle qui a fini

### Corrigé

- 🛠️ **La relance fabriquait le charabia qu'elle était censée réparer.** Séance du 15/09, tour 11. La réponse du LLM2 se termine proprement : *« …al selon données. --- \*A vous, parlez.\* »*. Ollama annonce pourtant `done_reason = "length"` — il le fait dès que le plafond de tokens est atteint, **même sur une phrase achevée**. d-IA a donc relancé, en demandant à un modèle qui avait fini de « poursuivre et terminer ». N'ayant plus rien à dire, il a produit trois mille caractères de charabia — et ce charabia est devenu le message : affiché, lu à voix haute, et relu au tour suivant comme s'il s'agissait d'un message d'exercice. Même mécanique au tour 18.

  Deux causes cumulées, toutes deux corrigées :

  - **La fin propre n'était pas reconnue** quand une décoration Markdown la suivait. `A vous, parlez.*` se terminait pour nous sur une astérisque, donc « en plein mot ». On retire désormais la décoration (` * _ \` ~ # > - —`) avant de juger.
  - **On relançait sur le seul `done_reason`.** Désormais, une réponse qui se termine sur une phrase achevée n'est jamais relancée, quel que soit ce que dit Ollama.

- 🛡️ **Une relance qui part en boucle est jetée, pas collée.** Quand la suite produite répète un fragment court un nombre absurde de fois — `FR AS, NN, FR AS, NN…` — elle est écartée, le message garde ce qui avait été écrit avant, et l'opérateur en est informé. Coller du charabia à un message d'exercice est pire que de le laisser court.

  Le détecteur exige **deux signaux ensemble** : répétition d'un fragment **et** mots anormalement courts. La répétition seule ne suffit pas — un point de situation énumère légitimement « autonomie estimée à N heures » trente fois, et il ne faut pas le jeter.

  Sa limite est assumée et écrite dans le banc : l'autre forme de dégénérescence observée — des bribes de mots plutôt qu'une boucle — a une longueur moyenne de mot de 4,41 contre 4,70 pour un vrai point de situation. **Aucun seuil ne sépare les deux**, et un détecteur qui jetterait l'un jetterait l'autre. Cette forme-là n'est pas détectée : elle est empêchée en amont, la relance qui la produisait n'ayant plus lieu.

- 🛠️ **Plus de fausse alarme de troncature.** Une réponse arrêtée au plafond de tokens mais terminée sur une phrase complète ne déclenche plus le message `Reponse TRONQUEE`. Crier au loup apprend à l'opérateur à ignorer le message — et le jour où une vraie coupure survient, il ne le lit plus.

---

## [1.11.22] — 2026-09 — Un ordre s'adresse à quelqu'un

### Corrigé

- 🛠️ **Le mot-clé au milieu de la ligne n'était pas lu.** Séance du 15/09 à 12:29, deux formes rejetées coup sur coup :

  ```
  - **POUR TOUS** : **MESURE:** *mesure_meteo(lieu=nangeville)* — Évaluation urgente.
  **Demande de relevé météo complémentaire pour anticipation : MESURE: mesure_meteo(lieu=chateau_d_eau)**
  ```

  Exiger qu'une directive commence la ligne, c'est exiger d'un modèle qu'il rédige comme un fichier de configuration. Il ne le fera pas, et il a raison : **un ordre s'adresse à quelqu'un**, il se commente, il se met en gras. La contrepartie est stricte — quand quelque chose précède le mot-clé, les **parenthèses deviennent obligatoires**. C'est ce qui sépare un ordre d'une phrase : `Pensez à faire une MESURE: relever la température` ne passe pas, faute d'appel. Et le mode d'exécution reste le dernier garde-fou : en mode `exercice`, seules les consultations et la signalisation aboutissent, quelle que soit la forme de la demande.

  Le message d'auto-diagnostic de la v1.11.20 a joué exactement son rôle ici : il a nommé les deux lignes fautives, ce qui a permis de corriger l'analyseur en une passe au lieu de chercher à l'aveugle.

### Sécurité

- 🛡️ **Plugin `meteo_3x30` 2.7 — un site inconnu est REFUSÉ, plus jamais substitué.** Même séance, 12:30 : le COD demande `mesure_meteo(lieu=chateau_d_eau)`. Le plugin relevait alors le **site par défaut** et publiait `LIEU_DEMANDE = Nangeville` — c'est-à-dire qu'il rendait, sous le nom du site demandé, une mesure prise ailleurs. C'est précisément ce que la **règle de lieu** de la v1.5 existe pour empêcher, contournée par la porte de service. Deux avertissements le disaient dans le fil, mais **un avertissement ne répare pas une variable fausse : le modèle lit les variables, pas les avertissements.**

  Le plugin ne publie donc plus aucune valeur, ne lance aucune acquisition, conserve `LIEU_DEMANDE` tel que demandé, et rend la liste des sites connus avec la consigne de redemander. Mieux vaut une mesure absente qu'une mesure attribuée au mauvais lieu — sur une règle de danger de feu, la différence n'est pas académique.

  Le libellé complet publié par le plugin lui-même (`Melun (prefecture 77)`) est reconnu comme le site correspondant : refuser ce qu'on vient de donner au modèle aurait été absurde, et depuis cette version un refus annule la mesure. Défaut trouvé au banc en écrivant le test du refus.

---

## [1.11.21] — 2026-09 — Une attente doit pouvoir aboutir

### Corrigé

- 🛠️ **L'exercice s'arrêtait quinze minutes sur une condition que rien ne pouvait satisfaire.** Séance du 15/09 à 12:01, le COD écrit `ATTENDRE: TEMPERATURE_C > 30 delai=1200` alors qu'il fait 27,5 °C et qu'AROME ne se rafraîchit qu'à l'heure. La boucle a scruté consciencieusement, toutes les 30 secondes, la même valeur : *« 30 s écoulées, TEMPERATURE_C = 27.5 »*, *« 60 s »*, *« 90 s »*… La séance était morte, et le fil le disait sans le dire.

  Le principe était pourtant déjà écrit dans le mémo depuis la v1.11.2 — *« une action qui invite à attendre doit garantir qu'une variable va bouger »* — mais il ne portait que sur les actions d'un plugin, pas sur les attentes écrites par un modèle.

  d-IA ne peut pas savoir si une grandeur **va** bouger. Il peut constater qu'elle **ne bouge pas**. Quand la valeur surveillée reste identique pendant `ATTENTE_IMMOBILE_S` (120 s, soit vingt-quatre scrutations), attendre davantage n'apporte rien : l'attente est abandonnée, la raison est dite, et le dialogue reprend. Le modèle reçoit une consigne exploitable — *« cette grandeur n'évolue pas à l'échelle de l'exercice : poursuis sans elle, et raisonne sur la valeur mesurée »* — avec la valeur sous les yeux. C'est lui qui mène, pas la boucle d'attente.

  Le critère est une **durée**, pas un nombre de scrutations : cinq scrutations feraient 25 s, bien trop court pour une attente légitimement lente comme celle d'un geste d'opérateur. Une grandeur qui bouge sans atteindre le seuil va, elle, jusqu'au bout du délai demandé — c'est le délai qui tranche, pas l'immobilité.

- 🛠️ **Le délai d'abandon est annoncé dès le départ** : *« délai max 900 s, abandonnée avant si TEMPERATURE_C ne bouge pas pendant 120 s »*. L'opérateur doit savoir combien de temps il peut rester bloqué avant de l'être.

- 🛠️ **Une clôture de bloc de code collée en fin de ligne faisait perdre tout le Markdown.** Le modèle a écrit `ATTENDRE: TEMPERATURE_C > 30 delai=1200` suivi immédiatement de ` ``` `. L'analyseur ne reconnaissait une *fence* qu'en **début** de ligne : le bloc ouvert plus haut n'a jamais été refermé, et les trente lignes suivantes se sont affichées en code brut — gras, titres, puces et hiérarchie perdus. Un point de situation qui perd sa hiérarchie reste lisible, mais il ne se lit plus d'un coup d'œil, et c'est précisément ce qu'on lui demande. Les ` ``` ` sont désormais isolés sur leur propre ligne avant l'analyse, où qu'ils se trouvent. Trois accents graves au fil d'une ligne ne sont jamais du code en ligne — celui-ci s'écrit avec un seul.

---

## [1.11.20] — 2026-09 — Un COD numérote ses ordres

### Corrigé

- 🛠️ **Une directive numérotée n'était pas lue.** Séance du 15/09 à 11:52, le COD écrit :

  ```
  Directives :
  1. MESURE: mesure_meteo(lieu=nangeville)
  2. Transmets POINT DE SITUATION 1/1 dans l'heure.
  ```

  d-IA a répondu « mesure_meteo est CITÉE sans directive ». La forme était pourtant parfaite : seul le `1. ` la faisait rejeter. La tolérance de la v1.11.4 absorbait les puces (`-`, `*`, `•`) et la décoration Markdown, mais pas la **numérotation** — alors que numéroter ses ordres est la forme normale d'un message opérationnel. Le même appel, écrit par l'opérateur avec une puce, passait sans problème : **une règle de forme qui dépend de la puce choisie n'est pas une règle, c'est un piège.**

  Conséquence réelle, et c'est ce qui rend le défaut sérieux : l'exercice s'est installé sur deux tours dans l'attente d'un relevé jamais lancé, chacun renvoyant à l'autre — *« Données météo Nangeville non encore transmises »*, *« Transmission en attente des données météo »*.

  `1.`, `2)`, `10.` et `- 1.` sont maintenant acceptés, sur `ACTION:`, `MESURE:` et `ATTENDRE:`. Rien n'est cédé sur le fond : `2. Transmets POINT DE SITUATION`, `3. Alertement préfectural imminent` et `3. **mesure_meteo** :` restent refusés.

- 🛡️ **Une directive illisible se dénonce comme telle.** Dire « citée sans directive » quand le modèle a écrit une directive que nous n'avons pas su lire, c'est envoyer l'opérateur reprendre le modèle pour une faute qu'il n'a pas commise. Quand une ligne porte le mot-clé **et** le nom d'une action connue sans être reconnue, d-IA affiche désormais la ligne en cause et précise que **c'est son analyseur qui est en défaut, pas le modèle**. Une prochaine lacune de forme se signalera donc elle-même, au lieu de se déguiser en erreur du modèle.

---

## [1.11.19] — 2026-09 — La sélection était invisible, au sens propre

### Corrigé

- 🛠️ **On pouvait sélectionner le fil, mais on ne le voyait pas.** La v1.11.18 avait rendu le widget copiable — Ctrl+C et le menu contextuel fonctionnaient — mais glisser la souris ne surlignait rien. La sélection avait pourtant lieu : elle était recouverte. Les messages des LLM portent un tag de bulle qui définit un `background`, et ces tags sont créés **après** le tag `sel` intégré à Tk, donc ils priment sur lui. Le fond opaque de la bulle masquait le surlignage.

  C'est exactement ce qui explique l'observation de terrain — *« on peut copier le texte mais pas sélectionner une zone »*, et *« les messages de commentaires, si »* : le tag des commentaires ne définit aucun fond, donc la sélection s'y voyait. Un même widget, deux comportements apparents, une seule cause.

  `rendre_selection_visible()` remonte `sel` au-dessus de tous les tags et lui donne des couleurs franches — blanc sur bleu soutenu — pour qu'il reste lisible par-dessus le fond de n'importe quelle bulle. Appliqué au fil et au panneau de résumé, **après** toute la configuration des tags : un tag créé plus tard reprendrait sinon la priorité.

### Technique

- ⚙️ `test_selection.py` (vrai Tk sous Xvfb) reproduit la superposition : il vérifie d'abord que le tag de bulle prime bien sur `sel` — le défaut — puis que la correction l'inverse, que la sélection dans une bulle se copie, et que la lecture seule tient toujours après coup.

---

## [1.11.18] — 2026-09 — Le fil se copie ; une action citée n'est pas une action demandée

### Corrigé

- 🛠️ **Le fil de conversation n'était pas sélectionnable ni copiable.** Le widget `Text` de Tk en `state="disabled"` protège bien en écriture, mais Tk ne lui donne pas le focus **au clic** — la liaison de classe `tk::TextButton1` ne fait `focus` que si l'état est `normal`. L'opérateur sélectionnait donc à la souris sans que le widget prenne le focus, et Ctrl+C partait ailleurs. Le panneau de résumé avait déjà été passé en `normal` un jour, avec le commentaire « le panneau reste lisible/copiable » : quelqu'un avait rencontré le problème et l'avait résolu là, sans voir qu'il valait aussi pour le fil principal — et en le laissant, du coup, éditable par inadvertance.

  Les deux passent maintenant par `texte_lecture_seule()` : état `normal`, donc sélection, Ctrl+C, Ctrl+A et menu contextuel (Copier / Tout sélectionner) opérants ; frappe, collage et coupe refusés par les liaisons. Les dix bascules d'état autour des écritures disparaissent. En séance, un fil copiable n'est pas du confort : c'est ce qui permet de coller un message dans la main courante papier ou dans un compte rendu sans attendre l'export de fin de séance.

- 🛠️ **Une action citée n'est pas une action demandée — et le silence coûtait la séance.** Relevé le 15/09 à 11:31 : le COD écrit `3. **mesure_meteo** : Résultats attendus sous H+20`. Aucune directive `MESURE:` n'est écrite. d-IA n'avait donc rien à exécuter, et se taisait — correct, mais inutile : la séance s'installait dans une attente que rien ne viendrait satisfaire, et le modèle aurait fini par inventer la température qu'on ne lui donnait pas.

  **On ne devine pas.** Exécuter une action parce qu'un modèle en a prononcé le nom, ce serait l'exécuter aussi sur « ne pas déclencher X » — sur un dispositif qui peut piloter du matériel, aucune tolérance de parsing ne rend cela acceptable. d-IA constate l'écart, le signale à l'opérateur, et rappelle au modèle la ligne exacte à écrire, par la variable `ACTION_RAPPEL`.

  Avec une distinction qui est le cœur du correctif : **le plus souvent, le modèle attend une donnée qu'il a déjà sous les yeux.** Un plugin de mesure publie ses variables à chaque tour par `collect()` ; l'action ne sert qu'à forcer un relevé neuf ou un autre site. Quand les valeurs sont là, le message le dit et les cite :

  > *mesure_meteo est CITÉE sans directive — mais les valeurs sont DÉJÀ publiées dans les données de situation (TEMPERATURE_C = 22.7 ; VENT_KMH = 10.8). Aucune mesure n'était nécessaire ; le modèle est invité à les utiliser.*

- 🛡️ **Une directive correcte n'échoue plus jamais en silence.** Si les plugins sont globalement désactivés, `traiter_directives` rendait la main sans un mot : le modèle demandait, rien ne se passait, et l'opérateur ne pouvait pas savoir que c'était son propre interrupteur. Un échec silencieux est le pire des échecs — il se confond avec un succès. d-IA le dit maintenant, et indique où réactiver. De même, un plugin **présent mais désactivé** s'annonçait comme une « action inconnue », ce qui envoyait chercher une faute de frappe là où il n'y avait qu'un interrupteur : le message nomme désormais le plugin et sa version. Et une action réellement inconnue liste celles qui existent.

- ⚠️ **Le bloc DONNÉES DE SITUATION donne une consigne, plus une invitation.** Il disait « à prendre en compte dans ta réponse » ; le modèle lisait cela comme facultatif et préférait annoncer une mesure à venir plutôt qu'utiliser celle qu'il avait sous les yeux. Il dit maintenant que les relevés sont **disponibles maintenant**, qu'ils sont **mesurés et non simulés**, qu'ils s'emploient tels quels avec leur unité — et qu'on n'annonce pas une mesure « à venir » pour une grandeur déjà présente, ni n'invente un chiffre absent.

### Technique

- ⚙️ `test_copiable.py` tourne sur un **vrai Tk** sous Xvfb, pas sur un stub : la question portait sur le comportement du widget, pas sur notre code. Deux affirmations que j'avais écrites de mémoire ont été démenties par la sonde et corrigées dans le banc — un `Text` désactivé accepte bien `focus_set()`, et un `insert` y est ignoré en silence plutôt que de lever.

---

## [1.11.17] — 2026-09 — Un refus doit dire quoi faire

### Corrigé

- 🛠️ **Le message de refus envoyait chercher un problème qui n'existait pas.** En séance le 15/09 : `MESURE: mesure_meteo(lieu=nangeville) — mode exercice : cette action commande du materiel, hors signalisation d'ambiance`. Le moteur avait raison sur le fond — l'action était bien classée `commande` — mais pour une raison qu'il ne disait pas : le plugin chargé était `meteo_3x30` **v2.5**, resté en place à côté de la v2.6, et la v2.5 ne déclare rien. Un plugin qui ne classe **aucune** de ses actions n'est pas un plugin dont les actions commandent du matériel : c'est un plugin périmé. Confondre les deux envoie l'opérateur vers une question de doctrine là où il n'a qu'un fichier à remplacer.

  Le refus distingue maintenant les deux cas et nomme le coupable :

  > *le plugin « Meteo 3x30 (AROME France HD) » v2.5 ne classe aucune de ses actions (ni ACTIONS_LECTURE ni ACTIONS_EXERCICE) : tout y est donc traité comme une commande. Mettez ce plugin à jour, ou passez en mode confirmer.*

  Un plugin à jour qui refuse une vraie commande garde, lui, le motif de doctrine — et aucune suggestion de mise à jour inutile.

### Technique

- ⚙️ **Le déploiement avait de nouveau divergé** : `meteo_3x30.py` v2.6 avait été signalé comme écrit sur les quatre emplacements, mais les quatre portaient encore la v2.5. C'est la cinquième occurrence, dans ce projet, de *le fichier que l'on corrige n'est pas le fichier qui tourne* — et la première où la vérification par re-listage, seule parade connue, avait été omise. Elle ne doit pas l'être.
- ⚙️ `test_lecture.py` rejoue le cas du 15/09 : plugin non classé + mode `exercice` → le message doit nommer le plugin, sa version, dire que rien n'est classé et quoi faire ; un plugin à jour ne doit rien voir changer.

---

## [1.11.16] — 2026-09 — Trois niveaux d'action : une sirène fait partie de l'exercice

> Le classement « lecture / le reste » de la v1.11.15 était trop grossier. Une sirène ou un gyrophare d'alerte **pilotent bien du matériel réel** — et c'est exactement ce qu'on veut pendant un exercice : la mise en ambiance de la doctrine DSC ne se joue pas qu'en mots. Les interdire appauvrit l'exercice ; les autoriser en bloc, c'est ouvrir la porte à tout ce qu'un plugin expose.

### Ajouté

- ➕ **Le plugin classe ses actions sur trois niveaux**, lui seul sachant ce qu'elles font :

  | niveau | déclaré par | exemple |
  |---|---|---|
  | `lecture` | `ACTIONS_LECTURE` | `mesure_meteo` — consulter, aucun effet |
  | `exercice` | `ACTIONS_EXERCICE` | `sirene_pco` — agit, mais c'est de la signalisation d'ambiance |
  | `commande` | **défaut** | ouvrir une vanne, déclencher une émission |

- ➕ **Cinq plafonds côté opérateur**, du plus ouvert au plus fermé : `auto`, `confirmer`, **`exercice`** (consultations + signalisation), `lecture` (consultations seules), `off`.
- 🛡️ **Le défaut reste le plus strict.** Une action qu'un plugin oublie de classer est une `commande` : refusée partout sauf en `auto`/`confirmer`. On n'autorise jamais par omission — c'est la seule règle qui rende les autres sûres. Une action classée dans les deux listes est traitée comme une `lecture`, le plus restrictif des deux.
- ⚙️ Le motif du refus est exprimé **en termes du mode choisi**, pas du niveau seul : « hors signalisation d'ambiance » n'aurait aucun sens en mode `lecture`, où même la signalisation est refusée. Le RETEX doit pouvoir expliquer pourquoi tel ordre n'a rien produit.

### Modifié

- ⚠️ **Presets HÉLIOS NOIR 26** : `plugins_actions_mode` passe à `exercice`, et la **convention n° 5 est réécrite**. Elle ouvrait sur une négation — *« Aucune action de plugin ne pilote de matériel réel »* — ce qui était doublement mauvais : la garantie est tenue par le code, pas par une phrase, et un modèle qui lit « rien n'est réel » en tête de convention peut en conclure que ses relevés sont simulés et se croire libre de les inventer. Une négation reste, la restriction qui suit s'oublie. Nouvelle rédaction, qui affirme au lieu de nier :

  > *5. Les données mesurées sont RÉELLES : la météo relevée par `ACTION: mesure_meteo(lieu=...)` provient du modèle AROME France HD de Météo-France. Citez-la telle quelle, avec son heure et son lieu. Ne l'inventez jamais, et ne l'arrondissez pas pour qu'elle serve le scénario. Les dispositifs de signalisation de la salle (sirène, gyrophare) peuvent être réellement actionnés pour la mise en ambiance : s'ils se déclenchent, c'est l'exercice, pas un incident.*

  La dernière phrase est la seule partie qui concerne vraiment les joueurs — savoir qu'une sirène qui sonne appartient au jeu.

---

## [1.11.15] — 2026-09 — Le mode LECTURE : consulter sans commander

> Le mode `off` existe pour une bonne raison — un COD fictif ne doit actionner aucun matériel réel. Mais il ne distinguait pas une action qui **agit** d'une action qui **lit**. Relever la météo ne commande rien : c'est une consultation. L'interdire privait l'exercice de ses données réelles, et c'est précisément ce qui fait la valeur pédagogique d'HÉLIOS NOIR 26 — un scénario fictif nourri de chiffres vrais.

### Ajouté

- ➕ **Un quatrième mode d'exécution**, entre `off` et `confirmer` :

  | mode | ce qui s'exécute |
  |---|---|
  | `auto` | tout (banc de mesure, domotique) |
  | `confirmer` | tout, après validation de l'opérateur |
  | **`lecture`** | **les consultations seulement — c'est le mode de l'exercice cadre** |
  | `off` | rien ; tout est journalisé |

  `off` garde **exactement** son sens : qui s'y fie ne voit aucun changement. C'est le preset qui déclare l'intention, explicitement.

- ➕ **C'est le PLUGIN qui déclare ce qui est une lecture**, par une constante de module `ACTIONS_LECTURE`. Lui seul sait si `mesure_meteo` interroge une API ou si `commander_relais` ferme un contact — d-IA n'a pas à le deviner depuis un nom. **Constante absente, aucune action n'est autorisée** : un plugin écrit avant cette version reste intégralement bloqué en mode lecture. On n'ouvre jamais par oubli.
- 🛡️ **Le catalogue ne propose que l'exécutable.** En mode lecture, le modèle ne voit plus les actions qu'on lui refuserait ensuite. Lui présenter une action pour la lui refuser, c'est le pousser à la demander pour rien — et un modèle à qui l'on refuse ce qu'on vient de lui offrir finit par inventer le résultat.

### Modifié

- ⚠️ **Presets HÉLIOS NOIR 26** (`_3llm` et `_operateur`) : `plugins_actions_mode` passe de `off` à `lecture`. La **convention d'exercice n° 5** est réécrite en conséquence — *« Aucune action de plugin ne pilote de matériel réel ; en revanche les MESURES sont vraies : la météo relevée par `ACTION: mesure_meteo(lieu=...)` provient du modèle AROME France HD, et doit être traitée comme une donnée réelle, jamais inventée. »* Une convention qui ne décrit plus le comportement réel est pire qu'une convention absente : le modèle lit ce qu'on lui écrit.
- ⚙️ **Plugin `meteo_3x30` 2.6** : déclare `ACTIONS_LECTURE = ("mesure_meteo", "releve_meteo_maintenant")`. Ses deux actions interrogent Open-Meteo et écrivent un relevé ; aucune ne commande quoi que ce soit.

---

## [1.11.14] — 2026-09 — Les dates se disent en français

### Corrigé

- 🛠️ **`11/07` était prononcé « novembre deux mille sept ».** SAPI5 lit une barre oblique avec un séparateur de son cru — souvent mois/année à l'anglo-saxonne. Sur un exercice cadre, où le chronogramme est daté ligne par ligne et où chaque inject porte son groupe horaire, une date mal prononcée n'est pas une coquetterie : c'est un événement que l'opérateur situe au mauvais moment. Le nettoyage vocal traitait le balisage Markdown ; il traite maintenant aussi la diction.

  | écrit | dit |
  |---|---|
  | `11/07` | 11 juillet |
  | `11/07/2026` | 11 juillet 2026 |
  | `01/07` | 1er juillet |
  | `2026-07-11 14:00` | 11 juillet 2026 à 14 heures |
  | `2026-09-15T10:27` | 15 septembre 2026 à 10 heures 27 |
  | `14:00` · `13h45` · `9h` | 14 heures · 13 heures 45 · 9 heures |
  | `H-15` · `J+2` | H moins 15 · J plus 2 |

- 🛡️ **Ce qui n'est pas une date reste intact.** Un correcteur trop zélé est pire que le défaut : il dirait `24/7` comme une date et `3:1` comme un horaire. Le mois doit donc être écrit sur **deux chiffres** et les bornes de calendrier sont vérifiées. Restent inchangés : `24/7`, `3/4`, `3:1`, `145.500 MHz`, `48.5575`, `3 x 30`, `145/175`, `45/12`, `25:70`. `test_diction.py` vérifie les deux listes — ce qui doit changer, et ce qui ne doit pas.

---

## [1.11.13] — 2026-09 — d-IA règle lui-même ce qu'il sait mesurer

> Jusqu'ici, d-IA *constatait* que le prompt ne tenait pas dans `num_ctx` — puis envoyait la requête telle quelle : **1 172 tokens de réponse demandés alors qu'il en restait un seul de libre**. Constater un budget dépassé puis dépenser comme si de rien n'était, ce n'est pas un avertissement, c'est un commentaire. Cette version remplace l'avertissement par le geste.

### Ajouté

- ➕ **Auto-tuning de `num_ctx` sur la machine du jour.** Avant DEBEX, d-IA détermine lui-même la fenêtre de contexte : il calcule le besoin de la séance (sujet, personas, fenêtre mémoire) et le confronte à ce que la machine porte réellement. Il n'y a plus de valeur à régler à la main.
- ➕ **La VRAM est MESURÉE, pas déduite.** d-IA charge les modèles au contexte visé puis demande à Ollama où il les a mis (`/api/ps` : `size_vram` contre `size`). Si un modèle déborde sur le CPU — la panne silencieuse qui fait tourner le dialogue cinq à dix fois plus lentement sans que rien ne le dise — il redescend d'un cran et recommence, trois fois au plus. **La mesure vient du serveur qui fera le travail**, donc elle vaut aussi bien pour l'Ollama du portable que pour celui d'une autre machine du réseau, et elle ne peut pas se tromper de carte.
- ➕ **Le cache KV se calcule** au lieu de s'estimer : `2 × couches × têtes_kv × dim_tête × num_ctx × 2 octets`, la géométrie étant lue dans `/api/show`. Cela donne un point de départ crédible et évite d'essayer 32768 sur une carte de 8 Go.
- ➕ **Local, réseau, cloud, ou les trois à la fois.** `num_ctx` est unique pour toute la séance : d-IA examine **chaque** cible et retient **la plus contrainte** — régler sur la plus confortable étranglerait la plus modeste, et c'est elle qui déciderait du résultat. En cloud, aucune VRAM de l'opérateur n'est en jeu : le seul plafond est le contexte d'entraînement du modèle, et **aucun modèle distant n'est chargé pour mesurer**.
- ➕ **Réadaptation automatique au changement de machine.** Le plafond mesuré appartient à la *cible* — serveur + modèles — pas à la séance. Repartir sur le même serveur ne recoûte rien ; basculer d'un Ollama distant vers celui du portable change la clé et déclenche un nouveau calibrage, sans que personne ait à le demander. Changer de preset, lui, ne change que le besoin : aucune raison de remesurer.
- ➕ **Machine sans GPU** : ce n'est plus la VRAM qui limite, redescendre ne gagnerait rien. d-IA le dit et règle `num_ctx` sur le besoin de la séance.

### Corrigé

- 🛠️ **`num_predict` est plafonné à la place réellement libre.** On réclamait 1 172 tokens là où il en restait un ; Ollama faisait alors la seule chose possible — tronquer le **début** du prompt, c'est-à-dire les personas et les règles de conduite, et couper la réponse. Le tour en cours est désormais sauvé : une réponse courte mais entière vaut mieux qu'une consigne coupée en plein mot, qui ressemble à une consigne complète.
- 🛠️ **La fenêtre mémoire se resserre toute seule** quand le prompt déborde, et **avant le premier tour** plutôt qu'au cinquième. Plutôt que d'agrandir le récipient — ce qui se paie en VRAM — on réduit ce qu'on y met. Rien n'est perdu : les tours sortants passent au résumé glissant. Le coût d'un tour est *mesuré* sur les tours réellement échangés, pas pris dans une constante — un dialogue d'exercice cadre, avec ses SITREP chiffrés, ne pèse pas comme une conversation ordinaire. Plancher à 4 tours : en dessous, un dialogue à trois voix perd le fil.
- 🛠️ **Un message de service ne se répète plus à chaque tour.** L'ajustement n'est annoncé qu'au *changement* ; sans cela, la même phrase serait revenue vingt fois dans la main courante, et l'opérateur aurait cessé de lire les messages de service — y compris ceux qui comptent.

### Garde-fous

- 🛡️ **En séance, `num_ctx` n'est jamais touché.** Le changer force Ollama à recharger le modèle : un gel de plusieurs secondes et un cache vidé — au milieu d'un inject du chronogramme, ce n'est pas anodin. Le réglage se fait avant DEBEX, ou pas du tout.
- 🛡️ **`d-ia_setup.json` n'est jamais réécrit.** L'ajustement vit le temps de la séance ; l'opérateur retrouve **sa** valeur au prochain lancement. Une configuration déclarée qui dérive derrière le dos de celui qui l'a posée est pire que le défaut qu'elle corrige.
- 🛡️ **Aucune sonde n'empêche une séance de démarrer.** `/api/ps` muet, `/api/show` muet, serveur injoignable : d-IA continue avec ce qu'il sait. `autotune_ctx: false` rend la main entièrement à l'opérateur.

### Technique

- ⚙️ `OllamaClient.ps()` et `.show()` — introspection volontairement **silencieuse** : elles rendent `None` plutôt que de lever. Une sonde qui fait tomber le démarrage du dialogue serait un remède pire que le mal.
- ⚙️ **Les jeux de test lisaient une copie périmée de `d-IA.py`** (build du 14/09) : neuf suites déclaraient « OK » sans jamais avoir vu le code des v1.11.12 et v1.11.13. L'arbre de test et l'arbre de livraison n'en font plus qu'un. C'est la quatrième occurrence, dans ce projet, du même piège — *le fichier que l'on corrige n'est pas le fichier qui tourne* — et la seule parade reste de vérifier sur disque plutôt que de faire confiance à une écriture qui a l'air réussie.
- ⚙️ Nouveaux bancs : `test_autotune.py` (serveur distant, portable, cloud, mixte, sans GPU, sondes muettes) et `test_budget.py` (plafonnement, resserrement, plancher, non-dérive de la configuration déclarée, vérifiée par lecture de l'arbre syntaxique).

---

## [plugin meteo_3x30 2.5] — 2026-09 — Le fichier écrit n'était pas le fichier lu

> Relevé en séance réelle le 15/09 à 10:27 : `acquisition relancee automatiquement sur Nangeville. Les valeurs arriveront dans quelques secondes.` — puis, trente-huit secondes plus tard : `releve absent ou illisible : meteo_releves.json. Acquisition automatique impossible.` Deux défauts distincts, tous deux introduits par l'automatisme de la v2.3.

### Corrigé

- 🛠️ **Le plugin acquérait dans un fichier et regardait dans un autre.** Sans site nommé, `collect()` lit le fichier **commun** (`meteo_releves.json`, l'emplacement d'avant la v2.0), mais l'acquisition automatique se rabat sur `SITE_DEFAUT` et écrit donc dans `meteo_releves_nangeville.json`. Il ne pouvait **rien** trouver — ni à la première séance, ni jamais. Le repli existait déjà dans l'autre sens (site → fichier commun, pour les installations d'avant la v2.0) ; il manquait dans celui-ci.
- 🛠️ **« Acquisition impossible » était annoncé pendant qu'une acquisition tournait.** `relance_auto()` rendait `None` dans trois situations très différentes : acquisition en cours, relance trop récente (garde-fou anti-martèlement de 10 minutes), et impossibilité réelle. L'appelant ne voyait qu'un `None` et parlait de réseau coupé — trente-huit secondes après en avoir lancé une. Dire qu'une chose est impossible pendant qu'elle est en cours, c'est envoyer l'opérateur chercher une panne qui n'existe pas. La fonction rend désormais une phrase dans tous les cas où quelque chose est en route (`acquisition deja en cours depuis 12 s`, `acquisition lancee il y a 40 s ; prochaine relance possible dans 9 min`), et `None` seulement quand il n'y a plus rien à attendre — cas où la commande manuelle revient, en dernier recours.

### Technique

- ⚙️ `test_seance_reelle.py` rejoue la séance du 15/09 : première installation sans aucun fichier, `collect()` sans site nommé, puis `collect()` une fois l'acquisition terminée — et vérifie que le plugin **retrouve le relevé qu'il a lui-même fait écrire**. Plus les cas acquisition-en-cours, garde-fou récent, panne réelle, et site nommé non détourné.

---

## [plugin meteo_3x30 2.4] — 2026-09 — Un automatisme ne passe pas devant une demande

### Corrigé

- 🛠️ **L'acquisition automatique volait le verrou à une mesure explicitement demandée.** `ACTION: mesure_meteo(lieu=melun)` commence par une lecture de l'état courant ; en v2.3, cette lecture, ne trouvant aucun relevé, lançait une acquisition — sur `SITE_DEFAUT`, puisqu'aucun site ne lui était passé à ce stade. Le verrou était alors pris par Nangeville, et la mesure de Melun demandée juste après se voyait répondre « acquisition déjà en cours ». **Le LLM demandait Melun ; il obtenait Nangeville, ou rien.** C'est exactement l'erreur que la règle de lieu de la v1.5 existe pour empêcher : attribuer à un site une mesure faite ailleurs. L'acquisition automatique appartient désormais au seul `collect()`, où personne ne viendra chercher la donnée derrière.
- 🛠️ **Une variable publiée pouvait dépasser 160 caractères** (`METEO_AUTRES_SITES` sortait à 167). Le contrat d-IA plafonne à 160, et c'est d-IA qui tronquait — au milieu d'un nombre. Une valeur coupée en plein chiffre n'est pas une valeur incomplète, c'est une valeur **fausse**. La coupe appartient au plugin, qui sait où couper : elle se fait sur un séparateur d'énumération, et `_ordonner()` devient l'entonnoir unique qui borne tout ce qui sort.

---

## [plugin meteo_3x30 2.3] — 2026-09 — Le plugin va chercher sa donnée

### Corrigé

- ⚠️ **Plus rien à lancer à la main.** Une première installation affichait `releve absent ou illisible [...] lancer : python meteo_3x30_collecte.py`. C'était demander à l'opérateur de réparer une chose que le plugin sait faire seul — et précisément au moment où il ne peut pas la deviner, avant même le premier tour. Un plugin dont la source de données est absente doit aller la chercher, pas rédiger une consigne. Le message de relevé *périmé* ne dicte plus de commande non plus ; la commande manuelle ne subsiste qu'en dernier recours, quand l'acquisition automatique est impossible.
- 🛡️ La règle des 2 secondes tient : `collect()` ne va toujours pas sur le réseau, il *démarre* l'acquisition en tâche de fond et rend la main. Une relance par site et par tranche de 10 minutes au plus ; hors ligne, le plugin le dit sans boucler ni inventer de valeur.

---

## [plugin meteo_3x30 2.2] — 2026-09 — Les points de mesure sont vérifiés

### Corrigé
- 🛠️ **Deux sites partageaient le même point.** `nangeville` et `fontainebleau` portaient tous deux `(48.40, 2.70)`. Le plugin travaillait donc correctement — il relevait bien le point demandé — mais deux noms différents désignaient la même mesure, et Nangeville étant la commune-pilote d'HÉLIOS NOIR 26, c'est le relevé de l'exercice qui était concerné. C'est le défaut le plus difficile à voir à la lecture d'un fil : les valeurs sont plausibles, elles sont seulement attribuées à un lieu qui n'a pas été mesuré.
- 🛠️ **Les six points ont été repris sur l'API Géo de l'État** (`geo.api.gouv.fr`, centre de commune, vérifiés le 14/09/2026) et portent désormais quatre décimales et leur **code INSEE en commentaire**, pour qu'ils soient recontrôlables. Deux autres écarts au passage : Melun était à 7 km de son centre, Nemours à 2 km.
- ⚠️ **Nangeville est une commune FICTIVE : elle n'a pas de météo.** Son relevé est pris sur un point réel — **Nangis (77327)** — et le libellé le dit : `Nangeville (site fictif - mesure reelle a Nangis 77)`. Un plugin ne présente jamais une valeur pour ce qu'elle n'est pas ; si le point de mesure est conventionnel, la convention doit être lisible par l'opérateur. Une seule ligne à changer pour déplacer ce point.

### Ajouté
- 🛡️ **Un relevé pris à l'ancien point du site est refusé.** Corriger des coordonnées ne suffisait pas : le fichier déjà sur disque portait le bon *nom* sous l'ancien *point*. Le plugin compare désormais les coordonnées du relevé à celles du site (tolérance 0,02°, au-delà de la maille AROME) et, en cas d'écart, ne publie **aucune valeur** — il dit lequel des deux points est lequel et rappelle la commande à lancer : `releve de nangeville pris a (48.4, 2.7) alors que le site est a (48.5575, 3.0079) - releve perime, ignore`. Le contrôle est placé au **point de publication unique**, pas sur un chemin particulier.
- 🛡️ **Garde-fou `controler_sites()`** : au chargement, le plugin vérifie qu'aucun site ne partage le point d'un autre. Une anomalie remonte dans le fil de la conversation — une fois par séance, pas à chaque tour — en nommant les deux clés et le point commun. Ce défaut ne pourra plus passer inaperçu.
- ⚙️ **Les jeux de test lisaient des coordonnées écrites en dur** — le défaut même que le plugin vient d'apprendre à détecter, reproduit dans les tests. `test_lieu`, `test_sync`, `test_relance` et `test_multisite` lisent maintenant le point dans `SITES`.
- ⚙️ Quatre cas de test ajoutés à `test_multisite.py` : table saine, points tous distincts, et détection d'un doublon réintroduit à la main. La coordonnée attendue se lit désormais dans `SITES` au lieu d'être recopiée dans le test.

---

## [plugin chronogramme 1.2] — 2026-09 — Une variable de session mal remplie ne ment plus

### Corrigé
- 🛠️ **Une variable `CHRONOGRAMME` vide — ou ne contenant que des espaces — retombait sur `chronogramme.csv` en prétendant qu'il avait été demandé.** Le fil annonçait alors `fichier absent - …\chronogramme.csv`, en nommant un fichier que personne n'avait jamais réclamé ni créé, pendant qu'un chronogramme parfaitement valide dormait dans le même dossier. Une variable vide vaut désormais absence de variable.
- ➕ **Un nom qui ne correspond à rien est dit comme tel, avec la liste de ce qui existe** : `CHRONOGRAMME = 'helios noir 27' ne correspond a aucun fichier (chronogramme_helios_noir_27.csv attendu). Disponible(s) dans ce dossier : helios noir 26.` Un message de diagnostic qui ne nomme pas ce qui EST disponible oblige à aller voir le dossier — autant le dire tout de suite.

---

## [plugin chronogramme 1.1] — 2026-09 — Le fichier déposé est le fichier joué

### Corrigé
- 🛠️ **Un chronogramme déposé dans `plugins_dia\` ne se chargeait pas.** Le plugin n'acceptait que `chronogramme.csv` ou un fichier désigné par la variable de session `CHRONOGRAMME`. Le fichier livré s'appelant `chronogramme_helios_noir_26.csv`, une séance préparée correctement démarrait sans chronogramme, avec pour seul indice un `fichier absent - …\chronogramme.csv` qui nommait un fichier que personne n'avait jamais créé.
- ⚠️ **La résolution suit désormais trois règles**, dans cet ordre : la variable `CHRONOGRAMME` ; `chronogramme.csv` ; puis l'**unique** `chronogramme_*.csv` présent dans le dossier. Déposer le fichier **est** un acte explicite — exiger en plus une variable invisible transformait une préparation correcte en séance sans chronogramme. C'était une erreur de conception : la sûreté visée (ne pas s'inviter dans une séance qui n'a rien demandé) est obtenue par l'annonce, pas par le silence.
- ➕ **Le plugin annonce toujours ce qu'il joue** : `chronogramme_helios_noir_26.csv charge - HELIOS NOIR 26 - sequence 7 (seul chronogramme present dans le dossier), 9 ligne(s) datee(s)`. Un plugin qui prend la main ne doit jamais le faire en silence.
- ➕ **Avec plusieurs fichiers, il ne choisit pas** : il les nomme tous et rappelle la variable à écrire. Sans aucun fichier, il se tait comme avant, une seule fois par séance.

### Technique
- ⚙️ 11 cas de test ajoutés (`test_chronogramme.py`, cas 17), dont le cas réel : un seul fichier nommé, aucune variable de session.

---

## [1.11.12] — 2026-09 — Une réponse coupée ne peut plus passer inaperçue

Retour de séance du 15 septembre : réponses tronquées « au bout de 4 à 5 tours ». Le diagnostic de la v1.11.11 a nommé le coupable — `prompt 4095 tokens + reponse 1 tokens, pour num_ctx = 4096 — c'est num_ctx qui est sature` — mais trois choses l'entouraient mal.

### Ajouté
- ➕ **Le contexte est contrôlé AVANT le premier tour.** L'alerte en cours de route arrivait trop tard : la séance avait déjà tourné quatre ou cinq tours, les réponses s'étaient raccourcies, et le prompt finissait par occuper la fenêtre entière — Ollama tronquant alors le **début** du prompt, c'est-à-dire le persona et les règles de conduite. Les modèles jouaient sans leurs instructions sans que rien ne le dise. d-IA estime désormais le prompt **en régime établi**, fenêtre mémoire pleine, et prévient au démarrage : `[CONTEXTE TROP PETIT DES LE DEPART : … Les reponses seront coupees a partir du 4e ou 5e tour, et Ollama tronquera le DEBUT du prompt - donc les personas. Portez num_ctx a 16384…]`. Une seule fois par séance.
- ➕ **L'export Markdown porte les incidents.** Les messages de service — troncature, contexte trop petit, actions de plugins, attentes — n'étaient affichés que dans le fil et disparaissaient de l'export. En RETEX, on relisait donc un dialogue **sans ses incidents**, alors que c'est justement là qu'on cherche ce qui a manqué. Ils sont désormais conservés et intercalés au tour où ils sont survenus, horodatés, en citation.

### Corrigé
- 🛠️ **La valeur de `num_ctx` conseillée était au ras du besoin.** Suivre le conseil ramenait au même problème au premier inject de chronogramme ou au premier preset un peu plus bavard. Le conseil porte désormais une marge de 30 %, il dit « au moins », et il précise que le calcul vaut pour **le sujet et les personas actuellement chargés** — importer un preset change le besoin, et le preset apporte son propre `num_ctx`.
- 🛠️ **Une troncature pouvait rester muette.** Quand la relance de `_generer_complet` rendait une chaîne vide, la boucle sortait avec un texte coupé en plein mot et `_signaler_troncature` ne disait rien : il interrogeait `last_done_reason`, qui décrivait la **relance** et non la génération coupée. Le signalement repose maintenant sur l'état de la première génération et sur la ponctuation finale du texte rendu.
- 🛠️ **La relance ne pouvait pas aboutir quand `num_ctx` sature** — elle repart avec un prompt **plus gros** que celui qui ne tenait déjà pas (le prompt d'origine, plus la réponse déjà écrite, plus une consigne). Le remède était donc voué à l'échec précisément dans le cas où il servait, au prix de deux appels perdus. `_fenetre_saturee()` s'appuie sur les compteurs réels d'Ollama pour abandonner la relance et le dire : `c'est num_ctx qui est sature : la relance ne peut pas aboutir, elle repartirait avec un prompt plus gros`.
- 🛠️ Un message qui se termine par deux-points n'est plus considéré comme une fin propre : il annonce une suite qui n'est pas venue.

### Technique
- ⚙️ 7 cas de test (`test_troncature.py`), dont le cas réel du 15 septembre reproduit à l'identique : prompt 4095 / `num_ctx` 4096 / réponse 1 token.

---

## [presets HÉLIOS NOIR 26 v2.0] — 2026-09 — Conformes à la doctrine « exercice cadre »

Les deux presets `formation_helios_noir_26_3llm` et `formation_helios_noir_26_operateur`.

### Changé
- ⚠️ **Le `sujet` est devenu une MISE EN AMBIANCE**, au sens du § 3.1.3.3 du guide : ce que les joueurs savent au DEBEX, et rien de plus. Les conséquences à venir — décès liés à la chaleur, pénurie de carburant, départs de feu, climatisation à l'arrêt à l'EHPAD — en ont été retirées. Les joueurs les découvriront par les messages qu'ils reçoivent. *« Un exercice faussé n'a aucun intérêt »* (§ 3.1.1, pas de divulgation).
- ⚠️ **Les huit séquences décrivent la situation, plus les actions attendues.** « Le COD prend contact avec l'ADRASEC pour vérifier… » prescrivait au joueur sa propre réaction ; la séquence 7 listait le contenu du SITREP que l'opérateur devait justement établir. Elles énoncent désormais des faits perçus, pas un programme.
- ⚠️ **`persona3` n'est plus un injecteur libre mais une ANIBAS d'appoint**, subordonnée au chronogramme : elle ne pose que des **conséquences** de ce qui figure déjà dans le fil, jamais une ligne nouvelle du scénario. L'animation haute (COZ, COGIC, préfet) est tenue par le chronogramme, via sa colonne `emetteur`. Le libellé du rôle passe de « Animation » à « Animation basse ».

### Ajouté
- ➕ **Les conventions d'exercice sont écrites dans le `sujet`** et énoncées aux joueurs : mot EXERCICE en tête de chaque message, téléphonie publique et Internet interdits, jeu auto-alimenté dans la limite des moyens et délais réels, temps compressé mais délais d'acheminement réels, aucune action de plugin sur du matériel réel, et — la plus importante — les joueurs ne connaissent pas la suite du scénario.
- ➕ **Le gabarit du point de situation de l'annexe 1** dans `persona1` et `persona2` : situation générale, situation par sites, autres événements et impacts collatéraux, bilan des victimes, décisions prises, moyens engagés et besoins exprimés, **évolution possible**. Cette dernière rubrique n'est jamais omise : elle oblige à anticiper au lieu de constater. Le trafic courant, lui, reste bref.
- ➕ **Le chronogramme est câblé** dans les deux personas joueurs : `HEURE_JEU` sert à horodater, `INJECT` est traité comme du trafic entrant, son absence n'autorise pas à inventer un événement, `PHASE_EXERCICE = FINEX` clôt le trafic.
- ➕ **Les trois règles d'animation du § 3.1.1 dans `persona3`** : pas de constat d'échec, un événement pour une réaction attendue, recalage des joueurs qui oublient les délais d'acheminement.
- ➕ **Le cadre espace-temps dans `persona1`** : mesures **immédiates** ET **différées**, parce qu'un renfort demandé n'arrive pas tout de suite. C'est l'écueil des « joueurs trop imaginatifs » décrit par le guide.

### Sécurité / garde-fou
- 🛡️ **`"plugins_actions_mode": "off"`** dans les deux presets. Ce n'était jusqu'ici qu'une précaution d'ingénierie ; le guide lui donne le statut de **convention d'exercice**, au même titre que l'interdiction du téléphone public. Un COD fictif ne doit pas pouvoir actionner du matériel réel, et la convention voyage désormais avec l'exercice au lieu de dépendre du souvenir de celui qui lance la séance.

---

## [plugin chronogramme 1.0] — 2026-09 — d-IA tient le rôle du DIRANIM

Référence : *Exercices de sécurité civile — Guide méthodologique sur les exercices Cadre et Terrain*, Direction de la Sécurité Civile, 2011, § 3.1.3.3.

### Ajouté
- ➕ **`plugins_dia\chronogramme.py`.** L'animation de d-IA tirait jusqu'ici un événement au sort dans un répertoire, tous les K tours, sans lien avec un objectif. Le plugin déroule désormais un **chronogramme** écrit en CSV par le formateur avant la séance — le tableau que la doctrine fait remplir « de la droite vers la gauche », en partant de la réaction attendue.
- ➕ **Une horloge de jeu.** Les prises de parole sont converties en minutes de jeu (`MINUTES_PAR_TOUR`, 5 par défaut) et `HEURE_JEU` est publiée à chaque tour : `11/07 14h20 (H+20)`. Les joueurs cessent d'inventer leurs horodates. C'est la double colonne « groupe horaire (réel et H+X mn) » du guide.
- ➕ **Un inject, un destinataire.** Une ligne n'est publiée qu'au tour du joueur désigné en colonne `recepteur` (`LLM1`, `LLM2`, `TOUS`, ou un libellé de rôle du preset). L'autre partie ne l'a pas reçue : elle l'apprendra si — et seulement si — l'information circule. C'est ce que le guide cherche à tester dans un centre opérationnel.
- ➕ **Pas de constat d'échec.** Sans réaction détectée au bout de 4 tours, le plugin envoie le texte de la colonne `relance`, marqué « par un autre vecteur ». Le guide : *« il est préférable de relancer l'événement ou l'incident par un autre vecteur de communication pour faire prendre conscience aux joueurs qu'ils ont raté quelque chose mais qu'ils ont encore le temps de réagir comme dans la réalité »*.
- ➕ **Incidents de réserve.** Les lignes dont le groupe horaire vaut `RESERVE` ne se jouent jamais seules ; le formateur les déclenche quand le jeu va trop vite.
- ➕ **Substitution inter-plugins.** `{TEMPERATURE_C}`, `{VENT_KMH}`, `{HUMIDITE_PCT}` dans le texte d'un événement sont remplacés par les valeurs publiées par `meteo_3x30`. La mise en ambiance type du guide — « il fait 25 degrés à l'ombre, le vent souffle à 5 km/h » — se remplit donc avec des relevés AROME **réels**.
- ➕ **Main courante de RETEX** : `..\logs\retex_chronogramme_AAAAMMJJ.csv`, une ligne par événement, avec la réaction attendue et son pointage. Bilan affiché dans le fil au FINEX. L'exercice devient **évaluable**.
- ➕ **`chronogramme_helios_noir_26.csv`** : la séquence 7 d'HÉLIOS NOIR 26 au format doctrine — 9 lignes datées, 5 incidents de réserve.

### Sécurité / garde-fou
- 🛡️ **La réaction attendue n'est jamais publiée.** Elle est lue, journalisée et pointée, mais ne sort pas du plugin — ni en variable, ni en avertissement. C'est la règle « pas de divulgation » du § 3.1.1, et elle fait l'objet d'un cas de test dédié.
- 🛡️ **Le pupitre du DIRANIM passe par les variables de session**, pas par des actions : `DIRANIM_PAUSE`, `DIRANIM_AVANCE`, `DIRANIM_RESERVE`, `DIRANIM_FINEX`, `MINUTES_PAR_TOUR`, `CHRONOGRAMME`. Le formateur garde donc la main complète alors même que le preset d'exercice impose `"plugins_actions_mode": "off"`. La seule action déclarée, `chronogramme_etat`, est en **lecture seule** : un COD fictif ne pilote pas le chronogramme de son propre exercice.

### Technique
- ⚙️ Le suivi est indexé par numéro de ligne dans le fichier : corriger une coquille en pleine séance ne fait pas perdre sa place au déroulé. Changer de `CHRONOGRAMME` remet le déroulé à zéro.
- ⚙️ Un destinataire qui ne prend jamais la parole ne bloque plus le chronogramme : au bout de 6 tours, l'inject est remis à qui parle, et l'anomalie est signalée.
- ⚙️ Lecture avec cache sur la date de modification ; 60 appels à `collect()` en 4 ms, très en deçà du budget de 2 s.
- ⚙️ 15 cas de test (`test_chronogramme.py`) : lecture et tri du CSV, horloge, destinataire, non-divulgation, relance et pointage, pupitre, main courante, substitution, plafond des valeurs, budget de temps, robustesse (fichier absent, groupe horaire illisible, DEBEX invalide).

---

## [1.11.2] — 2026-09 — Le souligné intra-mot n'est plus de l'italique

### Corrigé
- 🛠️ **`RELEVE_AGE_MIN` s'affichait `RELEVEAGEMIN`, en italique.** Le tokenizer Markdown inline traitait `_` comme `*` et ouvrait une emphase n'importe où, y compris au milieu d'un mot — donc au milieu de tous les identifiants snake_case que les modèles écrivent en permanence : noms de variables de plugins, noms de fichiers, identifiants d'actions. La directive s'exécutait correctement (le journal montre bien `Attente de RELEVE_AGE_MIN < 2`) : seul l'affichage mentait. En formation, c'est l'opérateur qui recopie une directive fausse depuis la transcription. Le souligné n'ouvre désormais une emphase qu'**en bordure de mot**, et sur un corps qui ne commence ni ne finit par une espace — la règle de CommonMark, et déjà celle du nettoyage TTS depuis la v1.4 (`snake_case` préservé à la lecture). `**gras**`, `*italique*`, code, liens, barré : inchangés.

---

## [1.11.11] — 2026-09 — Mesurer au lieu de supposer

### Ajouté
- ➕ **Les compteurs réels d'Ollama sont mémorisés et affichés.** Diagnostiquer une réponse coupée à partir d'une estimation du prompt ne menait à rien : tantôt LLM1, tantôt LLM2, et des ordres de grandeur qui ne collaient pas. Ollama rapporte pourtant `prompt_eval_count` (tokens du prompt réellement consommés) et `eval_count` (tokens produits) à chaque génération. Le message de troncature les affiche désormais à côté des réglages, et **désigne le plafond atteint** : `[Reponse TRONQUEE - prompt 2735 tokens + reponse 1172 tokens, pour num_ctx = 4096 et num_predict effectif = 1172 (base 700, creativite 45 %) - c'est num_predict qui est atteint. Fin recue : « ...en service : ** »]`
- ⚙️ Rappel utile au passage : le `num_predict` **effectif** n'est pas celui du preset. Le curseur Créativité le multiplie (jusqu'à +150 %) — à 45 %, une base de 700 donne 1 172. Le message le dit maintenant explicitement.

---

## [1.11.10] — 2026-09 — Les réponses coupées venaient de num_ctx

### Corrigé
- 🛠️ **Le coupable n'était pas `num_predict`, mais `num_ctx`.** Sur le preset HÉLIOS NOIR, le prompt pèse environ **5 400 tokens** — sujet 540, persona 520, gabarit et variables de plugins 350, mémoire de 10 tours 3 900 — pour un `num_ctx` de **4 096**. Ollama tronque alors le début du prompt et il ne reste plus rien pour écrire : la réponse s'arrête après quelques mots (« …relevé des besoins résidents. E »), `done_reason` vaut `length`, et augmenter `num_predict` ne peut rien y changer puisque la place manque en **entrée**.
- ➕ **d-IA estime la taille du prompt avant de générer** et prévient, avec les deux nombres et la marche à suivre : `[CONTEXTE TROP PETIT : prompt estimé à 5400 tokens + 1400 de réponse, pour num_ctx = 4096. Ollama tronque le début du prompt et coupe la réponse. Portez num_ctx à 8192, ou réduisez la fenêtre mémoire (actuellement 10 tours).]` Une alerte au plus toutes les 10 minutes.
- ⚙️ Le message de troncature **désigne le bon coupable** : `num_ctx` quand le prompt occupe déjà plus de 70 % de la fenêtre, `num_predict` sinon.
- ⚙️ Presets HÉLIOS NOIR : `num_ctx` porté de 4 096 à **16 384**, `num_predict` de 700 à **1 400**.

---

## [1.11.9] — 2026-09 — Fil resserré, troncature signalée

### Corrigé
- 🛠️ **Plus aucune ligne vide dans le fil.** La 1.11.8 en gardait une entre deux blocs ; sur un message de COD structuré en rubriques, cela suffisait à étirer une seule réponse sur deux écrans, là où l'opérateur de terrain — qui rédige en puces serrées — tenait en dix lignes. Les blocs de code gardent les leurs. Constante `LIGNES_VIDES_MAX` pour revenir à l'aéré d'avant.
- ➕ **Une réponse tronquée le dit.** Après ses deux relances automatiques, d-IA pouvait encore rendre un texte coupé — parfois en plein mot — sans que rien ne le signale. Une consigne tronquée ressemble à une consigne complète : en exercice, c'est une information perdue à l'insu de tous. Le fil affiche désormais `[Reponse TRONQUEE au budget de tokens (num_predict = 700) - fin recue : « ... » ]` avec la marche à suivre.

---

## [plugin meteo_3x30 2.1] — 2026-09 — Le relevé se rafraîchit tout seul

### Ajouté
- ➕ **Rafraîchissement automatique d'un relevé périmé.** Au-delà de 90 minutes, le plugin ne se contente plus d'écrire « relancer le collecteur » : il **relance l'acquisition** et l'annonce (`relevé météo vieux de 93 min - acquisition relancée automatiquement sur Melun`). Attendre d'un modèle qu'il joue le rôle d'une tâche planifiée n'est pas raisonnable — il lit « vieux de 90 min » comme une information, pas comme une consigne. C'est au plugin de tenir ses données à jour.
- 🛡️ **La règle des 2 secondes est intacte** : `collect()` ne va toujours pas sur le réseau, il *démarre* une acquisition en tâche de fond et rend la main aussitôt (mesuré : moins de 0,5 s). Garde-fous : une seule relance par site et par tranche de 10 minutes, et aucune si une acquisition est déjà en cours.

---

## [1.11.8] — 2026-09 — On voit enfin que ça travaille

### Ajouté
- ➕ **Barre de progression et témoin d'activité**, sous les boutons Démarrer / Pause / Arrêter. Un modèle local met 5 à 30 secondes à répondre ; jusqu'ici, seule une ligne discrète changeait dans le panneau de droite, et l'opérateur pouvait croire l'application figée — puis cliquer une seconde fois. Une barre animée et un libellé en gras nomment désormais **ce qui travaille et depuis combien de temps** : `LLM1 reflechit... 12 s`, `Attente fin lecture vocale 3 s`, `Attente : RELEVE_AGE_MIN < 2  45 s`, `Question au LLM1 (mistral-nemo:12b) 8 s`.
- ⚙️ Le chronomètre repart **à chaque étape** : on lit la durée de l'étape en cours, pas le total depuis le démarrage. La barre s'arrête d'elle-même sur les états de repos (*Prêt, Arrêté, Terminé, En pause, a répondu*), et le témoin de la question directe au LLM1 s'éteint dans un `finally` — quelle que soit la manière dont la requête se termine.
- ⚙️ La barre reste **toujours en place**, y compris au repos : un témoin qui apparaît et disparaît déplace les boutons voisins et déroute plus qu'il n'aide.

---

## [1.11.7] — 2026-09 — Formule de passage de parole conforme au trafic

### Modifié
- ⚙️ **« À vous, parlez. » remplace « Rendez la main ».** En simulation ADRASEC, les modèles terminaient leur message par une formule qui n'existe pas en procédure radio. Les gabarits de Jeu de Rôle imposent désormais la formule de trafic réelle — c'est celle que les opérateurs doivent entendre et reproduire à l'entraînement. En jeu de rôle de **fiction**, le narrateur continue de finir par une question ouverte (« Que fais-tu ? ») : la formule est choisie par `jdr_profil["contexte"]`, et le mode recherche n'est pas concerné.

---

## [1.11.6] — 2026-09 — Le fil ne s'étire plus en lignes vides

### Corrigé
- 🛠️ **Les lignes vides inutiles sont compactées à l'affichage.** Un modèle aère sa rédaction ; un message de COD structuré en rubriques pouvait comporter quatre lignes vides d'affilée, au point qu'une seule réponse ne tenait plus à l'écran. Toute suite de lignes vides est réduite à **une**, et celles du début et de la fin du message sont retirées. Les blocs de code ``` ``` sont laissés intacts, l'indentation et les blancs y étant signifiants. **Seul l'affichage change** : la mémoire, les exports, la synthèse vocale et la détection des directives voient toujours le texte d'origine.

---

## [1.11.5] — 2026-09 — En mode preset, le persona écrasait la syntaxe

### Corrigé
- 🛠️ **Une demande de mesure disparaissait dans le style du scénario.** Un COD ADRASEC rédige son message en rubriques — `ACCUSE RECEPTION :`, `DIRECTIVE :`, `MESURE :` — chaque titre seul sur sa ligne, le contenu en dessous. Le modèle écrivait donc `MESURE :` puis, à la ligne, `releve_meteo_maintenant(lieu=nangeville) (urgence feux de vegetation)` : un mot-clé sans appel, puis un appel sans mot-clé, dont aucune ligne n'était une directive. Deux tolérances, toutes deux bornées : un **mot-clé seul sur sa ligne** est recollé à la ligne utile suivante (jamais à une autre rubrique, jamais à du vide) ; un **commentaire libre** est admis après un appel **entre parenthèses** — sans parenthèses, la ligne doit toujours se terminer là, faute de quoi « ACTION: mesurer la temperature du local » deviendrait une commande.
- ⚙️ Le catalogue injecté dans le prompt demande explicitement de ne pas employer `ACTION` ou `MESURE` comme titre de rubrique.

> ⚠️ Cette tolérance accroît la surface d'exécution en mode Jeu de Rôle, où le scénario **est** fait de consignes d'action. La parade reste celle du chapitre 7 du mémo : `"plugins_actions_mode": "off"` dans les presets d'exercice, et pas de plugin de commande matérielle dans `plugins_dia\` pendant les séances.

---

## [1.11.4] — 2026-09 — Une directive habillée en Markdown est reconnue

### Corrigé
- 🛠️ **Une directive mise en forme par le modèle était ignorée en silence.** Le motif exigeait le mot-clé en tout début de ligne ; or les modèles habillent volontiers ce qu'ils prennent pour du code ou pour une consigne : `` `ACTION: mesure_meteo(lieu=melun)` ``, `**ACTION:** mesure_meteo(...)`, `- ACTION: ...`, `> ACTION: ...`. Aucune de ces quatre formes n'était exécutée — et le modèle répondait ensuite qu'il attendait toujours un résultat qui ne viendrait jamais. La **décoration de bordure** (accents graves, étoiles, soulignés, puces, chevrons, tildes) est désormais absorbée de part et d'autre du mot-clé. La garde de fond est inchangée : mot-clé **en majuscules**, deux-points, identifiant, et rien d'autre sur la ligne — une phrase de prose ne peut toujours pas devenir une commande (7 formulations de prose vérifiées, dont `action:` en minuscules et « Le COD demande une ACTION : envoyer une équipe »).

---

## [plugin meteo_3x30 2.0] — 2026-09 — Un fichier de relevés par site

### Ajouté
- ➕ **Un relevé par site** : `meteo_releves_melun.json`, `meteo_releves_provins.json`… Deux mesures successives ne s'écrasent plus, ce qui rend la **comparaison entre communes** possible dans un même tour de dialogue.
- ➕ Variable **`METEO_AUTRES_SITES`** : une ligne de résumé par site déjà relevé (`melun T 15.9 C vent 2.5 km/h HR 92 % 3x30 0/3 (4 min)`), du plus récent au plus ancien. Le site que l'on vient de mesurer garde le détail complet ; les autres restent visibles et comparables.
- ➕ Collecteur v1.2 : option **`--site melun`**, qui reprend la table `SITES` du plugin — elle fixe les coordonnées **et** écrit dans le fichier du site. Une tâche planifiée par commune suivie : `--site melun --boucle 900`.

### Modifié
- ⚙️ Les variables de fond de tableau (`SITES_METEO`, `METEO_AUTRES_SITES`) sont publiées **en dernier** : si d-IA tronque à 12 variables, ce sont elles qui sautent, jamais le résultat de la mesure.
- ✅ **Compatibilité** : une installation d'avant la 2.0 continue de fonctionner. En l'absence de fichier par site, le plugin retombe sur `meteo_releves.json` — mais seulement si son `lieu` correspond au site demandé.

---

## [1.11.3] — 2026-09 — Le balisage retiré ne doit pas être du contenu

### Corrigé
- 🛠️ **L'assainissement des valeurs de plugin changeait leur sens.** `_assainir_valeur_plugin()` retirait `` ` `` `*` `_` `#` `>` `|` de toute valeur, pour que les modèles n'imitent pas du Markdown. Deux de ces caractères sont du contenu : le **souligné** — « acquisition en cours, attendre RELEVE_AGE_MIN < 2 » arrivait dans le prompt sous la forme « attendre RELEVEAGEMIN < 2 », un nom de variable inexistant que le modèle recopiait ensuite dans une directive impossible à satisfaire — et le **chevron** — le rappel de règle « T >= 30 C ET vent >= 30 km/h » devenait « T = 30 C ET vent = 30 km/h », soit un seuil minimal transformé en égalité. Seuls `` ` `` `*` `|` sont désormais retirés partout ; `>` et `#` uniquement en **début** de valeur, là où ils ouvriraient une citation ou un titre. Le souligné n'est plus touché — l'affichage ne le mange plus depuis la 1.11.2.

---

## [plugin meteo_3x30 1.8] — 2026-09 — Une variable se suffit à elle-même

### Corrigé
- 🛠️ **`mesure_meteo` ignorait le paramètre `lieu=`.** On demandait Melun, l'action relisait le dernier relevé — celui de Nangeville — et le publiait tel quel : `LIEU_METEO = Nangeville`. Le modèle, à juste titre, répondait qu'il n'avait pas de données pour Melun. `mesure_meteo(lieu=<site>)` résout désormais le site, et si le relevé disponible concerne un **autre** lieu, il **ne publie aucune de ses valeurs** : il lance l'acquisition du site demandé et le dit (`ATTENDRE: RELEVE_AGE_MIN < 2 delai=300`). Attribuer à une commune des mesures faites ailleurs, sur une règle de danger de feu, n'est pas une approximation acceptable.
- 🛠️ Relevé du bon site mais vieillissant (au-delà de `AGE_FRAIS_MIN` = 20 min) : les valeurs sont rendues — elles sont vraies, seulement datées — avec leur ancienneté et un rafraîchissement lancé en arrière-plan.

### Ajouté
- ➕ Variable `LIEU_DEMANDE` : le site visé par la dernière action de mesure, distinct de `LIEU_METEO` qui reste le lieu du relevé effectivement lu.
- 🛠️ **Les seuils sont publiés avec les valeurs.** `CRITERES_3X30` donnait la valeur et le verdict (`humidite 62 % non`) mais pas le critère : le modèle en a fabriqué un pour justifier une conclusion par ailleurs exacte — « la règle n'est pas remplie car l'humidité est inférieure à 80 % », un seuil qui n'existe nulle part. `REGLE_3X30` rappelle désormais la règle complète et chaque critère porte son seuil (`humidite 62 % (seuil <= 30) non`). Le verdict était juste, c'est le raisonnement affiché qui était faux — et en formation, c'est le raisonnement que le stagiaire retient.
- 🛠️ **Une attente sans objet ne peut plus se produire.** Un relevé du bon site vieux de 16 min était jugé « assez frais » : aucune acquisition n'était lancée, et le modèle — à qui le catalogue prescrivait d'attendre `RELEVE_AGE_MIN < 2` — scrutait pendant 600 s un compteur qui ne pouvait que monter, pour finir sur un échec alors que la mesure figurait déjà dans sa première ligne. Trois corrections : `MESURE_RESULTAT` dit désormais dans lequel des deux cas on se trouve (« acquisition en cours, attendre… » ou « valeurs déjà à jour, répondre maintenant, ne pas attendre »), le catalogue prescrit de **lire** `MESURE_RESULTAT` au lieu d'attendre systématiquement, et le seuil de fraîcheur passe de 20 min à **2 min** — une requête réseau de plus coûte moins cher que dix minutes de séance.
- 🛠️ **Vent et rafales publiés avec une décimale**, comme la température. `VENT_KMH = 20` arrondi à l'entier laissait le modèle « compléter » de lui-même : il restituait « 20,1 km/h », une décimale qu'aucune source n'avait fournie. Une valeur publiée doit être exactement celle de la mesure.
- ➕ Le catalogue d'actions énonce que `mesure_meteo` fournit **ensemble** température, vent, humidité et règle 3 × 30 — les petits modèles locaux inventaient `MESURE: temperature`, `MESURE: vent`, `MESURE: humidite`, correctement rejetées mais coûteuses en tours.

---

## [1.11.1] — 2026-09 — La question au LLM1 voit les plugins

### Corrigé
- 🛠️ **La question directe au LLM1 était aveugle aux plugins.** Son prompt était construit à part, sans le bloc `{variables}`, et sa réponse n'était pas passée au traitement des directives : demander « relève la météo » au LLM1 ne déclenchait rien, et le modèle répondait sur des valeurs imaginaires.

### Modifié
- ⚙️ **Extraction d'une classe `MoteurPlugins`**, utilisée par la boucle de dialogue ET par les appels hors dialogue : variables, actions, mesures et attentes n'ont plus qu'une implémentation. La classe ne connaît ni les modèles ni la GUI — le contexte arrive par des fonctions de rappel (`emit`, `running`, `paused`, `contexte`, `confirmer`).
- ⚙️ `DialogueEngine` conserve toutes ses méthodes et ses attributs historiques (`plugin_vars`, `plugin_bloc`, `session_vars`, `actions_mode`, `_maj_variables_plugins`, `_notifier_plugins_message`, `_traiter_directives`) : ce sont désormais des délégations. Rien à changer dans les presets, les plugins ou les habitudes.

### Ajouté
- ➕ **Relance automatique de la question au LLM1** : si la réponse contenait des directives qui ont produit un résultat (mesure obtenue, attente satisfaite), d-IA réinterroge le modèle **une** fois avec les données fraîches et **sans le catalogue d'actions**, pour qu'il réponde à la question au lieu de redemander une acquisition.
- ➕ L'attente d'une question au LLM1 est interruptible par Échap, et la validation des actions en mode `confirmer` s'ouvre correctement depuis le thread de travail.

---

## [1.11.0] — 2026-09 — Le LLM agit, mesure et attend

### Ajouté
- ➕ **Plugins actifs aussi en mode RECHERCHE** : le bloc `{variables}` est désormais injecté dans les gabarits du dialogue scientifique (Investigateur, Analyste, Modérateur, question initiale), et plus seulement en mode Jeu de Rôle. Un dialogue de recherche raisonne enfin sur des mesures réelles.
- ➕ **Actions et mesures demandées par les LLM** : un plugin déclare `list_actions()` / `execute_action(action_id, params, ctx)` — **même contrat que les plugins IAbrain** (tuples à 3 éléments). d-IA injecte le catalogue dans le prompt, et le modèle appelle une action en écrivant une directive **seule sur sa ligne** :
  - `ACTION: allumer_lampe(zone=serre1)` — agir sur du matériel ;
  - `MESURE: mesure_meteo()` — relever une grandeur.

  Le résultat devient une variable, donc il est relu par les trois LLM au tour suivant.
- ➕ **Attente d'une mesure ou d'un état** : `ATTENDRE: TEMPERATURE_C >= 30 delai=600` suspend le dialogue et fait scruter la condition (un `collect()` toutes les `PLUGIN_ATTENTE_POLL_S` secondes) jusqu'à satisfaction ou expiration. Opérateurs : `>`, `>=`, `<`, `<=`, `=`, `!=`, `contient`. L'issue est réinjectée dans `ATTENTE_RESULTAT`.
- ➕ **Trois modes d'exécution** (clé `plugins_actions_mode`, menu *Plugins E/S → Actions demandées par les LLM*) : `auto` (défaut), `confirmer` (boîte de dialogue avant chaque action) et `off` (directive journalisée, rien n'est exécuté).
- ➕ **Plugin livré `meteo_3x30.py`** : injecte température, vent, rafales et humidité du modèle **AROME France HD** (Météo-France, via Open-Meteo) et l'état de la **règle des 3 × 30** (T ≥ 30 °C, vent ≥ 30 km/h, HR ≤ 30 %). Il réutilise `meteo_lib.py` de TCQ quand elle est accessible : une seule implémentation de la règle pour TCQ et pour d-IA. Livré avec son collecteur `meteo_3x30_collecte.py` (acquisition réseau séparée, options `--simuler` et `--boucle`).
- ➕ Clés `plugins_actions_mode` et `plugins_attente_max_s` persistées dans `d-ia_setup.json` et transportées par les presets.

### Garde-fous
- 🛡️ **Le timeout de 2 s par appel de plugin reste intact** : une attente longue est une suite d'appels courts, jamais un appel bloquant. Une action dispose d'un budget propre (10 s), et l'acquisition réseau se fait toujours dans un programme tiers.
- 🛡️ **Directives en MAJUSCULES, seules sur leur ligne** : une phrase de prose (« le COD demande une action : allumer le groupe ») n'est jamais confondue avec une commande.
- 🛡️ **Trois directives au maximum par message**, catalogue d'actions plafonné, paramètres bornés, délai d'attente plafonné (`plugins_attente_max_s`, 15 min par défaut).
- 🛡️ **Attente interruptible** : Pause et Arrêter restent réactifs pendant toute la scrutation.
- 🛡️ **Anti-répétition** : un même message de plugin n'est pas réémis dans le fil avant 10 minutes — une attente longue sur un capteur muet ne noie plus la main courante.
- 🛡️ En mode `confirmer`, une demande sans réponse au bout de 120 s est **refusée** : le silence ne vaut pas accord quand il s'agit de piloter du matériel.

### Comportement
- ⚠️ Un preset d'exercice FICTIF a tout intérêt à imposer `"plugins_actions_mode": "off"` : une consigne de jeu ne doit jamais actionner du matériel réel.
- ⚠️ Plugins décochés : comportement strictement identique à la v1.9.

---

## [1.10.0] — 2026-09 — Plugins d'entrées-sorties

### Ajouté
- ➕ **Système de plugins Python** : d-IA charge au démarrage les fichiers `.py` déposés dans le dossier **`plugins_dia/`** (à côté de l'exe ou du script). Même philosophie que les plugins IAbrain v1.40.7+, adaptée à une boucle de dialogue.
- ➕ **Variables d'ENTRÉE** (`collect(ctx)`) : appelées avant chaque prise de parole, elles alimentent un nouveau bloc **`{variables}`** injecté dans les trois gabarits JdR (narrateur, joueur, injecteur) et dans l'ouverture de simulation — « DONNEES DE SITUATION ». Le COD, l'opérateur et la cellule d'animation raisonnent enfin sur des relevés réels.
- ➕ **Hook de SORTIE** (`on_message(msg, ctx)`) : appelé après chaque prise de parole (LLM **et** opérateur humain en mode CHAT). Permet d'écrire un fichier, de noter un SITREP, de piloter un équipement ; un dict retourné est réinjecté dans les variables du tour suivant (rétroaction).
- ➕ **Variables de session manuelles** : menu *Plugins E/S → Variables de session…*, une variable par ligne au format `NOM = valeur` (équivalent du `/set` d'IAbrain). Elles **priment** sur les valeurs des plugins et sont prises en compte à chaud, en pleine séance.
- ➕ **Menu « Plugins E/S »** : activation, éditeur de variables, **Diagnostic plugins** (rapport de chargement, variables déclarées, erreurs, valeurs du dernier tour), rechargement à chaud, ouverture du dossier.
- ➕ **Trois plugins livrés** : `exemple_minimal.py` (squelette), `propagation_vars.py` (Kp / état NVIS / SFI / autonomie depuis un fichier de relevés, alimentable par GEOMAG-Observer), `sitrep_scoring.py` (notation de forme des SITREP sur 20, CSV de RETEX, défaut réinjecté dans la simulation).
- ➕ Réglage **persisté** dans `d-ia_setup.json` et **transporté** par les presets `.diapreset.json` (clés `plugins_actifs` et `session_vars`).

### Garde-fous
- 🛡️ **Timeout de 2 s par appel** + isolation `try/except` : un plugin lent ou cassé est neutralisé sans jamais figer le dialogue. Deux dépassements consécutifs le désactivent pour la séance.
- 🛡️ **Repli vide systématique** (même contrat que la recherche web) : pas de plugin, pas de donnée, pas de bloc — le prompt redevient celui de la v1.9. Utilisable en exercice de black-out.
- 🛡️ **Assainissement des valeurs** : texte d'une seule ligne, sans markdown, 160 caractères par valeur, 12 variables, bloc plafonné à 800 caractères pour ne pas dévorer la fenêtre de contexte.
- 🛡️ Un plugin à la syntaxe invalide est signalé dans le rapport de chargement et **n'empêche pas d-IA de démarrer**. Désactivation par simple renommage en `.py.disabled`.

### Comportement
- ⚠️ Case décochée ou dossier `plugins_dia/` vide : comportement **strictement identique** à la v1.9.0.

---

## [1.5.0] — 2026-06 — Créativité & innovation pilotables

### Ajouté
- ➕ **Curseur « Créativité / innovation » (0–100 %)** (colonne de gauche → Paramètres avancés) qui pousse d-IA à **proposer de nouveaux concepts** à partir de la requête initiale.
- ➕ **Double levier piloté par le curseur** :
  - *Échantillonnage* — boost **additif** de `température` (jusqu'à +0,6, plafonné à 1,5) et de `top_p` (0,90 → 0,98), par-dessus les températures par-LLM existantes.
  - *Prompts* — **directive d'innovation graduée et adaptée au rôle** :
    - 🔬 **Investigateur** : reste bref, **au plus une** piste concise avant sa question (il ne développe pas).
    - 🧠 **Analyste** : moteur à concepts, développe **1 à 3 pistes** au niveau élevé, avec évaluation critique.
    - 🆕 **Modérateur** : pousse à rendre une piste **concrète et chiffrée** (convergence), boost réduit de moitié.
- ➕ Pistes préfixées **`PISTE INNOVANTE :`**, signalées **exploratoires** et suivies d'une **évaluation critique** (faisabilité, ordres de grandeur, conditions de validité).
- ➕ **Budget de tokens (`num_predict`) adaptatif** : croît avec la créativité (≈ ×1 à ×2,5, plafonné et borné par la fenêtre de contexte) pour **éviter la troncature** des réponses multi-concepts. Le modérateur conserve un budget court.
- ➕ Réglage **persisté** dans `d-ia_setup.json` et **transporté** par les presets `.diapreset.json` (clé `creativite`).

### Amélioré
- 🛠️ **Fenêtre Paramètres IA défilante** : chaque onglet (IA 1/2/3, Mode ADRASEC, Synthèse vocale) est désormais scrollable (molette + barre). Plus rien n'est coupé en bas sur les petits écrans ; les boutons « Fermer » / « Tester » restent ancrés en bas.
- 🛠️ **Colonne de configuration défilante** (sujet, thèmes, paramètres avancés, recherche web). Les boutons **Démarrer / Pause / Arrêter** restent fixes en haut ; les zones de texte (sujet, thèmes) gardent leur propre défilement.

### Garde-fou
- 🛡️ **ADRASEC** : une spéculation n'est **jamais** présentée comme un fait — la créativité propose des concepts *à explorer*, elle n'invente pas de certitudes.

### Comportement
- ⚠️ À **0 %** de créativité : directive vide, échantillonnage et budget **inchangés** — comportement strictement identique à la v1.4.

### Corrigé
- 🛠️ Troncature des réponses en plein milieu à forte créativité (cause : `num_predict` figé à 512) — résolue par le budget adaptatif.
- 🛠️ Investigateur qui se transformait en brainstormeur (plusieurs `PISTE INNOVANTE` au lieu d'une question) — résolu par la directive adaptée au rôle.

---

## [1.4.0] — 2026-06 — Rendu Markdown du dialogue & voix assainie

### Ajouté
- ➕ **Rendu Markdown** dans la zone de conversation : **gras**, *italique*, `code` et blocs de code, titres, citations, listes (puces et numérotées), liens et barré sont **interprétés et affichés proprement** (plus de balises brutes à l'écran).
- ➕ **Nettoyage TTS renforcé** : les artefacts Markdown (antislash `\`, `***`, `` ` ``, `#`, `>`, `|`, puces, liens…) sont retirés **avant lecture** — SAPI5 ne les prononce plus.

### Préservé
- 🛠️ Le `snake_case` technique (ex. `IAbrain_rag`) est **conservé** à la lecture vocale (seuls les underscores d'emphase en bordure de mot sont retirés).

### Technique
- ⚙️ Parseur Markdown **maison**, **sans dépendance externe** — compatible autonomie hors-ligne et PyInstaller `--onedir`.

---

## [1.3.0] — 2026-06 — Enrichissement par le web & auto-export IAbrain

### Ajouté
- ➕ **Enrichissement par le web de l'Investigateur** : le LLM1 interroge le web avant son tour et synthétise 2-3 sources en français, avec esprit critique.
- ➕ Deux fournisseurs interchangeables : **DuckDuckGo** (sans installation, `urllib` seul) et **SearXNG** (auto-hébergé, souverain).
- ➕ Recherche **throttlée** (1 / N tours), **dédupliquée par thème**, à **repli hors-ligne** (inerte sans réseau ou désactivée).
- ➕ **Auto-export des fiches vers IAbrain** au fil de l'eau, dans une zone de **staging `_a_valider/`** (relecture humaine avant exploitation).
- ➕ Détection automatique de l'emplacement d'IAbrain ; régénération de l'`_INDEX.md` par domaine.
- ➕ Persistance des nouveaux paramètres dans `d-ia_setup.json` et transport dans les presets.

---

## [1.2.0] — 2026-05 — Modérateur conversationnel & presets

### Ajouté
- ➕ **Modérateur conversationnel** : un 3ᵉ LLM intervient dans le fil tous les K tours (bilan + recadrage + consigne de convergence) — la conversation **aboutit à une solution**.
- ➕ Intervention **réinjectée** dans le contexte des deux IA (rétroaction → convergence).
- ➕ **Compatible avec le modérateur RAG** : parler et ficher en même temps.
- ➕ Section « Modérateur conversationnel » dans l'onglet Mode ADRASEC (activation, fréquence K, température, objectif de convergence).
- ➕ Affichage **vert** dédié au modérateur ; gestion dans les exports JSON / Markdown / RTF.
- ➕ **Presets de sujet** : Importer / Exporter / Aperçu ; format natif `.diapreset.json` + import du format texte.
- ➕ Preset d'exemple « Communication par ondes gravitationnelles ».

### Amélioré
- 🛠️ Garde-fou langue appliqué aussi au modérateur ; persistance complète des nouveaux paramètres.

---

## [1.1.0] — 2026-05 — Modérateur RAG ADRASEC

### Ajouté
- ➕ **Modérateur RAG** : un 3ᵉ LLM extrait des fiches structurées (JSON) du dialogue en arrière-plan.
- ➕ **Mode ADRASEC enrichi** : activation via case à cocher, fréquence d'extraction configurable.
- ➕ Onglets « IA 3 - Modérateur » et « Mode ADRASEC » dans Paramètres IA.
- ➕ **Synthèse finale** déclenchée automatiquement au clic Arrêter.
- ➕ **Parseur JSON robuste** tolérant aux artefacts LLM ; détection de troncature.
- ➕ Format de stockage `rag_adrasec.json` portable ; **intégration IAbrain**.

---

## [1.0.0] — 2026-05 — Première version stable

### Ajouté
- ➕ Dialogue entre deux LLM avec rôles asymétriques (Investigateur / Analyste).
- ➕ Thèmes secondaires guidés, mémoire à fenêtre glissante, détection de dérive linguistique.
- ➕ Synthèse vocale SAPI5 deux voix avec synchronisation dialogue/voix.
- ➕ Déblocage des voix OneCore Windows 10/11.
- ➕ Export JSON / Markdown / RTF.
- ➕ Configuration persistante avec offuscation base64 des clés API.
- ➕ Support Ollama local et cloud.

---

*Auteur : Jean-Louis (F1GBD) — ADRASEC 77 / FNRASEC.*
