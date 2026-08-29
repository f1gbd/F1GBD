/* =========================================================================
 * provisioning.cpp — le repondeur de configuration, sur le port USB
 * =========================================================================
 *
 * Voir osjt_provisioning.h pour le protocole et les raisons.
 *
 * Copyright 2026 F1GBD / F4JHW — ADRASEC 77 — Licence MIT
 * ========================================================================= */

#include <Arduino.h>
#include <Preferences.h>

#include "osjt_msgpack.h"
#include "osjt_provisioning.h"

/* --- constantes du fil, identiques a RWLoRa ----------------------------- */
#define FEND   0xC0
#define FESC   0xDB
#define TFEND  0xDC
#define TFESC  0xDD
#define CMD_PROVISION_REQ 0x86
#define CMD_PROVISION_RSP 0x87

static const int32_t OP_GET_STATE = 4;
static const int32_t OP_SET_STATE = 5;
static const int32_t OP_COMMIT    = 6;
static const int32_t OP_REBOOT    = 9;
static const int32_t OP_ACK       = 100;
static const int32_t OP_ERROR     = 101;

static const int32_t NS_NET   = 101;
static const int32_t FLD_SSID = 1;
static const int32_t FLD_PASS = 2;
static const int32_t FLD_HOST = 3;
static const int32_t FLD_PORT = 4;

/* Codes d'erreur : ceux de microReticulum, pour que la console affiche les
 * memes libelles pour les deux appareils. */
static const int32_t E_MALFORMED = 1;
static const int32_t E_UNKNOWN_OP = 2;
static const int32_t E_UNKNOWN_NS = 3;
static const int32_t E_BAD_VALUE = 5;
static const int32_t E_STORAGE = 8;

/* --- etat --------------------------------------------------------------- */
static OsjtNetConfig _cfg;
static bool _dirty = false;          /* modifie mais pas encore ecrit */
static bool _reboot = false;         /* modifie depuis le demarrage */
static Preferences _nvs;

/* Un mot sur la taille : la plus grosse requete possible est un SET_STATE
 * portant les quatre champs au maximum, soit environ 180 octets. 512 laisse
 * de la marge sans immobiliser de memoire pour rien. */
static const uint16_t RX_MAX = 512;
static uint8_t _rx[RX_MAX];
static uint16_t _rxlen = 0;
static bool _escaped = false, _overflow = false;
static uint8_t _command = 0;
/* Meme automate que le lecteur KISS de la console, dans l'autre sens. */
enum RxState { RX_IDLE, RX_CMD, RX_FRAME };
static RxState _state = RX_IDLE;

/* --- persistance -------------------------------------------------------- */
/* Le WiFi de l'ESP32 sait deja garder des identifiants en flash, mais il les
 * reecrit a chaque association : sur une tete qui redemarre a chaque coupure
 * solaire, c'est de l'usure pour rien. On tient donc nos propres cles, et le
 * pilote WiFi tourne en persistent(false). */
static const char *NVS_NS = "osjt-net";

static void loadConfig() {
  memset(&_cfg, 0, sizeof(_cfg));
  _cfg.port = 10077;
  if (!_nvs.begin(NVS_NS, true)) return;      /* jamais ecrit : valeurs nulles */
  String s = _nvs.getString("ssid", "");
  String p = _nvs.getString("pass", "");
  String h = _nvs.getString("host", "");
  uint16_t pt = (uint16_t)_nvs.getUShort("port", 10077);
  _nvs.end();
  strncpy(_cfg.ssid, s.c_str(), OSJT_PROV_SSID_MAX);
  strncpy(_cfg.pass, p.c_str(), OSJT_PROV_PASS_MAX);
  strncpy(_cfg.host, h.c_str(), OSJT_PROV_HOST_MAX);
  if (pt >= 1) _cfg.port = pt;
}

static bool saveConfig() {
  if (!_nvs.begin(NVS_NS, false)) return false;
  bool ok = true;
  ok &= _nvs.putString("ssid", _cfg.ssid) >= 0;
  ok &= _nvs.putString("pass", _cfg.pass) >= 0;
  ok &= _nvs.putString("host", _cfg.host) >= 0;
  ok &= _nvs.putUShort("port", _cfg.port) > 0;
  _nvs.end();
  return ok;
}

const OsjtNetConfig &osjtProvConfig() { return _cfg; }
bool osjtProvNeedsReboot() { return _reboot; }

/* --- emission ----------------------------------------------------------- */
static void kissWrite(uint8_t b) {
  if (b == FEND)      { Serial.write(FESC); Serial.write(TFEND); }
  else if (b == FESC) { Serial.write(FESC); Serial.write(TFESC); }
  else                  Serial.write(b);
}

