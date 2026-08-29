/* =========================================================================
 * main.cpp — aiguillage de role
 * =========================================================================
 * Un seul arbre de sources, trois environnements PlatformIO :
 *
 *   pio run -e heltec_v4_node        -DOSJT_ROLE=1   tete LoRa
 *   pio run -e heltec_v4_gateway     -DOSJT_ROLE=2   passerelle LoRa
 *   pio run -e heltec_v4_node_wifi   -DOSJT_ROLE=3   tete WiFi
 *
 * Les trois partagent la definition des trames — osjt_lora_frame.h pour la
 * liaison radio, osjt_teensy_frame.h pour ce qui arrive au PC. C'est tout
 * l'interet : des projets separes divergeraient un jour sur un champ de
 * structure, et la panne se presenterait comme un magnetogramme aux valeurs
 * absurdes, sans le moindre message d'erreur.
 * ========================================================================= */

#include <Arduino.h>

#ifndef OSJT_ROLE
#error "OSJT_ROLE non defini : compiler avec -e heltec_v4_node, -e heltec_v4_gateway ou -e heltec_v4_node_wifi"
#endif

#if OSJT_ROLE == 1
void nodeSetup();
void nodeLoop();
void setup() { nodeSetup(); }
void loop()  { nodeLoop(); }

#elif OSJT_ROLE == 2
void gatewaySetup();
void gatewayLoop();
void setup() { gatewaySetup(); }
void loop()  { gatewayLoop(); }

#elif OSJT_ROLE == 3
void nodeWifiSetup();
void nodeWifiLoop();
void setup() { nodeWifiSetup(); }
void loop()  { nodeWifiLoop(); }

#else
#error "OSJT_ROLE inconnu"
#endif
