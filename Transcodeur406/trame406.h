/////////////////////////////////////////////////////////////////////////////////////////
/////                                                                          //////////
///// FICHIERS DE PARAMETRAGE DU TRANSCODEUR406 v 1.0 par F1GBD de l'ADRASEC77 //////////
/////                                                                          //////////
/////////////////////////////////////////////////////////////////////////////////////////

#define TEMPO 50  // temporisation de 50 sec entre chaque trames 406 envoyées

///////////////////////////////////////////////////////////////////////////////////////////////////////
//       Paramètres des données COSPAS-SARSAT à envoyer sur la balise 406 à simuler                 ///
//                                                                                                  ///
// pour vérifier l& validité du codage de la BCH1 et BCH2 voir : http://www.stanguard.com/406.html  ///
///////////////////////////////////////////////////////////////////////////////////////////////////////

// Trame406 (#1) 22 HEX : 8E227B929230A0552C04B4
// représentation semi-graphique (affichée sur le port COM) de la trame 406 envoyée
// Datas:--______------______--______--____--------__------____--____--__--____--____--______----________--__--____________--__--__--__--____--__----______________--____--__----__--____
// Clock:-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_
/*
#define DATALEN 88    // Nombre de bits de données de la trame 406
char datafield[DATALEN+1] = {1,                                          // long format (F=1)
                             0,                                          // Location protocol (P=0)
                             0,0,1,1,1,0,0,0,1,0,                        //country code: 226 FRANCE
                             0,0,1,0,                                    // type of location protocol  (EPIRB MMSI)
                             0,1,1,1,1,0,1,1,1,0,0,1,0,0,1,0,1,0,0,1,    // MID: 506153
                             0,0,1,0,                                    // specific beacon = 2
                             0,                                          // lat sign    0 = N,  1 = S
                             0,1,1,0,0,0,0,                              // latitude degrees   48° (codé en binaire)
                             1,0,                                        // 10 = 2, lat minutes   30' = 2 * 15 minute
                             1,                                          // long sign   1 = W,  1 = E
                             0,0,0,0,0,0,1,0,                            // longitude degrees  2°  (codé en binaire)
                             1,0,                                        // 10 = 2, lon minutes  30' = 2 * 15 minute
                             1,0,1,0,0,1,0,1,1,0,0,0,0,0,0,0,1,0,0,1,0,  // BCH1
                             1,1,0,1,                                    // Fixed bits (pass)
                             0,                                          // Position data
                             0                                           // Aux device :  No 121.5 MHz homer
                             };                                          // fin de champ de données
*/           
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/////// Exemple de trame longue (30 hex     ) : 8E23ADEC7730A0616807B7082709A3                                                     ///////
/////// 100011100010001110101101111011000111011100110000 10 1 00000011 00 001011010000000011110 1101 1 1 0 00010 0000 1 00111 0000 100110100011   ///////
/////// 100011100010001110101101111011000111011100110000101000000110000101101000000001111011011100001000001001110000100110100011   ///////
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#define DATALEN 120    // Nombre de bits de données de la trame 406
char datafield[DATALEN+1] = {1,                                                // long format (F=1)
                             0,                                                // Location protocol (P=0)
                             0,0,1,1,1,0,0,0,1,0,                              //country code: 226 FRANCE
                             0,0,1,1,                                          // type: Aircraft 24 bit address
                             1,0,1,0,1,1,0,1,1,1,1,0,1,1,0,0,0,1,1,1,0,1,1,1,  // ADEC77
                             0,                                                // lat sign    0 = N,  1 = S
                             0,1,1,0,0,0,0,                                    // latitude degrees   48° (codé en binaire)
                             1,0,                                              // 10 = 2, lat minutes   30' = 2 * 15 minute
                             1,                                                // long sign   1 = W,  1 = E
                             0,0,0,0,0,0,1,1,                                  // longitude degrees  3°  (codé en binaire)
                             0,0,                                              // 00 = 0, lon minutes  30' = 2 * 15 minute
                             0,0,1,0,1,1,0,1,0,0,0,0,0,0,0,0,1,1,1,1,0,        // BCH1 : 001011010000000011110
                             1,1,0,1,                                          // Fixed bits (pass)
                             1,                                                // Position data, encoded position data source from internal navigation device
                             1,                                                // Aux device :  121.5 MHz homer
                             0,                                                // lat offset sign 0 = (-), 1 = (+)
                             0,0,0,1,0,                                        // lat offset minute (-2')
                             0,0,0,0,                                          // lat offset second (0")
                             1,                                                // lon offset sign 0 = (-), 1 = (+)
                             0,0,1,1,1,                                        // lon offset minute (+7')
                             0,0,0,0,                                          // lon offset second (0")
                             1,0,0,1,1,0,1,0,0,0,1,1                           // BCH2 : 100110100011
                             };    // fin de champ de données

// Exemple de codage de la position en dur                             
// codage latitude 
// exemple : 48° 28"                              
// 48 => 0,1,1,0,0,0,0,
// 28' = 30' - 2' (offset)
// 30 = 2 * 15 => 1,0,
// offset -2'
// signe (-) => 0,
// 2' => 0,0,0,1,0,
// 0" => 0,0,0,0,
// codage longitude 
// exemple : 3° 7'                              
// 3 => 0,0,0,0,0,0,1,1,
// 7' = 0' + 7' (offset)
// 0' => 0,0,
// offset +7'
// signe (+) => 1,
// 7' => 0,0,1,1,1,
// 0" => 0,0,0,0,

