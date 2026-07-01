#!/usr/bin/env bash
# =====================================================================
#  install_pi.sh  -  MeshRNS Pi  -  ADRASEC 77 / F1GBD
#  Configuration systeme (Raspberry Pi OS 64 bits) pour l'edition autonome.
#  A lancer UNE FOIS apres extraction de l'archive, depuis le dossier de l'appli.
#  Usage : chmod +x install_pi.sh && ./install_pi.sh
#
#  MeshRNS est une passerelle Reticulum / LXMF : PAS de Direwolf, PAS d'AX.25.
#  La pile Reticulum se connecte en lisant ~/.reticulum/config (voir plus bas).
# =====================================================================
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"

echo "============================================================"
echo "  MeshRNS Pi - configuration systeme"
echo "============================================================"

# 1. Acces aux ports serie sans sudo (companion MeshCore USB) : groupe dialout
if id -nG "$USER" | grep -qw dialout; then
    echo "-- $USER est deja dans le groupe 'dialout'."
else
    echo "-- Ajout de $USER au groupe 'dialout' (acces /dev/ttyACM*, /dev/ttyUSB*)."
    sudo usermod -aG dialout "$USER"
    echo "   >> DECONNECTEZ / RECONNECTEZ votre session pour l'appliquer."
fi

# 2. Bluetooth (OPTIONNEL) : seulement si companion MeshCore en BLE (transport=ble)
echo "-- Bluetooth (optionnel, companion BLE) --"
sudo apt-get update -qq || true
sudo apt-get install -y bluez rfkill 2>/dev/null \
  || echo "   (bluez non installe : sans effet si le companion est en USB/serie.)"

# 3. Raccourci dans le menu (si le binaire est present a cote de ce script)
BIN="$HERE/MeshRNS"
if [ -x "$BIN" ]; then
    echo "-- Raccourci application (menu)."
    APPS="$HOME/.local/share/applications"
    mkdir -p "$APPS"
    ICON="$HERE/MeshRNS.png"
    cat > "$APPS/meshrns-pi.desktop" <<DESK
[Desktop Entry]
Type=Application
Name=MeshRNS Pi
Comment=Passerelle Reticulum/LXMF pour MeshCore (ADRASEC 77)
Exec=$BIN
Icon=$ICON
Terminal=false
Categories=HamRadio;Network;Utility;
DESK
    chmod +x "$APPS/meshrns-pi.desktop"
    echo "   -> $APPS/meshrns-pi.desktop"
else
    echo "-- (Binaire 'MeshRNS' non trouve a cote : raccourci ignore.)"
fi

# 4. Rappel configuration Reticulum
echo "------------------------------------------------------------"
echo "  Reticulum : MeshRNS lit ~/.reticulum/config."
echo "  - 1er lancement sur machine vierge : une config par defaut est"
echo "    installee automatiquement (a adapter a votre reseau ADRASEC)."
echo "  - Sinon, placez votre ~/.reticulum/config (interface RNode LoRa /"
echo "    TCP / I2P qui joint vos stations TCQ)."
echo "  - Verifier les interfaces : 'rnstatus' (paquet rns, si installe)."
echo "------------------------------------------------------------"

echo "============================================================"
echo "  Termine. Lancez l'application :  $HERE/MeshRNS"
echo "============================================================"
