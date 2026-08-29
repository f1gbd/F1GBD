/* Faux Arduino, uniquement pour le banc d'essai natif du provisioning.
 * Ne fait pas partie du firmware. */
#ifndef SHIM_ARDUINO_H
#define SHIM_ARDUINO_H

#include <stdarg.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <string>
#include <vector>

typedef std::string String;
#define F(x) (x)

extern bool g_restarted;

struct FakeSerial {
    std::vector<uint8_t> in;    /* ce que l'hote a envoye */
    size_t inpos = 0;
    std::vector<uint8_t> out;   /* ce que le firmware a repondu */
    std::string text;           /* les lignes de journal, a part */

    int available() { return (int)(in.size() - inpos); }
    int read() { return inpos < in.size() ? in[inpos++] : -1; }
    void write(uint8_t b) { out.push_back(b); }
    void write(const uint8_t *p, size_t n) { for (size_t i = 0; i < n; i++) out.push_back(p[i]); }
    void flush() {}
    void println(const char *s) { text += s; text += "\n"; }
    void print(const char *s) { text += s; }
    int printf(const char *fmt, ...) {
        char b[512];
        va_list ap; va_start(ap, fmt); int n = vsnprintf(b, sizeof b, fmt, ap); va_end(ap);
        text += b;
        return n;
    }
    void begin(unsigned long) {}
};
extern FakeSerial Serial;

inline void delay(unsigned long) {}
inline unsigned long millis() { return 0; }

struct FakeEsp { void restart(); };
extern FakeEsp ESP;

#endif
