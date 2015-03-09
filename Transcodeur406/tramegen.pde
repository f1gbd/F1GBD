// Creation de la trame 406 à envoyer bit à bit
void tramecreate()
{
  // on recompose la trame406
   unsigned int dataini=0, z=0;
   byte clk=1; 

   Serial.print("\nNombre de bits de datas : "); Serial.print(DATALEN, DEC);
   
// conditions initiales
       if(dataini==datafield[0])  // si data = data+1
       { if(dataini==0)
         {trame[z]=!clk; clk=!clk; z++;  // clk = 1 puis  0
          trame[z]=!clk; clk=!clk; z++;
         } else if(dataini==1)
         {trame[z]=clk; clk=!clk; z++;
          trame[z]=clk; clk=!clk; z++;
         }         
       } else if(dataini!=datafield[0])  // si data != data+1
       { if(dataini==0)          
         {trame[z]=!clk; clk=!clk; z++;
          trame[z]=clk; clk=!clk; z++;
         } else if(dataini==1)
         {trame[z]=clk; clk=!clk; z++;
          trame[z]=!clk; clk=!clk; z++;
         }       
       }
       
// synthetise la trame406, oublier les 2 premier bits de synchro
   for(int i=0;i<DATALEN;i++)  
     { 
       if(datafield[i]==datafield[i+1])  // si data = data+1
       { if(datafield[i]==0)
         {trame[z]=!clk; clk=!clk; z++;
          trame[z]=!clk; clk=!clk; z++;
         } else if(datafield[i]==1)
         {trame[z]=clk; clk=!clk; z++;
          trame[z]=clk; clk=!clk; z++;
         }         
       } else if(datafield[i]!=datafield[i+1])  // si data != data+1
       { if(datafield[i]==0)  
         {trame[z]=!clk; clk=!clk; z++;
          trame[z]=clk; clk=!clk; z++;
         } else if(datafield[i]==1)
         {trame[z]=clk; clk=!clk; z++;
          trame[z]=!clk; clk=!clk; z++;
         }       
       }
     }
     bitcount = z;
//     Serial.print("\nil y a "); Serial.print(bitcount); Serial.println(" bits");     
}

 //génère la trame406 à envoyer: inversion de la trame initiale
void tramegen()
{ unsigned int k=0;
  int data;
  
    for(int i=2;i<bitcount;i=i+8)
    {
      for(int j=7;j>=0;j--)
      { trameTosend[k]=trame[i+j];
        k++;
      }
    }
#if TRACE == ENABLED
  Serial.print("Data :");  
  for(int i=0;i<DATALEN;i++)  // imprime les données de la trame406 à envoyer
         Serial.print((int)datafield[i]); 
  Serial.println();  
#endif  
/* 
   Serial.print("\nFlux :");  
   for(int i=2;i<bitcount;i++)  // imprime le flux de la trame406 (bits à bits) à envoyer
       Serial.print((int)trame[i]);   
  
   Serial.print("\n!Flux:");
   for(int i=0;i<bitcount-2;i++)  // imprime le flux de trame406 inverse qui est réellement envoyé
       Serial.print((int)trameTosend[i]);
  
       Serial.println();
 */     
// génère le code inversé par paquets de 8 bits
    lcd.setCursor(0,0);

      k=0;
      for (int j=0; j<(DATALEN*2); j=j+8)
      {  data=(trameTosend[j]*8)+(trameTosend[j+1]*4)+(trameTosend[j+2]*2)+(trameTosend[j+3]);
         data=(data*16)+(trameTosend[j+4]*8)+(trameTosend[j+5]*4)+(trameTosend[j+6]*2)+(trameTosend[j+7]);
         msg[k]=(char)data;
//         Serial.print(data,HEX); Serial.print(" ");
         k++; msg[k]=0;
      }      
}    

void trame_send()
{    lcd.clear(); lcd.setCursor(0,0);
    lcd.print("Transcodeur 406");
    lcd.setCursor(0,1);
    lcd.print("ADRASEC77  F1GBD");
    delay(1000);  // pause 1 secs
    lcd.clear();    
    lcd.setCursor(0,0); lcd.print("Trame 406 ENVOYEE");
    lcd.setCursor(0,1); lcd.print("---> # ");
    lcd.print(count);   // affiche le compteur de trame
    delay(1000);  // pause 1 secs
    lcd.clear();    
    lcd.setCursor(0,0);    
    print_code();    // affiche sur le LCD le trame 406 en HEX

#if TRACE == ENABLED
    Serial.print(" msg sent:"); Serial.println(vw_send((uint8_t *)msg, strlen(msg)));  // emission de la trame sur la sortie
#else    
    vw_send((uint8_t *)msg, strlen(msg));  // emission de la trame sur la sortie
#endif

    vw_wait_tx(); // Wait until the whole message is gone  
}
