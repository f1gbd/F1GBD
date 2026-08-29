/* =========================================================================
 * osjt_teensy_frame.h — la trame de 36 octets que GEOMAG-Observer parle deja
 * =========================================================================
 *
 * C'est le format du firmware Teensy osjt_maghead. La passerelle LoRa le
 * rejoue, la tete WiFi l'emet en UDP : dans les trois cas le PC decode avec
 * le meme code, celui qui a ete eprouve le premier.
 *
 * POURQUOI UNE DEFINITION PARTAGEE PLUTOT QU'UNE COPIE
 * ---------------------------------------------------
 * Elle etait ecrite deux fois — dans gateway.cpp et, sans ce fichier, elle
 * l'aurait ete une troisieme dans la tete WiFi. Deux copies d'une structure
 * binaire divergent toujours un jour sur un champ, et la panne ne se
 * presente pas comme une erreur de compilation : elle se presente comme un
 * magnetogramme aux valeurs absurdes, six semaines plus tard.
 *
 * LE CRC NE COUVRE PAS LA MAGIE
 * -----------------------------
 * Il porte sur les 32 octets qui suivent les deux octets de magie, et non
 * sur la trame entiere. Ce n'est pas un choix : c'est ce que fait le
 * firmware Teensy d'origine, et le decodeur du PC verifie exactement cela.
 * Le « corriger » romprait la compatibilite avec la seule tete qui soit
 * deja en service.
 *
 * Copyright 2026 F1GBD / F4JHW — ADRASEC 77 — Licence MIT
 * ========================================================================= */

#ifndef OSJT_TEENSY_FRAME_H
#define OSJT_TEENSY_FRAME_H

#include <math.h>
#include <stdint.h>
#include <string.h>

#include "osjt_lora_frame.h"   /* osjt_crc16 */

#define OSJT_TEENSY_MAGIC 0x4A53
#define OSJT_TEENSY_LEN   36

#pragma pack(push, 1)
struct OsjtTeensyFrame {
  uint16_t magic;
  uint8_t  ver;
  uint8_t  len;
  uint32_t seq;
  uint64_t t_us;
  int32_t  bx_mnT, by_mnT, bz_mnT;
  uint16_t n;
  int16_t  temp_cC;
  uint16_t flags;
  uint16_t crc;
};
#pragma pack(pop)

#ifdef __cplusplus
static_assert(sizeof(OsjtTeensyFrame) == OSJT_TEENSY_LEN,
              "OsjtTeensyFrame doit faire 36 octets");
#endif

/* Remplit la structure et pose le CRC. Le champ magnetique est donne en nT,
 * la temperature en degres (NAN si absente). */
static inline void osjt_teensy_build(OsjtTeensyFrame *f, uint32_t seq,
                                     uint64_t t_us, float bx, float by,
                                     float bz, uint16_t n, int16_t temp_cC,
                                     uint16_t flags) {
  f->magic  = OSJT_TEENSY_MAGIC;
  f->ver    = 1;
  f->len    = OSJT_TEENSY_LEN - 6;
  f->seq    = seq;
  f->t_us   = t_us;
  f->bx_mnT = (int32_t)llroundf(bx * 1000.0f);
  f->by_mnT = (int32_t)llroundf(by * 1000.0f);
  f->bz_mnT = (int32_t)llroundf(bz * 1000.0f);
  f->n      = n;
  f->temp_cC = temp_cC;
  f->flags  = flags;
  f->crc = osjt_crc16((const uint8_t *)f + 2, OSJT_TEENSY_LEN - 4);
}

#endif /* OSJT_TEENSY_FRAME_H */
