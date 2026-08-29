#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Banc d'essai du dialogue de configuration de la tete WiFi.

    cd osjt_maghead_lora
    python -m pip install msgpack
    python test/test_provisioning.py

CE QUE CE BANC PROUVE, ET POURQUOI IL EXISTE
--------------------------------------------
Le firmware embarque son propre codec MsgPack — une centaine de lignes
ecrites a la main plutot qu'une bibliotheque generique, pour les raisons
exposees dans osjt_msgpack.h. Un codec binaire ecrit a la main sans banc
d'essai est une prise de risque : une erreur d'un octet ne se voit pas, elle
se manifeste six semaines plus tard par une tete qui refuse toute
configuration sur le bureau d'un operateur.

Le banc compile le firmware TEL QUEL, avec un faux Arduino et un faux NVS,
et confronte chaque octet a la bibliotheque msgpack de reference — celle que
parle la console RWLoRa. Ce qui est verifie ici est donc exactement ce qui
circulera sur le cable USB.

Il ne demande ni carte, ni PlatformIO : un compilateur C++ et msgpack.
"""

import os
import random
import subprocess
import sys

try:
    import msgpack
except ImportError:
    print("Il faut la bibliotheque de reference : python -m pip install msgpack")
    sys.exit(2)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BENCH = os.path.join(HERE, "prov_bench")
MPB = os.path.join(HERE, "mp_bench")

FEND, FESC, TFEND, TFESC = 0xC0, 0xDB, 0xDC, 0xDD
CMD_REQ, CMD_RSP = 0x86, 0x87

_fails = 0


def build():
    """Compile les deux bancs. Le firmware n'est pas modifie pour l'occasion."""
    exe = ".exe" if os.name == "nt" else ""
    jobs = [
        (["src/provisioning.cpp", "test/prov_bench.cpp"], BENCH + exe),
        (["test/mp_bench.cpp"], MPB + exe),
    ]
    for srcs, out in jobs:
        cmd = ["g++", "-std=c++11", "-Wall", "-Wextra",
               "-Itest/shim", "-Iinclude"] + srcs + ["-o", out]
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        if r.returncode:
            print("Compilation impossible :")
            print(r.stderr)
            sys.exit(2)
        if r.stderr.strip():
            print("AVERTISSEMENTS du compilateur :")
            print(r.stderr)
            sys.exit(2)
    return BENCH + exe, MPB + exe


def kiss(cmd, payload):
    out = bytearray([FEND, cmd])
    for b in payload:
        if b == FEND:
            out += bytes([FESC, TFEND])
        elif b == FESC:
            out += bytes([FESC, TFESC])
        else:
            out.append(b)
    out.append(FEND)
    return bytes(out)


def req(op, seq, payload):
    return kiss(CMD_REQ, msgpack.packb([op, seq, payload], use_bin_type=True))


def dekiss(data):
    out, st, cmd, buf, esc = [], "idle", None, bytearray(), False
    for b in data:
        if b == FEND:
            if st == "frame" and cmd == CMD_RSP and buf:
                out.append(bytes(buf))
            st, esc = "cmd", False
            buf.clear()
            continue
        if st == "cmd":
            cmd = b
            st = "frame" if b == CMD_RSP else "idle"
            continue
        if st == "frame":
            if esc:
                b = FEND if b == TFEND else (FESC if b == TFESC else b)
                esc = False
            elif b == FESC:
                esc = True
                continue
            buf.append(b)
    return out


def frames(hexline):
    return [msgpack.unpackb(f, raw=False, strict_map_key=False)
            for f in dekiss(bytes.fromhex(hexline))]


def chk(name, cond, extra=""):
    global _fails
    if not cond:
        _fails += 1
    print(("[OK ] " if cond else "[FAUX] ") + name
          + (("\n       " + str(extra)) if not cond else ""))


def main():
    bench, mpb = build()

    def run(*cmds):
        r = subprocess.run([bench] + list(cmds), capture_output=True, text=True)
        if r.returncode:
            print("banc en erreur :", r.stderr)
            sys.exit(2)
        return r.stdout.splitlines()

    def emit(case):
        return subprocess.run([mpb, "emit", case],
                              capture_output=True, text=True).stdout.strip()

    print("--- 1. le codec du firmware, octet pour octet contre msgpack ---")
    for case, obj in [
        ("commit",   [6, 1, None]),
        ("getstate", [4, 300, {1: [101]}]),
        ("state",    [100, 7, {101: {1: "ADRASEC77-AP", 3: "192.168.1.20",
                                     4: 10077}}]),
        ("error",    [101, 9, {1: 5, 2: "Valeur invalide"}]),
        ("edges",    [0, 127, 128, 255, 256, 65535, 65536, -1, -32769]),
        ("longstr",  ["a" * 31, "b" * 32, "c" * 300]),
    ]:
        chk("encodage " + case,
            emit(case) == msgpack.packb(obj, use_bin_type=True).hex(),
            emit(case))

    print()
    print("--- 2. lecture de ce que la console envoie ---")
    o = run("begin", "rx:" + req(4, 1, {1: [101]}).hex(), "out")
    chk("GET_STATE sur une tete vierge",
        frames(o[0]) == [[100, 1, {101: {1: "", 3: "", 4: 10077}}]], frames(o[0]))

    o = run("nvs:ssid=Livebox-A1B2", "nvs:pass=secret",
            "nvs:host=192.168.1.20", "nvs:port=10078", "begin",
            "rx:" + req(4, 2, {1: [101]}).hex(), "out")
    chk("GET_STATE sur une tete configuree",
        frames(o[0]) == [[100, 2, {101: {1: "Livebox-A1B2",
                                         3: "192.168.1.20", 4: 10078}}]],
        frames(o[0]))
    # Le champ 2 part vers la tete, jamais l'inverse : une console capable de
    # relire la cle WiFi serait un moyen de l'extraire de toute tete a
    # laquelle on a acces physique.
    chk("le mot de passe n'est jamais rendu",
        b"secret" not in bytes.fromhex(o[0]))

    print()
    print("--- 3. ecriture, validation et persistance ---")
    o = run("begin",
            "rx:" + req(5, 3, {101: {1: "ADRASEC77", 2: "mot de passe 77",
                                     3: "192.168.1.20", 4: 10077}}).hex(),
            "out", "cfg", "rx:" + req(6, 4, None).hex(), "out", "nvs", "reboot")
    chk("SET_STATE accepte", frames(o[0]) == [[100, 3, {}]], frames(o[0]))
    chk("configuration en vigueur",
        o[1] == "ssid='ADRASEC77' pass='mot de passe 77' "
                "host='192.168.1.20' port=10077", o[1])
    chk("COMMIT signale qu'un redemarrage est requis",
        frames(o[2]) == [[100, 4, {1: 1}]], frames(o[2]))
    chk("configuration ecrite en memoire non volatile",
        o[3] == "ssid='ADRASEC77' pass='mot de passe 77' "
                "host='192.168.1.20' port=10077", o[3])

    # Ne pas envoyer le mot de passe ne doit pas l'effacer : il revient vide
    # en lecture, et l'ecrire tel quel effacerait celui qui est enregistre.
    o = run("nvs:ssid=A", "nvs:pass=ancien", "nvs:host=h", "nvs:port=1",
            "begin", "rx:" + req(5, 5, {101: {1: "B"}}).hex(), "cfg")
    chk("mot de passe preserve s'il n'est pas envoye",
        o[0] == "ssid='B' pass='ancien' host='h' port=1", o[0])

    print()
    print("--- 4. refus argumentes ---")
    o = run("begin", "rx:" + req(5, 6, {101: {4: 0}}).hex(), "out")
    chk("port 0 refuse et rendu", frames(o[0]) == [[100, 6, {3: [4]}]],
        frames(o[0]))
    o = run("begin", "rx:" + req(5, 7, {101: {4: 70000}}).hex(), "out")
    chk("port 70000 refuse et rendu", frames(o[0]) == [[100, 7, {3: [4]}]],
        frames(o[0]))
    o = run("begin", "rx:" + req(5, 8, {101: {9: "x"}}).hex(), "out")
    chk("champ inconnu refuse et rendu", frames(o[0]) == [[100, 8, {3: [9]}]],
        frames(o[0]))

    # 33 a 64 caracteres : la chaine tient dans le tampon de lecture, le champ
    # la refuse et le dit. Au-dela de 64 elle ne tient plus, et c'est une
    # erreur franche — jamais une troncature silencieuse, qui donnerait un
    # mot de passe ampute accepte sans un mot.
    o = run("nvs:ssid=bon", "begin",
            "rx:" + req(5, 9, {101: {1: "S" * 40}}).hex(), "out", "cfg")
    chk("SSID de 40 caracteres refuse", frames(o[0]) == [[100, 9, {3: [1]}]],
        frames(o[0]))
    chk("SSID inchange apres refus", o[1].startswith("ssid='bon'"), o[1])
    o = run("nvs:ssid=bon", "begin",
            "rx:" + req(5, 10, {101: {1: "S" * 100}}).hex(), "out", "cfg")
    f = frames(o[0])
    chk("SSID de 100 caracteres : erreur franche",
        len(f) == 1 and f[0][0] == 101 and f[0][2][1] == 5, f)
    chk("SSID inchange apres erreur", o[1].startswith("ssid='bon'"), o[1])

    chk("SSID de 32 caracteres accepte",
        run("begin", "rx:" + req(5, 11, {101: {1: "S" * 32}}).hex(),
            "cfg")[0].startswith("ssid='" + "S" * 32 + "'"))
    chk("mot de passe de 64 caracteres accepte",
        "pass='" + "P" * 64 + "'" in
        run("begin", "rx:" + req(5, 12, {101: {2: "P" * 64}}).hex(), "cfg")[0])

    # Une console RWLoRa demanderait aussi le namespace radio 100. Cette tete
    # n'a pas de radio a regler : elle le dit, au lieu de faire semblant.
    o = run("begin", "rx:" + req(5, 13, {100: {1: 868100000}}).hex(), "out")
    f = frames(o[0])
    chk("namespace radio seul : refus explicite",
        len(f) == 1 and f[0][0] == 101 and f[0][2][1] == 3, f)
    o = run("begin",
            "rx:" + req(5, 14, {100: {1: 868100000},
                                101: {1: "X"}}).hex(), "out", "cfg")
    chk("namespace radio ignore si le reseau est present",
        frames(o[0]) == [[100, 14, {}]], frames(o[0]))
    chk("le namespace reseau est traite malgre l'autre",
        o[1].startswith("ssid='X'"), o[1])

    o = run("begin", "rx:" + req(42, 15, None).hex(), "out")
    f = frames(o[0])
    chk("operation inconnue", len(f) == 1 and f[0][0] == 101 and f[0][2][1] == 2, f)

    o = run("begin", "rx:" + req(5, 16, {101: {1: "Y"}}).hex(), "fail",
            "rx:" + req(6, 17, None).hex(), "out")
    f = [x for x in frames(o[0]) if x[1] == 17]
    chk("echec d'ecriture en flash signale, pas tu",
        len(f) == 1 and f[0][0] == 101 and f[0][2][1] == 8, f)

    o = run("begin", "rx:" + req(9, 18, None).hex(), "reboot")
    chk("REBOOT redemarre la tete", o[0] == "needs=0 restarted=1", o[0])

    print()
    print("--- 5. le fil, tel qu'il arrive vraiment ---")
    # Un port serie ne livre pas des trames entieres : il livre des octets.
    o = run("begin", "rx1:" + req(4, 19, {1: [101]}).hex(), "out")
    chk("reception octet par octet",
        frames(o[0]) == [[100, 19, {101: {1: "", 3: "", 4: 10077}}]],
        frames(o[0]))

    # La tete journalise sur le meme port. Le texte ne doit rien casser.
    stream = (b"# tete WiFi prete\n# RM3100 CC=800\n"
              + req(4, 20, {1: [101]})
              + b"# WiFi associe - IP 192.168.1.44\n"
              + req(6, 21, None))
    o = run("begin", "rx1:" + stream.hex(), "out")
    chk("journal sortant melange aux trames entrantes",
        [g[1] for g in frames(o[0])] == [20, 21], frames(o[0]))

    # Un mot de passe qui contient les octets d'echappement KISS : c'est
    # improbable en ASCII, mais l'echappement doit tenir quand meme.
    pw = "".join(chr(c) for c in (0xC0, 0xDB, 0xDC, 0xDD))
    o = run("begin", "rx:" + req(5, 22, {101: {2: pw}}).hex(), "cfg")
    chk("octets d'echappement dans une valeur",
        o[0].split("pass='")[1].split("'")[0].encode("utf-8")
        == pw.encode("utf-8"), o[0])

    print()
    print("--- 6. ce qui n'est pas une trame ---")
    good = req(5, 23, {101: {1: "abc", 4: 10077}})
    bad = 0
    for n in range(1, len(good) - 1):        # -1 : sans le FEND de fin
        o = run("begin", "rx:" + good[:n].hex() + "c0", "out")
        for g in frames(o[0]):
            if g[0] == 100:                  # un ACK sur une trame tronquee
                bad += 1
    chk(f"troncatures ({len(good) - 2} prefixes) : aucun acquittement indu",
        bad == 0, bad)

    random.seed(7)
    for _ in range(300):
        junk = bytes(random.randrange(256)
                     for _ in range(random.randrange(1, 80)))
        run("begin", "rx:" + junk.hex(), "out")
    chk("300 salves d'octets aleatoires : ni plantage ni blocage", True)

    # Une trame plus longue que le tampon de reception doit etre abandonnee,
    # pas ecrire au-dela.
    o = run("begin", "rx:" + kiss(CMD_REQ, b"\x93" + b"\x00" * 2000).hex(), "out")
    chk("trame surdimensionnee abandonnee sans reponse", o[0] == "", o[0])

    print()
    print("VERDICT : " + ("CONFORME" if _fails == 0 else f"{_fails} DEFAUT(S)"))
    return 1 if _fails else 0


if __name__ == "__main__":
    sys.exit(main())
