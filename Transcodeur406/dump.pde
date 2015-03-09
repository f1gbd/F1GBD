// imprime la trame à envoyer en mode semi-graphique sur le port com
#if TRACE == ENABLED
void dumptrame()
{
   byte dataini=0, z=0, clk=1; 
   
   lcd.setCursor(0,0);
   Serial.print("\nDatas:");   
   for(int i=0;i<DATALEN;i++)  // imprime la trame PDF-1
     { 
       if(datafield[i]==1) 
       { Serial.print("--");
       }
       else 
       { Serial.print("__");
       }
     }   
   Serial.print("\nClock:");   

   for(int i=0;i<bitcount-2;i++)  // imprime le signal d'horloge
   { if(clk==1) Serial.print("-");
     else Serial.print("_");
     clk=!clk;
   }
 /* 
   Serial.print("\nT:");
   for(int i=2;i<(DATALEN+2);i++)  // imprime la trame406 à envoyer
   {
     if(trame[i]==1) Serial.print("-");
     else Serial.print("_");
   }
   */
    Serial.println();
}
#endif

// Affiche le code HEXA de la trame 406
void print_code()
{ unsigned int data;

  if(TRACE) 
  {   Serial.print("Trame406 (#"); Serial.print(count); Serial.print(") ");
      Serial.print(strlen(msg)); Serial.print(" HEX : ");
  }
      lcd.setCursor(0,0);
      for (int j=0; j<DATALEN; j=j+4)
      {  data=(datafield[j]*8)+(datafield[j+1]*4)+(datafield[j+2]*2)+(datafield[j+3]);
         if(TRACE) Serial.print(data,HEX);
         if(j==64) lcd.setCursor(0,1);
         lcd.print(data,HEX);
      }      
}
