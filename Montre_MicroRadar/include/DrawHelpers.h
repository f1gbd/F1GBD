#pragma once

#include "LGFX.h"
#include "DisplayConfig.h"

// Balayage radar. Identique a la version C3, sauf que les couleurs sont
// devenues des index de palette (sprite 4 bits).
inline void DrawScanLines(LGFX_Sprite& buf, const int x0, const int y0, const int x1, const int y1, const int thickness, const int trailBrightness, const int spacing)
{
    float dx = x1 - x0;
    float dy = y1 - y0;
    float len = sqrt(dx * dx + dy * dy);
    if (len <= 0.0f) return;

    // vecteur unitaire perpendiculaire
    float px = -dy / len;
    float py = dx / len;

    for (int i = 0; i <= thickness; i++) {
        // 1.0 au centre, 0.0 sur les bords
        float t = i / (float)(thickness);
        uint8_t brightness = (uint8_t)(t * trailBrightness);

        buf.drawLine(
            x0, y0,
            x1 + (px * (i * spacing)), y1 + (py * (i * spacing)),
            G(brightness)
        );
    }

    buf.drawLine(
        x0, y0,
        x1 + (px * (thickness * spacing)), y1 + (py * (thickness * spacing)),
        COL_RING
    );
}

// Ecran de statut (boot / WiFi / erreur), rendu dans la sprite puis pousse.
//
// A NOTER : le pilote Panel_AMOLED de LovyanGFX impose que X et la largeur de
// toute fenetre d'ecriture soient PAIRS, sinon la commande est ignoree
// silencieusement. Ecrire du texte directement sur "tft" fait donc disparaitre
// des caracteres au hasard. On passe donc TOUT par la sprite plein ecran, que
// l'on pousse en (0,0) sur 410 px de large -> toujours aligne.
inline void ShowStatus(LGFX_Sprite& buf, const char* line1, const char* line2 = nullptr, const char* line3 = nullptr)
{
    buf.fillScreen(COL_BLACK);
    buf.setTextSize(2);
    buf.setTextColor(COL_BRIGHT);

    const int lineHeight = buf.fontHeight() + 12;
    int y = SCREEN_H / 2 - lineHeight;

    buf.drawCentreString(line1, SCREEN_W / 2, y);
    if (line2) {
        buf.setTextColor(COL_TEXT);
        buf.drawCentreString(line2, SCREEN_W / 2, y + lineHeight);
    }
    if (line3) {
        buf.setTextColor(COL_BRIGHT);
        buf.drawCentreString(line3, SCREEN_W / 2, y + lineHeight * 2);
    }

    buf.pushSprite(0, 0);
}
