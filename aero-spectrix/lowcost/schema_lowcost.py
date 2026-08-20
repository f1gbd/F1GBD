#!/usr/bin/env python3
"""
schema_lowcost.py -- Schémas des montages d'évaluation à bas coût.

    python3 lowcost/schema_lowcost.py            # -> lowcost/schema_lowcost.html

Deux architectures, dessinées côte à côte pour qu'on puisse les comparer :

  A. Teensy 4 + 4 capsules MEMS I²S     le moins cher, un peu de mise au point
  B. PC ou Raspberry Pi + interface     rien à mettre au point, plus cher
     USB classe audio 2

Les couleurs et les conventions sont celles de schema_cablage.py : les deux
documents doivent se lire de la même façon.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from schema_cablage import (BG, PANEL, GRID, GRID_HI, TXT, DIM, ACCENT, BLUE,
                            ORANGE, ALARM, _box, _arrow)          # noqa: E402


# ==========================================================================
def svg_teensy():
    """Teensy 4 + 4 capsules MEMS I²S, une seule horloge pour les quatre."""
    o = [f'<svg viewBox="0 0 1080 470" width="100%">',
         f'<defs><marker id="at" viewBox="0 0 10 10" refX="9" refY="5" '
         f'markerWidth="7" markerHeight="7" orient="auto">'
         f'<path d="M0,0 L10,5 L0,10 z" fill="{ACCENT}"/></marker></defs>',
         f'<rect width="1080" height="470" fill="{PANEL}" rx="6"/>',
         f'<text x="30" y="34" fill="{ACCENT}" font-size="15" font-weight="700" '
         f'letter-spacing="1.5">MONTAGE A — TEENSY 4 + 4 CAPSULES MEMS '
         f'I²S</text>',
         f'<text x="30" y="56" fill="{DIM}" font-size="11.5">'
         f'Le moins cher. Aucun préampli, aucun câble analogique. Toute la '
         f'difficulté se ramène au partage des horloges — et ce partage est '
         f'ici obtenu par le câblage lui-même.</text>']

    # les quatre capsules, groupées par ligne de données
    lignes = [("SD → broche 8", 92, ACCENT, ("M1", "L/R → GND"),
               ("M2", "L/R → 3V3")),
              ("SD → broche 6", 244, BLUE, ("M3", "L/R → GND"),
               ("M4", "L/R → 3V3"))]
    for lab, y, col, (a, sa), (b, sb) in lignes:
        _box(o, 40, y, 150, 44, a, sa, col)
        _box(o, 40, y + 56, 150, 44, b, sb, col)
        # jonction en Y : les deux capsules partagent UNE ligne de données
        o.append(f'<path d="M190,{y+22} L232,{y+22} L232,{y+50} L268,{y+50}" '
                 f'fill="none" stroke="{col}" stroke-width="2.2" '
                 f'marker-end="url(#at)"/>')
        o.append(f'<path d="M190,{y+78} L232,{y+78} L232,{y+50}" fill="none" '
                 f'stroke="{col}" stroke-width="2.2"/>')
        # Le libellé va AU-DESSUS du segment horizontal : placé à sa droite,
        # il passerait sous le bloc du Teensy et deviendrait illisible.
        o.append(f'<text x="196" y="{y+14}" fill="{DIM}" font-size="10">'
                 f'{lab}</text>')

    _box(o, 268, 92, 232, 196, "TEENSY 4.0 / 4.1", "", ACCENT)
    for k, t in enumerate([
            "AudioInputI2SQuad",
            "",
            "broche 21 → BCLK",
            "broche 20 → LRCLK",
            "broches 8 et 6 → données",
            "",
            "44 100 Hz · 16 bits · 4 voies"]):
        col = ACCENT if k in (0, 6) else TXT
        o.append(f'<text x="384" y="{136+k*20}" fill="{col}" font-size="11.5" '
                 f'text-anchor="middle" '
                 f'font-weight="{700 if k in (0, 6) else 400}">{t}</text>')

    o.append(f'<text x="574" y="170" fill="{DIM}" font-size="10.5" '
             f'text-anchor="middle">USB série</text>')
    o.append(f'<text x="574" y="185" fill="{DIM}" font-size="10.5" '
             f'text-anchor="middle">355 ko/s</text>')
    o.append(f'<line x1="500" y1="196" x2="638" y2="196" stroke="{ACCENT}" '
             f'stroke-width="2" marker-end="url(#at)"/>')
    _box(o, 640, 164, 200, 64, "PC", "serial_bridge.py", ACCENT)
    o.append(f'<text x="740" y="248" fill="{DIM}" font-size="10.5" '
             f'text-anchor="middle">→ WAV 4 voies, ou direction en direct</text>')

    # encadré : pourquoi c'est synchrone
    o.append(f'<rect x="864" y="92" width="186" height="196" rx="5" '
             f'fill="#0d1a22" stroke="{BLUE}" stroke-width="1.6"/>')
    o.append(f'<text x="957" y="116" fill="{BLUE}" font-size="12.5" '
             f'font-weight="700" text-anchor="middle">LE POINT CLÉ</text>')
    for k, t in enumerate([
            "Un SEUL périphérique SAI",
            "génère BCLK et LRCLK pour",
            "les quatre capsules.",
            "",
            "Elles sont donc échantil-",
            "lonnées au même instant,",
            "par construction et non",
            "par réglage.",
            "",
            "C'est exactement ce qu'une",
            "mesure de temps d'arrivée",
            "exige."]):
        o.append(f'<text x="878" y="{138+k*13}" fill="#bde0f5" '
                 f'font-size="10">{t}</text>')

    # bandeau du bas : le câblage commun
    o.append(f'<rect x="40" y="368" width="800" height="72" rx="5" '
             f'fill="#12201a" stroke="{ORANGE}" stroke-width="1.2"/>')
    o.append(f'<text x="58" y="390" fill="{ORANGE}" font-size="11.5" '
             f'font-weight="700">CÂBLAGE COMMUN AUX QUATRE CAPSULES</text>')
    o.append(f'<text x="58" y="410" fill="{TXT}" font-size="10.5">'
             f'VDD → 3V3 · GND → GND · SCK → broche 21 · WS → broche 20. '
             f'Seules les broches SD et L/R distinguent les capsules.</text>')
    o.append(f'<text x="58" y="428" fill="{TXT}" font-size="10.5">'
             f'Câbles blindés de MÊME LONGUEUR, torsadés ; au-delà de 1,5 m '
             f'de barre, prévoyez des tampons de ligne côté horloges.</text>')
    o.append("</svg>")
    return "\n".join(o)


# ==========================================================================
def svg_usb():
    """PC ou Raspberry Pi + interface USB classe audio 2."""
    o = [f'<svg viewBox="0 0 1080 400" width="100%">',
         # `_arrow` (repris de schema_cablage) référence un marqueur nommé
         # « ar » : il faut donc le définir ici aussi, sinon les flèches
         # s'affichent sans pointe.
         f'<defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" '
         f'markerWidth="7" markerHeight="7" orient="auto">'
         f'<path d="M0,0 L10,5 L0,10 z" fill="{GRID_HI}"/></marker>'
         f'<marker id="au" viewBox="0 0 10 10" refX="9" refY="5" '
         f'markerWidth="7" markerHeight="7" orient="auto">'
         f'<path d="M0,0 L10,5 L0,10 z" fill="{GRID_HI}"/></marker></defs>',
         f'<rect width="1080" height="400" fill="{PANEL}" rx="6"/>',
         f'<text x="30" y="34" fill="{ACCENT}" font-size="15" font-weight="700" '
         f'letter-spacing="1.5">MONTAGE B — PC OU RASPBERRY PI + INTERFACE '
         f'USB CLASSE AUDIO 2</text>',
         f'<text x="30" y="56" fill="{DIM}" font-size="11.5">'
         f'Plus cher, mais rien à mettre au point : le mode Direct '
         f'd\'AERO-SPECTRIX ouvre l\'interface tel quel.</text>']

    for i, y in enumerate((88, 142, 196, 250)):
        _box(o, 40, y, 140, 44, f"M{i+1}", "électret ou capsule" if i == 0 else "")
        _arrow(o, 180, y + 22, 300, y + 22, GRID_HI,
               "câble blindé" if i == 0 else "")
        o.append(f'<text x="240" y="{y+38}" fill="{DIM}" font-size="9.5" '
                 f'text-anchor="middle">entrée {i+1}</text>')

    _box(o, 300, 88, 216, 206, "INTERFACE 4 PRÉAMPLIS", "", ACCENT)
    o.append(f'<text x="408" y="160" fill="{TXT}" font-size="11.5" '
             f'text-anchor="middle">classe audio 2 (UAC2)</text>')
    o.append(f'<text x="408" y="182" fill="{ACCENT}" font-size="12" '
             f'font-weight="700" text-anchor="middle">UNE SEULE HORLOGE</text>')
    o.append(f'<text x="408" y="212" fill="{ORANGE}" font-size="10.5" '
             f'text-anchor="middle">Windows : pilote ASIO</text>')
    o.append(f'<text x="408" y="228" fill="{ORANGE}" font-size="10.5" '
             f'text-anchor="middle">du constructeur OBLIGATOIRE</text>')
    o.append(f'<text x="408" y="252" fill="{ACCENT}" font-size="10.5" '
             f'text-anchor="middle">Linux : aucun pilote à installer,</text>')
    o.append(f'<text x="408" y="268" fill="{ACCENT}" font-size="10.5" '
             f'text-anchor="middle">snd-usb-audio suffit</text>')

    _arrow(o, 516, 191, 636, 191, ACCENT, "USB — 4 voies")
    _box(o, 638, 160, 200, 64, "PC ou Raspberry Pi", "mode Direct", ACCENT)

    o.append(f'<rect x="862" y="88" width="188" height="206" rx="5" '
             f'fill="#1a0d0d" stroke="{ALARM}" stroke-width="1.6"/>')
    o.append(f'<text x="956" y="112" fill="{ALARM}" font-size="12.5" '
             f'font-weight="700" text-anchor="middle">À NE PAS FAIRE</text>')
    for k, t in enumerate([
            "L'I²S natif du Raspberry",
            "Pi n'a qu'UNE ligne de",
            "données en entrée : deux",
            "voies, pas quatre.",
            "",
            "Une carte 4 micros à",
            "capsules soudées (type",
            "ReSpeaker) : l'écartement",
            "y est de quelques centi-",
            "mètres, inutilisable ici.",
            "",
            "Deux interfaces stéréo :",
            "horloges indépendantes."]):
        o.append(f'<text x="876" y="{134+k*12.4:.0f}" fill="#ffbdbd" '
                 f'font-size="10">{t}</text>')
    o.append("</svg>")
    return "\n".join(o)


# ==========================================================================
def build_html():
    return f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8">
<title>Montages d'évaluation à bas coût — AERO-SPECTRIX</title>
<style>
 body {{ background:{BG}; color:{TXT}; margin:0; padding:26px 30px 60px;
        font-family:"Segoe UI",system-ui,sans-serif; }}
 h1 {{ color:{ACCENT}; font-size:23px; margin:0 0 4px; }}
 h2 {{ color:{GRID_HI}; font-size:15px; margin:30px 0 10px;
       text-transform:uppercase; letter-spacing:1.6px; }}
 .sub {{ color:{DIM}; font-size:13px; margin-bottom:22px; }}
 .wrap {{ max-width:1120px; margin:0 auto; }}
 table {{ border-collapse:collapse; width:100%; font-size:13px;
          font-family:Consolas,monospace; }}
 th {{ background:#111b1f; color:{ACCENT}; text-align:left; padding:7px 10px;
       font-size:11px; letter-spacing:1px; text-transform:uppercase; }}
 td {{ padding:6px 10px; border-top:1px solid #16302a; }}
 tr:nth-child(even) td {{ background:#0b1518; }}
 td.ok {{ color:{ACCENT}; font-weight:600; }}
 td.no {{ color:{ALARM}; font-weight:600; }}
</style></head><body><div class="wrap">
<h1>Montages d'évaluation à bas coût</h1>
<div class="sub">Deux façons d'obtenir quatre voies rigoureusement synchrones
sans investir dans une chaîne de mesure complète.</div>

<h2>A · Teensy 4 et capsules MEMS</h2>
<div id="fig-teensy">{svg_teensy()}</div>

<h2>B · Interface USB classe audio 2</h2>
<div id="fig-usb">{svg_usb()}</div>

<h2>C · Comparaison</h2>
<table id="tab-lowcost">
<tr><th>Critère</th><th>A — Teensy + MEMS</th><th>B — Interface USB</th></tr>
<tr><td>Coût indicatif</td><td class="ok">60 – 90 €</td><td>150 – 220 €</td></tr>
<tr><td>Mise au point</td><td>flasher un croquis, vérifier les niveaux</td>
<td class="ok">aucune</td></tr>
<tr><td>Échantillonnage</td><td>44 100 Hz, 16 bits</td>
<td class="ok">48 000 Hz, 24 bits</td></tr>
<tr><td>Bruit propre du capteur</td><td>29 à 33 dB(A)</td>
<td class="ok">14 dB(A) avec un EM272</td></tr>
<tr><td>Longueur de câble</td><td>quelques mètres (I²S)</td>
<td class="ok">plusieurs dizaines de mètres</td></tr>
<tr><td>Fonctionne avec le mode Direct</td>
<td>non — passe par <code>serial_bridge.py</code></td><td class="ok">oui</td></tr>
<tr><td>Consommation</td><td class="ok">~0,5 W, sur batterie USB</td>
<td>5 à 10 W avec le calculateur</td></tr>
</table>
</div></body></html>
"""


def main():
    out = os.path.join(HERE, "schema_lowcost.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(build_html())
    print(f"Schéma écrit : {out}")


if __name__ == "__main__":
    main()
