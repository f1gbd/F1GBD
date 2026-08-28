/* =========================================================================
 * OSJT — Ou Suis-Je sur Terre
 * =========================================================================
 * osjt_maghead — tete magnetique RM3100 sur Teensy 4.1
 * Version 0.1.0
 *
 * Lit un PNI RM3100 en SPI a pleine resolution, horodate chaque echantillon
 * sur interruption DRDY, moyenne, et diffuse le resultat par trois voies
 * simultanees : USB serie, Ethernet UDP et carte SD.
 *
 * POURQUOI CE FIRMWARE EXISTE
 * ---------------------------
 * Le message MAG du dataflash ArduPilot stocke des int16 en gauss avec un
 * multiplicateur 1e-3 : le pas de quantification vaut 100 nT. C'est 20 a 50
 * fois trop grossier pour du MagNav ou pour un indice K local. Cette tete
 * contourne le probleme : elle lit le capteur elle-meme, en pleine
 * resolution (3,39 nT/LSB a CC=800), et produit sa propre donnee horodatee.
 *
 * Elle resout aussi le probleme de cable : le SPI ne franchit pas les 30 m
 * qui separent un capteur enterre de la maison. Le Teensy va DANS le tube,
 * a cote du capteur, et c'est de l'Ethernet qui remonte.
 *
 * PROPRETE MAGNETIQUE — a lire avant de cabler
 * --------------------------------------------
 * Le Teensy est lui-meme une source magnetique. A 600 MHz il consomme une
 * centaine de milliamperes ; la boucle de courant correspondante produit
 * environ 6 nT a 10 cm, 0,8 nT a 20 cm, 0,2 nT a 30 cm. Le plancher de
 * bruit vise etant de 1 a 3 nT :
 *
 *   - 30 cm MINIMUM entre le Teensy et le RM3100, 50 cm de preference ;
 *   - sous-cadencer le processeur (commande CLK=150) : aucune puissance de
 *     calcul n'est necessaire pour lire un capteur a 40 Hz, et la
 *     consommation chute avec sa variabilite ;
 *   - le magjack RJ45 contient des transformateurs a NOYAU FERRITE : objet
 *     magnetiquement permeable, a placer aussi loin que le Teensy et a fixer
 *     rigidement ;
 *   - sur la tete elle-meme, rien d'autre que le RM3100 et ses condensateurs
 *     ceramiques. Pas de connecteur USB, pas de carte SD, pas de
 *     condensateur a boitier acier ;
 *   - l'alimentation qui descend dans le CAT5E doit emprunter une PAIRE
 *     TORSADEE (aller et retour dans la meme paire) : la boucle est alors
 *     minuscule. Aller sur une paire et retour sur une autre produit environ
 *     1 nT a 20 cm.
 *
 * CABLAGE (broches par defaut du Teensy 4.1)
 * ------------------------------------------
 *   RM3100 VDD  -> 3.3V     (2,0 a 3,6 V ; les broches du Teensy 4.x ne
 *   RM3100 GND  -> GND       sont PAS tolerantes 5 V, donc connexion directe)
 *   RM3100 SCK  -> 13
 *   RM3100 MISO -> 12
 *   RM3100 MOSI -> 11
 *   RM3100 CS   -> 10
 *   RM3100 DRDY ->  9        (interruption ; sinon scrutation du registre)
 *
 *   Sonde MCP9808 optionnelle sur I2C : SDA 18, SCL 19, adresse 0x18.
 *
 *   Sur 50 cm a 1 m de paire torsadee blindee, garder le SPI a 1 MHz et
 *   inserer 33 a 100 ohms en serie sur SCK, MOSI et CS pour amortir les
 *   reflexions.
 *
 * COMMANDES (terminal serie, 115200, une ligne par commande)
 * ----------------------------------------------------------
 *   ?            aide
 *   ID           revision du capteur, version du firmware, gain courant
 *   STAT         compteurs de sante
 *   BIST         auto-test integre du RM3100
 *   CC=<50..800> cycle count (resolution)
 *   TMRC=<hex>   cadence interne, 0x92..0x9D
 *   OUT=<hz>     cadence de sortie apres moyennage (0,1 a 100)
 *   FMT=CSV|BIN|BOTH
 *   CLK=<mhz>    sous-cadencement du processeur (24..600)
 *   SD=ON|OFF    journalisation sur carte SD
 *   UDP=ON|OFF   diffusion Ethernet
 *   IP=a.b.c.d   destination UDP
 *   PORT=<n>     port UDP
 *   ZERO         remet a zero les compteurs
 *   SAVE         ecrit la configuration en EEPROM
 *
 * Dependances : SPI, EEPROM, SD (fournis par Teensyduino).
 *               QNEthernet si l'Ethernet est utilise (facultatif, detecte
 *               automatiquement a la compilation).
 *
 * Auteur : F1GBD / ADRASEC 77 — projet OSJT
 * ========================================================================= */

