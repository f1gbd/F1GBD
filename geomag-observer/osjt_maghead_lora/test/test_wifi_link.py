#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Le client de GEOMAG-Observer confronte au VRAI firmware.

    cd osjt_maghead_lora
    python test/test_wifi_link.py

CE QUE CE BANC AJOUTE A test_provisioning.py
--------------------------------------------
test_provisioning.py eprouve le firmware contre la bibliotheque msgpack de
reference. Celui-ci branche l'un sur l'autre les DEUX codes qui devront se
parler : la classe SensorProvisioning de geomag_observer.py d'un cote, le
firmware compile de l'autre, relies par un faux port serie.

C'est la seule facon d'attraper une erreur symetrique — les deux cotes qui
se trompent de la meme facon et se comprennent parfaitement entre eux, mais
ne correspondent a rien. Chacun teste separement, on ne la voit pas.

Aucune carte n'est necessaire : un compilateur C++ suffit. Le fichier
geomag_observer.py est importe tel quel — il n'ouvre tkinter que dans ses
fonctions d'interface, donc l'import ne demande pas d'affichage.
"""

import os
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
# geomag_observer.py est deux niveaux au-dessus : osjt\osjt_maghead_lora\test
APP = os.path.dirname(ROOT)
sys.path.insert(0, APP)

try:
    import geomag_observer as G
except ImportError as e:
    print("geomag_observer.py est introuvable au-dessus de "
          f"{ROOT} ({e}).\n\n"
          "Ce banc confronte le firmware au client de l'application : il "
          "lui faut donc les deux. Il tourne dans l'arbre de developpement "
          "OSJT, ou geomag_observer.py est le repertoire parent. Depuis le "
          "seul depot des sources firmware, utiliser test_provisioning.py, "
          "qui se suffit a lui-meme.")
    sys.exit(2)

_fails = 0


def chk(name, cond, extra=""):
    global _fails
    if not cond:
        _fails += 1
    print(("[OK ] " if cond else "[FAUX] ") + name
          + (("\n       " + str(extra)) if not cond else ""))


class FakeSerial:
    """Un port serie qui va au firmware compile, et en revient.

    L'ecriture pousse les octets dans le processus ; ce qu'il repond est mis
    en attente et rendu par read(), exactement comme le ferait pyserial. Le
    client ne sait pas qu'il ne parle pas a une carte.
    """

    def __init__(self, proc):
        self.proc = proc
        self.inbox = bytearray()
        self.lock = threading.Lock()
        # Le firmware journalise des son demarrage, sur le meme fil : ces
        # octets-la arrivent avant toute requete, exactement comme sur une
        # carte qu'on vient de brancher.
        first = self.proc.stdout.readline().strip()
        if first:
            self.inbox += bytes.fromhex(first)

    def write(self, data):
        with self.lock:
            self.proc.stdin.write(data.hex() + "\n")
            self.proc.stdin.flush()
            line = self.proc.stdout.readline().strip()
            if line:
                self.inbox += bytes.fromhex(line)
        return len(data)

    def flush(self):
        pass

    def read(self, n=1):
        # Le fil de pompage du client appelle read() en boucle : on lui rend
        # ce qui est arrive, sans jamais bloquer indefiniment.
        for _ in range(50):
            with self.lock:
                if self.inbox:
                    out, self.inbox = bytes(self.inbox[:n]), self.inbox[n:]
                    return out
            time.sleep(0.005)
        return b""

    def reset_input_buffer(self):
        pass

    def close(self):
        try:
            self.proc.stdin.close()
            self.proc.wait(timeout=2)
        except Exception:
            self.proc.kill()


def link(bench):
    """Un client SensorProvisioning branche sur le firmware."""
    proc = subprocess.Popen([bench, "serve"], stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, text=True, bufsize=1)
    journal = []
    c = G.SensorProvisioning("FAUX", board="V4", timeout=5.0,
                             on_text=journal.append)
    c.ser = FakeSerial(proc)
    c._thread = threading.Thread(target=c._pump, daemon=True)
    c._thread.start()
    return c, journal


def build():
    exe = ".exe" if os.name == "nt" else ""
    out = os.path.join(HERE, "prov_bench" + exe)
    cmd = ["g++", "-std=c++11", "-Wall", "-Wextra", "-Itest/shim", "-Iinclude",
           "src/provisioning.cpp", "test/prov_bench.cpp", "-o", out]
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if r.returncode or r.stderr.strip():
        print("Compilation impossible :")
        print(r.stderr)
        sys.exit(2)
    return out


def main():
    bench = build()

    print("--- lecture, ecriture, relecture ---")
    c, journal = link(bench)
    st = c.get_state()
    chk("tete vierge : SSID vide, port 10077",
        st.get(G.PROV_FLD_SSID) == "" and st.get(G.PROV_FLD_PORT) == 10077, st)

    c.set_state({G.PROV_FLD_SSID: "ADRASEC77-AP",
                 G.PROV_FLD_PASS: "un mot de passe",
                 G.PROV_FLD_HOST: "192.168.1.20",
                 G.PROV_FLD_PORT: 10077})
    need = c.commit()
    chk("le commit demande un redemarrage", need is True, need)

    st = c.get_state()
    chk("relecture : SSID", st.get(G.PROV_FLD_SSID) == "ADRASEC77-AP", st)
    chk("relecture : hote", st.get(G.PROV_FLD_HOST) == "192.168.1.20", st)
    chk("relecture : port", st.get(G.PROV_FLD_PORT) == 10077, st)
    chk("relecture : le mot de passe n'est pas rendu",
        G.PROV_FLD_PASS not in st, st)

    print()
    print("--- ce que le client doit refuser de croire ---")
    try:
        c.set_state({G.PROV_FLD_PORT: 0})
        chk("port 0 : le refus remonte", False, "aucune exception")
    except RuntimeError as e:
        chk("port 0 : le refus remonte", "port" in str(e), e)

    try:
        c.set_state({G.PROV_FLD_SSID: "S" * 40})
        chk("SSID de 40 caracteres : le refus remonte", False, "aucune exception")
    except RuntimeError as e:
        chk("SSID de 40 caracteres : le refus remonte", "SSID" in str(e), e)

    st = c.get_state()
    chk("apres deux refus, la configuration est intacte",
        st.get(G.PROV_FLD_SSID) == "ADRASEC77-AP", st)

    print()
    print("--- les caracteres qui font tomber les protocoles ---")
    # Un mot de passe qui contient les octets d'encadrement KISS, et un SSID
    # accentue : ni l'un ni l'autre n'a le droit de casser le fil.
    dur = "".join(chr(x) for x in (0xC0, 0xDB, 0xDC, 0xDD))
    c.set_state({G.PROV_FLD_PASS: dur})
    chk("mot de passe contenant FEND et FESC : accepte", True)
    c.set_state({G.PROV_FLD_SSID: "Reseau-Ete", G.PROV_FLD_HOST: "pc-pco"})
    st = c.get_state()
    chk("SSID et hote relus a l'identique",
        st[G.PROV_FLD_SSID] == "Reseau-Ete" and st[G.PROV_FLD_HOST] == "pc-pco",
        st)
    # 32 et 64 caracteres sont les bornes exactes des champs.
    c.set_state({G.PROV_FLD_SSID: "S" * 32, G.PROV_FLD_PASS: "P" * 64})
    chk("SSID de 32 et mot de passe de 64 caracteres : acceptes",
        c.get_state()[G.PROV_FLD_SSID] == "S" * 32)

    print()
    print("--- le journal de la tete arrive bien au client ---")
    chk("le journal de demarrage est capte, hors bande",
        any("reseau" in x for x in journal), journal[:4])

    print()
    print("--- une carte qui n'est pas une tete WiFi ---")
    c.close()
    # Une carte muette : le client doit rendre un message qui dit quoi
    # faire, pas une trace Python.
    class Muet:
        def write(self, d):
            return len(d)

        def flush(self):
            pass

        def read(self, n=1):
            time.sleep(0.05)
            return b""

        def close(self):
            pass
    d = G.SensorProvisioning("FAUX", board="V4", timeout=1.0)
    d.ser = Muet()
    d._thread = threading.Thread(target=d._pump, daemon=True)
    d._thread.start()
    try:
        d.get_state()
        chk("carte muette : message explicite", False, "aucune exception")
    except TimeoutError as e:
        chk("carte muette : message explicite",
            "CAPTEUR WiFi" in str(e) and "acquisition" in str(e), e)

    print()
    print("--- la trame de mesure, du firmware au decodeur du PC ---")
    # La tete WiFi emet la trame de 36 octets du firmware Teensy. On la
    # fabrique avec le constructeur de reference du PC et on verifie que le
    # decodeur la relit — c'est le contrat que le firmware doit tenir.
    f = G.build_teensy_frame(7, 123456789, 21234.5, -1234.25, 42123.75, 20)
    chk("trame de 36 octets", len(f) == G.TEENSY_FRAME_LEN, len(f))
    r = G.parse_teensy_frame(f)
    chk("relecture de la trame",
        r and r["seq"] == 7 and abs(r["bx"] - 21234.5) < 1e-6
        and abs(r["bz"] - 42123.75) < 1e-6 and r["n"] == 20, r)
    chk("un octet modifie est rejete par le CRC",
        G.parse_teensy_frame(f[:10] + bytes([f[10] ^ 1]) + f[11:]) is None)

    print()
    print("--- reception UDP de bout en bout ---")
    # La tete emet en UDP ; on rejoue exactement cela sur la boucle locale et
    # on verifie que le backend « Heltec WiFi (UDP) » de l'application rend
    # les valeurs attendues. C'est le second contrat de la tete WiFi, apres
    # celui de sa configuration.
    import socket
    sensor = G.RM3100HeltecWifi(port=0, timeout=2.0)
    sensor.open()
    port = sensor.sock.getsockname()[1]
    tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    tx.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    tx.sendto(G.build_teensy_frame(1, 1000000, 21000.0, -1500.0, 42000.0, 18),
              ("127.0.0.1", port))
    bx, by, bz = sensor.read()
    chk("un datagramme = un echantillon",
        abs(bx - 21000.0) < 1e-6 and abs(by + 1500.0) < 1e-6
        and abs(bz - 42000.0) < 1e-6, (bx, by, bz))

    # Un datagramme corrompu ne doit pas etre pris pour une mesure : il est
    # ecarte, et le suivant passe. Une valeur fausse acceptee en silence
    # ferait un SSC qui n'a jamais eu lieu.
    bad = bytearray(G.build_teensy_frame(2, 2000000, 1.0, 2.0, 3.0, 1))
    bad[8] ^= 0xFF
    tx.sendto(bytes(bad), ("127.0.0.1", port))
    tx.sendto(G.build_teensy_frame(3, 3000000, 21001.5, -1499.0, 42002.0, 20),
              ("127.0.0.1", port))
    bx, by, bz = sensor.read()
    chk("datagramme corrompu ecarte, le suivant passe",
        abs(bx - 21001.5) < 1e-6, (bx, by, bz))

    # Un datagramme qui n'est pas une trame du tout : idem.
    tx.sendto(b"bonjour", ("127.0.0.1", port))
    tx.sendto(G.build_teensy_frame(4, 4000000, 20999.0, -1501.0, 41998.0, 19),
              ("127.0.0.1", port))
    bx, _, _ = sensor.read()
    chk("datagramme etranger ignore", abs(bx - 20999.0) < 1e-6, bx)

    # Silence : une erreur qui nomme le port, pas une attente sans fin.
    t0 = time.time()
    try:
        sensor.read()
        chk("silence : delai puis message", False, "aucune exception")
    except TimeoutError as e:
        chk("silence : delai puis message",
            str(port) in str(e) and 1.0 < time.time() - t0 < 6.0, e)

    chk("la description nomme la tete Heltec",
        "Heltec" in sensor.describe() and "WiFi" in sensor.describe(),
        sensor.describe())
    tx.close()
    sensor.close()

    print()
    print("VERDICT : " + ("CONFORME" if _fails == 0 else f"{_fails} DEFAUT(S)"))
    return 1 if _fails else 0


if __name__ == "__main__":
    sys.exit(main())
