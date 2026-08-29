/* =========================================================================
 * node.cpp — la tete magnetique : RM3100 + SX1262, dans le tube
 * =========================================================================
 *
 * Elle accumule une minute d'echantillons, en tire la moyenne, le min et le
 * max de chaque axe, y ajoute une forme d'onde decimee si le budget radio
 * le permet, et emet une trame.
 *
 * LES TROIS CHOSES QUI FONT LA QUALITE DE CETTE TETE
 * --------------------------------------------------
 *
 * 1. LE BLANKING D'EMISSION. Le module est lui-meme une source magnetique :
 *    a 14 dBm le SX1262 tire une soixantaine de milliamperes pendant une
 *    centaine de millisecondes, ce qui produit quelques nT a 10 cm. Mais
 *    contrairement a une liaison Ethernet qui emet en permanence, le
 *    microcontroleur SAIT exactement quand il emet. On jette donc les
 *    echantillons de la fenetre d'emission, marge comprise. Cela represente
 *    0,4 % du temps au SF7. Le probleme disparait completement — c'est
 *    l'avantage decisif du LoRa sur l'Ethernet pour une tete magnetique.
 *
 * 2. LE GARDE-FOU DE RAPPORT CYCLIQUE. La limite de 1 % dans la sous-bande
 *    g1 est une obligation reglementaire, pas une recommandation. Le
 *    firmware tient une comptabilite glissante sur l'heure et REFUSE
 *    d'emettre au-dela, en levant un drapeau plutot qu'en trichant. Une
 *    tete qui deborde son budget est une tete qu'on ne peut pas laisser
 *    tourner sans surveillance.
 *
 * 3. LE CHOIX AUTOMATIQUE DU TYPE DE TRAME. Au SF7 la forme d'onde complete
 *    passe ; au SF9 elle ne passe plus. Plutot que de laisser l'operateur
 *    composer une configuration illegale, le noeud interroge RadioLib sur
 *    le temps d'antenne reel de ses parametres modem et decide seul.
 *
 * Copyright 2026 F1GBD / F4JHW — ADRASEC 77 — Licence MIT
 * ========================================================================= */

#include <Arduino.h>
#include <RadioLib.h>
#include <SPI.h>

#include "osjt_lora_frame.h"
#include "osjt_oled.h"
#include "osjt_pins.h"
#include "rm3100.h"

#ifndef OSJT_TMRC
#define OSJT_TMRC 0x99
#endif
#ifndef OSJT_CYCLE_COUNT
#define OSJT_CYCLE_COUNT 800
#endif

/* Fenetre de garde autour de l'emission, de part et d'autre. */
static const uint32_t TX_GUARD_MS = 60;

/* Duree d'une periode d'agregation. La minute est la maille de l'IAGA-2002
 * et celle de l'indice K : la changer casserait la compatibilite. */
static const uint32_t PERIOD_MS = 60000;

static SPIClass spiRm(FSPI);
static RM3100 mag(spiRm, PIN_RM_CS, PIN_RM_DRDY);
static SX1262 radio = new Module(PIN_LORA_NSS, PIN_LORA_DIO1,
                                 PIN_LORA_RST, PIN_LORA_BUSY);

/* --- accumulateur de la minute ------------------------------------------ */
struct Acc {
  double sum[3];
  float  mn[3], mx[3];
  uint32_t n;
  void reset() {
    for (uint8_t a = 0; a < 3; a++) {
      sum[a] = 0.0;
      mn[a]  = 1e30f;
      mx[a]  = -1e30f;
    }
    n = 0;
  }
  void push(const float *b) {
    for (uint8_t a = 0; a < 3; a++) {
      sum[a] += b[a];
      if (b[a] < mn[a]) mn[a] = b[a];
      if (b[a] > mx[a]) mx[a] = b[a];
    }
    n++;
  }
};

static Acc acc;

/* Forme d'onde decimee : une moyenne partielle par case. */
static const uint8_t MAXW = OSJT_LF_MAXSAMP;
static double waveSum[MAXW][3];
static uint32_t waveN[MAXW];
static uint8_t waveCount = 0;      /* cases reellement utilisees */

static uint16_t seq = 0;
static uint16_t flags = 0;
static uint32_t periodStart = 0;
static bool txBlank = false;

/* Comptabilite d'antenne glissante sur une heure. */
static const uint8_t DUTY_SLOTS = 60;    /* une case par minute */
static uint16_t dutyMs[DUTY_SLOTS];
static uint8_t dutySlot = 0;

