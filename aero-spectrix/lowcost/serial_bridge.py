#!/usr/bin/env python3
"""
serial_bridge.py -- Pont entre une tête d'acquisition Teensy et AERO-SPECTRIX.

    python3 lowcost/serial_bridge.py --port COM7 --wav vacation.wav
    python3 lowcost/serial_bridge.py --port /dev/ttyACM0 --doa
    python3 lowcost/serial_bridge.py --list

Le Teensy émet un flux binaire trame par trame (voir teensy_4mic.ino). Ce
pont le reconstruit, comble les blocs perdus, et sait en faire deux choses :

    --wav FICHIER   enregistre les 4 voies au fil de l'eau. Le fichier se
                    relit ensuite dans n'importe quel outil, et permet de
                    rejouer toute la chaîne de traitement.
    --doa           fait tourner le DoaProcessor en direct et affiche
                    azimut, élévation, score et résidu dans la console.

--------------------------------------------------------------------------
POURQUOI COMBLER LES BLOCS PERDUS, ET NE PAS SIMPLEMENT LES IGNORER
--------------------------------------------------------------------------
Un bloc perdu, c'est 2,9 ms de signal absent. Si on se contente de recoller
les deux morceaux, l'axe des temps se raccourcit d'autant et rien ne le
signale : la piste continue de s'afficher, simplement elle n'est plus à
l'heure. En insérant du silence à la place du bloc manquant, on garde un axe
des temps juste — et le trou se voit sur le spectrogramme, ce qui est
exactement ce qu'on veut : un défaut visible plutôt qu'un défaut silencieux.

Les écarts de temps entre voies, eux, ne sont jamais affectés : le Teensy
n'émet un bloc que lorsque les quatre voies en ont un, et les quatre
capsules partagent la même horloge d'échantillonnage.
"""

import argparse
import os
import struct
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

MAGIC = b"AS4\xa5"
HEADER = 10
N_CH = 4
FS = 44100.0                 # bibliothèque audio du Teensy : 44,1 kHz fixe


# ==========================================================================
class FrameParser:
    """
    Reconstitue les blocs à partir d'un flux d'octets quelconque.

    Le flux série n'a ni début ni fin : on peut se brancher au milieu d'un
    paquet, et une perturbation peut en tronquer un. L'analyseur cherche
    donc le motif de synchronisation à chaque fois qu'il doute, plutôt que
    de supposer un alignement qu'il n'a aucun moyen de garantir.
    """

    def __init__(self):
        self.buf = bytearray()
        self.expected_seq = None
        self.n_blocks = 0
        self.n_lost = 0          # blocs perdus, déclarés par le Teensy
        self.n_gaps = 0          # sauts de numéro de séquence
        self.n_resync = 0        # octets jetés pour retrouver la synchro

    def feed(self, data):
        """Ajoute des octets et retourne la liste des blocs (n_ch, n) prêts."""
        self.buf.extend(data)
        out = []
        while True:
            i = self.buf.find(MAGIC)
            if i < 0:
                # Garder les 3 derniers octets : le motif peut être à cheval
                # sur deux lectures.
                if len(self.buf) > 3:
                    self.n_resync += len(self.buf) - 3
                    del self.buf[:-3]
                return out
            if i:
                self.n_resync += i
                del self.buf[:i]
            if len(self.buf) < HEADER:
                return out
            seq, nsamp, lost = struct.unpack_from("<HHH", self.buf, 4)
            payload = nsamp * N_CH * 2
            if nsamp == 0 or nsamp > 4096:
                # En-tête aberrant : ce n'était pas un vrai motif. On avance
                # d'un octet et on recherche, sinon on boucle indéfiniment.
                del self.buf[:1]
                self.n_resync += 1
                continue
            if len(self.buf) < HEADER + payload:
                return out

            # Copie explicite : un np.frombuffer pris DIRECTEMENT sur le
            # bytearray en exporte la mémoire, et Python refuse alors de le
            # redimensionner — le `del` ci-dessous lèverait BufferError.
            raw = bytes(self.buf[HEADER:HEADER + payload])
            x = np.frombuffer(raw, dtype="<i2")
            del self.buf[:HEADER + payload]

            if lost:
                self.n_lost += lost
                out.append(np.zeros((N_CH, nsamp * lost), dtype=np.float32))
            if self.expected_seq is not None and seq != self.expected_seq:
                manquants = (seq - self.expected_seq) & 0xFFFF
                if 0 < manquants < 1000:
                    self.n_gaps += manquants
                    out.append(np.zeros((N_CH, nsamp * manquants),
                                        dtype=np.float32))
            self.expected_seq = (seq + 1) & 0xFFFF
            self.n_blocks += 1
            # int16 -> flottant normalisé, disposition (voies, échantillons)
            out.append(x.reshape(nsamp, N_CH).T.astype(np.float32) / 32768.0)

    def report(self):
        return (f"{self.n_blocks} blocs reçus · {self.n_lost} perdus côté "
                f"Teensy · {self.n_gaps} sauts de séquence · "
                f"{self.n_resync} octets de resynchronisation")


# ==========================================================================
def open_serial(port, baud=2000000):
    try:
        import serial                                # pyserial
    except ImportError:
        sys.exit("Le module « pyserial » est nécessaire :\n"
                 f"    {sys.executable} -m pip install pyserial")
    # En USB natif, la vitesse déclarée est ignorée par le Teensy : elle
    # n'existe que pour satisfaire l'API. Le débit réel est celui de l'USB.
    return serial.Serial(port, baud, timeout=0.2)