#include <SPI.h>
#include <EEPROM.h>
#include <Wire.h>

#define FW_VERSION "0.1.0"

/* -- Ethernet optionnel : detecte a la compilation ----------------------- */
#if __has_include(<QNEthernet.h>)
  #include <QNEthernet.h>
  using namespace qindesign::network;
  #define HAS_ETHERNET 1
#else
  #define HAS_ETHERNET 0
#endif

/* -- Carte SD (socket integre du Teensy 4.1) ----------------------------- */
#if __has_include(<SD.h>)
  #include <SD.h>
  #define HAS_SD 1
#else
  #define HAS_SD 0
#endif

/* =========================================================================
 * 1. REGISTRES DU RM3100
 * Carte verifiee sur le pilote PX4 (rm3100.h) et le manuel PNI.
 * ========================================================================= */
static const uint8_t REG_POLL   = 0x00;
static const uint8_t REG_CMM    = 0x01;
static const uint8_t REG_CCX    = 0x04;   /* CCX(2) CCY(2) CCZ(2) */
static const uint8_t REG_TMRC   = 0x0B;
static const uint8_t REG_MX     = 0x24;   /* MX(3) MY(3) MZ(3), 24 bits */
static const uint8_t REG_BIST   = 0x33;
static const uint8_t REG_STATUS = 0x34;
static const uint8_t REG_REVID  = 0x36;
static const uint8_t REVID_EXPECTED = 0x22;

/* CMM = start + DRDM(jeu complet) + axes X, Y, Z */
static const uint8_t CMM_RUN = 0x79;

/* Broches */
static const uint8_t PIN_CS   = 10;
static const uint8_t PIN_DRDY = 9;

/* =========================================================================
 * 2. CONFIGURATION PERSISTANTE
 * ========================================================================= */
struct Config {
  uint32_t magic;
  uint16_t cycleCount;      /* 50 a 800 */
  uint8_t  tmrc;            /* 0x92..0x9D */
  uint8_t  fmt;             /* 0 = CSV, 1 = BIN, 2 = BOTH */
  float    outRateHz;       /* cadence apres moyennage */
  uint16_t cpuMHz;
  uint8_t  sdEnable;
  uint8_t  udpEnable;
  uint8_t  ip[4];
  uint16_t port;
  uint16_t crc;
};

static const uint32_t CFG_MAGIC = 0x4A534A54UL;   /* "JSJT" */
Config cfg;

void configDefaults() {
  cfg.magic      = CFG_MAGIC;
  cfg.cycleCount = 800;          /* 3,39 nT/LSB */
  cfg.tmrc       = 0x96;         /* ~37 Hz : cadence maximale a CC=800 */
  cfg.fmt        = 0;            /* CSV : lisible au terminal */
  cfg.outRateHz  = 10.0f;
  cfg.cpuMHz     = 150;          /* sous-cadence : moins de champ parasite */
  cfg.sdEnable   = 0;
  cfg.udpEnable  = 0;
  cfg.ip[0] = 192; cfg.ip[1] = 168; cfg.ip[2] = 1; cfg.ip[3] = 255;
  cfg.port       = 10077;
}

/* =========================================================================
 * 3. ETAT
 * ========================================================================= */
volatile uint32_t g_drdyCount = 0;
volatile uint32_t g_drdyMicros = 0;
volatile bool     g_drdyFlag = false;

struct Health {
  uint32_t samples;
  uint32_t frames;
  uint32_t drdyTimeouts;
  uint32_t spiErrors;
  uint32_t saturations;
  uint32_t sdErrors;
  uint32_t udpErrors;
} health;

/* flags remontes dans chaque trame */
static const uint16_t F_DRDY_TIMEOUT = 1 << 0;
static const uint16_t F_SPI_ERROR    = 1 << 1;
static const uint16_t F_SATURATION   = 1 << 2;
static const uint16_t F_SD_ERROR     = 1 << 3;
static const uint16_t F_ETH_DOWN     = 1 << 4;
static const uint16_t F_NO_TEMP      = 1 << 5;
static const uint16_t F_POLLING      = 1 << 6;   /* DRDY non cable */

