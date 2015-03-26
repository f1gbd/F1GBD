// Attente d'une trame GPRMC (position) du GPS
void getposition()
{ String gpsbuff="";
  boolean gpsrec = false;
  
  while(!gpsrec)
  {
    if (Serial2.available() > 0 ) {
      char c = Serial2.read();
      if (c != 37)
      { // read incoming character from GPS and feed it to NMEA type object
        if (gps.decode(c)) 
          {
              gpsbuff = (String)gps.term(0);
             if(gpsbuff == "GPRMC") 
                  gpsrec = true;
          }
      } else 
      { bearing[bcount] = Serial2.parseInt();
        bearingset = true;
        bcount++;        
      }
    }
  }  
}

