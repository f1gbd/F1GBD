/* =========================================================================
 * osjt_lora_frame.h — protocole radio OSJT, partage noeud / passerelle
 * =========================================================================
 * Version de protocole 1.
 *
 * Ce fichier est la SEULE definition de la trame. Le noeud l'emet, la
 * passerelle la decode, et le decodeur Python de GEOMAG-Observer en rejoue
 * la structure a l'identique dans son autotest. Toute modification ici doit
 * etre repercutee dans osjt_lora_selftest() cote Python, sinon le flux
 * devient muet sans le moindre message d'erreur — c'est exactement la panne
 * que l'autotest existe pour rendre impossible.
 *
 *
 * POURQUOI ON N'EMET PAS EN TEMPS REEL
 * ------------------------------------
 * La sous-bande g1 (868,0-868,6 MHz) est limitee a 1 % de rapport cyclique
 * par l'ERC 70-03. Une trame par seconde, meme minuscule, demanderait 6 %
 * au SF7 : illegal d'un facteur six.
 *
 * On groupe donc la minute. Et la physique aide : l'indice K est une
 * statistique de PLAGE sur des blocs de trois heures, calculee a partir de
 * valeurs minute. En transmettant la moyenne minute exacte, plus le min et
 * le max de chaque axe dans la minute, l'indice K est calcule SANS AUCUNE
 * PERTE — identique au bit pres a ce qu'aurait donne une liaison filaire.
 *
 * Ce qu'on perd est la finesse de l'oscillogramme : 4 s au lieu de 1 s, et
 * une minute de latence. Pour un observatoire geomagnetique, c'est
 * rigoureusement sans consequence.
 *
 *
 * TROIS TYPES DE TRAME, ET POURQUOI
 * ---------------------------------
 * Le budget de 1 % impose un compromis entre portee et contenu :
 *
 *   trame      octets   SF7      SF8      SF9
 *   COMPACT      42     0,15 %   0,26 %   0,48 %
 *   FULL 10      92     0,26 %   0,48 %   0,86 %
 *   FULL 15     132     0,37 %   0,65 %   1,16 %  <-- hors limite
 *
 * Le noeud choisit donc son type TOUT SEUL en fonction du facteur
 * d'etalement, plutot que de laisser l'operateur configurer une
 * combinaison illegale. Au SF9 et au-dela, la forme d'onde saute et seule
 * la statistique minute passe : c'est la bonne priorite, puisque c'est elle
 * qui porte l'indice K.
 *
 * La trame ALARME est une COMPACT emise hors cadence sur franchissement de
 * dB/dt. Meme au SF9, 0,48 + 0,48 = 0,96 % : le budget tient encore.
 *
 *
 * UNITES
 * ------
 * Moyenne minute   : milli-nT ABSOLUS, en int32. Plage +-2 147 483 nT.
 * Ecarts et min/max: deci-nT RELATIFS a la moyenne, en int16. Plage
 *                    +-3276,7 nT, resolution 0,1 nT.
 *
 * 0,1 nT est tres en dessous du pas du capteur (3,39 nT/LSB a CC=800), et
 * meme en dessous du bruit residuel apres moyennage — la quantification ne
 * coute donc rien. La plage de +-3276 nT couvre le plus violent des orages :
 * un K9 vaut 500 nT sur TROIS HEURES, l'ecart a la moyenne DANS UNE MINUTE
 * n'en approche jamais le dixieme.
 *
 * Copyright 2026 F1GBD / F4JHW — ADRASEC 77 — Licence MIT
 * ========================================================================= */

#ifndef OSJT_LORA_FRAME_H
#define OSJT_LORA_FRAME_H

#include <stdint.h>
#include <string.h>

/* Octets 4A 4C dans le flux, soit "JL". Distinct de la magie 0x4A53 de la
 * trame serie Teensy : les deux protocoles ne doivent jamais se confondre
 * si un cable est branche au mauvais endroit. */
#define OSJT_LORA_MAGIC   0x4C4A
#define OSJT_LORA_VER     1

/* Types de trame */
#define OSJT_LF_FULL      1   /* statistique minute + forme d'onde */
#define OSJT_LF_COMPACT   2   /* statistique minute seule */
#define OSJT_LF_ALARM     3   /* COMPACT hors cadence, dB/dt franchi */
#define OSJT_LF_STATUS    4   /* etat du noeud, une fois par heure */

/* Nombre maximal d'echantillons de forme d'onde dans une trame FULL. */
#define OSJT_LF_MAXSAMP   15

/* Drapeaux */
#define OSJT_FLAG_TXBLANK   (1u << 0)  /* la minute contient une salve TX */
#define OSJT_FLAG_ALARM     (1u << 1)  /* seuil dB/dt franchi */
#define OSJT_FLAG_SAT       (1u << 2)  /* saturation capteur */
#define OSJT_FLAG_NOTEMP    (1u << 3)  /* pas de sonde de temperature */
#define OSJT_FLAG_SHORTMIN  (1u << 4)  /* minute incomplete */
#define OSJT_FLAG_DUTYHOLD  (1u << 5)  /* emission retenue, budget epuise */
#define OSJT_FLAG_BATLOW    (1u << 6)  /* batterie faible */