uint16_t g_flags = 0;
float    g_nT_per_lsb = 3.39f;
uint32_t g_seq = 0;
bool     g_usePolling = false;
bool     g_haveTemp = false;
bool     g_sdOpen = false;

/* accumulateur de moyennage */
double   acc[3] = {0, 0, 0};
uint32_t accN = 0;
uint64_t accT = 0;

SPISettings spiCfg(1000000, MSBFIRST, SPI_MODE0);   /* 1 MHz : sur 1 m de
                                                       paire torsadee, ne pas
                                                       monter plus haut */
#if HAS_ETHERNET
EthernetUDP udp;
bool ethUp = false;
#endif
#if HAS_SD
File sdFile;
char sdName[32] = {0};
#endif

/* =========================================================================
 * 4. PILOTE RM3100
 * ========================================================================= */
static inline void csLow()  { digitalWriteFast(PIN_CS, LOW); }
static inline void csHigh() { digitalWriteFast(PIN_CS, HIGH); }

void rmWrite(uint8_t reg, const uint8_t *data, uint8_t n) {
  SPI.beginTransaction(spiCfg);
  csLow();
  SPI.transfer(reg & 0x7F);
  for (uint8_t i = 0; i < n; i++) SPI.transfer(data[i]);
  csHigh();
  SPI.endTransaction();
}

void rmWrite8(uint8_t reg, uint8_t v) { rmWrite(reg, &v, 1); }

void rmRead(uint8_t reg, uint8_t *buf, uint8_t n) {
  SPI.beginTransaction(spiCfg);
  csLow();
  SPI.transfer(reg | 0x80);
  for (uint8_t i = 0; i < n; i++) buf[i] = SPI.transfer(0x00);
  csHigh();
  SPI.endTransaction();
}

uint8_t rmRead8(uint8_t reg) {
  uint8_t v;
  rmRead(reg, &v, 1);
  return v;
}

/* Gain PNI : LSB/uT = 0,3671 x CC + 1,5.
   Verification : CC = 200 -> 74,9, exactement la constante 75,0 du pilote
   PX4. CC = 800 -> 295,2 LSB/uT, soit 3,39 nT/LSB. */
float rmGain(uint16_t cc)      { return 0.3671f * (float)cc + 1.5f; }
float rmNtPerLsb(uint16_t cc)  { return 1000.0f / rmGain(cc); }

/* Entier 24 bits signe, gros-boutiste */
static inline int32_t s24(const uint8_t *b) {
  int32_t v = ((int32_t)b[0] << 16) | ((int32_t)b[1] << 8) | b[2];
  if (v & 0x800000L) v -= 0x1000000L;
  return v;
}

bool rmConfigure() {
  uint8_t rev = rmRead8(REG_REVID);
  if (rev != REVID_EXPECTED) {
    health.spiErrors++;
    g_flags |= F_SPI_ERROR;
    Serial.printf("# ERREUR RM3100 : REVID lu 0x%02X, attendu 0x%02X.\n", rev,
                  REVID_EXPECTED);
    Serial.println(F("#   Verifier CS, alimentation 3,3 V, longueur de cable"));
    Serial.println(F("#   et resistances serie sur SCK/MOSI/CS."));
    return false;
  }
  uint16_t cc = cfg.cycleCount;
  uint8_t d[6] = { (uint8_t)(cc >> 8), (uint8_t)(cc & 0xFF),
                   (uint8_t)(cc >> 8), (uint8_t)(cc & 0xFF),
                   (uint8_t)(cc >> 8), (uint8_t)(cc & 0xFF) };
  rmWrite(REG_CCX, d, 6);
  rmWrite8(REG_TMRC, cfg.tmrc);
  rmWrite8(REG_CMM, CMM_RUN);
  g_nT_per_lsb = rmNtPerLsb(cc);
  g_flags &= ~F_SPI_ERROR;
  return true;
}

bool rmSelfTest() {
  rmWrite8(REG_CMM, 0x00);
  delay(5);
  rmWrite8(REG_BIST, 0x8F);
  rmWrite8(REG_POLL, 0x70);
  delay(120);
  uint8_t r = rmRead8(REG_BIST);
  rmWrite8(REG_BIST, 0x00);
  rmWrite8(REG_CMM, CMM_RUN);
  bool ok = ((r & 0x70) == 0x70);
  Serial.printf("BIST=0x%02X %s\n", r, ok ? "OK" : "ECHEC");
  if (!ok)
    Serial.println(F("# Un axe ne repond pas : cable coupe ou capteur HS."));
  return ok;
}

