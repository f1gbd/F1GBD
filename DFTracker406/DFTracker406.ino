/*
 Radio Direction Finder Tracker 406 "DFTracker406" v1.0 par Jean-Louis Naudin (F1GBD) de l'ADRASEC77
 - début du projet 12 mars 2015

Ces informations sont publiées en Open Source (licence GNU v3.0) pour un usage personnel uniquement, non professionel et non commercial.

Ce firmware utilise la librairie "NMEA 0183 sentence decoding library for Wiring & Arduino" de Maarten Lamers en licence GNU v2.1

/// Open Source Licensing GPL V2
///
/// This is the appropriate option if you want to share the source code of your application with everyone you distribute it to, and you also want to give them
/// the right to share who uses it. If you wish to use this software under Open Source Licensing, you must contribute all your source code to the open source
/// community in accordance with the GPL Version 2 when your application is distributed. See http://www.gnu.org/copyleft/gpl.html

/// Arduino MEGA 2560    connexions  KN2C DDF2020T/GPS
///  RX2 --------------------------- Pin(3)-TxD Sortie RSS32 (prise DB9)
///  GND --------------------------- Pin(5)-GND (prise DB9)
///  +5V --------------------------  Sortie +5V
///  +12V -------------------------- Entrée +12V
*/

#define MISEAJOUR " 26/3/2015"   // date de la dernière mise à jour
#define VERSION "v 1.0"             // réference de la version actuelle

#include <LiquidCrystal.h>   // librarie pour l'afficheur LCD
#include <nmea.h>            // librairie NMEA de décodage de trame GPS

#define ENABLED   1
#define DISABLED  0

#define AGRELLO   ENABLED    // ENABLED = Trame de type AGRELLO DF en sortie, DISABLED = mode trace (NMEA + CAP) en sortie

NMEA gps(ALL);    // GPS data connection to all sentence types

static float lat, lon, lat_off_deg, lon_off_deg, lat_off_min, lon_off_min, clat, clon, course;

LiquidCrystal lcd(8,9,4,5,6,7);

static unsigned int bearing[50] = {};
static int bcount = 0, isec = 0, cap=0;
static boolean  heartbeat = false, bearingset=false;

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

// ----------------------------------------------------------------------------------------------------------

void setup() {
  Serial.begin(4800);
  Serial2.begin(4800);
  
    lcd.begin(16, 2);     // indique que l'afficheur est de 16 caractères sur 2 lignes
    lcd.clear();          // efface l'écran LCD  
    lcd.setCursor(0,0);
    
    Serial.println("\nDirection Finder Tracker v1.0 de F1GBD (Jean-Louis Naudin) - ADRASEC 77");
    Serial.print(VERSION); Serial.print(" - "); Serial.println(MISEAJOUR); 
    lcd.print("*** ADRASEC77 **"); 
    lcd.setCursor(0,1);
    lcd.print(" DFT406 - F1GBD ");
    delay(2000);
    lcd.clear();          // efface l'écran LCD  
    lcd.setCursor(0,0);
    lcd.print(VERSION); lcd.print(MISEAJOUR);
    delay(2000);
    lcd.setCursor(0,1);
    Serial.print("\nAttente acquisition satellites GPS...");   
    lcd.print("Acquisition GPS");
    
    getposition();  // attente de la validation de l'acquisition des satellites GPS

    Serial.println(" OK\nREADY\n");
    lcd.clear();          // efface l'écran LCD  
    affichage();
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
                  getposition();  // recupère la geolocalisaton GPS
		  medium_loopCounter++;
                break;
                
                case 1:
                if(bearingset)
                {
                  affichage();
                }
		  medium_loopCounter++;
                break;
                
                case 2:
                  gpsflag();
		  medium_loopCounter++;
                break;
                
                case 3:
                  clock();
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
  isec++;
  if (isec>5)
  { bcount = 0;
    isec = 0;
  }
}

// Affichage de l'indicateur de reception de trame GPS

void gpsflag()
{
  lcd.setCursor(15,0);
  heartbeat = !heartbeat;
  if (heartbeat)
      lcd.print("*");
  else
      lcd.print(" ");  
}

// Affichage du temps GPS UTC

void clock()
{
  lcd.setCursor(0,1); lcd.print(round(gps.gprmc_utc()));
}

// Affichage des coordonées GPS et du relevement de la balise

void affichage()
{    
//    lcd.clear();          // efface l'écran LCD  
    lcd.setCursor(0,0);

    // Affiche le coordonnées GPS
    lat=gps.gprmc_latitude();
    lcd.print(lat);  lcd.print(" "); 
    lcd.print(gps.term(4)); lcd.print(" ");
    lon=gps.gprmc_longitude();
    lcd.print(lon); lcd.print(" ");
    lcd.print(gps.term(6));
    if (AGRELLO == DISABLED)    
    { Serial.print("Lat : "); Serial.print(lat);  Serial.print(" "); 
      Serial.print(gps.term(4)); Serial.print(" ");
      Serial.print("Lon : "); Serial.print(lon); Serial.print(" ");
      Serial.print(gps.term(6)); Serial.print("    Time: "); Serial.println(round(gps.gprmc_utc()),DEC);
    }
    if (bcount>0)
    { int beartot = 0;
      for(int i=0; i<bcount; i++)
        beartot = beartot + bearing[i];
      cap = beartot/bcount;
      if (AGRELLO == DISABLED)
      {    
          Serial.print("Cap balise : "); Serial.println(cap);
      } else
      {
        Serial.print("%"); Serial.print(cap); Serial.println("/7");
      }
      for(int i=0; i<50; i++)
        bearing[i]=0;
      bcount = 0;
    }

    lcd.setCursor(7,1); lcd.print("<"); lcd.print(cap, DEC); lcd.print(">  ");
}
