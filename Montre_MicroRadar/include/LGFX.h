#pragma once

// ============================================================================
//  Configuration LovyanGFX pour les cartes Waveshare AMOLED 2.06"
//
//  Deux cartes partagent exactement la meme dalle mais pas le meme brochage :
//    - ESP32-S3-Touch-AMOLED-2.06   -> -DMICRORADAR_BOARD_S3   (defaut)
//    - ESP32-C6-Touch-AMOLED-2.06   -> -DMICRORADAR_BOARD_C6
//  Le choix se fait dans platformio.ini (env:...-s3 ou env:...-c6).
//
//  Ecran   : AMOLED CO5300, 410 x 502, bus QSPI, offset colonne 22
//  Tactile : FT3168 (I2C 0x38) sur les deux cartes d'apres les exemples
//            Arduino officiels Waveshare.
// ============================================================================

#include <LovyanGFX.hpp>

#if !defined(MICRORADAR_BOARD_S3) && !defined(MICRORADAR_BOARD_C6)
#define MICRORADAR_BOARD_S3 1
#endif

#if !defined(LGFX_USE_QSPI)
#error "LovyanGFX n'a pas active le support QSPI (il faut ESP-IDF >= 4.4)"
#endif

// Mettre a 0 si le tactile pose probleme au demarrage. Micro Radar ne s'en
// sert pas : c'est purement optionnel.
// NB : certaines revisions de la carte S3 embarquent un CST9220 (adresse 0x5A)
// qui n'est pas gere par LovyanGFX -> le tactile restera simplement inactif,
// sans empecher l'affichage.
#define MICRORADAR_USE_TOUCH 1

// --- brochage carte ---------------------------------------------------------
#if defined(MICRORADAR_BOARD_S3)
  // Waveshare ESP32-S3-Touch-AMOLED-2.06
  #define PIN_LCD_SCLK  11
  #define PIN_LCD_SDIO0  4
  #define PIN_LCD_SDIO1  5
  #define PIN_LCD_SDIO2  6
  #define PIN_LCD_SDIO3  7
  #define PIN_LCD_CS    12
  #define PIN_LCD_RESET  8

  #define PIN_IIC_SDA   15
  #define PIN_IIC_SCL   14
  #define PIN_TP_INT    38
  #define PIN_TP_RESET   9
#else
  // Waveshare ESP32-C6-Touch-AMOLED-2.06
  #define PIN_LCD_SCLK   0
  #define PIN_LCD_SDIO0  1
  #define PIN_LCD_SDIO1  2
  #define PIN_LCD_SDIO2  3
  #define PIN_LCD_SDIO3  4
  #define PIN_LCD_CS     5
  #define PIN_LCD_RESET 11

  #define PIN_IIC_SDA    8
  #define PIN_IIC_SCL    7
  #define PIN_TP_INT    15
  #define PIN_TP_RESET  10
#endif

class LGFX : public lgfx::LGFX_Device
{
    lgfx::Bus_SPI      _bus;      // pilote aussi le mode QSPI (pin_io0..io3)
    lgfx::Panel_CO5300 _panel;
#if MICRORADAR_USE_TOUCH
    lgfx::Touch_FT5x06 _touch;    // compatible registres FT3168
#endif

public:
    LGFX(void)
    {
        {   // ---------- bus QSPI ----------
            auto cfg = _bus.config();

            cfg.spi_host    = SPI2_HOST;
            cfg.spi_mode    = 0;
            cfg.dma_channel = SPI_DMA_CH_AUTO;

            // 40 MHz = valeur sure. On peut tenter 80000000 pour doubler le
            // debit (~10 ms par trame pleine au lieu de ~20 ms) si l'affichage
            // reste stable.
            cfg.freq_write = 40000000;
            cfg.freq_read  = 16000000;

            cfg.pin_sclk = PIN_LCD_SCLK;
            cfg.pin_io0  = PIN_LCD_SDIO0;
            cfg.pin_io1  = PIN_LCD_SDIO1;
            cfg.pin_io2  = PIN_LCD_SDIO2;
            cfg.pin_io3  = PIN_LCD_SDIO3;

            _bus.config(cfg);
            _panel.setBus(&_bus);
        }

        {   // ---------- panneau CO5300 ----------
            auto cfg = _panel.config();

            cfg.pin_cs  = PIN_LCD_CS;
            cfg.pin_rst = PIN_LCD_RESET;

            // Le constructeur de Panel_CO5300 est cable pour la LilyGO
            // T-Watch-Ultra (502 x 410, paysage). La dalle Waveshare est
            // montee en portrait : on inverse largeur / hauteur.
            cfg.panel_width   = 410;
            cfg.panel_height  = 502;
            cfg.memory_width  = 410;
            cfg.memory_height = 502;

            cfg.offset_x = 22;   // fenetre colonne 22..431
            cfg.offset_y = 0;
            cfg.offset_rotation = 0;

            cfg.readable  = false;
            cfg.invert    = false;
            cfg.rgb_order = false;

            _panel.config(cfg);
        }

#if MICRORADAR_USE_TOUCH
        {   // ---------- tactile FT3168 ----------
            auto cfg = _touch.config();

            cfg.i2c_addr = 0x38;
            cfg.i2c_port = 0;
            cfg.pin_sda  = PIN_IIC_SDA;
            cfg.pin_scl  = PIN_IIC_SCL;
            cfg.pin_int  = PIN_TP_INT;
            cfg.pin_rst  = PIN_TP_RESET;
            cfg.freq     = 400000;

            cfg.x_min = 0;   cfg.x_max = 409;
            cfg.y_min = 0;   cfg.y_max = 501;
            cfg.bus_shared = false;
            cfg.offset_rotation = 0;

            _touch.config(cfg);
            _panel.setTouch(&_touch);
        }
#endif

        setPanel(&_panel);
    }
};