/* Cadence associee au registre TMRC */
float tmrcRate(uint8_t t) {
  switch (t) {
    case 0x92: return 600.0f; case 0x93: return 300.0f;
    case 0x94: return 150.0f; case 0x95: return 75.0f;
    case 0x96: return 37.0f;  case 0x97: return 18.0f;
    case 0x98: return 9.0f;   case 0x99: return 4.5f;
    case 0x9A: return 2.3f;   case 0x9B: return 1.2f;
    case 0x9C: return 0.6f;   case 0x9D: return 0.3f;
    default:   return 37.0f;
  }
}

/* =========================================================================
 * 5. SONDE DE TEMPERATURE MCP9808 (optionnelle, I2C 0x18)
 * Ecrite en direct pour ne pas dependre d'une bibliotheque de plus.
 * ========================================================================= */
static const uint8_t MCP9808_ADDR = 0x18;

bool tempBegin() {
  Wire.begin();
  Wire.setClock(100000);
  Wire.beginTransmission(MCP9808_ADDR);
  Wire.write(0x06);                       /* registre fabricant */
  if (Wire.endTransmission() != 0) return false;
  Wire.requestFrom((int)MCP9808_ADDR, 2);
  if (Wire.available() < 2) return false;
  uint16_t id = (Wire.read() << 8) | Wire.read();
  return (id == 0x0054);
}

float tempRead() {
  Wire.beginTransmission(MCP9808_ADDR);
  Wire.write(0x05);
  if (Wire.endTransmission() != 0) return NAN;
  Wire.requestFrom((int)MCP9808_ADDR, 2);
  if (Wire.available() < 2) return NAN;
  uint16_t v = (Wire.read() << 8) | Wire.read();
  float t = (v & 0x0FFF) / 16.0f;
  if (v & 0x1000) t -= 256.0f;
  return t;
}

/* =========================================================================
 * 6. TRAMES DE SORTIE
 * ========================================================================= */
/* CRC-16/CCITT-FALSE — meme polynome cote Python (osjt_magobs). */
uint16_t crc16(const uint8_t *p, size_t n) {
  uint16_t c = 0xFFFF;
  for (size_t i = 0; i < n; i++) {
    c ^= (uint16_t)p[i] << 8;
    for (uint8_t b = 0; b < 8; b++)
      c = (c & 0x8000) ? (uint16_t)((c << 1) ^ 0x1021) : (uint16_t)(c << 1);
  }
  return c;
}

/* Trame binaire, petit-boutiste, 36 octets.
   Les composantes sont en MILLI-nanoteslas : la plage +-2100 uT couvre
   largement les +-1100 uT du capteur, et la resolution de 1 pT preserve le
   benefice du moyennage. */
#pragma pack(push, 1)
struct BinFrame {
  uint16_t magic;      /* 0x4A53 */
  uint8_t  ver;        /* 1 */
  uint8_t  len;        /* octets de charge utile apres cet octet */
  uint32_t seq;
  uint64_t t_us;
  int32_t  bx_mnT;
  int32_t  by_mnT;
  int32_t  bz_mnT;
  uint16_t n;          /* echantillons moyennes */
  int16_t  temp_cC;    /* centi-degres, -32768 si absent */
  uint16_t flags;
  uint16_t crc;        /* sur tout ce qui precede, magic exclu */
};
#pragma pack(pop)

