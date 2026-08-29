/* =========================================================================
 * osjt_provisioning.h — configuration de la tete par le port USB
 * =========================================================================
 *
 * MEME DIALOGUE QUE RWLoRa, DELIBEREMENT
 * --------------------------------------
 * Trame KISS sur le port serie, charge utile MsgPack :
 *
 *     hote -> tete : FEND 0x86 <MsgPack echappe> FEND
 *     tete -> hote : FEND 0x87 <MsgPack echappe> FEND
 *
 * Enveloppe, dans les DEUX sens : [op_id, seq, payload].
 *
 * Namespace 101 « reseau », champs 1 SSID, 2 mot de passe, 3 hote, 4 port —
 * exactement ceux de RWLoRa. Un operateur qui a configure une passerelle
 * RWLoRa retrouve la meme fenetre, les memes boutons et les memes messages.
 * C'est aussi ce qui permet de mettre les deux codes cote a cote quand l'un
 * des deux se met a ne plus repondre.
 *
 * CE QUI DIFFERE DE RWLoRa, ET POURQUOI
 * ------------------------------------
 * RWLoRa s'appuie sur le sous-systeme Provisioning de microReticulum, que
 * ce firmware n'embarque pas : la tete magnetique n'est pas un noeud
 * Reticulum, et tirer toute la bibliotheque pour quatre champs serait
 * absurde. Le protocole est donc reimplemente ici, en direct — une centaine
 * de lignes — mais le FIL est identique, et c'est le fil qui compte.
 *
 * Il n'y a pas de namespace radio 100 : cette tete n'a pas de radio LoRa a
 * regler. Une console qui demande les deux recoit le 101 seul, ce qui est
 * la reponse honnete.
 *
 * LE MOT DE PASSE NE SE RELIT PAS
 * -------------------------------
 * Le champ 2 part vers la tete, jamais l'inverse. Une console capable de le
 * relire serait un moyen d'extraire la cle WiFi de toute tete a laquelle on
 * a acces physique — et une tete magnetique passe sa vie dehors, sur un
 * mat, a portee de qui veut.
 *
 * Copyright 2026 F1GBD / F4JHW — ADRASEC 77 — Licence MIT
 * ========================================================================= */

#ifndef OSJT_PROVISIONING_H
#define OSJT_PROVISIONING_H

#include <stdint.h>

#define OSJT_PROV_SSID_MAX 32
#define OSJT_PROV_PASS_MAX 64
#define OSJT_PROV_HOST_MAX 64

struct OsjtNetConfig {
  char     ssid[OSJT_PROV_SSID_MAX + 1];
  char     pass[OSJT_PROV_PASS_MAX + 1];
  char     host[OSJT_PROV_HOST_MAX + 1];
  uint16_t port;
};

/* Charge la configuration persistee. A appeler AVANT de demarrer le WiFi. */
void osjtProvBegin();

/* A appeler depuis loop() : consomme le port serie, traite les requetes.
 * Ne bloque pas, et ne consomme que ce qui ressemble a une trame KISS. */
void osjtProvLoop();

/* La configuration en vigueur. Jamais nulle. */
const OsjtNetConfig &osjtProvConfig();

/* Vrai si un champ a ete modifie depuis le demarrage : les valeurs ne
 * prennent effet qu'au redemarrage, il faut pouvoir le dire. */
bool osjtProvNeedsReboot();

#endif /* OSJT_PROVISIONING_H */
