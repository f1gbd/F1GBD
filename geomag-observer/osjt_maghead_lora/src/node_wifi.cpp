/* =========================================================================
 * node_wifi.cpp — la tete magnetique en WiFi : RM3100 -> UDP sur le reseau
 * =========================================================================
 *
 * Meme carte, meme capteur, meme brochage que la tete LoRa. Ce qui change
 * est le transport, et ce que ce transport permet.
 *
 * CE QUE LE WiFi APPORTE
 * ----------------------
 * Il n'y a plus de rapport cyclique a respecter. La tete LoRa doit tenir
 * dans 1 % du temps d'antenne : elle groupe donc la minute et n'emet qu'une
 * trame. En WiFi elle emet a la CADENCE D'ACQUISITION — une seconde par
 * defaut. Le dB/dt gagne en fidelite, et l'onglet Sante recoit enfin un flux
 * continu sur lequel calculer un spectre.
 *
 * Il n'y a plus de passerelle non plus : la tete parle directement au PC.
 * Une carte au lieu de deux.
 *
 * CE QUE LE WiFi COUTE, ET QU'IL NE FAUT PAS SE CACHER
 * ---------------------------------------------------
 * 1. LA CONSOMMATION. Une station associee tire une soixantaine de
 *    milliamperes en moyenne, contre une vingtaine pour la tete LoRa. Sur
 *    3000 mAh cela fait un jour et demi au lieu de cinq jours et demi :
 *    LA TETE WiFi VEUT LE SECTEUR. L'entree solaire du V4 ne suit pas.
 *
 * 2. LE FENETRAGE N'EST PLUS COMPLET. La tete LoRa sait a la microseconde
 *    pres quand elle emet, et jette les echantillons de sa fenetre
 *    d'emission. Une station WiFi associee, elle, recoit les balises de son
 *    point d'acces, les ARP et les retransmissions SUR L'HORLOGE DU POINT
 *    D'ACCES — 1 a 3 % du temps, imprevisible. On fenetre donc ce qu'on
 *    maitrise, notre propre emission, et on ne pretend pas fenetrer le
 *    reste.
 *
 *    Ce n'est pas grave si le deport est suffisant. Le WiFi tire environ
 *    350 mA en crete contre 135 mA pour le SX1262, soit un facteur 2,6 en
 *    courant et donc 1,37 en distance, le champ d'une boucle decroissant en
 *    1/r cube : LES 30 cm DE LA TETE LoRa DEVIENNENT 41 cm ICI. Les 50 cm
 *    recommandes dans la fiche de cablage laissent la marge.
 *
 * 3. LA COUPURE RESEAU EST UN TROU DANS LA DONNEE. Rien n'est mis en
 *    reserve pour etre reemis plus tard : une trame qui n'est pas partie
 *    est perdue, et le PC verra un trou — exactement comme pour une
 *    coupure de liaison LoRa. Reemettre des minutes anciennes en vrac
 *    desordonnerait la serie pour rattraper des points que l'operateur
 *    aurait de toute facon vu manquer.
 *
 * LE FORMAT SUR LE FIL
 * --------------------
 * Un datagramme UDP = une trame de 36 octets, celle du firmware Teensy, que
 * GEOMAG-Observer decode deja. Pas de nouveau protocole cote PC : le
 * decodeur eprouve, son CRC et son autotest servent tels quels.
 *
 * Le CRC de la trame suffit a se proteger de la corruption ; UDP ne
 * garantit rien d'autre, et c'est bien ainsi. TCP retransmettrait un
 * echantillon vieux de plusieurs secondes en le faisant passer pour frais,
 * ce qui est pire qu'un trou franc pour une serie temporelle.
 *
 * Copyright 2026 F1GBD / F4JHW — ADRASEC 77 — Licence MIT
 * ========================================================================= */

#include <Arduino.h>
#include <SPI.h>
#include <WiFi.h>
#include <WiFiUdp.h>

#include "osjt_oled.h"
#include "osjt_pins.h"
#include "osjt_provisioning.h"
#include "osjt_teensy_frame.h"
#include "rm3100.h"

