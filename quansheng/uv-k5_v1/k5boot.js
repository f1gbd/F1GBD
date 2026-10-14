/* k5boot.js - Quansheng UV-K5 / K6 / 5R "v1" (DP32G030): firmware flashing
 * through the bootloader, and EEPROM backup through the running firmware.
 *
 * Frames (as uvproto.js): AB CD | size LE16 | obf(body + CRC16) | DC BA,
 * body = id LE16 | len LE16 | data.  On receive the data is taken from the
 * frame size (body minus its 4-byte head), as k5flash.py does, not from the
 * inner len field.
 *
 * Bootloader (radio switched on with PTT held, LED lit):
 *   0x0518  beacon, sent about every 0.5 s, data = bootloader version text
 *   0x0530  version handshake: 16 bytes, "*" first = any firmware accepted
 *   0x0519  write 256 bytes: seq LE32 | chunk LE16 | count LE16 | len LE16 | 0 | data[256]
 *   0x051A  ack: seq LE32 | chunk LE16 | error u8 (0 = OK)
 * Protocol of utils/k5flash.py (TA1JS, after qrp73/K5TOOL), proven on the radio.
 *
 * Running firmware (normal mode):
 *   0x0514  session: timestamp LE32 -> 0x0515 version[16], custom AES key, lock
 *   0x051B  read EEPROM: offset LE16 | size u8 | 0 | timestamp LE32
 *   0x051C  offset LE16 | size u8 | 0 | data[size]          (app/uart.c)
 *
 * F1GBD / ADRASEC 77 - Apache License 2.0
 */