def list_ports():
    try:
        from serial.tools import list_ports as lp
    except ImportError:
        sys.exit("Installez pyserial pour lister les ports.")
    found = list(lp.comports())
    if not found:
        print("Aucun port série trouvé.")
        return
    print("Ports série disponibles :")
    for p in found:
        marque = "  <-- probablement le Teensy" if "Teensy" in (p.description or "") \
                 or "16C0" in (p.hwid or "").upper() else ""
        print(f"  {p.device:<16} {p.description}{marque}")


# ==========================================================================
def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Pont série entre une tête Teensy 4 voies et AERO-SPECTRIX")
    ap.add_argument("--port", help="port série (COM7, /dev/ttyACM0…)")
    ap.add_argument("--list", action="store_true",
                    help="liste les ports série et quitte")
    ap.add_argument("--from-file", help="relit un flux brut capturé (mise au "
                                        "point du pont sans matériel)")
    ap.add_argument("--wav", help="enregistre les 4 voies dans ce fichier WAV")
    ap.add_argument("--doa", action="store_true",
                    help="traite en direct et affiche la direction")
    ap.add_argument("--gain", type=float, default=1.0,
                    help="pascals correspondant à la pleine échelle numérique")
    ap.add_argument("--seconds", type=float, default=0.0,
                    help="durée d'acquisition ; 0 = jusqu'à Ctrl-C")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)

    if a.list:
        list_ports()
        return 0
    if not a.port and not a.from_file:
        ap.error("indiquez --port ou --from-file (ou --list)")

    parser = FrameParser()
    writer = None
    proc = None
    ring = None

    if a.wav:
        from audio import WavWriter
        writer = WavWriter(a.wav, int(FS), N_CH)
        print(f"Enregistrement : {a.wav}  "
              f"({FS/1000:.1f} kHz, {N_CH} voies, float32)")

    if a.doa:
        from config import SimConfig
        from doa import DoaProcessor
        cfg = SimConfig()
        cfg.acq.fs = int(FS)
        proc = DoaProcessor(int(FS), cfg.array.positions(), cfg.atmo.c,
                            cfg.proc)
        ring = np.zeros((N_CH, cfg.proc.frame), dtype=np.float32)
        remplissage = 0
        hop = cfg.proc.hop
        depuis_trame = 0
        print(f"Traitement en direct : trame {cfg.proc.frame}, pas {hop}, "
              f"soit {FS/hop:.1f} mises à jour par seconde")
        print(f"{'t (s)':>7} {'azimut':>8} {'élév.':>7} {'f0 (Hz)':>8} "
              f"{'score':>7} {'résidu':>8}  état")

    src = (open(a.from_file, "rb") if a.from_file else open_serial(a.port))
    t0 = time.time()
    n_ech = 0
    try:
        while True:
            data = src.read(4096)
            if not data:
                if a.from_file:
                    break
                continue
            for blk in parser.feed(data):
                n_ech += blk.shape[1]
                if writer is not None:
                    writer.write(blk * a.gain)
                if proc is not None:
                    nb = blk.shape[1]
                    if nb >= ring.shape[1]:
                        ring[:] = blk[:, -ring.shape[1]:]
                        remplissage = ring.shape[1]
                    else:
                        ring[:] = np.roll(ring, -nb, axis=1)
                        ring[:, -nb:] = blk * a.gain
                        remplissage = min(remplissage + nb, ring.shape[1])
                    depuis_trame += nb
                    if remplissage >= ring.shape[1] and depuis_trame >= hop:
                        depuis_trame = 0
                        r = proc.process([ring[m] for m in range(N_CH)])
                        print(f"{n_ech/FS:7.2f} {_f(r['az_trk']):>8} "
                              f"{_f(r['el_trk']):>7} {r['f0']:8.1f} "
                              f"{r['score']:7.2f} {_f(r['resid_us'], 0):>8}  "
                              f"{r['status']}")
            if not a.quiet and writer is not None and n_ech and \
                    int(n_ech / FS) % 10 == 0 and n_ech % 44100 < 512:
                print(f"  … {n_ech/FS:.0f} s enregistrées, "
                      f"{writer.megabytes:.1f} Mo")
            if a.seconds and (n_ech / FS) >= a.seconds:
                break
    except KeyboardInterrupt:
        print("\nInterruption.")
    finally:
        try:
            src.close()
        except Exception:                            # noqa: BLE001
            pass
        if writer is not None:
            writer.close()
            print(f"WAV fermé : {writer.path} — {writer.seconds:.1f} s, "
                  f"{writer.megabytes:.1f} Mo")

    dt = time.time() - t0
    print(parser.report())
    if n_ech:
        # Le rapport entre le temps écoulé et le nombre d'échantillons reçus
        # est le meilleur indicateur de santé du lien : s'il s'écarte de 1,
        # c'est que des blocs disparaissent quelque part.
        print(f"{n_ech} échantillons en {dt:.1f} s → "
              f"{n_ech/FS/max(dt,1e-9)*100:.1f} % du temps réel")
    return 0


def _f(v, dec=1):
    try:
        return "—" if not np.isfinite(v) else f"{v:.{dec}f}"
    except TypeError:
        return "—"


if __name__ == "__main__":
    sys.exit(main())