#ifndef OSJT_TMRC
#define OSJT_TMRC 0x96
#endif
#ifndef OSJT_CYCLE_COUNT
#define OSJT_CYCLE_COUNT 800
#endif
#ifndef OSJT_OLED_BOOT_S
#define OSJT_OLED_BOOT_S 20
#endif

/* Periode d'agregation. Une seconde : c'est la cadence a laquelle la chaine
 * de traitement du PC a ete eprouvee, et celle qui rend le dB/dt le plus
 * juste (3,00 nT/min sur une rampe de reference a 3 nT/min, contre 3,43 a
 * une trame par minute). */
#ifndef OSJT_WIFI_PERIOD_MS
#define OSJT_WIFI_PERIOD_MS 1000
#endif

/* Fenetre de garde autour de NOTRE emission. Un datagramme UDP part en
 * quelques millisecondes ; 20 ms de part et d'autre couvrent la salve du
 * PA sans amputer la mesure. */
static const uint32_t TX_GUARD_MS = 20;

/* Bornes de la reconnexion : un point d'acces absent ne doit pas faire
 * tourner la carte en boucle serree. Memes valeurs que RWLoRa. */
static const uint32_t RETRY_MIN_MS = 2000;
static const uint32_t RETRY_MAX_MS = 60000;

static SPIClass spiRm(FSPI);
static RM3100 mag(spiRm, PIN_RM_CS, PIN_RM_DRDY);
static WiFiUDP udp;

static double sum[3];
static uint32_t nAcc = 0;
static uint32_t periodStart = 0;
static uint32_t seq = 0;
static uint16_t flags = 0;
static bool txBlank = false;

static IPAddress dest;
static bool destKnown = false;
static uint32_t nSent = 0, nLost = 0;
static uint32_t nextRetry = 0;
static uint16_t failCount = 0;
static bool wasOnline = false;

/* --- destination ---------------------------------------------------------
 *
 * Hote vide = DIFFUSION SUR LE SOUS-RESEAU. C'est volontaire : un operateur
 * qui pose une tete ne connait pas forcement l'adresse IP de son PC, et
 * celle-ci change au gre du bail DHCP. La diffusion dirigee atteint le PC
 * sans rien savoir de lui, et l'application ecoute deja sur toutes les
 * interfaces. Un datagramme de 36 octets par seconde sur un reseau
 * domestique ne derange personne.
 *
 * Certains points d'acces filtrent la diffusion entre clients WiFi. Si
 * rien n'arrive, saisir l'adresse du PC dans le champ « Hote » : c'est le
 * premier reflexe, et le manuel le dit. */
static bool resolveDest() {
  const OsjtNetConfig &c = osjtProvConfig();
  if (c.host[0] == 0) {
    IPAddress ip = WiFi.localIP();
    IPAddress mk = WiFi.subnetMask();
    for (uint8_t i = 0; i < 4; i++) dest[i] = ip[i] | (uint8_t)~mk[i];
    return true;
  }
  if (dest.fromString(c.host)) return true;
  return WiFi.hostByName(c.host, dest) == 1;
}

/* --- emission ------------------------------------------------------------ */
static void sendSample(float bx, float by, float bz, uint16_t n) {
  if (WiFi.status() != WL_CONNECTED || !destKnown) { nLost++; return; }

  OsjtTeensyFrame f;
  osjt_teensy_build(&f, seq++, (uint64_t)millis() * 1000ULL,
                    bx, by, bz, n, -32768, flags);

  txBlank = true;
  const uint32_t t0 = millis();
  bool ok = udp.beginPacket(dest, osjtProvConfig().port) == 1;
  if (ok) {
    udp.write((const uint8_t *)&f, OSJT_TEENSY_LEN);
    ok = udp.endPacket() == 1;
  }
  while (millis() - t0 < TX_GUARD_MS) delay(1);
  txBlank = false;

  if (ok) nSent++;
  else nLost++;
}

/* --- supervision du lien ------------------------------------------------- */
static void wifiStart() {
  const OsjtNetConfig &c = osjtProvConfig();
  if (c.ssid[0] == 0) return;
  WiFi.mode(WIFI_STA);
  /* Le pilote WiFi ne doit PAS reecrire ses identifiants en flash a chaque
   * demarrage : sur une tete qui redemarre a chaque coupure d'alimentation
   * c'est de l'usure pour rien, et nos identifiants viennent de toute
   * facon du provisioning. */
  WiFi.persistent(false);
  WiFi.setAutoReconnect(true);
  WiFi.begin(c.ssid, c.pass);
}

