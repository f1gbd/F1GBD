/* =========================================================================
 * gateway.cpp — la passerelle : SX1262 -> USB serie, sur le PC
 * =========================================================================
 *
 * Elle recoit les trames LoRa et les re-emet sur le port serie AU FORMAT
 * 36 OCTETS QUE GEOMAG-Observer PARLE DEJA.
 *
 * POURQUOI CE CHOIX PLUTOT QU'UN NOUVEAU PROTOCOLE COTE PC
 * --------------------------------------------------------
 * Le programme sait deja decoder la trame serie de la tete Teensy, avec son
 * CRC, son extraction dans un flux bruite et son autotest. Reecrire tout
 * cela pour le LoRa, c'est doubler la surface de bug pour un resultat
 * identique. La passerelle degroupe donc la minute et rejoue les
 * echantillons un par un, comme si un capteur filaire etait branche.
 *
 * Le backend « Teensy (serie) » fonctionne sans une ligne de modification.
 *
 * LA RECONSTRUCTION DES HORODATAGES
 * ---------------------------------
 * La trame porte le millis() du noeud au centre de la minute. Ce n'est pas
 * une heure : c'est un compteur depuis le dernier demarrage, qui derive.
 * La passerelle ne cherche pas a le corriger — elle rend l'horodatage du
 * noeud tel quel, et c'est le PC qui fait l'ajustement, parce que lui seul
 * connait l'heure vraie.
 *
 * Les echantillons de forme d'onde sont repartis regulierement dans la
 * minute. On ne pretend pas connaitre leur instant exact au millieme : ils
 * ont ete moyennes sur une case de 4 s, et c'est le centre de cette case
 * qui est rendu. Pretendre mieux serait mentir sur la donnee.
 *
 * Copyright 2026 F1GBD / F4JHW — ADRASEC 77 — Licence MIT
 * ========================================================================= */

#include <Arduino.h>
#include <RadioLib.h>
#include <SPI.h>

#include "osjt_lora_frame.h"
#include "osjt_oled.h"
#include "osjt_pins.h"
/* La trame de 36 octets vit desormais dans son propre en-tete : la tete
 * WiFi l'emet elle aussi, et deux copies d'une structure binaire finissent
 * toujours par diverger sur un champ. */
#include "osjt_teensy_frame.h"

static SX1262 radio = new Module(PIN_LORA_NSS, PIN_LORA_DIO1,
                                 PIN_LORA_RST, PIN_LORA_BUSY);

static uint32_t outSeq = 0;
static uint32_t nFrames = 0, nBad = 0;
static uint32_t lastRx = 0;

static void emitSerial(uint64_t t_us, float bx, float by, float bz,
                       uint16_t n, int16_t temp_cC, uint16_t flags) {
  OsjtTeensyFrame f;
  osjt_teensy_build(&f, outSeq++, t_us, bx, by, bz, n, temp_cC, flags);
  Serial.write((const uint8_t *)&f, OSJT_TEENSY_LEN);
}

static void handle(const uint8_t *buf, uint16_t len) {
  if (!osjt_lf_check(buf, len)) { nBad++; return; }
  nFrames++;
  lastRx = millis();

  OsjtLoraHdr h;
  OsjtLoraStat st;
  memcpy(&h, buf, sizeof(h));
  memcpy(&st, buf + OSJT_LF_HDR_LEN, sizeof(st));

  float mean[3];
  for (uint8_t a = 0; a < 3; a++) mean[a] = st.mean_mnT[a] / 1000.0f;

  const uint64_t centre_us = (uint64_t)h.t_ms * 1000ULL;

  if (h.type == OSJT_LF_FULL && h.nsamp) {
    /* Degroupage : une trame serie par case, horodatee au centre de sa
     * case. La minute couvre [centre - 30 s, centre + 30 s]. */
    const uint32_t step_us = 60000000UL / h.nsamp;
    const uint8_t *p = buf + OSJT_LF_HDR_LEN + OSJT_LF_STAT_LEN;
    for (uint8_t i = 0; i < h.nsamp; i++) {
      float b[3];
      for (uint8_t a = 0; a < 3; a++) {
        int16_t d;
        memcpy(&d, p, 2);
        p += 2;
        b[a] = mean[a] + d / 10.0f;
      }
      uint64_t t = centre_us - 30000000ULL + (uint64_t)i * step_us
                   + step_us / 2;
      emitSerial(t, b[0], b[1], b[2], 1, h.temp_cC, h.flags);
    }
  } else {
    /* COMPACT ou ALARME : la moyenne minute seule, horodatee au centre. */
    emitSerial(centre_us, mean[0], mean[1], mean[2], 1, h.temp_cC, h.flags);
  }
}