void emitFrame(uint64_t t_us, double bx, double by, double bz, uint16_t n,
               float tC) {
  bool haveT = !isnan(tC);
  if (cfg.fmt == 0 || cfg.fmt == 2) {
    /* Ligne ASCII avec somme de controle, style NMEA : lisible dans
       n'importe quel terminal, ce qui compte pour la mise au point. */
    char tbuf[12];
    if (haveT) snprintf(tbuf, sizeof(tbuf), "%.2f", (double)tC);
    else       tbuf[0] = 0;
    char body[160];
    int m = snprintf(body, sizeof(body),
                     "MAG,%lu,%llu,%.3f,%.3f,%.3f,%u,%s,%u",
                     (unsigned long)g_seq, (unsigned long long)t_us,
                     bx, by, bz, n, tbuf, g_flags);
    uint8_t ck = 0;
    for (int i = 0; i < m; i++) ck ^= (uint8_t)body[i];
    Serial.printf("$%s*%02X\n", body, ck);
  }
  if (cfg.fmt == 1 || cfg.fmt == 2) {
    BinFrame f;
    f.magic = 0x4A53;
    f.ver = 1;
    f.len = sizeof(BinFrame) - 4 - 2;   /* apres len, avant crc */
    f.seq = g_seq;
    f.t_us = t_us;
    f.bx_mnT = (int32_t)llround(bx * 1000.0);
    f.by_mnT = (int32_t)llround(by * 1000.0);
    f.bz_mnT = (int32_t)llround(bz * 1000.0);
    f.n = n;
    f.temp_cC = haveT ? (int16_t)lround(tC * 100.0f) : (int16_t)-32768;
    f.flags = g_flags;
    f.crc = crc16(((const uint8_t *)&f) + 2, sizeof(BinFrame) - 4);
    Serial.write((const uint8_t *)&f, sizeof(f));
  }

#if HAS_ETHERNET
  if (cfg.udpEnable && ethUp) {
    BinFrame f;
    f.magic = 0x4A53; f.ver = 1; f.len = sizeof(BinFrame) - 6;
    f.seq = g_seq; f.t_us = t_us;
    f.bx_mnT = (int32_t)llround(bx * 1000.0);
    f.by_mnT = (int32_t)llround(by * 1000.0);
    f.bz_mnT = (int32_t)llround(bz * 1000.0);
    f.n = n;
    f.temp_cC = haveT ? (int16_t)lround(tC * 100.0f) : (int16_t)-32768;
    f.flags = g_flags;
    f.crc = crc16(((const uint8_t *)&f) + 2, sizeof(BinFrame) - 4);
    IPAddress dst(cfg.ip[0], cfg.ip[1], cfg.ip[2], cfg.ip[3]);
    if (udp.beginPacket(dst, cfg.port)) {
      udp.write((const uint8_t *)&f, sizeof(f));
      if (!udp.endPacket()) { health.udpErrors++; }
    } else {
      health.udpErrors++;
    }
  }
#endif

#if HAS_SD
  if (cfg.sdEnable && g_sdOpen) {
    /* CSV brut : la SD est le filet de securite si le reseau tombe. */
    sdFile.printf("%lu,%llu,%.3f,%.3f,%.3f,%u,%.2f,%u\n",
                  (unsigned long)g_seq, (unsigned long long)t_us,
                  bx, by, bz, n, haveT ? tC : NAN, g_flags);
    if ((g_seq & 0x3F) == 0) sdFile.flush();   /* toutes les 64 trames */
  }
#endif

  g_seq++;
  health.frames++;
}

/* =========================================================================
 * 7. INTERRUPTION DRDY
 * L'ISR ne fait QUE dater. Lire le SPI dans une interruption est une
 * mauvaise idee : la transaction dure des dizaines de microsecondes et
 * bloquerait tout le reste. On date, on leve un drapeau, la boucle lit.
 * ========================================================================= */
void drdyISR() {
  g_drdyMicros = micros();
  g_drdyCount++;
  g_drdyFlag = true;
}

/* =========================================================================
 * 8. INITIALISATION
 * ========================================================================= */
void cfgLoad() {
  EEPROM.get(0, cfg);
  uint16_t want = crc16((const uint8_t *)&cfg, sizeof(Config) - 2);
  if (cfg.magic != CFG_MAGIC || cfg.crc != want) {
    configDefaults();
    Serial.println(F("# Configuration par defaut (EEPROM vide ou corrompue)."));
  }
}

void cfgSave() {
  cfg.magic = CFG_MAGIC;
  cfg.crc = crc16((const uint8_t *)&cfg, sizeof(Config) - 2);
  EEPROM.put(0, cfg);
  Serial.println(F("# Configuration enregistree."));
}

void applyCpuClock() {
#if defined(__IMXRT1062__)
  extern "C" uint32_t set_arm_clock(uint32_t frequency);
  uint32_t hz = (uint32_t)cfg.cpuMHz * 1000000UL;
  if (hz >= 24000000UL && hz <= 600000000UL) set_arm_clock(hz);
#endif
}

