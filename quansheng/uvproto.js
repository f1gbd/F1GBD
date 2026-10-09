/* uvproto.js - UV-K1 / UV-K5 v3 (firmware F4HWN, Labs edition) serial protocol
 * for overlay apps (.app): session hello and app slot info / erase / write /
 * validate, as implemented by App/app/uart.c (commands 0x0514, 0x0730-0x0737).
 *
 * Frame (host -> radio):  AB CD | size LE16 | obf(body + CRC16) | DC BA
 *   body  = id LE16 | len LE16 | data,   size = body length
 *   CRC16 = CRC-16/XMODEM (poly 0x1021, init 0) over the clear body, LE
 *   obf   = XOR with the 16-byte Quansheng key, index i % 16 over body + CRC
 * Reply (radio -> host):  AB CD | size LE16 | obf(body) | 2 pad | DC BA
 *
 * F1GBD / ADRASEC 77 - based on the firmware sources of Armel F4HWN
 * (UV Studio uses the same commands). Apache License 2.0.
 */
(function (root) {
  "use strict";
  const OBF = [0x16, 0x6C, 0x14, 0xE6, 0x2E, 0x91, 0x0D, 0x40,
               0x21, 0x35, 0xD5, 0x40, 0x13, 0x03, 0xE9, 0x80];

  const APP_MAGIC = 0x31504146;          // "FAP1"
  const APP_HDR_VERSION = 1;
  const APP_ABI_MAJOR = 1;
  const APP_OVERLAY_MAX = 0x1000;
  const APP_ASSET_OFFSET = 0x100;
  const APP_ASSET_MAX = 0xF00;
  const APP_CODE_OFFSET = 0x1000;
  const APP_SLOT_COUNT = 16;
  const APP_FLAG_COMMITTED = 1;
  const CHUNK = 128;                     // bytes per write (frame <= 248 B)

  const STATUS = [
    "OK", "emplacement invalide", "en-tête absent ou invalide",
    "ABI / niveau d'API incompatible avec le firmware", "image non validée",
    "taille hors limites", "CRC incorrect", "VMA de l'overlay différente du firmware",
    "refusé : session expirée (timestamp)", "capacité firmware requise absente",
  ];

  function crc16(buf) {
    let c = 0;
    for (let i = 0; i < buf.length; i++) {
      c ^= buf[i] << 8;
      for (let j = 0; j < 8; j++)
        c = (c & 0x8000) ? ((c << 1) ^ 0x1021) & 0xFFFF : (c << 1) & 0xFFFF;
    }
    return c;
  }

  const CRC32_T = (() => {
    const t = new Uint32Array(256);
    for (let n = 0; n < 256; n++) {
      let c = n;
      for (let k = 0; k < 8; k++) c = (c & 1) ? 0xEDB88320 ^ (c >>> 1) : c >>> 1;
      t[n] = c >>> 0;
    }
    return t;
  })();
  function crc32(buf) {
    let c = 0xFFFFFFFF;
    for (let i = 0; i < buf.length; i++) c = CRC32_T[(c ^ buf[i]) & 0xFF] ^ (c >>> 8);
    return (c ^ 0xFFFFFFFF) >>> 0;
  }

  function buildFrame(id, data) {
    data = data || new Uint8Array(0);
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

  /* Incremental parser of the radio's replies. */
  class ReplyParser {
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
        if (size > 1024) { this.buf = this.buf.slice(2); continue; }
        if (this.buf.length < size + 8) break;
        if (this.buf[size + 6] !== 0xDC || this.buf[size + 7] !== 0xBA) {
          this.buf = this.buf.slice(2); continue;
        }
        const body = new Uint8Array(size);
        for (let k = 0; k < size; k++) body[k] = this.buf[4 + k] ^ OBF[k % 16];
        this.buf = this.buf.slice(size + 8);
        if (size < 4) continue;
        const len = Math.min(body[2] | (body[3] << 8), size - 4);
        out.push({ id: body[0] | (body[1] << 8), data: body.slice(4, 4 + len) });
      }
      return out;
    }
  }

  const cstr = (u8) => {
    let s = "";
    for (let i = 0; i < u8.length && u8[i] && u8[i] !== 0xFF; i++) s += String.fromCharCode(u8[i]);
    return s;
  };

  function parseHeader(h) {
    const dv = new DataView(h.buffer, h.byteOffset, 64);
    return {
      magic: dv.getUint32(0, true), hdrVersion: dv.getUint16(4, true),
      abiMajor: h[6], apiMin: h[7],
      codeSize: dv.getUint32(8, true), codeCrc: dv.getUint32(12, true),
      entry: dv.getUint16(16, true), flags: dv.getUint16(18, true),
      name: cstr(h.subarray(20, 36)), version: cstr(h.subarray(36, 52)),
      linkVma: dv.getUint32(52, true), caps: dv.getUint32(56, true),
      assetSize: dv.getUint16(60, true), assetCrc: dv.getUint16(62, true),
    };
  }

  /* Validate a .app blob (pack_app.py): 64-byte header + code + assets. */
  function parseApp(u8) {
    if (!(u8 instanceof Uint8Array)) u8 = new Uint8Array(u8);
    if (u8.length < 66) throw new Error("fichier trop court pour un .app");
    const h = parseHeader(u8.subarray(0, 64));
    if (h.magic !== APP_MAGIC) throw new Error("ce n'est pas un .app (signature FAP1 absente)");
    if (h.hdrVersion !== APP_HDR_VERSION || h.abiMajor !== APP_ABI_MAJOR)
      throw new Error("format d'en-tête / ABI non supporté");
    if (h.codeSize < 2 || h.codeSize > APP_OVERLAY_MAX) throw new Error("taille de code hors limites (4 Kio max)");
    if (h.assetSize > APP_ASSET_MAX) throw new Error("ressources trop volumineuses");
    if (u8.length !== 64 + h.codeSize + h.assetSize) throw new Error("longueur du fichier incohérente avec l'en-tête");
    if (!(h.flags & APP_FLAG_COMMITTED)) throw new Error("image non validée (drapeau COMMITTED absent)");
    const code = u8.slice(64, 64 + h.codeSize);
    const assets = u8.slice(64 + h.codeSize);
    if (crc32(code) !== h.codeCrc) throw new Error("CRC-32 du code incorrect (fichier corrompu)");
    if (assets.length && (crc32(assets) & 0xFFFF) !== h.assetCrc) throw new Error("CRC des ressources incorrect");
    return Object.assign(h, { header: u8.slice(0, 64), code, assets, size: u8.length });
  }

  const le32 = (v) => [v & 0xFF, (v >>> 8) & 0xFF, (v >>> 16) & 0xFF, (v >>> 24) & 0xFF];

  /* transport: { write(Uint8Array): Promise }; feed incoming bytes with onBytes(). */
  class UVRadio {
    constructor(transport, log) {
      this.t = transport; this.log = log || (() => {});
      this.parser = new ReplyParser(); this.waiters = [];
      this.ts = 0; this.version = "";
    }
    onBytes(bytes) {
      for (const r of this.parser.push(bytes)) {
        const w = this.waiters.findIndex((x) => x.id === r.id && (!x.match || x.match(r.data)));
        if (w >= 0) { const x = this.waiters.splice(w, 1)[0]; clearTimeout(x.timer); x.resolve(r.data); }
      }
    }
    request(id, data, replyId, opts) {
      opts = opts || {};
      const tries = opts.tries || 3, timeout = opts.timeout || 1500;
      const once = () => new Promise((resolve, reject) => {
        const x = { id: replyId, match: opts.match, resolve };
        x.timer = setTimeout(() => {
          const k = this.waiters.indexOf(x); if (k >= 0) this.waiters.splice(k, 1);
          reject(new Error("pas de réponse de la radio (0x" + replyId.toString(16).padStart(4, "0") + ")"));
        }, timeout);
        this.waiters.push(x);
        this.t.write(buildFrame(id, new Uint8Array(data))).catch(reject);
      });
      return (async () => {
        let err;
        for (let k = 0; k < tries; k++) {
          try { return await once(); } catch (e) { err = e; }
        }
        throw err;
      })();
    }
    async hello() {
      this.ts = (Math.random() * 0xFFFFFFFF) >>> 0 || 1;
      const d = await this.request(0x0514, le32(this.ts), 0x0515);
      this.version = cstr(d.subarray(0, 16));
      return { version: this.version, locked: !!d[17] };
    }
    async slotInfo(slot) {
      const d = await this.request(0x0730, [slot, 0], 0x0731, { match: (r) => r[0] === slot });
      const status = d[1];
      const h = d.length >= 66 ? parseHeader(d.slice(2, 66)) : null;
      const empty = !h || h.magic === 0xFFFFFFFF || h.magic !== APP_MAGIC;
      return { slot, status, header: empty ? null : h };
    }
    async listSlots(onEach) {
      const r = [];
      for (let s = 0; s < APP_SLOT_COUNT; s++) { const i = await this.slotInfo(s); r.push(i); if (onEach) onEach(i); }
      return r;
    }
    check(d, what) {
      if (d[1] !== 0) throw new Error(what + " : " + (STATUS[d[1]] || ("statut " + d[1])));
    }
    async erase(slot) {
      const d = await this.request(0x0732, [slot, 0, ...le32(this.ts)], 0x0733,
        { match: (r) => r[0] === slot, timeout: 4000, tries: 1 });
      this.check(d, "effacement");
    }
    async write(slot, offset, chunk) {
      const d = await this.request(0x0734,
        [slot, 0, ...le32(offset), chunk.length & 0xFF, chunk.length >> 8, ...le32(this.ts), ...chunk],
        0x0735, { match: (r) => r[0] === slot, timeout: 2000 });
      this.check(d, "écriture @0x" + offset.toString(16));
    }
    async validate(slot) {
      const d = await this.request(0x0736, [slot, 0], 0x0737, { match: (r) => r[0] === slot });
      this.check(d, "validation");
    }
    /* Erase, then assets (0x100), code (0x1000), and the header last (0x000):
     * the slot only becomes a valid, committed app once everything is written. */
    async install(slot, app, progress) {
      progress = progress || (() => {});
      const parts = [];
      if (app.assets.length) parts.push([APP_ASSET_OFFSET, app.assets]);
      parts.push([APP_CODE_OFFSET, app.code]);
      parts.push([0, app.header]);
      const total = parts.reduce((a, p) => a + p[1].length, 0);
      let done = 0;
      await this.hello();                       // fresh session timestamp
      this.log("Effacement de l'emplacement " + slot + "…");
      await this.erase(slot);
      progress(0.02);
      for (const [base, data] of parts) {
        for (let o = 0; o < data.length; o += CHUNK) {
          const c = data.subarray(o, Math.min(o + CHUNK, data.length));
          await this.write(slot, base + o, Array.from(c));
          done += c.length;
          progress(0.02 + 0.93 * done / total);
        }
      }
      this.log("Vérification de l'en-tête…");
      await this.validate(slot);
      progress(1);
    }
  }

  const api = { OBF, crc16, crc32, buildFrame, ReplyParser, parseHeader, parseApp, UVRadio, STATUS,
                APP_SLOT_COUNT, APP_ASSET_OFFSET, APP_CODE_OFFSET };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.UVProto = api;
})(typeof window !== "undefined" ? window : globalThis);