#pragma pack(push, 1)

/* En-tete commun — 16 octets */
typedef struct {
  uint16_t magic;     /* OSJT_LORA_MAGIC */
  uint8_t  ver;       /* OSJT_LORA_VER */
  uint8_t  type;      /* OSJT_LF_* */
  uint8_t  node;      /* identifiant de noeud, 1..254 */
  uint8_t  nsamp;     /* echantillons de forme d'onde, 0 si COMPACT */
  uint16_t seq;       /* numero de minute, boucle a 65536 */
  uint32_t t_ms;      /* millis() du noeud au CENTRE de la minute */
  int16_t  temp_cC;   /* temperature x100 ; -32768 = absente */
  uint16_t flags;     /* OSJT_FLAG_* */
} OsjtLoraHdr;

/* Statistique de la minute — 24 octets */
typedef struct {
  int32_t mean_mnT[3];  /* moyenne minute, milli-nT absolus, X Y Z */
  int16_t min_dnT[3];   /* min de la minute, deci-nT relatifs a la moyenne */
  int16_t max_dnT[3];   /* max de la minute, idem */
} OsjtLoraStat;

#pragma pack(pop)

/* Tailles utiles. Le CRC-16 occupe les deux derniers octets et couvre tout
 * ce qui precede, magie comprise. */
#define OSJT_LF_HDR_LEN     16
#define OSJT_LF_STAT_LEN    24
#define OSJT_LF_CRC_LEN     2
#define OSJT_LF_COMPACT_LEN (OSJT_LF_HDR_LEN + OSJT_LF_STAT_LEN + OSJT_LF_CRC_LEN)
#define OSJT_LF_FULL_LEN(n) (OSJT_LF_COMPACT_LEN + (n) * 6)
#define OSJT_LF_MAX_LEN     OSJT_LF_FULL_LEN(OSJT_LF_MAXSAMP)

/* CRC-16/CCITT-FALSE. Identique au firmware Teensy et au Python.
 * Verification canonique : "123456789" -> 0x29B1. */
static inline uint16_t osjt_crc16(const uint8_t *d, uint16_t n) {
  uint16_t c = 0xFFFF;
  while (n--) {
    c ^= (uint16_t)(*d++) << 8;
    for (uint8_t i = 0; i < 8; i++)
      c = (c & 0x8000) ? (uint16_t)((c << 1) ^ 0x1021) : (uint16_t)(c << 1);
  }
  return c;
}

/* Longueur attendue d'une trame d'apres son en-tete, 0 si incoherente. */
static inline uint16_t osjt_lf_len(const OsjtLoraHdr *h) {
  if (h->magic != OSJT_LORA_MAGIC || h->ver != OSJT_LORA_VER) return 0;
  switch (h->type) {
    case OSJT_LF_COMPACT:
    case OSJT_LF_ALARM:
    case OSJT_LF_STATUS:
      return h->nsamp ? 0 : OSJT_LF_COMPACT_LEN;
    case OSJT_LF_FULL:
      if (h->nsamp == 0 || h->nsamp > OSJT_LF_MAXSAMP) return 0;
      return OSJT_LF_FULL_LEN(h->nsamp);
    default:
      return 0;
  }
}

/* Validation complete d'une trame recue. */
static inline bool osjt_lf_check(const uint8_t *buf, uint16_t n) {
  if (n < OSJT_LF_COMPACT_LEN || n > OSJT_LF_MAX_LEN) return false;
  OsjtLoraHdr h;
  memcpy(&h, buf, sizeof(h));
  uint16_t want = osjt_lf_len(&h);
  if (want == 0 || want != n) return false;
  uint16_t crc;
  memcpy(&crc, buf + n - 2, 2);
  return osjt_crc16(buf, (uint16_t)(n - 2)) == crc;
}

/* Combien d'echantillons de forme d'onde tiennent dans le budget legal ?
 *
 * On refuse simplement d'emettre ce qui ne passe pas : c'est au firmware de
 * garantir la conformite, pas a l'operateur de la calculer. Rendre 0 revient
 * a dire « au mieux une COMPACT a cette portee ».
 *
 * airtime_ms doit etre fourni par l'appelant pour une trame FULL de n
 * echantillons — RadioLib sait le calculer exactement pour les parametres
 * reels du modem, ce qui vaut mieux qu'une formule recopiee ici. */
static inline uint8_t osjt_lf_fit(uint32_t (*airtime_ms)(uint16_t len),
                                  uint32_t period_s, uint16_t permille) {
  /* Contrainte : airtime / periode <= permille / 1000, donc en
   * millisecondes  airtime_ms <= period_s * permille. */
  const uint32_t budget_ms = period_s * (uint32_t)permille;
  for (int8_t n = OSJT_LF_MAXSAMP; n > 0; n -= 5)
    if (airtime_ms(OSJT_LF_FULL_LEN(n)) <= budget_ms)
      return (uint8_t)n;
  return 0;   /* meme une FULL de 5 echantillons ne passe pas : COMPACT */
}

#endif /* OSJT_LORA_FRAME_H */
