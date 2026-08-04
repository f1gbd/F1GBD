#pragma once

// ============================================================================
//  Geometrie de l'ecran + couleurs du backbuffer.
//
//  Le backbuffer plein ecran 410 x 502 coute :
//      16 bpp : 410 * 502 * 2 = 411 640 octets
//       4 bpp : 410 * 502 / 2 = 102 910 octets
//
//  ESP32-S3 : 8 Mo de PSRAM  -> sprite 16 bits, couleurs RGB reelles.
//  ESP32-C6 : PAS de PSRAM, 512 Ko de SRAM seulement -> sprite en palette
//             4 bits (16 nuances de vert). En mode palette, les fonctions de
//             dessin de LovyanGFX recoivent un NUMERO DE PALETTE et non une
//             couleur RGB : d'ou la fonction G() ci-dessous qui renvoie l'un
//             ou l'autre selon la cible.
// ============================================================================

#include "LGFX.h"

// --- dalle -----------------------------------------------------------------
constexpr int SCREEN_W = 410;
constexpr int SCREEN_H = 502;

// --- profondeur du backbuffer ----------------------------------------------
#if defined(MICRORADAR_BOARD_S3)
  #define RADAR_COLOR_DEPTH_16 1
#else
  #define RADAR_COLOR_DEPTH_16 0
#endif

// --- zone radar ------------------------------------------------------------
// Le radar est projete dans un CARRE de cote RADAR_SPAN centre sur l'ecran.
//   RADAR_SPAN = SCREEN_H (502, defaut) -> radar plein ecran, le cercle
//                                          exterieur deborde a gauche/droite
//   RADAR_SPAN = SCREEN_W (410)         -> cercle entierement visible, bandes
//                                          noires de 46 px en haut et en bas
constexpr int RADAR_SPAN = SCREEN_H;

constexpr int RADAR_X0 = (SCREEN_W - RADAR_SPAN) / 2;  // origine X du carre
constexpr int RADAR_Y0 = (SCREEN_H - RADAR_SPAN) / 2;  // origine Y du carre
constexpr int RADAR_CX = RADAR_X0 + RADAR_SPAN / 2;    // centre X
constexpr int RADAR_CY = RADAR_Y0 + RADAR_SPAN / 2;    // centre Y
constexpr int RADAR_R  = RADAR_SPAN / 2 - 1;           // rayon exterieur

// --- couleurs ---------------------------------------------------------------
// G(niveau 0..255) -> vert d'intensite donnee.
#if RADAR_COLOR_DEPTH_16
// couleur RGB888 : 0x00GG00
constexpr uint32_t G(int level255)
{
    return static_cast<uint32_t>(level255 & 0xFF) << 8;
}
#else
// index de palette 0..15
constexpr uint32_t G(int level255)
{
    return static_cast<uint32_t>((level255 * 15 + 127) / 255);
}
#endif

constexpr uint32_t COL_BLACK      = 0;
constexpr uint32_t COL_RING_FAINT = G(32);
constexpr uint32_t COL_RING_MID   = G(64);
constexpr uint32_t COL_RING       = G(200);
constexpr uint32_t COL_TEXT       = G(128);
constexpr uint32_t COL_BRIGHT     = G(255);

// En mode palette, installe les 16 nuances de vert. Sans effet en 16 bits.
inline void InitRadarPalette(LGFX_Sprite& buf)
{
#if RADAR_COLOR_DEPTH_16
    (void)buf;
#else
    for (int i = 0; i < 16; ++i)
        buf.setPaletteColor(i, 0, i * 17, 0);
#endif
}

// Alloue le backbuffer plein ecran dans la bonne profondeur / memoire.
// Renvoie false si l'allocation echoue.
inline bool CreateBackbuffer(LGFX_Sprite& buf)
{
#if RADAR_COLOR_DEPTH_16
    buf.setColorDepth(lgfx::rgb565_2Byte);
    buf.setPsram(true);              // 412 Ko -> obligatoirement en PSRAM
#else
    buf.setColorDepth(lgfx::palette_4bit);
#endif
    if (buf.createSprite(SCREEN_W, SCREEN_H) == nullptr)
        return false;

    InitRadarPalette(buf);
    return true;
}

// --- echelle des elements (le 240x240 d'origine passe a 410x502) ------------
constexpr float UI_SCALE = static_cast<float>(RADAR_SPAN) / 240.0f;  // ~2.09

constexpr int   AIRCRAFT_TEXT_SIZE   = 2;
constexpr float TRIANGLE_LENGTH      = 6.0f * UI_SCALE;
constexpr float TRIANGLE_WIDTH       = 3.0f * UI_SCALE;
constexpr int   SCANLINE_THICKNESS   = 20;
constexpr int   SCANLINE_SPACING     = 11;   // 5 * UI_SCALE arrondi
constexpr int   SCANLINE_TRAIL       = 128;