void sdOpen() {
#if HAS_SD
  g_sdOpen = false;
  if (!cfg.sdEnable) return;
  if (!SD.begin(BUILTIN_SDCARD)) {
    health.sdErrors++;
    g_flags |= F_SD_ERROR;
    Serial.println(F("# Carte SD absente ou illisible."));
    return;
  }
  for (int i = 0; i < 1000; i++) {
    snprintf(sdName, sizeof(sdName), "MAG%04d.CSV", i);
    if (!SD.exists(sdName)) break;
  }
  sdFile = SD.open(sdName, FILE_WRITE);
  if (!sdFile) {
    health.sdErrors++;
    g_flags |= F_SD_ERROR;
    return;
  }
  sdFile.println("seq,t_us,bx_nT,by_nT,bz_nT,n,temp_C,flags");
  g_sdOpen = true;
  g_flags &= ~F_SD_ERROR;
  Serial.printf("# Journalisation SD : %s\n", sdName);
#endif
}

void ethStart() {
#if HAS_ETHERNET
  if (!cfg.udpEnable) return;
  Ethernet.begin();                       /* DHCP */
  if (!Ethernet.waitForLocalIP(8000)) {
    g_flags |= F_ETH_DOWN;
    Serial.println(F("# Ethernet : pas d'adresse (DHCP absent ?)."));
    ethUp = false;
    return;
  }
  udp.begin(cfg.port);
  ethUp = true;
  g_flags &= ~F_ETH_DOWN;
  Serial.print(F("# Ethernet actif, adresse "));
  Serial.println(Ethernet.localIP());
#else
  if (cfg.udpEnable)
    Serial.println(F("# QNEthernet absent a la compilation : UDP indisponible."));
#endif
}

void banner() {
  Serial.println();
  Serial.println(F("# ================================================="));
  Serial.printf ("# OSJT maghead %s — RM3100 sur Teensy 4.1\n", FW_VERSION);
  Serial.println(F("# ================================================="));
  Serial.printf ("# cycle count %u  ->  %.2f nT/LSB  (%.0f LSB/uT)\n",
                 cfg.cycleCount, g_nT_per_lsb, rmGain(cfg.cycleCount));
  Serial.printf ("# cadence capteur %.1f Hz, sortie %.2f Hz\n",
                 tmrcRate(cfg.tmrc), cfg.outRateHz);
  Serial.printf ("# processeur %u MHz  (sous-cadencer reduit le champ "
                 "parasite)\n", cfg.cpuMHz);
  Serial.printf ("# format %s, SD %s, UDP %s\n",
                 cfg.fmt == 0 ? "CSV" : (cfg.fmt == 1 ? "BIN" : "BOTH"),
                 cfg.sdEnable ? "on" : "off",
                 cfg.udpEnable ? "on" : "off");
  Serial.println(F("# tapez ? pour l'aide"));
  Serial.println();
}

void setup() {
  pinMode(PIN_CS, OUTPUT);
  csHigh();
  pinMode(PIN_DRDY, INPUT);

  Serial.begin(115200);
  uint32_t t0 = millis();
  while (!Serial && (millis() - t0) < 2000) { }

  cfgLoad();
  applyCpuClock();

  SPI.begin();
  delay(20);
  rmConfigure();
  g_nT_per_lsb = rmNtPerLsb(cfg.cycleCount);

  /* DRDY cable ? On observe la broche pendant 200 ms. Si elle ne bouge
     jamais, on bascule en scrutation du registre STATUS — degrade mais
     fonctionnel, avec un horodatage un peu moins fin. */
  attachInterrupt(digitalPinToInterrupt(PIN_DRDY), drdyISR, RISING);
  uint32_t c0 = g_drdyCount;
  delay(200);
  if (g_drdyCount == c0) {
    detachInterrupt(digitalPinToInterrupt(PIN_DRDY));
    g_usePolling = true;
    g_flags |= F_POLLING;
    Serial.println(F("# DRDY inactive : passage en scrutation du registre "
                     "STATUS. Cabler DRDY sur la broche 9 pour un "
                     "horodatage a la microseconde."));
  }

  g_haveTemp = tempBegin();
  if (!g_haveTemp) g_flags |= F_NO_TEMP;

  sdOpen();
  ethStart();
  banner();
}

/* =========================================================================
 * 9. COMMANDES
 * ========================================================================= */
