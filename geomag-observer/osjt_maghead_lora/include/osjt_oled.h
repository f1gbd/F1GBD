/* =========================================================================
 * osjt_oled.h — ecran OLED, present sur la passerelle, eteint sur le noeud
 * =========================================================================
 *
 * DEUX USAGES OPPOSES, ET LA MEME SOLUTION
 * ----------------------------------------
 * L'OLED consomme une quinzaine de milliamperes et cree une boucle de
 * courant a quelques centimetres du RM3100. Sur la PASSERELLE cela n'a
 * aucune importance : elle est posee sur le bureau, il n'y a pas de
 * magnetometre a proximite, et un ecran qui affiche le nombre de trames et
 * le RSSI repond a la seule question qu'on se pose devant elle — est-ce que
 * ca recoit ? Il reste donc allume en permanence.
 *
 * Sur le NOEUD, l'ecran serait disqualifiant s'il restait allume. Mais son
 * cout n'existe QUE PENDANT QU'IL EST ALLUME : vingt secondes au demarrage,
 * quand aucune mesure n'a encore commence, ne coutent rien du tout.
 *
 * Le noeud affiche donc son ecran d'accueil et son verdict d'autotest, puis
 * COUPE l'alimentation de l'OLED — Vext repasse a l'etat haut — et ne la
 * rallume jamais. Apres extinction, osjtOledStatus() ne fait plus rien : il
 * n'y a aucun risque qu'un appel oublie rallume l'ecran en service.
 *
 * C'est le meilleur des deux : on voit que la tete fonctionne avant de la
 * descendre dans le tube, et elle ne pollue rien une fois enterree.
 *
 * Quand OSJT_OLED vaut 0, tout ce fichier se reduit a des fonctions vides :
 * ni bibliotheque, ni code, ni octet de plus dans l'image.
 *
 * Copyright 2026 F1GBD / F4JHW — ADRASEC 77 — Licence MIT
 * ========================================================================= */

#ifndef OSJT_OLED_H
#define OSJT_OLED_H

#include <Arduino.h>
#include "osjt_pins.h"

#ifndef OSJT_OLED
#define OSJT_OLED 0
#endif

#if OSJT_OLED

#include <U8g2lib.h>
#include <Wire.h>

static U8G2_SSD1306_128X64_NONAME_F_HW_I2C
    g_oled(U8G2_R0, PIN_OLED_RST, PIN_OLED_SCL, PIN_OLED_SDA);

static bool g_oledOk = false;

inline void osjtOledBegin(const char *title) {
  /* L'OLED des Heltec V3/V4 est alimente par Vext, pilote a l'etat BAS.
   * Sans cette ligne l'ecran reste noir et l'I2C ne repond pas — c'est la
   * premiere chose qu'on oublie sur ces cartes. */
  pinMode(PIN_VEXT, OUTPUT);
  digitalWrite(PIN_VEXT, LOW);
  delay(60);

  pinMode(PIN_OLED_RST, OUTPUT);
  digitalWrite(PIN_OLED_RST, LOW);
  delay(20);
  digitalWrite(PIN_OLED_RST, HIGH);
  delay(20);

  g_oledOk = g_oled.begin();
  if (!g_oledOk) return;
  g_oled.setBusClock(400000);
  g_oled.clearBuffer();
  g_oled.setFont(u8g2_font_7x13B_tr);
  g_oled.drawStr(0, 12, "GEOMAG-Observer");
  g_oled.setFont(u8g2_font_6x10_tr);
  g_oled.drawStr(0, 28, title);
  g_oled.drawStr(0, 40, OSJT_FW_VERSION);
  g_oled.drawStr(0, 58, "ADRASEC 77");
  g_oled.sendBuffer();
}

/* Quatre lignes libres. Ecrire NULL pour laisser une ligne vide. */
inline void osjtOledStatus(const char *l1, const char *l2,
                           const char *l3, const char *l4) {
  if (!g_oledOk) return;
  g_oled.clearBuffer();
  g_oled.setFont(u8g2_font_7x13B_tr);
  if (l1) g_oled.drawStr(0, 12, l1);
  g_oled.setFont(u8g2_font_6x10_tr);
  if (l2) g_oled.drawStr(0, 28, l2);
  if (l3) g_oled.drawStr(0, 42, l3);
  if (l4) g_oled.drawStr(0, 56, l4);
  g_oled.sendBuffer();
}

/* Coupe l'ecran DEFINITIVEMENT pour cette session.
 *
 * setPowerSave eteint la matrice, mais le controleur SSD1306 continue de
 * consommer : on coupe donc Vext, ce qui retire l'alimentation. Mettre
 * g_oledOk a false rend tous les appels ulterieurs inoperants, si bien
 * qu'un osjtOledStatus() oublie dans la boucle principale ne peut pas
 * ressusciter l'ecran au milieu d'une mesure. */
inline void osjtOledOff() {
  if (g_oledOk) g_oled.setPowerSave(1);
  g_oledOk = false;
  pinMode(PIN_VEXT, OUTPUT);
  digitalWrite(PIN_VEXT, HIGH);
}

inline bool osjtOledPresent() { return g_oledOk; }

#else   /* ------------------------------------------------------------ */

inline void osjtOledBegin(const char *) {}
inline void osjtOledStatus(const char *, const char *, const char *,
                           const char *) {}
inline void osjtOledOff() {}
inline bool osjtOledPresent() { return false; }

#endif
#endif /* OSJT_OLED_H */