static uint32_t airtimeMs(uint16_t len) {
  return (uint32_t)(radio.getTimeOnAir(len) / 1000ULL);
}

static uint32_t dutyUsedMs() {
  uint32_t s = 0;
  for (uint8_t i = 0; i < DUTY_SLOTS; i++) s += dutyMs[i];
  return s;
}

/* Le budget est evalue sur l'heure glissante : 1 % d'une heure vaut 36 s.
 * Raisonner minute par minute serait plus severe que la reglementation et
 * interdirait la trame d'alarme. */
static bool dutyAllows(uint32_t ms) {
  const uint32_t budget = 3600UL * OSJT_DUTY_PERMILLE;   /* ms */
  return dutyUsedMs() + ms <= budget;
}

/* --- emission ------------------------------------------------------------ */
static void sendFrame(uint8_t type, uint8_t nsamp, const float *mean,
                      const float *mn, const float *mx, float tempC) {
  uint8_t buf[OSJT_LF_MAX_LEN];
  OsjtLoraHdr h;
  h.magic   = OSJT_LORA_MAGIC;
  h.ver     = OSJT_LORA_VER;
  h.type    = type;
  h.node    = 1;
  h.nsamp   = nsamp;
  h.seq     = seq;
  h.t_ms    = periodStart + PERIOD_MS / 2;
  h.temp_cC = isnan(tempC) ? -32768 : (int16_t)lroundf(tempC * 100.0f);
  h.flags   = flags;
  memcpy(buf, &h, sizeof(h));

  OsjtLoraStat st;
  for (uint8_t a = 0; a < 3; a++) {
    st.mean_mnT[a] = (int32_t)llroundf(mean[a] * 1000.0f);
    /* min et max en deci-nT RELATIFS a la moyenne : c'est ce qui permet de
     * tenir dans un int16 tout en gardant 0,1 nT de resolution. */
    long dmn = lroundf((mn[a] - mean[a]) * 10.0f);
    long dmx = lroundf((mx[a] - mean[a]) * 10.0f);
    st.min_dnT[a] = (int16_t)constrain(dmn, -32767, 32767);
    st.max_dnT[a] = (int16_t)constrain(dmx, -32767, 32767);
  }
  memcpy(buf + OSJT_LF_HDR_LEN, &st, sizeof(st));

  uint16_t len = OSJT_LF_COMPACT_LEN;
  if (type == OSJT_LF_FULL && nsamp) {
    uint8_t *p = buf + OSJT_LF_HDR_LEN + OSJT_LF_STAT_LEN;
    for (uint8_t i = 0; i < nsamp; i++) {
      for (uint8_t a = 0; a < 3; a++) {
        float v = waveN[i] ? (float)(waveSum[i][a] / waveN[i]) : mean[a];
        long d  = lroundf((v - mean[a]) * 10.0f);
        int16_t s = (int16_t)constrain(d, -32767, 32767);
        memcpy(p, &s, 2);
        p += 2;
      }
    }
    len = OSJT_LF_FULL_LEN(nsamp);
  }
  uint16_t crc = osjt_crc16(buf, (uint16_t)(len - 2));
  memcpy(buf + len - 2, &crc, 2);

  const uint32_t ms = airtimeMs(len);
  if (!dutyAllows(ms)) {
    flags |= OSJT_FLAG_DUTYHOLD;
    return;
  }

  /* La fenetre de blanking encadre l'emission. On la ferme APRES le retour
   * de transmit() : RadioLib rend la main quand le PA est retombe. */
  txBlank = true;
  const uint32_t t0 = millis();
  radio.transmit(buf, len);
  while (millis() - t0 < ms + TX_GUARD_MS) delay(1);
  txBlank = false;

  dutyMs[dutySlot] += (uint16_t)ms;
}


#ifndef OSJT_OLED_BOOT_S
#define OSJT_OLED_BOOT_S 20
#endif

/* --- autotest de mise en service ----------------------------------------
 *
 * Ce qu'on veut savoir avant de descendre la tete dans le tube : est-ce que
 * le capteur repond, est-ce qu'il mesure VRAIMENT le champ terrestre, et
 * est-ce que la radio est initialisee.
 *
 * Le point important est le deuxieme. Un REVID correct prouve seulement que
 * le bus SPI fonctionne : un capteur sature, mal alimente ou dont un axe est
 * coupe repond parfaitement au REVID tout en rendant des valeurs absurdes.
 * On mesure donc pendant huit secondes et on verifie que |F| tombe dans la
 * plage du champ terrestre, et que le bruit reste raisonnable.
 *
 * L'ecran s'eteint ensuite pour de bon, et la premiere minute de mesure
 * commence apres — pas pendant.
 */