void gatewaySetup() {
  setCpuFrequencyMhz(OSJT_CPU_MHZ);
  Serial.begin(115200);
  delay(200);

  SPI.begin(PIN_LORA_SCK, PIN_LORA_MISO, PIN_LORA_MOSI, PIN_LORA_NSS);
  int s = radio.begin(OSJT_LORA_FREQ_HZ / 1e6, OSJT_LORA_BW_KHZ,
                      OSJT_LORA_SF, OSJT_LORA_CR, OSJT_LORA_SYNC,
                      OSJT_LORA_DBM);
  /* Les commentaires partent sur la sortie serie AVANT tout flux binaire :
   * le decodeur du PC sait ignorer ce qui n'est pas une trame, mais autant
   * ne pas melanger inutilement. */
  if (s == RADIOLIB_ERR_NONE)
    Serial.printf("# OSJT passerelle LoRa %s — SF%d, %.3f MHz\n",
                  OSJT_FW_VERSION, OSJT_LORA_SF,
                  OSJT_LORA_FREQ_HZ / 1e6);
  else
    Serial.printf("# ERREUR SX1262 : %d\n", s);

  osjtOledBegin("Passerelle LoRa");
  radio.startReceive();
}

/* Ce qu'on veut lire d'un coup d'oeil, sans ouvrir de terminal : est-ce que
 * ca recoit, depuis quand, et avec quelle marge. */
static void oledRefresh() {
  if (!osjtOledPresent()) return;
  char l1[24], l2[24], l3[24], l4[24];
  snprintf(l1, sizeof l1, "%lu trames", (unsigned long)nFrames);
  if (nFrames == 0) {
    snprintf(l2, sizeof l2, "en attente...");
    snprintf(l3, sizeof l3, "SF%d  %.1f MHz", OSJT_LORA_SF,
             OSJT_LORA_FREQ_HZ / 1e6);
    snprintf(l4, sizeof l4, "%lu s d'ecoute",
             (unsigned long)(millis() / 1000));
  } else {
    uint32_t age = (millis() - lastRx) / 1000;
    snprintf(l2, sizeof l2, "RSSI %.0f dBm", radio.getRSSI());
    snprintf(l3, sizeof l3, "SNR  %.1f dB", radio.getSNR());
    /* Au-dela de 90 s sans trame, la liaison a un probleme : le noeud emet
     * toutes les minutes. On le dit plutot que d'afficher un age qui monte
     * sans que personne ne le remarque. */
    if (age > 90) snprintf(l4, sizeof l4, "! RIEN DEPUIS %lus",
                           (unsigned long)age);
    else          snprintf(l4, sizeof l4, "il y a %lu s",
                           (unsigned long)age);
  }
  osjtOledStatus(l1, l2, l3, l4);
}

void gatewayLoop() {
  static uint32_t lastStat = 0;

  if (radio.available()) {
    uint8_t buf[OSJT_LF_MAX_LEN];
    int16_t n = radio.getPacketLength();
    if (n > 0 && n <= (int16_t)sizeof(buf)) {
      int s = radio.readData(buf, n);
      if (s == RADIOLIB_ERR_NONE) handle(buf, (uint16_t)n);
      else nBad++;
    }
    radio.startReceive();
    oledRefresh();
  }

  /* L'ecran se rafraichit aussi sans trame : c'est justement l'absence de
   * trame qu'il faut pouvoir constater. */
  static uint32_t lastOled = 0;
  if (millis() - lastOled > 5000UL) { lastOled = millis(); oledRefresh(); }

  /* Un signe de vie toutes les cinq minutes. Sur une liaison qui ne parle
   * qu'une fois par minute, l'absence de trame est ambigue : panne du
   * noeud, ou simplement rien a dire ? Cette ligne tranche. */
  if (millis() - lastStat > 300000UL) {
    lastStat = millis();
    Serial.printf("# passerelle : %lu trames, %lu rejetees, RSSI %.0f dBm, "
                  "SNR %.1f dB\n", (unsigned long)nFrames,
                  (unsigned long)nBad, radio.getRSSI(), radio.getSNR());
  }

  delay(2);
}