void help() {
  Serial.println(F(
    "# ?            aide\n"
    "# ID           revision capteur, firmware, gain\n"
    "# STAT         compteurs de sante\n"
    "# BIST         auto-test du RM3100\n"
    "# CC=<50..800> cycle count (800 -> 3,39 nT/LSB, 200 -> 13,3)\n"
    "# TMRC=<hex>   cadence interne 92..9D (96 = 37 Hz)\n"
    "# OUT=<hz>     cadence de sortie apres moyennage\n"
    "# FMT=CSV|BIN|BOTH\n"
    "# CLK=<mhz>    24..600, sous-cadencer reduit le champ parasite\n"
    "# SD=ON|OFF    UDP=ON|OFF    IP=a.b.c.d    PORT=<n>\n"
    "# ZERO         remise a zero des compteurs\n"
    "# SAVE         enregistre en EEPROM"));
}

void stat() {
  Serial.printf("# echantillons=%lu trames=%lu drdy=%lu\n",
                (unsigned long)health.samples, (unsigned long)health.frames,
                (unsigned long)g_drdyCount);
  Serial.printf("# timeouts=%lu spi=%lu saturations=%lu sd=%lu udp=%lu\n",
                (unsigned long)health.drdyTimeouts,
                (unsigned long)health.spiErrors,
                (unsigned long)health.saturations,
                (unsigned long)health.sdErrors,
                (unsigned long)health.udpErrors);
  Serial.printf("# flags=0x%04X  temperature=%s  mode=%s\n", g_flags,
                g_haveTemp ? "MCP9808" : "absente",
                g_usePolling ? "scrutation" : "interruption DRDY");
}

void handleLine(char *s) {
  while (*s == ' ') s++;
  for (char *p = s; *p; p++) if (*p >= 'a' && *p <= 'z') *p -= 32;

  if (!strcmp(s, "?") || !strcmp(s, "HELP")) { help(); return; }
  if (!strcmp(s, "ID")) {
    Serial.printf("# RM3100 REVID=0x%02X firmware=%s gain=%.1f LSB/uT "
                  "(%.2f nT/LSB)\n", rmRead8(REG_REVID), FW_VERSION,
                  rmGain(cfg.cycleCount), g_nT_per_lsb);
    return;
  }
  if (!strcmp(s, "STAT")) { stat(); return; }
  if (!strcmp(s, "BIST")) { rmSelfTest(); return; }
  if (!strcmp(s, "ZERO")) { memset(&health, 0, sizeof(health));
                            Serial.println(F("# compteurs remis a zero"));
                            return; }
  if (!strcmp(s, "SAVE")) { cfgSave(); return; }

  if (!strncmp(s, "CC=", 3)) {
    long v = atol(s + 3);
    if (v < 50 || v > 800) { Serial.println(F("# CC hors bornes (50..800)"));
                             return; }
    cfg.cycleCount = (uint16_t)v;
    rmConfigure();
    Serial.printf("# CC=%u -> %.2f nT/LSB\n", cfg.cycleCount, g_nT_per_lsb);
    if (v > 400 && tmrcRate(cfg.tmrc) > 40.0f)
      Serial.println(F("# ATTENTION : a CC>400 le capteur ne suit pas au-dela "
                       "de ~40 Hz. Passer TMRC=96."));
    return;
  }
  if (!strncmp(s, "TMRC=", 5)) {
    long v = strtol(s + 5, nullptr, 16);
    if (v < 0x92 || v > 0x9D) { Serial.println(F("# TMRC hors bornes"));
                                return; }
    cfg.tmrc = (uint8_t)v;
    rmConfigure();
    Serial.printf("# TMRC=0x%02X -> %.1f Hz\n", cfg.tmrc, tmrcRate(cfg.tmrc));
    return;
  }
  if (!strncmp(s, "OUT=", 4)) {
    float v = atof(s + 4);
    if (v < 0.01f || v > 200.0f) { Serial.println(F("# OUT hors bornes"));
                                   return; }
    cfg.outRateHz = v;
    Serial.printf("# sortie a %.2f Hz (%.0f echantillons moyennes)\n",
                  v, tmrcRate(cfg.tmrc) / v);
    return;
  }
  if (!strncmp(s, "FMT=", 4)) {
    if (!strcmp(s + 4, "CSV")) cfg.fmt = 0;
    else if (!strcmp(s + 4, "BIN")) cfg.fmt = 1;
    else if (!strcmp(s + 4, "BOTH")) cfg.fmt = 2;
    else { Serial.println(F("# FMT=CSV|BIN|BOTH")); return; }
    Serial.printf("# format %u\n", cfg.fmt);
    return;
  }
  if (!strncmp(s, "CLK=", 4)) {
    long v = atol(s + 4);
    if (v < 24 || v > 600) { Serial.println(F("# CLK hors bornes (24..600)"));
                             return; }
    cfg.cpuMHz = (uint16_t)v;
    applyCpuClock();
    Serial.printf("# processeur a %u MHz\n", cfg.cpuMHz);
    return;
  }
  if (!strncmp(s, "SD=", 3)) {
    cfg.sdEnable = !strcmp(s + 3, "ON");
    sdOpen();
    return;
  }
  if (!strncmp(s, "UDP=", 4)) {
    cfg.udpEnable = !strcmp(s + 4, "ON");
    ethStart();
    return;
  }
  if (!strncmp(s, "IP=", 3)) {
    int a, b, c, d;
    if (sscanf(s + 3, "%d.%d.%d.%d", &a, &b, &c, &d) == 4) {
      cfg.ip[0] = a; cfg.ip[1] = b; cfg.ip[2] = c; cfg.ip[3] = d;
      Serial.printf("# destination %d.%d.%d.%d\n", a, b, c, d);
    } else Serial.println(F("# IP=a.b.c.d"));
    return;
  }
  if (!strncmp(s, "PORT=", 5)) {
    cfg.port = (uint16_t)atol(s + 5);
    Serial.printf("# port %u\n", cfg.port);
    return;
  }
  if (*s) Serial.println(F("# commande inconnue, tapez ?"));
}

