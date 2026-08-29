/* Banc d'essai natif du repondeur de provisioning.
 *
 * Le firmware est compile tel quel, avec un faux Arduino et un faux NVS. On
 * lui pousse les octets qu'enverrait la console et on rend, en hexadecimal,
 * les octets qu'il repond — que le script confronte a msgpack.
 *
 *   g++ -std=c++11 -Wall -Wextra -Itest/shim -Iinclude \
 *       src/provisioning.cpp test/prov_bench.cpp -o test/prov_bench
 */
#include <Arduino.h>
#include <Preferences.h>
#include <stdlib.h>
#include <string>

#include "osjt_provisioning.h"

FakeSerial Serial;
FakeEsp ESP;
bool g_restarted = false;
void FakeEsp::restart() { g_restarted = true; }
std::map<std::string, std::string> g_nvs_str;
std::map<std::string, uint16_t> g_nvs_u16;
bool g_nvs_fail = false;

static int unhex(const char *h, uint8_t *out, int cap) {
    int n = 0;
    for (; h[0] && h[1] && n < cap; h += 2, n++) {
        char t[3] = { h[0], h[1], 0 };
        out[n] = (uint8_t)strtol(t, NULL, 16);
    }
    return n;
}

/* Un scenario = une suite de commandes separees par des virgules :
 *   nvs:ssid=...   pose une valeur dans le faux NVS avant le demarrage
 *   fail           rend le NVS defaillant
 *   begin          appelle osjtProvBegin()
 *   rx:<hex>       pousse des octets sur le port serie, puis osjtProvLoop()
 *   out            imprime ce que le firmware a repondu, en hexadecimal
 *   cfg            imprime la configuration en vigueur
 *   reboot         imprime si un redemarrage a ete demande / est requis
 *   text           imprime le journal
 */
/* Sur une vraie carte, le journal et les trames partagent le MEME fil : le
 * client doit savoir demeler les deux. Le mode serve reproduit donc cela,
 * en emettant le texte accumule avant les trames. Le mode ligne de commande,
 * lui, les garde separes — ses comparaisons sont octet pour octet. */
static void wire() {
    for (size_t j = 0; j < Serial.text.size(); j++)
        printf("%02x", (unsigned char)Serial.text[j]);
    Serial.text.clear();
    for (size_t j = 0; j < Serial.out.size(); j++) printf("%02x", Serial.out[j]);
    Serial.out.clear();
    printf("\n");
    fflush(stdout);
}

/* Mode « serve » : le firmware reste vivant et dialogue par l'entree
 * standard, une ligne d'hexadecimal a la fois. C'est ce qui permet de
 * brancher dessus le VRAI client de GEOMAG-Observer, et donc d'eprouver la
 * paire telle qu'elle fonctionnera sur le cable USB — plutot que chacun de
 * son cote contre une idee de l'autre. */
static void serve() {
    char line[8192];
    osjtProvBegin();
    wire();
    while (fgets(line, sizeof line, stdin)) {
        size_t n = strlen(line);
        while (n && (line[n - 1] == '\n' || line[n - 1] == '\r')) line[--n] = 0;
        uint8_t b[4096];
        int m = unhex(line, b, sizeof b);
        for (int j = 0; j < m; j++) { Serial.in.push_back(b[j]); osjtProvLoop(); }
        wire();
    }
}

int main(int argc, char **argv) {
    if (argc == 2 && std::string(argv[1]) == "serve") { serve(); return 0; }
    for (int i = 1; i < argc; i++) {
        std::string c(argv[i]);
        if (c == "begin") osjtProvBegin();
        else if (c == "fail") g_nvs_fail = true;
        else if (c == "ok") g_nvs_fail = false;
        else if (c.rfind("nvs:", 0) == 0) {
            std::string kv = c.substr(4);
            size_t e = kv.find('=');
            std::string k = kv.substr(0, e), v = kv.substr(e + 1);
            if (k == "port") g_nvs_u16[k] = (uint16_t)atoi(v.c_str());
            else g_nvs_str[k] = v;
        }
        else if (c.rfind("rx:", 0) == 0) {
            uint8_t b[2048];
            int n = unhex(c.c_str() + 3, b, sizeof b);
            for (int j = 0; j < n; j++) Serial.in.push_back(b[j]);
            osjtProvLoop();
        }
        else if (c.rfind("rx1:", 0) == 0) {
            /* Meme chose, mais UN OCTET A LA FOIS : c'est ainsi qu'un port
             * serie livre reellement, et c'est la que les automates a etats
             * se trompent. */
            uint8_t b[2048];
            int n = unhex(c.c_str() + 4, b, sizeof b);
            for (int j = 0; j < n; j++) { Serial.in.push_back(b[j]); osjtProvLoop(); }
        }
        else if (c == "out") {
            for (size_t j = 0; j < Serial.out.size(); j++) printf("%02x", Serial.out[j]);
            printf("\n");
            Serial.out.clear();
        }
        else if (c == "cfg") {
            const OsjtNetConfig &f = osjtProvConfig();
            printf("ssid='%s' pass='%s' host='%s' port=%u\n",
                   f.ssid, f.pass, f.host, (unsigned)f.port);
        }
        else if (c == "nvs") {
            printf("ssid='%s' pass='%s' host='%s' port=%u\n",
                   g_nvs_str["ssid"].c_str(), g_nvs_str["pass"].c_str(),
                   g_nvs_str["host"].c_str(), (unsigned)g_nvs_u16["port"]);
        }
        else if (c == "reboot") {
            printf("needs=%d restarted=%d\n", osjtProvNeedsReboot() ? 1 : 0,
                   g_restarted ? 1 : 0);
        }
        else if (c == "text") { printf("%s", Serial.text.c_str()); Serial.text.clear(); }
        else { fprintf(stderr, "commande inconnue : %s\n", c.c_str()); return 2; }
    }
    return 0;
}
