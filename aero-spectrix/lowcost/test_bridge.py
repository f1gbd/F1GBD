#!/usr/bin/env python3
"""
test_bridge.py -- Vérifie le pont série SANS matériel.

    python3 lowcost/test_bridge.py

On fabrique un flux binaire identique à celui du Teensy, à partir d'une VRAIE
scène acoustique : un drone dans une direction connue, rendu par le moteur de
synthèse du projet à 44,1 kHz.

Trois séries de tests, chacune isolant UNE chose :

  1. Flux propre — la transmission est-elle exacte ? Comparaison bit à bit
     avec les entiers 16 bits que le Teensy détient.

  2. Direction — le pont fausse-t-il la mesure ? On ne compare pas à la
     vérité-terrain, ce qui mesurerait la chaîne de localisation et non le
     pont : on compare la direction trouvée APRÈS encodage à celle trouvée
     AVANT, sur exactement les mêmes trames. C'est le test qui prouve que le
     format de trame préserve l'alignement entre voies — l'information dont
     dépend toute la mesure.

  3. Flux dégradé — octets parasites, branchement en cours de paquet, blocs
     jetés par la tête et paquet perdu sur la liaison. On vérifie la
     resynchronisation, le comptage des pertes et surtout la conservation de
     l'axe des temps.
"""

import os
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)

from serial_bridge import FrameParser, MAGIC, N_CH, FS   # noqa: E402

N = 128
OK = []


def check(nom, cond, detail=""):
    OK.append(bool(cond))
    print(f"  [{'OK ' if cond else 'ÉCHEC'}] {nom}" + (f"   {detail}" if detail else ""))


def encode(xi, seq0=0, perdus_a=None):
    """
    Encode un tableau (4, n) d'ENTIERS 16 BITS en flux Teensy.

    Entiers et non flottants, volontairement : le Teensy n'effectue aucune
    conversion, il transmet tels quels les mots 16 bits que lui a donnés la
    bibliothèque audio. Faire quantifier le tableau ici mêlerait l'erreur de
    quantification à l'erreur de transport, et le test ne mesurerait plus ce
    qu'il prétend mesurer.

    `perdus_a` : indices de blocs sautés.

    Le numéro de séquence n'avance QUE sur un paquet réellement émis — c'est
    ce que fait le firmware. Les blocs jetés faute de place sont rapportés
    par le champ « perdus », pas par un trou dans la numérotation. Les deux
    mécanismes sont indépendants et comptent des pertes différentes : le
    champ « perdus » compte ce que le Teensy a jeté, un saut de numéro
    compte ce que la liaison USB a perdu.
    """
    perdus_a = set(perdus_a or ())
    out = bytearray()
    n_blocs = xi.shape[1] // N
    seq = seq0
    perdus = 0
    for k in range(n_blocs):
        if k in perdus_a:
            perdus += 1
            continue
        blk = xi[:, k * N:(k + 1) * N]
        out += MAGIC
        out += struct.pack("<HHH", seq, N, perdus)
        out += np.ascontiguousarray(blk.T, dtype="<i2").tobytes()
        seq = (seq + 1) & 0xFFFF
        perdus = 0
    return bytes(out)


def scene(az=118.0, el=37.0, seconds=6.0):
    """Rend une scène réelle à 44,1 kHz, drone dans une direction fixe."""
    from config import SimConfig
    from geometry import Trajectory
    import synth

    cfg = SimConfig()
    cfg.acq.fs = int(FS)
    cfg.acq.duration = seconds
    cfg.atmo.ground_reflection = False        # scène épurée : on teste le pont
    r = 240.0
    a, e = np.radians(az), np.radians(el)
    # az mesuré depuis le Nord, sens horaire -> (Est, Nord, haut)
    p = (r * np.cos(e) * np.sin(a), r * np.cos(e) * np.cos(a), r * np.sin(e))
    cfg.traj.waypoints = [(0.0, *p), (seconds, *p)]
    traj = Trajectory(cfg.traj.waypoints, cfg.array.height_agl)
    ren = synth.render_channels(cfg, traj, verbose=False)
    x = ren["p"]
    x = x / (np.max(np.abs(x)) + 1e-12) * 0.6      # cadrage pleine échelle
    return cfg, x.astype(np.float32)


