/* ------------------------------------------------------------------------
 * teensy_4mic.ino -- tête d'acquisition 4 voies pour AERO-SPECTRIX
 *
 * Cible   : Teensy 4.0 ou 4.1 (PJRC), bibliothèque Audio de Teensyduino
 * Capteurs: 4 capsules MEMS I2S (INMP441 ou ICS-43434)
 * Sortie  : flux binaire trame par trame sur l'USB série, 44100 Hz,
 *           4 voies entrelacees, entiers signes 16 bits
 *
 * ------------------------------------------------------------------------
 * POURQUOI CE MONTAGE CONVIENT A LA MESURE DE TEMPS D'ARRIVEE
 * ------------------------------------------------------------------------
 * Tout le systeme repose sur des ecarts de quelques microsecondes entre les
 * quatre microphones. Il faut donc que les quatre voies soient echantillonnees
 * PAR LA MEME HORLOGE, sans quoi la direction derive continument.
 *
 * AudioInputI2SQuad utilise UN seul peripherique SAI : une seule BCLK
 * (broche 21), un seul LRCLK (broche 20), et deux lignes de donnees
 * (broches 8 et 6). Les quatre capsules sont donc cadencees ensemble par
 * construction -- ce n'est pas un reglage, c'est le cablage.
 *
 * Chaque ligne de donnees porte deux capsules : la broche L/R de la capsule
 * choisit la moitie de trame qu'elle occupe (L/R a la masse = voie gauche,
 * L/R au VDD = voie droite).
 *
 * ------------------------------------------------------------------------
 * CABLAGE
 * ------------------------------------------------------------------------
 *   Toutes les capsules : VDD -> 3.3V, GND -> GND
 *                         SCK -> broche 21 (BCLK)
 *                         WS  -> broche 20 (LRCLK)
 *
 *   M1 : SD -> broche 8    L/R -> GND
 *   M2 : SD -> broche 8    L/R -> 3.3V
 *   M3 : SD -> broche 6    L/R -> GND
 *   M4 : SD -> broche 6    L/R -> 3.3V
 *
 *   L'ordre M1..M4 doit correspondre aux sommets du tetraedre decrits par
 *   schema_cablage.py. Intervertir deux voies retourne le ciel.
 *
 * ------------------------------------------------------------------------
 * FORMAT DE TRAME (little endian)
 * ------------------------------------------------------------------------
 *   0..3   'A' 'S' '4' 0xA5      motif de synchronisation
 *   4..5   numero de bloc, uint16, boucle a 65536
 *   6..7   nombre d'echantillons par voie, uint16 (toujours 128 ici)
 *   8..9   nombre de blocs PERDUS depuis le dernier envoi, uint16
 *   10..   128 * 4 echantillons int16 entrelaces : M1 M2 M3 M4 M1 M2 ...
 *
 * Le compteur de blocs perdus n'est pas decoratif : un bloc perdu decale le
 * temps de 2,9 ms. Le recepteur doit le savoir pour combler le trou, sinon
 * la piste se decale sans que rien ne le signale.
 * ------------------------------------------------------------------------ */

#include <Audio.h>

// --- chaine audio : 4 entrees I2S -> 4 files d'attente --------------------
AudioInputI2SQuad    micros_i2s;
AudioRecordQueue     q1, q2, q3, q4;
AudioConnection      c1(micros_i2s, 0, q1, 0);
AudioConnection      c2(micros_i2s, 1, q2, 0);
AudioConnection      c3(micros_i2s, 2, q3, 0);
AudioConnection      c4(micros_i2s, 3, q4, 0);

const int  N        = AUDIO_BLOCK_SAMPLES;    // 128
const int  HEADER   = 10;
const int  PAYLOAD  = N * 4 * 2;              // 128 x 4 voies x 2 octets
uint8_t    paquet[HEADER + PAYLOAD];

uint16_t   seq        = 0;
uint16_t   perdus     = 0;
elapsedMillis         depuis_led;

void setup() {
  Serial.begin(115200);            // la vitesse est ignoree en USB natif
  pinMode(LED_BUILTIN, OUTPUT);

  // 200 blocs de 128 echantillons : de quoi absorber une pause de l'hote
  // sans perdre d'echantillons. Chaque bloc coute 256 octets de RAM.
  AudioMemory(200);

  paquet[0] = 'A'; paquet[1] = 'S'; paquet[2] = '4'; paquet[3] = 0xA5;
  paquet[6] = N & 0xFF;
  paquet[7] = (N >> 8) & 0xFF;

  q1.begin(); q2.begin(); q3.begin(); q4.begin();
}

void loop() {
  // On n'emet que lorsque les QUATRE files ont un bloc : emettre des voies
  // desynchronisees serait pire que ne rien emettre du tout, puisque rien
  // en aval ne pourrait s'en apercevoir.
  if (q1.available() < 1 || q2.available() < 1 ||
      q3.available() < 1 || q4.available() < 1) {
    // Une file qui deborde signale que l'hote ne lit pas assez vite. On vide
    // TOUTES les files ensemble pour ne pas casser l'alignement entre voies.
    if (q1.available() > 100 || q2.available() > 100 ||
        q3.available() > 100 || q4.available() > 100) {
      while (q1.available()) { q1.readBuffer(); q1.freeBuffer(); }
      while (q2.available()) { q2.readBuffer(); q2.freeBuffer(); }
      while (q3.available()) { q3.readBuffer(); q3.freeBuffer(); }
      while (q4.available()) { q4.readBuffer(); q4.freeBuffer(); }
      if (perdus < 0xFFFF) perdus++;
    }
    return;
  }

  int16_t *b1 = q1.readBuffer();
  int16_t *b2 = q2.readBuffer();
  int16_t *b3 = q3.readBuffer();
  int16_t *b4 = q4.readBuffer();

  paquet[4] = seq & 0xFF;
  paquet[5] = (seq >> 8) & 0xFF;
  paquet[8] = perdus & 0xFF;
  paquet[9] = (perdus >> 8) & 0xFF;

  int16_t *out = (int16_t *)(paquet + HEADER);
  for (int i = 0; i < N; i++) {
    out[4 * i + 0] = b1[i];
    out[4 * i + 1] = b2[i];
    out[4 * i + 2] = b3[i];
    out[4 * i + 3] = b4[i];
  }

  q1.freeBuffer(); q2.freeBuffer(); q3.freeBuffer(); q4.freeBuffer();

  Serial.write(paquet, HEADER + PAYLOAD);
  seq++;
  perdus = 0;

  if (depuis_led > 500) {          // battement de coeur : la tete vit
    depuis_led = 0;
    digitalWriteFast(LED_BUILTIN, !digitalReadFast(LED_BUILTIN));
  }
}