static void kissSend(const uint8_t *p, uint16_t n) {
  Serial.write(FEND);
  Serial.write(CMD_PROVISION_RSP);
  for (uint16_t i = 0; i < n; i++) kissWrite(p[i]);
  Serial.write(FEND);
  Serial.flush();
}

static void sendError(int32_t seq, int32_t code, const char *msg) {
  uint8_t buf[128];
  MpWriter w; w.init(buf, sizeof buf);
  w.array(3); w.sint(OP_ERROR); w.sint(seq);
  w.map(2); w.uint(1); w.sint(code); w.uint(2); w.str(msg);
  if (!w.ovf) kissSend(buf, w.len);
}

/* --- traitement des operations ------------------------------------------ */

/* GET_STATE. La requete porte {1: [liste de namespaces]} ; on rend ceux
 * qu'on connait, sans se plaindre de ceux qu'on ne connait pas — une
 * console qui interroge aussi le namespace radio 100 n'est pas en faute,
 * elle parle simplement a un appareil qui n'a pas de radio a regler. */
static void doGetState(int32_t seq, MpReader &r) {
  uint8_t buf[256];
  MpWriter w; w.init(buf, sizeof buf);
  w.array(3); w.sint(OP_ACK); w.sint(seq);
  w.map(1);
    w.sint(NS_NET);
    /* Trois champs : le mot de passe n'est jamais rendu. */
    w.map(3);
      w.sint(FLD_SSID); w.str(_cfg.ssid);
      w.sint(FLD_HOST); w.str(_cfg.host);
      w.sint(FLD_PORT); w.uint(_cfg.port);
  (void)r;
  if (w.ovf) { sendError(seq, E_STORAGE, "reponse trop longue"); return; }
  kissSend(buf, w.len);
}

/* SET_STATE. La requete porte {ns: {champ: valeur}}. Les champs refuses
 * sont RENDUS, pas ignores : une console qui croit avoir ecrit une valeur
 * que la tete a rejetee est le debut d'une longue soiree. */
static void doSetState(int32_t seq, MpReader &r) {
  int32_t rejected[8];
  uint8_t nrej = 0;
  bool unknownNs = false;
  /* Local, et non _dirty : _dirty peut rester vrai d'un SET_STATE precedent
   * non encore valide, ce qui ferait passer pour traitee une requete qui ne
   * portait que des namespaces inconnus. */
  bool touched = false;

  uint16_t nns = 0;
  if (!r.map(nns)) { sendError(seq, E_MALFORMED, "payload attendu : table"); return; }

  for (uint16_t i = 0; i < nns && r.ok(); i++) {
    int32_t ns = 0;
    if (!r.sint(ns)) { sendError(seq, E_MALFORMED, "namespace illisible"); return; }
    if (ns != NS_NET) { unknownNs = true; r.skip(); continue; }
    touched = true;

    uint16_t nf = 0;
    if (!r.map(nf)) { sendError(seq, E_MALFORMED, "champs attendus : table"); return; }
    for (uint16_t j = 0; j < nf && r.ok(); j++) {
      int32_t fid = 0;
      if (!r.sint(fid)) { sendError(seq, E_MALFORMED, "champ illisible"); return; }

      if (fid == FLD_PORT) {
        int32_t v = 0;
        if (!r.sint(v)) { sendError(seq, E_BAD_VALUE, "port : entier attendu"); return; }
        if (v < 1 || v > 65535) {
          if (nrej < 8) rejected[nrej++] = fid;
        } else if (_cfg.port != (uint16_t)v) {
          _cfg.port = (uint16_t)v; _dirty = true; _reboot = true;
        }
        continue;
      }

      char tmp[OSJT_PROV_PASS_MAX + 1];
      if (!r.str(tmp, sizeof tmp)) {
        /* Chaine trop longue pour le champ, ou type inattendu. Le lecteur
         * est en erreur : on ne peut plus rien lire de fiable ensuite. */
        sendError(seq, E_BAD_VALUE, "chaine invalide ou trop longue");
        return;
      }
      char *dst = nullptr;
      uint16_t cap = 0;
      if (fid == FLD_SSID)      { dst = _cfg.ssid; cap = OSJT_PROV_SSID_MAX; }
      else if (fid == FLD_PASS) { dst = _cfg.pass; cap = OSJT_PROV_PASS_MAX; }
      else if (fid == FLD_HOST) { dst = _cfg.host; cap = OSJT_PROV_HOST_MAX; }
      else { if (nrej < 8) rejected[nrej++] = fid; continue; }

      if (strlen(tmp) > cap) { if (nrej < 8) rejected[nrej++] = fid; continue; }
      if (strcmp(dst, tmp) != 0) {
        strncpy(dst, tmp, cap);
        dst[cap] = 0;
        _dirty = true;
        _reboot = true;
      }
    }
  }

  if (!r.ok()) { sendError(seq, E_MALFORMED, "requete tronquee"); return; }
  if (unknownNs && !touched && nrej == 0) {
    sendError(seq, E_UNKNOWN_NS, "cette tete n'expose que le namespace 101");
    return;
  }

  uint8_t buf[96];
  MpWriter w; w.init(buf, sizeof buf);
  w.array(3); w.sint(OP_ACK); w.sint(seq);
  if (nrej) {
    w.map(1); w.uint(3); w.array(nrej);
    for (uint8_t i = 0; i < nrej; i++) w.sint(rejected[i]);
  } else {
    w.map(0);
  }
  if (!w.ovf) kissSend(buf, w.len);
}

