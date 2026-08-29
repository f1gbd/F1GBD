/* =========================================================================
 * osjt_pins.h — brochage Heltec WiFi LoRa 32 V4 (et V3, identique)
 * =========================================================================
 *
 * A VERIFIER SUR VOTRE EXEMPLAIRE avant le premier cablage. Le SX1262 et
 * l'OLED sont figes par la carte ; le bus du RM3100, lui, est un choix,
 * fait ici parmi les GPIO libres. Rien n'oblige a le suivre.
 *
 * POURQUOI UN SECOND BUS SPI
 * --------------------------
 * Le SX1262 occupe deja SPI2, et il emet par salves de plusieurs dizaines
 * de milliamperes. Partager le bus obligerait a arbitrer entre une lecture
 * capteur et une emission, exactement au moment ou l'on veut que les deux
 * soient bien separees dans le temps. L'ESP32-S3 a trois controleurs SPI :
 * autant en dedier un au capteur.
 * ========================================================================= */

#ifndef OSJT_PINS_H
#define OSJT_PINS_H

/* --- SX1262, fige par la carte ---------------------------------------- */
#define PIN_LORA_NSS    8
#define PIN_LORA_SCK    9
#define PIN_LORA_MOSI   10
#define PIN_LORA_MISO   11
#define PIN_LORA_RST    12
#define PIN_LORA_BUSY   13
#define PIN_LORA_DIO1   14

/* --- OLED, fige par la carte ------------------------------------------ */
#define PIN_OLED_SDA    17
#define PIN_OLED_SCL    18
#define PIN_OLED_RST    21
#define PIN_VEXT        36   /* actif a l'etat BAS : alimente l'OLED */

/* --- Mesure de batterie ----------------------------------------------- */
#define PIN_VBAT_ADC    1
#define PIN_VBAT_CTRL   37   /* actif a l'etat BAS : ferme le pont diviseur */

/* --- RM3100 : J3 broches 14 a 17, quatre GPIO reellement libres --------
 *
 * Choisies pour etre CONTIGUES sur le connecteur ET dans l'ordre des
 * broches du module RM3100 (5=SCK, 6=MISO, 7=MOSI, 8=CS) : la nappe part
 * droite, sans un seul croisement.
 *
 *   J3-14  GPIO3  ->  RM3100 broche 5  SCK
 *   J3-15  GPIO4  ->  RM3100 broche 6  MISO
 *   J3-16  GPIO5  ->  RM3100 broche 7  MOSI
 *   J3-17  GPIO6  ->  RM3100 broche 8  CS
 *
 * CE QU'IL NE FAUT SURTOUT PAS PRENDRE, et pourquoi
 * -------------------------------------------------
 * Le V4 a un etage RF haute puissance et de la PSRAM qui mangent des GPIO
 * d'apparence libre. Les toucher donne une carte qui demarre, compile et
 * fonctionne — jusqu'a la premiere emission, ou au premier acces PSRAM.
 *
 *   GPIO2   FEM_EN        etage RF
 *   GPIO7   VFEM_Ctrl     etage RF   <-- piege : J3-18, juste a cote
 *   GPIO46  FEM_PA        etage RF + broche de strapping
 *   GPIO45                broche de strapping (VDD_SPI)
 *   GPIO1   VBAT_Read     mesure de batterie
 *   GPIO37  ADC_Ctrl      pont diviseur de batterie
 *   GPIO36  Vext_Ctrl     alimentation de l'OLED
 *   GPIO35  LED_Write
 *   GPIO34  PGNSS_Ctrl
 *   GPIO21  OLED_RST
 *   GPIO26  SPICS1        flash / PSRAM
 *   GPIO19  GPIO20        USB D+ / D-
 *   GPIO33 a GPIO37       CONSOMMES par la PSRAM octale sur un ESP32-S3R8
 *   GPIO38 a GPIO42       libres, mais ce sont le JTAG et l'interface GNSS
 */
#define PIN_RM_SCK      3    /* J3-14 */
#define PIN_RM_MISO     4    /* J3-15 */
#define PIN_RM_MOSI     5    /* J3-16 */
#define PIN_RM_CS       6    /* J3-17 */

/* DRDY : VOLONTAIREMENT NON CABLE.
 *
 * A 10 Hz, interroger le registre d'etat coute une transaction SPI par
 * boucle et ne fait rien perdre — le pilote sait deja se rabattre dessus.
 * Un fil de moins, c'est une paire de moins dans le cable enterre et une
 * soudure de moins a l'exterieur. DRDY n'a d'interet qu'a 40 Hz ou plus,
 * ou l'horodatage sur interruption devient utile.
 *
 * Pour le cabler quand meme : J2-13 (GPIO47) ou J2-14 (GPIO48), tous deux
 * libres, et remplacer 0xFF ci-dessous par le numero choisi. */
#define PIN_RM_DRDY     0xFF

/* Le connecteur du capteur doit etre a 30 cm MINIMUM de la carte, 50 cm de
 * preference. A 10 cm, la boucle de courant du module produit environ 6 nT
 * — six fois le plancher de bruit vise. Le SPI supporte tres bien un metre
 * de nappe blindee a 1 MHz. */

#endif /* OSJT_PINS_H */