(function (root) {
  "use strict";

  const OBF = [0x16, 0x6C, 0x14, 0xE6, 0x2E, 0x91, 0x0D, 0x40,
               0x21, 0x35, 0xD5, 0x40, 0x13, 0x03, 0xE9, 0x80];

  function crc16(buf) {
    let c = 0;
    for (let i = 0; i < buf.length; i++) {
      c ^= buf[i] << 8;
      for (let j = 0; j < 8; j++) c = (c & 0x8000) ? ((c << 1) ^ 0x1021) & 0xFFFF : (c << 1) & 0xFFFF;
    }
    return c;
  }

  function buildFrame(id, data) {
    const n = 4 + data.length;
    const body = new Uint8Array(n);
    body[0] = id & 0xFF; body[1] = id >> 8;
    body[2] = data.length & 0xFF; body[3] = data.length >> 8;
    body.set(data, 4);
    const crc = crc16(body);
    const out = new Uint8Array(n + 8);
    out[0] = 0xAB; out[1] = 0xCD; out[2] = n & 0xFF; out[3] = n >> 8;
    for (let i = 0; i < n; i++) out[4 + i] = body[i] ^ OBF[i % 16];
    out[4 + n] = (crc & 0xFF) ^ OBF[n % 16];
    out[5 + n] = (crc >> 8) ^ OBF[(n + 1) % 16];
    out[6 + n] = 0xDC; out[7 + n] = 0xBA;
    return out;
  }

  /* Incremental frame parser -> [{id, data}] */
  class Parser {
    constructor() { this.buf = new Uint8Array(0); }
    push(bytes) {
      const b = new Uint8Array(this.buf.length + bytes.length);
      b.set(this.buf); b.set(bytes, this.buf.length);
      this.buf = b;
      const out = [];
      for (;;) {
        let i = 0;
        while (i + 1 < this.buf.length && !(this.buf[i] === 0xAB && this.buf[i + 1] === 0xCD)) i++;
        if (i) this.buf = this.buf.slice(i);
        if (this.buf.length < 8) break;
        const size = this.buf[2] | (this.buf[3] << 8);
        if (size > 2048) { this.buf = this.buf.slice(2); continue; }
        if (this.buf.length < size + 8) break;
        if (this.buf[size + 6] !== 0xDC || this.buf[size + 7] !== 0xBA) { this.buf = this.buf.slice(2); continue; }
        const body = new Uint8Array(size);
        for (let k = 0; k < size; k++) body[k] = this.buf[4 + k] ^ OBF[k % 16];
        this.buf = this.buf.slice(size + 8);
        if (size >= 4) out.push({ id: body[0] | (body[1] << 8), data: body.slice(4) });
      }
      return out;
    }
  }

  /* Link over a Web Serial port (or any {write(u8), onBytes} transport). */
  class Link {
    constructor(write) { this.write = write; this.parser = new Parser(); this.q = []; this.w = null; }
    onBytes(bytes) {
      for (const r of this.parser.push(bytes)) {
        if (this.w) { const w = this.w; this.w = null; clearTimeout(w.t); w.res(r); }
        else this.q.push(r);
      }
    }
    send(id, data) { return this.write(buildFrame(id, Uint8Array.from(data))); }
    drain() { this.q.length = 0; }
    next(timeout) {
      if (this.q.length) return Promise.resolve(this.q.shift());
      return new Promise((res) => {
        const w = { res };
        w.t = setTimeout(() => { if (this.w === w) this.w = null; res(null); }, timeout);
        this.w = w;
      });
    }
  }

  const FW_MAX = 0xF000;                 // program area of the DP32G030 (60 KiB)
  const EEPROM_SIZE = 0x2000;            // 8 KiB, calibration at 0x1E00
  const EE_STEP = 0x80;

  const le32 = (v) => [v & 0xFF, (v >>> 8) & 0xFF, (v >>> 16) & 0xFF, (v >>> 24) & 0xFF];
  const u16 = (d, i) => d[i] | (d[i + 1] << 8);
  const text = (d) => { let s = ""; for (const c of d) if (c >= 32 && c < 127) s += String.fromCharCode(c); return s.trim(); };

  /* A raw firmware image starts with the Cortex-M0 vector table: initial
   * stack pointer in RAM (0x2000xxxx) and a Thumb reset vector in flash.  A
   * .packed.bin is obfuscated and fails this test. */
  function checkFirmware(u8) {
    if (!(u8 instanceof Uint8Array)) u8 = new Uint8Array(u8);
    if (u8.length < 1024) throw new Error("fichier trop court pour un firmware");
    if (u8.length > FW_MAX) throw new Error(`firmware trop gros : ${u8.length} o (60 Kio = 61 440 o au plus)`);
    const sp = (u8[0] | (u8[1] << 8) | (u8[2] << 16) | (u8[3] << 24)) >>> 0;
    const rv = (u8[4] | (u8[5] << 8) | (u8[6] << 16) | (u8[7] << 24)) >>> 0;
    if ((sp & 0xFFFF0000) !== 0x20000000 || !(rv & 1) || rv >= FW_MAX)
      throw new Error("ce n'est pas un firmware brut (.bin) pour DP32G030 — un .packed.bin ne se flashe pas ici");
    return u8;
  }

  /* link: { send(id, dataArray): Promise, next(timeoutMs): Promise<{id,data}|null>, drain() } */
  async function waitFor(link, ids, timeout, skip) {
    const t0 = Date.now();
    for (;;) {
      const left = timeout - (Date.now() - t0);
      if (left <= 0) return null;
      const r = await link.next(left);
      if (!r) return null;
      if (ids.includes(r.id)) return r;
      if (skip) skip(r);
    }
  }

  async function flash(link, fw, version, progress, log) {
    progress = progress || (() => {}); log = log || (() => {});
    fw = checkFirmware(fw);
    const count = Math.ceil(fw.length / 256);

    log("Attente du chargeur de démarrage (radio allumée PTT enfoncé)…");
    const b = await waitFor(link, [0x0518], 15000);
    if (!b) throw new Error("aucun signal du chargeur de démarrage : la radio est-elle en mode chargement (PTT enfoncé à l'allumage, LED allumée) ?");
    const boot = text(b.data);
    log("Chargeur de démarrage : " + (boot || "?"));

    const v = new Array(16).fill(0);
    for (let i = 0; i < Math.min(16, version.length); i++) v[i] = version.charCodeAt(i) & 0x7F;
    link.drain();
    await link.send(0x0530, v);
    const a = await waitFor(link, [0x0518], 6000);
    if (!a) throw new Error("le chargeur de démarrage n'a pas accepté la version « " + version + " »");
    log(`Version « ${version} » acceptée, écriture de ${fw.length} o en ${count} blocs…`);

    const seq = 0x1D9F8D8A;
    for (let n = 0; n < count; n++) {
      const part = fw.subarray(n * 256, Math.min((n + 1) * 256, fw.length));
      const blk = new Array(256).fill(0xFF);
      for (let i = 0; i < part.length; i++) blk[i] = part[i];
      link.drain();
      await link.send(0x0519, [...le32(seq), n & 0xFF, n >> 8, count & 0xFF, count >> 8,
                               part.length & 0xFF, part.length >> 8, 0, 0, ...blk]);
      const r = await waitFor(link, [0x051A], 6000);
      if (!r) throw new Error(`pas d'accusé pour le bloc ${n + 1}/${count}`);
      if (r.data.length < 7) throw new Error(`accusé du bloc ${n + 1} trop court`);
      if (u16(r.data, 4) !== n) throw new Error(`accusé du bloc ${u16(r.data, 4) + 1} au lieu de ${n + 1}`);
      if (r.data[6] !== 0) throw new Error(`le bloc ${n + 1} a été refusé (erreur ${r.data[6]})`);
      progress((n + 1) / count);
    }
    return { boot, blocks: count };
  }

  async function hello(link) {
    const ts = (Math.random() * 0xFFFFFFFF) >>> 0 || 1;
    for (let k = 0; k < 3; k++) {
      link.drain();
      await link.send(0x0514, le32(ts));
      const r = await waitFor(link, [0x0515], 1500);
      if (r) {
        let v = "";
        for (let i = 0; i < 16 && r.data[i]; i++) v += String.fromCharCode(r.data[i]);
        return { ts, version: v, locked: !!r.data[17] };
      }
    }
    throw new Error("la radio ne répond pas : allumée normalement (pas en mode chargement), câble branché ?");
  }

  async function readEeprom(link, progress, log, size) {
    progress = progress || (() => {}); log = log || (() => {});
    size = size || EEPROM_SIZE;
    const h = await hello(link);
    log("Firmware : " + (h.version || "?"));
    if (h.locked) log("Radio verrouillée : la lecture peut renvoyer des zéros.");
    const out = new Uint8Array(size);
    for (let off = 0; off < size; off += EE_STEP) {
      let r = null;
      for (let k = 0; k < 3 && !r; k++) {
        link.drain();
        await link.send(0x051B, [off & 0xFF, off >> 8, EE_STEP, 0, ...le32(h.ts)]);
        r = await waitFor(link, [0x051C], 1500);
        if (r && (u16(r.data, 0) !== off || r.data[2] !== EE_STEP || r.data.length < 4 + EE_STEP)) r = null;
      }
      if (!r) throw new Error("lecture EEPROM interrompue à 0x" + off.toString(16).padStart(4, "0"));
      out.set(r.data.subarray(4, 4 + EE_STEP), off);
      progress((off + EE_STEP) / size);
    }
    const cal = out.subarray(0x1E00, 0x2000);
    const blank = cal.every((x) => x === 0xFF) || cal.every((x) => x === 0);
    return { data: out, version: h.version, calibrationBlank: blank };
  }

  const api = { flash, readEeprom, hello, checkFirmware, buildFrame, Parser, Link, crc16, OBF, FW_MAX, EEPROM_SIZE };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.K5Boot = api;
})(typeof window !== "undefined" ? window : globalThis);
