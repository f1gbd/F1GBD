# ---------------------------------------------------------------------------
#  Script post-build PlatformIO : fabrique un binaire unique flashable a 0x0.
#
#  Il fusionne bootloader + table de partitions + boot_app0 + application en
#  un seul fichier, indispensable pour ESP Web Tools (flashage depuis un
#  navigateur) et pratique pour les mises a jour manuelles a l'esptool.
#
#  Sortie : .pio/build/<env>/<env>-merged.bin
#  Active via   extra_scripts = post:tools/merge_bin.py   dans platformio.ini
# ---------------------------------------------------------------------------
Import("env")

import os
import shutil

board = env.BoardConfig()


def _esptool_cmd():
    """Retourne la commande esptool a utiliser (binaire du penv, ou module)."""
    exe = shutil.which("esptool")
    if exe:
        return [exe]
    return [env.subst("$PYTHONEXE"), "-m", "esptool"]


def merge_bin(source, target, env):
    app_offset = env.subst("$ESP32_APP_OFFSET") or "0x10000"
    firmware = env.subst("$BUILD_DIR/${PROGNAME}.bin")
    out = os.path.join(env.subst("$BUILD_DIR"), env.subst("$PIOENV") + "-merged.bin")

    # bootloader, table de partitions, boot_app0... fournis par le builder
    images = []
    for offset, path in env.get("FLASH_EXTRA_IMAGES", []):
        images += [str(offset), env.subst(path)]
    images += [app_offset, firmware]

    cmd = _esptool_cmd() + [
        "--chip", board.get("build.mcu", "esp32"),
        "merge-bin",
        "-o", out,
        "--flash-mode", board.get("build.flash_mode", "dio"),
        "--flash-freq", "80m",
        "--flash-size", board.get("upload.flash_size", "4MB"),
    ] + images

    env.Execute(env.VerboseAction(" ".join('"%s"' % c for c in cmd),
                                  "Fusion en un binaire unique -> %s" % out))
    if os.path.exists(out):
        print("[merge_bin] %s (%d octets) - a flasher a l'offset 0x0"
              % (out, os.path.getsize(out)))


env.AddPostAction("$BUILD_DIR/${PROGNAME}.bin", merge_bin)
