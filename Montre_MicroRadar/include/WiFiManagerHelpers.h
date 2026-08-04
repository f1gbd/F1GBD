#pragma once

#include <WiFiManager.h>
#include "DisplayConfig.h"
#include "DrawHelpers.h"

namespace WiFiManagerHelpers
{
    constexpr const char* WiFiManagerName = "MicroRadar-Setup";

    // La capture de la sprite (et non du LGFX) evite le probleme d'alignement
    // pair impose par le CO5300 sur les ecritures partielles.
    static void ConfigureWiFiManager(WiFiManager& wm, LGFX_Sprite& backbuffer)
    {
        wm.setTitle("Micro Radar - Setup WiFi");
        wm.setCustomHeadElement("<style>body{background:#111;color:#00ff00;font-family:monospace;} div:has(> a){background:#00ff00;} a:hover{color:#111;}</style>");

        wm.setAPCallback([&backbuffer](WiFiManager* wifiManager) {
            ShowStatus(backbuffer,
                       "- SETUP -",
                       "Connect to this WiFi hotspot:",
                       WiFiManagerName);
            }
        );
    }
}