static void nodeBootCheck(bool magOk, bool bistOk, bool radioOk) {
  char l1[24], l2[24], l3[24], l4[24];

  osjtOledStatus("GEOMAG-Observer", "Tete magnetique",
                 "version " OSJT_FW_VERSION, "autotest en cours...");
  delay(2000);

  /* Huit secondes de mesure : assez pour une moyenne et un ecart-type
   * significatifs a 10 Hz, assez court pour ne pas lasser l'operateur. */
  double s1 = 0.0, s2 = 0.0;
  uint32_t n = 0;
  const uint32_t t0 = millis();
  while (millis() - t0 < 8000UL) {
    if (mag.dataReady()) {
      float b[3];
      if (mag.read(b[0], b[1], b[2])) {
        double f = sqrt((double)b[0] * b[0] + (double)b[1] * b[1]
                        + (double)b[2] * b[2]);
        s1 += f;
        s2 += f * f;
        n++;
      }
    }
    delay(2);
  }

  double favg = n ? s1 / n : 0.0;
  double var = (n > 1) ? (s2 / n - favg * favg) : 0.0;
  double sd = var > 0.0 ? sqrt(var) : 0.0;

  /* Le champ terrestre va d'environ 23 000 nT a l'equateur magnetique a
   * 66 000 nT aux poles. Hors de cette plage, ce n'est pas le champ qu'on
   * mesure — c'est un capteur sature, mal alimente, ou un axe coupe. */
  const bool fieldOk = (n >= 40) && (favg > 20000.0) && (favg < 70000.0);
  /* Un ecart-type de plus de 50 nT sur huit secondes en interieur signale
   * un cablage instable ou une source parasite immediate. */
  const bool noiseOk = fieldOk && (sd < 50.0);
  const bool allOk = magOk && bistOk && radioOk && fieldOk && noiseOk;

  Serial.printf("# autotest : capteur %s, BIST %s, radio %s\n",
                magOk ? "OK" : "MUET", bistOk ? "OK" : "ECHEC",
                radioOk ? "OK" : "ECHEC");
  Serial.printf("# |F| = %.0f nT, ecart-type %.1f nT sur %lu echantillons\n",
                favg, sd, (unsigned long)n);
  Serial.printf("# VERDICT : %s\n", allOk ? "OPERATIONNEL"
                                           : "DEFAUT - ne pas enterrer");

  if (!magOk)        snprintf(l1, sizeof l1, "CAPTEUR MUET");
  else if (!fieldOk) snprintf(l1, sizeof l1, "MESURE INVALIDE");
  else if (!radioOk) snprintf(l1, sizeof l1, "RADIO KO");
  else if (!noiseOk) snprintf(l1, sizeof l1, "BRUIT ELEVE");
  else               snprintf(l1, sizeof l1, "OPERATIONNEL");

  snprintf(l2, sizeof l2, "|F| %.0f nT", favg);
  snprintf(l3, sizeof l3, "bruit %.1f nT  n=%lu", sd, (unsigned long)n);
  snprintf(l4, sizeof l4, "SF%d  trame %s", OSJT_LORA_SF,
           waveCount ? "FULL" : "COMPACT");
  osjtOledStatus(l1, l2, l3, l4);

  /* On laisse le verdict a l'ecran le temps restant, puis on coupe. */
  const uint32_t shown = millis() - t0 + 2000;
  const uint32_t total = (uint32_t)OSJT_OLED_BOOT_S * 1000UL;
  if (total > shown) delay(total - shown);
  osjtOledOff();
  Serial.println(F("# ecran coupe, debut des mesures."));
}