static void wifiSupervise() {
  const bool up = (WiFi.status() == WL_CONNECTED);

  if (up && !wasOnline) {
    wasOnline = true;
    failCount = 0;
    destKnown = resolveDest();
    Serial.printf("# WiFi associe — IP %s, RSSI %d dBm\n",
                  WiFi.localIP().toString().c_str(), (int)WiFi.RSSI());
    if (destKnown)
      Serial.printf("# destination %s:%u%s\n", dest.toString().c_str(),
                    (unsigned)osjtProvConfig().port,
                    osjtProvConfig().host[0] ? "" : "  (diffusion)");
    else
      Serial.printf("# ATTENTION : '%s' ne se resout pas. Le DNS du point "
                    "d'acces repond-il ?\n", osjtProvConfig().host);
    return;
  }

  if (!up && wasOnline) {
    wasOnline = false;
    destKnown = false;
    Serial.println(F("# WiFi perdu — les mesures de la coupure seront "
                     "absentes de la serie."));
  }

  if (up || osjtProvConfig().ssid[0] == 0) return;

  /* Backoff exponentiel plafonne. WiFi.setAutoReconnect travaille en tache
   * de fond ; on ne relance explicitement que si cela dure. */
  const uint32_t now = millis();
  if (now < nextRetry) return;
  failCount++;
  uint32_t wait = RETRY_MIN_MS;
  for (uint16_t i = 1; i < failCount && wait < RETRY_MAX_MS; ++i) wait *= 2;
  if (wait > RETRY_MAX_MS) wait = RETRY_MAX_MS;
  nextRetry = now + wait;
  if (failCount <= 5)
    Serial.printf("# WiFi : pas d'association, nouvelle tentative dans "
                  "%lu s.\n", (unsigned long)(wait / 1000));
  WiFi.disconnect();
  wifiStart();
}

/* --- autotest de mise en service -----------------------------------------
 *
 * Le meme que la tete LoRa, augmente de l'etat du reseau : ce que l'on veut
 * savoir avant de refermer le boitier, c'est que le capteur mesure vraiment
 * le champ terrestre ET que la tete a trouve son point d'acces. Sinon on
 * repart avec un mat installe et rien qui arrive.
 */
static void nodeWifiBootCheck(bool magOk, bool bistOk) {
  char l1[24], l2[24], l3[24], l4[24];

  osjtOledStatus("GEOMAG-Observer", "Tete magnetique WiFi",
                 "version " OSJT_FW_VERSION, "autotest en cours...");
  delay(2000);

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

  const bool fieldOk = (n >= 40) && (favg > 20000.0) && (favg < 70000.0);
  const bool noiseOk = fieldOk && (sd < 50.0);

  /* On laisse au WiFi le temps restant de l'ecran d'accueil pour
   * s'associer, plutot que de conclure a l'echec au bout de deux secondes.
   * Le provisioning reste servi pendant cette attente : une tete mal
   * configuree peut ainsi etre corrigee sans redemarrer. */
  const uint32_t total = (uint32_t)OSJT_OLED_BOOT_S * 1000UL;
  while (millis() - t0 + 2000 < total && WiFi.status() != WL_CONNECTED) {
    osjtProvLoop();
    delay(50);
  }
  const bool netOk = (WiFi.status() == WL_CONNECTED);
  if (netOk) {
    destKnown = resolveDest();
    wasOnline = true;
  }

  const bool allOk = magOk && bistOk && fieldOk && noiseOk && netOk;

  Serial.printf("# autotest : capteur %s, BIST %s, WiFi %s\n",
                magOk ? "OK" : "MUET", bistOk ? "OK" : "ECHEC",
                netOk ? "OK" : "NON ASSOCIE");
  Serial.printf("# |F| = %.0f nT, ecart-type %.1f nT sur %lu echantillons\n",
                favg, sd, (unsigned long)n);
  Serial.printf("# VERDICT : %s\n", allOk ? "OPERATIONNEL"
                                          : "DEFAUT - ne pas refermer");

  if (!magOk)              snprintf(l1, sizeof l1, "CAPTEUR MUET");
  else if (!fieldOk)       snprintf(l1, sizeof l1, "MESURE INVALIDE");
  else if (!noiseOk)       snprintf(l1, sizeof l1, "BRUIT ELEVE");
  else if (!netOk)         snprintf(l1, sizeof l1, "PAS DE WIFI");
  else                     snprintf(l1, sizeof l1, "OPERATIONNEL");

  snprintf(l2, sizeof l2, "|F| %.0f nT", favg);
  snprintf(l3, sizeof l3, "bruit %.1f nT  n=%lu", sd, (unsigned long)n);
  if (netOk)
    snprintf(l4, sizeof l4, "%s", WiFi.localIP().toString().c_str());
  else if (osjtProvConfig().ssid[0] == 0)
    snprintf(l4, sizeof l4, "non configure");
  else
    snprintf(l4, sizeof l4, "SSID %.14s ?", osjtProvConfig().ssid);
  osjtOledStatus(l1, l2, l3, l4);

  /* Le verdict reste affiche cinq secondes, puis l'ecran s'eteint pour de
   * bon : ses 15 mA n'ont rien a faire dans la premiere valeur publiee. */
  delay(5000);
  osjtOledOff();
  Serial.println(F("# ecran coupe, debut des mesures."));
}

