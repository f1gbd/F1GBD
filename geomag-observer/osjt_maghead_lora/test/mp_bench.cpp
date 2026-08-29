/* Banc d'essai natif du codec MsgPack : il ecrit sur la sortie standard les
 * trames que le firmware produirait, et relit celles que Python lui donne.
 * Le script test_msgpack.py confronte les deux a la bibliotheque msgpack.
 *
 *   g++ -std=c++11 -Wall -Wextra -I../include mp_bench.cpp -o mp_bench
 */
#include <stdio.h>
#include <stdlib.h>
#include <string>
#include "osjt_msgpack.h"

static void dump(const uint8_t *b, uint16_t n) {
    for (uint16_t i = 0; i < n; i++) printf("%02x", b[i]);
    printf("\n");
}

/* Chaque cas produit une des quatre formes reellement echangees. */
static void emit(const char *what) {
    uint8_t buf[512];
    MpWriter w; w.init(buf, sizeof buf);
    std::string k(what);

    if (k == "commit") {                       /* [6, 1, nil] */
        w.array(3); w.uint(6); w.uint(1); w.nil();
    }
    else if (k == "getstate") {                /* [4, 300, {1: [101]}] */
        w.array(3); w.uint(4); w.uint(300);
        w.map(1); w.uint(1); w.array(1); w.uint(101);
    }
    else if (k == "state") {                   /* reponse GET_STATE */
        w.array(3); w.uint(100); w.uint(7);
        w.map(1);
          w.uint(101);
          w.map(3);
            w.uint(1); w.str("ADRASEC77-AP");
            w.uint(3); w.str("192.168.1.20");
            w.uint(4); w.uint(10077);
    }
    else if (k == "error") {                   /* [101, 9, {1:5, 2:"..."}] */
        w.array(3); w.uint(101); w.uint(9);
        w.map(2); w.uint(1); w.uint(5); w.uint(2); w.str("Valeur invalide");
    }
    else if (k == "edges") {                   /* bornes de l'encodage */
        w.array(9);
        w.uint(0); w.uint(127); w.uint(128); w.uint(255); w.uint(256);
        w.uint(65535); w.uint(65536);
        w.sint(-1); w.sint(-32769);
    }
    else if (k == "longstr") {                 /* 31, 32 et 300 caracteres */
        std::string a(31, 'a'), b(32, 'b'), c(300, 'c');
        w.array(3); w.str(a.c_str()); w.str(b.c_str()); w.str(c.c_str());
    }
    else { fprintf(stderr, "cas inconnu : %s\n", what); exit(2); }

    if (w.ovf) { fprintf(stderr, "debordement\n"); exit(3); }
    dump(buf, w.len);
}

static int unhex(const char *h, uint8_t *out, int cap) {
    int n = 0;
    for (; h[0] && h[1] && n < cap; h += 2, n++) {
        char t[3] = { h[0], h[1], 0 };
        out[n] = (uint8_t)strtol(t, NULL, 16);
    }
    return n;
}

/* Relit une requete de la console et en rend une description a plat, que le
 * script compare a ce que Python a encode. */
static void parse(const char *hex) {
    uint8_t buf[1024];
    int n = unhex(hex, buf, sizeof buf);
    MpReader r; r.init(buf, (uint16_t)n);

    uint16_t na = 0;
    if (!r.array(na) || na != 3) { printf("ERR enveloppe\n"); return; }
    int32_t op = 0, seq = 0;
    if (!r.sint(op) || !r.sint(seq)) { printf("ERR entete\n"); return; }
    printf("op=%d seq=%d", op, seq);

    if (r.is_nil()) { printf(" payload=nil\n"); return; }

    uint16_t nm = 0;
    if (!r.map(nm)) { printf(" ERR payload\n"); return; }
    for (uint16_t i = 0; i < nm; i++) {
        int32_t key = 0;
        if (!r.sint(key)) { printf(" ERR cle\n"); return; }
        /* GET_STATE : {1: [ns...]} — SET_STATE : {ns: {champ: valeur}} */
        if (key == 1 && op == 4) {
            uint16_t nn = 0;
            if (!r.array(nn)) { printf(" ERR liste\n"); return; }
            printf(" ns=[");
            for (uint16_t j = 0; j < nn; j++) {
                int32_t v = 0;
                if (!r.sint(v)) { printf("ERR"); return; }
                printf("%s%d", j ? "," : "", v);
            }
            printf("]");
            continue;
        }
        uint16_t nf = 0;
        if (!r.map(nf)) { printf(" ERR champs\n"); return; }
        printf(" ns%d{", key);
        for (uint16_t j = 0; j < nf; j++) {
            int32_t fid = 0;
            if (!r.sint(fid)) { printf("ERR"); return; }
            printf("%s%d=", j ? "," : "", fid);
            /* Port entier, tout le reste en chaine : c'est exactement la
             * discrimination que fait le provisioning reel. */
            if (fid == 4) {
                int32_t v = 0;
                if (!r.sint(v)) { printf("ERR"); return; }
                printf("%d", v);
            } else {
                char s[128];
                if (!r.str(s, sizeof s)) { printf("ERR"); return; }
                printf("'%s'", s);
            }
        }
        printf("}");
    }
    if (!r.ok()) { printf(" ERR fin\n"); return; }
    printf(" reste=%u\n", (unsigned)r.left());
}

/* Verifie que skip() traverse n'importe quel element sans se perdre : on
 * saute le premier element d'un tableau de deux et on lit le second. */
static void skiptest(const char *hex) {
    uint8_t buf[1024];
    int n = unhex(hex, buf, sizeof buf);
    MpReader r; r.init(buf, (uint16_t)n);
    uint16_t na = 0;
    if (!r.array(na) || na != 2) { printf("ERR\n"); return; }
    if (!r.skip()) { printf("ERR skip\n"); return; }
    int32_t v = 0;
    if (!r.sint(v)) { printf("ERR lecture\n"); return; }
    printf("%d reste=%u\n", v, (unsigned)r.left());
}

int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: mp_bench emit|parse|skip ARG\n"); return 1; }
    std::string mode(argv[1]);
    if (mode == "emit") emit(argv[2]);
    else if (mode == "parse") parse(argv[2]);
    else if (mode == "skip") skiptest(argv[2]);
    else return 1;
    return 0;
}
