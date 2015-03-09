/*
 Transcodeur de trame 406 v1.0 par Jean-Louis Naudin (F1GBD) de l'ADRASEC77

- début du projet 9 janvier 2015

Ce firmware utilise une version spécialement modifiée, pour cette application transcodeur406 , de la librairie VirtualWire 1.27 de Mike McCauley

/// Open Source Licensing GPL V2
///
/// This is the appropriate option if you want to share the source code of your application with everyone you distribute it to, and you also want to give them
/// the right to share who uses it. If you wish to use this software under Open Source Licensing, you must contribute all your source code to the open source
/// community in accordance with the GPL Version 2 when your application is distributed. See http://www.gnu.org/copyleft/gpl.html

/// Arduino UNO    connexions        Emetteur balise 406
///  D3----------------------------- Ptt Tx 406
///  D12-----------------------------Interface Tx 406
///  GND-----------------------------GND

******  POUR LE PARAMETRAGE DE LA TRAME406 A ENVOYER MODIFIER LE FICHIER trame406.h  *******
ATTENTION DANS CETTE VERSION LA POSITION EST ENCODEE EN DUR DANS LE FIRMWARE (Pas de GPS externe)
Les coordonnées encodées de la balise 406 sont dans cet exemple : lat: 48.47° N long: 3.12° W
*/

#include <VirtualWire.h>     // librairie VirtualWire 1.27 de Mike McCauley
#include <SPI.h>             // Not actually used but needed to compile
#include <LiquidCrystal.h>   // librarie pour l'afficheur LCD
#include "trame406.h"        // FICHIER DE PARAMETRAGE DE LA TRAME 406 à ENVOYER

#define MISEAJOUR "8 mars 2015"   // date de la dernière mise à jour
#define VERSION "1.2"             // réference de la version actuelle

#define ENABLED                 1
#define DISABLED                0

#define TRACE     DISABLED

static byte pdf1[DATALEN+4] = "";
static char trame[DATALEN*2]="";
static char trameTosend[(DATALEN*2)+8]="";
static char msg[(DATALEN/4)+9];
unsigned int count=1, bitcount=0;
unsigned int datalen=0;

LiquidCrystal lcd(8,9,4,5,6,7);

// System Timers
// --------------
unsigned long fast_loopTimer	= 0;	// Time in miliseconds of main control loop
byte medium_loopCounter		= 0;	// Counters for branching from main control loop to slower loops
byte slow_loopCounter		= 0;	// 
unsigned long deltaMiliSeconds 	= 0;	// Delta Time in miliseconds


void lcd_print_P(const char *string)
{
  char c;
  while( (c = pgm_read_byte(string++)) )
    lcd.LiquidCrystal::write(c);
}

void setup()
{
    Serial.begin(9600);	  // Sortie trace (optionel) sur le port com PC

    lcd.begin(16, 2);     // indique que l'afficheur est de 16 caractères sur 2 lignes
    lcd.clear();          // efface l'écran LCD  
    
    // Initialise the IO and ISR
    // vw_set_ptt_inverted(true); // Required for DR3100
    vw_setup(800);	          // 400 Bits per sec : 800 = 2x400

    Serial.println("\n\nTranscodeur de trame 406 COSPAS-SARSAT de F1GBD (Jean-Louis Naudin)");
    Serial.print("ADRASEC77 - Transcodeur406 "); Serial.print(VERSION); Serial.print(" - "); Serial.println(MISEAJOUR); 
    
    tramecreate();   // creation de la trame 406 à partir de la datafield
#if TRACE == ENABLED    
    dumptrame();     // trace détaillée de la trame sur le port com 
#endif
    tramegen();      // compose la trame 406 à envoyer 
#if TRACE == ENABLED    
    Serial.print("\nPeriode : "); Serial.print(TEMPO,DEC); Serial.println(" sec.");
#endif 

  count=0; // RAZ du compteur
  
  trame_send();  // envoie une trame
}
////////////////////// Moniteur transactionnel //////////////////
////// boucle principale 0.1 Hz, boucle secondaire à 0.5 Hz /////
/////////////////////////////////////////////////////////////////
void loop() {
  
  	// Boucle à 100 ms
	// -----------------------------------------------------------------
	if (DIYmillis()-fast_loopTimer > 100) {
		deltaMiliSeconds 	= DIYmillis() - fast_loopTimer;
		fast_loopTimer		= DIYmillis();

	//	This is the start of the medium (10 Hz) loop pieces
	// -----------------------------------------
	switch (medium_loopCounter) {
		case 0:
		  medium_loopCounter++;
                break;
                
                case 1:
		  medium_loopCounter++;
                break;
                
                case 2:
		  medium_loopCounter++;
                break;
                
                case 3:
		  medium_loopCounter++;
                break;

                case 4:
		  medium_loopCounter = 0;
                  slow_loop();
                break;
              }
    }
}

void slow_loop()   //	boucle à 500 ms
{
	switch (slow_loopCounter) {
		case 0:
		  slow_loopCounter++;
                  one_secloop();          // appel de la boucle à une seconde
		  break;
		case 1:
		  slow_loopCounter=0;
                  break;
		}
}

void one_secloop()  // appelé une fois par seconde
{
 if(count==TEMPO)
  { trame_send();     // envoie une trame
    count=0;          // RAZ du compteur
  }
   count++;           // décompte
   lcd.setCursor(15,1); lcd.print((char)(64+count));   // affiche un cartère de comptage
}