def main():
    print("=" * 74)
    print("  VÉRIFICATION DU PONT SÉRIE (sans matériel)")
    print("=" * 74)
    az_vrai, el_vrai = 118.0, 37.0
    print(f"\nScène : drone à azimut {az_vrai}°, élévation {el_vrai}°, "
          f"240 m, {FS/1000:.1f} kHz")
    cfg, x = scene(az_vrai, el_vrai)
    n_blocs = x.shape[1] // N
    x = x[:, :n_blocs * N]                            # tronqué au bloc entier
    # Ce que la bibliothèque audio du Teensy détient réellement : des entiers
    # 16 bits. `xf` est leur valeur normalisée, et c'est la référence exacte
    # que le pont doit restituer.
    xi = np.clip(np.round(x * 32767.0), -32768, 32767).astype(np.int16)
    xf = (xi.astype(np.float32) / 32768.0)

    # ------------------------------------------------------------------
    # 1. Flux PROPRE : on isole la fidélité de la transmission
    # ------------------------------------------------------------------
    print(f"\n1. Flux sans perte ({n_blocs} blocs)")
    p = FrameParser()
    blocs = []
    flux = encode(xi)
    for i in range(0, len(flux), 997):                # lectures de taille impaire
        blocs += p.feed(flux[i:i + 997])
    y = np.concatenate(blocs, axis=1) if blocs else np.zeros((4, 0))
    check("tous les blocs sont restitués", y.shape == xf.shape,
          f"{y.shape} contre {xf.shape}")
    err = np.max(np.abs(y - xf)) if y.shape == xf.shape else 9e9
    check("les échantillons traversent le pont SANS AUCUNE altération",
          err == 0.0, f"écart max {err*32768:.3f} LSB — comparaison bit à bit")

    # ------------------------------------------------------------------
    # 2. Le pont fausse-t-il la direction ? Comparaison avec la référence.
    # ------------------------------------------------------------------
    # On ne compare PAS à la vérité-terrain : ce test ne mesure pas la
    # qualité de la chaîne de localisation, il mesure ce que le pont lui
    # fait subir. La bonne référence est donc la même chaîne appliquée au
    # signal AVANT encodage.
    print("\n2. La direction est-elle préservée par le pont ?")
    from doa import DoaProcessor
    from geometry import angular_error_deg
    F, H = cfg.proc.frame, cfg.proc.hop

    def doa_sur(sig, i0, i1):
        proc = DoaProcessor(int(FS), cfg.array.positions(), cfg.atmo.c,
                            cfg.proc)
        az, el, res = [], [], []
        for i in range(i0, i1 - F, H):
            r = proc.process([sig[m, i:i + F] for m in range(N_CH)])
            az.append(r["az_raw"])
            el.append(r["el_raw"])
            res.append(r["resid_us"])
        return np.array(az), np.array(el), np.array(res)

    i0, i1 = N * 60, min(xf.shape[1], N * 500)
    az_r, el_r, res_r = doa_sur(xf, i0, i1)
    az_y, el_y, res_y = doa_sur(y, i0, i1)
    m = np.isfinite(az_r) & np.isfinite(az_y)
    ecart = angular_error_deg(az_r[m], el_r[m], az_y[m], el_y[m])
    check("mesure identique à celle obtenue avant encodage",
          m.sum() > 3 and float(np.max(ecart)) < 0.05,
          f"{m.sum()} trames comparées, écart max {np.max(ecart):.4f}°")

    e_abs = angular_error_deg(az_vrai, el_vrai, az_y[m], el_y[m])
    print(f"     azimut médian {np.median(az_y[m]):.2f}° (vrai {az_vrai}) · "
          f"élévation {np.median(el_y[m]):.2f}° (vrai {el_vrai})")
    check("la direction reste physiquement plausible après le pont",
          float(np.median(e_abs)) < 3.0,
          f"erreur médiane à la vérité {np.median(e_abs):.2f}° "
          f"(scène bruitée, ce n'est pas ce qu'on teste ici)")
    check("les temps d'arrivée restent mutuellement cohérents",
          float(np.median(res_y[m])) < 30.0,
          f"résidu médian {np.median(res_y[m]):.0f} µs")

    # ------------------------------------------------------------------
    # 3. Flux DÉGRADÉ : resynchronisation et comblement des trous
    # ------------------------------------------------------------------
    perdus = {40, 41, 300}
    flux = encode(xi, seq0=65500, perdus_a=perdus)     # seq0 : teste le bouclage
    # On se branche au milieu d'un paquet, précédé d'octets parasites : c'est
    # ce qui arrive quand on ouvre le port alors que la tête émet déjà.
    sale = b"\x00\x11\x22" + MAGIC[:2] + b"\x99" + flux[517:]
    # Et on ampute un paquet complet en plein milieu, comme le ferait une
    # perte sur la liaison USB : le numéro de séquence saute.
    coupe = 900 * (10 + N * 4 * 2)
    sale = sale[:coupe] + sale[coupe + (10 + N * 4 * 2):]

    print(f"\n3. Flux dégradé ({len(perdus)} blocs jetés par la tête, "
          f"1 paquet perdu sur la liaison, entrée en cours de paquet)")
    p = FrameParser()
    blocs = []
    for i in range(0, len(sale), 997):
        blocs += p.feed(sale[i:i + 997])
    z = np.concatenate(blocs, axis=1) if blocs else np.zeros((4, 0))
    print("     " + p.report())
    check("l'analyseur se resynchronise sur un flux tronqué et bruité",
          p.n_blocks >= n_blocs - len(perdus) - 2 and p.n_resync < 1200,
          f"{p.n_blocks} blocs, {p.n_resync} octets jetés")
    check("les pertes de la tête sont déclarées et comblées",
          p.n_lost == len(perdus), f"{p.n_lost} déclarés")
    check("les pertes de la liaison sont déduites du numéro de séquence",
          p.n_gaps == 1, f"{p.n_gaps} saut détecté")
    # L'axe des temps doit être conservé à un bloc près (le premier paquet,
    # amputé par le branchement à chaud, est irrécupérable).
    check("l'axe des temps est conservé malgré les trous",
          abs(z.shape[1] - xf.shape[1]) <= N,
          f"{z.shape[1]} échantillons pour {xf.shape[1]} émis "
          f"(écart {z.shape[1]-x.shape[1]:+d})")

    print("\n" + "=" * 74)
    print(f"  {sum(OK)}/{len(OK)} tests réussis")
    print("=" * 74)
    return 0 if all(OK) else 1


if __name__ == "__main__":
    sys.exit(main())