/* COMMIT : ecrit en flash. La reponse porte {1: 1} si un redemarrage est
 * necessaire pour que les valeurs prennent effet — ce qui est toujours le
 * cas ici, le WiFi ne se reconfigurant pas a chaud. */
static void doCommit(int32_t seq) {
  if (_dirty && !saveConfig()) {
    sendError(seq, E_STORAGE, "ecriture en memoire non volatile impossible");
    return;
  }
  _dirty = false;
  uint8_t buf[32];
  MpWriter w; w.init(buf, sizeof buf);
  w.array(3); w.sint(OP_ACK); w.sint(seq);
  w.map(1); w.uint(1); w.uint(_reboot ? 1 : 0);
  if (!w.ovf) kissSend(buf, w.len);
}

static void handleFrame(const uint8_t *p, uint16_t n) {
  MpReader r; r.init(p, n);
  uint16_t na = 0;
  if (!r.array(na) || na != 3) { sendError(0, E_MALFORMED, "enveloppe attendue : [op, seq, payload]"); return; }
  int32_t op = 0, seq = 0;
  if (!r.sint(op) || !r.sint(seq)) { sendError(0, E_MALFORMED, "entete illisible"); return; }

  if (op == OP_GET_STATE)      doGetState(seq, r);
  else if (op == OP_SET_STATE) doSetState(seq, r);
  else if (op == OP_COMMIT)    doCommit(seq);
  else if (op == OP_REBOOT) {
    /* Aucune reponse : la console n'en attend pas, et la tete ne sera plus
     * la pour l'emettre. On laisse le port se vider d'abord. */
    Serial.println(F("# redemarrage demande par la console."));
    Serial.flush();
    delay(150);
    ESP.restart();
  }
  else sendError(seq, E_UNKNOWN_OP, "operation non geree par cette tete");
}

/* --- reception ---------------------------------------------------------- */
void osjtProvBegin() {
  loadConfig();
  Serial.printf("# reseau : SSID '%s' -> %s:%u\n",
                _cfg.ssid,
                _cfg.host[0] ? _cfg.host : "(diffusion sur le sous-reseau)",
                (unsigned)_cfg.port);
  if (_cfg.ssid[0] == 0)
    Serial.println(F("# aucun WiFi configure — onglet Firmware, "
                     "« Configuration WiFi du capteur »."));
}

void osjtProvLoop() {
  while (Serial.available()) {
    uint8_t b = (uint8_t)Serial.read();

    if (b == FEND) {
      if (_state == RX_FRAME && _command == CMD_PROVISION_REQ
          && _rxlen && !_overflow)
        handleFrame(_rx, _rxlen);
      /* Un FEND ferme la trame courante ET ouvre la suivante : l'octet
       * d'apres est une commande. */
      _state = RX_CMD;
      _escaped = false;
      _overflow = false;
      _rxlen = 0;
      _command = 0;
      continue;
    }

    if (_state == RX_CMD) {
      _command = b;
      /* Un octet qui n'est pas une commande de provisioning : c'etait un
       * FEND isole au milieu d'autre chose. On repasse en attente plutot
       * que d'accumuler du bruit. */
      _state = (b == CMD_PROVISION_REQ) ? RX_FRAME : RX_IDLE;
      continue;
    }
    if (_state != RX_FRAME) continue;

    if (_escaped) {
      if (b == TFEND) b = FEND;
      else if (b == TFESC) b = FESC;
      _escaped = false;
    } else if (b == FESC) {
      _escaped = true;
      continue;
    }
    if (_rxlen < RX_MAX) _rx[_rxlen++] = b;
    else _overflow = true;            /* trame aberrante : on la laissera tomber */
  }
}
