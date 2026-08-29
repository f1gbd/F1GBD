/* =========================================================================
 * rm3100.h — pilote PNI RM3100 sur SPI, portage du firmware Teensy OSJT
 * =========================================================================
 * Carte de registres verifiee sur le pilote PX4 (rm3100.h) et le manuel
 * PNI. Identique a osjt_maghead.ino : les deux tetes doivent rendre les
 * memes nanoteslas pour les memes conditions, sinon comparer un site
 * filaire et un site LoRa n'a plus de sens.
 *
 * LE GAIN, ET L'ERREUR QUE TOUT LE MONDE RECOPIE
 * ----------------------------------------------
 * gain = 0,3671 x CC + 1,5  LSB/uT
 *
 * A CC=200 (defaut usine) cela donne 74,9 LSB/uT, que PX4 arrondit a 75,0
 * en dur dans son code. L'arrondi est sans consequence a 200 ; il devient
 * faux partout ailleurs. A CC=800 le gain vaut 295,2 LSB/uT, soit
 * 3,39 nT/LSB au lieu de 13,3 — c'est ce qui fait passer l'instrument
 * sous le seuil K1 de 5 nT.
 * ========================================================================= */

#ifndef OSJT_RM3100_H
#define OSJT_RM3100_H

#include <Arduino.h>
#include <SPI.h>

class RM3100 {
 public:
  /* Registres */
  static const uint8_t REG_POLL   = 0x00;
  static const uint8_t REG_CMM    = 0x01;
  static const uint8_t REG_CCX    = 0x04;   /* CCX(2) CCY(2) CCZ(2) */
  static const uint8_t REG_TMRC   = 0x0B;
  static const uint8_t REG_MX     = 0x24;   /* MX(3) MY(3) MZ(3), 24 bits */
  static const uint8_t REG_BIST   = 0x33;
  static const uint8_t REG_STATUS = 0x34;
  static const uint8_t REG_REVID  = 0x36;
  static const uint8_t REVID_EXPECTED = 0x22;

  /* CMM = start + DRDM (jeu complet) + axes X, Y, Z */
  static const uint8_t CMM_RUN = 0x79;

  RM3100(SPIClass &spi, uint8_t cs, uint8_t drdy)
      : spi_(spi), cs_(cs), drdy_(drdy), cc_(800) {}

  static float gainLsbPerUt(uint16_t cc) { return 0.3671f * cc + 1.5f; }
  static float nTPerLsb(uint16_t cc) { return 1000.0f / gainLsbPerUt(cc); }

  float nTPerLsb() const { return nTPerLsb(cc_); }

  bool begin(uint16_t cycleCount, uint8_t tmrc) {
    pinMode(cs_, OUTPUT);
    digitalWrite(cs_, HIGH);
    pinMode(drdy_, INPUT);
    delay(10);

    if (read8(REG_REVID) != REVID_EXPECTED) return false;

    cc_ = cycleCount;
    uint8_t d[6];
    for (uint8_t a = 0; a < 3; a++) {
      d[a * 2]     = (uint8_t)(cycleCount >> 8);
      d[a * 2 + 1] = (uint8_t)(cycleCount & 0xFF);
    }
    write(REG_CCX, d, 6);
    write8(REG_TMRC, tmrc);
    write8(REG_CMM, CMM_RUN);
    return true;
  }

  /* Autotest integre du capteur. Coupe la mesure continue, la relance. */
  bool bist() {
    write8(REG_CMM, 0x00);
    write8(REG_BIST, 0x8F);
    write8(REG_POLL, 0x70);
    delay(30);
    uint8_t r = read8(REG_BIST);
    write8(REG_BIST, 0x00);
    write8(REG_CMM, CMM_RUN);
    return (r & 0x70) == 0x70;   /* les trois oscillateurs ont repondu */
  }

  bool dataReady() {
    /* DRDY cable, sinon repli sur le registre d'etat. Le repli coute une
     * transaction SPI ; il evite qu'un cablage incomplet rende la tete
     * definitivement muette. */
    if (drdy_ != 0xFF && digitalRead(drdy_)) return true;
    return (read8(REG_STATUS) & 0x80) != 0;
  }

  /* Lit les trois axes. Rend false en cas de saturation manifeste. */
  bool read(float &bx, float &by, float &bz) {
    uint8_t b[9];
    read(REG_MX, b, 9);
    const float k = nTPerLsb();
    int32_t r[3];
    for (uint8_t a = 0; a < 3; a++) r[a] = s24(&b[a * 3]);
    bx = r[0] * k; by = r[1] * k; bz = r[2] * k;
    /* Le RM3100 rend un 24 bits ; une valeur collee a la butee signale une
     * saturation ou un bus muet, pas une mesure. */
    for (uint8_t a = 0; a < 3; a++)
      if (r[a] <= -8388607L || r[a] >= 8388607L) return false;
    return true;
  }

 private:
  SPIClass &spi_;
  uint8_t cs_, drdy_;
  uint16_t cc_;

  /* 1 MHz : large pour ce capteur, et assez lent pour traverser un metre
   * de nappe blindee sans reflexions. MODE0, MSB en tete. */
  SPISettings cfg_{1000000, MSBFIRST, SPI_MODE0};

  static int32_t s24(const uint8_t *p) {
    int32_t v = ((int32_t)p[0] << 16) | ((int32_t)p[1] << 8) | p[2];
    return (v & 0x800000L) ? (v - 0x1000000L) : v;
  }

  void write8(uint8_t reg, uint8_t v) { write(reg, &v, 1); }

  void write(uint8_t reg, const uint8_t *d, uint8_t n) {
    spi_.beginTransaction(cfg_);
    digitalWrite(cs_, LOW);
    spi_.transfer(reg & 0x7F);
    for (uint8_t i = 0; i < n; i++) spi_.transfer(d[i]);
    digitalWrite(cs_, HIGH);
    spi_.endTransaction();
  }

  uint8_t read8(uint8_t reg) { uint8_t v = 0; read(reg, &v, 1); return v; }

  void read(uint8_t reg, uint8_t *d, uint8_t n) {
    spi_.beginTransaction(cfg_);
    digitalWrite(cs_, LOW);
    spi_.transfer(reg | 0x80);
    for (uint8_t i = 0; i < n; i++) d[i] = spi_.transfer(0x00);
    digitalWrite(cs_, HIGH);
    spi_.endTransaction();
  }
};

#endif /* OSJT_RM3100_H */
