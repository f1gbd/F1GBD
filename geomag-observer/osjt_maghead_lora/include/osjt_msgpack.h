/* =========================================================================
 * osjt_msgpack.h — le sous-ensemble de MsgPack dont le provisioning a besoin
 * =========================================================================
 *
 * POURQUOI PAS UNE BIBLIOTHEQUE
 * -----------------------------
 * Le dialogue de configuration echange exactement quatre formes :
 *
 *     [op, seq, nil]                          COMMIT, REBOOT
 *     [op, seq, {1: [101]}]                   GET_STATE
 *     [op, seq, {101: {1:"...", 4: 10077}}]   SET_STATE
 *     [op, seq, {1: 5, 2: "..."}]             ERROR
 *
 * Des entiers, des chaines, des tableaux et des tables de moins de seize
 * elements. Tirer une bibliotheque generique — ses templates, ses
 * allocations, ses flottants, ses extensions — pour cela, c'est ajouter
 * quelques kilo-octets et une dependance a un firmware qui doit tenir des
 * mois sur batterie, en echange de types dont aucun ne circule ici.
 *
 * Ce fichier ne compile RIEN d'Arduino : il se compile en natif, et c'est
 * ainsi qu'il est confronte a la bibliotheque msgpack de Python — la meme
 * que parle la console. Un codec ecrit a la main sans ce banc d'essai
 * serait une prise de risque ; avec lui, c'est une centaine de lignes
 * verifiees octet par octet.
 *
 * CE QUI EST VOLONTAIREMENT ABSENT
 * --------------------------------
 * Flottants, entiers 64 bits, chaines de plus de 65 535 octets, extensions,
 * tables de plus de 65 535 entrees. Rien de tout cela ne peut apparaitre
 * dans le dialogue ci-dessus ; si cela apparait, c'est que l'interlocuteur
 * n'est pas celui qu'on croit, et le decodeur doit echouer, pas deviner.
 *
 * Copyright 2026 F1GBD / F4JHW — ADRASEC 77 — Licence MIT
 * ========================================================================= */

#ifndef OSJT_MSGPACK_H
#define OSJT_MSGPACK_H

#include <stdint.h>
#include <string.h>

/* --- ecriture ------------------------------------------------------------
 *
 * Le tampon est fourni par l'appelant et sa taille est verifiee a chaque
 * ecriture. En cas de debordement le drapeau ovf est leve et TOUTES les
 * ecritures suivantes sont sans effet : on ne rend jamais une trame
 * tronquee en la faisant passer pour valide, c'est mp_ok() qui tranche.
 */
struct MpWriter {
  uint8_t *buf;
  uint16_t cap;
  uint16_t len;
  bool ovf;

  void init(uint8_t *b, uint16_t c) { buf = b; cap = c; len = 0; ovf = false; }

  void raw(uint8_t b) {
    if (ovf || len >= cap) { ovf = true; return; }
    buf[len++] = b;
  }
  void raw(const void *p, uint16_t n) {
    if (ovf || (uint32_t)len + n > cap) { ovf = true; return; }
    memcpy(buf + len, p, n);
    len = (uint16_t)(len + n);
  }
  /* MsgPack est gros-boutiste, contrairement a l'ESP32. */
  void be16(uint16_t v) { raw((uint8_t)(v >> 8)); raw((uint8_t)v); }
  void be32(uint32_t v) { be16((uint16_t)(v >> 16)); be16((uint16_t)v); }

  void nil() { raw(0xC0); }

  /* Encodage MINIMAL, comme le fait msgpack-python : c'est ce qui rend la
   * comparaison octet par octet possible dans le banc d'essai. */
  void uint(uint32_t v) {
    if (v < 128)        raw((uint8_t)v);
    else if (v < 256)   { raw(0xCC); raw((uint8_t)v); }
    else if (v < 65536) { raw(0xCD); be16((uint16_t)v); }
    else                { raw(0xCE); be32(v); }
  }
  void sint(int32_t v) {
    if (v >= 0) { uint((uint32_t)v); return; }
    if (v >= -32)          raw((uint8_t)(0xE0 | (v + 32)));
    else if (v >= -128)    { raw(0xD0); raw((uint8_t)(int8_t)v); }
    else if (v >= -32768)  { raw(0xD1); be16((uint16_t)(int16_t)v); }
    else                   { raw(0xD2); be32((uint32_t)v); }
  }
  void str(const char *s) {
    uint16_t n = s ? (uint16_t)strlen(s) : 0;
    if (n < 32)        raw((uint8_t)(0xA0 | n));
    else if (n < 256)  { raw(0xD9); raw((uint8_t)n); }
    else               { raw(0xDA); be16(n); }
    raw(s, n);
  }
  void array(uint16_t n) {
    if (n < 16) raw((uint8_t)(0x90 | n));
    else        { raw(0xDC); be16(n); }
  }
  void map(uint16_t n) {
    if (n < 16) raw((uint8_t)(0x80 | n));
    else        { raw(0xDE); be16(n); }
  }
};

