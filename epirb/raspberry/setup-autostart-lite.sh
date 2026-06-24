#!/usr/bin/env bash
# ============================================================================
#  setup-autostart-lite.sh
#  Active / désactive le lancement automatique d'EPIRBpi-decoder-lite au
#  démarrage du bureau Raspberry Pi (mode kiosque).
#
#  Couvre les deux sessions de Raspberry Pi OS :
#    - Wayland / labwc  (Pi OS « Trixie », Pi 5)  -> ~/.config/labwc/autostart
#    - Bureaux honorant freedesktop (X11, wayfire) -> ~/.config/autostart/*.desktop
#
#  Usage :
#    ./setup-autostart-lite.sh            (= enable)
#    ./setup-autostart-lite.sh enable
#    ./setup-autostart-lite.sh disable
#    ./setup-autostart-lite.sh status
#
#  À lancer en tant qu'UTILISATEUR normal (pas root) : l'autostart est par
#  utilisateur. F1GBD / ADRASEC 77.
# ============================================================================
set -euo pipefail

ACTION="${1:-enable}"

APPNAME="EPIRB 406 MHz Decoder"
DESKTOP_ID="EPIRBpi-decoder-lite"
XDG_AUTOSTART="$HOME/.config/autostart/$DESKTOP_ID.desktop"
LABWC_AUTOSTART="$HOME/.config/labwc/autostart"
MARK_BEGIN="# >>> EPIRBpi-decoder-lite >>>"
MARK_END="# <<< EPIRBpi-decoder-lite <<<"
DELAY=4   # secondes d'attente avant lancement (laisse le bureau s'initialiser)

if [ "$(id -u)" = "0" ]; then
    echo "ERREUR : lancez ce script en utilisateur normal (sans sudo)."
    echo "         L'autostart est propre à votre session graphique."
    exit 1
fi

# ----- Localiser le lanceur installé -----
find_launcher() {
    if command -v epirbpi-decoder-lite >/dev/null 2>&1; then
        command -v epirbpi-decoder-lite; return 0
    fi
    local p
    for p in \
        /opt/EPIRBpi-decoder-lite/EPIRBpi-decoder-lite.sh \
        "$HOME/.local/share/EPIRBpi-decoder-lite/EPIRBpi-decoder-lite.sh" \
        "$HOME/.local/bin/epirbpi-decoder-lite"; do
        [ -x "$p" ] && { echo "$p"; return 0; }
    done
    return 1
}

remove_autostart() {
    rm -f "$XDG_AUTOSTART"
    if [ -f "$LABWC_AUTOSTART" ]; then
        sed -i "\|$MARK_BEGIN|,\|$MARK_END|d" "$LABWC_AUTOSTART"
    fi
}

case "$ACTION" in
    disable)
        remove_autostart
        echo "Lancement automatique DÉSACTIVÉ."
        exit 0
        ;;
    status)
        if [ -f "$XDG_AUTOSTART" ]; then echo "  autostart XDG    : ACTIF   ($XDG_AUTOSTART)"
        else echo "  autostart XDG    : inactif"; fi
        if [ -f "$LABWC_AUTOSTART" ] && grep -qF "$MARK_BEGIN" "$LABWC_AUTOSTART"; then
            echo "  autostart labwc  : ACTIF   ($LABWC_AUTOSTART)"
        else echo "  autostart labwc  : inactif"; fi
        exit 0
        ;;
    enable|"")
        ;;
    *)
        echo "Usage : $0 [enable|disable|status]"; exit 1
        ;;
esac

# ----- ENABLE -----
LAUNCHER="$(find_launcher)" || {
    echo "ERREUR : lanceur introuvable."
    echo "         Installez d'abord l'application :"
    echo "           sudo ./install-lite.sh --system"
    exit 1
}
echo "Lanceur détecté : $LAUNCHER"

# On repart propre (idempotent)
remove_autostart

# 1) Autostart XDG (.desktop) — X11, wayfire, et bureaux freedesktop
mkdir -p "$(dirname "$XDG_AUTOSTART")"
cat > "$XDG_AUTOSTART" <<EOF
[Desktop Entry]
Type=Application
Name=$APPNAME
Comment=Décodeur balise 406 MHz — lancement automatique
Exec=sh -c 'sleep $DELAY; exec "$LAUNCHER"'
Terminal=false
X-GNOME-Autostart-enabled=true
EOF
echo "Créé  : $XDG_AUTOSTART"

# 2) Autostart labwc (Pi OS Trixie / Wayland) — bloc balisé idempotent
mkdir -p "$(dirname "$LABWC_AUTOSTART")"
touch "$LABWC_AUTOSTART"
{
    echo "$MARK_BEGIN"
    echo "( sleep $DELAY; \"$LAUNCHER\" ) &"
    echo "$MARK_END"
} >> "$LABWC_AUTOSTART"
chmod +x "$LABWC_AUTOSTART" 2>/dev/null || true
echo "Mis à jour : $LABWC_AUTOSTART"

cat <<EOF

============================================================
 Lancement automatique ACTIVÉ.
 Au prochain redémarrage, l'application se lancera seule.

 Tester sans redémarrer        : $LAUNCHER
 Redémarrer maintenant         : sudo reboot
 Désactiver l'autostart        : ./setup-autostart-lite.sh disable
 Vérifier l'état               : ./setup-autostart-lite.sh status
============================================================

 IMPORTANT — pré-requis :
 1) Le Pi doit démarrer sur le BUREAU avec connexion automatique.
    Réglage : sudo raspi-config  ->  1 System Options  ->  S5 Boot / Auto Login
              ->  « Desktop Autologin ».
 2) Pour un vrai kiosque, désactivez la mise en veille de l'écran :
    sudo raspi-config  ->  2 Display Options  ->  Screen Blanking  ->  Disable.
EOF