/* --- API appelee par main.cpp ------------------------------------------- */
void nodeSetup() {
  setCpuFrequencyMhz(OSJT_CPU_MHZ);
  Serial.begin(115200);
  delay(200);
  Serial.printf("# OSJT maghead LoRa %s — noeud\n", OSJT_FW_VERSION);

  spiRm.begin(PIN_RM_SCK, PIN_RM_MISO, PIN_RM_MOSI, PIN_RM_CS);
  bool magOk = mag.begin(OSJT_CYCLE_COUNT, OSJT_TMRC);
  bool bistOk = false;
  if (!magOk) {
    Serial.println(F("# ERREUR : RM3100 muet (REVID). Verifier le cablage."));
  } else {
    bistOk = mag.bist();
    Serial.printf("# RM3100 CC=%d -> %.2f nT/LSB, BIST %s\n",
                  OSJT_CYCLE_COUNT, RM3100::nTPerLsb(OSJT_CYCLE_COUNT),
                  bistOk ? "OK" : "ECHEC");
  }

  SPI.begin(PIN_LORA_SCK, PIN_LORA_MISO, PIN_LORA_MOSI, PIN_LORA_NSS);
  int s = radio.begin(OSJT_LORA_FREQ_HZ / 1e6, OSJT_LORA_BW_KHZ,
                      OSJT_LORA_SF, OSJT_LORA_CR, OSJT_LORA_SYNC,
                      OSJT_LORA_DBM);
  const bool radioOk = (s == RADIOLIB_ERR_NONE);
  if (!radioOk) Serial.printf("# ERREUR SX1262 : %d\n", s);

  osjtOledBegin("Tete magnetique");
  memset(dutyMs, 0, sizeof(dutyMs));
  acc.reset();
  for (uint8_t i = 0; i < MAXW; i++) {
    waveN[i] = 0;
    for (uint8_t a = 0; a < 3; a++) waveSum[i][a] = 0.0;
  }

  /* Combien d'echantillons de forme d'onde le budget autorise-t-il ? */
  waveCount = osjt_lf_fit(airtimeMs, PERIOD_MS / 1000, OSJT_DUTY_PERMILLE);
  Serial.printf("# SF%d : trame %s", OSJT_LORA_SF,
                waveCount ? "FULL" : "COMPACT");
  if (waveCount)
    Serial.printf(" %d echantillons (%lu ms d'antenne, %.2f %%)",
                  waveCount,
                  (unsigned long)airtimeMs(OSJT_LF_FULL_LEN(waveCount)),
                  airtimeMs(OSJT_LF_FULL_LEN(waveCount)) / 600.0);
  else
    Serial.printf(" (%lu ms d'antenne)",
                  (unsigned long)airtimeMs(OSJT_LF_COMPACT_LEN));
  Serial.println();

  /* L'autotest se fait ECRAN ALLUME, la premiere minute de mesure APRES son
   * extinction : jamais pendant, sinon les 15 mA de l'OLED entreraient dans
   * la toute premiere valeur publiee. */
  nodeBootCheck(magOk, bistOk, radioOk);
  acc.reset();
  periodStart = millis();
}

void nodeLoop() {
  const uint32_t now = millis();

  /* --- acquisition --------------------------------------------------- */
  if (!txBlank && mag.dataReady()) {
    float b[3];
    if (mag.read(b[0], b[1], b[2])) {
      acc.push(b);
      if (waveCount) {
        uint32_t el = now - periodStart;
        uint8_t i = (uint8_t)((el * waveCount) / PERIOD_MS);
        if (i < waveCount) {
          for (uint8_t a = 0; a < 3; a++) waveSum[i][a] += b[a];
          waveN[i]++;
        }
      }
    } else {
      flags |= OSJT_FLAG_SAT;
    }
  }

  /* --- fin de periode -------------------------------------------------- */
  if (now - periodStart >= PERIOD_MS) {
    if (acc.n >= 8) {
      float mean[3], mn[3], mx[3];
      for (uint8_t a = 0; a < 3; a++) {
        mean[a] = (float)(acc.sum[a] / acc.n);
        mn[a] = acc.mn[a];
        mx[a] = acc.mx[a];
      }
      /* Moins d'echantillons qu'attendu : la minute est marquee, elle n'est
       * pas jetee. C'est au PC de decider ce qu'il en fait — jeter en
       * silence serait pire que signaler. */
      if (acc.n < (PERIOD_MS / 1000) * 5) flags |= OSJT_FLAG_SHORTMIN;

      sendFrame(waveCount ? OSJT_LF_FULL : OSJT_LF_COMPACT,
                waveCount, mean, mn, mx, NAN);
      seq++;

    }
    acc.reset();
    for (uint8_t i = 0; i < MAXW; i++) {
      waveN[i] = 0;
      for (uint8_t a = 0; a < 3; a++) waveSum[i][a] = 0.0;
    }
    flags = 0;
    periodStart += PERIOD_MS;
    dutySlot = (uint8_t)((dutySlot + 1) % DUTY_SLOTS);
    dutyMs[dutySlot] = 0;
  }

  /* Rien a faire jusqu'au prochain DRDY : on rend la main au lieu de faire
   * tourner le processeur pour rien. A 10 Hz cela divise la consommation
   * par pres de trois, et la signature magnetique avec elle. */
  delay(1);
}