/* --- API appelee par main.cpp -------------------------------------------- */
void nodeWifiSetup() {
  /* 80 MHz : c'est le minimum pour que la radio WiFi fonctionne, et cela
   * suffit tres largement a lire un capteur a quelques dizaines de hertz.
   * Moins de calcul, moins de courant, moins de signature magnetique. */
  setCpuFrequencyMhz(80);
  Serial.begin(115200);
  delay(200);
  Serial.printf("# OSJT maghead WiFi %s — tete magnetique\n",
                OSJT_FW_VERSION);

  osjtProvBegin();

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

  wifiStart();
  udp.begin(0);   /* port source quelconque : la tete n'attend rien */

  osjtOledBegin("Tete WiFi");
  Serial.printf("# cadence d'emission : une trame toutes les %lu ms\n",
                (unsigned long)OSJT_WIFI_PERIOD_MS);

  for (uint8_t a = 0; a < 3; a++) sum[a] = 0.0;
  nAcc = 0;
  nodeWifiBootCheck(magOk, bistOk);
  for (uint8_t a = 0; a < 3; a++) sum[a] = 0.0;
  nAcc = 0;
  periodStart = millis();
}

void nodeWifiLoop() {
  const uint32_t now = millis();

  osjtProvLoop();

  if (!txBlank && mag.dataReady()) {
    float b[3];
    if (mag.read(b[0], b[1], b[2])) {
      for (uint8_t a = 0; a < 3; a++) sum[a] += b[a];
      nAcc++;
    } else {
      flags |= OSJT_FLAG_SAT;
    }
  }

  if (now - periodStart >= OSJT_WIFI_PERIOD_MS) {
    if (nAcc >= 1) {
      sendSample((float)(sum[0] / nAcc), (float)(sum[1] / nAcc),
                 (float)(sum[2] / nAcc), (uint16_t)nAcc);
    }
    for (uint8_t a = 0; a < 3; a++) sum[a] = 0.0;
    nAcc = 0;
    flags = 0;
    periodStart += OSJT_WIFI_PERIOD_MS;
    /* Un demarrage tardif ou une longue coupure peuvent laisser periodStart
     * loin derriere : on se recale plutot que d'emettre une rafale pour
     * rattraper un temps qui n'a pas ete mesure. */
    if (now - periodStart > 5UL * OSJT_WIFI_PERIOD_MS) periodStart = now;
  }

  wifiSupervise();

  /* Un signe de vie toutes les cinq minutes : sur une liaison silencieuse,
   * l'absence de trame est ambigue. Cette ligne tranche. */
  static uint32_t lastStat = 0;
  if (now - lastStat > 300000UL) {
    lastStat = now;
    Serial.printf("# tete WiFi : %lu trames emises, %lu perdues, RSSI %d dBm\n",
                  (unsigned long)nSent, (unsigned long)nLost,
                  wasOnline ? (int)WiFi.RSSI() : 0);
  }

  delay(1);
}
