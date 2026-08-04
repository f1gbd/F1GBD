// ============================================================================
//  Micro Radar - portage Waveshare ESP32-C6-Touch-AMOLED-2.06
//  D'apres https://github.com/AnthonySturdy/micro-radar (ESP32-C3 / GC9A01)
// ============================================================================

#include <Arduino.h>
#include <ArduinoJson.h>
#include <WiFiManager.h>

#include "LGFX.h"
#include "DisplayConfig.h"
#include "WiFiManagerHelpers.h"
#include "ConfigurationWebServer.h"
#include "HttpRequestManager.h"
#include "OpenSkyAuthTokenHandler.h"
#include "AircraftManager.h"
#include "DrawHelpers.h"
#include "models/Aircraft.h"
#include "models/TrackedAircraft.h"

// Identifiants WiFi optionnels. Laisser vide pour passer par le hotspot de
// configuration.
const char* preconfiguredWifiSsid = "";
const char* preconfiguredWifiPassword = "";

LGFX tft;
LGFX_Sprite backbuffer(&tft);

WiFiManager wm;
ConfigurationWebServer configServer;
HttpRequestManager http;
OpenSkyAuthTokenHandler authHandler(http);

AircraftManager aircraftManager(configServer, authHandler, http, tft);

// Reglage d'affichage lu une seule fois au demarrage (voir setup()).
bool renderScanlines = true;

void setup()
{
    Serial.begin(115200);          // USB Serial/JTAG natif du C6
    delay(300);                    // laisse le CDC s'enumerer

    // ---- ecran -------------------------------------------------------------
    tft.init();
    tft.setRotation(0);            // 0 = portrait 410 x 502
    tft.setBrightness(200);        // 0..255, registre 0x51 du CO5300
    tft.fillScreen(0);             // (0,0,410,502) : X et largeur pairs -> OK

    // ---- backbuffer plein ecran -------------------------------------------
    // S3 : 16 bits en PSRAM (412 Ko).  C6 : palette 4 bits en SRAM (103 Ko),
    // a allouer AVANT le demarrage du WiFi car c'est le seul moment ou un bloc
    // contigu de cette taille est disponible.
    if (!CreateBackbuffer(backbuffer)) {
        Serial.println("[FATAL] backbuffer allocation failed");
        while (true) delay(1000);
    }

    Serial.printf("[INFO] heap libre apres backbuffer : %u octets\n",
                  (unsigned)ESP.getFreeHeap());

    // ---- WiFi --------------------------------------------------------------
    ShowStatus(backbuffer, "MICRO RADAR", "Connecting to WiFi...");

    WiFiManagerHelpers::ConfigureWiFiManager(wm, backbuffer);

    if (strlen(preconfiguredWifiSsid) > 0) {
        WiFi.begin(preconfiguredWifiSsid, preconfiguredWifiPassword);
        WiFi.waitForConnectResult();
    }

    wm.autoConnect(WiFiManagerHelpers::WiFiManagerName);

    // Desactive le mode veille modem du WiFi.
    // Sans cela, le PHY est arrete/redemarre en permanence (routine pm_dream) ;
    // sur arduino-esp32 3.x / IDF 5.5 ce chemin appelle phy_track_pll_init(),
    // qui fait un ESP_ERROR_CHECK(esp_timer_create(...)) et provoque un
    // "ESP_ERR_NO_MEM ... abort()" en boucle de reboot des que la memoire
    // interne est sollicitee. La radar est alimentee en USB : aucune raison
    // de garder l'economie d'energie.
    WiFi.setSleep(false);

    // ---- services ----------------------------------------------------------
    configServer.Initialise();
    aircraftManager.Initialise();

    // Lu UNE SEULE FOIS ici : lire la NVS a chaque image (comme le faisait la
    // version d'origine) ouvre/ferme un espace de noms NVS des dizaines de fois
    // par seconde, ce qui fragmente le tas interne et finit par faire echouer
    // les petites allocations de la pile WiFi.
    const String scanlineSetting = configServer.GetStoredString("scanline");
    renderScanlines = scanlineSetting.isEmpty() || scanlineSetting == "true";

    Serial.printf("[INFO] heap libre apres WiFi : %u octets (plus grand bloc : %u)\n",
                  (unsigned)ESP.getFreeHeap(),
                  (unsigned)ESP.getMaxAllocHeap());
}

void loop()
{
    // ---- suivi memoire (a surveiller sur la console serie) -----------------
    static uint32_t lastHeapLog = 0;
    if (millis() - lastHeapLog > 10000) {
        lastHeapLog = millis();
        Serial.printf("[HEAP] interne %u (bloc max %u) | psram %u\n",
                      (unsigned)ESP.getFreeHeap(),
                      (unsigned)ESP.getMaxAllocHeap(),
                      (unsigned)ESP.getFreePsram());
    }

    // ---- tant que la position n'est pas saisie ------------------------------
    if (!aircraftManager.IsConfigured()) {
        static String ipLine;
        if (ipLine.isEmpty()) ipLine = "http://" + WiFi.localIP().toString() + "/";
        ShowStatus(backbuffer, "MICRO RADAR", "Configurer la position sur :", ipLine.c_str());
        delay(500);
        return;
    }

    aircraftManager.Update();

    // ---- cycle de rendu ----------------------------------------------------
    backbuffer.fillScreen(COL_BLACK);

    if (renderScanlines) {
        DrawScanLines(backbuffer,
            RADAR_CX,
            RADAR_CY,
            RADAR_CX + (std::cos(millis() / 3000.0f) * RADAR_R),
            RADAR_CY + (std::sin(millis() / 3000.0f) * RADAR_R),
            SCANLINE_THICKNESS, SCANLINE_TRAIL, SCANLINE_SPACING
        );
    }

    aircraftManager.Draw(backbuffer);

    // 410 px de large a partir de X=0 : les deux valeurs sont paires, la
    // contrainte d'alignement du CO5300 est respectee.
    backbuffer.pushSprite(0, 0);

    // Laisse respirer les taches systeme (pile WiFi, lwIP, serveur web async).
    // Sans cela la boucle de rendu monopolise son coeur et les taches de meme
    // priorite se font servir au compte-gouttes.
    delay(5);
}