void pollSerial() {
  static char buf[64];
  static uint8_t n = 0;
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\r') continue;
    if (c == '\n') { buf[n] = 0; handleLine(buf); n = 0; continue; }
    if (n < sizeof(buf) - 1) buf[n++] = c;
  }
}

/* =========================================================================
 * 10. BOUCLE PRINCIPALE
 * ========================================================================= */
void loop() {
  pollSerial();

  static uint32_t lastSample = 0;
  bool ready = false;
  uint32_t stamp = 0;

  if (g_usePolling) {
    float per_us = 1000000.0f / tmrcRate(cfg.tmrc);
    if ((micros() - lastSample) >= (uint32_t)per_us) {
      if (rmRead8(REG_STATUS) & 0x80) { ready = true; stamp = micros(); }
    }
  } else if (g_drdyFlag) {
    noInterrupts();
    stamp = g_drdyMicros;
    g_drdyFlag = false;
    interrupts();
    ready = true;
  }

  /* surveillance : le capteur a-t-il cesse de produire ? */
  static uint32_t lastReady = 0;
  if (ready) lastReady = millis();
  else if (millis() - lastReady > 2000) {
    health.drdyTimeouts++;
    g_flags |= F_DRDY_TIMEOUT;
    lastReady = millis();
    Serial.println(F("# Capteur muet depuis 2 s : reconfiguration."));
    rmConfigure();
  }

  if (ready) {
    lastSample = stamp;
    uint8_t b[9];
    rmRead(REG_MX, b, 9);
    int32_t rx = s24(b), ry = s24(b + 3), rz = s24(b + 6);

    /* saturation : le convertisseur est en butee */
    const int32_t SAT = 0x7F0000L;
    if (labs(rx) > SAT || labs(ry) > SAT || labs(rz) > SAT) {
      health.saturations++;
      g_flags |= F_SATURATION;
    }

    acc[0] += (double)rx * g_nT_per_lsb;
    acc[1] += (double)ry * g_nT_per_lsb;
    acc[2] += (double)rz * g_nT_per_lsb;
    if (accN == 0) accT = (uint64_t)stamp;
    accN++;
    health.samples++;
    g_flags &= ~F_DRDY_TIMEOUT;
  }

  /* emission a la cadence demandee */
  float ratio = tmrcRate(cfg.tmrc) / cfg.outRateHz;
  uint32_t need = (ratio < 1.0f) ? 1u : (uint32_t)ratio;
  if (accN >= need) {
    float tC = g_haveTemp ? tempRead() : NAN;
    /* horodatage au CENTRE de la fenetre de moyennage : c'est la date que
       represente reellement la valeur moyenne. */
    uint64_t tmid = accT + (uint64_t)((accN - 1) * 500000.0f
                                      / tmrcRate(cfg.tmrc));
    emitFrame(tmid, acc[0] / accN, acc[1] / accN, acc[2] / accN,
              (uint16_t)accN, tC);
    acc[0] = acc[1] = acc[2] = 0.0;
    accN = 0;
  }
  /* Pas de clignotant : sur Teensy 4.x la LED partage la broche 13 avec
     SCK. L'allumer pendant une transaction SPI corromprait l'horloge. */
}
