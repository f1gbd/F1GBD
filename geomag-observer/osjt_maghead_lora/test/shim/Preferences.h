/* Faux NVS en memoire, pour le banc d'essai natif. */
#ifndef SHIM_PREFERENCES_H
#define SHIM_PREFERENCES_H

#include <map>
#include <string>
#include <stdint.h>

extern std::map<std::string, std::string> g_nvs_str;
extern std::map<std::string, uint16_t> g_nvs_u16;
extern bool g_nvs_fail;          /* pour eprouver le chemin d'erreur */

class Preferences {
public:
    bool begin(const char *, bool ro = false) { (void)ro; return !g_nvs_fail; }
    void end() {}
    std::string getString(const char *k, const char *dflt) {
        auto it = g_nvs_str.find(k);
        return it == g_nvs_str.end() ? std::string(dflt) : it->second;
    }
    uint16_t getUShort(const char *k, uint16_t dflt) {
        auto it = g_nvs_u16.find(k);
        return it == g_nvs_u16.end() ? dflt : it->second;
    }
    int putString(const char *k, const char *v) { g_nvs_str[k] = v; return (int)strlen(v); }
    int putUShort(const char *k, uint16_t v) { g_nvs_u16[k] = v; return 2; }
};

#endif