/* --- lecture -------------------------------------------------------------
 *
 * Un curseur sur un tampon, et des accesseurs qui rendent false plutot que
 * de lever quoi que ce soit. Toute erreur est collante : une fois err pose,
 * plus rien n'est lu, ce qui evite d'avoir a tester chaque appel.
 */
struct MpReader {
  const uint8_t *buf;
  uint16_t len;
  uint16_t pos;
  bool err;

  void init(const uint8_t *b, uint16_t n) { buf = b; len = n; pos = 0; err = false; }
  bool ok() const { return !err; }
  uint16_t left() const { return err ? 0 : (uint16_t)(len - pos); }

  uint8_t next() { if (err || pos >= len) { err = true; return 0; } return buf[pos++]; }
  uint16_t next16() { uint16_t h = next(); return (uint16_t)((h << 8) | next()); }
  uint32_t next32() { uint32_t h = next16(); return (h << 16) | next16(); }

  bool is_nil() { return !err && pos < len && buf[pos] == 0xC0; }

  /* Entier signe. Accepte toutes les largeurs que msgpack-python peut
   * produire pour les valeurs qui nous concernent. */
  bool sint(int32_t &out) {
    if (err) return false;
    uint8_t t = next();
    if (err) return false;
    if (t < 0x80)  { out = t; return true; }
    if (t >= 0xE0) { out = (int32_t)(int8_t)t; return true; }
    switch (t) {
      case 0xCC: out = (int32_t)next(); return !err;
      case 0xCD: out = (int32_t)next16(); return !err;
      case 0xCE: out = (int32_t)next32(); return !err;
      case 0xD0: out = (int32_t)(int8_t)next(); return !err;
      case 0xD1: out = (int32_t)(int16_t)next16(); return !err;
      case 0xD2: out = (int32_t)next32(); return !err;
      default: err = true; return false;
    }
  }

  /* Chaine copiee dans un tampon de l'appelant, toujours terminee par 0.
   * Une chaine trop longue pour la destination est une ERREUR, pas une
   * troncature silencieuse : un mot de passe WiFi ampute serait accepte
   * sans un mot et ne se manifesterait qu'a la premiere association.
   * Les types bin sont acceptes en lecture — une console qui enverrait des
   * octets plutot qu'une chaine reste comprise. */
  bool str(char *dst, uint16_t dstcap) {
    if (err) return false;
    uint8_t t = next();
    if (err) return false;
    uint32_t n;
    if ((t & 0xE0) == 0xA0)      n = t & 0x1F;
    else if (t == 0xD9 || t == 0xC4) n = next();
    else if (t == 0xDA || t == 0xC5) n = next16();
    else { err = true; return false; }
    if (err || n + 1 > dstcap || pos + n > len) { err = true; return false; }
    memcpy(dst, buf + pos, n);
    dst[n] = 0;
    pos = (uint16_t)(pos + n);
    return true;
  }

  bool array(uint16_t &n) {
    if (err) return false;
    uint8_t t = next();
    if (err) return false;
    if ((t & 0xF0) == 0x90) { n = t & 0x0F; return true; }
    if (t == 0xDC) { n = next16(); return !err; }
    err = true;
    return false;
  }

  bool map(uint16_t &n) {
    if (err) return false;
    uint8_t t = next();
    if (err) return false;
    if ((t & 0xF0) == 0x80) { n = t & 0x0F; return true; }
    if (t == 0xDE) { n = next16(); return !err; }
    err = true;
    return false;
  }

  /* Saute un element quelconque, quel que soit son type. Indispensable :
   * une console plus recente peut envoyer un champ que ce firmware ne
   * connait pas, et il faut pouvoir passer par-dessus pour lire les
   * suivants au lieu de rejeter toute la requete. */
  bool adv(uint32_t n) {
    if (err || (uint32_t)pos + n > len) { err = true; return false; }
    pos = (uint16_t)(pos + n);
    return true;
  }

  bool skipn(uint16_t n) {
    for (uint16_t i = 0; i < n && !err; i++) skip();
    return !err;
  }

  bool skip() {
    if (err) return false;
    uint8_t t = next();
    if (err) return false;
    if (t < 0x80 || t >= 0xE0) return true;              /* fixint */
    if ((t & 0xE0) == 0xA0) return adv(t & 0x1F);        /* fixstr */
    if ((t & 0xF0) == 0x90) return skipn((uint16_t)(t & 0x0F));
    if ((t & 0xF0) == 0x80) return skipn((uint16_t)(2 * (t & 0x0F)));
    switch (t) {
      case 0xC0: case 0xC2: case 0xC3: return true;      /* nil, false, true */
      case 0xCC: case 0xD0: return adv(1);
      case 0xCD: case 0xD1: return adv(2);
      case 0xCE: case 0xD2: case 0xCA: return adv(4);
      case 0xCF: case 0xD3: case 0xCB: return adv(8);
      case 0xD9: case 0xC4: return adv(next());
      case 0xDA: case 0xC5: return adv(next16());
      case 0xDC: return skipn(next16());
      case 0xDE: return skipn((uint16_t)(2 * next16()));
      default: err = true; return false;
    }
  }
};

#endif /* OSJT_MSGPACK_H */
